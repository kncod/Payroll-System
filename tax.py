from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class TaxBracket:
    lower: float
    upper: Optional[float]
    rate: float
    deduction: float


class EthiopianTaxEngine:
    """Monthly employment income tax engine for Ethiopia."""

    def __init__(self) -> None:
        self.brackets: List[TaxBracket] = [
            TaxBracket(0, 600, 0.00, 0),
            TaxBracket(601, 1650, 0.10, 60),
            TaxBracket(1651, 3200, 0.15, 142.50),
            TaxBracket(3201, 5250, 0.20, 302.50),
            TaxBracket(5251, 7800, 0.25, 565),
            TaxBracket(7801, 10900, 0.30, 955),
            TaxBracket(10901, None, 0.35, 1500),
        ]

    def calculate_tax(self, salary: float) -> float:
        return self.calculate_tax_breakdown(salary)["tax"]

    def calculate_tax_breakdown(self, salary: float) -> Dict[str, float | str]:
        if salary < 0:
            raise ValueError("Salary cannot be negative.")

        for bracket in self.brackets:
            if salary >= bracket.lower and (bracket.upper is None or salary <= bracket.upper):
                tax = max((salary * bracket.rate) - bracket.deduction, 0)
                return {
                    "taxable_income": round(salary, 2),
                    "rate": bracket.rate,
                    "deduction": bracket.deduction,
                    "tax": round(tax, 2),
                    "bracket": self._format_bracket(bracket),
                }
        return {"taxable_income": salary, "rate": 0, "deduction": 0, "tax": 0, "bracket": "None"}

    def _format_bracket(self, bracket: TaxBracket) -> str:
        upper = "and above" if bracket.upper is None else f"to {bracket.upper:,.2f}"
        return f"{bracket.lower:,.2f} {upper}"
