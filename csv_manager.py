from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List


class CSVManager:
    def read_csv(self, file_path: str) -> List[Dict[str, str]]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")
        with path.open("r", newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    def write_csv(self, file_path: str, rows: Iterable[Dict[str, str]], fieldnames: List[str]) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    def export_rows(self, source_rows: List[Dict[str, str]], destination: str) -> None:
        if not source_rows:
            raise ValueError("There are no records to export.")
        self.write_csv(destination, source_rows, list(source_rows[0].keys()))
