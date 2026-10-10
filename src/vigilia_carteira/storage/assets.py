"""Cadastro, consulta e listagem de ativos no SQLite."""

import sqlite3

from vigilia_carteira.domain.assets import Asset


def create_assets_table(connection: sqlite3.Connection) -> None:
    """Cria o esquema de ativos explicitamente, sem confirmar a transação."""
    connection.execute(
        "CREATE TABLE IF NOT EXISTS assets (ticker TEXT PRIMARY KEY NOT NULL)"
    )


def register_asset(connection: sqlite3.Connection, asset: Asset) -> None:
    """Registra um ativo; duplicidades propagam sqlite3.IntegrityError."""
    connection.execute("INSERT INTO assets (ticker) VALUES (?)", (asset.ticker,))


def get_asset(connection: sqlite3.Connection, ticker: str) -> Asset | None:
    """Consulta um ticker normalizado e retorna None quando não há cadastro."""
    normalized_ticker = Asset(ticker).ticker
    row = connection.execute(
        "SELECT ticker FROM assets WHERE ticker = ?", (normalized_ticker,)
    ).fetchone()
    return Asset(row[0]) if row is not None else None


def list_assets(connection: sqlite3.Connection) -> list[Asset]:
    """Retorna os ativos cadastrados em ordem de ticker."""
    rows = connection.execute("SELECT ticker FROM assets ORDER BY ticker").fetchall()
    return [Asset(row[0]) for row in rows]
