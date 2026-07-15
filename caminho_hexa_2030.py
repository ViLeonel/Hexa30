import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(
    page_title="O Caminho para o Hexa 2030",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to style the football pitch and UI elements
st.markdown("""
<style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .pitch-container {
        background-color: #1b4d3e;
        border: 4px solid #ffffff;
        border-radius: 15px;
        padding: 20px;
        position: relative;
        min-height: 650px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    .pitch-line-center {
        position: absolute;
        top: 50%;
        left: 0;
        width: 100%;
        height: 2px;
        background-color: rgba(255, 255, 255, 0.6);
    }
    .pitch-circle {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 150px;
        height: 150px;
        border: 2px solid rgba(255, 255, 255, 0.6);
        border-radius: 50%;
    }
    .pitch-penalty-top {
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 250px;
        height: 100px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.6);
        border-left: 2px solid rgba(255, 255, 255, 0.6);
        border-right: 2px solid rgba(255, 255, 255, 0.6);
    }
    .pitch-penalty-bottom {
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 250px;
        height: 100px;
        border-top: 2px solid rgba(255, 255, 255, 0.6);
        border-left: 2px solid rgba(255, 255, 255, 0.6);
        border-right: 2px solid rgba(255, 255, 255, 0.6);
    }
    .player-card {
        background: rgba(15, 23, 42, 0.85);
        border: 2px solid #eab308;
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        color: white;
        font-weight: bold;
        font-size: 11pt;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .player-card:hover {
        transform: scale(1.05);
        border-color: #22c55e;
    }
    .rating-badge {
        background-color: #eab308;
        color: #0f172a;
        border-radius: 4px;
        padding: 1px 5px;
        font-size: 9pt;
        margin-left: 5px;
    }
    .stat-box {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #eab308;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# File to store player data
DATA_FILE = "jogadores_hexa_2030.json"

# Default pre-populated players from Roberto & Vini's actual chat
DEFAULT_PLAYERS = {
    "Alisson": {
        "nome": "Alisson", "posicao": "Goleiro", "grupo": "Titulares", "nota_vini": 7.0, "nota_roberto": 7.5,
        "clube": "Liverpool", "idade": 33, "tipo": "Certeza Atual",
        "pontos_fortes": "Experiência de Copa, posicionamento excelente, condução de carreira séria.",
        "pontos_fracos": "Idade avançada para 2030 (estará com 37 anos).",
        "historico": "Considerado o melhor atualmente, mas Roberto o descartaria para o ciclo todo de 2030. Vini acha que dá para ser campeão com ele experiente."
    },
    "Brazão": {
        "nome": "Brazão", "posicao": "Goleiro", "grupo": "Reservas", "nota_vini": 7.5, "nota_roberto": 7.5,
        "clube": "Santos", "idade": 25, "tipo": "Promessa 2030",
        "pontos_fortes": "Teto de evolução altíssimo, boa envergadura.",
        "pontos_fracos": "Precisa de afirmação e minutos consistentes em alto nível.",
        "historico": "Roberto acredita que, dos novos goleiros, ele é o que possui o teto mais alto para 2030."
    },
    "Lucas Perri": {
        "nome": "Lucas Perri", "posicao": "Goleiro", "grupo": "Observação", "nota_vini": 6.5, "nota_roberto": 6.0,
        "clube": "Lyon", "idade": 28, "tipo": "Observação",
        "pontos_fortes": "Boa altura, joga na Europa, boa idade para goleiro.",
        "pontos_fracos": "Tem cedido à pressão em momentos cruciais.",
        "historico": "Vini o vê como bom segundo ou terceiro goleiro, mas sem depositar muitas esperanças."
    },
    "Wesley": {
        "nome": "Wesley", "posicao": "Lateral Direito", "grupo": "Titulares", "nota_vini": 7.5, "nota_roberto": 7.5,
        "clube": "Flamengo", "idade": 22, "tipo": "Promessa 2030",
        "pontos_fortes": "Extremamente físico, ofensivo, velocidade de elite.",
        "pontos_fracos": "Precisa melhorar defensivamente.",
        "historico": "Roberto o vê como futuro dono absoluto da posição com teto para ser nota 8+."
    },
    "Yan Couto": {
        "nome": "Yan Couto", "posicao": "Lateral Direito", "grupo": "Reservas", "nota_vini": 7.5, "nota_roberto": 7.0,
        "clube": "Borussia Dortmund", "idade": 24, "tipo": "Certeza Atual",
        "pontos_fortes": "Excelente apoio ofensivo, refino técnico.",
        "pontos_fracos": "Balanço defensivo e estatura.",
        "historico": "Garante um nível sólido (nota 7,5) na lateral direita ao lado de Wesley."
    },
    "Kaiki Bruno": {
        "nome": "Kaiki Bruno", "posicao": "Lateral Esquerdo", "grupo": "Titulares", "nota_vini": 6.0, "nota_roberto": 6.0,
        "clube": "Cruzeiro", "idade": 23, "tipo": "Promessa 2030",
        "pontos_fortes": "Ofensivo, rápido, boa margem de evolução.",
        "pontos_fracos": "Muito jovem, cru taticamente e defensivamente.",
        "historico": "Vini o acha muito bebê ainda, mas Roberto iniciaria o ciclo com ele por falta de opções melhores."
    },
    "Denner": {
        "nome": "Denner", "posicao": "Lateral Esquerdo", "grupo": "Reservas", "nota_vini": 7.0, "nota_roberto": 8.0,
        "clube": "Chelsea", "idade": 18, "tipo": "Promessa 2030",
        "pontos_fortes": "Diferenciado tecnicamente, drible, capacidade física de elite.",
        "pontos_fracos": "Muito jovem, acabou de chegar à Europa.",
        "historico": "Roberto o considera diferenciado pra caramba, com capacidade para ser nível Alphonso Davies."
    },
    "Luciano Juba": {
        "nome": "Luciano Juba", "posicao": "Lateral Esquerdo", "grupo": "Observação", "nota_vini": 6.5, "nota_roberto": 7.0,
        "clube": "Bahia", "idade": 26, "tipo": "Observação",
        "pontos_fortes": "Cruzamento de elite, boa batida na bola, polivalente.",
        "pontos_fracos": "Defesa em linha de 4 contra pontas mundiais.",
        "historico": "Roberto gosta da opção e brinca que traz de volta o charme dos apelidos da seleção."
    },
    "Gabriel Magalhães": {
        "nome": "Gabriel Magalhães", "posicao": "Zagueiro Esquerdo", "grupo": "Titulares", "nota_vini": 9.0, "nota_roberto": 9.0,
        "clube": "Arsenal", "idade": 28, "tipo": "Certeza Atual",
        "pontos_fortes": "Força física, imposição aérea (ofensiva e defensiva), liderança.",
        "pontos_fracos": "Velocidade em campo muito aberto contra pontas de elite.",
        "historico": "Unanimidade entre os amigos. Nível de classe mundial absoluto (Nota 9,0)."
    },
    "Lucas Beraldo": {
        "nome": "Lucas Beraldo", "posicao": "Zagueiro Direito", "grupo": "Titulares", "nota_vini": 8.0, "nota_roberto": 8.0,
        "clube": "PSG", "idade": 22, "tipo": "Promessa 2030",
        "pontos_fortes": "Saída de bola espetacular, inteligência tática, versatilidade (pode jogar de 1º volante).",
        "pontos_fracos": "Combates de força física pura na área.",
        "historico": "Vini destaca sua qualidade na canhota. Roberto aponta que ele tem jogado de volante no PSG e pode ser uma grande opção por ali."
    },
    "Murillo": {
        "nome": "Murillo", "posicao": "Zagueiro Direito", "grupo": "Reservas", "nota_vini": 8.0, "nota_roberto": 8.0,
        "clube": "Nottingham Forest", "idade": 23, "tipo": "Promessa 2030",
        "pontos_fortes": "Força física absurda, desarme preciso, passe longo de qualidade.",
        "pontos_fracos": "Concentração mental durante os 90 minutos.",
        "historico": "Roberto o considera de classe mundial e diz que ele ao lado de Magalhães dá muita segurança."
    },
    "Andrey Santos": {
        "nome": "Andrey Santos", "posicao": "Meio-Campo (Defensivo)", "grupo": "Titulares", "nota_vini": 7.5, "nota_roberto": 8.0,
        "clube": "Strasbourg / Chelsea", "idade": 22, "tipo": "Promessa 2030",
        "pontos_fortes": "Infiltração na área, poder de marcação, liderança de base.",
        "pontos_fracos": "Precisa de consolidação em um gigante europeu.",
        "historico": "Vini e Roberto concordam que ele é o pilar de sustentação ideal para o meio-campo pós-Casemiro."
    },
    "Bruno Guimarães": {
        "nome": "Bruno Guimarães", "posicao": "Meio-Campo (Apoio)", "grupo": "Titulares", "nota_vini": 8.0, "nota_roberto": 8.5,
        "clube": "Newcastle United", "idade": 28, "tipo": "Certeza Atual",
        "pontos_fortes": "Visão de jogo, controle de ritmo, passe de quebra de linhas.",
        "pontos_fracos": "Falta de velocidade pura.",
        "historico": "Absoluto no meio-campo. Considerado o cérebro da transição."
    },
    "Rodrygo": {
        "nome": "Rodrygo", "posicao": "Meio-Campo (Criativo)", "grupo": "Titulares", "nota_vini": 8.0, "nota_roberto": 8.0,
        "clube": "Real Madrid", "idade": 25, "tipo": "Certeza Atual",
        "pontos_fortes": "Refino técnico absurdo, associação rápida, finalização.",
        "pontos_fracos": "Não é um organizador clássico/pensador do ritmo do jogo.",
        "historico": "Adaptado para a função de 10 na falta de um armador clássico. Vini pondera que ele é vertical e não um pensador cadenciado."
    },
    "Breno Bidon": {
        "nome": "Breno Bidon", "posicao": "Meio-Campo (Apoio)", "grupo": "Reservas", "nota_vini": 7.0, "nota_roberto": 8.0,
        "clube": "Corinthians", "idade": 21, "tipo": "Promessa 2030",
        "pontos_fortes": "Ginga, drible curto, criatividade sob pressão.",
        "pontos_fracos": "Falta de físico europeu ainda.",
        "historico": "Roberto gosta muito e o quer na Europa para ganhar bagagem. É o reserva natural de transição."
    },
    "Gabriel Mec": {
        "nome": "Gabriel Mec", "posicao": "Meio-Campo (Criativo)", "grupo": "Observação", "nota_vini": 7.5, "nota_roberto": 7.5,
        "clube": "Grêmio", "idade": 18, "tipo": "Promessa 2030",
        "pontos_fortes": "Drible desconcertante, capacidade de dar passes decisivos ('pifar o ataque').",
        "pontos_fracos": "Extrema juventude, fragilidade física.",
        "historico": "Vini já está 'Mecquizado'. Roberto diz que ele sabe achar os atacantes e joga muito."
    },
    "Vini Jr.": {
        "nome": "Vini Jr.", "posicao": "Ponta Esquerda", "grupo": "Titulares", "nota_vini": 9.0, "nota_roberto": 9.0,
        "clube": "Real Madrid", "idade": 26, "tipo": "Certeza Atual",
        "pontos_fortes": "Melhor ponta do mundo, drible imparável, explosão física.",
        "pontos_fracos": "Controle emocional em provocações.",
        "historico": "O grande trunfo técnico e de liderança do ciclo. Nota 9 unânime."
    },
    "Estevão": {
        "nome": "Estevão", "posicao": "Ponta Direita", "grupo": "Titulares", "nota_vini": 9.0, "nota_roberto": 10.0,
        "clube": "Chelsea / Palmeiras", "idade": 19, "tipo": "Promessa 2030",
        "pontos_fortes": "Drible curto genial, finalização de fora da área, gênio da ponta.",
        "pontos_fracos": "Preocupação com lesões precoces no joelho.",
        "historico": "Roberto deu nota 10 pela genialidade. Vini deu 9 com medo do físico, mas ambos sabem que ele é o futuro."
    },
    "Endrick": {
        "nome": "Endrick", "posicao": "Centroavante", "grupo": "Titulares", "nota_vini": 8.0, "nota_roberto": 9.0,
        "clube": "Real Madrid", "idade": 19, "tipo": "Promessa 2030",
        "pontos_fortes": "Arrancada brutal, finalização cirúrgica com os dois pés, mentalidade forte.",
        "pontos_fracos": "Perda de espaço ou falta de minutos no clube europeu.",
        "historico": "O centroavante titular absoluto do projeto do Hexa."
    }
}

# Helper functions to load/save data
def carregar_jogadores():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_PLAYERS, f, indent=4, ensure_ascii=False)
        return DEFAULT_PLAYERS
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return DEFAULT_PLAYERS

def salvar_jogadores(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Load database
jogadores = carregar_jogadores()

# Sidebar Navigation
st.sidebar.image("https://upload.wikimedia.org/wikipedia/pt/e/e4/Confedera%C3%A7%C3%A3o_Brasileira_de_Futebol_2019.svg", width=80)
st.sidebar.title("O Caminho para o Hexa 2030")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação",
    ["🏟️ Campo de Jogo (Escalação)", "📋 Gestão do Roster", "👤 Detalhes & Páginas de Jogadores", "📊 Estatísticas & Análises"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Ciclo 2026-2030**\n\n"
    "Projeto interativo criado por Roberto Munoz & Vini para acompanhar a evolução da Seleção rumo ao Hexa."
)

# ----------------- TELA 1: CAMPO DE JOGO -----------------
if menu == "🏟️ Campo de Jogo (Escalação)":
    st.title("🏟️ O Campo do Hexa 2030")
    st.write("Esta é a escalação ideal projetada por Roberto e Vini na formação **4-3-3** do técnico Carlo Ancelotti.")
    
    # Calculate Averages
    titulares_list = [j for j in jogadores.values() if j['grupo'] == 'Titulares']
    if titulares_list:
        vini_avg = sum(j['nota_vini'] for j in titulares_list) / len(titulares_list)
        roberto_avg = sum(j['nota_roberto'] for j in titulares_list) / len(titulares_list)
        geral_avg = (vini_avg + roberto_avg) / 2
    else:
        vini_avg, roberto_avg, geral_avg = 0, 0, 0

    col_metrics = st.columns(3)
    with col_metrics[0]:
        st.metric("Média do Vini", f"{vini_avg:.2f} / 10", delta=None)
    with col_metrics[1]:
        st.metric("Média do Roberto", f"{roberto_avg:.2f} / 10", delta=None)
    with col_metrics[2]:
        st.metric("Nota Geral do Time", f"{geral_avg:.2f} / 10", delta="Seleção Nota 8", delta_color="normal")

    st.markdown("---")

    # Draw the Football Pitch visually
    # We will map standard position slots to specific coordinates using columns to build a grid
    st.subheader("Disposição Tática (4-3-3)")
    
    # Grid construction for 4-3-3
    # Attack Row
    lw = jogadores.get("Vini Jr.", {"nome": "Vini Jr.", "nota_vini": 9.0})
    st_f = jogadores.get("Endrick", {"nome": "Endrick", "nota_vini": 8.0})
    rw = jogadores.get("Estevão", {"nome": "Estevão", "nota_vini": 9.5})
    
    # Midfield Row
    me_l = jogadores.get("Bruno Guimarães", {"nome": "B. Guimarães", "nota_vini": 8.0})
    me_c = jogadores.get("Rodrygo", {"nome": "Rodrygo (10)", "nota_vini": 8.0})
    me_r = jogadores.get("Andrey Santos", {"nome": "Andrey Santos", "nota_vini": 7.5})
    
    # Defense Row
    lb = jogadores.get("Kaiki Bruno", {"nome": "Kaiki Bruno", "nota_vini": 6.0})
    lcb = jogadores.get("Gabriel Magalhães", {"nome": "G. Magalhães", "nota_vini": 9.0})
    rcb = jogadores.get("Lucas Beraldo", {"nome": "Lucas Beraldo", "nota_vini": 8.0})
    rb = jogadores.get("Wesley", {"nome": "Wesley", "nota_vini": 7.5})
    
    # Goalkeeper
    gk = jogadores.get("Alisson", {"nome": "Alisson", "nota_vini": 7.25})

    with st.container():
        st.markdown('<div class="pitch-container">', unsafe_allow_html=True)
        st.markdown('<div class="pitch-line-center"></div>', unsafe_allow_html=True)
        st.markdown('<div class="pitch-circle"></div>', unsafe_allow_html=True)
        st.markdown('<div class="pitch-penalty-top"></div>', unsafe_allow_html=True)
        st.markdown('<div class="pitch-penalty-bottom"></div>', unsafe_allow_html=True)
        
        # Row 1: Attackers
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown(f'<div class="player-card">PE: {lw["nome"]}<br><span class="rating-badge">★ {lw.get("nota_vini", 0.0)}</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="player-card">CA: {st_f["nome"]}<br><span class="rating-badge">★ {st_f.get("nota_vini", 0.0)}</span></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="player-card">PD: {rw["nome"]}<br><span class="rating-badge">★ {rw.get("nota_vini", 0.0)}</span></div>', unsafe_allow_html=True)
        
        st.write("")
        st.write("")
        st.write("")

        # Row 2: Midfielders
        col4, col5, col6 = st.columns([1, 1, 1])
        with col4:
            st.markdown(f'<div class="player-card">MEZ: {me_l["nome"]}<br><span class="rating-badge">★ {me_l.get("nota_vini", 0.0)}</span></div>', unsafe_allow_html=True)
        with col5:
            st.markdown(f'<div class="player-card">10: {me_c["nome"]}<br><span class="rating-badge">★ {me_c.get("nota_vini", 0.0)}</span></div>', unsafe_allow_html=True)
        with col6:
            st.markdown(f'<div class="player-card">VOL: {me_r["nome"]}<br><span class="rating-badge">★ {me_r.get("nota_vini", 0.0)}</span></div>', unsafe_allow_html=True)

        st.write("")
        st.write("")
        st.write("")

        # Row 3: Defenders
        col7, col8, col9, col10 = st.columns([1, 1, 1, 1])
        with col7:
            st.markdown(f'<div class="player-card">LE: {lb["nome"]}<br><span class="rating-badge">★ {lb.get("nota_vini", 0.0)}</span></div>', unsafe_allow_html=True)
        with col8:
            st.markdown(f'<div class="player-card">ZAG: {lcb["nome"]}<br><span class="rating-badge">★ {lcb.get("nota_vini", 0.0)}</span></div>', unsafe_allow_html=True)
        with col9:
            st.markdown(f'<div class="player-card">ZAG: {rcb["nome"]}<br><span class="rating-badge">★ {rcb.get("nota_vini", 0.0)}</span></div>', unsafe_allow_html=True)
        with col10:
            st.markdown(f'<div class="player-card">LD: {rb["nome"]}<br><span class="rating-badge">★ {rb.get("nota_vini", 0.0)}</span></div>', unsafe_allow_html=True)

        st.write("")
        st.write("")

        # Row 4: Goalkeeper
        col11, col12, col13 = st.columns([1.5, 1, 1.5])
        with col12:
            st.markdown(f'<div class="player-card">GOL: {gk["nome"]}<br><span class="rating-badge">★ {gk.get("nota_vini", 0.0)}</span></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- TELA 2: GESTÃO DO ROSTER -----------------
elif menu == "📋 Gestão do Roster":
    st.title("📋 Painel de Controle de Jogadores")
    st.write("Adicione novos jogadores descobertos, edite informações ou mude um atleta de categoria (Titular / Reserva / Observação).")
    
    tab_list, tab_add = st.tabs(["Listagem Atual", "➕ Adicionar Novo Jogador"])
    
    with tab_list:
        # We can view the existing players in a table, delete them or edit them.
        df_players = pd.DataFrame([
            {
                "Nome": k,
                "Posição": v["posicao"],
                "Clube": v["clube"],
                "Idade": v["idade"],
                "Grupo": v["grupo"],
                "Nota Vini": v["nota_vini"],
                "Nota Roberto": v["nota_roberto"],
                "Tipo": v["tipo"]
            } for k, v in jogadores.items()
        ])
        st.dataframe(df_players, use_container_width=True)
        
        st.markdown("### 🗑️ Remover Jogador")
        remover_nome = st.selectbox("Selecione o jogador a ser excluído:", list(jogadores.keys()))
        if st.button("Remover permanentemente"):
            del jogadores[remover_nome]
            salvar_jogadores(jogadores)
            st.success(f"{remover_nome} foi removido do banco de dados!")
            st.rerun()

    with tab_add:
        st.subheader("Cadastrar Jogador no Ciclo")
        with st.form("add_player_form"):
            new_nome = st.text_input("Nome do Jogador*")
            new_pos = st.selectbox("Posição Principal*", [
                "Goleiro", "Lateral Direito", "Lateral Esquerdo", 
                "Zagueiro Esquerdo", "Zagueiro Direito", 
                "Meio-Campo (Defensivo)", "Meio-Campo (Apoio)", "Meio-Campo (Criativo)",
                "Ponta Esquerda", "Ponta Direita", "Centroavante"
            ])
            new_clube = st.text_input("Clube Atual")
            new_idade = st.number_input("Idade em 2026", min_value=15, max_value=45, value=22)
            new_grupo = st.selectbox("Grupo Hierárquico*", ["Titulares", "Reservas", "Observação"])
            new_tipo = st.selectbox("Status de Evolução", ["Certeza Atual", "Promessa 2030", "Observação"])
            
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                new_nota_vini = st.slider("Nota do Vini", 0.0, 10.0, 7.5, step=0.5)
            with col_n2:
                new_nota_rob = st.slider("Nota do Roberto", 0.0, 10.0, 7.5, step=0.5)
                
            new_fortes = st.text_area("Pontos Fortes")
            new_fracos = st.text_area("Pontos Fracos / Desafios")
            new_hist = st.text_area("Notas do Histórico / Notas do Chat")
            
            submitted = st.form_submit_button("Salvar no Sistema")
            if submitted:
                if not new_nome:
                    st.error("O nome do jogador é obrigatório.")
                else:
                    jogadores[new_nome] = {
                        "nome": new_nome,
                        "posicao": new_pos,
                        "clube": new_clube,
                        "idade": int(new_idade),
                        "grupo": new_grupo,
                        "tipo": new_tipo,
                        "nota_vini": float(new_nota_vini),
                        "nota_roberto": float(new_nota_rob),
                        "pontos_fortes": new_fortes,
                        "pontos_fracos": new_fracos,
                        "historico": new_hist
                    }
                    salvar_jogadores(jogadores)
                    st.success(f"{new_nome} adicionado com sucesso!")
                    st.rerun()

# ----------------- TELA 3: PERFIS DETALHADOS -----------------
elif menu == "👤 Detalhes & Páginas de Jogadores":
    st.title("👤 Páginas Individuais dos Atletas")
    st.write("Selecione um jogador para abrir o dossiê detalhado com os comentários e notas da dupla.")

    selected_player_name = st.selectbox("Escolha o Jogador:", sorted(list(jogadores.keys())))
    player = jogadores[selected_player_name]
    
    st.markdown("---")
    
    col_p1, col_p2 = st.columns([1, 2])
    
    with col_p1:
        # Stylized player card/avatar box
        st.markdown(f"""
        <div style="background-color: #1e293b; padding: 25px; border-radius: 15px; text-align: center; border: 3px solid #eab308;">
            <h2 style="color: #ffffff; margin-bottom: 5px;">{player['nome']}</h2>
            <span style="background-color: #22c55e; color: black; font-weight: bold; padding: 4px 10px; border-radius: 20px; font-size: 10pt;">
                {player['tipo']}
            </span>
            <p style="margin-top: 15px; font-size: 11pt; color: #cbd5e1;">
                <b>Posição:</b> {player['posicao']}<br>
                <b>Clube:</b> {player['clube']}<br>
                <b>Idade em 2026:</b> {player['idade']} anos<br>
                <b>Idade na Copa 2030:</b> {player['idade'] + 4} anos
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.subheader("Calibração de Notas")
        st.metric("Nota Média do Vini", f"{player['nota_vini']:.1f} / 10")
        st.metric("Nota Média do Roberto", f"{player['nota_roberto']:.1f} / 10")

    with col_p2:
        st.markdown("### 📝 Dossiê de Desempenho")
        
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.markdown("**🟢 Pontos Fortes:**")
        st.write(player.get("pontos_fortes", "Nenhuma informação cadastrada."))
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="stat-box" style="border-left-color: #ef4444;">', unsafe_allow_html=True)
        st.markdown("**🔴 Desafios & Pontos Fracos:**")
        st.write(player.get("pontos_fracos", "Nenhuma informação cadastrada."))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="stat-box" style="border-left-color: #3b82f6;">', unsafe_allow_html=True)
        st.markdown("**🗣️ Notas dos Debates (Vini & Roberto):**")
        st.write(player.get("historico", "Nenhuma nota inserida nas conversas."))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # In-line note updater
        st.write("---")
        st.write("✍️ **Atualizar Rápido as Notas:**")
        up_vini = st.slider("Nova Nota Vini", 0.0, 10.0, float(player['nota_vini']), step=0.5, key="up_vini")
        up_rob = st.slider("Nova Nota Roberto", 0.0, 10.0, float(player['nota_roberto']), step=0.5, key="up_rob")
        if st.button("Salvar Calibração"):
            jogadores[selected_player_name]['nota_vini'] = up_vini
            jogadores[selected_player_name]['nota_roberto'] = up_rob
            salvar_jogadores(jogadores)
            st.success("Calibração salva!")
            st.rerun()

# ----------------- TELA 4: ESTATÍSTICAS & ANÁLISES -----------------
elif menu == "📊 Estatísticas & Análises":
    st.title("📊 Painel Analítico da Amizade")
    st.write("Aqui você consegue comparar as notas do Vini contra as do Roberto para analisar onde moram as maiores divergências e concordâncias.")

    df_stats = pd.DataFrame([
        {
            "Nome": k,
            "Posição": v["posicao"],
            "Vini": v["nota_vini"],
            "Roberto": v["nota_roberto"],
            "Diferença Absoluta": abs(v["nota_vini"] - v["nota_roberto"])
        } for k, v in jogadores.items()
    ])

    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.subheader("🤝 Maiores Concordâncias")
        st.write("Jogadores em que a opinião da dupla é quase idêntica:")
        concordancias = df_stats.sort_values(by="Diferença Absoluta", ascending=True).head(5)
        st.dataframe(concordancias[["Nome", "Posição", "Vini", "Roberto"]], use_container_width=True)

    with col_s2:
        st.subheader("🔥 Maiores Divergências")
        st.write("Jogadores que rendem as discussões de bar mais longas:")
        divergencias = df_stats.sort_values(by="Diferença Absoluta", ascending=False).head(5)
        st.dataframe(divergencias[["Nome", "Posição", "Vini", "Roberto", "Diferença Absoluta"]], use_container_width=True)

    st.write("---")
    st.subheader("🔍 Filtro por Categoria (Hierarquia)")
    cat_filtro = st.selectbox("Selecione a Categoria:", ["Titulares", "Reservas", "Observação"])
    
    filtrados = [j for j in jogadores.values() if j['grupo'] == cat_filtro]
    df_f = pd.DataFrame([
        {"Nome": j['nome'], "Posição": j['posicao'], "Clube": j['clube'], "Média": (j['nota_vini'] + j['nota_roberto'])/2}
        for j in filtrados
    ])
    st.dataframe(df_f.sort_values(by="Média", ascending=False), use_container_width=True)
