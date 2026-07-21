"""Regressões visuais e de acessibilidade da Fase 5."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from hexa_style_phase5 import PHASE5_CSS

ROOT = Path(__file__).resolve().parents[1]


def _rgb(hexadecimal: str) -> tuple[int, int, int]:
    texto = hexadecimal.lstrip("#")
    return tuple(int(texto[indice : indice + 2], 16) for indice in (0, 2, 4))


def _luminancia(hexadecimal: str) -> float:
    canais = []
    for canal in _rgb(hexadecimal):
        valor = canal / 255
        canais.append(
            valor / 12.92 if valor <= 0.04045 else ((valor + 0.055) / 1.055) ** 2.4
        )
    return 0.2126 * canais[0] + 0.7152 * canais[1] + 0.0722 * canais[2]


def _contraste(frente: str, fundo: str) -> float:
    clara, escura = sorted((_luminancia(frente), _luminancia(fundo)), reverse=True)
    return (clara + 0.05) / (escura + 0.05)


class Phase5DesignTests(unittest.TestCase):
    def test_texto_principal_atende_wcag_aa(self) -> None:
        self.assertGreaterEqual(_contraste("#F5F7F2", "#0A1222"), 4.5)

    def test_texto_secundario_atende_wcag_aa(self) -> None:
        self.assertGreaterEqual(_contraste("#C2CBDA", "#121D31"), 4.5)

    def test_destaque_tem_contraste_quando_usado_como_texto(self) -> None:
        self.assertGreaterEqual(_contraste("#F2C94C", "#0A1222"), 4.5)

    def test_reduced_motion_e_forced_colors_estao_presentes(self) -> None:
        self.assertIn("@media (prefers-reduced-motion: reduce)", PHASE5_CSS)
        self.assertIn("@media (forced-colors: active)", PHASE5_CSS)

    def test_foco_visivel_e_alvos_de_toque(self) -> None:
        self.assertIn(":focus-visible", PHASE5_CSS)
        self.assertRegex(PHASE5_CSS, r"min-height:\s*3rem")

    def test_campo_possui_wrapper_responsivo(self) -> None:
        componentes = (ROOT / "hexa_components.py").read_text(encoding="utf-8")
        self.assertIn('class="pitch-scroll"', componentes)
        self.assertIn("deslize horizontalmente", componentes)

    def test_configuracao_e_modulo_usam_mesma_paleta(self) -> None:
        config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
        for cor in ("#F2C94C", "#0A1222", "#F5F7F2"):
            self.assertIn(cor, config)
            self.assertIn(cor, PHASE5_CSS)

    def test_css_nao_importa_fontes_remotas(self) -> None:
        self.assertIsNone(
            re.search(r"@import\s+url|fonts\.googleapis", PHASE5_CSS, re.I)
        )


if __name__ == "__main__":
    unittest.main()
