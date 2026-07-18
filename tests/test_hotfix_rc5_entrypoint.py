"""Regressão do hotfix RC5: entrypoint e roteador temporal devem permanecer sincronizados."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
ENTRYPOINT = BASE_DIR / "caminho_hexa_2030.py"


class TestHotfixRC5Entrypoint(unittest.TestCase):
    def test_entrypoint_carrega_base_e_periodo_trimestrais(self) -> None:
        texto = ENTRYPOINT.read_text(encoding="utf-8")
        self.assertIn("carregar_avaliacoes_seguras(jogadores)", texto)
        self.assertIn("render_seletor_periodo(base_avaliacoes)", texto)

    def test_render_tela_recebe_contrato_temporal_completo(self) -> None:
        arvore = ast.parse(
            ENTRYPOINT.read_text(encoding="utf-8"),
            filename=str(ENTRYPOINT),
        )
        chamadas = [
            no
            for no in ast.walk(arvore)
            if isinstance(no, ast.Call)
            and isinstance(no.func, ast.Name)
            and no.func.id == "render_tela"
        ]
        self.assertEqual(len(chamadas), 1)

        chamada = chamadas[0]
        self.assertEqual(
            {argumento.arg for argumento in chamada.keywords},
            {"menu", "jogadores", "base_avaliacoes", "periodo"},
        )
        self.assertEqual(chamada.args, [])

    def test_nao_existe_chamada_legada_de_dois_argumentos(self) -> None:
        texto_compactado = "".join(
            ENTRYPOINT.read_text(encoding="utf-8").split()
        )
        self.assertNotIn("render_tela(menu,jogadores)", texto_compactado)


if __name__ == "__main__":
    unittest.main()
