"""Testes da RC5.1 — UX, convocação única e persistência local."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from hexa_persistencia_local import (
    CHAVE_LIMPEZA_SOLICITADA,
    apagar_convocacoes_locais,
    restaurar_convocacoes,
    serializar_convocacoes,
)
from hexa_session import (
    chave_reserva_livre,
    chave_reserva_posicional,
    chave_titular,
    opcoes_reserva_livre,
    prioridade_posicoes_tatica,
    quantidade_vagas_livres,
    reconciliar_convocacao,
)
from hexa_taticas import TATICAS

BASE_DIR = Path(__file__).resolve().parents[1]


class TestRC51ConvocacaoPersistente(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.jogadores = json.loads(
            (BASE_DIR / "jogadores_hexa_2030.json").read_text(encoding="utf-8")
        )
        cls.tatica = next(iter(TATICAS))
        cls.layout = TATICAS[cls.tatica]

    def _primeiro_compativel(self, indice: int) -> str:
        configuracao = list(self.layout.values())[indice]
        permitidas = set(configuracao.posicoes)
        for nome, dados in self.jogadores.items():
            posicoes = dados.get("posicoes_multiplas") or [dados.get("posicao")]
            if any(posicao in permitidas for posicao in posicoes):
                return nome
        self.fail("A base não possui atleta compatível para o slot.")

    def test_reconciliacao_remove_duplicidade_em_slots_posteriores(self) -> None:
        nome = next(iter(self.jogadores))
        estado = {
            chave_reserva_livre(self.tatica, 0): nome,
            chave_reserva_livre(self.tatica, 1): nome,
        }
        relatorio = reconciliar_convocacao(
            estado,
            self.tatica,
            self.layout,
            self.jogadores,
        )
        self.assertEqual(
            estado[chave_reserva_livre(self.tatica, 0)],
            nome,
        )
        self.assertIsNone(
            estado[chave_reserva_livre(self.tatica, 1)]
        )
        self.assertEqual(relatorio["reservas"], [nome])

    def test_titular_tem_prioridade_sobre_reserva_repetida(self) -> None:
        nome = self._primeiro_compativel(0)
        estado = {
            chave_titular(self.tatica, 0): nome,
            chave_reserva_livre(self.tatica, 0): nome,
        }
        relatorio = reconciliar_convocacao(
            estado,
            self.tatica,
            self.layout,
            self.jogadores,
        )
        self.assertIn(nome, relatorio["titulares"].values())
        self.assertNotIn(nome, relatorio["reservas"])
        self.assertIsNone(
            estado[chave_reserva_livre(self.tatica, 0)]
        )

    def test_opcoes_nao_oferecem_atleta_salvo_em_outro_slot(self) -> None:
        prioridade = prioridade_posicoes_tatica(self.layout)
        nome = next(iter(self.jogadores))
        opcoes = opcoes_reserva_livre(
            self.jogadores,
            prioridade,
            {nome},
        )
        self.assertNotIn(nome, opcoes)

    def test_roundtrip_usa_id_estavel_e_preserva_tatica(self) -> None:
        titular = self._primeiro_compativel(0)
        reserva = next(
            nome for nome in self.jogadores if nome != titular
        )
        estado = {
            "tactical_selector": self.tatica,
            chave_titular(self.tatica, 0): titular,
            chave_reserva_livre(self.tatica, 0): reserva,
        }
        payload = serializar_convocacoes(
            estado,
            TATICAS,
            self.jogadores,
        )
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["tatica_ativa"], self.tatica)
        self.assertTrue(
            payload["convocacoes"][self.tatica]["titulares"][0].startswith(
                "ATH-"
            )
        )

        restaurado: dict[str, object] = {}
        incluidos, descartados = restaurar_convocacoes(
            restaurado,
            payload,
            TATICAS,
            self.jogadores,
        )
        self.assertEqual(descartados, 0)
        self.assertEqual(incluidos, 2)
        self.assertEqual(restaurado["tactical_selector"], self.tatica)
        self.assertEqual(
            restaurado[chave_titular(self.tatica, 0)],
            titular,
        )
        self.assertEqual(
            restaurado[chave_reserva_livre(self.tatica, 0)],
            reserva,
        )

    def test_restauracao_descarta_id_inexistente(self) -> None:
        payload = {
            "schema_version": 1,
            "tatica_ativa": self.tatica,
            "convocacoes": {
                self.tatica: {
                    "titulares": ["ATH-INEXISTENTE"],
                    "reservas_posicionais": [],
                    "reservas_livres": [],
                }
            },
        }
        estado: dict[str, object] = {}
        incluidos, descartados = restaurar_convocacoes(
            estado,
            payload,
            TATICAS,
            self.jogadores,
        )
        self.assertEqual(incluidos, 0)
        self.assertEqual(descartados, 1)

    def test_formacoes_sao_persistidas_separadamente(self) -> None:
        nomes_taticas = list(TATICAS)[:2]
        self.assertEqual(len(nomes_taticas), 2)
        estado: dict[str, object] = {}
        escolhidos: list[str] = []

        for tatica in nomes_taticas:
            layout = TATICAS[tatica]
            configuracao = next(iter(layout.values()))
            permitidas = set(configuracao.posicoes)
            nome = next(
                nome
                for nome, dados in self.jogadores.items()
                if nome not in escolhidos
                and any(
                    posicao in permitidas
                    for posicao in (
                        dados.get("posicoes_multiplas")
                        or [dados.get("posicao")]
                    )
                )
            )
            escolhidos.append(nome)
            estado[chave_titular(tatica, 0)] = nome

        payload = serializar_convocacoes(
            estado,
            TATICAS,
            self.jogadores,
        )
        restaurado: dict[str, object] = {}
        restaurar_convocacoes(
            restaurado,
            payload,
            TATICAS,
            self.jogadores,
        )
        for tatica, nome in zip(nomes_taticas, escolhidos):
            self.assertEqual(
                restaurado[chave_titular(tatica, 0)],
                nome,
            )

    def test_apagar_local_remove_todas_as_formacoes(self) -> None:
        estado: dict[str, object] = {}
        for tatica, layout in list(TATICAS.items())[:2]:
            estado[chave_titular(tatica, 0)] = self._primeiro_compativel(0)
        apagar_convocacoes_locais(estado, TATICAS)
        for tatica, layout in TATICAS.items():
            self.assertNotIn(chave_titular(tatica, 0), estado)
        self.assertTrue(estado[CHAVE_LIMPEZA_SOLICITADA])

    def test_quatro_vagas_livres_continuam_preservadas(self) -> None:
        self.assertEqual(
            quantidade_vagas_livres(len(self.layout)),
            4,
        )


class TestRC51ContratoVisual(unittest.TestCase):
    def test_placeholder_neutro_solicitado(self) -> None:
        pages = (BASE_DIR / "hexa_pages.py").read_text(encoding="utf-8")
        self.assertIn("Ex.: Real Madrid ou Vini Jr", pages)
        self.assertNotIn("Ex.: Palmeiras", pages)

    def test_rotulo_explica_pico_de_mercado(self) -> None:
        for arquivo in (
            "hexa_pages.py",
            "hexa_selectors.py",
            "hexa_components.py",
        ):
            texto = (BASE_DIR / arquivo).read_text(encoding="utf-8")
            self.assertIn("pico de mercado", texto.lower())

    def test_resumo_individual_nao_usa_metric_para_textos_longos(self) -> None:
        pages = (BASE_DIR / "hexa_pages.py").read_text(encoding="utf-8")
        self.assertIn("evaluation-meta-grid", pages)
        self.assertNotIn('c1.metric("Situação"', pages)
        self.assertIn("Data de referência", pages)

    def test_acessibilidade_e_renderizada_apos_feedback(self) -> None:
        entrypoint = (
            BASE_DIR / "caminho_hexa_2030.py"
        ).read_text(encoding="utf-8")
        self.assertLess(
            entrypoint.rfind("render_feedback_sidebar()"),
            entrypoint.rfind("render_preferencias_acessibilidade()"),
        )

    def test_componente_usa_local_storage_sem_dependencia_externa(self) -> None:
        modulo = (
            BASE_DIR / "hexa_persistencia_local.py"
        ).read_text(encoding="utf-8")
        self.assertIn("window.localStorage", modulo)
        self.assertIn("st.components.v2.component", modulo)
        self.assertIn("id_atleta", modulo)


if __name__ == "__main__":
    unittest.main()
