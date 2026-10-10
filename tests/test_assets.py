"""Cadastro de ativos usando somente tickers sintéticos e bancos temporários."""

import sqlite3
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from vigilia_carteira.domain.assets import Asset
from vigilia_carteira.storage.assets import (
    create_assets_table,
    get_asset,
    list_assets,
    register_asset,
)
from vigilia_carteira.storage.database import database_connection


@pytest.mark.parametrize("ticker", ["TESTA1", "TEST", "1234"])
def test_valid_asset(ticker: str) -> None:
    asset = Asset(ticker)

    assert asset.ticker == ticker


def test_asset_normalizes_lowercase_and_surrounding_whitespace() -> None:
    assert Asset(" \t testa1 \n").ticker == "TESTA1"


def test_asset_is_immutable() -> None:
    asset = Asset("TESTA1")

    with pytest.raises(FrozenInstanceError):
        asset.ticker = "TESTB2"


@pytest.mark.parametrize(
    "ticker",
    [
        "",
        " \t\n ",
        "TEST A1",
        "TEST-A1",
        "TEST_A1",
        "TEST.A1",
        "TESTA1'",
        "TÉSTA1",
        "ＴESTA1",
        "TESTß1",
        "TESTı1",
        "TESTſ1",
    ],
)
def test_asset_rejects_empty_or_invalid_tickers(ticker: str) -> None:
    with pytest.raises(ValueError):
        Asset(ticker)


@pytest.mark.parametrize("ticker", [None, 42, False, ["TESTA1"]])
def test_asset_rejects_non_string_tickers(ticker: object) -> None:
    with pytest.raises(ValueError):
        Asset(ticker)


def test_assets_table_requires_explicit_creation_and_has_expected_schema(
    tmp_path: Path,
) -> None:
    with database_connection(tmp_path / "test.db") as connection:
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE type = ? AND name = ?",
                ("table", "assets"),
            ).fetchone()
            is None
        )

        create_assets_table(connection)

        assert connection.execute("PRAGMA table_info(assets)").fetchall() == [
            (0, "ticker", "TEXT", 1, None, 1)
        ]


def test_assets_table_creation_is_idempotent(tmp_path: Path) -> None:
    with database_connection(tmp_path / "test.db") as connection:
        create_assets_table(connection)
        register_asset(connection, Asset("TESTA1"))

        create_assets_table(connection)

        assert list_assets(connection) == [Asset("TESTA1")]


def test_register_and_get_asset(tmp_path: Path) -> None:
    asset = Asset("TESTA1")
    with database_connection(tmp_path / "test.db") as connection:
        create_assets_table(connection)

        register_asset(connection, asset)

        assert get_asset(connection, "TESTA1") == asset
        assert get_asset(connection, " testa1 ") == asset


@pytest.mark.parametrize("ticker", ["TESTA1", " testa1 "])
def test_duplicate_asset_is_rejected(tmp_path: Path, ticker: str) -> None:
    asset = Asset("TESTA1")
    with database_connection(tmp_path / "test.db") as connection:
        create_assets_table(connection)
        register_asset(connection, asset)

        with pytest.raises(sqlite3.IntegrityError):
            register_asset(connection, Asset(ticker))

        assert list_assets(connection) == [asset]


def test_get_missing_asset_returns_none(tmp_path: Path) -> None:
    with database_connection(tmp_path / "test.db") as connection:
        create_assets_table(connection)

        assert get_asset(connection, "TESTA1") is None


def test_list_assets_is_empty_for_new_table(tmp_path: Path) -> None:
    with database_connection(tmp_path / "test.db") as connection:
        create_assets_table(connection)

        assert list_assets(connection) == []


def test_list_assets_orders_by_ticker(tmp_path: Path) -> None:
    with database_connection(tmp_path / "test.db") as connection:
        create_assets_table(connection)
        for ticker in ["TESTZ9", "TESTA1", "TESTB2"]:
            register_asset(connection, Asset(ticker))

        assert list_assets(connection) == [
            Asset("TESTA1"),
            Asset("TESTB2"),
            Asset("TESTZ9"),
        ]


def test_assets_persist_between_connections(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    asset = Asset("TESTA1")
    with database_connection(db_path) as connection:
        create_assets_table(connection)
        register_asset(connection, asset)

    with database_connection(db_path) as connection:
        assert get_asset(connection, "TESTA1") == asset
        assert list_assets(connection) == [asset]


def test_failed_transaction_rolls_back_new_asset_and_preserves_existing_asset(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "test.db"
    asset = Asset("TESTA1")
    with database_connection(db_path) as connection:
        create_assets_table(connection)
        register_asset(connection, asset)

    error = RuntimeError("falha sintética")
    with pytest.raises(RuntimeError) as caught:
        with database_connection(db_path) as connection:
            register_asset(connection, Asset("TESTB2"))
            assert get_asset(connection, "TESTB2") == Asset("TESTB2")
            assert len(list_assets(connection)) == 2
            create_assets_table(connection)
            raise error

    assert caught.value is error
    with database_connection(db_path) as connection:
        assert get_asset(connection, "TESTB2") is None
        assert list_assets(connection) == [asset]


def test_failed_schema_initialization_rolls_back_table_creation(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    with pytest.raises(RuntimeError, match="falha sintética"):
        with database_connection(db_path) as connection:
            create_assets_table(connection)
            raise RuntimeError("falha sintética")

    with database_connection(db_path) as connection:
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE type = ? AND name = ?",
                ("table", "assets"),
            ).fetchone()
            is None
        )
