from __future__ import annotations

from attendance import AttendanceManager, AttendanceRecord
from csv_manager import CSVManager
from dashboard import Dashboard
from employee import Employee, EmployeeManager
from payroll import Allowance, Deduction, PayrollProcessor
from report import ReportGenerator


class PayrollApplication:
    def __init__(self) -> None:
        self.employee_manager = EmployeeManager()
        self.attendance_manager = AttendanceManager()
        self.payroll_processor = PayrollProcessor(self.employee_manager, self.attendance_manager)
        self.csv_manager = CSVManager()
        self.reports = ReportGenerator()
        self.dashboard = Dashboard()

    def run(self) -> None:
        while True:
            print("\nETHIOPIAN PAYROLL MANAGEMENT SYSTEM")
            print("1. Employee Management")
            print("2. Process Payroll")
            print("3. Generate Reports")
            print("4. Import Employees")
            print("5. Export Payroll")
            print("6. Dashboard")
            print("7. Exit")
            choice = input("Choose an option: ").strip()

            try:
                if choice == "1":
                    self.employee_menu()
                elif choice == "2":
                    self.process_payroll_menu()
                elif choice == "3":
                    self.report_menu()
                elif choice == "4":
                    self.import_employees()
                elif choice == "5":
                    self.export_payroll()
                elif choice == "6":
                    print(self.dashboard.build(self.employee_manager.all_employees(), self.payroll_processor.load_records()))
                elif choice == "7":
                    print("Goodbye.")
                    break
                else:
                    print("Invalid option.")
            except (ValueError, KeyError, FileNotFoundError) as error:
                print(f"Error: {error}")

    def employee_menu(self) -> None:
        while True:
            print("\nEmployee Management")
            print("1. Add Employee")
            print("2. Update Employee")
            print("3. Delete Employee")
            print("4. Search Employee")
            print("5. View All Employees")
            print("6. Record Attendance")
            print("7. Back")
            choice = input("Choose an option: ").strip()

            if choice == "1":
                self.add_employee()
            elif choice == "2":
                self.update_employee()
            elif choice == "3":
                employee_id = input("Employee ID: ")
                self.employee_manager.delete_employee(employee_id)
                print("Employee deleted.")
            elif choice == "4":
                keyword = input("Search keyword: ")
                print(self.reports.employee_list_report(self.employee_manager.search(keyword)))
            elif choice == "5":
                print(self.reports.employee_list_report(self.employee_manager.all_employees()))
            elif choice == "6":
                self.record_attendance()
            elif choice == "7":
                return
            else:
                print("Invalid option.")

    def add_employee(self) -> None:
        employee = Employee(
            input("Employee ID: "),
            input("Full Name: "),
            input("Gender (Male/Female/Other): "),
            input("Department: "),
            input("Position: "),
            input("Phone Number: "),
            input("Hire Date (YYYY-MM-DD): "),
            float(input("Basic Salary: ")),
            input("Bank Account Number: "),
            input("Status (Active/Inactive): ") or "Active",
        )
        self.employee_manager.add_employee(employee)
        print("Employee added.")

    def update_employee(self) -> None:
        employee_id = input("Employee ID to update: ")
        print("Leave fields blank to keep current values.")
        updates = {
            "full_name": input("Full Name: "),
            "gender": input("Gender: "),
            "department": input("Department: "),
            "position": input("Position: "),
            "phone_number": input("Phone Number: "),
            "hire_date": input("Hire Date (YYYY-MM-DD): "),
            "basic_salary": input("Basic Salary: "),
            "bank_account_number": input("Bank Account Number: "),
            "status": input("Status: "),
        }
        self.employee_manager.update_employee(employee_id, **updates)
        print("Employee updated.")

    def record_attendance(self) -> None:
        record = AttendanceRecord(
            employee_id=input("Employee ID: "),
            month=input("Month (YYYY-MM): "),
            working_days=int(input("Working Days: ") or 22),
            absent_days=int(input("Absent Days: ") or 0),
            overtime_hours=float(input("Overtime Hours: ") or 0),
            late_days=int(input("Late Days: ") or 0),
        )
        self.attendance_manager.set_record(record)
        print("Attendance recorded.")

    def process_payroll_menu(self) -> None:
        month = input("Payroll month (YYYY-MM): ").strip()
        print("Default allowance and deduction values will apply to all active employees.")
        allowance = Allowance(
            housing=float(input("Housing Allowance: ") or 0),
            transport=float(input("Transport Allowance: ") or 0),
            meal=float(input("Meal Allowance: ") or 0),
            communication=float(input("Communication Allowance: ") or 0),
            bonus=float(input("Bonus: ") or 0),
        )
        deduction = Deduction(
            loan_repayment=float(input("Loan Repayment: ") or 0),
            advance_salary=float(input("Advance Salary: ") or 0),
            penalty=float(input("Penalty: ") or 0),
            other=float(input("Other Deductions: ") or 0),
        )
        records = self.payroll_processor.process_monthly_payroll(month, allowance, deduction)
        for record in records:
            payslip = self.payroll_processor.generate_payslip(record)
            print("\n" + payslip)
        print(f"Processed payroll for {len(records)} employee(s).")

    def report_menu(self) -> None:
        payroll_rows = self.payroll_processor.load_records()
        print("\nReports")
        print("1. Payroll Summary Report")
        print("2. Employee Payroll Report")
        print("3. Tax Report")
        print("4. Pension Report")
        print("5. Department Payroll Report")
        choice = input("Choose report: ").strip()

        if choice == "1":
            print(self.reports.payroll_summary_report(payroll_rows))
        elif choice == "2":
            print(self.reports.employee_payroll_report(payroll_rows))
        elif choice == "3":
            print(self.reports.tax_report(payroll_rows))
        elif choice == "4":
            print(self.reports.pension_report(payroll_rows))
        elif choice == "5":
            print(self.reports.department_payroll_report(payroll_rows))
        else:
            print("Invalid option.")

    def import_employees(self) -> None:
        file_path = input("CSV file path [employees.csv]: ").strip() or "employees.csv"
        rows = self.csv_manager.read_csv(file_path)
        count = self.employee_manager.import_rows(rows, overwrite=True)
        print(f"Imported {count} employee(s).")

    def export_payroll(self) -> None:
        destination = input("Export path [exports/payroll_report.csv]: ").strip() or "exports/payroll_report.csv"
        rows = self.payroll_processor.load_records()
        self.csv_manager.export_rows(rows, destination)
        print(f"Payroll exported to {destination}.")


if __name__ == "__main__":
    PayrollApplication().run()
