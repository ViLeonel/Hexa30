"""Agenda inteligente de clubes e Seleção.

A camada consolida calendários anuais sem expor detalhes internos na interface.
A associação é exata após normalização e pode usar IDs ou aliases explícitos.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

__all__ = [
    "AgendaIntegrityError",
    "EscopoAgenda",
    "FiltroAgenda",
    "carregar_aliases_equipes",
    "listar_competicoes_agenda",
    "normalizar_identidade_equipe",
    "proximos_jogos_inteligentes",
]

EscopoAgenda = Literal["todos", "clube", "selecao"]
_STATUS_EXCLUIDOS = frozenset(
    {"cancelado", "cancelada", "adiado", "adiada", "encerrado", "encerrada"}
)


class AgendaIntegrityError(ValueError):
    """Indica configuração inválida da agenda inteligente."""


@dataclass(frozen=True, slots=True)
class FiltroAgenda:
    escopo: EscopoAgenda = "todos"
    competicao: str = ""

    def __post_init__(self) -> None:
        if self.escopo not in {"todos", "clube", "selecao"}:
            raise AgendaIntegrityError("Escopo de agenda inválido.")


def normalizar_identidade_equipe(valor: Any) -> str:
    """Produz uma chave estável sem aplicar aproximação arriscada."""
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    texto = "".join(caractere for caractere in texto if not unicodedata.combining(caractere))
    texto = texto.casefold().strip()
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def carregar_aliases_equipes(caminho: Path | None) -> dict[str, str]:
    """Carrega aliases explícitos no formato alias normalizado -> nome canônico."""
    if caminho is None or not Path(caminho).exists():
        return {}
    try:
        documento = json.loads(Path(caminho).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as erro:
        raise AgendaIntegrityError(
            f"{Path(caminho).name} está inválido e não foi alterado."
        ) from erro
    if not isinstance(documento, Mapping):
        raise AgendaIntegrityError("O arquivo de aliases precisa conter um objeto JSON.")
    if documento.get("schema_version") not in (None, "1.0"):
        raise AgendaIntegrityError("schema_version de aliases precisa ser 1.0.")

    equipes = documento.get("equipes", {})
    if not isinstance(equipes, Mapping):
        raise AgendaIntegrityError("equipes precisa ser um objeto.")

    resultado: dict[str, str] = {}
    for canonico, aliases in equipes.items():
        nome_canonico = str(canonico or "").strip()
        if not nome_canonico:
            continue
        chave_canonica = normalizar_identidade_equipe(nome_canonico)
        resultado[chave_canonica] = chave_canonica
        if isinstance(aliases, str):
            valores: Iterable[Any] = (aliases,)
        elif isinstance(aliases, list):
            valores = aliases
        else:
            continue
        for alias in valores:
            chave_alias = normalizar_identidade_equipe(alias)
            if chave_alias:
                resultado[chave_alias] = chave_canonica
    return resultado


def _canonico(valor: Any, aliases: Mapping[str, str]) -> str:
    chave = normalizar_identidade_equipe(valor)
    return aliases.get(chave, chave)


def _identidades_jogador(
    jogador: Mapping[str, Any],
    aliases: Mapping[str, str],
    nome_selecao: str,
) -> tuple[set[str], set[str], set[str], set[str]]:
    clubes = {
        _canonico(valor, aliases)
        for valor in (
            jogador.get("clube"),
            jogador.get("tm_clube"),
            jogador.get("clube_atual"),
        )
        if str(valor or "").strip()
    }
    selecoes = {_canonico(nome_selecao, aliases)}
    ids_clube = {
        str(valor).strip().casefold()
        for valor in (jogador.get("clube_id"), jogador.get("tm_clube_id"))
        if str(valor or "").strip()
    }
    ids_selecao = {
        str(valor).strip().casefold()
        for valor in (jogador.get("selecao_id"), "BRA")
        if str(valor or "").strip()
    }
    return clubes, selecoes, ids_clube, ids_selecao


def _equipes_jogo(
    jogo: Mapping[str, Any],
    aliases: Mapping[str, str],
) -> tuple[set[str], set[str]]:
    nomes = {
        _canonico(jogo.get("mandante"), aliases),
        _canonico(jogo.get("visitante"), aliases),
    }
    ids = {
        str(valor).strip().casefold()
        for valor in (jogo.get("mandante_id"), jogo.get("visitante_id"))
        if str(valor or "").strip()
    }
    return {nome for nome in nomes if nome}, ids


def _origem_jogo(
    *,
    jogo: Mapping[str, Any],
    jogador: Mapping[str, Any],
    aliases: Mapping[str, str],
    nome_selecao: str,
) -> str | None:
    clubes, selecoes, ids_clube, ids_selecao = _identidades_jogador(
        jogador, aliases, nome_selecao
    )
    nomes_jogo, ids_jogo = _equipes_jogo(jogo, aliases)
    clube_encontrado = bool(clubes & nomes_jogo or ids_clube & ids_jogo)
    selecao_encontrada = bool(selecoes & nomes_jogo or ids_selecao & ids_jogo)
    if clube_encontrado:
        return "clube"
    if selecao_encontrada:
        return "selecao"
    return None


def _chave_deduplicacao(jogo: Mapping[str, Any]) -> tuple[str, ...]:
    id_jogo = str(jogo.get("id_jogo") or "").strip()
    if id_jogo:
        return ("id", id_jogo.casefold())
    return (
        "dados",
        str(jogo.get("data") or ""),
        str(jogo.get("hora") or ""),
        normalizar_identidade_equipe(jogo.get("competicao")),
        normalizar_identidade_equipe(jogo.get("mandante")),
        normalizar_identidade_equipe(jogo.get("visitante")),
    )


def _iterar_jogos(
    documentos: Iterable[Mapping[str, Any]],
) -> Iterable[Mapping[str, Any]]:
    for documento in documentos:
        jogos = documento.get("jogos")
        if not isinstance(jogos, list):
            continue
        for jogo in jogos:
            if isinstance(jogo, Mapping):
                yield jogo


def proximos_jogos_inteligentes(
    *,
    jogador: Mapping[str, Any],
    calendarios: Iterable[Mapping[str, Any]],
    hoje: date | None = None,
    limite: int = 3,
    filtro: FiltroAgenda | None = None,
    aliases: Mapping[str, str] | None = None,
    nome_selecao: str = "Brasil",
) -> list[dict[str, str]]:
    """Consolida calendários e retorna apenas data, competição e confronto."""
    referencia = hoje or date.today()
    filtro_ativo = filtro or FiltroAgenda()
    aliases_ativos = aliases or {}
    competicao_filtro = normalizar_identidade_equipe(filtro_ativo.competicao)
    unicos: dict[tuple[str, ...], tuple[date, str, dict[str, str]]] = {}

    for jogo in _iterar_jogos(calendarios):
        status = str(jogo.get("status") or "agendado").strip().casefold()
        if status in _STATUS_EXCLUIDOS:
            continue
        try:
            data_jogo = date.fromisoformat(str(jogo.get("data") or "")[:10])
        except ValueError:
            continue
        if data_jogo < referencia:
            continue

        origem = _origem_jogo(
            jogo=jogo,
            jogador=jogador,
            aliases=aliases_ativos,
            nome_selecao=nome_selecao,
        )
        if origem is None:
            continue
        if filtro_ativo.escopo != "todos" and origem != filtro_ativo.escopo:
            continue

        competicao = str(jogo.get("competicao") or "").strip()
        if competicao_filtro and (
            normalizar_identidade_equipe(competicao) != competicao_filtro
        ):
            continue
        mandante = str(jogo.get("mandante") or "").strip()
        visitante = str(jogo.get("visitante") or "").strip()
        if not competicao or not mandante or not visitante:
            continue

        publico = {
            "data": data_jogo.isoformat(),
            "competicao": competicao,
            "confronto": f"{mandante} x {visitante}",
        }
        chave = _chave_deduplicacao(jogo)
        hora = str(jogo.get("hora") or "")
        atual = unicos.get(chave)
        candidato = (data_jogo, hora, publico)
        if atual is None or candidato[:2] < atual[:2]:
            unicos[chave] = candidato

    ordenados = sorted(
        unicos.values(),
        key=lambda item: (
            item[0],
            item[1],
            item[2]["competicao"].casefold(),
            item[2]["confronto"].casefold(),
        ),
    )
    return [item[2] for item in ordenados[: max(0, int(limite))]]


def listar_competicoes_agenda(
    *,
    jogador: Mapping[str, Any],
    calendarios: Iterable[Mapping[str, Any]],
    hoje: date | None = None,
    escopo: EscopoAgenda = "todos",
    aliases: Mapping[str, str] | None = None,
    nome_selecao: str = "Brasil",
) -> tuple[str, ...]:
    """Lista competições futuras aplicáveis ao atleta, sem duplicidade."""
    jogos = proximos_jogos_inteligentes(
        jogador=jogador,
        calendarios=calendarios,
        hoje=hoje,
        limite=10_000,
        filtro=FiltroAgenda(escopo=escopo),
        aliases=aliases,
        nome_selecao=nome_selecao,
    )
    return tuple(
        sorted(
            {jogo["competicao"] for jogo in jogos if jogo["competicao"]},
            key=str.casefold,
        )
    )
