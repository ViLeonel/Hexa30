"""Workflow editorial versionado para edição administrativa segura.

A edição nunca escreve diretamente na fonte canônica. Alterações passam por
rascunho, revisão e publicação. A publicação exige backend SQLite durável,
controle otimista de concorrência, validação integral e auditoria campo a campo.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sqlite3
import uuid
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

from hexa_audit import gerar_eventos_alteracao
from hexa_models import validar_estrutura_bruta, validar_jogadores_normalizados
from hexa_repository import ConflitoConcorrenciaError, DataIntegrityError
from hexa_repository_sqlite import (
    SqliteAuditoriaRepository,
    SqliteJogadoresRepository,
)
from hexa_taticas import POSICOES_OFICIAIS

__all__ = [
    "CAMPOS_EDITAVEIS",
    "RascunhoEditorial",
    "StatusRascunho",
    "WorkflowEditorialError",
    "WorkflowEditorialRepository",
]


class WorkflowEditorialError(RuntimeError):
    """Falha de regra ou persistência no workflow editorial."""


class StatusRascunho(str, Enum):
    RASCUNHO = "rascunho"
    EM_REVISAO = "em_revisao"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"
    PUBLICADO = "publicado"
    CANCELADO = "cancelado"


CAMPOS_EDITAVEIS: frozenset[str] = frozenset(
    {
        "clube",
        "idade",
        "grupo",
        "posicao",
        "posicoes_multiplas",
        "nota_vini",
        "nota_roberto",
        "pontos_fortes",
        "pontos_fracos",
        "historico",
    }
)


@dataclass(frozen=True, slots=True)
class RascunhoEditorial:
    id_rascunho: str
    jogador: str
    status: StatusRascunho
    versao_base: str
    alteracoes: Mapping[str, Any]
    justificativa: str
    criado_em: str
    atualizado_em: str
    criado_por_email: str = ""
    criado_por_nome: str = ""
    criado_por_id: str = ""
    revisado_por_email: str = ""
    revisado_por_nome: str = ""
    revisado_por_id: str = ""
    comentario_revisao: str = ""
    versao_publicada: str = ""


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json(valor: Any) -> str:
    return json.dumps(valor, ensure_ascii=False, sort_keys=True, default=str)


def _validar_alteracoes(alteracoes: Mapping[str, Any]) -> dict[str, Any]:
    desconhecidos = sorted(set(alteracoes) - CAMPOS_EDITAVEIS)
    if desconhecidos:
        raise WorkflowEditorialError(
            f"Campos não editáveis no workflow: {', '.join(desconhecidos)}."
        )
    resultado = copy.deepcopy(dict(alteracoes))
    if "posicao" in resultado and resultado["posicao"] not in POSICOES_OFICIAIS:
        raise WorkflowEditorialError("A posição principal não pertence ao vocabulário oficial.")
    if "posicoes_multiplas" in resultado:
        posicoes = resultado["posicoes_multiplas"]
        if not isinstance(posicoes, list) or not posicoes:
            raise WorkflowEditorialError("Posições múltiplas deve ser uma lista não vazia.")
        invalidas = [item for item in posicoes if item not in POSICOES_OFICIAIS]
        if invalidas:
            raise WorkflowEditorialError(
                f"Posições múltiplas inválidas: {', '.join(map(str, invalidas))}."
            )
    if "idade" in resultado:
        try:
            idade = int(resultado["idade"])
        except (TypeError, ValueError) as erro:
            raise WorkflowEditorialError("Idade deve ser um número inteiro.") from erro
        if not 15 <= idade <= 45:
            raise WorkflowEditorialError("Idade fora do intervalo permitido (15–45).")
        resultado["idade"] = idade
    for campo in ("nota_vini", "nota_roberto"):
        if campo in resultado:
            try:
                nota = float(resultado[campo])
            except (TypeError, ValueError) as erro:
                raise WorkflowEditorialError(f"{campo} deve ser numérico.") from erro
            if not 0.0 <= nota <= 10.0:
                raise WorkflowEditorialError(f"{campo} deve estar entre 0 e 10.")
            resultado[campo] = nota
    for campo in ("pontos_fortes", "pontos_fracos", "historico", "clube", "grupo"):
        if campo in resultado:
            texto = str(resultado[campo] or "").strip()
            if len(texto) > 8000:
                raise WorkflowEditorialError(f"{campo} excede o limite de 8.000 caracteres.")
            resultado[campo] = texto
    return resultado


class WorkflowEditorialRepository:
    """Rascunhos e transições editoriais no mesmo SQLite versionado."""

    def __init__(self, caminho: Path) -> None:
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        self._inicializar()
        SqliteAuditoriaRepository(self.caminho)

    def _conectar(self) -> sqlite3.Connection:
        conexao = sqlite3.connect(self.caminho, timeout=5.0)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        conexao.execute("PRAGMA journal_mode = WAL")
        conexao.execute("PRAGMA synchronous = FULL")
        return conexao

    def _inicializar(self) -> None:
        with closing(self._conectar()) as conexao:
            conexao.executescript(
                """
                CREATE TABLE IF NOT EXISTS editorial_rascunhos (
                    id_rascunho TEXT PRIMARY KEY,
                    jogador TEXT NOT NULL,
                    status TEXT NOT NULL,
                    versao_base TEXT NOT NULL,
                    alteracoes_json TEXT NOT NULL,
                    justificativa TEXT NOT NULL,
                    criado_em TEXT NOT NULL,
                    atualizado_em TEXT NOT NULL,
                    criado_por_email TEXT NOT NULL DEFAULT '',
                    criado_por_nome TEXT NOT NULL DEFAULT '',
                    criado_por_id TEXT NOT NULL DEFAULT '',
                    revisado_por_email TEXT NOT NULL DEFAULT '',
                    revisado_por_nome TEXT NOT NULL DEFAULT '',
                    revisado_por_id TEXT NOT NULL DEFAULT '',
                    comentario_revisao TEXT NOT NULL DEFAULT '',
                    versao_publicada TEXT NOT NULL DEFAULT ''
                );
                CREATE INDEX IF NOT EXISTS idx_editorial_status_data
                    ON editorial_rascunhos(status, atualizado_em DESC);
                CREATE TABLE IF NOT EXISTS editorial_eventos (
                    id_evento TEXT PRIMARY KEY,
                    id_rascunho TEXT NOT NULL,
                    ocorrido_em TEXT NOT NULL,
                    acao TEXT NOT NULL,
                    ator_email TEXT NOT NULL DEFAULT '',
                    ator_nome TEXT NOT NULL DEFAULT '',
                    ator_id TEXT NOT NULL DEFAULT '',
                    comentario TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY (id_rascunho)
                        REFERENCES editorial_rascunhos(id_rascunho)
                );
                CREATE INDEX IF NOT EXISTS idx_editorial_eventos_rascunho
                    ON editorial_eventos(id_rascunho, ocorrido_em);
                """
            )
            conexao.commit()

    @staticmethod
    def _linha_para_rascunho(linha: sqlite3.Row) -> RascunhoEditorial:
        alteracoes = json.loads(str(linha["alteracoes_json"]))
        if not isinstance(alteracoes, dict):
            raise WorkflowEditorialError("Rascunho armazenado com alterações inválidas.")
        return RascunhoEditorial(
            id_rascunho=str(linha["id_rascunho"]),
            jogador=str(linha["jogador"]),
            status=StatusRascunho(str(linha["status"])),
            versao_base=str(linha["versao_base"]),
            alteracoes=alteracoes,
            justificativa=str(linha["justificativa"]),
            criado_em=str(linha["criado_em"]),
            atualizado_em=str(linha["atualizado_em"]),
            criado_por_email=str(linha["criado_por_email"]),
            criado_por_nome=str(linha["criado_por_nome"]),
            criado_por_id=str(linha["criado_por_id"]),
            revisado_por_email=str(linha["revisado_por_email"]),
            revisado_por_nome=str(linha["revisado_por_nome"]),
            revisado_por_id=str(linha["revisado_por_id"]),
            comentario_revisao=str(linha["comentario_revisao"]),
            versao_publicada=str(linha["versao_publicada"]),
        )

    def _evento(
        self,
        conexao: sqlite3.Connection,
        *,
        id_rascunho: str,
        acao: str,
        ator_email: str,
        ator_nome: str,
        ator_id: str,
        comentario: str = "",
    ) -> None:
        conexao.execute(
            """
            INSERT INTO editorial_eventos (
                id_evento, id_rascunho, ocorrido_em, acao,
                ator_email, ator_nome, ator_id, comentario
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                id_rascunho,
                _agora(),
                acao,
                ator_email,
                ator_nome,
                ator_id,
                comentario,
            ),
        )

    def criar(
        self,
        *,
        jogador: str,
        versao_base: str,
        estado_atual: Mapping[str, Any],
        alteracoes: Mapping[str, Any],
        justificativa: str,
        ator_email: str = "",
        ator_nome: str = "",
        ator_id: str = "",
    ) -> RascunhoEditorial:
        patch = _validar_alteracoes(alteracoes)
        patch = {
            campo: valor
            for campo, valor in patch.items()
            if estado_atual.get(campo) != valor
        }
        if not patch:
            raise WorkflowEditorialError("O rascunho não contém alterações efetivas.")
        justificativa_normalizada = str(justificativa or "").strip()
        if len(justificativa_normalizada) < 5:
            raise WorkflowEditorialError("Informe uma justificativa com pelo menos 5 caracteres.")

        id_rascunho = str(uuid.uuid4())
        agora = _agora()
        with closing(self._conectar()) as conexao:
            conexao.execute(
                """
                INSERT INTO editorial_rascunhos (
                    id_rascunho, jogador, status, versao_base,
                    alteracoes_json, justificativa, criado_em, atualizado_em,
                    criado_por_email, criado_por_nome, criado_por_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    id_rascunho,
                    jogador,
                    StatusRascunho.RASCUNHO.value,
                    versao_base,
                    _json(patch),
                    justificativa_normalizada,
                    agora,
                    agora,
                    ator_email,
                    ator_nome,
                    ator_id,
                ),
            )
            self._evento(
                conexao,
                id_rascunho=id_rascunho,
                acao="criado",
                ator_email=ator_email,
                ator_nome=ator_nome,
                ator_id=ator_id,
                comentario=justificativa_normalizada,
            )
            conexao.commit()
        return self.obter(id_rascunho)

    def obter(self, id_rascunho: str) -> RascunhoEditorial:
        with closing(self._conectar()) as conexao:
            linha = conexao.execute(
                "SELECT * FROM editorial_rascunhos WHERE id_rascunho = ?",
                (str(id_rascunho),),
            ).fetchone()
        if linha is None:
            raise WorkflowEditorialError("Rascunho não encontrado.")
        return self._linha_para_rascunho(linha)

    def listar(
        self,
        *,
        status: StatusRascunho | None = None,
        limite: int = 100,
    ) -> list[RascunhoEditorial]:
        limite_seguro = max(1, min(int(limite), 500))
        consulta = "SELECT * FROM editorial_rascunhos"
        parametros: list[Any] = []
        if status is not None:
            consulta += " WHERE status = ?"
            parametros.append(status.value)
        consulta += " ORDER BY atualizado_em DESC LIMIT ?"
        parametros.append(limite_seguro)
        with closing(self._conectar()) as conexao:
            linhas = conexao.execute(consulta, parametros).fetchall()
        return [self._linha_para_rascunho(linha) for linha in linhas]

    def _transicionar(
        self,
        id_rascunho: str,
        *,
        esperado: Sequence[StatusRascunho],
        novo: StatusRascunho,
        ator_email: str,
        ator_nome: str,
        ator_id: str,
        comentario: str = "",
    ) -> RascunhoEditorial:
        with closing(self._conectar()) as conexao:
            conexao.execute("BEGIN IMMEDIATE")
            linha = conexao.execute(
                "SELECT status FROM editorial_rascunhos WHERE id_rascunho = ?",
                (id_rascunho,),
            ).fetchone()
            if linha is None:
                raise WorkflowEditorialError("Rascunho não encontrado.")
            atual = StatusRascunho(str(linha["status"]))
            if atual not in esperado:
                permitidos = ", ".join(item.value for item in esperado)
                raise WorkflowEditorialError(
                    f"Transição inválida: status atual {atual.value}; esperado {permitidos}."
                )
            conexao.execute(
                """
                UPDATE editorial_rascunhos
                SET status = ?, atualizado_em = ?,
                    revisado_por_email = ?, revisado_por_nome = ?,
                    revisado_por_id = ?, comentario_revisao = ?
                WHERE id_rascunho = ?
                """,
                (
                    novo.value,
                    _agora(),
                    ator_email,
                    ator_nome,
                    ator_id,
                    comentario,
                    id_rascunho,
                ),
            )
            self._evento(
                conexao,
                id_rascunho=id_rascunho,
                acao=novo.value,
                ator_email=ator_email,
                ator_nome=ator_nome,
                ator_id=ator_id,
                comentario=comentario,
            )
            conexao.commit()
        return self.obter(id_rascunho)

    def enviar_revisao(self, id_rascunho: str, **ator: str) -> RascunhoEditorial:
        return self._transicionar(
            id_rascunho,
            esperado=(StatusRascunho.RASCUNHO, StatusRascunho.REJEITADO),
            novo=StatusRascunho.EM_REVISAO,
            **ator,
        )

    def aprovar(self, id_rascunho: str, *, comentario: str = "", **ator: str) -> RascunhoEditorial:
        rascunho = self.obter(id_rascunho)
        if ator.get("ator_id") and ator.get("ator_id") == rascunho.criado_por_id:
            raise WorkflowEditorialError("O autor do rascunho não pode aprovar a própria alteração.")
        return self._transicionar(
            id_rascunho,
            esperado=(StatusRascunho.EM_REVISAO,),
            novo=StatusRascunho.APROVADO,
            comentario=comentario,
            **ator,
        )

    def rejeitar(self, id_rascunho: str, *, comentario: str, **ator: str) -> RascunhoEditorial:
        if len(str(comentario).strip()) < 5:
            raise WorkflowEditorialError("A rejeição exige comentário com pelo menos 5 caracteres.")
        return self._transicionar(
            id_rascunho,
            esperado=(StatusRascunho.EM_REVISAO,),
            novo=StatusRascunho.REJEITADO,
            comentario=str(comentario).strip(),
            **ator,
        )

    def cancelar(self, id_rascunho: str, **ator: str) -> RascunhoEditorial:
        return self._transicionar(
            id_rascunho,
            esperado=(StatusRascunho.RASCUNHO, StatusRascunho.REJEITADO),
            novo=StatusRascunho.CANCELADO,
            **ator,
        )

    @staticmethod
    def _nova_versao(
        dados: Mapping[str, Any],
        *,
        versao_anterior: str,
        criada_em: str,
        origem: str,
    ) -> tuple[str, str]:
        payload = json.dumps(
            dados,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        material = "\n".join((versao_anterior, criada_em, origem, payload))
        return hashlib.sha256(material.encode("utf-8")).hexdigest(), payload

    @staticmethod
    def _inserir_auditoria(
        conexao: sqlite3.Connection,
        eventos: Sequence[Any],
    ) -> None:
        for evento in eventos:
            conexao.execute(
                """
                INSERT INTO auditoria_eventos (
                    id_evento, ocorrido_em, jogador, campo, acao,
                    valor_anterior_json, valor_novo_json, origem,
                    versao_anterior, versao_nova,
                    ator_email, ator_nome, ator_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evento.id_evento,
                    evento.ocorrido_em,
                    evento.jogador,
                    evento.campo,
                    evento.acao.value,
                    _json(evento.valor_anterior),
                    _json(evento.valor_novo),
                    evento.origem,
                    evento.versao_anterior,
                    evento.versao_nova,
                    evento.ator_email,
                    evento.ator_nome,
                    evento.ator_id,
                ),
            )

    def publicar(
        self,
        id_rascunho: str,
        *,
        repositorio: SqliteJogadoresRepository,
        ator_email: str = "",
        ator_nome: str = "",
        ator_id: str = "",
    ) -> str:
        """Publica revisão, auditoria e status do workflow em uma transação."""
        rascunho = self.obter(id_rascunho)
        if rascunho.status is not StatusRascunho.APROVADO:
            raise WorkflowEditorialError("Somente rascunhos aprovados podem ser publicados.")

        leitura = repositorio.carregar()
        if leitura.versao != rascunho.versao_base:
            raise ConflitoConcorrenciaError(rascunho.versao_base, leitura.versao)
        antes = copy.deepcopy(leitura.jogadores)
        if rascunho.jogador not in antes:
            raise WorkflowEditorialError("O jogador do rascunho não existe mais na base.")
        depois = copy.deepcopy(antes)
        depois[rascunho.jogador].update(_validar_alteracoes(rascunho.alteracoes))

        estrutural = validar_estrutura_bruta(depois)
        normalizado = validar_jogadores_normalizados(depois)
        if estrutural.possui_erros or normalizado.possui_erros:
            raise DataIntegrityError("A publicação foi bloqueada por falha de integridade.")

        origem = f"workflow_editorial:{id_rascunho}"
        criado_em = _agora()
        versao_nova, payload = self._nova_versao(
            depois,
            versao_anterior=rascunho.versao_base,
            criada_em=criado_em,
            origem=origem,
        )
        eventos = gerar_eventos_alteracao(
            antes,
            depois,
            origem=origem,
            versao_anterior=rascunho.versao_base,
            versao_nova=versao_nova,
            ocorrido_em=criado_em,
            ator_email=ator_email,
            ator_nome=ator_nome,
            ator_id=ator_id,
        )

        with closing(self._conectar()) as conexao:
            try:
                conexao.execute("BEGIN IMMEDIATE")
                linha = conexao.execute(
                    "SELECT versao_atual FROM jogadores_estado WHERE id = 1"
                ).fetchone()
                atual = str(linha["versao_atual"]) if linha else "ausente"
                if atual != rascunho.versao_base:
                    raise ConflitoConcorrenciaError(rascunho.versao_base, atual)
                status = conexao.execute(
                    "SELECT status FROM editorial_rascunhos WHERE id_rascunho = ?",
                    (id_rascunho,),
                ).fetchone()
                if status is None or str(status["status"]) != StatusRascunho.APROVADO.value:
                    raise WorkflowEditorialError("O rascunho deixou de estar aprovado.")

                conexao.execute(
                    """
                    INSERT INTO jogadores_revisoes (
                        versao, criada_em, origem, versao_anterior, payload_json,
                        ator_email, ator_nome, ator_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        versao_nova,
                        criado_em,
                        origem,
                        rascunho.versao_base,
                        payload,
                        ator_email,
                        ator_nome,
                        ator_id,
                    ),
                )
                conexao.execute(
                    "UPDATE jogadores_estado SET versao_atual = ? WHERE id = 1",
                    (versao_nova,),
                )
                self._inserir_auditoria(conexao, eventos)
                conexao.execute(
                    """
                    UPDATE editorial_rascunhos
                    SET status = ?, atualizado_em = ?, versao_publicada = ?
                    WHERE id_rascunho = ?
                    """,
                    (
                        StatusRascunho.PUBLICADO.value,
                        criado_em,
                        versao_nova,
                        id_rascunho,
                    ),
                )
                self._evento(
                    conexao,
                    id_rascunho=id_rascunho,
                    acao="publicado",
                    ator_email=ator_email,
                    ator_nome=ator_nome,
                    ator_id=ator_id,
                    comentario=versao_nova,
                )
                conexao.commit()
            except Exception:
                conexao.rollback()
                raise
        return versao_nova

    def eventos(self, id_rascunho: str) -> list[dict[str, str]]:
        with closing(self._conectar()) as conexao:
            linhas = conexao.execute(
                """
                SELECT ocorrido_em, acao, ator_email, ator_nome, ator_id, comentario
                FROM editorial_eventos
                WHERE id_rascunho = ?
                ORDER BY ocorrido_em ASC
                """,
                (id_rascunho,),
            ).fetchall()
        return [dict(linha) for linha in linhas]

    def rollback(
        self,
        *,
        repositorio: SqliteJogadoresRepository,
        versao_alvo: str,
        versao_esperada: str,
        ator_email: str = "",
        ator_nome: str = "",
        ator_id: str = "",
    ) -> str:
        """Cria uma nova revisão de rollback com auditoria na mesma transação."""
        antes = repositorio.carregar().jogadores
        alvo = repositorio.carregar_revisao(versao_alvo)
        origem = f"rollback_administrativo:{versao_alvo}"
        criado_em = _agora()
        versao_nova, payload = self._nova_versao(
            alvo,
            versao_anterior=versao_esperada,
            criada_em=criado_em,
            origem=origem,
        )
        eventos = gerar_eventos_alteracao(
            antes,
            alvo,
            origem=origem,
            versao_anterior=versao_esperada,
            versao_nova=versao_nova,
            ocorrido_em=criado_em,
            ator_email=ator_email,
            ator_nome=ator_nome,
            ator_id=ator_id,
        )
        with closing(self._conectar()) as conexao:
            try:
                conexao.execute("BEGIN IMMEDIATE")
                linha = conexao.execute(
                    "SELECT versao_atual FROM jogadores_estado WHERE id = 1"
                ).fetchone()
                atual = str(linha["versao_atual"]) if linha else "ausente"
                if atual != versao_esperada:
                    raise ConflitoConcorrenciaError(versao_esperada, atual)
                conexao.execute(
                    """
                    INSERT INTO jogadores_revisoes (
                        versao, criada_em, origem, versao_anterior, payload_json,
                        ator_email, ator_nome, ator_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        versao_nova,
                        criado_em,
                        origem,
                        versao_esperada,
                        payload,
                        ator_email,
                        ator_nome,
                        ator_id,
                    ),
                )
                conexao.execute(
                    "UPDATE jogadores_estado SET versao_atual = ? WHERE id = 1",
                    (versao_nova,),
                )
                self._inserir_auditoria(conexao, eventos)
                conexao.commit()
            except Exception:
                conexao.rollback()
                raise
        return versao_nova

