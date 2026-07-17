"""Vocabulário oficial, formações e regras de compatibilidade tática."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

POSICOES_OFICIAIS: tuple[str, ...] = (
    "Goleiro",
    "Lateral-direito",
    "Lateral-esquerdo",
    "Zagueiro",
    "Volante",
    "Mezzala esquerdo",
    "Mezzala direito",
    "Meia-esquerda",
    "Meia-direita",
    "Meia-armador",
    "Ponta-esquerda",
    "Ponta-direita",
    "Segundo atacante",
    "Centroavante",
)

ABREVIACOES: dict[str, str] = {
    "Goleiro": "GOL",
    "Lateral-direito": "LD",
    "Lateral-esquerdo": "LE",
    "Zagueiro": "ZAG",
    "Volante": "VOL",
    "Mezzala esquerdo": "MCE",
    "Mezzala direito": "MCD",
    "Meia-esquerda": "ME",
    "Meia-direita": "MD",
    "Meia-armador": "MEI",
    "Ponta-esquerda": "PE",
    "Ponta-direita": "PD",
    "Segundo atacante": "SA",
    "Centroavante": "CA",
}

# Migração de grafias antigas e equivalências de fontes externas.
# Esses aliases servem somente para normalização; a lista oficial acima prevalece.
ALIASES_POSICAO: dict[str, str] = {
    "Guarda-redes": "Goleiro",
    "Guarda-Redes": "Goleiro",
    "Lateral Direito": "Lateral-direito",
    "Lateral Esquerdo": "Lateral-esquerdo",
    "Zagueiro Direito": "Zagueiro",
    "Zagueiro Esquerdo": "Zagueiro",
    "Defesa central": "Zagueiro",
    "Defesa Central": "Zagueiro",
    "Médio Defensivo": "Volante",
    "Meio-Campo (Defensivo)": "Volante",
    "Médio Centro": "Mezzala direito",
    "Meio-Campo (Apoio)": "Mezzala esquerdo",
    "Meio-Campo (Criativo)": "Meia-armador",
    "Médio Ofensivo": "Meia-armador",
    "Médio Direito": "Meia-direita",
    "Médio Esquerdo": "Meia-esquerda",
    "Meia Direita": "Meia-direita",
    "Meia Esquerda": "Meia-esquerda",
    "Ponta Direita": "Ponta-direita",
    "Ponta Esquerda": "Ponta-esquerda",
    "Ponta-direito": "Ponta-direita",
    "Ponta-esquerdo": "Ponta-esquerda",
    "Extremo Direito": "Ponta-direita",
    "Extremo Esquerdo": "Ponta-esquerda",
    "Segundo Avançado": "Segundo atacante",
    "Ponta de Lança": "Centroavante",
}

LIMITE_TITULARES = 11
LIMITE_RESERVAS = 15
LIMITE_CONVOCADOS = LIMITE_TITULARES + LIMITE_RESERVAS


@dataclass(frozen=True, slots=True)
class SlotTatico:
    """Configuração visual e posicional de um lugar no campo."""

    posicoes: tuple[str, ...]
    left: str
    bottom: str
    tag: str


# Não existem atletas padrão. Cada formação começa vazia e é preenchida pelo usuário.
TATICAS: dict[str, dict[str, SlotTatico]] = {
    "4-3-3 Diamante": {
        "Goleiro (GOL)": SlotTatico(("Goleiro",), "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": SlotTatico(("Lateral-esquerdo",), "15%", "28%", "LE"),
        "Zagueiro Esquerdo (ZAG)": SlotTatico(("Zagueiro",), "37%", "22%", "ZAG"),
        "Zagueiro Direito (ZAG)": SlotTatico(("Zagueiro",), "63%", "22%", "ZAG"),
        "Lateral-direito (LD)": SlotTatico(("Lateral-direito",), "85%", "28%", "LD"),
        "Mezzala Esquerdo (MCE)": SlotTatico(("Mezzala esquerdo", "Meia-esquerda", "Volante"), "30%", "52%", "MCE"),
        "Volante (VOL)": SlotTatico(("Volante",), "50%", "40%", "VOL"),
        "Mezzala Direito (MCD)": SlotTatico(("Mezzala direito", "Meia-direita", "Volante"), "70%", "52%", "MCD"),
        "Ponta-esquerda (PE)": SlotTatico(("Ponta-esquerda", "Segundo atacante"), "20%", "72%", "PE"),
        "Centroavante (CA)": SlotTatico(("Centroavante",), "50%", "82%", "CA"),
        "Ponta-direita (PD)": SlotTatico(("Ponta-direita", "Meia-armador"), "80%", "72%", "PD"),
    },
    "4-3-3 Clássico": {
        "Goleiro (GOL)": SlotTatico(("Goleiro",), "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": SlotTatico(("Lateral-esquerdo",), "15%", "28%", "LE"),
        "Zagueiro Esquerdo (ZAG)": SlotTatico(("Zagueiro",), "37%", "22%", "ZAG"),
        "Zagueiro Direito (ZAG)": SlotTatico(("Zagueiro",), "63%", "22%", "ZAG"),
        "Lateral-direito (LD)": SlotTatico(("Lateral-direito",), "85%", "28%", "LD"),
        "Volante (VOL)": SlotTatico(("Volante",), "38%", "45%", "VOL"),
        "Volante Apoio (VOL)": SlotTatico(("Volante", "Mezzala esquerdo", "Mezzala direito"), "62%", "45%", "VOL"),
        "Meia-Armador (MEI)": SlotTatico(("Meia-armador",), "50%", "60%", "MEI"),
        "Ponta-esquerda (PE)": SlotTatico(("Ponta-esquerda",), "20%", "72%", "PE"),
        "Centroavante (CA)": SlotTatico(("Centroavante",), "50%", "82%", "CA"),
        "Ponta-direita (PD)": SlotTatico(("Ponta-direita",), "80%", "72%", "PD"),
    },
    "4-4-2 Diamante": {
        "Goleiro (GOL)": SlotTatico(("Goleiro",), "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": SlotTatico(("Lateral-esquerdo",), "15%", "28%", "LE"),
        "Zagueiro Esquerdo (ZAG)": SlotTatico(("Zagueiro",), "37%", "22%", "ZAG"),
        "Zagueiro Direito (ZAG)": SlotTatico(("Zagueiro",), "63%", "22%", "ZAG"),
        "Lateral-direito (LD)": SlotTatico(("Lateral-direito",), "85%", "28%", "LD"),
        "Volante (VOL)": SlotTatico(("Volante",), "50%", "40%", "VOL"),
        "Mezzala Esquerdo (MCE)": SlotTatico(("Mezzala esquerdo",), "30%", "52%", "MCE"),
        "Mezzala Direito (MCD)": SlotTatico(("Mezzala direito", "Mezzala esquerdo", "Meia-armador"), "70%", "52%", "MCD"),
        "Meia-Armador (MEI)": SlotTatico(("Meia-armador",), "50%", "65%", "MEI"),
        "Segundo Atacante (SA)": SlotTatico(("Segundo atacante", "Ponta-esquerda", "Ponta-direita", "Centroavante"), "38%", "78%", "SA"),
        "Centroavante (CA)": SlotTatico(("Centroavante",), "62%", "78%", "CA"),
    },
    "4-4-2 Clássico": {
        "Goleiro (GOL)": SlotTatico(("Goleiro",), "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": SlotTatico(("Lateral-esquerdo",), "15%", "28%", "LE"),
        "Zagueiro Esquerdo (ZAG)": SlotTatico(("Zagueiro",), "37%", "22%", "ZAG"),
        "Zagueiro Direito (ZAG)": SlotTatico(("Zagueiro",), "63%", "22%", "ZAG"),
        "Lateral-direito (LD)": SlotTatico(("Lateral-direito",), "85%", "28%", "LD"),
        "Meia-esquerda (ME)": SlotTatico(("Meia-esquerda", "Mezzala esquerdo", "Ponta-esquerda"), "20%", "55%", "ME"),
        "Volante Esquerdo (VOL)": SlotTatico(("Volante",), "40%", "45%", "VOL"),
        "Volante Direito (VOL)": SlotTatico(("Volante",), "60%", "45%", "VOL"),
        "Meia-direita (MD)": SlotTatico(("Meia-direita", "Mezzala direito", "Ponta-direita"), "80%", "55%", "MD"),
        "Segundo Atacante (SA)": SlotTatico(("Segundo atacante", "Meia-armador", "Ponta-esquerda"), "38%", "78%", "SA"),
        "Centroavante (CA)": SlotTatico(("Centroavante", "Segundo atacante"), "62%", "78%", "CA"),
    },
    "4-2-3-1": {
        "Goleiro (GOL)": SlotTatico(("Goleiro",), "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": SlotTatico(("Lateral-esquerdo",), "15%", "28%", "LE"),
        "Zagueiro Esquerdo (ZAG)": SlotTatico(("Zagueiro",), "37%", "22%", "ZAG"),
        "Zagueiro Direito (ZAG)": SlotTatico(("Zagueiro",), "63%", "22%", "ZAG"),
        "Lateral-direito (LD)": SlotTatico(("Lateral-direito",), "85%", "28%", "LD"),
        "Volante Esquerdo (VOL)": SlotTatico(("Volante", "Mezzala esquerdo"), "38%", "42%", "VOL"),
        "Volante Direito (VOL)": SlotTatico(("Volante", "Mezzala direito"), "62%", "42%", "VOL"),
        "Ponta-esquerda (PE)": SlotTatico(("Ponta-esquerda", "Meia-esquerda"), "20%", "65%", "PE"),
        "Meia-Armador (MEI)": SlotTatico(("Meia-armador", "Segundo atacante"), "50%", "62%", "MEI"),
        "Ponta-direita (PD)": SlotTatico(("Ponta-direita", "Meia-direita"), "80%", "65%", "PD"),
        "Centroavante (CA)": SlotTatico(("Centroavante",), "50%", "82%", "CA"),
    },
    "4-3-2-1 Árvore de Natal": {
        "Goleiro (GOL)": SlotTatico(("Goleiro",), "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": SlotTatico(("Lateral-esquerdo",), "15%", "28%", "LE"),
        "Zagueiro Esquerdo (ZAG)": SlotTatico(("Zagueiro",), "37%", "22%", "ZAG"),
        "Zagueiro Direito (ZAG)": SlotTatico(("Zagueiro",), "63%", "22%", "ZAG"),
        "Lateral-direito (LD)": SlotTatico(("Lateral-direito",), "85%", "28%", "LD"),
        "Mezzala Esquerdo (MCE)": SlotTatico(("Mezzala esquerdo", "Volante"), "25%", "45%", "MCE"),
        "Volante (VOL)": SlotTatico(("Volante",), "50%", "42%", "VOL"),
        "Mezzala Direito (MCD)": SlotTatico(("Mezzala direito", "Volante"), "75%", "45%", "MCD"),
        "Meia-Armador Esq (MEI)": SlotTatico(("Meia-armador", "Segundo atacante", "Ponta-esquerda"), "35%", "65%", "MEI"),
        "Meia-Armador Dir (MEI)": SlotTatico(("Meia-armador", "Segundo atacante", "Ponta-direita"), "65%", "65%", "MEI"),
        "Centroavante (CA)": SlotTatico(("Centroavante",), "50%", "82%", "CA"),
    },
}


def normalizar_posicao(posicao: Any) -> str | None:
    """Converte grafias antigas/externas para uma posição oficial."""
    if posicao is None:
        return None
    valor = str(posicao).strip()
    if not valor:
        return None
    if valor in POSICOES_OFICIAIS:
        return valor
    return ALIASES_POSICAO.get(valor)


def normalizar_lista_posicoes(posicoes: Iterable[Any] | None) -> list[str]:
    """Normaliza, elimina duplicidades e descarta posições não reconhecidas."""
    resultado: list[str] = []
    for item in posicoes or []:
        normalizada = normalizar_posicao(item)
        if normalizada and normalizada not in resultado:
            resultado.append(normalizada)
    return resultado


def obter_atletas_compativeis(
    jogadores: Mapping[str, Mapping[str, Any]],
    posicoes_permitidas: Iterable[str],
) -> list[str]:
    permitidas = set(posicoes_permitidas)
    nomes: list[str] = []
    for nome, dados in jogadores.items():
        posicoes = dados.get("posicoes_multiplas") or [dados.get("posicao")]
        if any(posicao in permitidas for posicao in posicoes):
            nomes.append(nome)
    return sorted(nomes, key=str.casefold)


def formatar_jogador_com_posicao(nome: str, jogadores: Mapping[str, Mapping[str, Any]]) -> str:
    dados = jogadores.get(nome)
    if not dados:
        return nome
    posicoes = dados.get("posicoes_multiplas") or [dados.get("posicao")]
    siglas: list[str] = []
    for posicao in posicoes:
        sigla = ABREVIACOES.get(str(posicao), "OBS")
        if sigla not in siglas:
            siglas.append(sigla)
    clube = str(dados.get("clube") or "N/A")
    return f"{nome} — {clube} — {'/'.join(siglas)}"


def indice_adaptabilidade(dados_jogador: Mapping[str, Any], posicoes_permitidas: Iterable[str]) -> int:
    """Retorna 0 para posição primária, 1 para secundária, 2+ para terciária e -1 se incompatível."""
    permitidas = set(posicoes_permitidas)
    posicoes = dados_jogador.get("posicoes_multiplas") or [dados_jogador.get("posicao")]
    for indice, posicao in enumerate(posicoes):
        if posicao in permitidas:
            return indice
    return -1


def validar_taticas(_jogadores: Mapping[str, Mapping[str, Any]] | None = None) -> list[str]:
    """Valida quantidade de slots e uso exclusivo das posições oficiais."""
    erros: list[str] = []
    for nome_tatica, slots in TATICAS.items():
        if len(slots) != LIMITE_TITULARES:
            erros.append(f"{nome_tatica}: possui {len(slots)} slots, não {LIMITE_TITULARES}.")
        for slot, configuracao in slots.items():
            invalidas = [p for p in configuracao.posicoes if p not in POSICOES_OFICIAIS]
            if invalidas:
                erros.append(f"{nome_tatica} / {slot}: posições inválidas {invalidas}.")
    return erros
