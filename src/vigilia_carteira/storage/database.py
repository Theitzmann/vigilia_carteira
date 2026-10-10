"""Conexões SQLite com transações e fechamento automático."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def database_connection(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Abre o banco, confirma o bloco ou reverte em caso de erro e fecha a conexão."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, autocommit=True)

    try:
        # O SQLite exige habilitar chaves estrangeiras fora de uma transação.
        connection.execute("PRAGMA foreign_keys = ON")
        connection.autocommit = False

        with connection:
            yield connection
    finally:
        connection.close()
