"""Ativos financeiros identificados por ticker."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    """Ativo com ticker normalizado, composto apenas por letras ASCII e números."""

    ticker: str

    def __post_init__(self) -> None:
        if not isinstance(self.ticker, str):
            raise ValueError("O ticker deve ser uma string.")

        ticker = self.ticker.strip()
        if not ticker or not ticker.isascii() or not ticker.isalnum():
            raise ValueError("O ticker deve conter somente letras ASCII e números.")

        object.__setattr__(self, "ticker", ticker.upper())
