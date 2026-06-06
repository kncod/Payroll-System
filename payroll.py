from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from attendance import AttendanceManager, AttendanceRecord
from employee import Employee, EmployeeManager
from pension import PensionCalculator
from tax import EthiopianTaxEngine


PAYROLL_FIELDS = [
    "month",
    "employee_id",
    "full_name",
    "department",
    "basic_salary",
    "housing_allowance",
    "transport_allowance",
    "meal_allowance",
    "communication_allowance",
    "bonus",
    "overtime_pay",
    "gross_salary",
    "income_tax",
    "employee_pension",
    "employer_pension",
    "loan_repayment",
    "advance_salary",
    "penalty",
    "other_deductions",
    "absence_deduction",
    "late_deduction",
    "total_deductions",
    "net_salary",
]


@dataclass
class Allowance:
    housing: float = 0
    transport: float = 0
    meal: float = 0
    communication: float = 0
    bonus: float = 0

    def total(self) -> float:
        return round(self.housing + self.transport + self.meal + self.communication + self.bonus, 2)


@dataclass
class Deduction:
    loan_repayment: float = 0
    advance_salary: float = 0
    penalty: float = 0
    other: float = 0

    def total(self) -> float:
        return round(self.loan_repayment + self.advance_salary + self.penalty + self.other, 2)


@dataclass
class PayrollRecord:
    month: str
    employee: Employee
    attendance: AttendanceRecord
    allowance: Allowance = field(default_factory=Allowance)
    deduction: Deduction = field(default_factory=Deduction)
    overtime_rate_multiplier: float = 1.5
    income_tax: float = 0
    employee_pension: float = 0
    employer_pension: float = 0
    absence_deduction: float = 0
    late_deduction: float = 0
    overtime_pay: float = 0
    gross_salary: float = 0
    total_deductions: float = 0
    net_salary: float = 0

    def to_dict(self) -> Dict[str, str]:
        return {
            "month": self.month,
            "employee_id": self.employee.employee_id,
            "full_name": self.employee.full_name,
            "department": self.employee.department,
            "basic_salary": f"{self.employee.basic_salary:.2f}",
            "housing_allowance": f"{self.allowance.housing:.2f}",
            "transport_allowance": f"{self.allowance.transport:.2f}",
            "meal_allowance": f"{self.allowance.meal:.2f}",
            "communication_allowance": f"{self.allowance.communication:.2f}",
            "bonus": f"{self.allowance.bonus:.2f}",
            "overtime_pay": f"{self.overtime_pay:.2f}",
            "gross_salary": f"{self.gross_salary:.2f}",
            "income_tax": f"{self.income_tax:.2f}",
            "employee_pension": f"{self.employee_pension:.2f}",
            "employer_pension": f"{self.employer_pension:.2f}",
            "loan_repayment": f"{self.deduction.loan_repayment:.2f}",
            "advance_salary": f"{self.deduction.advance_salary:.2f}",
            "penalty": f"{self.deduction.penalty:.2f}",
            "other_deductions": f"{self.deduction.other:.2f}",
            "absence_deduction": f"{self.absence_deduction:.2f}",
            "late_deduction": f"{self.late_deduction:.2f}",
            "total_deductions": f"{self.total_deductions:.2f}",
            "net_salary": f"{self.net_salary:.2f}",
        }


class PayrollProcessor:
    def __init__(
        self,
        employee_manager: EmployeeManager,
        attendance_manager: Optional[AttendanceManager] = None,
        tax_engine: Optional[EthiopianTaxEngine] = None,
        pension_calculator: Optional[PensionCalculator] = None,
        output_file: str = "data/payroll_results.csv",
    ) -> None:
        self.employee_manager = employee_manager
        self.attendance_manager = attendance_manager or AttendanceManager()
        self.tax_engine = tax_engine or EthiopianTaxEngine()
        self.pension_calculator = pension_calculator or PensionCalculator()
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.records: List[PayrollRecord] = []

    def process_employee(
        self,
        employee: Employee,
        month: str,
        allowance: Optional[Allowance] = None,
        deduction: Optional[Deduction] = None,
        attendance: Optional[AttendanceRecord] = None,
    ) -> PayrollRecord:
        allowance = allowance or Allowance()
        deduction = deduction or Deduction()
        attendance = attendance or self.attendance_manager.get_record(employee.employee_id, month)

        daily_rate = employee.basic_salary / attendance.working_days
        hourly_rate = daily_rate / 8
        absence_deduction = daily_rate * attendance.absent_days
        late_deduction = (hourly_rate * 0.5) * attendance.late_days
        overtime_pay = hourly_rate * attendance.overtime_hours * 1.5

        taxable_gross = employee.basic_salary + allowance.total() + overtime_pay
        income_tax = self.tax_engine.calculate_tax(taxable_gross)
        employee_pension = self.pension_calculator.calculate_employee_pension(employee.basic_salary)
        employer_pension = self.pension_calculator.calculate_employer_pension(employee.basic_salary)
        total_deductions = (
            income_tax
            + employee_pension
            + deduction.total()
            + absence_deduction
            + late_deduction
        )

        record = PayrollRecord(
            month=month,
            employee=employee,
            attendance=attendance,
            allowance=allowance,
            deduction=deduction,
            income_tax=round(income_tax, 2),
            employee_pension=round(employee_pension, 2),
            employer_pension=round(employer_pension, 2),
            absence_deduction=round(absence_deduction, 2),
            late_deduction=round(late_deduction, 2),
            overtime_pay=round(overtime_pay, 2),
            gross_salary=round(taxable_gross, 2),
            total_deductions=round(total_deductions, 2),
            net_salary=round(taxable_gross - total_deductions, 2),
        )
        return record

    def process_monthly_payroll(
        self,
        month: str,
        default_allowance: Optional[Allowance] = None,
        default_deduction: Optional[Deduction] = None,
    ) -> List[PayrollRecord]:
        if not month.strip():
            raise ValueError("Payroll month is required.")

        self.records = []
        for employee in self.employee_manager.all_employees(active_only=True):
            record = self.process_employee(employee, month, default_allowance, default_deduction)
            self.records.append(record)
        self.save_records(self.records)
        return self.records

    def save_records(self, records: List[PayrollRecord]) -> None:
        with self.output_file.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=PAYROLL_FIELDS)
            writer.writeheader()
            for record in records:
                writer.writerow(record.to_dict())

    def load_records(self) -> List[Dict[str, str]]:
        if not self.output_file.exists():
            return []
        with self.output_file.open("r", newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    def generate_payslip(self, record: PayrollRecord, folder: str = "payslips") -> str:
        Path(folder).mkdir(parents=True, exist_ok=True)
        text = self._format_payslip(record)
        file_path = Path(folder) / f"{record.employee.employee_id}_{record.month}_payslip.txt"
        file_path.write_text(text, encoding="utf-8")
        return text

    def _format_payslip(self, record: PayrollRecord) -> str:
        employee = record.employee
        return f"""
ETHIOPIAN PAYROLL MANAGEMENT SYSTEM - PAYSLIP
Month: {record.month}
Employee: {employee.employee_id} - {employee.full_name}
Department: {employee.department}
Position: {employee.position}
Bank Account: {employee.bank_account_number}

EARNINGS
Basic Salary:              {employee.basic_salary:,.2f}
Housing Allowance:         {record.allowance.housing:,.2f}
Transport Allowance:       {record.allowance.transport:,.2f}
Meal Allowance:            {record.allowance.meal:,.2f}
Communication Allowance:   {record.allowance.communication:,.2f}
Bonus:                     {record.allowance.bonus:,.2f}
Overtime Pay:              {record.overtime_pay:,.2f}
Gross Salary:              {record.gross_salary:,.2f}

DEDUCTIONS
Income Tax:                {record.income_tax:,.2f}
Employee Pension:          {record.employee_pension:,.2f}
Loan Repayment:            {record.deduction.loan_repayment:,.2f}
Advance Salary:            {record.deduction.advance_salary:,.2f}
Penalty:                   {record.deduction.penalty:,.2f}
Other Deductions:          {record.deduction.other:,.2f}
Absence Deduction:         {record.absence_deduction:,.2f}
Late Deduction:            {record.late_deduction:,.2f}
Total Deductions:          {record.total_deductions:,.2f}

NET SALARY:                {record.net_salary:,.2f}
Employer Pension:          {record.employer_pension:,.2f}
""".strip()
