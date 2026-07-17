import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
import requests
from bs4 import BeautifulSoup

# ==========================================
# 1. CONFIGURAÇÕES DE TELA & METADADOS
# ==========================================
st.set_page_config(
    page_title="O Caminho para o Hexa 2030",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. DESIGN VISUAL E CSS PERSONALIZADO (PADRÕES WCAG)
# ==========================================
st.markdown("""
<style>
    /* Estilização Geral do App (Soft Navy & Ouro Queimado) */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Cabeçalho do App */
    .app-title {
        text-align: center;
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #EAB308 0%, #F8FAFC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    
    .project-subtitle {
        color: #94A3B8;
        font-size: 1.15rem;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    /* O Campo Tático Verde Floresta Responsivo */
    .pitch-container {
        background-color: #14532D; 
        background-image: linear-gradient(to bottom, #14532D 0%, #166534 100%);
        border: 4px solid #EAB308;
        border-radius: 20px;
        position: relative;
        width: 100%;
        height: 680px; 
        overflow: hidden;
        box-shadow: 0 15px 35px rgba(0,0,0,0.7);
        margin-bottom: 25px;
    }
    .pitch-line-center {
        position: absolute;
        top: 50%;
        left: 0;
        width: 100%;
        height: 2px;
        background-color: rgba(248, 250, 252, 0.3);
    }
    .pitch-circle {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 150px;
        height: 150px;
        border: 2px solid rgba(248, 250, 252, 0.3);
        border-radius: 50%;
    }
    .pitch-penalty-top, .pitch-penalty-bottom {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        width: 280px;
        height: 100px;
        border: 2px solid rgba(248, 250, 252, 0.3);
    }
    .pitch-penalty-top { top: 0; border-top: none; }
    .pitch-penalty-bottom { bottom: 0; border-bottom: none; }
    
    /* Nós dos Jogadores */
    .player-node {
        position: absolute;
        transform: translate(-50%, -50%);
        width: 130px;
        text-align: center;
        z-index: 10;
        transition: all 0.3s ease-in-out;
    }
    .player-card-pitch {
        background: #020617;
        border: 2px solid #EAB308;
        border-radius: 8px;
        padding: 6px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .player-pos-tag {
        font-size: 7pt;
        color: #EAB308;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .player-name-tag {
        font-size: 8.5pt;
        color: #F8FAFC;
        font-weight: 700;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .player-rating-tag {
        background-color: #EAB308;
        color: #020617;
        font-size: 7.5pt;
        font-weight: 800;
        border-radius: 4px;
        padding: 2px 6px;
        margin-top: 4px;
        display: inline-block;
    }
    
    /* Caixas de Informações de Análise */
    .stat-box {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 20px;
        border-left: 6px solid #EAB308;
        margin-bottom: 18px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Sidebar Escura */
    section[data-testid="stSidebar"] {
        background-color: #020617 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }
    
    /* Clean UI */
    header[data-testid="stHeader"], #MainMenu, footer, .stDeployButton {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. FONTE ÚNICA DE VERDADE (POSIÇÕES OFICIAIS)
# ==========================================
POSICOES_OFICIAIS = [
    "Goleiro", "Lateral-direito", "Lateral-esquerdo", "Zagueiro", "Volante",
    "Mezzala esquerdo", "Mezzala direito", "Meia-armador", 
    "Ponta-esquerda", "Ponta-direita", "Segundo atacante", "Centroavante"
]

ABREVIACOES = {
    "Goleiro": "GOL", "Lateral-direito": "LD", "Lateral-esquerdo": "LE", 
    "Zagueiro": "ZAG", "Volante": "VOL", "Mezzala esquerdo": "MCE", 
    "Mezzala direito": "MCD", "Meia-armador": "MEI", "Ponta-esquerda": "PE", 
    "Ponta-direita": "PD", "Segundo atacante": "SA", "Centroavante": "CA"
}

# ==========================================
# 4. GERENCIAMENTO DE BANCO DE DADOS (JSON)
# ==========================================
DATA_FILE = "jogadores_hexa_2030.json"

def normalizar_banco_dados(data):
    """
    Função guardiã: Limpa nomenclaturas erradas sem apagar os históricos táticos.
    """
    if "Vini Jr." in data:
        data["Vinicius Junior"] = data.pop("Vini Jr.")
        data["Vinicius Junior"]["nome"] = "Vinicius Junior"
        
    if "Wesley" in data and "Wesley França" not in data:
        data["Wesley França"] = data.pop("Wesley")
        data["Wesley França"]["nome"] = "Wesley França"

    # Mapeamento estrito para a lista POSICOES_OFICIAIS
    pos_map_limpeza = {
        "Goleiro": "Goleiro",
        "Lateral Esquerdo": "Lateral-esquerdo", "Lateral-esquerdo": "Lateral-esquerdo",
        "Lateral Direito": "Lateral-direito", "Lateral-direito": "Lateral-direito",
        "Zagueiro Esquerdo": "Zagueiro", "Zagueiro Direito": "Zagueiro", "Zagueiro": "Zagueiro",
        "Meio-Campo (Defensivo)": "Volante", "Volante": "Volante",
        "Meio-Campo (Apoio)": "Mezzala esquerdo", "Mezzala esquerdo": "Mezzala esquerdo", "Mezzala direito": "Mezzala direito",
        "Meio-Campo (Criativo)": "Meia-armador", "Meia-armador": "Meia-armador",
        "Ponta Esquerda": "Ponta-esquerda", "Ponta-esquerda": "Ponta-esquerda", "Ponta-esquerdo": "Ponta-esquerda", "Ponta-Tail": "Ponta-esquerda", "Ponta-Core": "Ponta-esquerda",
        "Ponta Direita": "Ponta-direita", "Ponta-direita": "Ponta-direita", "Ponta-direito": "Ponta-direita",
        "Segundo atacante": "Segundo atacante",
        "Centroavante": "Centroavante"
    }

    # Atualizações complementares para múltiplos posicionamentos
    atualizacoes_obrigatorias = {
        "Wesley França": {"posicao": "Lateral-direito", "posicoes_multiplas": ["Lateral-direito", "Lateral-esquerdo"]},
        "Denner": {"posicao": "Lateral-esquerdo", "posicoes_multiplas": ["Lateral-esquerdo"]},
        "Luciano Juba": {"posicao": "Lateral-esquerdo", "posicoes_multiplas": ["Lateral-esquerdo", "Mezzala esquerdo"]},
        "Lucas Beraldo": {"posicao": "Zagueiro", "posicoes_multiplas": ["Zagueiro", "Lateral-esquerdo"]},
        "Andrey Santos": {"posicao": "Volante", "posicoes_multiplas": ["Volante", "Mezzala esquerdo", "Mezzala direito", "Lateral-esquerdo"]},
        "Bruno Guimarães": {"posicao": "Mezzala esquerdo", "posicoes_multiplas": ["Mezzala esquerdo", "Mezzala direito", "Volante"]},
        "Rodrygo": {"posicao": "Ponta-direita", "posicoes_multiplas": ["Ponta-direita", "Ponta-esquerda", "Meia-armador", "Segundo atacante", "Centroavante"]},
        "Breno Bidon": {"posicao": "Mezzala esquerdo", "posicoes_multiplas": ["Mezzala esquerdo", "Mezzala direito", "Volante", "Meia-armador"]},
        "Gabriel Mec": {"posicao": "Meia-armador", "posicoes_multiplas": ["Meia-armador", "Ponta-esquerda", "Segundo atacante"]},
        "Vinicius Junior": {"posicao": "Ponta-esquerda", "posicoes_multiplas": ["Ponta-esquerda", "Segundo atacante", "Centroavante"]},
        "Estevão": {"posicao": "Ponta-direita", "posicoes_multiplas": ["Ponta-direita", "Meia-armador"]},
        "Gabriel Martinelli": {"posicao": "Ponta-esquerda", "posicoes_multiplas": ["Ponta-esquerda", "Meia-armador", "Mezzala esquerdo"]}
    }

    for jogador, info in data.items():
        # Limpeza da posição principal
        curr_pos = info.get("posicao")
        if curr_pos in pos_map_limpeza:
            info["posicao"] = pos_map_limpeza[curr_pos]
        elif curr_pos not in POSICOES_OFICIAIS:
            info["posicao"] = "Volante" # Fallback de segurança
            
        # Garantir inicialização de posições múltiplas
        if "posicoes_multiplas" not in info or not info["posicoes_multiplas"]:
            info["posicoes_multiplas"] = [info["posicao"]]
        else:
            # Limpar a lista de posições múltiplas também
            info["posicoes_multiplas"] = [pos_map_limpeza.get(p, p) for p in info["posicoes_multiplas"] if pos_map_limpeza.get(p, p) in POSICOES_OFICIAIS]

    # Aplicar as atualizações obrigatórias (subscrevendo quando necessário)
    for jogador, campos in atualizacoes_obrigatorias.items():
        if jogador in data:
            for campo, valor in campos.items():
                data[jogador][campo] = valor

    return data

def carregar_jogadores():
    contingencia = {
        "Alisson": {"nome": "Alisson", "posicao": "Goleiro", "clube": "Liverpool", "idade": 33, "grupo": "Titulares", "tipo": "Certeza Atual", "nota_vini": 7.0, "nota_roberto": 7.5, "posicoes_multiplas": ["Goleiro"]},
        "Kaiki Bruno": {"nome": "Kaiki Bruno", "posicao": "Lateral-esquerdo", "clube": "Cruzeiro", "idade": 23, "grupo": "Titulares", "tipo": "Certeza Atual", "nota_vini": 6.0, "nota_roberto": 6.0, "posicoes_multiplas": ["Lateral-esquerdo"]},
        "Gabriel Magalhães": {"nome": "Gabriel Magalhães", "posicao": "Zagueiro", "clube": "Arsenal", "idade": 28, "grupo": "Titulares", "tipo": "Certeza Atual", "nota_vini": 9.0, "nota_roberto": 9.0, "posicoes_multiplas": ["Zagueiro"]},
        "Lucas Beraldo": {"nome": "Lucas Beraldo", "posicao": "Zagueiro", "clube": "Paris Saint-Germain", "idade": 22, "grupo": "Titulares", "tipo": "Certeza Atual", "nota_vini": 8.0, "nota_roberto": 8.0, "posicoes_multiplas": ["Zagueiro", "Lateral-esquerdo"]},
        "Wesley França": {"nome": "Wesley França", "posicao": "Lateral-direito", "clube": "Roma", "idade": 22, "grupo": "Titulares", "tipo": "Certeza Atual", "nota_vini": 7.5, "nota_roberto": 7.5, "posicoes_multiplas": ["Lateral-direito", "Lateral-esquerdo"]},
        "Andrey Santos": {"nome": "Andrey Santos", "posicao": "Volante", "clube": "Chelsea", "idade": 22, "grupo": "Titulares", "tipo": "Certeza Atual", "nota_vini": 7.5, "nota_roberto": 8.0, "posicoes_multiplas": ["Volante", "Mezzala esquerdo", "Mezzala direito", "Lateral-esquerdo"]},
        "Bruno Guimarães": {"nome": "Bruno Guimarães", "posicao": "Mezzala esquerdo", "clube": "Newcastle", "idade": 28, "grupo": "Titulares", "tipo": "Certeza Atual", "nota_vini": 8.0, "nota_roberto": 8.5, "posicoes_multiplas": ["Mezzala esquerdo", "Mezzala direito", "Volante"]},
        "Rodrygo": {"nome": "Rodrygo", "posicao": "Ponta-direita", "clube": "Real Madrid", "idade": 25, "grupo": "Titulares", "tipo": "Certeza Atual", "nota_vini": 8.0, "nota_roberto": 8.0, "posicoes_multiplas": ["Ponta-direita", "Ponta-esquerda", "Meia-armador", "Segundo atacante", "Centroavante"]},
        "Vinicius Junior": {"nome": "Vinicius Junior", "posicao": "Ponta-esquerda", "clube": "Real Madrid", "idade": 26, "grupo": "Titulares", "tipo": "Certeza Atual", "nota_vini": 9.0, "nota_roberto": 9.0, "posicoes_multiplas": ["Ponta-esquerda", "Segundo atacante", "Centroavante"]},
        "Endrick": {"nome": "Endrick", "posicao": "Centroavante", "clube": "Real Madrid", "idade": 19, "grupo": "Titulares", "tipo": "Certeza Atual", "nota_vini": 8.0, "nota_roberto": 9.0, "posicoes_multiplas": ["Centroavante"]},
        "Estevão": {"nome": "Estevão", "posicao": "Ponta-direita", "clube": "Palmeiras", "idade": 19, "grupo": "Titulares", "tipo": "Promessa 2030", "nota_vini": 9.0, "nota_roberto": 10.0, "posicoes_multiplas": ["Ponta-direita", "Meia-armador"]}
    }
    
    if not os.path.exists(DATA_FILE):
        salvar_jogadores(contingencia)
        return contingencia
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data = normalizar_banco_dados(data)
        
        # Corrige erro de digitação de nomes passados sem alterar as notas de scout
        for k, v in data.items():
            if "historico" in v and "Vini Leoneo" in v["historico"]:
                v["historico"] = v["historico"].replace("Vini Leoneo", "Vini Leonel")
        
        salvar_jogadores(data)
        return data
    except Exception:
        return contingencia

def salvar_jogadores(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

jogadores = carregar_jogadores()

# ==========================================
# 5. MOTOR LIVE SCRAPING (CBF BRASILEIRÃO)
# ==========================================
@st.cache_data(ttl=600)
def buscar_classificacao_cbf():
    url_base = "https://www.cbf.com.br/futebol-brasileiro"
    urls = {
        "Série A": f"{url_base}/tabelas/campeonato-brasileiro/serie-a",
        "Série B": f"{url_base}/tabelas/campeonato-brasileiro/serie-b"
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    dados_cbf = {}
    
    for serie, url in urls.items():
        try:
            resposta = requests.get(url, headers=headers, timeout=10)
            if resposta.status_code == 200:
                soup = BeautifulSoup(resposta.content, "html.parser")
                tabela = soup.find("table") or soup.find(class_="table") or soup.find(class_="tabela-completa")
                if tabela:
                    linhas = tabela.find_all("tr")
                    for linha in linhas[1:]:
                        colunas = linha.find_all("td")
                        if len(colunas) >= 5:
                            posicao = "".join(filter(str.isdigit, colunas[0].text.strip()))
                            nome_chave = " ".join(colunas[1].text.strip().split()).lower()
                            dados_cbf[nome_chave] = {
                                "posicao": f"{posicao}º",
                                "pts": colunas[2].text.strip(),
                                "jogos": colunas[3].text.strip(),
                                "vitorias": colunas[4].text.strip(),
                                "serie": serie
                            }
        except Exception:
            pass
    return dados_cbf

tabela_ao_vivo_cbf = buscar_classificacao_cbf()

TABELA_BACKUP_CBF = {
    "palmeiras": {"posicao": "1º", "pts": "41", "jogos": "19", "vitorias": "12", "serie": "Série A"},
    "flamengo": {"posicao": "2º", "pts": "35", "jogos": "18", "vitorias": "10", "serie": "Série A"}
}

def obter_dados_reais_clube(clube):
    clube_busca = clube.lower().strip()
    for chave_time, dados in tabela_ao_vivo_cbf.items():
        if clube_busca in chave_time or chave_time in clube_busca:
            return dados
    return TABELA_BACKUP_CBF.get(clube_busca, None)

# ==========================================
# 6. MATRIZ TÁTICA DO CARLO ANCELOTTI
# ==========================================
# A matriz agora aceita EXCLUSIVAMENTE a nossa lista POSICOES_OFICIAIS
TATICAS = {
    "4-3-3 Clássico": {
        "Goleiro (GOL)": (["Goleiro"], "Alisson", "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": (["Lateral-esquerdo"], "Kaiki Bruno", "15%", "26%", "LE"),
        "Zagueiro Esquerdo (ZAG)": (["Zagueiro"], "Gabriel Magalhães", "37%", "23%", "ZAG"),
        "Zagueiro Direito (ZAG)": (["Zagueiro"], "Lucas Beraldo", "63%", "23%", "ZAG"),
        "Lateral-direito (LD)": (["Lateral-direito"], "Wesley França", "85%", "26%", "LD"),
        "Volante (VOL)": (["Volante"], "Andrey Santos", "38%", "46%", "VOL"),
        "Volante Apoio (VOL)": (["Volante", "Mezzala esquerdo", "Mezzala direito"], "Bruno Guimarães", "62%", "46%", "VOL"),
        "Meia-Armador (MEI)": (["Meia-armador"], "Rodrygo", "50%", "58%", "MEI"),
        "Ponta-esquerda (PE)": (["Ponta-esquerda"], "Vinicius Junior", "20%", "80%", "PE"),
        "Centroavante (CA)": (["Centroavante"], "Endrick", "50%", "84%", "CA"),
        "Ponta-direita (PD)": (["Ponta-direita"], "Estevão", "80%", "80%", "PD")
    },
    "4-3-3 Diamante": {
        "Goleiro (GOL)": (["Goleiro"], "Alisson", "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": (["Lateral-esquerdo"], "Kaiki Bruno", "15%", "26%", "LE"),
        "Zagueiro Esquerdo (ZAG)": (["Zagueiro"], "Gabriel Magalhães", "37%", "23%", "ZAG"),
        "Zagueiro Direito (ZAG)": (["Zagueiro"], "Lucas Beraldo", "63%", "23%", "ZAG"),
        "Lateral-direito (LD)": (["Lateral-direito"], "Wesley França", "85%", "26%", "LD"),
        "Volante (VOL)": (["Volante"], "Andrey Santos", "50%", "43%", "VOL"),
        "Mezzala Esquerdo (MCE)": (["Mezzala esquerdo"], "Bruno Guimarães", "32%", "53%", "MCE"),
        "Mezzala Direito (MCD)": (["Mezzala direito", "Mezzala esquerdo", "Meia-armador"], "Breno Bidon", "68%", "53%", "MCD"),
        "Ponta-esquerda (PE)": (["Ponta-esquerda"], "Vinicius Junior", "20%", "80%", "PE"),
        "Centroavante (CA)": (["Centroavante"], "Endrick", "50%", "84%", "CA"),
        "Ponta-direita (PD)": (["Ponta-direita"], "Estevão", "80%", "80%", "PD")
    },
    "4-4-2 Clássico": {
        "Goleiro (GOL)": (["Goleiro"], "Alisson", "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": (["Lateral-esquerdo"], "Kaiki Bruno", "15%", "26%", "LE"),
        "Zagueiro Esquerdo (ZAG)": (["Zagueiro"], "Gabriel Magalhães", "37%", "23%", "ZAG"),
        "Zagueiro Direito (ZAG)": (["Zagueiro"], "Lucas Beraldo", "63%", "23%", "ZAG"),
        "Lateral-direito (LD)": (["Lateral-direito"], "Wesley França", "85%", "26%", "LD"),
        "Meia-Esquerda (ME)": (["Ponta-esquerda", "Mezzala esquerdo", "Lateral-esquerdo"], "Vinicius Junior", "15%", "55%", "ME"),
        "Volante (VOL)": (["Volante"], "Andrey Santos", "38%", "45%", "VOL"),
        "Volante Apoio (VOL)": (["Volante", "Mezzala esquerdo", "Mezzala direito"], "Bruno Guimarães", "62%", "45%", "VOL"),
        "Meia-Direita (MD)": (["Ponta-direita", "Lateral-direito"], "Estevão", "85%", "55%", "MD"),
        "Segundo Atacante (SA)": (["Segundo atacante", "Ponta-esquerda", "Ponta-direita", "Meia-armador"], "Rodrygo", "35%", "82%", "SA"),
        "Centroavante (CA)": (["Centroavante"], "Endrick", "65%", "82%", "CA")
    },
    "4-4-2 Diamante": {
        "Goleiro (GOL)": (["Goleiro"], "Alisson", "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": (["Lateral-esquerdo"], "Kaiki Bruno", "15%", "26%", "LE"),
        "Zagueiro Esquerdo (ZAG)": (["Zagueiro"], "Gabriel Magalhães", "37%", "23%", "ZAG"),
        "Zagueiro Direito (ZAG)": (["Zagueiro"], "Lucas Beraldo", "63%", "23%", "ZAG"),
        "Lateral-direito (LD)": (["Lateral-direito"], "Wesley França", "85%", "26%", "LD"),
        "Volante (VOL)": (["Volante"], "Andrey Santos", "50%", "42%", "VOL"),
        "Mezzala Esquerdo (MCE)": (["Mezzala esquerdo"], "Bruno Guimarães", "32%", "53%", "MCE"),
        "Mezzala Direito (MCD)": (["Mezzala direito", "Mezzala esquerdo", "Meia-armador"], "Breno Bidon", "68%", "53%", "MCD"),
        "Meia-Armador (MEI)": (["Meia-armador"], "Rodrygo", "50%", "65%", "MEI"),
        "Segundo Atacante (SA)": (["Ponta-esquerda", "Ponta-direita", "Segundo atacante", "Centroavante"], "Vinicius Junior", "35%", "83%", "SA"),
        "Centroavante (CA)": (["Centroavante"], "Endrick", "65%", "83%", "CA")
    }
}

def obter_atletas_compativeis(pos_permitidas):
    filtrados = []
    for nome, dados in jogadores.items():
        pos_do_atleta = dados.get("posicoes_multiplas", [dados.get("posicao")])
        if any(pos in pos_permitidas for pos in pos_do_atleta):
            filtrados.append(nome)
    return sorted(filtrados)

def formatar_jogador_com_posicao(nome):
    p = jogadores.get(nome)
    if not p:
        return nome
    pos_list = p.get("posicoes_multiplas", [p.get("posicao", "OBS")])
    abrevs = [ABREVIACOES.get(pos, "OBS") for pos in pos_list]
    abrev_str = "/".join(sorted(set(abrevs), key=abrevs.index))
    return f"{nome} ({abrev_str})"

# ==========================================
# 7. MENU LATERAL & NAVEGAÇÃO UNIVERSAL
# ==========================================
st.sidebar.markdown("<h2 style='text-align: center; color: #EAB308; margin-top:15px;'>CONSELHO TÁTICO</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação do Painel:",
    ["🏟️ Campo de Jogo", "👤 Perfis dos Jogadores", "📋 Gestão do Roster", "📊 Análise de Opiniões"]
)

if "escalados" not in st.session_state:
    st.session_state.escalados = {
        "Goleiro (GOL)": "Alisson", "Lateral-esquerdo (LE)": "Kaiki Bruno",
        "Zagueiro Esquerdo (ZAG)": "Gabriel Magalhães", "Zagueiro Direito (ZAG)": "Lucas Beraldo",
        "Lateral-direito (LD)": "Wesley França", "Volante (VOL)": "Andrey Santos",
        "Volante Apoio (VOL)": "Bruno Guimarães", "Meia-Armador (MEI)": "Rodrygo",
        "Ponta-esquerda (PE)": "Vinicius Junior", "Centroavante (CA)": "Endrick",
        "Ponta-direita (PD)": "Estevão"
    }

# ==========================================
# 8. TELAS DO APLICATIVO
# ==========================================
if menu == "🏟️ Campo de Jogo":
    st.markdown("<h1 class='app-title'>🏆 O Caminho para o Hexa</h1>", unsafe_allow_html=True)
    st.markdown("<p class='project-subtitle' style='text-align: center;'>Painel tático interativo desenvolvido para organizar escalações, avaliar pontuações de scout e planejar o percurso de renovação.</p>", unsafe_allow_html=True)
    
    col_config, col_campo = st.columns([1, 2])
    
    with col_config:
        st.markdown("### 📋 Calibrar Escalação")
        tática_ativa = st.selectbox("Esquema Tático (Carlo Ancelotti):", list(TATICAS.keys()), key="tactical_selector")
        layout_ativo = TATICAS[tática_ativa]
        
        if "ultima_formacao" not in st.session_state or st.session_state.ultima_formacao != tática_ativa:
            nova_escalacao = {}
            for slot, info in layout_ativo.items():
                pos_validas, atleta_padrao = info[0], info[1]
                atleta_reutilizado = None
                if "escalados" in st.session_state:
                    for old_slot, old_player in st.session_state.escalados.items():
                        if old_player in jogadores:
                            pos_do_atleta = jogadores[old_player].get("posicoes_multiplas", [jogadores[old_player]["posicao"]])
                            if any(pos in pos_validas for pos in pos_do_atleta) and old_player not in nova_escalacao.values():
                                atleta_reutilizado = old_player
                                break
                nova_escalacao[slot] = atleta_reutilizado if atleta_reutilizado else atleta_padrao
            st.session_state.escalados = nova_escalacao
            st.session_state.ultima_formacao = tática_ativa
            st.rerun()

        novos_titulares = {}
        for slot, info in layout_ativo.items():
            valid_names = obter_atletas_compativeis(info[0])
            available_choices = [name for name in valid_names if name not in novos_titulares.values()]
            if not available_choices: available_choices = valid_names
            default_val = st.session_state.escalados.get(slot, info[1])
            if default_val not in available_choices: available_choices.append(default_val)
            available_choices = sorted(list(set(available_choices)))
            idx = available_choices.index(default_val) if default_val in available_choices else 0
            escolha_selecionada = st.selectbox(f"{slot}:", available_choices, index=idx, format_func=formatar_jogador_com_posicao, key=f"field_{tática_ativa}_{slot}")
            novos_titulares[slot] = escolha_selecionada
        st.session_state.escalados = novos_titulares

    with col_campo:
        players_html = ""
        for slot, info in layout_ativo.items():
            pos_validas, left, bottom, pos_tag = info[0], info[2], info[3], info[4]
            player_name = st.session_state.escalados.get(slot, info[1])
            p_data = jogadores.get(player_name, {"nome": player_name, "nota_vini": 0, "nota_roberto": 0})
            
            player_multi_pos = p_data.get("posicoes_multiplas", [p_data.get("posicao")])
            match_index = next((i for i, p in enumerate(player_multi_pos) if p in pos_validas), -1)
            
            # Dinâmica de Cores do Card via Aderência Tática
            border_color = "#22C55E" if match_index == 0 else "#EAB308" if match_index == 1 else "#F97316"
            
            players_html += (
                f'<div class="player-node" style="left:{left};bottom:{bottom};">'
                f'<div class="player-card-pitch" style="border-color: {border_color} !important;">'
                f'<div class="player-pos-tag">{pos_tag}</div>'
                f'<div class="player-name-tag">{p_data["nome"]}</div>'
                f'<div class="player-rating-tag">★ {p_data.get("nota_vini", 0):.1f} / {p_data.get("nota_roberto", 0):.1f}</div>'
                f'</div></div>'
            )
        
        st.markdown(f'<div class="pitch-container"><div class="pitch-line-center"></div><div class="pitch-circle"></div><div class="pitch-penalty-top"></div><div class="pitch-penalty-bottom"></div>{players_html}</div>', unsafe_allow_html=True)

elif menu == "👤 Perfis dos Jogadores":
    st.title("👤 Ficha Individual do Atleta")
    selected_name = st.selectbox("Escolha o Atleta:", sorted(list(jogadores.keys())))
    p = jogadores[selected_name]
    
    col_p, col_d = st.columns([1, 2])
    with col_p:
        st.markdown(f"""
        <div style="background-color: #1E293B; padding: 25px; border-radius: 15px; border: 3px solid #EAB308; text-align: center;">
            <h2 style="color: #F8FAFC; margin-bottom: 5px; font-size: 2.2rem;">{p.get('nome', selected_name)}</h2>
            <p style="margin-top: 20px; font-size: 11pt; color: #CBD5E1; text-align: left; line-height: 1.8;">
                <b>🏢 Clube Atual:</b> {p.get('clube', 'N/A')}<br>
                <b>📅 Idade (2026):</b> {p.get('idade', 22)} anos<br>
                <b>🏆 Idade (2030):</b> <span style="color:#EAB308; font-weight:bold;">{p.get('idade', 22) + 4} anos</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.metric("Nota do Vini", f"{p.get('nota_vini', 0.0):.1f} / 10")
        st.metric("Nota do Roberto", f"{p.get('nota_roberto', 0.0):.1f} / 10")

    with col_d:
        st.markdown("### 📝 Dossiê Histórico de Discussões")
        st.markdown('<div class="stat-box">**🟢 Pontos Fortes:**<br>'+p.get("pontos_fortes", "N/A")+'</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-box" style="border-left-color: #EF4444;">**🔴 Desafios:**<br>'+p.get("pontos_fracos", "N/A")+'</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-box" style="border-left-color: #3B82F6;">**🗣️ Histórico:**<br>'+p.get("historico", "N/A")+'</div>', unsafe_allow_html=True)

elif menu == "📋 Gestão do Roster":
    st.title("📋 Gerenciador do Banco de Dados")
    tab_list, tab_add = st.tabs(["Jogadores Inscritos", "➕ Inscrever Nova Joia"])
    
    with tab_list:
        df_players = pd.DataFrame([{"Nome": k, "Posição": v.get("posicao"), "Clube": v.get("clube")} for k, v in jogadores.items()])
        st.dataframe(df_players, use_container_width=True)
        
        remover_nome = st.selectbox("Selecione quem quer cortar:", list(jogadores.keys()))
        if st.button("Confirmar Corte Permanente") and remover_nome in jogadores:
            del jogadores[remover_nome]
            salvar_jogadores(jogadores)
            st.success(f"{remover_nome} foi cortado com sucesso!")
            st.rerun()

    with tab_add:
        with st.form("add_player_form"):
            new_nome = st.text_input("Nome do Jogador*")
            new_pos = st.selectbox("Posição Principal*", POSICOES_OFICIAIS)
            new_clube = st.text_input("Clube Atual")
            new_idade = st.number_input("Idade em 2026", min_value=15, max_value=45, value=22)
            col_n1, col_n2 = st.columns(2)
            with col_n1: new_nota_vini = st.slider("Nota do Vini", 0.0, 10.0, 7.5, step=0.5)
            with col_n2: new_nota_rob = st.slider("Nota do Roberto", 0.0, 10.0, 7.5, step=0.5)
            new_fortes = st.text_area("Pontos Fortes")
            new_fracos = st.text_area("Pontos Fracos")
            new_hist = st.text_area("Notas e Histórico de Conversas")
            
            if st.form_submit_button("Inscrever Jogador") and new_nome:
                jogadores[new_nome] = {
                    "nome": new_nome, "posicao": new_pos, "clube": new_clube, "idade": int(new_idade),
                    "nota_vini": float(new_nota_vini), "nota_roberto": float(new_nota_rob),
                    "pontos_fortes": new_fortes, "pontos_fracos": new_fracos, "historico": new_hist,
                    "posicoes_multiplas": [new_pos]
                }
                salvar_jogadores(jogadores)
                st.success("Salvo!")
                st.rerun()

elif menu == "📊 Análise de Opiniões":
    st.title("📊 Análise de Divergências Técnicas")
    df_stats = pd.DataFrame([{"Nome": k, "Vini": v.get("nota_vini", 0), "Roberto": v.get("nota_roberto", 0), "Diferença": abs(v.get("nota_vini", 0) - v.get("nota_roberto", 0))} for k, v in jogadores.items()])
    st.dataframe(df_stats.sort_values(by="Diferença", ascending=False), use_container_width=True)

# Rodapé de versão
st.sidebar.markdown("---")
st.sidebar.caption("App desenvolvido por Vini Leonel & Beto Muñoz | v2.0 HexaMaster")