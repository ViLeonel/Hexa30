"""Componentes visuais reutilizáveis do aplicativo."""

from __future__ import annotations

import html
from collections.abc import Mapping, Sequence
from typing import Any

import streamlit as st

from hexa_config import (
    ANO_BASE_DADOS,
    ANO_COPA,
    GRUPO_OBSERVACAO,
    GRUPO_RESERVAS,
    GRUPO_TITULARES,
    IDADE_PADRAO,
)
from hexa_data import (
    extrair_altura_metros,
    formatar_valor_milhoes,
    percentual_do_pico,
    valor_mercado_atual,
    valor_mercado_maximo,
)
from hexa_taticas import ABREVIACOES, LIMITE_CONVOCADOS, LIMITE_RESERVAS, LIMITE_TITULARES, SlotTatico, indice_adaptabilidade


def _esc(valor: Any, padrao: str = "N/A") -> str:
    texto = padrao if valor in (None, "", []) else str(valor)
    return html.escape(texto)


def _nota_texto(valor: Any) -> str:
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return "Sem nota"
    return f"{numero:.1f}".replace(".", ",") if numero > 0 else "Sem nota"


def render_cabecalho(titulo: str, subtitulo: str) -> None:
    st.markdown(f'<h1 class="app-title">{_esc(titulo)}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="project-subtitle">{_esc(subtitulo)}</p>', unsafe_allow_html=True)


def render_campo(
    layout: Mapping[str, SlotTatico],
    escalados: Mapping[str, str],
    jogadores: Mapping[str, Mapping[str, Any]],
) -> None:
    cards: list[str] = []
    cores = {0: "#22C55E", 1: "#EAB308"}

    for slot, configuracao in layout.items():
        nome = escalados.get(slot)
        if not nome or nome not in jogadores:
            cards.append(
                f'<div class="player-node" style="left:{configuracao.left};bottom:{configuracao.bottom};">'
                '<div class="player-card-pitch player-card-empty">'
                f'<div class="player-pos-tag">{_esc(configuracao.tag)}</div>'
                '<div class="player-name-tag">Selecionar atleta</div>'
                '<div class="player-empty-tag">Vaga aberta</div>'
                '</div></div>'
            )
            continue

        dados = jogadores[nome]
        indice = indice_adaptabilidade(dados, configuracao.posicoes)
        cor = cores.get(indice, "#F97316" if indice >= 2 else "#EF4444")
        nota_vini = float(dados.get("nota_vini") or 0.0)
        nota_roberto = float(dados.get("nota_roberto") or 0.0)

        cards.append(
            f'<div class="player-node" style="left:{configuracao.left};bottom:{configuracao.bottom};">'
            f'<div class="player-card-pitch" style="border-color:{cor}!important;">'
            f'<div class="player-pos-tag">{_esc(configuracao.tag)}</div>'
            f'<div class="player-name-tag" title="{_esc(dados.get("nome", nome))}">{_esc(dados.get("nome", nome))}</div>'
            f'<div class="player-rating-tag">★ {nota_vini:.1f} / {nota_roberto:.1f}</div>'
            '</div></div>'
        )

    campo = (
        '<div class="pitch-container">'
        '<div class="pitch-line-center"></div>'
        '<div class="pitch-circle"></div>'
        '<div class="pitch-penalty-top"></div>'
        '<div class="pitch-penalty-bottom"></div>'
        f'{"".join(cards)}'
        '</div>'
    )
    st.markdown(campo, unsafe_allow_html=True)


def render_legenda_adaptabilidade() -> None:
    st.markdown(
        """
        <div class="legend-box">
            <div class="legend-item"><span class="legend-dot" style="background:#22C55E"></span><b>Verde:</b> função primária</div>
            <div class="legend-item"><span class="legend-dot" style="background:#EAB308"></span><b>Amarela:</b> função secundária</div>
            <div class="legend-item"><span class="legend-dot" style="background:#F97316"></span><b>Laranja:</b> função terciária</div>
            <div class="legend-item"><span class="legend-dot" style="background:#64748B"></span><b>Cinza:</b> vaga não preenchida</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_banco_reservas(
    reservas: Sequence[str],
    jogadores: Mapping[str, Mapping[str, Any]],
) -> None:
    st.markdown(f"### Banco de reservas ({len(reservas)}/{LIMITE_RESERVAS})")
    if not reservas:
        st.info("Nenhum reserva selecionado. É possível convocar até 15 jogadores para o banco.")
        return

    cards: list[str] = []
    for nome in reservas:
        dados = jogadores.get(nome, {})
        posicao = str(dados.get("posicao") or "N/A")
        sigla = ABREVIACOES.get(posicao, "OBS")
        cards.append(
            '<div class="bench-card">'
            f'<div class="bench-number">{_esc(sigla)}</div>'
            f'<div class="bench-name">{_esc(nome)}</div>'
            f'<div class="bench-club">{_esc(dados.get("clube"))}</div>'
            '</div>'
        )

    st.markdown(
        '<div class="bench-box"><div class="bench-grid">'
        + ''.join(cards)
        + '</div></div>',
        unsafe_allow_html=True,
    )


def calcular_resumo_elenco(elenco: Sequence[Mapping[str, Any]]) -> dict[str, float | int]:
    idades = [int(j.get("idade", 0)) for j in elenco if j.get("idade")]
    alturas = [extrair_altura_metros(j.get("tm_altura"), 0.0) for j in elenco]
    alturas_validas = [valor for valor in alturas if valor > 0]
    valores_atuais = [valor_mercado_atual(j) for j in elenco]
    valores_atuais_validos = [valor for valor in valores_atuais if valor > 0]
    valores_maximos = [valor_mercado_maximo(j) for j in elenco]
    valores_maximos_validos = [valor for valor in valores_maximos if valor > 0]

    return {
        "idade_copa": (sum(idades) / len(idades) + (ANO_COPA - ANO_BASE_DADOS)) if idades else 0.0,
        "altura_media": sum(alturas_validas) / len(alturas_validas) if alturas_validas else 0.0,
        "valor_atual": sum(valores_atuais_validos),
        "valor_maximo": sum(valores_maximos_validos),
        "cobertura_mercado": len(valores_atuais_validos),
        "cobertura_altura": len(alturas_validas),
    }


def render_resumo_elenco(
    titulares: Sequence[Mapping[str, Any]],
    reservas: Sequence[Mapping[str, Any]],
) -> None:
    elenco = [*titulares, *reservas]
    if not elenco:
        st.info("Preencha os titulares e os reservas para gerar o raio-X da convocação.")
        return

    resumo = calcular_resumo_elenco(elenco)
    atual = float(resumo["valor_atual"])
    maximo = float(resumo["valor_maximo"])
    percentual = (atual / maximo * 100.0) if maximo > 0 else 0.0

    st.markdown(
        f"""
        <div class="summary-box">
            <div class="summary-grid">
                <div><div class="summary-label">{_esc(GRUPO_TITULARES)}</div><div class="summary-value">{len(titulares)}/{LIMITE_TITULARES}</div></div>
                <div><div class="summary-label">{_esc(GRUPO_RESERVAS)}</div><div class="summary-value">{len(reservas)}/{LIMITE_RESERVAS}</div></div>
                <div><div class="summary-label">Convocados</div><div class="summary-value" style="color:#EAB308">{len(elenco)}/{LIMITE_CONVOCADOS}</div></div>
                <div><div class="summary-label">Idade média em {ANO_COPA}</div><div class="summary-value">{resumo['idade_copa']:.1f}</div></div>
                <div><div class="summary-label">Valor atual</div><div class="summary-value" style="color:#22C55E">{formatar_valor_milhoes(atual)}</div></div>
                <div><div class="summary-label">Atual / pico</div><div class="summary-value">{percentual:.0f}%</div></div>
            </div>
            <div class="summary-footnote">
                Cobertura dos {len(elenco)} selecionados: mercado de {int(resumo['cobertura_mercado'])}; altura de {int(resumo['cobertura_altura'])}.
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
            <div class="profile-details">
                <b>Posições do projeto:</b> {_esc(' / '.join(siglas))}<br>
                <b>Nome completo:</b> {_esc(dados.get('nome_completo', dados.get('nome', nome)))}<br>
                <b>Clube atual:</b> {_esc(dados.get('clube'))}<br>
                <b>Grupo:</b> {_esc(dados.get('grupo'))}<br>
                <b>Idade em {ANO_BASE_DADOS}:</b> {int(dados.get('idade', IDADE_PADRAO))} anos<br>
                <b>Idade em {ANO_COPA}:</b> <span style="color:#EAB308;font-weight:800">{int(dados.get('idade', IDADE_PADRAO)) + (ANO_COPA - ANO_BASE_DADOS)} anos</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_avaliacao_leitura(dados: Mapping[str, Any]) -> None:
    nota_vini = float(dados.get("nota_vini") or 0.0)
    nota_roberto = float(dados.get("nota_roberto") or 0.0)
    notas_validas = [nota for nota in (nota_vini, nota_roberto) if nota > 0]
    media = sum(notas_validas) / len(notas_validas) if notas_validas else 0.0

    st.markdown(
        f"""
        <div class="rating-box">
            <div class="rating-grid">
                <div class="rating-card"><div class="rating-label">Vini</div><div class="rating-value">{_nota_texto(nota_vini)}</div></div>
                <div class="rating-card"><div class="rating-label">Roberto</div><div class="rating-value">{_nota_texto(nota_roberto)}</div></div>
                <div class="rating-card"><div class="rating-label">Média</div><div class="rating-value rating-gold">{_nota_texto(media)}</div></div>
            </div>
            <div class="rating-note">Registro editorial somente para leitura.</div>
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
        f"<b>Clube atual:</b> {_esc(dados.get('clube'))}",
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
    if dados.get("tm_observacao_transferencia"):
        linhas.append(
            f"<b>Observação de transferência:</b> {_esc(dados.get('tm_observacao_transferencia'))}"
        )
    if dados.get("tm_clube_imagem"):
        linhas.append(
            f"<b>Clube exibido na imagem:</b> {_esc(dados.get('tm_clube_imagem'))}"
            f" &nbsp; | &nbsp; <b>Contrato exibido:</b> {_esc(dados.get('tm_contrato_imagem'))}"
        )
    if dados.get("tm_equipador"):
        linhas.append(f"<b>Equipador:</b> {_esc(dados.get('tm_equipador'))}")
    linhas.append(
        f"<b>Posição no site externo:</b> {_esc(dados.get('tm_posicao_site'))}"
        + (f" ({_esc(', '.join(posicoes_site))})" if posicoes_site else "")
    )
    if dados.get("tm_altura_metros"):
        linhas.append(f"<b>Altura normalizada:</b> {_esc(f'{float(dados["tm_altura_metros"]):.2f} m'.replace('.', ','))}")
    if dados.get("tm_fonte") or dados.get("tm_extraido_em"):
        linhas.append(
            f"<b>Origem do registro:</b> {_esc(dados.get('tm_fonte'))}"
            f" &nbsp; | &nbsp; <b>Extraído em:</b> {_esc(dados.get('tm_extraido_em'))}"
        )

    st.markdown(
        '<div class="market-card" style="border-left-color:#3B82F6">'
        + '<div style="color:#CBD5E1;line-height:1.85;font-size:.88rem">'
        + '<br>'.join(linhas)
        + '</div></div>',
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
            <div class="market-dates">
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
