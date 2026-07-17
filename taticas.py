"""Regras táticas e vocabulário oficial do projeto.

Este módulo não lê nem grava dados. Ele concentra as posições permitidas,
as formações e as funções de compatibilidade entre atleta e posição.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
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

# Migração de grafias antigas ou nomenclaturas externas para o vocabulário do projeto.
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

# Cada slot contém: posições aceitas, atleta padrão, left, bottom e etiqueta curta.
TATICAS: dict[str, dict[str, tuple[list[str], str, str, str, str]]] = {
    "4-3-3 Diamante": {
        "Goleiro (GOL)": (["Goleiro"], "Alisson", "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": (["Lateral-esquerdo"], "Kaiki Bruno", "15%", "28%", "LE"),
        "Zagueiro Esquerdo (ZAG)": (["Zagueiro"], "Gabriel Magalhães", "37%", "22%", "ZAG"),
        "Zagueiro Direito (ZAG)": (["Zagueiro"], "Lucas Beraldo", "63%", "22%", "ZAG"),
        "Lateral-direito (LD)": (["Lateral-direito"], "Wesley França", "85%", "28%", "LD"),
        "Mezzala Esquerdo (MCE)": (["Mezzala esquerdo", "Meia-esquerda", "Volante"], "Bruno Guimarães", "30%", "52%", "MCE"),
        "Volante (VOL)": (["Volante"], "André", "50%", "40%", "VOL"),
        "Mezzala Direito (MCD)": (["Mezzala direito", "Meia-direita", "Volante"], "João Gomes", "70%", "52%", "MCD"),
        "Ponta-esquerda (PE)": (["Ponta-esquerda", "Segundo atacante"], "Vinicius Junior", "20%", "72%", "PE"),
        "Centroavante (CA)": (["Centroavante"], "Endrick", "50%", "82%", "CA"),
        "Ponta-direita (PD)": (["Ponta-direita", "Meia-armador"], "Estevão", "80%", "72%", "PD"),
    },
    "4-3-3 Clássico": {
        "Goleiro (GOL)": (["Goleiro"], "Alisson", "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": (["Lateral-esquerdo"], "Kaiki Bruno", "15%", "28%", "LE"),
        "Zagueiro Esquerdo (ZAG)": (["Zagueiro"], "Gabriel Magalhães", "37%", "22%", "ZAG"),
        "Zagueiro Direito (ZAG)": (["Zagueiro"], "Lucas Beraldo", "63%", "22%", "ZAG"),
        "Lateral-direito (LD)": (["Lateral-direito"], "Wesley França", "85%", "28%", "LD"),
        "Volante (VOL)": (["Volante"], "André", "38%", "45%", "VOL"),
        "Volante Apoio (VOL)": (["Volante", "Mezzala esquerdo", "Mezzala direito"], "Bruno Guimarães", "62%", "45%", "VOL"),
        "Meia-Armador (MEI)": (["Meia-armador"], "Rodrygo", "50%", "60%", "MEI"),
        "Ponta-esquerda (PE)": (["Ponta-esquerda"], "Vinicius Junior", "20%", "72%", "PE"),
        "Centroavante (CA)": (["Centroavante"], "Endrick", "50%", "82%", "CA"),
        "Ponta-direita (PD)": (["Ponta-direita"], "Estevão", "80%", "72%", "PD"),
    },
    "4-4-2 Diamante": {
        "Goleiro (GOL)": (["Goleiro"], "Alisson", "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": (["Lateral-esquerdo"], "Kaiki Bruno", "15%", "28%", "LE"),
        "Zagueiro Esquerdo (ZAG)": (["Zagueiro"], "Gabriel Magalhães", "37%", "22%", "ZAG"),
        "Zagueiro Direito (ZAG)": (["Zagueiro"], "Lucas Beraldo", "63%", "22%", "ZAG"),
        "Lateral-direito (LD)": (["Lateral-direito"], "Wesley França", "85%", "28%", "LD"),
        "Volante (VOL)": (["Volante"], "André", "50%", "40%", "VOL"),
        "Mezzala Esquerdo (MCE)": (["Mezzala esquerdo"], "Bruno Guimarães", "30%", "52%", "MCE"),
        "Mezzala Direito (MCD)": (["Mezzala direito", "Mezzala esquerdo", "Meia-armador"], "João Gomes", "70%", "52%", "MCD"),
        "Meia-Armador (MEI)": (["Meia-armador"], "Rodrygo", "50%", "65%", "MEI"),
        "Segundo Atacante (SA)": (["Segundo atacante", "Ponta-esquerda", "Ponta-direita", "Centroavante"], "Vinicius Junior", "38%", "78%", "SA"),
        "Centroavante (CA)": (["Centroavante"], "Endrick", "62%", "78%", "CA"),
    },
    "4-4-2 Clássico": {
        "Goleiro (GOL)": (["Goleiro"], "Alisson", "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": (["Lateral-esquerdo"], "Kaiki Bruno", "15%", "28%", "LE"),
        "Zagueiro Esquerdo (ZAG)": (["Zagueiro"], "Gabriel Magalhães", "37%", "22%", "ZAG"),
        "Zagueiro Direito (ZAG)": (["Zagueiro"], "Lucas Beraldo", "63%", "22%", "ZAG"),
        "Lateral-direito (LD)": (["Lateral-direito"], "Wesley França", "85%", "28%", "LD"),
        "Meia-esquerda (ME)": (["Meia-esquerda", "Mezzala esquerdo", "Ponta-esquerda"], "Bruno Guimarães", "20%", "55%", "ME"),
        "Volante Esquerdo (VOL)": (["Volante"], "André", "40%", "45%", "VOL"),
        "Volante Direito (VOL)": (["Volante"], "João Gomes", "60%", "45%", "VOL"),
        "Meia-direita (MD)": (["Meia-direita", "Mezzala direito", "Ponta-direita"], "Estevão", "80%", "55%", "MD"),
        "Segundo Atacante (SA)": (["Segundo atacante", "Meia-armador", "Ponta-esquerda"], "Vinicius Junior", "38%", "78%", "SA"),
        "Centroavante (CA)": (["Centroavante", "Segundo atacante"], "Endrick", "62%", "78%", "CA"),
    },
    "4-2-3-1": {
        "Goleiro (GOL)": (["Goleiro"], "Alisson", "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": (["Lateral-esquerdo"], "Kaiki Bruno", "15%", "28%", "LE"),
        "Zagueiro Esquerdo (ZAG)": (["Zagueiro"], "Gabriel Magalhães", "37%", "22%", "ZAG"),
        "Zagueiro Direito (ZAG)": (["Zagueiro"], "Lucas Beraldo", "63%", "22%", "ZAG"),
        "Lateral-direito (LD)": (["Lateral-direito"], "Wesley França", "85%", "28%", "LD"),
        "Volante Esquerdo (VOL)": (["Volante", "Mezzala esquerdo"], "André", "38%", "42%", "VOL"),
        "Volante Direito (VOL)": (["Volante", "Mezzala direito"], "Bruno Guimarães", "62%", "42%", "VOL"),
        "Ponta-esquerda (PE)": (["Ponta-esquerda", "Meia-esquerda"], "Vinicius Junior", "20%", "65%", "PE"),
        "Meia-Armador (MEI)": (["Meia-armador", "Segundo atacante"], "Rodrygo", "50%", "62%", "MEI"),
        "Ponta-direita (PD)": (["Ponta-direita", "Meia-direita"], "Estevão", "80%", "65%", "PD"),
        "Centroavante (CA)": (["Centroavante"], "Endrick", "50%", "82%", "CA"),
    },
    "4-3-2-1 Árvore de Natal": {
        "Goleiro (GOL)": (["Goleiro"], "Alisson", "50%", "8%", "GOL"),
        "Lateral-esquerdo (LE)": (["Lateral-esquerdo"], "Kaiki Bruno", "15%", "28%", "LE"),
        "Zagueiro Esquerdo (ZAG)": (["Zagueiro"], "Gabriel Magalhães", "37%", "22%", "ZAG"),
        "Zagueiro Direito (ZAG)": (["Zagueiro"], "Lucas Beraldo", "63%", "22%", "ZAG"),
        "Lateral-direito (LD)": (["Lateral-direito"], "Wesley França", "85%", "28%", "LD"),
        "Mezzala Esquerdo (MCE)": (["Mezzala esquerdo", "Volante"], "Bruno Guimarães", "25%", "45%", "MCE"),
        "Volante (VOL)": (["Volante"], "André", "50%", "42%", "VOL"),
        "Mezzala Direito (MCD)": (["Mezzala direito", "Volante"], "João Gomes", "75%", "45%", "MCD"),
        "Meia-Armador Esq (MEI)": (["Meia-armador", "Segundo atacante", "Ponta-esquerda"], "Vinicius Junior", "35%", "65%", "MEI"),
        "Meia-Armador Dir (MEI)": (["Meia-armador", "Segundo atacante", "Ponta-direita"], "Rodrygo", "65%", "65%", "MEI"),
        "Centroavante (CA)": (["Centroavante"], "Endrick", "50%", "82%", "CA"),
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
    abreviacoes: list[str] = []
    for posicao in posicoes:
        sigla = ABREVIACOES.get(str(posicao), "OBS")
        if sigla not in abreviacoes:
            abreviacoes.append(sigla)
    return f"{nome} ({'/'.join(abreviacoes)})"


def indice_adaptabilidade(dados_jogador: Mapping[str, Any], posicoes_permitidas: Iterable[str]) -> int:
    """Retorna 0 para posição primária, 1 para secundária, 2+ para terciária e -1 se incompatível."""
    permitidas = set(posicoes_permitidas)
    posicoes = dados_jogador.get("posicoes_multiplas") or [dados_jogador.get("posicao")]
    for indice, posicao in enumerate(posicoes):
        if posicao in permitidas:
            return indice
    return -1


def validar_taticas(jogadores: Mapping[str, Mapping[str, Any]]) -> list[str]:
    """Valida formações e retorna mensagens de inconsistência."""
    erros: list[str] = []
    for nome_tatica, slots in TATICAS.items():
        if len(slots) != 11:
            erros.append(f"{nome_tatica}: possui {len(slots)} slots, não 11.")
        for slot, (permitidas, padrao, _left, _bottom, _tag) in slots.items():
            invalidas = [p for p in permitidas if p not in POSICOES_OFICIAIS]
            if invalidas:
                erros.append(f"{nome_tatica} / {slot}: posições inválidas {invalidas}.")
            if padrao not in jogadores:
                erros.append(f"{nome_tatica} / {slot}: atleta padrão '{padrao}' não existe.")
                continue
            if indice_adaptabilidade(jogadores[padrao], permitidas) < 0:
                erros.append(f"{nome_tatica} / {slot}: atleta padrão '{padrao}' é incompatível.")
    return erros
