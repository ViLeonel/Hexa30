"""Componentes visuais reutilizáveis do aplicativo."""

from __future__ import annotations

import html
from collections.abc import Mapping
from typing import Any

import streamlit as st

from data import (
    extrair_altura_metros,
    formatar_valor_milhoes,
    percentual_do_pico,
    valor_mercado_atual,
    valor_mercado_maximo,
)
from taticas import ABREVIACOES, indice_adaptabilidade


def _esc(valor: Any, padrao: str = "N/A") -> str:
    texto = padrao if valor in (None, "", []) else str(valor)
    return html.escape(texto)


def render_cabecalho(titulo: str, subtitulo: str) -> None:
    st.markdown(f'<h1 class="app-title">{_esc(titulo)}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="project-subtitle">{_esc(subtitulo)}</p>', unsafe_allow_html=True)


def render_campo(
    layout: Mapping[str, tuple[list[str], str, str, str, str]],
    escalados: Mapping[str, str],
    jogadores: Mapping[str, Mapping[str, Any]],
) -> None:
    cards: list[str] = []
    cores = {0: "#22C55E", 1: "#EAB308"}

    for slot, (permitidas, padrao, left, bottom, tag) in layout.items():
        nome = escalados.get(slot, padrao)
        dados = jogadores.get(nome, {"nome": nome, "nota_vini": 0.0, "nota_roberto": 0.0})
        indice = indice_adaptabilidade(dados, permitidas)
        cor = cores.get(indice, "#F97316" if indice >= 2 else "#EF4444")
        nota_vini = float(dados.get("nota_vini") or 0.0)
        nota_roberto = float(dados.get("nota_roberto") or 0.0)

        cards.append(
            f'<div class="player-node" style="left:{left};bottom:{bottom};">'
            f'<div class="player-card-pitch" style="border-color:{cor}!important;">'
            f'<div class="player-pos-tag">{_esc(tag)}</div>'
            f'<div class="player-name-tag" title="{_esc(dados.get("nome", nome))}">{_esc(dados.get("nome", nome))}</div>'
            f'<div class="player-rating-tag">★ {nota_vini:.1f} / {nota_roberto:.1f}</div>'
            "</div></div>"
        )

    campo = (
        '<div class="pitch-container">'
        '<div class="pitch-line-center"></div>'
        '<div class="pitch-circle"></div>'
        '<div class="pitch-penalty-top"></div>'
        '<div class="pitch-penalty-bottom"></div>'
        f'{"".join(cards)}'
        "</div>"
    )
    st.markdown(campo, unsafe_allow_html=True)


def render_legenda_adaptabilidade() -> None:
    st.markdown(
        """
        <div class="legend-box">
            <div class="legend-item"><span class="legend-dot" style="background:#22C55E"></span><b>Verde:</b> função primária</div>
            <div class="legend-item"><span class="legend-dot" style="background:#EAB308"></span><b>Amarela:</b> função secundária</div>
            <div class="legend-item"><span class="legend-dot" style="background:#F97316"></span><b>Laranja:</b> função terciária</div>
            <div class="legend-item"><span class="legend-dot" style="background:#EF4444"></span><b>Vermelha:</b> incompatibilidade</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def calcular_resumo_elenco(titulares: list[Mapping[str, Any]]) -> dict[str, float | int]:
    idades = [int(j.get("idade", 0)) for j in titulares if j.get("idade")]
    alturas = [extrair_altura_metros(j.get("tm_altura"), 0.0) for j in titulares]
    alturas_validas = [v for v in alturas if v > 0]
    valores_atuais = [valor_mercado_atual(j) for j in titulares]
    valores_atuais_validos = [v for v in valores_atuais if v > 0]
    valores_maximos = [valor_mercado_maximo(j) for j in titulares]
    valores_maximos_validos = [v for v in valores_maximos if v > 0]

    return {
        "idade_2026": sum(idades) / len(idades) if idades else 0.0,
        "idade_2030": (sum(idades) / len(idades) + 4) if idades else 0.0,
        "altura_media": sum(alturas_validas) / len(alturas_validas) if alturas_validas else 0.0,
        "valor_atual": sum(valores_atuais_validos),
        "valor_maximo": sum(valores_maximos_validos),
        "cobertura_mercado": len(valores_atuais_validos),
        "cobertura_altura": len(alturas_validas),
    }


def render_resumo_elenco(titulares: list[Mapping[str, Any]]) -> None:
    resumo = calcular_resumo_elenco(titulares)
    atual = float(resumo["valor_atual"])
    maximo = float(resumo["valor_maximo"])
    percentual = (atual / maximo * 100.0) if maximo > 0 else 0.0

    st.markdown(
        f"""
        <div class="summary-box">
            <div class="summary-grid">
                <div><div class="summary-label">Idade média 2026</div><div class="summary-value">{resumo['idade_2026']:.1f}</div></div>
                <div><div class="summary-label">Idade média 2030</div><div class="summary-value" style="color:#EAB308">{resumo['idade_2030']:.1f}</div></div>
                <div><div class="summary-label">Altura média</div><div class="summary-value">{resumo['altura_media']:.2f} m</div></div>
                <div><div class="summary-label">Valor atual</div><div class="summary-value" style="color:#22C55E">{formatar_valor_milhoes(atual)}</div></div>
                <div><div class="summary-label">Atual / pico</div><div class="summary-value">{percentual:.0f}%</div></div>
            </div>
            <div style="color:#94A3B8;font-size:.72rem;text-align:center;margin-top:12px;">
                Cobertura: mercado de {int(resumo['cobertura_mercado'])}/11 atletas; altura de {int(resumo['cobertura_altura'])}/11.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_cartao_perfil(nome: str, dados: Mapping[str, Any]) -> None:
    posicoes = dados.get("posicoes_multiplas") or [dados.get("posicao")]
    siglas: list[str] = []
    for posicao in posicoes:
        sigla = ABREVIACOES.get(str(posicao), "OBS")
        if sigla not in siglas:
            siglas.append(sigla)

    st.markdown(
        f"""
        <div class="profile-card">
            <h2>{_esc(dados.get('nome', nome))}</h2>
            <span class="status-pill">{_esc(dados.get('tipo', 'Observação'))}</span>
            <div class="profile-details">
                <b>Posições do projeto:</b> {_esc(' / '.join(siglas))}<br>
                <b>Clube atual:</b> {_esc(dados.get('clube'))}<br>
                <b>Grupo:</b> {_esc(dados.get('grupo'))}<br>
                <b>Idade em 2026:</b> {int(dados.get('idade', 22))} anos<br>
                <b>Idade em 2030:</b> <span style="color:#EAB308;font-weight:800">{int(dados.get('idade', 22)) + 4} anos</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dados_transfermarkt(dados: Mapping[str, Any]) -> None:
    if not any(chave.startswith("tm_") for chave in dados):
        st.info("Ainda não há dados externos cadastrados para este atleta.")
        return

    nacionalidades = dados.get("tm_nacionalidades") or []
    if isinstance(nacionalidades, str):
        nacionalidades = [nacionalidades]
    posicoes_site = dados.get("tm_posicoes_secundarias_site") or []
    if isinstance(posicoes_site, str):
        posicoes_site = [posicoes_site]

    linhas = [
        f"<b>Nome completo:</b> {_esc(dados.get('nome_completo', dados.get('nome')))}",
        f"<b>Nascimento:</b> {_esc(dados.get('tm_nascimento'))} &nbsp; | &nbsp; <b>Naturalidade:</b> {_esc(dados.get('tm_naturalidade'))}",
        f"<b>Altura:</b> {_esc(dados.get('tm_altura'))} &nbsp; | &nbsp; <b>Pé:</b> {_esc(dados.get('tm_pe'))}",
        f"<b>Nacionalidades:</b> {_esc(', '.join(nacionalidades) if nacionalidades else 'N/A')}",
        f"<b>Agente:</b> {_esc(dados.get('tm_empresario'))}",
        f"<b>No clube desde:</b> {_esc(dados.get('tm_clube_desde'))} &nbsp; | &nbsp; <b>Contrato:</b> {_esc(dados.get('tm_contrato'))}",
    ]
    if dados.get("tm_opcao_contrato"):
        linhas.append(f"<b>Opção contratual:</b> {_esc(dados.get('tm_opcao_contrato'))}")
    if dados.get("tm_ultima_renovacao"):
        linhas.append(f"<b>Última renovação:</b> {_esc(dados.get('tm_ultima_renovacao'))}")
    if dados.get("tm_equipador"):
        linhas.append(f"<b>Equipador:</b> {_esc(dados.get('tm_equipador'))}")
    linhas.append(
        f"<b>Posição no site externo:</b> {_esc(dados.get('tm_posicao_site'))}"
        + (f" ({_esc(', '.join(posicoes_site))})" if posicoes_site else "")
    )

    st.markdown(
        '<div class="market-card" style="border-left-color:#3B82F6">'
        + '<div style="color:#CBD5E1;line-height:1.85;font-size:.88rem">'
        + "<br>".join(linhas)
        + "</div></div>",
        unsafe_allow_html=True,
    )


def render_comparativo_mercado(dados: Mapping[str, Any]) -> None:
    atual = valor_mercado_atual(dados)
    maximo = valor_mercado_maximo(dados)
    percentual = percentual_do_pico(dados)
    diferenca = maximo - atual if maximo > 0 and atual > 0 else None

    if atual <= 0 and maximo <= 0:
        st.info("Ainda não há valores de mercado cadastrados para este atleta.")
        return

    percentual_exibido = percentual or 0.0
    st.markdown(
        f"""
        <div class="market-card">
            <div class="market-grid">
                <div><div class="market-label">Valor atual</div><div class="market-value green">{formatar_valor_milhoes(atual)}</div></div>
                <div><div class="market-label">Maior valor da carreira</div><div class="market-value gold">{formatar_valor_milhoes(maximo)}</div></div>
                <div><div class="market-label">Distância do pico</div><div class="market-value">{formatar_valor_milhoes(diferenca) if diferenca is not None else 'N/A'}</div></div>
            </div>
            <div class="market-label">Valor atual equivale a {percentual_exibido:.0f}% do pico de carreira</div>
            <div class="progress-track"><div class="progress-fill" style="width:{max(0, min(percentual_exibido, 100)):.1f}%"></div></div>
            <div style="color:#94A3B8;font-size:.72rem;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;">
                <span>Pico registrado em {_esc(dados.get('tm_data_valor_maximo'))}</span>
                <span>Última atualização: {_esc(dados.get('tm_ultima_atualizacao'))}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dossie(dados: Mapping[str, Any]) -> None:
    blocos = (
        ("Pontos fortes", dados.get("pontos_fortes"), "#22C55E"),
        ("Desafios e pontos fracos", dados.get("pontos_fracos"), "#EF4444"),
        ("Histórico das discussões", dados.get("historico"), "#3B82F6"),
    )
    for titulo, conteudo, cor in blocos:
        texto = conteudo or "Nenhuma informação cadastrada."
        st.markdown(
            f'<div class="stat-box" style="border-left-color:{cor}"><strong>{_esc(titulo)}:</strong><br>{_esc(texto)}</div>',
            unsafe_allow_html=True,
        )
