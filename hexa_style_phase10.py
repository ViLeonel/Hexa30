"""Ajustes visuais da Agenda Inteligente."""

from __future__ import annotations

__all__ = ["PHASE10_CSS"]

PHASE10_CSS = """
<style>
    .agenda-inteligente-meta {
        color: var(--slate-300);
        font-size: .875rem;
        line-height: 1.5;
    }

    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] {
            gap: .75rem;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        .agenda-inteligente-meta {
            scroll-behavior: auto;
        }
    }
</style>
"""
