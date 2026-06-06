from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


ATTENDANCE_FIELDS = [
    "employee_id",
    "month",
    "working_days",
    "absent_days",
    "overtime_hours",
    "late_days",
]


@dataclass
class AttendanceRecord:
    employee_id: str
    month: str
    working_days: int
    absent_days: int = 0
    overtime_hours: float = 0
    late_days: int = 0

    def __post_init__(self) -> None:
        self.employee_id = self.employee_id.strip().upper()
        self.month = self.month.strip()
        self.working_days = int(self.working_days)
        self.absent_days = int(self.absent_days)
        self.overtime_hours = float(self.overtime_hours)
        self.late_days = int(self.late_days)
        self.validate()

    def validate(self) -> None:
        if not self.employee_id:
            raise ValueError("Employee ID is required for attendance.")
        if not self.month:
            raise ValueError("Attendance month is required.")
        if self.working_days <= 0:
            raise ValueError("Working days must be greater than zero.")
        if self.absent_days < 0 or self.overtime_hours < 0 or self.late_days < 0:
            raise ValueError("Attendance values cannot be negative.")

    def to_dict(self) -> Dict[str, str]:
        return {
            "employee_id": self.employee_id,
            "month": self.month,
            "working_days": str(self.working_days),
            "absent_days": str(self.absent_days),
            "overtime_hours": f"{self.overtime_hours:.2f}",
            "late_days": str(self.late_days),
        }

    @classmethod
    def from_dict(cls, row: Dict[str, str]) -> "AttendanceRecord":
        return cls(
            row.get("employee_id", ""),
            row.get("month", ""),
            int(row.get("working_days") or 22),
            int(row.get("absent_days") or 0),
            float(row.get("overtime_hours") or 0),
            int(row.get("late_days") or 0),
        )


class AttendanceManager:
    def __init__(self, file_path: str = "data/attendance.csv") -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.records: Dict[str, AttendanceRecord] = {}
        self.load()

    def _key(self, employee_id: str, month: str) -> str:
        return f"{employee_id.strip().upper()}::{month.strip()}"

    def load(self) -> None:
        self.records = {}
        if not self.file_path.exists():
            self.save()
            return
        with self.file_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not any(row.values()):
                    continue
                record = AttendanceRecord.from_dict(row)
                self.records[self._key(record.employee_id, record.month)] = record

    def save(self) -> None:
        with self.file_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=ATTENDANCE_FIELDS)
            writer.writeheader()
            for record in self.records.values():
                writer.writerow(record.to_dict())

    def set_record(self, record: AttendanceRecord) -> None:
        self.records[self._key(record.employee_id, record.month)] = record
        self.save()

    def get_record(self, employee_id: str, month: str) -> AttendanceRecord:
        key = self._key(employee_id, month)
        return self.records.get(
            key,
            AttendanceRecord(employee_id=employee_id, month=month, working_days=22),
        )

    def all_records(self) -> List[AttendanceRecord]:
        return list(self.records.values())
