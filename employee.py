from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


EMPLOYEE_FIELDS = [
    "employee_id",
    "full_name",
    "gender",
    "department",
    "position",
    "phone_number",
    "hire_date",
    "basic_salary",
    "bank_account_number",
    "status",
]


@dataclass
class Employee:
    employee_id: str
    full_name: str
    gender: str
    department: str
    position: str
    phone_number: str
    hire_date: str
    basic_salary: float
    bank_account_number: str
    status: str = "Active"

    def __post_init__(self) -> None:
        self.employee_id = self.employee_id.strip().upper()
        self.full_name = self.full_name.strip()
        self.gender = self.gender.strip().title()
        self.department = self.department.strip()
        self.position = self.position.strip()
        self.phone_number = self.phone_number.strip()
        self.hire_date = self.hire_date.strip()
        self.bank_account_number = self.bank_account_number.strip()
        self.status = self.status.strip().title() or "Active"
        self.basic_salary = float(self.basic_salary)
        self.validate()

    def validate(self) -> None:
        if not self.employee_id:
            raise ValueError("Employee ID is required.")
        if not self.full_name:
            raise ValueError("Full name is required.")
        if self.gender not in {"Male", "Female", "Other"}:
            raise ValueError("Gender must be Male, Female, or Other.")
        if not self.department:
            raise ValueError("Department is required.")
        if self.basic_salary < 0:
            raise ValueError("Basic salary cannot be negative.")
        if self.status not in {"Active", "Inactive"}:
            raise ValueError("Status must be Active or Inactive.")
        try:
            datetime.strptime(self.hire_date, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("Hire date must use YYYY-MM-DD format.") from exc

    def to_dict(self) -> Dict[str, str]:
        return {
            "employee_id": self.employee_id,
            "full_name": self.full_name,
            "gender": self.gender,
            "department": self.department,
            "position": self.position,
            "phone_number": self.phone_number,
            "hire_date": self.hire_date,
            "basic_salary": f"{self.basic_salary:.2f}",
            "bank_account_number": self.bank_account_number,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, row: Dict[str, str]) -> "Employee":
        # Supports both the full application schema and the short sample import schema.
        return cls(
            employee_id=row.get("employee_id", "").strip(),
            full_name=(row.get("full_name") or row.get("name") or "").strip(),
            gender=row.get("gender", "Other").strip() or "Other",
            department=row.get("department", "").strip(),
            position=row.get("position", "Staff").strip() or "Staff",
            phone_number=row.get("phone_number", "").strip(),
            hire_date=row.get("hire_date", datetime.today().strftime("%Y-%m-%d")).strip(),
            basic_salary=row.get("basic_salary") or row.get("salary") or 0,
            bank_account_number=row.get("bank_account_number", "").strip(),
            status=row.get("status", "Active").strip() or "Active",
        )


class EmployeeManager:
    def __init__(self, file_path: str = "data/employees.csv") -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.employees: Dict[str, Employee] = {}
        self.load()

    def load(self) -> None:
        self.employees = {}
        if not self.file_path.exists():
            self.save()
            return

        with self.file_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not any(row.values()):
                    continue
                employee = Employee.from_dict(row)
                self.employees[employee.employee_id] = employee

    def save(self) -> None:
        with self.file_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=EMPLOYEE_FIELDS)
            writer.writeheader()
            for employee in sorted(self.employees.values(), key=lambda item: item.employee_id):
                writer.writerow(employee.to_dict())

    def add_employee(self, employee: Employee) -> None:
        if employee.employee_id in self.employees:
            raise ValueError(f"Employee {employee.employee_id} already exists.")
        self.employees[employee.employee_id] = employee
        self.save()

    def update_employee(self, employee_id: str, **updates: object) -> Employee:
        employee_id = employee_id.strip().upper()
        employee = self.get_employee(employee_id)
        data = employee.to_dict()
        data.update({key: str(value) for key, value in updates.items() if value not in (None, "")})
        updated = Employee.from_dict(data)
        self.employees[employee_id] = updated
        self.save()
        return updated

    def delete_employee(self, employee_id: str) -> None:
        employee_id = employee_id.strip().upper()
        if employee_id not in self.employees:
            raise KeyError(f"Employee {employee_id} was not found.")
        del self.employees[employee_id]
        self.save()

    def get_employee(self, employee_id: str) -> Employee:
        employee_id = employee_id.strip().upper()
        if employee_id not in self.employees:
            raise KeyError(f"Employee {employee_id} was not found.")
        return self.employees[employee_id]

    def search(self, keyword: str) -> List[Employee]:
        keyword = keyword.strip().lower()
        return [
            employee
            for employee in self.employees.values()
            if keyword in employee.employee_id.lower()
            or keyword in employee.full_name.lower()
            or keyword in employee.department.lower()
            or keyword in employee.position.lower()
        ]

    def all_employees(self, active_only: bool = False) -> List[Employee]:
        employees = list(self.employees.values())
        if active_only:
            employees = [employee for employee in employees if employee.status == "Active"]
        return sorted(employees, key=lambda item: item.employee_id)

    def import_rows(self, rows: List[Dict[str, str]], overwrite: bool = False) -> int:
        imported = 0
        for row in rows:
            employee = Employee.from_dict(row)
            if employee.employee_id in self.employees and not overwrite:
                continue
            self.employees[employee.employee_id] = employee
            imported += 1
        self.save()
        return imported
