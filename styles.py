"""Configuração visual compartilhada do aplicativo."""

from __future__ import annotations

import streamlit as st

PAGE_CONFIG = {
    "page_title": "O Caminho para o Hexa 2030",
    "page_icon": "🏆",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

CSS = """
<style>
    :root {
        --navy-950: #020617;
        --navy-900: #0F172A;
        --navy-800: #1E293B;
        --slate-300: #CBD5E1;
        --slate-400: #94A3B8;
        --white: #F8FAFC;
        --gold: #EAB308;
        --green: #22C55E;
        --orange: #F97316;
        --red: #EF4444;
        --blue: #3B82F6;
    }

    .stApp {
        background-color: var(--navy-900);
        color: var(--white);
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .app-title {
        text-align: center;
        font-size: clamp(2rem, 5vw, 3.2rem);
        font-weight: 800;
        line-height: 1.1;
        background: linear-gradient(135deg, var(--gold) 0%, var(--white) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 .35rem;
    }

    .project-subtitle {
        color: var(--slate-400);
        font-size: clamp(.95rem, 2vw, 1.15rem);
        text-align: center;
        margin: 0 auto 1.75rem;
        max-width: 850px;
        line-height: 1.6;
    }

    .pitch-container {
        background-color: #14532D;
        background-image: linear-gradient(to bottom, #14532D 0%, #166534 100%);
        border: 4px solid var(--gold);
        border-radius: 20px;
        position: relative;
        width: 100%;
        height: 680px;
        overflow: hidden;
        box-shadow: 0 15px 35px rgba(0, 0, 0, .55);
        margin-bottom: 25px;
    }

    .pitch-line-center {
        position: absolute;
        top: 50%;
        left: 0;
        width: 100%;
        height: 2px;
        background-color: rgba(248, 250, 252, .35);
    }

    .pitch-circle {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 150px;
        height: 150px;
        border: 2px solid rgba(248, 250, 252, .35);
        border-radius: 50%;
    }

    .pitch-penalty-top,
    .pitch-penalty-bottom {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        width: 280px;
        height: 100px;
        border-left: 2px solid rgba(248, 250, 252, .35);
        border-right: 2px solid rgba(248, 250, 252, .35);
    }

    .pitch-penalty-top {
        top: 0;
        border-bottom: 2px solid rgba(248, 250, 252, .35);
    }

    .pitch-penalty-bottom {
        bottom: 0;
        border-top: 2px solid rgba(248, 250, 252, .35);
    }

    .player-node {
        position: absolute;
        transform: translate(-50%, -50%);
        width: 135px;
        text-align: center;
        z-index: 10;
    }

    .player-card-pitch {
        background: rgba(2, 6, 23, .95);
        border: 2px solid var(--gold);
        border-radius: 9px;
        padding: 6px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, .5);
    }

    .player-pos-tag {
        color: var(--gold);
        font-size: .66rem;
        font-weight: 800;
        text-transform: uppercase;
    }

    .player-name-tag {
        color: var(--white);
        font-size: .78rem;
        font-weight: 700;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .player-rating-tag {
        display: inline-block;
        background-color: var(--gold);
        color: var(--navy-950);
        font-size: .64rem;
        font-weight: 800;
        border-radius: 4px;
        padding: 2px 5px;
        margin-top: 3px;
    }

    .legend-box,
    .summary-box,
    .profile-card,
    .market-card,
    .stat-box {
        background-color: var(--navy-950);
        border-radius: 14px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, .3);
    }

    .legend-box {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 16px;
        padding: 12px;
        margin: -10px 0 25px;
        border: 1px solid var(--navy-800);
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 7px;
        color: var(--white);
        font-size: .82rem;
    }

    .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        flex: 0 0 auto;
    }

    .summary-box {
        padding: 18px;
        border-top: 4px solid var(--gold);
        margin-bottom: 22px;
    }

    .summary-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(105px, 1fr));
        gap: 12px;
        text-align: center;
    }

    .summary-label {
        color: var(--slate-400);
        font-size: .66rem;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: .03em;
    }

    .summary-value {
        color: var(--white);
        font-size: 1.05rem;
        font-weight: 800;
        margin-top: 3px;
    }

    .profile-card {
        padding: 24px;
        border: 3px solid var(--gold);
        text-align: center;
    }

    .profile-card h2 {
        color: var(--white);
        margin: 0 0 5px;
        font-size: clamp(1.6rem, 4vw, 2.2rem);
    }

    .status-pill {
        display: inline-block;
        background-color: var(--navy-800);
        color: var(--gold);
        border: 1px solid var(--gold);
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 999px;
        font-size: .78rem;
    }

    .profile-details {
        margin-top: 18px;
        color: var(--slate-300);
        text-align: left;
        line-height: 1.85;
        font-size: .9rem;
    }

    .market-card {
        padding: 18px;
        border-left: 5px solid var(--gold);
        margin-bottom: 22px;
    }

    .market-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(120px, 1fr));
        gap: 14px;
        margin-bottom: 14px;
    }

    .market-label {
        color: var(--slate-400);
        font-size: .7rem;
        text-transform: uppercase;
        font-weight: 800;
    }

    .market-value {
        color: var(--white);
        font-size: 1.15rem;
        font-weight: 800;
        margin-top: 4px;
    }

    .market-value.gold { color: var(--gold); }
    .market-value.green { color: var(--green); }

    .progress-track {
        width: 100%;
        height: 12px;
        border-radius: 999px;
        background: var(--navy-800);
        overflow: hidden;
        margin: 8px 0 5px;
    }

    .progress-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, var(--orange), var(--gold), var(--green));
    }

    .stat-box {
        padding: 18px;
        border-left: 6px solid var(--gold);
        margin-bottom: 14px;
        color: var(--slate-300);
        line-height: 1.6;
    }

    .stat-box strong { color: var(--white); }

    section[data-testid="stSidebar"] {
        background-color: var(--navy-950) !important;
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: var(--white) !important;
    }

    header[data-testid="stHeader"],
    #MainMenu,
    footer,
    .stDeployButton {
        display: none !important;
    }

    @media (max-width: 900px) {
        .pitch-container { height: 620px; }
        .player-node { width: 112px; }
        .player-name-tag { font-size: .68rem; }
        .player-rating-tag { font-size: .57rem; }
        .summary-grid { grid-template-columns: repeat(2, minmax(120px, 1fr)); }
        .market-grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 600px) {
        .block-container { padding-left: .75rem; padding-right: .75rem; }
        .pitch-container { height: 560px; border-width: 3px; border-radius: 14px; }
        .pitch-circle { width: 105px; height: 105px; }
        .pitch-penalty-top, .pitch-penalty-bottom { width: 180px; height: 75px; }
        .player-node { width: 92px; }
        .player-card-pitch { padding: 4px; }
        .player-pos-tag { font-size: .52rem; }
        .player-name-tag { font-size: .58rem; }
        .player-rating-tag { font-size: .5rem; padding: 1px 3px; }
        .legend-box { justify-content: flex-start; gap: 10px; }
        .legend-item { width: 100%; font-size: .75rem; }
        .summary-grid { grid-template-columns: 1fr 1fr; }
    }
</style>
"""


def aplicar_estilos() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
