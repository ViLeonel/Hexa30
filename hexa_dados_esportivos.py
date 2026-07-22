"""Leitura segura dos documentos esportivos sazonais usados pela ficha do atleta."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any

from hexa_agenda import (
    EscopoAgenda,
    FiltroAgenda,
    carregar_aliases_equipes,
    listar_competicoes_agenda,
    proximos_jogos_inteligentes,
)

__all__ = [
    "DocumentoEsportivoError",
    "carregar_competicoes_agenda",
    "carregar_documento_anual",
    "carregar_proximos_jogos",
    "carregar_totais_atleta",
    "listar_anos_disponiveis",
]


class DocumentoEsportivoError(RuntimeError):
    """Indica que um arquivo sazonal existe, mas não pode ser usado com segurança."""


def listar_anos_disponiveis(diretorio: Path, prefixo: str) -> tuple[int, ...]:
    """Lista anos com documento JSON válido pelo nome, do mais recente ao mais antigo."""
    caminho = Path(diretorio)
    if not caminho.exists():
        return ()
    padrao = re.compile(rf"^{re.escape(prefixo)}_(\d{{4}})\.json$")
    anos: set[int] = set()
    for arquivo in caminho.iterdir():
        if not arquivo.is_file():
            continue
        correspondencia = padrao.match(arquivo.name)
        if correspondencia:
            anos.add(int(correspondencia.group(1)))
    return tuple(sorted(anos, reverse=True))


def carregar_documento_anual(
    diretorio: Path,
    prefixo: str,
    ano: int,
) -> dict[str, Any] | None:
    """Carrega um documento anual sem reparar ou sobrescrever conteúdo inválido."""
    caminho = Path(diretorio) / f"{prefixo}_{int(ano)}.json"
    if not caminho.exists():
        return None
    try:
        documento = json.loads(caminho.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as erro:
        raise DocumentoEsportivoError(
            f"{caminho.name} está inválido e não foi alterado."
        ) from erro
    if not isinstance(documento, dict):
        raise DocumentoEsportivoError(
            f"{caminho.name} precisa conter um objeto JSON."
        )
    return documento


def carregar_totais_atleta(
    *,
    diretorio: Path,
    temporada: int,
    id_atleta: str,
) -> dict[str, Mapping[str, Any]]:
    """Retorna totais de clube, Seleção e combinado indexados por âmbito."""
    documento = carregar_documento_anual(diretorio, "temporada", temporada)
    if documento is None:
        return {}
    totais = documento.get("totais")
    if not isinstance(totais, list):
        raise DocumentoEsportivoError(
            f"temporada_{int(temporada)}.json não possui totais válidos."
        )
    resultado: dict[str, Mapping[str, Any]] = {}
    for item in totais:
        if not isinstance(item, Mapping):
            continue
        if str(item.get("id_atleta") or "") != str(id_atleta):
            continue
        ambito = str(item.get("ambito") or "").strip().casefold()
        if ambito in {"clube", "selecao", "combinado"}:
            resultado[ambito] = item
    return resultado


def _carregar_calendarios_ativos(
    diretorio: Path,
    *,
    hoje: date,
) -> list[dict[str, Any]]:
    documentos: list[dict[str, Any]] = []
    for ano in listar_anos_disponiveis(diretorio, "calendario"):
        if ano < hoje.year:
            continue
        documento = carregar_documento_anual(diretorio, "calendario", ano)
        if documento is not None:
            documentos.append(documento)
    return documentos


def carregar_competicoes_agenda(
    *,
    jogador: Mapping[str, Any],
    diretorio: Path,
    hoje: date | None = None,
    escopo: EscopoAgenda = "todos",
) -> tuple[str, ...]:
    """Lista competições futuras aplicáveis ao atleta."""
    referencia = hoje or date.today()
    try:
        aliases = carregar_aliases_equipes(Path(diretorio) / "aliases_equipes.json")
        documentos = _carregar_calendarios_ativos(Path(diretorio), hoje=referencia)
        return listar_competicoes_agenda(
            jogador=jogador,
            calendarios=documentos,
            hoje=referencia,
            escopo=escopo,
            aliases=aliases,
        )
    except ValueError as erro:
        raise DocumentoEsportivoError(str(erro)) from erro


def carregar_proximos_jogos(
    *,
    jogador: Mapping[str, Any],
    diretorio: Path,
    hoje: date | None = None,
    limite: int = 3,
    escopo: EscopoAgenda = "todos",
    competicao: str = "",
) -> list[dict[str, str]]:
    """Combina calendários, aliases e filtros e devolve os próximos jogos."""
    referencia = hoje or date.today()
    try:
        aliases = carregar_aliases_equipes(Path(diretorio) / "aliases_equipes.json")
        documentos = _carregar_calendarios_ativos(Path(diretorio), hoje=referencia)
        return proximos_jogos_inteligentes(
            jogador=jogador,
            calendarios=documentos,
            hoje=referencia,
            limite=limite,
            filtro=FiltroAgenda(escopo=escopo, competicao=competicao),
            aliases=aliases,
        )
    except ValueError as erro:
        raise DocumentoEsportivoError(str(erro)) from erro
