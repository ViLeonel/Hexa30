"""Seleção segura do backend persistente e migração inicial."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from hexa_audit import AuditoriaRepository
from hexa_config import DATA_FILE
from hexa_repository import JogadoresRepository, JsonJogadoresRepository
from hexa_repository_sqlite import (
    SqliteAuditoriaRepository,
    SqliteJogadoresRepository,
)

__all__ = [
    "ConfiguracaoPersistencia",
    "configuracao_persistencia",
    "criar_auditoria",
    "criar_repositorio",
    "migrar_json_para_sqlite",
]


@dataclass(frozen=True, slots=True)
class ConfiguracaoPersistencia:
    backend: str = "json"
    caminho_sqlite: Path | None = None

    @property
    def duravel(self) -> bool:
        return self.backend == "sqlite"

    @property
    def descricao(self) -> str:
        if self.backend == "sqlite":
            return f"SQLite versionado ({self.caminho_sqlite})"
        return f"JSON local ({DATA_FILE.name})"


def _secrets_streamlit() -> Mapping[str, Any]:
    try:
        import streamlit as st
        return st.secrets
    except Exception:
        return {}


def configuracao_persistencia(
    secrets: Mapping[str, Any] | None = None,
) -> ConfiguracaoPersistencia:
    """Lê configuração opt-in. O padrão continua sendo JSON."""
    fonte = secrets if secrets is not None else _secrets_streamlit()
    secao: Mapping[str, Any] = {}
    try:
        candidata = fonte.get("persistencia", {})
        if isinstance(candidata, Mapping):
            secao = candidata
    except Exception:
        secao = {}

    backend = str(
        os.getenv("HEXA_PERSISTENCE_BACKEND")
        or secao.get("backend")
        or "json"
    ).strip().casefold()
    if backend not in {"json", "sqlite"}:
        raise ValueError("Backend de persistência inválido. Use 'json' ou 'sqlite'.")

    if backend == "json":
        return ConfiguracaoPersistencia()

    caminho_bruto = (
        os.getenv("HEXA_SQLITE_PATH")
        or secao.get("sqlite_path")
        or "dados/hexa2030.sqlite3"
    )
    caminho = Path(str(caminho_bruto)).expanduser()
    if not caminho.is_absolute():
        caminho = DATA_FILE.parent / caminho
    return ConfiguracaoPersistencia(
        backend="sqlite",
        caminho_sqlite=caminho.resolve(),
    )


def criar_repositorio(
    configuracao: ConfiguracaoPersistencia | None = None,
) -> JogadoresRepository:
    config = configuracao or configuracao_persistencia()
    if config.backend == "sqlite":
        if config.caminho_sqlite is None:
            raise ValueError("Caminho SQLite não configurado.")
        return SqliteJogadoresRepository(config.caminho_sqlite)
    return JsonJogadoresRepository(DATA_FILE)


def criar_auditoria(
    repositorio: JogadoresRepository,
) -> AuditoriaRepository | None:
    if isinstance(repositorio, SqliteJogadoresRepository):
        return SqliteAuditoriaRepository(repositorio.caminho)
    return None


def migrar_json_para_sqlite(
    *,
    origem: JsonJogadoresRepository,
    destino: SqliteJogadoresRepository,
    forcar: bool = False,
) -> str:
    """Cria a primeira revisão SQLite sem modificar o JSON de origem."""
    if destino.versao_atual() != "ausente" and not forcar:
        raise RuntimeError(
            "O banco SQLite já possui revisão ativa; migração cancelada."
        )
    resultado = origem.carregar()
    registro = destino.salvar(
        resultado.jogadores,
        versao_esperada=destino.versao_atual(),
        origem="migracao_inicial_json",
    )
    return registro.versao
