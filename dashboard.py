from __future__ import annotations

from typing import Dict, List

from employee import Employee
from report import TableFormatter


class Dashboard(TableFormatter):
    def build(self, employees: List[Employee], payroll_rows: List[Dict[str, str]]) -> str:
        total_employees = len(employees)
        active_employees = len([employee for employee in employees if employee.status == "Active"])
        total_payroll_cost = sum(float(row["net_salary"]) + float(row["employer_pension"]) for row in payroll_rows)
        total_tax = sum(float(row["income_tax"]) for row in payroll_rows)
        total_pension = sum(
            float(row["employee_pension"]) + float(row["employer_pension"]) for row in payroll_rows
        )
        salaries = [employee.basic_salary for employee in employees]
        average_salary = sum(salaries) / len(salaries) if salaries else 0
        highest = max(employees, key=lambda item: item.basic_salary, default=None)
        lowest = min(employees, key=lambda item: item.basic_salary, default=None)

        rows = [
            ["Total Employees", total_employees],
            ["Active Employees", active_employees],
            ["Total Payroll Cost", f"{total_payroll_cost:,.2f}"],
            ["Total Tax Collected", f"{total_tax:,.2f}"],
            ["Total Pension Contributions", f"{total_pension:,.2f}"],
            ["Average Salary", f"{average_salary:,.2f}"],
            ["Highest Paid Employee", highest.full_name if highest else "N/A"],
            ["Lowest Paid Employee", lowest.full_name if lowest else "N/A"],
        ]
        return self.format_table(["Dashboard Metric", "Value"], rows)
