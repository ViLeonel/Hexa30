"""Configurações centrais do projeto O Caminho para o Hexa 2030."""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Identidade e navegação
NOME_APLICACAO = "O Caminho para o Hexa 2030"
TITULO_PROJETO = "🏆 O Caminho para o Hexa"
ICONE_APLICACAO = "🏆"
TITULO_SIDEBAR = "CONSELHO TÁTICO"
ROTULO_NAVEGACAO = "Navegação do Painel:"

MENU_CAMPO = "🏟️ Campo de Jogo"
MENU_PERFIS = "👤 Perfis & Scout"
MENU_ROSTER = "📋 Gestão do Roster"
MENU_ANALISE = "📊 Análise de Opiniões"
MENUS: tuple[str, ...] = (
    MENU_CAMPO,
    MENU_PERFIS,
    MENU_ROSTER,
    MENU_ANALISE,
)

# Referências temporais
ANO_BASE_DADOS = 2026
ANO_COPA = 2030

# Vocabulário editorial
GRUPO_TITULARES = "Titulares"
GRUPO_RESERVAS = "Reservas"
GRUPO_OBSERVACAO = "Observação"
GRUPOS_EDITORIAIS: tuple[str, ...] = (
    GRUPO_TITULARES,
    GRUPO_RESERVAS,
    GRUPO_OBSERVACAO,
)

# Valores padrão e limites de entrada
IDADE_PADRAO = 22
IDADE_MINIMA_CADASTRO = 15
IDADE_MAXIMA_CADASTRO = 45
LIMITE_DESTAQUES_ANALISE = 8

# Feedback
EMAIL_FEEDBACK = "viniciusbl87@gmail.com"
TIPOS_SUGESTAO: tuple[str, ...] = (
    "Sugerir jogador",
    "Sugerir melhoria",
)
ASSUNTO_FEEDBACK_PREFIXO = "Caminho para o Hexa"
SAUDACAO_FEEDBACK = "Olá, Vini e Roberto!"

# Persistência
NOME_ARQUIVO_JOGADORES = "jogadores_hexa_2030.json"
NOME_ARQUIVO_ENRIQUECIMENTOS = "enriquecimentos_tm.json"
DATA_FILE = BASE_DIR / NOME_ARQUIVO_JOGADORES
ENRICHMENTS_FILE = BASE_DIR / NOME_ARQUIVO_ENRIQUECIMENTOS

# Configuração da página Streamlit. Mantida como estrutura simples para não
# introduzir dependência do Streamlit neste módulo.
PAGE_CONFIG = {
    "page_title": NOME_APLICACAO,
    "page_icon": ICONE_APLICACAO,
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}
