"""Índices transparentes e rankings sazonais derivados.

Nenhum indicador deste módulo substitui a avaliação editorial. Os rankings
são objetivos, reproduzíveis e recalculados sempre a partir dos totais anuais.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from hexa_estatisticas import calcular_indices

__all__ = [
    "AMBITOS_RANKING",
    "INDICADORES_RANKING",
    "IndicadorRanking",
    "construir_painel_rankings",
    "recalcular_indices_rankings",
    "validar_painel_rankings",
]

AMBITOS_RANKING: tuple[str, ...] = ("clube", "selecao", "combinado")


@dataclass(frozen=True, slots=True)
class IndicadorRanking:
    chave: str
    rotulo: str
    categoria: str
    origem: str
    formato: str
    ordem_crescente: bool = False
    minimo_minutos: int = 0


INDICADORES_RANKING: tuple[IndicadorRanking, ...] = (
    IndicadorRanking("jogos", "Jogos", "Participação", "total", "inteiro"),
    IndicadorRanking("minutos", "Minutos", "Participação", "total", "inteiro"),
    IndicadorRanking("titular", "Titular", "Participação", "total", "inteiro"),
    IndicadorRanking(
        "minutos_por_jogo",
        "Minutos por jogo",
        "Participação",
        "indice",
        "decimal_1",
    ),
    IndicadorRanking(
        "titular_percentual",
        "Titular %",
        "Participação",
        "indice",
        "percentual_1",
    ),
    IndicadorRanking("gols", "Gols", "Ataque", "total", "inteiro"),
    IndicadorRanking("assistencias", "Assistências", "Ataque", "total", "inteiro"),
    IndicadorRanking(
        "gols_por_90",
        "Gols por 90",
        "Ataque",
        "indice",
        "decimal_2",
        minimo_minutos=450,
    ),
    IndicadorRanking(
        "assistencias_por_90",
        "Assistências por 90",
        "Ataque",
        "indice",
        "decimal_2",
        minimo_minutos=450,
    ),
    IndicadorRanking(
        "participacoes_gol_por_90",
        "Participações em gol por 90",
        "Ataque",
        "indice",
        "decimal_2",
        minimo_minutos=450,
    ),
    IndicadorRanking("chutes", "Chutes", "Ataque", "total", "inteiro"),
    IndicadorRanking(
        "chutes_no_alvo_percentual",
        "Chutes no alvo %",
        "Ataque",
        "indice",
        "percentual_1",
        minimo_minutos=450,
    ),
    IndicadorRanking("passes", "Passes", "Passe", "total", "inteiro"),
    IndicadorRanking(
        "passes_certos_percentual",
        "Passes certos %",
        "Passe",
        "total",
        "percentual_1",
        minimo_minutos=450,
    ),
    IndicadorRanking("passes_chave", "Passes-chave", "Passe", "total", "inteiro"),
    IndicadorRanking("dribles", "Dribles", "Drible", "total", "inteiro"),
    IndicadorRanking("desarmes", "Desarmes", "Defesa", "total", "inteiro"),
    IndicadorRanking(
        "interceptacoes",
        "Interceptações",
        "Defesa",
        "total",
        "inteiro",
    ),
    IndicadorRanking(
        "cabeceios_ganhos",
        "Cabeceios ganhos",
        "Defesa",
        "total",
        "inteiro",
    ),
    IndicadorRanking(
        "erros",
        "Menos erros",
        "Defesa",
        "total",
        "inteiro",
        ordem_crescente=True,
        minimo_minutos=450,
    ),
    IndicadorRanking(
        "erros_geraram_gol",
        "Menos erros que geraram gol",
        "Defesa",
        "total",
        "inteiro",
        ordem_crescente=True,
        minimo_minutos=450,
    ),
    IndicadorRanking(
        "cartoes_amarelos",
        "Menos cartões amarelos",
        "Disciplina",
        "total",
        "inteiro",
        ordem_crescente=True,
        minimo_minutos=450,
    ),
    IndicadorRanking(
        "cartoes_vermelhos",
        "Menos cartões vermelhos",
        "Disciplina",
        "total",
        "inteiro",
        ordem_crescente=True,
        minimo_minutos=450,
    ),
)


def _valor_indicador(
    total: Mapping[str, Any],
    indicador: IndicadorRanking,
) -> float | None:
    if indicador.origem == "indice":
        indices = total.get("indices")
        if not isinstance(indices, Mapping):
            return None
        valor = indices.get(indicador.chave)
    else:
        valor = total.get(indicador.chave)
    if valor is None or isinstance(valor, bool):
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _ranking_indicador(
    totais: Sequence[Mapping[str, Any]],
    indicador: IndicadorRanking,
    *,
    ambito: str,
    limite: int,
) -> list[dict[str, Any]]:
    elegiveis: list[tuple[Mapping[str, Any], float]] = []
    for total in totais:
        if total.get("ambito") != ambito:
            continue
        minutos = int(total.get("minutos") or 0)
        if minutos < indicador.minimo_minutos:
            continue
        valor = _valor_indicador(total, indicador)
        if valor is None:
            continue
        elegiveis.append((total, valor))

    elegiveis.sort(
        key=lambda par: (
            par[1] if indicador.ordem_crescente else -par[1],
            str(par[0].get("nome") or "").casefold(),
        )
    )

    resultado: list[dict[str, Any]] = []
    posicao = 0
    valor_anterior: float | None = None
    for indice, (total, valor) in enumerate(elegiveis[:limite], start=1):
        if valor_anterior is None or valor != valor_anterior:
            posicao = indice
            valor_anterior = valor
        resultado.append(
            {
                "posicao": posicao,
                "id_atleta": str(total.get("id_atleta") or ""),
                "nome": str(total.get("nome") or ""),
                "ambito": ambito,
                "valor": valor,
                "minutos": int(total.get("minutos") or 0),
                "jogos": int(total.get("jogos") or 0),
            }
        )
    return resultado


def construir_painel_rankings(
    totais: Sequence[Mapping[str, Any]],
    *,
    temporada: int,
    limite: int = 20,
    atualizado_em_utc: str | None = None,
) -> dict[str, Any]:
    """Constrói rankings por âmbito e indicador, com metodologia explícita."""
    limite_seguro = max(1, min(int(limite), 100))
    rankings: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for ambito in AMBITOS_RANKING:
        rankings[ambito] = {
            indicador.chave: _ranking_indicador(
                totais,
                indicador,
                ambito=ambito,
                limite=limite_seguro,
            )
            for indicador in INDICADORES_RANKING
        }

    carimbo = atualizado_em_utc or datetime.now(timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )
    return {
        "schema_version": "1.0",
        "temporada": int(temporada),
        "recalculado_em_utc": carimbo,
        "metodologia": {
            "nota_composta": False,
            "limite_por_ranking": limite_seguro,
            "criterio_desempate": "nome do atleta em ordem alfabética",
            "minimo_minutos_indices_eficiencia": 450,
            "ambitos": list(AMBITOS_RANKING),
        },
        "indicadores": [
            {
                "chave": item.chave,
                "rotulo": item.rotulo,
                "categoria": item.categoria,
                "origem": item.origem,
                "formato": item.formato,
                "ordem_crescente": item.ordem_crescente,
                "minimo_minutos": item.minimo_minutos,
            }
            for item in INDICADORES_RANKING
        ],
        "rankings": rankings,
    }


def recalcular_indices_rankings(
    documento: Mapping[str, Any],
    *,
    limite: int = 20,
) -> dict[str, Any]:
    """Recalcula índices de cada total e substitui somente dados derivados."""
    resultado = dict(documento)
    totais_brutos = documento.get("totais")
    if not isinstance(totais_brutos, list):
        raise ValueError("O documento de temporada não possui totais válidos.")

    totais: list[dict[str, Any]] = []
    for item in totais_brutos:
        if not isinstance(item, Mapping):
            continue
        total = dict(item)
        total["indices"] = calcular_indices(total)
        totais.append(total)

    temporada = int(documento.get("temporada") or 0)
    if not 2000 <= temporada <= 2100:
        raise ValueError("Temporada inválida para recalcular rankings.")

    carimbo = str(documento.get("atualizado_em_utc") or "").strip() or None
    resultado["totais"] = totais
    resultado["indices_rankings"] = construir_painel_rankings(
        totais,
        temporada=temporada,
        limite=limite,
        atualizado_em_utc=carimbo,
    )
    return resultado


def validar_painel_rankings(painel: Mapping[str, Any]) -> list[str]:
    problemas: list[str] = []
    if painel.get("schema_version") != "1.0":
        problemas.append("schema_version de índices e rankings precisa ser 1.0.")
    if not isinstance(painel.get("rankings"), Mapping):
        problemas.append("rankings precisa ser um objeto.")
    if not isinstance(painel.get("indicadores"), list):
        problemas.append("indicadores precisa ser uma lista.")
    metodologia = painel.get("metodologia")
    if not isinstance(metodologia, Mapping):
        problemas.append("metodologia precisa ser um objeto.")
    elif metodologia.get("nota_composta") is not False:
        problemas.append("nota_composta precisa permanecer falsa.")
    return problemas
