"""Migra o JSON canônico para SQLite sem alterar a fonte original."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hexa_config import DATA_FILE
from hexa_persistencia_servidor import migrar_json_para_sqlite
from hexa_repository import JsonJogadoresRepository
from hexa_repository_sqlite import SqliteJogadoresRepository


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--destino",
        default="dados/hexa2030.sqlite3",
        help="Caminho do banco SQLite de destino.",
    )
    parser.add_argument(
        "--forcar",
        action="store_true",
        help="Permite criar nova revisão em banco já inicializado.",
    )
    args = parser.parse_args()

    destino = Path(args.destino).expanduser().resolve()
    versao = migrar_json_para_sqlite(
        origem=JsonJogadoresRepository(DATA_FILE),
        destino=SqliteJogadoresRepository(destino),
        forcar=args.forcar,
    )
    print(f"Migração concluída: {destino} | revisão {versao}")


if __name__ == "__main__":
    main()
