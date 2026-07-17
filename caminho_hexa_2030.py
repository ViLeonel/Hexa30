"""Entrada principal do aplicativo O Caminho para o Hexa 2030."""

from __future__ import annotations

import urllib.parse
from typing import Any

import pandas as pd
import streamlit as st

from components import (
    render_cabecalho,
    render_campo,
    render_cartao_perfil,
    render_comparativo_mercado,
    render_dados_transfermarkt,
    render_dossie,
    render_legenda_adaptabilidade,
    render_resumo_elenco,
)
from data import (
    DataIntegrityError,
    adicionar_jogador,
    atualizar_avaliacoes,
    carregar_jogadores,
    formatar_valor_milhoes,
    percentual_do_pico,
    validar_posicoes,
    valor_mercado_atual,
    valor_mercado_maximo,
)
from styles import PAGE_CONFIG, aplicar_estilos
from taticas import (
    POSICOES_OFICIAIS,
    TATICAS,
    formatar_jogador_com_posicao,
    obter_atletas_compativeis,
    validar_taticas,
)

st.set_page_config(**PAGE_CONFIG)
aplicar_estilos()

try:
    jogadores = carregar_jogadores()
except DataIntegrityError as erro:
    st.error(str(erro))
    st.info("Corrija o JSON no GitHub e reinicie o aplicativo. O arquivo inválido não foi sobrescrito.")
    st.stop()

ERROS_CONFIGURACAO = validar_posicoes(jogadores) + validar_taticas(jogadores)
if ERROS_CONFIGURACAO:
    with st.expander("Inconsistências de configuração detectadas", expanded=True):
        for mensagem in ERROS_CONFIGURACAO:
            st.error(mensagem)

MENU_CAMPO = "🏟️ Campo de Jogo"
MENU_PERFIS = "👤 Perfis & Scout"
MENU_ROSTER = "📋 Gestão do Roster"
MENU_ANALISE = "📊 Análise de Opiniões"

st.sidebar.markdown(
    "<h2 style='text-align:center;color:#EAB308;margin-top:15px;'>CONSELHO TÁTICO</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegação do Painel:",
    [MENU_CAMPO, MENU_PERFIS, MENU_ROSTER, MENU_ANALISE],
)


def _escalacao_inicial() -> dict[str, str]:
    primeira_tatica = next(iter(TATICAS.values()))
    return {slot: info[1] for slot, info in primeira_tatica.items()}


if "escalados" not in st.session_state:
    st.session_state.escalados = _escalacao_inicial()


# ==========================================
# TELA 1 — CAMPO DE JOGO
# ==========================================
if menu == MENU_CAMPO:
    render_cabecalho(
        "🏆 O Caminho para o Hexa",
        "Painel tático para planejar a renovação geracional da Seleção Brasileira rumo a 2030.",
    )

    col_config, col_campo = st.columns([1, 2], gap="large")

    with col_config:
        st.markdown("### Calibrar escalação")
        tatica_ativa = st.selectbox(
            "Esquema tático:",
            list(TATICAS.keys()),
            key="tactical_selector",
        )
        layout_ativo = TATICAS[tatica_ativa]

        if st.session_state.get("ultima_formacao") != tatica_ativa:
            nova_escalacao: dict[str, str] = {}
            usados: set[str] = set()

            for slot, info in layout_ativo.items():
                posicoes_validas, atleta_padrao = info[0], info[1]
                atleta_reutilizado = None

                for atleta_anterior in st.session_state.escalados.values():
                    if atleta_anterior in usados or atleta_anterior not in jogadores:
                        continue
                    compativeis = obter_atletas_compativeis(jogadores, posicoes_validas)
                    if atleta_anterior in compativeis:
                        atleta_reutilizado = atleta_anterior
                        break

                escolhido = atleta_reutilizado or atleta_padrao
                if escolhido not in jogadores:
                    compativeis = obter_atletas_compativeis(jogadores, posicoes_validas)
                    escolhido = compativeis[0] if compativeis else atleta_padrao

                nova_escalacao[slot] = escolhido
                usados.add(escolhido)

            st.session_state.escalados = nova_escalacao
            st.session_state.ultima_formacao = tatica_ativa
            st.rerun()

        st.caption("Os filtros respeitam somente as posições oficiais definidas pelo projeto.")
        novos_titulares: dict[str, str] = {}

        for slot, info in layout_ativo.items():
            posicoes_validas = info[0]
            validos = obter_atletas_compativeis(jogadores, posicoes_validas)
            ja_escalados = set(novos_titulares.values())
            disponiveis = [nome for nome in validos if nome not in ja_escalados]

            if not disponiveis:
                disponiveis = validos
            if not disponiveis:
                st.error(f"Não há atletas compatíveis com {slot}.")
                continue

            atual = st.session_state.escalados.get(slot, info[1])
            if atual in ja_escalados or atual not in disponiveis:
                atual = disponiveis[0]

            indice = disponiveis.index(atual)
            escolha = st.selectbox(
                f"{slot}:",
                disponiveis,
                index=indice,
                format_func=lambda nome, base=jogadores: formatar_jogador_com_posicao(nome, base),
                key=f"escala_{tatica_ativa}_{slot}",
            )
            novos_titulares[slot] = escolha

        st.session_state.escalados = novos_titulares

    with col_campo:
        render_campo(layout_ativo, st.session_state.escalados, jogadores)
        render_legenda_adaptabilidade()

        titulares = [
            jogadores[nome]
            for nome in st.session_state.escalados.values()
            if nome in jogadores
        ]
        render_resumo_elenco(titulares)

        notas_vini = [float(j.get("nota_vini") or 0) for j in titulares if float(j.get("nota_vini") or 0) > 0]
        notas_roberto = [float(j.get("nota_roberto") or 0) for j in titulares if float(j.get("nota_roberto") or 0) > 0]
        media_vini = sum(notas_vini) / len(notas_vini) if notas_vini else 0.0
        media_roberto = sum(notas_roberto) / len(notas_roberto) if notas_roberto else 0.0

        c1, c2, c3 = st.columns(3)
        c1.metric("Média Vini", f"{media_vini:.2f}")
        c2.metric("Média Roberto", f"{media_roberto:.2f}")
        c3.metric("Média coletiva", f"{((media_vini + media_roberto) / 2):.2f}")


# ==========================================
# TELA 2 — PERFIS E SCOUT
# ==========================================
elif menu == MENU_PERFIS:
    render_cabecalho(
        "Ficha Individual do Atleta",
        "Avaliação editorial, informações contratuais e comparação de valor de mercado.",
    )

    nomes = sorted(jogadores.keys(), key=str.casefold)
    selected_name = st.selectbox("Escolha o atleta:", nomes)
    atleta = jogadores[selected_name]
    st.markdown("---")

    col_perfil, col_dados = st.columns([1, 2], gap="large")

    with col_perfil:
        render_cartao_perfil(selected_name, atleta)
        st.markdown("### Avaliação tática")

        with st.form(f"avaliacao_{selected_name}"):
            nota_vini = st.slider(
                "Nota do Vini",
                min_value=0.0,
                max_value=10.0,
                value=float(atleta.get("nota_vini") or 0.0),
                step=0.1,
            )
            nota_roberto = st.slider(
                "Nota do Roberto",
                min_value=0.0,
                max_value=10.0,
                value=float(atleta.get("nota_roberto") or 0.0),
                step=0.1,
            )
            salvar_notas = st.form_submit_button("Salvar avaliações", width="stretch")

        if salvar_notas:
            atualizar_avaliacoes(jogadores, selected_name, nota_vini, nota_roberto)
            st.success("Avaliações salvas no JSON.")
            st.rerun()

    with col_dados:
        st.markdown("### Valor de mercado")
        render_comparativo_mercado(atleta)

        with st.expander("Dados externos e contratuais", expanded=True):
            render_dados_transfermarkt(atleta)

        st.markdown("### Dossiê do projeto")
        render_dossie(atleta)


# ==========================================
# TELA 3 — GESTÃO DO ROSTER
# ==========================================
elif menu == MENU_ROSTER:
    render_cabecalho(
        "Gestão do Roster",
        "Consulta, filtros e inclusão de atletas. A base não oferece exclusão de jogadores.",
    )

    tab_base, tab_novo = st.tabs(["Base de jogadores", "Adicionar atleta"])

    with tab_base:
        filtro_1, filtro_2, filtro_3 = st.columns([2, 1, 1])
        busca = filtro_1.text_input("Buscar por nome ou clube", placeholder="Ex.: Palmeiras")
        posicao_filtro = filtro_2.selectbox("Posição", ["Todas", *POSICOES_OFICIAIS])
        grupos = sorted({str(d.get("grupo", "Observação")) for d in jogadores.values()})
        grupo_filtro = filtro_3.selectbox("Grupo", ["Todos", *grupos])

        registros: list[dict[str, Any]] = []
        for nome, dados in jogadores.items():
            texto_busca = f"{nome} {dados.get('clube', '')}".casefold()
            if busca and busca.casefold() not in texto_busca:
                continue
            if posicao_filtro != "Todas" and posicao_filtro not in dados.get("posicoes_multiplas", []):
                continue
            if grupo_filtro != "Todos" and dados.get("grupo") != grupo_filtro:
                continue

            atual = valor_mercado_atual(dados)
            maximo = valor_mercado_maximo(dados)
            registros.append(
                {
                    "Nome": nome,
                    "Posição": dados.get("posicao", "N/A"),
                    "Grupo": dados.get("grupo", "N/A"),
                    "Clube": dados.get("clube", "N/A"),
                    "Idade 2026": dados.get("idade", 0),
                    "Idade 2030": int(dados.get("idade", 0)) + 4,
                    "Vini": float(dados.get("nota_vini") or 0.0),
                    "Roberto": float(dados.get("nota_roberto") or 0.0),
                    "Valor atual": formatar_valor_milhoes(atual),
                    "Pico": formatar_valor_milhoes(maximo),
                    "% do pico": round(percentual_do_pico(dados) or 0.0, 1),
                }
            )

        df_roster = pd.DataFrame(registros)
        st.caption(f"{len(df_roster)} atleta(s) exibido(s) de {len(jogadores)} cadastrados.")
        st.dataframe(df_roster, width="stretch", hide_index=True)

    with tab_novo:
        st.info("O cadastro inclui o atleta no JSON. Nenhum registro existente é removido ou sobrescrito.")
        with st.form("novo_jogador", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            nome_curto = col_a.text_input("Nome curto*")
            nome_completo = col_b.text_input("Nome completo")

            col_c, col_d = st.columns(2)
            posicao = col_c.selectbox("Posição principal*", POSICOES_OFICIAIS)
            clube = col_d.text_input("Clube atual")

            posicoes_secundarias = st.multiselect(
                "Posições secundárias",
                [p for p in POSICOES_OFICIAIS if p != posicao],
            )

            col_e, col_f, col_g = st.columns(3)
            idade = col_e.number_input("Idade em 2026", min_value=15, max_value=45, value=22)
            grupo = col_f.selectbox("Grupo", ["Titulares", "Reservas", "Observação"])
            tipo = col_g.selectbox("Status", ["Certeza Atual", "Promessa 2030", "Observação"])

            pontos_fortes = st.text_area("Pontos fortes")
            pontos_fracos = st.text_area("Pontos fracos")
            historico = st.text_area("Histórico das discussões")

            cadastrar = st.form_submit_button("Cadastrar atleta", width="stretch")

        if cadastrar:
            try:
                adicionar_jogador(
                    jogadores,
                    {
                        "nome": nome_curto,
                        "nome_completo": nome_completo,
                        "posicao": posicao,
                        "posicoes_multiplas": [posicao, *posicoes_secundarias],
                        "clube": clube or "N/A",
                        "idade": int(idade),
                        "grupo": grupo,
                        "tipo": tipo,
                        "nota_vini": 0.0,
                        "nota_roberto": 0.0,
                        "pontos_fortes": pontos_fortes,
                        "pontos_fracos": pontos_fracos,
                        "historico": historico,
                    },
                )
                st.success(f"{nome_curto} foi incluído na base.")
                st.rerun()
            except ValueError as erro:
                st.error(str(erro))


# ==========================================
# TELA 4 — ANÁLISE DE OPINIÕES E MERCADO
# ==========================================
elif menu == MENU_ANALISE:
    render_cabecalho(
        "Análise Coletiva de Scout",
        "Consensos, divergências e leitura do valor de mercado do elenco monitorado.",
    )

    avaliados: list[dict[str, Any]] = []
    mercado: list[dict[str, Any]] = []

    for nome, dados in jogadores.items():
        nota_vini = float(dados.get("nota_vini") or 0.0)
        nota_roberto = float(dados.get("nota_roberto") or 0.0)
        if nota_vini > 0 and nota_roberto > 0:
            avaliados.append(
                {
                    "Nome": nome,
                    "Posição": dados.get("posicao", "N/A"),
                    "Vini": nota_vini,
                    "Roberto": nota_roberto,
                    "Diferença": abs(nota_vini - nota_roberto),
                    "Média": (nota_vini + nota_roberto) / 2,
                }
            )

        atual = valor_mercado_atual(dados)
        maximo = valor_mercado_maximo(dados)
        if atual > 0:
            mercado.append(
                {
                    "Nome": nome,
                    "Posição": dados.get("posicao", "N/A"),
                    "Atual (M€)": atual,
                    "Pico (M€)": maximo,
                    "% do pico": percentual_do_pico(dados) or 0.0,
                    "Diferença para o pico (M€)": max(maximo - atual, 0.0),
                }
            )

    df_avaliados = pd.DataFrame(avaliados)
    df_mercado = pd.DataFrame(mercado)

    if df_avaliados.empty:
        st.info("Ainda não existem atletas com as duas avaliações preenchidas.")
    else:
        media_geral = df_avaliados["Média"].mean()
        divergencia_media = df_avaliados["Diferença"].mean()
        c1, c2, c3 = st.columns(3)
        c1.metric("Atletas avaliados", len(df_avaliados))
        c2.metric("Média geral", f"{media_geral:.2f}")
        c3.metric("Divergência média", f"{divergencia_media:.2f}")

        col_consenso, col_divergencia = st.columns(2, gap="large")
        with col_consenso:
            st.markdown("### Maiores consensos")
            consenso = df_avaliados.sort_values(["Diferença", "Média"], ascending=[True, False]).head(8)
            st.dataframe(
                consenso[["Nome", "Posição", "Vini", "Roberto", "Média"]],
                width="stretch",
                hide_index=True,
            )

        with col_divergencia:
            st.markdown("### Maiores divergências")
            divergencias = df_avaliados.sort_values(["Diferença", "Média"], ascending=[False, False]).head(8)
            st.dataframe(
                divergencias[["Nome", "Posição", "Vini", "Roberto", "Diferença"]],
                width="stretch",
                hide_index=True,
            )

    st.markdown("---")
    st.markdown("### Leitura de mercado")
    if df_mercado.empty:
        st.info("Ainda não existem valores de mercado cadastrados.")
    else:
        total_atual = df_mercado["Atual (M€)"].sum()
        total_pico = df_mercado["Pico (M€)"].sum()
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Atletas com valor", len(df_mercado))
        col_m2.metric("Valor atual somado", formatar_valor_milhoes(total_atual))
        col_m3.metric("Pico somado", formatar_valor_milhoes(total_pico))

        mercado_ordenado = df_mercado.sort_values("Atual (M€)", ascending=False)
        st.dataframe(
            mercado_ordenado,
            width="stretch",
            hide_index=True,
            column_config={
                "Atual (M€)": st.column_config.NumberColumn(format="€ %.2f mi"),
                "Pico (M€)": st.column_config.NumberColumn(format="€ %.2f mi"),
                "% do pico": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%"),
                "Diferença para o pico (M€)": st.column_config.NumberColumn(format="€ %.2f mi"),
            },
        )


# ==========================================
# FEEDBACK PRIVADO NA SIDEBAR
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("Radar do projeto")
with st.sidebar.form("form_sugestao", clear_on_submit=True):
    tipo_sugestao = st.selectbox("Tipo:", ["Sugerir jogador", "Sugestão de melhoria"])
    detalhes = st.text_area("Mensagem:", placeholder="Escreva sua sugestão...")
    enviar = st.form_submit_button("Preparar e-mail")

if enviar:
    if detalhes.strip():
        assunto = urllib.parse.quote(f"Caminho para o Hexa: {tipo_sugestao}")
        corpo = urllib.parse.quote(f"Olá, Vini e Roberto!\n\n{detalhes.strip()}")
        mailto = f"mailto:viniciusbl87@gmail.com?subject={assunto}&body={corpo}"
        st.sidebar.markdown(
            f'<a href="{mailto}" style="display:block;text-align:center;background:#EAB308;color:#020617;'
            'font-weight:800;padding:10px;border-radius:8px;text-decoration:none;">Abrir e-mail</a>',
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.warning("Digite uma mensagem antes de continuar.")
