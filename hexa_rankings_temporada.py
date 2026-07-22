"""Painel público de índices e rankings sazonais."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import streamlit as st

from hexa_components import (
    ColunaTabelaExecutiva,
    KPI,
    render_cabecalho_secao,
    render_kpis,
    render_tabela_executiva,
)
from hexa_dados_esportivos import (
    DocumentoEsportivoError,
    carregar_documento_anual,
    listar_anos_disponiveis,
)
from hexa_indices_rankings import (
    AMBITOS_RANKING,
    INDICADORES_RANKING,
    recalcular_indices_rankings,
)

__all__ = ["render_indices_rankings_temporada"]


_ROTULOS_AMBITO = {
    "clube": "Clube",
    "selecao": "Seleção",
    "combinado": "Clube + Seleção",
}


def _indicadores_por_categoria() -> dict[str, list[Any]]:
    resultado: dict[str, list[Any]] = {}
    for indicador in INDICADORES_RANKING:
        resultado.setdefault(indicador.categoria, []).append(indicador)
    return resultado


def _painel_documento(documento: Mapping[str, Any]) -> Mapping[str, Any]:
    painel = documento.get("indices_rankings")
    if isinstance(painel, Mapping):
        return painel
    recalculado = recalcular_indices_rankings(documento)
    painel = recalculado.get("indices_rankings")
    return painel if isinstance(painel, Mapping) else {}


def render_indices_rankings_temporada(
    *,
    jogadores: Mapping[str, Mapping[str, Any]],
    temporadas_dir: Path,
) -> None:
    """Exibe rankings objetivos derivados dos arquivos anuais."""
    render_cabecalho_secao(
        "Índices e rankings sazonais",
        (
            "Leitura objetiva dos dados atualizados. Os rankings não substituem "
            "as avaliações editoriais de Vini e Beto."
        ),
    )

    anos = listar_anos_disponiveis(temporadas_dir, prefixo="temporada")
    if not anos:
        st.info(
            "Ainda não há temporadas estatísticas publicadas para gerar rankings."
        )
        return

    col_ano, col_ambito, col_categoria = st.columns(3, gap="medium")
    with col_ano:
        temporada = st.selectbox(
            "Temporada dos rankings",
            anos,
            key="ranking_temporada",
        )
    with col_ambito:
        ambito = st.selectbox(
            "Âmbito",
            AMBITOS_RANKING,
            format_func=_ROTULOS_AMBITO.__getitem__,
            index=2,
            key="ranking_ambito",
        )

    categorias = _indicadores_por_categoria()
    with col_categoria:
        categoria = st.selectbox(
            "Categoria",
            tuple(categorias),
            key="ranking_categoria",
        )

    indicadores = categorias[categoria]
    indicador = st.selectbox(
        "Indicador",
        indicadores,
        format_func=lambda item: item.rotulo,
        key="ranking_indicador",
    )

    try:
        documento = carregar_documento_anual(
            temporadas_dir / f"temporada_{temporada}.json"
        )
        painel = _painel_documento(documento)
    except (DocumentoEsportivoError, ValueError) as erro:
        st.warning(str(erro))
        return

    rankings = painel.get("rankings")
    if not isinstance(rankings, Mapping):
        st.warning("O arquivo da temporada não possui rankings válidos.")
        return
    rankings_ambito = rankings.get(ambito)
    if not isinstance(rankings_ambito, Mapping):
        st.info("Ainda não há ranking para o âmbito selecionado.")
        return
    linhas = rankings_ambito.get(indicador.chave)
    if not isinstance(linhas, list) or not linhas:
        st.info(
            "Não há atletas elegíveis para este indicador e âmbito. "
            "Índices de eficiência exigem ao menos 450 minutos."
        )
        return

    por_id = {
        str(dados.get("id_atleta") or ""): dados
        for dados in jogadores.values()
        if str(dados.get("id_atleta") or "")
    }
    registros: list[dict[str, Any]] = []
    for linha in linhas:
        if not isinstance(linha, Mapping):
            continue
        dados = por_id.get(str(linha.get("id_atleta") or ""), {})
        registros.append(
            {
                "Posição": int(linha.get("posicao") or 0),
                "Nome": str(linha.get("nome") or ""),
                "Posição editorial": str(dados.get("posicao") or "Não informada"),
                "Valor": linha.get("valor"),
                "Jogos": int(linha.get("jogos") or 0),
                "Minutos": int(linha.get("minutos") or 0),
            }
        )

    metodologia = painel.get("metodologia")
    minimo = indicador.minimo_minutos
    contexto_minimo = (
        f"Mínimo de {minimo} minutos para elegibilidade."
        if minimo
        else "Sem corte mínimo de minutos."
    )
    render_kpis(
        (
            KPI("Temporada", temporada, "Arquivo anual ativo", "informativo"),
            KPI(
                "Âmbito",
                _ROTULOS_AMBITO[ambito],
                "Origem dos dados comparados",
            ),
            KPI(
                "Atletas ranqueados",
                len(registros),
                contexto_minimo,
                "destaque",
            ),
        ),
        titulo="Resumo do ranking",
        rotulo_aria="Resumo do ranking sazonal selecionado",
    )

    render_tabela_executiva(
        registros,
        (
            ColunaTabelaExecutiva(
                "Posição",
                "#",
                formato="inteiro",
                alinhamento="centro",
                largura=72,
            ),
            ColunaTabelaExecutiva(
                "Nome",
                "Atleta",
                fixada="left",
                largura="28%",
            ),
            ColunaTabelaExecutiva(
                "Posição editorial",
                "Posição",
                largura="22%",
            ),
            ColunaTabelaExecutiva(
                "Valor",
                indicador.rotulo,
                formato=indicador.formato,
                alinhamento="direita",
                destaque=True,
            ),
            ColunaTabelaExecutiva(
                "Jogos",
                "Jogos",
                formato="inteiro",
                alinhamento="direita",
            ),
            ColunaTabelaExecutiva(
                "Minutos",
                "Minutos",
                formato="inteiro",
                alinhamento="direita",
            ),
        ),
        rotulo_aria=f"Ranking de {indicador.rotulo} em {temporada}",
        legenda=(
            f"{indicador.rotulo}, âmbito {_ROTULOS_AMBITO[ambito]}, "
            f"temporada {temporada}"
        ),
        chave=f"ranking_{temporada}_{ambito}_{indicador.chave}",
        mostrar_barra=False,
        altura_maxima=560,
    )

    criterio = ""
    if isinstance(metodologia, Mapping):
        criterio = str(metodologia.get("criterio_desempate") or "")
    st.caption(
        "Metodologia: dados objetivos, sem nota composta. "
        f"{contexto_minimo} "
        f"Desempate: {criterio or 'nome do atleta em ordem alfabética'}."
    )
