from __future__ import annotations

import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from attendance import AttendanceManager, AttendanceRecord
from csv_manager import CSVManager
from dashboard import Dashboard
from employee import Employee, EmployeeManager
from payroll import Allowance, Deduction, PayrollProcessor
from report import ReportGenerator


class PayrollGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Ethiopian Payroll Management System")
        self.geometry("1180x760")
        self.minsize(980, 640)

        self.employee_manager = EmployeeManager()
        self.attendance_manager = AttendanceManager()
        self.payroll_processor = PayrollProcessor(self.employee_manager, self.attendance_manager)
        self.csv_manager = CSVManager()
        self.reports = ReportGenerator()
        self.dashboard = Dashboard()

        self.employee_vars: dict[str, tk.StringVar] = {}
        self.attendance_vars: dict[str, tk.StringVar] = {}
        self.payroll_vars: dict[str, tk.StringVar] = {}
        self.report_type = tk.StringVar(value="Payroll Summary")

        self.configure_style()
        self.build_layout()
        self.refresh_all()

    def configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook.Tab", padding=(16, 8))
        style.configure("Treeview", rowheight=28)
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Action.TButton", padding=(10, 6))

    def build_layout(self) -> None:
        header = ttk.Frame(self, padding=(18, 14))
        header.pack(fill="x")
        ttk.Label(header, text="Ethiopian Payroll Management System", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="Refresh", command=self.refresh_all, style="Action.TButton").pack(side="right")

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.dashboard_tab = ttk.Frame(self.tabs, padding=12)
        self.employee_tab = ttk.Frame(self.tabs, padding=12)
        self.attendance_tab = ttk.Frame(self.tabs, padding=12)
        self.payroll_tab = ttk.Frame(self.tabs, padding=12)
        self.report_tab = ttk.Frame(self.tabs, padding=12)
        self.import_export_tab = ttk.Frame(self.tabs, padding=12)

        self.tabs.add(self.dashboard_tab, text="Dashboard")
        self.tabs.add(self.employee_tab, text="Employees")
        self.tabs.add(self.attendance_tab, text="Attendance")
        self.tabs.add(self.payroll_tab, text="Payroll")
        self.tabs.add(self.report_tab, text="Reports")
        self.tabs.add(self.import_export_tab, text="Import / Export")

        self.build_dashboard_tab()
        self.build_employee_tab()
        self.build_attendance_tab()
        self.build_payroll_tab()
        self.build_report_tab()
        self.build_import_export_tab()

    def build_dashboard_tab(self) -> None:
        self.dashboard_text = self.make_text(self.dashboard_tab, height=20)
        self.dashboard_text.pack(fill="both", expand=True)

    def build_employee_tab(self) -> None:
        container = ttk.Frame(self.employee_tab)
        container.pack(fill="both", expand=True)

        form = ttk.LabelFrame(container, text="Employee Details", padding=12)
        form.pack(side="left", fill="y", padx=(0, 12))

        fields = [
            ("employee_id", "Employee ID"),
            ("full_name", "Full Name"),
            ("gender", "Gender"),
            ("department", "Department"),
            ("position", "Position"),
            ("phone_number", "Phone Number"),
            ("hire_date", "Hire Date"),
            ("basic_salary", "Basic Salary"),
            ("bank_account_number", "Bank Account"),
            ("status", "Status"),
        ]
        defaults = {"gender": "Other", "hire_date": "2026-06-06", "status": "Active"}
        for row, (key, label) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=4)
            var = tk.StringVar(value=defaults.get(key, ""))
            self.employee_vars[key] = var
            if key == "gender":
                widget = ttk.Combobox(form, textvariable=var, values=("Male", "Female", "Other"), state="readonly")
            elif key == "status":
                widget = ttk.Combobox(form, textvariable=var, values=("Active", "Inactive"), state="readonly")
            else:
                widget = ttk.Entry(form, textvariable=var, width=28)
            widget.grid(row=row, column=1, sticky="ew", pady=4)

        buttons = ttk.Frame(form)
        buttons.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(buttons, text="Add", command=self.add_employee).pack(side="left", padx=(0, 6))
        ttk.Button(buttons, text="Update", command=self.update_employee).pack(side="left", padx=6)
        ttk.Button(buttons, text="Delete", command=self.delete_employee).pack(side="left", padx=6)
        ttk.Button(buttons, text="Clear", command=self.clear_employee_form).pack(side="left", padx=6)

        table_frame = ttk.Frame(container)
        table_frame.pack(side="left", fill="both", expand=True)
        self.employee_tree = self.make_tree(
            table_frame,
            ("ID", "Name", "Gender", "Department", "Position", "Phone", "Hire Date", "Salary", "Bank", "Status"),
        )
        self.employee_tree.bind("<<TreeviewSelect>>", self.on_employee_select)

    def build_attendance_tab(self) -> None:
        container = ttk.Frame(self.attendance_tab)
        container.pack(fill="both", expand=True)

        form = ttk.LabelFrame(container, text="Attendance Record", padding=12)
        form.pack(side="left", fill="y", padx=(0, 12))

        fields = [
            ("employee_id", "Employee ID", ""),
            ("month", "Month", "2026-06"),
            ("working_days", "Working Days", "22"),
            ("absent_days", "Absent Days", "0"),
            ("overtime_hours", "Overtime Hours", "0"),
            ("late_days", "Late Days", "0"),
        ]
        for row, (key, label, default) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=4)
            var = tk.StringVar(value=default)
            self.attendance_vars[key] = var
            ttk.Entry(form, textvariable=var, width=24).grid(row=row, column=1, sticky="ew", pady=4)

        ttk.Button(form, text="Save Attendance", command=self.save_attendance).grid(
            row=len(fields), column=0, columnspan=2, sticky="ew", pady=(12, 0)
        )

        table_frame = ttk.Frame(container)
        table_frame.pack(side="left", fill="both", expand=True)
        self.attendance_tree = self.make_tree(
            table_frame,
            ("Employee ID", "Month", "Working Days", "Absent Days", "Overtime Hours", "Late Days"),
        )

    def build_payroll_tab(self) -> None:
        container = ttk.Frame(self.payroll_tab)
        container.pack(fill="both", expand=True)

        form = ttk.LabelFrame(container, text="Monthly Payroll", padding=12)
        form.pack(fill="x")

        fields = [
            ("month", "Month", "2026-06"),
            ("housing", "Housing Allowance", "1000"),
            ("transport", "Transport Allowance", "700"),
            ("meal", "Meal Allowance", "500"),
            ("communication", "Communication Allowance", "300"),
            ("bonus", "Bonus", "1000"),
            ("loan_repayment", "Loan Repayment", "500"),
            ("advance_salary", "Advance Salary", "0"),
            ("penalty", "Penalty", "0"),
            ("other", "Other Deductions", "0"),
        ]
        for index, (key, label, default) in enumerate(fields):
            row = index // 5
            column = (index % 5) * 2
            ttk.Label(form, text=label).grid(row=row, column=column, sticky="w", padx=(0, 6), pady=5)
            var = tk.StringVar(value=default)
            self.payroll_vars[key] = var
            ttk.Entry(form, textvariable=var, width=16).grid(row=row, column=column + 1, sticky="ew", padx=(0, 14), pady=5)

        ttk.Button(form, text="Process Payroll", command=self.process_payroll, style="Action.TButton").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0)
        )
        ttk.Button(form, text="Generate Selected Payslip", command=self.generate_selected_payslip).grid(
            row=2, column=2, columnspan=2, sticky="ew", pady=(12, 0)
        )

        self.payroll_tree = self.make_tree(
            container,
            ("ID", "Name", "Department", "Gross", "Tax", "Pension", "Deductions", "Net"),
        )

    def build_report_tab(self) -> None:
        controls = ttk.Frame(self.report_tab)
        controls.pack(fill="x", pady=(0, 10))
        ttk.Combobox(
            controls,
            textvariable=self.report_type,
            values=("Payroll Summary", "Employee Payroll", "Tax", "Pension", "Department Payroll"),
            state="readonly",
            width=28,
        ).pack(side="left")
        ttk.Button(controls, text="Generate Report", command=self.generate_report, style="Action.TButton").pack(
            side="left", padx=8
        )

        self.report_text = self.make_text(self.report_tab, height=24)
        self.report_text.pack(fill="both", expand=True)

    def build_import_export_tab(self) -> None:
        panel = ttk.Frame(self.import_export_tab)
        panel.pack(anchor="nw")

        ttk.Button(panel, text="Import Employees CSV", command=self.import_employees, style="Action.TButton").grid(
            row=0, column=0, sticky="ew", padx=6, pady=6
        )
        ttk.Button(panel, text="Export Payroll CSV", command=self.export_payroll, style="Action.TButton").grid(
            row=0, column=1, sticky="ew", padx=6, pady=6
        )
        ttk.Button(panel, text="Open Payslips Folder", command=lambda: self.show_info("Payslips are saved in the payslips folder.")).grid(
            row=0, column=2, sticky="ew", padx=6, pady=6
        )

        self.import_export_text = self.make_text(self.import_export_tab, height=16)
        self.import_export_text.pack(fill="both", expand=True, pady=(12, 0))
        self.set_text(self.import_export_text, "Ready. Import employees from employees.csv or export processed payroll results.")

    def make_tree(self, parent: ttk.Frame, columns: tuple[str, ...]) -> ttk.Treeview:
        frame = ttk.Frame(parent)
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=120, anchor="w")
        frame.pack(fill="both", expand=True)
        return tree

    def make_text(self, parent: ttk.Frame, height: int) -> tk.Text:
        text = tk.Text(parent, height=height, wrap="none", font=("Consolas", 10))
        text.configure(bg="#fbfbfb", fg="#111111", relief="solid", borderwidth=1)
        return text

    def refresh_all(self) -> None:
        self.employee_manager.load()
        self.attendance_manager.load()
        self.refresh_employee_table()
        self.refresh_attendance_table()
        self.refresh_payroll_table()
        self.refresh_dashboard()
        self.generate_report()

    def refresh_employee_table(self) -> None:
        self.clear_tree(self.employee_tree)
        for employee in self.employee_manager.all_employees():
            self.employee_tree.insert(
                "",
                "end",
                values=(
                    employee.employee_id,
                    employee.full_name,
                    employee.gender,
                    employee.department,
                    employee.position,
                    employee.phone_number,
                    employee.hire_date,
                    f"{employee.basic_salary:.2f}",
                    employee.bank_account_number,
                    employee.status,
                ),
            )

    def refresh_attendance_table(self) -> None:
        self.clear_tree(self.attendance_tree)
        for record in self.attendance_manager.all_records():
            self.attendance_tree.insert(
                "",
                "end",
                values=(
                    record.employee_id,
                    record.month,
                    record.working_days,
                    record.absent_days,
                    f"{record.overtime_hours:.2f}",
                    record.late_days,
                ),
            )

    def refresh_payroll_table(self) -> None:
        self.clear_tree(self.payroll_tree)
        for row in self.payroll_processor.load_records():
            self.payroll_tree.insert(
                "",
                "end",
                values=(
                    row["employee_id"],
                    row["full_name"],
                    row["department"],
                    row["gross_salary"],
                    row["income_tax"],
                    row["employee_pension"],
                    row["total_deductions"],
                    row["net_salary"],
                ),
            )

    def refresh_dashboard(self) -> None:
        text = self.dashboard.build(self.employee_manager.all_employees(), self.payroll_processor.load_records())
        self.set_text(self.dashboard_text, text)

    def clear_tree(self, tree: ttk.Treeview) -> None:
        for item in tree.get_children():
            tree.delete(item)

    def on_employee_select(self, _event: tk.Event) -> None:
        selected = self.employee_tree.selection()
        if not selected:
            return
        values = self.employee_tree.item(selected[0], "values")
        keys = list(self.employee_vars.keys())
        for key, value in zip(keys, values):
            self.employee_vars[key].set(value)
        self.attendance_vars["employee_id"].set(values[0])

    def add_employee(self) -> None:
        try:
            self.employee_manager.add_employee(self.employee_from_form())
            self.refresh_all()
            self.show_info("Employee added.")
        except Exception as error:
            self.show_error(error)

    def update_employee(self) -> None:
        try:
            employee_id = self.employee_vars["employee_id"].get()
            updates = {key: var.get() for key, var in self.employee_vars.items()}
            self.employee_manager.update_employee(employee_id, **updates)
            self.refresh_all()
            self.show_info("Employee updated.")
        except Exception as error:
            self.show_error(error)

    def delete_employee(self) -> None:
        employee_id = self.employee_vars["employee_id"].get().strip().upper()
        if not employee_id:
            self.show_error("Select or enter an employee ID first.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete employee {employee_id}?"):
            return
        try:
            self.employee_manager.delete_employee(employee_id)
            self.clear_employee_form()
            self.refresh_all()
            self.show_info("Employee deleted.")
        except Exception as error:
            self.show_error(error)

    def employee_from_form(self) -> Employee:
        return Employee(
            self.employee_vars["employee_id"].get(),
            self.employee_vars["full_name"].get(),
            self.employee_vars["gender"].get(),
            self.employee_vars["department"].get(),
            self.employee_vars["position"].get(),
            self.employee_vars["phone_number"].get(),
            self.employee_vars["hire_date"].get(),
            float(self.employee_vars["basic_salary"].get() or 0),
            self.employee_vars["bank_account_number"].get(),
            self.employee_vars["status"].get(),
        )

    def clear_employee_form(self) -> None:
        defaults = {"gender": "Other", "hire_date": "2026-06-06", "status": "Active"}
        for key, var in self.employee_vars.items():
            var.set(defaults.get(key, ""))

    def save_attendance(self) -> None:
        try:
            record = AttendanceRecord(
                self.attendance_vars["employee_id"].get(),
                self.attendance_vars["month"].get(),
                int(self.attendance_vars["working_days"].get() or 22),
                int(self.attendance_vars["absent_days"].get() or 0),
                float(self.attendance_vars["overtime_hours"].get() or 0),
                int(self.attendance_vars["late_days"].get() or 0),
            )
            self.attendance_manager.set_record(record)
            self.refresh_all()
            self.show_info("Attendance saved.")
        except Exception as error:
            self.show_error(error)

    def process_payroll(self) -> None:
        try:
            allowance = Allowance(
                housing=self.float_var("housing"),
                transport=self.float_var("transport"),
                meal=self.float_var("meal"),
                communication=self.float_var("communication"),
                bonus=self.float_var("bonus"),
            )
            deduction = Deduction(
                loan_repayment=self.float_var("loan_repayment"),
                advance_salary=self.float_var("advance_salary"),
                penalty=self.float_var("penalty"),
                other=self.float_var("other"),
            )
            records = self.payroll_processor.process_monthly_payroll(self.payroll_vars["month"].get(), allowance, deduction)
            for record in records:
                self.payroll_processor.generate_payslip(record)
            shutil.copyfile("data/payroll_results.csv", "exports/payroll_report.csv")
            self.refresh_all()
            self.show_info(f"Processed payroll for {len(records)} employee(s).")
        except Exception as error:
            self.show_error(error)

    def generate_selected_payslip(self) -> None:
        selected = self.payroll_tree.selection()
        if not selected:
            self.show_error("Select a payroll row first.")
            return
        employee_id = self.payroll_tree.item(selected[0], "values")[0]
        employee = self.employee_manager.get_employee(employee_id)
        month = self.payroll_vars["month"].get()
        record = self.payroll_processor.process_employee(employee, month)
        payslip = self.payroll_processor.generate_payslip(record)
        self.set_text(self.report_text, payslip)
        self.tabs.select(self.report_tab)

    def generate_report(self) -> None:
        rows = self.payroll_processor.load_records()
        report = self.report_type.get()
        if report == "Payroll Summary":
            text = self.reports.payroll_summary_report(rows)
        elif report == "Employee Payroll":
            text = self.reports.employee_payroll_report(rows)
        elif report == "Tax":
            text = self.reports.tax_report(rows)
        elif report == "Pension":
            text = self.reports.pension_report(rows)
        else:
            text = self.reports.department_payroll_report(rows)
        self.set_text(self.report_text, text)

    def import_employees(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Import Employees",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
        )
        if not file_path:
            return
        try:
            rows = self.csv_manager.read_csv(file_path)
            count = self.employee_manager.import_rows(rows, overwrite=True)
            self.refresh_all()
            self.set_text(self.import_export_text, f"Imported {count} employee(s) from {file_path}.")
        except Exception as error:
            self.show_error(error)

    def export_payroll(self) -> None:
        file_path = filedialog.asksaveasfilename(
            title="Export Payroll",
            defaultextension=".csv",
            initialfile="payroll_report.csv",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
        )
        if not file_path:
            return
        try:
            self.csv_manager.export_rows(self.payroll_processor.load_records(), file_path)
            self.set_text(self.import_export_text, f"Exported payroll to {file_path}.")
        except Exception as error:
            self.show_error(error)

    def float_var(self, key: str) -> float:
        return float(self.payroll_vars[key].get() or 0)

    def set_text(self, widget: tk.Text, value: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value)
        widget.configure(state="disabled")

    def show_info(self, message: str) -> None:
        messagebox.showinfo("Payroll System", message)

    def show_error(self, error: object) -> None:
        messagebox.showerror("Payroll System", str(error))


if __name__ == "__main__":
    PayrollGUI().mainloop()
