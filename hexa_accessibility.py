"""Utilitários puros de acessibilidade e contraste WCAG."""

from __future__ import annotations

import re

_HEX = re.compile(r"^#?([0-9a-fA-F]{6})$")


def hex_para_rgb(cor: str) -> tuple[float, float, float]:
    correspondencia = _HEX.fullmatch(cor.strip())
    if not correspondencia:
        raise ValueError(f"Cor hexadecimal inválida: {cor!r}")
    valor = correspondencia.group(1)
    return tuple(int(valor[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def luminancia_relativa(cor: str) -> float:
    canais = []
    for canal in hex_para_rgb(cor):
        canais.append(canal / 12.92 if canal <= 0.04045 else ((canal + 0.055) / 1.055) ** 2.4)
    vermelho, verde, azul = canais
    return 0.2126 * vermelho + 0.7152 * verde + 0.0722 * azul


def razao_contraste(cor_a: str, cor_b: str) -> float:
    maior, menor = sorted((luminancia_relativa(cor_a), luminancia_relativa(cor_b)), reverse=True)
    return (maior + 0.05) / (menor + 0.05)


def atende_aa(cor_texto: str, cor_fundo: str, *, texto_grande: bool = False) -> bool:
    limite = 3.0 if texto_grande else 4.5
    return razao_contraste(cor_texto, cor_fundo) >= limite
