"""Persistência SQLite versionada para ambientes com disco durável.

O repositório mantém snapshots completos e imutáveis. Rollbacks criam uma nova
revisão; nenhuma versão histórica é apagada ou reescrita.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from hexa_audit import AuditoriaError, AuditoriaRepository, EventoAuditoria
from hexa_repository import (
    ConflitoConcorrenciaError,
    DataIntegrityError,
    JogadoresRepository,
    RegistroVersao,
    ResultadoLeitura,
    VERSAO_AUSENTE,
)

__all__ = [
    "RevisaoPersistencia",
    "SqliteAuditoriaRepository",
    "SqliteJogadoresRepository",
]


@dataclass(frozen=True, slots=True)
class RevisaoPersistencia:
    versao: str
    criada_em: str
    origem: str
    versao_anterior: str
    ator_email: str = ""
    ator_nome: str = ""
    ator_id: str = ""


class SqliteJogadoresRepository(JogadoresRepository):
    """Repositório transacional de snapshots completos em SQLite."""

    def __init__(self, caminho: Path) -> None:
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        self._inicializar()

    def _conectar(self) -> sqlite3.Connection:
        conexao = sqlite3.connect(
            self.caminho,
            timeout=5.0,
            isolation_level=None,
        )
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        conexao.execute("PRAGMA journal_mode = WAL")
        conexao.execute("PRAGMA synchronous = FULL")
        return conexao

    def _inicializar(self) -> None:
        with closing(self._conectar()) as conexao:
            conexao.executescript(
                """
                CREATE TABLE IF NOT EXISTS jogadores_revisoes (
                    versao TEXT PRIMARY KEY,
                    criada_em TEXT NOT NULL,
                    origem TEXT NOT NULL,
                    versao_anterior TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    ator_email TEXT NOT NULL DEFAULT '',
                    ator_nome TEXT NOT NULL DEFAULT '',
                    ator_id TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS jogadores_estado (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    versao_atual TEXT NOT NULL,
                    FOREIGN KEY (versao_atual)
                        REFERENCES jogadores_revisoes(versao)
                );

                CREATE INDEX IF NOT EXISTS idx_revisoes_criada_em
                    ON jogadores_revisoes(criada_em DESC);
                """
            )

    @staticmethod
    def _serializar(jogadores: Mapping[str, Any]) -> str:
        return json.dumps(
            jogadores,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @staticmethod
    def _versao(
        payload: str,
        *,
        versao_anterior: str,
        criada_em: str,
        origem: str,
    ) -> str:
        material = "\n".join(
            (versao_anterior, criada_em, origem, payload)
        )
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    @staticmethod
    def _validar_payload(payload: str) -> dict[str, Any]:
        try:
            dados = json.loads(payload)
        except json.JSONDecodeError as erro:
            raise DataIntegrityError(
                "A revisão persistida está corrompida e não foi carregada."
            ) from erro
        if not isinstance(dados, dict):
            raise DataIntegrityError(
                "A revisão persistida não contém um objeto de jogadores."
            )
        return dados

    def versao_atual(self) -> str:
        with closing(self._conectar()) as conexao:
            linha = conexao.execute(
                "SELECT versao_atual FROM jogadores_estado WHERE id = 1"
            ).fetchone()
        return str(linha["versao_atual"]) if linha else VERSAO_AUSENTE

    def carregar(self) -> ResultadoLeitura:
        with closing(self._conectar()) as conexao:
            linha = conexao.execute(
                """
                SELECT r.versao, r.payload_json
                FROM jogadores_estado e
                JOIN jogadores_revisoes r
                  ON r.versao = e.versao_atual
                WHERE e.id = 1
                """
            ).fetchone()
        if linha is None:
            raise DataIntegrityError(
                "O banco SQLite ainda não possui uma revisão ativa. "
                "Execute a migração inicial antes de ativá-lo."
            )
        dados = self._validar_payload(str(linha["payload_json"]))
        return ResultadoLeitura(
            jogadores=dados,
            versao=str(linha["versao"]),
        )

    def salvar(
        self,
        jogadores: Mapping[str, Any],
        *,
        versao_esperada: str | None = None,
        origem: str = "aplicacao",
        ator_email: str = "",
        ator_nome: str = "",
        ator_id: str = "",
    ) -> RegistroVersao:
        payload = self._serializar(jogadores)
        criado_em = datetime.now(timezone.utc).isoformat()
        origem_normalizada = str(origem or "aplicacao")

        conexao = self._conectar()
        try:
            conexao.execute("BEGIN IMMEDIATE")
            linha = conexao.execute(
                "SELECT versao_atual FROM jogadores_estado WHERE id = 1"
            ).fetchone()
            versao_atual = (
                str(linha["versao_atual"]) if linha else VERSAO_AUSENTE
            )
            if (
                versao_esperada is not None
                and versao_esperada != versao_atual
            ):
                raise ConflitoConcorrenciaError(
                    versao_esperada=versao_esperada,
                    versao_atual=versao_atual,
                )

            versao_nova = self._versao(
                payload,
                versao_anterior=versao_atual,
                criada_em=criado_em,
                origem=origem_normalizada,
            )
            conexao.execute(
                """
                INSERT OR IGNORE INTO jogadores_revisoes (
                    versao, criada_em, origem, versao_anterior, payload_json,
                    ator_email, ator_nome, ator_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    versao_nova,
                    criado_em,
                    origem_normalizada,
                    versao_atual,
                    payload,
                    str(ator_email),
                    str(ator_nome),
                    str(ator_id),
                ),
            )
            conexao.execute(
                """
                INSERT INTO jogadores_estado (id, versao_atual)
                VALUES (1, ?)
                ON CONFLICT(id) DO UPDATE
                    SET versao_atual = excluded.versao_atual
                """,
                (versao_nova,),
            )
            conexao.execute("COMMIT")
        except Exception:
            conexao.execute("ROLLBACK")
            raise
        finally:
            conexao.close()

        return RegistroVersao(
            versao=versao_nova,
            atualizado_em=criado_em,
            origem=origem_normalizada,
        )

    def listar_revisoes(self, limite: int = 50) -> list[RevisaoPersistencia]:
        limite_seguro = max(1, min(int(limite), 500))
        with closing(self._conectar()) as conexao:
            linhas = conexao.execute(
                """
                SELECT versao, criada_em, origem, versao_anterior,
                       ator_email, ator_nome, ator_id
                FROM jogadores_revisoes
                ORDER BY criada_em DESC
                LIMIT ?
                """,
                (limite_seguro,),
            ).fetchall()
        return [
            RevisaoPersistencia(
                versao=str(linha["versao"]),
                criada_em=str(linha["criada_em"]),
                origem=str(linha["origem"]),
                versao_anterior=str(linha["versao_anterior"]),
                ator_email=str(linha["ator_email"]),
                ator_nome=str(linha["ator_nome"]),
                ator_id=str(linha["ator_id"]),
            )
            for linha in linhas
        ]

    def carregar_revisao(self, versao: str) -> dict[str, Any]:
        with closing(self._conectar()) as conexao:
            linha = conexao.execute(
                "SELECT payload_json FROM jogadores_revisoes WHERE versao = ?",
                (str(versao),),
            ).fetchone()
        if linha is None:
            raise DataIntegrityError("A revisão solicitada não existe.")
        return self._validar_payload(str(linha["payload_json"]))

    def rollback(
        self,
        versao_alvo: str,
        *,
        versao_esperada: str,
        origem: str = "rollback_administrativo",
        ator_email: str = "",
        ator_nome: str = "",
        ator_id: str = "",
    ) -> RegistroVersao:
        """Restaura conteúdo histórico criando uma nova revisão auditável."""
        dados = self.carregar_revisao(versao_alvo)
        # Inclui a revisão-alvo na origem para preservar a trilha de decisão.
        origem_completa = f"{origem}:{versao_alvo}"
        return self.salvar(
            dados,
            versao_esperada=versao_esperada,
            origem=origem_completa,
            ator_email=ator_email,
            ator_nome=ator_nome,
            ator_id=ator_id,
        )


class SqliteAuditoriaRepository(AuditoriaRepository):
    """Auditoria append-only armazenada no mesmo banco SQLite."""

    def __init__(self, caminho: Path) -> None:
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._conectar()) as conexao:
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS auditoria_eventos (
                    id_evento TEXT PRIMARY KEY,
                    ocorrido_em TEXT NOT NULL,
                    jogador TEXT NOT NULL,
                    campo TEXT NOT NULL,
                    acao TEXT NOT NULL,
                    valor_anterior_json TEXT NOT NULL,
                    valor_novo_json TEXT NOT NULL,
                    origem TEXT NOT NULL,
                    versao_anterior TEXT NOT NULL,
                    versao_nova TEXT NOT NULL,
                    ator_email TEXT NOT NULL DEFAULT '',
                    ator_nome TEXT NOT NULL DEFAULT '',
                    ator_id TEXT NOT NULL DEFAULT ''
                )
                """
            )
            conexao.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_auditoria_jogador_data
                ON auditoria_eventos(jogador, ocorrido_em DESC)
                """
            )
            conexao.commit()

    def _conectar(self) -> sqlite3.Connection:
        conexao = sqlite3.connect(self.caminho, timeout=5.0)
        conexao.row_factory = sqlite3.Row
        return conexao

    def registrar(self, eventos: Sequence[EventoAuditoria]) -> None:
        if not eventos:
            return
        try:
            with closing(self._conectar()) as conexao:
                conexao.executemany(
                    """
                    INSERT INTO auditoria_eventos (
                        id_evento, ocorrido_em, jogador, campo, acao,
                        valor_anterior_json, valor_novo_json, origem,
                        versao_anterior, versao_nova,
                        ator_email, ator_nome, ator_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            evento.id_evento,
                            evento.ocorrido_em,
                            evento.jogador,
                            evento.campo,
                            evento.acao.value,
                            json.dumps(
                                evento.valor_anterior,
                                ensure_ascii=False,
                                default=str,
                            ),
                            json.dumps(
                                evento.valor_novo,
                                ensure_ascii=False,
                                default=str,
                            ),
                            evento.origem,
                            evento.versao_anterior,
                            evento.versao_nova,
                            evento.ator_email,
                            evento.ator_nome,
                            evento.ator_id,
                        )
                        for evento in eventos
                    ],
                )
                conexao.commit()
        except sqlite3.Error as erro:
            raise AuditoriaError(
                "Falha ao registrar a auditoria no banco SQLite."
            ) from erro

    def listar(
        self,
        *,
        jogador: str | None = None,
        limite: int | None = None,
    ) -> list[EventoAuditoria]:
        limite_seguro = 100 if limite is None else max(1, min(int(limite), 1000))
        consulta = """
            SELECT * FROM auditoria_eventos
        """
        parametros: list[Any] = []
        if jogador:
            consulta += " WHERE jogador = ?"
            parametros.append(str(jogador))
        consulta += " ORDER BY ocorrido_em DESC LIMIT ?"
        parametros.append(limite_seguro)

        try:
            with closing(self._conectar()) as conexao:
                linhas = conexao.execute(consulta, parametros).fetchall()
        except sqlite3.Error as erro:
            raise AuditoriaError(
                "Falha ao consultar a auditoria no banco SQLite."
            ) from erro

        from hexa_audit import AcaoAuditoria

        return [
            EventoAuditoria(
                id_evento=str(linha["id_evento"]),
                ocorrido_em=str(linha["ocorrido_em"]),
                jogador=str(linha["jogador"]),
                campo=str(linha["campo"]),
                acao=AcaoAuditoria(str(linha["acao"])),
                valor_anterior=json.loads(str(linha["valor_anterior_json"])),
                valor_novo=json.loads(str(linha["valor_novo_json"])),
                origem=str(linha["origem"]),
                versao_anterior=str(linha["versao_anterior"]),
                versao_nova=str(linha["versao_nova"]),
                ator_email=str(linha["ator_email"]),
                ator_nome=str(linha["ator_nome"]),
                ator_id=str(linha["ator_id"]),
            )
            for linha in linhas
        ]
