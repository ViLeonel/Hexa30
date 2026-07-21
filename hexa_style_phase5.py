"""Aprimoramentos visuais e responsivos da Fase 5.

Este módulo contém somente overrides estáveis do design system. Ele evita
seletores internos frágeis sempre que há classes próprias do projeto.
"""

from __future__ import annotations

__all__ = ["PHASE5_CSS"]


PHASE5_CSS = """
<style>
    :root {
        --hexa-bg: #0A1222;
        --hexa-surface: #121D31;
        --hexa-surface-raised: #18253B;
        --hexa-surface-soft: #20304A;
        --hexa-text: #F5F7F2;
        --hexa-text-muted: #C2CBDA;
        --hexa-text-subtle: #9EABC0;
        --hexa-gold: #F2C94C;
        --hexa-gold-strong: #FFD75A;
        --hexa-green: #2CB67D;
        --hexa-green-field: #176B45;
        --hexa-blue: #6EA8FE;
        --hexa-danger: #FF8A8A;
        --hexa-border: rgba(194, 203, 218, .24);
        --hexa-border-strong: rgba(194, 203, 218, .42);
        --hexa-focus: #9CC2FF;
        --hexa-shadow: 0 14px 34px rgba(0, 0, 0, .28);
        --hexa-font:
            Inter, "Source Sans 3", -apple-system, BlinkMacSystemFont,
            "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 82% -12%, rgba(46, 107, 209, .14), transparent 34rem),
            radial-gradient(circle at 12% 6%, rgba(242, 201, 76, .07), transparent 27rem),
            var(--hexa-bg);
        color: var(--hexa-text);
        font-family: var(--hexa-font);
        text-rendering: optimizeLegibility;
        -webkit-font-smoothing: antialiased;
    }

    .stApp p,
    .stApp li,
    .stApp label,
    .stApp input,
    .stApp textarea,
    .stApp button {
        font-family: var(--hexa-font);
    }

    .block-container {
        width: min(100%, 1500px);
        padding-inline: clamp(1rem, 3vw, 2.5rem);
    }

    .project-hero {
        justify-content: flex-start;
        margin-inline: 0;
        padding: 1rem clamp(1rem, 2vw, 1.5rem);
        border: 1px solid var(--hexa-border);
        border-radius: 22px;
        background:
            linear-gradient(135deg, rgba(24, 37, 59, .94), rgba(10, 18, 34, .9));
        box-shadow: var(--hexa-shadow);
    }

    .project-hero-title,
    .app-title,
    .section-title,
    .convocation-builder-title {
        color: var(--hexa-text);
        letter-spacing: -.025em;
    }

    .project-hero-subtitle,
    .project-subtitle {
        color: var(--hexa-text-muted);
        max-width: 76ch;
    }

    .section-subtitle,
    .kpi-context,
    .evaluation-meta-label {
        color: var(--hexa-text-subtle);
    }

    .section-eyebrow,
    .player-pos-tag,
    .bench-number {
        color: var(--hexa-gold);
    }

    .app-title::after {
        width: 4.25rem;
        background: linear-gradient(90deg, var(--hexa-gold), var(--hexa-green));
    }

    .kpi-card,
    .profile-card,
    .market-card,
    .stat-box,
    .bench-box,
    .rating-box,
    .executive-table-card,
    .evaluation-context,
    .evaluation-meta-card {
        border-color: var(--hexa-border);
        background: linear-gradient(180deg, var(--hexa-surface-raised), var(--hexa-surface));
        box-shadow: 0 9px 24px rgba(0, 0, 0, .2);
    }

    .kpi-card {
        min-height: 8.25rem;
        padding: 1.05rem 1.1rem;
    }

    .kpi-value,
    .evaluation-meta-value {
        color: var(--hexa-text);
        font-variant-numeric: tabular-nums;
    }

    .kpi-card:hover,
    .profile-card:hover,
    .bench-card:hover {
        border-color: var(--hexa-border-strong);
        transform: translateY(-1px);
    }

    .pitch-container {
        height: clamp(540px, 64vw, 700px);
        border: 2px solid rgba(242, 201, 76, .68);
        border-radius: 22px;
        background:
            linear-gradient(rgba(255, 255, 255, .022) 50%, transparent 50%) 0 0 / 100% 86px,
            linear-gradient(180deg, #176B45, #115A3A);
        box-shadow: var(--hexa-shadow);
    }

    .player-card-pitch {
        border-width: 1px;
        border-color: rgba(242, 201, 76, .8);
        background: rgba(10, 18, 34, .94);
        box-shadow: 0 7px 16px rgba(0, 0, 0, .34);
    }

    .player-rating-tag {
        background: var(--hexa-gold);
        color: #121212;
    }

    .executive-table-scroll {
        scrollbar-color: var(--hexa-text-subtle) var(--hexa-surface);
        scrollbar-width: thin;
    }

    .executive-table thead th {
        color: #C7DBFF;
        background: #101B2E;
    }

    .executive-table tbody tr:nth-child(even) {
        background: rgba(255, 255, 255, .025);
    }

    .executive-table tbody tr:hover {
        background: rgba(110, 168, 254, .09);
    }

    .executive-table td,
    .executive-table th {
        border-color: var(--hexa-border);
        font-variant-numeric: tabular-nums;
    }

    .stButton > button,
    .stDownloadButton > button {
        min-height: 2.75rem;
        border-color: var(--hexa-border-strong);
        font-weight: 650;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: var(--hexa-gold);
    }

    :where(
        button,
        a,
        input,
        textarea,
        select,
        [tabindex]:not([tabindex="-1"])
    ):focus-visible {
        outline: 3px solid var(--hexa-focus) !important;
        outline-offset: 3px !important;
    }

    @media (max-width: 900px) {
        .project-hero {
            align-items: flex-start;
        }

        .bench-grid {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }

        .player-node {
            width: 118px;
        }
    }

    @media (max-width: 700px) {
        .block-container {
            padding-inline: .85rem;
            padding-top: .5rem;
        }

        .project-hero {
            flex-direction: column;
            gap: .65rem;
            padding: 1rem;
            border-radius: 16px;
        }

        .project-trophy {
            width: 58px;
        }

        .project-hero-title {
            font-size: clamp(1.9rem, 10vw, 2.5rem);
        }

        .project-hero-subtitle,
        .project-subtitle {
            font-size: .98rem;
            line-height: 1.58;
        }

        .kpi-grid {
            grid-template-columns: 1fr;
        }

        .kpi-card {
            min-height: auto;
        }

        .pitch-container {
            min-width: 620px;
            height: 560px;
        }

        .pitch-container-wrapper,
        .pitch-scroll,
        .field-scroll {
            overflow-x: auto;
            overscroll-behavior-inline: contain;
            scrollbar-width: thin;
        }

        .bench-grid {
            grid-template-columns: 1fr 1fr;
        }

        .stButton > button,
        .stDownloadButton > button {
            min-height: 3rem;
        }
    }

    @media (max-width: 430px) {
        .bench-grid {
            grid-template-columns: 1fr;
        }

        .section-header {
            margin-top: 1.5rem;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            scroll-behavior: auto !important;
            animation-duration: .01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: .01ms !important;
        }

        .kpi-card:hover,
        .profile-card:hover,
        .bench-card:hover {
            transform: none;
        }
    }

    @media (forced-colors: active) {
        .project-hero,
        .kpi-card,
        .profile-card,
        .market-card,
        .bench-box,
        .executive-table-card,
        .evaluation-context,
        .evaluation-meta-card,
        .pitch-container,
        .player-card-pitch {
            border: 2px solid CanvasText;
            box-shadow: none;
        }
    }
</style>
"""
