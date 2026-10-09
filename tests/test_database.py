"""Testes da infraestrutura SQLite usando apenas bancos e dados temporários."""

import sqlite3
from pathlib import Path

import pytest

from vigilia_carteira.storage.database import database_connection


@pytest.fixture
def populated_db_path(tmp_path: Path) -> Path:
    db_path = tmp_path / "test.db"
    with database_connection(db_path) as connection:
        connection.execute(
            "CREATE TABLE test_items (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
        )
        connection.execute("INSERT INTO test_items (name) VALUES (?)", ("persistido",))
    return db_path


def test_database_is_created(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    assert not db_path.exists()

    with database_connection(db_path):
        assert db_path.is_file()


def test_parent_directories_are_created(tmp_path: Path) -> None:
    db_path = tmp_path / "nested" / "storage" / "test.db"
    assert not db_path.parent.exists()

    with database_connection(db_path):
        assert db_path.parent.is_dir()
        assert db_path.is_file()


def test_connection_executes_sql(tmp_path: Path) -> None:
    with database_connection(tmp_path / "test.db") as connection:
        assert connection.execute("SELECT ?", (42,)).fetchone() == (42,)


def test_foreign_keys_are_enabled_on_every_connection(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"

    for _ in range(2):
        with database_connection(db_path) as connection:
            assert connection.execute("PRAGMA foreign_keys").fetchone() == (1,)


def test_foreign_key_violations_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        with database_connection(tmp_path / "test.db") as connection:
            connection.execute("CREATE TABLE test_parents (id INTEGER PRIMARY KEY)")
            connection.execute(
                "CREATE TABLE test_items "
                "(parent_id INTEGER REFERENCES test_parents(id))"
            )
            connection.execute("INSERT INTO test_items (parent_id) VALUES (?)", (99,))


def test_successful_transaction_persists_changes(populated_db_path: Path) -> None:
    with database_connection(populated_db_path) as connection:
        connection.execute("INSERT INTO test_items (name) VALUES (?)", ("novo item",))

    with database_connection(populated_db_path) as connection:
        assert connection.execute(
            "SELECT name FROM test_items ORDER BY id"
        ).fetchall() == [("persistido",), ("novo item",)]


def test_error_rolls_back_uncommitted_changes(populated_db_path: Path) -> None:
    with pytest.raises(RuntimeError, match="falha sintética"):
        with database_connection(populated_db_path) as connection:
            connection.execute(
                "INSERT INTO test_items (name) VALUES (?)", ("descartado",)
            )
            connection.execute(
                "UPDATE test_items SET name = ? WHERE id = ?", ("alterado", 1)
            )
            raise RuntimeError("falha sintética")

    with database_connection(populated_db_path) as connection:
        assert connection.execute("SELECT name FROM test_items").fetchall() == [
            ("persistido",)
        ]


@pytest.mark.parametrize("error_type", [ValueError, KeyboardInterrupt])
def test_original_exception_is_propagated(
    tmp_path: Path, error_type: type[BaseException]
) -> None:
    error = error_type("erro original")

    with pytest.raises(error_type) as caught:
        with database_connection(tmp_path / "test.db"):
            raise error

    assert caught.value is error


def test_connection_is_closed_after_success(tmp_path: Path) -> None:
    with database_connection(tmp_path / "test.db") as connection:
        connection.execute("SELECT 1")

    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        connection.execute("SELECT 1")


def test_connection_is_closed_after_error(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="falha sintética"):
        with database_connection(tmp_path / "test.db") as connection:
            raise RuntimeError("falha sintética")

    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        connection.execute("SELECT 1")


def test_table_creation_is_rolled_back_after_error(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"

    with pytest.raises(RuntimeError, match="falha sintética"):
        with database_connection(db_path) as connection:
            connection.execute("CREATE TABLE test_items (id INTEGER PRIMARY KEY)")
            raise RuntimeError("falha sintética")

    with database_connection(db_path) as connection:
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE type = ? AND name = ?",
                ("table", "test_items"),
            ).fetchone()
            is None
        )


def test_commit_failure_rolls_back_and_closes_connection(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    with database_connection(db_path) as connection:
        connection.execute("CREATE TABLE test_parents (id INTEGER PRIMARY KEY)")
        connection.execute(
            "CREATE TABLE test_items "
            "(parent_id INTEGER REFERENCES test_parents(id) "
            "DEFERRABLE INITIALLY DEFERRED)"
        )

    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        with database_connection(db_path) as connection:
            connection.execute("INSERT INTO test_items (parent_id) VALUES (?)", (99,))

    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        connection.execute("SELECT 1")

    with database_connection(db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM test_items").fetchone() == (0,)
