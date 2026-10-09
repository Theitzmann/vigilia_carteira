"""Verifica a importação do pacote instalado."""

from importlib import import_module


def test_package_is_importable() -> None:
    package = import_module("vigilia_carteira")

    assert package.__name__ == "vigilia_carteira"
