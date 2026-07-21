"""Compatibilidade entre navegadores, responsividade e preferências do usuário."""

from __future__ import annotations

__all__ = ["PHASE6_CSS"]


PHASE6_CSS = """
<style>
    html {
        -webkit-text-size-adjust: 100%;
        text-size-adjust: 100%;
        scroll-behavior: smooth;
        scrollbar-gutter: stable;
    }

    *, *::before, *::after {
        box-sizing: border-box;
    }

    body, button, input, select, textarea {
        font-family: Inter, "Source Sans 3", -apple-system, BlinkMacSystemFont,
            "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    img, svg, video, canvas {
        max-width: 100%;
        height: auto;
    }

    .stApp,
    .block-container,
    [data-testid="stVerticalBlock"],
    [data-testid="column"] {
        min-width: 0;
    }

    p, li, td, th, label, .stMarkdown {
        overflow-wrap: anywhere;
    }

    button,
    [role="button"],
    input,
    select,
    textarea,
    a {
        touch-action: manipulation;
    }

    :where(a, button, input, select, textarea, [tabindex]):focus-visible {
        outline: 3px solid var(--color-focus, #60A5FA) !important;
        outline-offset: 3px;
        border-radius: 6px;
    }

    .pitch-container,
    .executive-table-scroll,
    [data-testid="stDataFrame"] {
        overscroll-behavior-inline: contain;
        -webkit-overflow-scrolling: touch;
    }

    @supports (min-height: 100dvh) {
        .stApp {
            min-height: 100dvh;
        }
    }

    @media (max-width: 1024px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .project-hero {
            align-items: flex-start;
        }

        .bench-grid {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: .75rem;
            padding-right: .75rem;
            padding-bottom: 2rem;
        }

        .project-hero {
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding-inline: .25rem;
        }

        .project-hero-copy,
        .page-header,
        .section-header {
            width: 100%;
        }

        .project-hero-title,
        .project-hero-subtitle {
            text-align: center;
        }

        .project-trophy {
            width: 64px;
        }

        .kpi-grid,
        .summary-grid,
        .profile-grid,
        .market-grid,
        .bench-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .pitch-container {
            min-width: 680px;
        }

        .executive-table-scroll {
            max-width: calc(100vw - 1.5rem);
        }

        [data-testid="stHorizontalBlock"] {
            gap: .75rem;
        }
    }

    @media (max-width: 480px) {
        .project-hero-title,
        .app-title {
            font-size: clamp(1.75rem, 9vw, 2.15rem);
        }

        .project-hero-subtitle,
        .project-subtitle {
            font-size: .98rem;
            line-height: 1.55;
        }

        .kpi-grid,
        .summary-grid,
        .profile-grid,
        .market-grid,
        .bench-grid {
            grid-template-columns: 1fr;
        }

        .kpi-card,
        .summary-card,
        .profile-card,
        .market-card,
        .bench-card {
            padding: .9rem;
        }

        .stButton > button,
        .stDownloadButton > button {
            min-height: 44px;
        }
    }

    @media (hover: none) and (pointer: coarse) {
        .ag-row-hover,
        .bench-card:hover,
        .kpi-card:hover {
            transform: none !important;
        }

        button,
        [role="button"],
        input,
        select {
            min-height: 44px;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        html {
            scroll-behavior: auto;
        }

        *, *::before, *::after {
            animation-duration: .01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: .01ms !important;
        }
    }

    @media (forced-colors: active) {
        :where(a, button, input, select, textarea, [tabindex]):focus-visible {
            outline: 3px solid Highlight !important;
        }

        .player-card-pitch,
        .kpi-card,
        .summary-card,
        .profile-card,
        .market-card,
        .bench-card {
            border: 1px solid CanvasText !important;
        }
    }

    @media print {
        [data-testid="stSidebar"],
        [data-testid="stToolbar"],
        .stButton,
        .stDownloadButton {
            display: none !important;
        }

        .stApp {
            background: #FFFFFF !important;
            color: #000000 !important;
        }
    }
</style>
"""
