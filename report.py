from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List


class TableFormatter:
    def format_table(self, headers: List[str], rows: List[List[object]]) -> str:
        if not rows:
            return "No records found."
        widths = [
            max(len(str(header)), *(len(str(row[index])) for row in rows))
            for index, header in enumerate(headers)
        ]
        border = "+-" + "-+-".join("-" * width for width in widths) + "-+"
        header_line = "| " + " | ".join(str(header).ljust(widths[index]) for index, header in enumerate(headers)) + " |"
        row_lines = [
            "| " + " | ".join(str(value).ljust(widths[index]) for index, value in enumerate(row)) + " |"
            for row in rows
        ]
        return "\n".join([border, header_line, border, *row_lines, border])


class ReportGenerator(TableFormatter):
    def payroll_summary_report(self, payroll_rows: List[Dict[str, str]]) -> str:
        total_gross = sum(float(row["gross_salary"]) for row in payroll_rows)
        total_net = sum(float(row["net_salary"]) for row in payroll_rows)
        total_tax = sum(float(row["income_tax"]) for row in payroll_rows)
        rows = [
            ["Employees Paid", len(payroll_rows)],
            ["Total Gross Salary", f"{total_gross:,.2f}"],
            ["Total Net Salary", f"{total_net:,.2f}"],
            ["Total Tax", f"{total_tax:,.2f}"],
        ]
        return self.format_table(["Metric", "Value"], rows)

    def employee_payroll_report(self, payroll_rows: List[Dict[str, str]]) -> str:
        rows = [
            [
                row["employee_id"],
                row["full_name"],
                row["department"],
                f"{float(row['gross_salary']):,.2f}",
                f"{float(row['total_deductions']):,.2f}",
                f"{float(row['net_salary']):,.2f}",
            ]
            for row in payroll_rows
        ]
        return self.format_table(["ID", "Name", "Department", "Gross", "Deductions", "Net"], rows)

    def tax_report(self, payroll_rows: List[Dict[str, str]]) -> str:
        rows = [
            [row["employee_id"], row["full_name"], f"{float(row['gross_salary']):,.2f}", f"{float(row['income_tax']):,.2f}"]
            for row in payroll_rows
        ]
        return self.format_table(["ID", "Name", "Taxable Gross", "Tax"], rows)

    def pension_report(self, payroll_rows: List[Dict[str, str]]) -> str:
        rows = [
            [
                row["employee_id"],
                row["full_name"],
                f"{float(row['employee_pension']):,.2f}",
                f"{float(row['employer_pension']):,.2f}",
            ]
            for row in payroll_rows
        ]
        return self.format_table(["ID", "Name", "Employee Pension", "Employer Pension"], rows)

    def department_payroll_report(self, payroll_rows: List[Dict[str, str]]) -> str:
        departments: Dict[str, Dict[str, float]] = defaultdict(lambda: {"count": 0, "gross": 0, "net": 0})
        for row in payroll_rows:
            item = departments[row["department"]]
            item["count"] += 1
            item["gross"] += float(row["gross_salary"])
            item["net"] += float(row["net_salary"])
        rows = [
            [department, int(values["count"]), f"{values['gross']:,.2f}", f"{values['net']:,.2f}"]
            for department, values in sorted(departments.items())
        ]
        return self.format_table(["Department", "Employees", "Gross", "Net"], rows)

    def employee_list_report(self, employees: Iterable[object]) -> str:
        rows = [
            [
                employee.employee_id,
                employee.full_name,
                employee.department,
                employee.position,
                f"{employee.basic_salary:,.2f}",
                employee.status,
            ]
            for employee in employees
        ]
        return self.format_table(["ID", "Name", "Department", "Position", "Salary", "Status"], rows)
