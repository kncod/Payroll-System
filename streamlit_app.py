from __future__ import annotations

import csv
import io
import shutil
from pathlib import Path
from typing import Dict, List

import streamlit as st

from attendance import AttendanceManager, AttendanceRecord
from csv_manager import CSVManager
from employee import Employee, EmployeeManager
from payroll import Allowance, Deduction, PayrollProcessor
from report import ReportGenerator


st.set_page_config(
    page_title="Ethiopian Payroll Management System",
    page_icon="ET",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        .metric-card {
            border: 1px solid #d8dee4;
            border-radius: 8px;
            padding: 16px;
            background: #ffffff;
            min-height: 96px;
        }
        .metric-label {
            color: #57606a;
            font-size: 0.85rem;
            margin-bottom: 6px;
        }
        .metric-value {
            color: #111827;
            font-size: 1.45rem;
            font-weight: 700;
        }
        .section-note {
            color: #57606a;
            font-size: 0.92rem;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.3rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def services() -> Dict[str, object]:
    employee_manager = EmployeeManager()
    attendance_manager = AttendanceManager()
    payroll_processor = PayrollProcessor(employee_manager, attendance_manager)
    return {
        "employees": employee_manager,
        "attendance": attendance_manager,
        "payroll": payroll_processor,
        "csv": CSVManager(),
        "reports": ReportGenerator(),
    }


def refresh_services() -> Dict[str, object]:
    svc = services()
    svc["employees"].load()
    svc["attendance"].load()
    return svc


def money(value: float | int | str) -> str:
    return f"{float(value):,.2f}"


def employee_table_rows(employee_manager: EmployeeManager) -> List[Dict[str, object]]:
    return [
        {
            "Employee ID": employee.employee_id,
            "Full Name": employee.full_name,
            "Gender": employee.gender,
            "Department": employee.department,
            "Position": employee.position,
            "Phone": employee.phone_number,
            "Hire Date": employee.hire_date,
            "Basic Salary": employee.basic_salary,
            "Bank Account": employee.bank_account_number,
            "Status": employee.status,
        }
        for employee in employee_manager.all_employees()
    ]


def attendance_table_rows(attendance_manager: AttendanceManager) -> List[Dict[str, object]]:
    return [
        {
            "Employee ID": record.employee_id,
            "Month": record.month,
            "Working Days": record.working_days,
            "Absent Days": record.absent_days,
            "Overtime Hours": record.overtime_hours,
            "Late Days": record.late_days,
        }
        for record in attendance_manager.all_records()
    ]


def payroll_rows(payroll_processor: PayrollProcessor) -> List[Dict[str, str]]:
    return payroll_processor.load_records()


def payroll_csv_bytes(rows: List[Dict[str, str]]) -> bytes:
    if not rows:
        return b""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def metric_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dashboard_page(employee_manager: EmployeeManager, payroll_processor: PayrollProcessor) -> None:
    employees = employee_manager.all_employees()
    rows = payroll_rows(payroll_processor)
    total_employees = len(employees)
    active_employees = len([employee for employee in employees if employee.status == "Active"])
    total_net = sum(float(row["net_salary"]) for row in rows)
    total_tax = sum(float(row["income_tax"]) for row in rows)
    total_pension = sum(float(row["employee_pension"]) + float(row["employer_pension"]) for row in rows)
    total_cost = sum(float(row["net_salary"]) + float(row["employer_pension"]) for row in rows)
    salaries = [employee.basic_salary for employee in employees]
    average_salary = sum(salaries) / len(salaries) if salaries else 0

    st.title("Dashboard")
    st.caption("Operational payroll view for Ethiopian company payroll teams.")

    cols = st.columns(4)
    with cols[0]:
        metric_card("Total Employees", str(total_employees))
    with cols[1]:
        metric_card("Active Employees", str(active_employees))
    with cols[2]:
        metric_card("Payroll Cost", money(total_cost))
    with cols[3]:
        metric_card("Average Salary", money(average_salary))

    cols = st.columns(3)
    with cols[0]:
        st.metric("Net Salary Paid", money(total_net))
    with cols[1]:
        st.metric("Tax Collected", money(total_tax))
    with cols[2]:
        st.metric("Pension Contributions", money(total_pension))

    st.subheader("Latest Payroll")
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No payroll has been processed yet.")


def employees_page(employee_manager: EmployeeManager) -> None:
    st.title("Employee Management")

    tab_add, tab_update, tab_view = st.tabs(["Add Employee", "Update / Delete", "View Employees"])

    with tab_add:
        with st.form("add_employee_form", clear_on_submit=True):
            cols = st.columns(2)
            employee_id = cols[0].text_input("Employee ID", placeholder="EMP004")
            full_name = cols[1].text_input("Full Name", placeholder="Selam Alemu")
            gender = cols[0].selectbox("Gender", ["Male", "Female", "Other"], index=2)
            department = cols[1].text_input("Department", placeholder="Operations")
            position = cols[0].text_input("Position", placeholder="Payroll Officer")
            phone = cols[1].text_input("Phone Number", placeholder="0911000004")
            hire_date = cols[0].date_input("Hire Date")
            salary = cols[1].number_input("Basic Salary", min_value=0.0, step=500.0)
            bank = cols[0].text_input("Bank Account Number")
            status = cols[1].selectbox("Status", ["Active", "Inactive"])
            submitted = st.form_submit_button("Add Employee", type="primary")

        if submitted:
            try:
                employee_manager.add_employee(
                    Employee(
                        employee_id,
                        full_name,
                        gender,
                        department,
                        position,
                        phone,
                        hire_date.strftime("%Y-%m-%d"),
                        salary,
                        bank,
                        status,
                    )
                )
                st.success("Employee added successfully.")
                st.cache_resource.clear()
                st.rerun()
            except Exception as error:
                st.error(str(error))

    with tab_update:
        employees = employee_manager.all_employees()
        if not employees:
            st.info("No employees available.")
        else:
            selected_id = st.selectbox("Select Employee", [employee.employee_id for employee in employees])
            selected = employee_manager.get_employee(selected_id)
            with st.form("update_employee_form"):
                cols = st.columns(2)
                full_name = cols[0].text_input("Full Name", value=selected.full_name)
                gender = cols[1].selectbox(
                    "Gender",
                    ["Male", "Female", "Other"],
                    index=["Male", "Female", "Other"].index(selected.gender),
                )
                department = cols[0].text_input("Department", value=selected.department)
                position = cols[1].text_input("Position", value=selected.position)
                phone = cols[0].text_input("Phone Number", value=selected.phone_number)
                hire_date = cols[1].text_input("Hire Date", value=selected.hire_date)
                salary = cols[0].number_input("Basic Salary", min_value=0.0, value=float(selected.basic_salary), step=500.0)
                bank = cols[1].text_input("Bank Account Number", value=selected.bank_account_number)
                status = cols[0].selectbox(
                    "Status",
                    ["Active", "Inactive"],
                    index=["Active", "Inactive"].index(selected.status),
                )
                update_clicked = st.form_submit_button("Update Employee", type="primary")

            delete_clicked = st.button("Delete Selected Employee")

            if update_clicked:
                try:
                    employee_manager.update_employee(
                        selected_id,
                        full_name=full_name,
                        gender=gender,
                        department=department,
                        position=position,
                        phone_number=phone,
                        hire_date=hire_date,
                        basic_salary=salary,
                        bank_account_number=bank,
                        status=status,
                    )
                    st.success("Employee updated successfully.")
                    st.cache_resource.clear()
                    st.rerun()
                except Exception as error:
                    st.error(str(error))

            if delete_clicked:
                try:
                    employee_manager.delete_employee(selected_id)
                    st.success("Employee deleted successfully.")
                    st.cache_resource.clear()
                    st.rerun()
                except Exception as error:
                    st.error(str(error))

    with tab_view:
        rows = employee_table_rows(employee_manager)
        st.dataframe(rows, use_container_width=True, hide_index=True)


def attendance_page(employee_manager: EmployeeManager, attendance_manager: AttendanceManager) -> None:
    st.title("Attendance")

    employee_ids = [employee.employee_id for employee in employee_manager.all_employees(active_only=True)]
    if not employee_ids:
        st.warning("Add active employees before recording attendance.")
        return

    with st.form("attendance_form"):
        cols = st.columns(3)
        employee_id = cols[0].selectbox("Employee", employee_ids)
        month = cols[1].text_input("Month", value="2026-06")
        working_days = cols[2].number_input("Working Days", min_value=1, value=22, step=1)
        absent_days = cols[0].number_input("Absent Days", min_value=0, value=0, step=1)
        overtime_hours = cols[1].number_input("Overtime Hours", min_value=0.0, value=0.0, step=1.0)
        late_days = cols[2].number_input("Late Days", min_value=0, value=0, step=1)
        submitted = st.form_submit_button("Save Attendance", type="primary")

    if submitted:
        try:
            attendance_manager.set_record(
                AttendanceRecord(employee_id, month, working_days, absent_days, overtime_hours, late_days)
            )
            st.success("Attendance saved.")
            st.cache_resource.clear()
            st.rerun()
        except Exception as error:
            st.error(str(error))

    st.subheader("Attendance Records")
    st.dataframe(attendance_table_rows(attendance_manager), use_container_width=True, hide_index=True)


def payroll_page(employee_manager: EmployeeManager, payroll_processor: PayrollProcessor) -> None:
    st.title("Payroll Processing")

    with st.form("payroll_form"):
        st.subheader("Payroll Month")
        month = st.text_input("Month", value="2026-06")

        st.subheader("Default Allowances")
        cols = st.columns(5)
        housing = cols[0].number_input("Housing", min_value=0.0, value=1000.0, step=100.0)
        transport = cols[1].number_input("Transport", min_value=0.0, value=700.0, step=100.0)
        meal = cols[2].number_input("Meal", min_value=0.0, value=500.0, step=100.0)
        communication = cols[3].number_input("Communication", min_value=0.0, value=300.0, step=100.0)
        bonus = cols[4].number_input("Bonus", min_value=0.0, value=1000.0, step=100.0)

        st.subheader("Default Deductions")
        cols = st.columns(4)
        loan = cols[0].number_input("Loan Repayment", min_value=0.0, value=500.0, step=100.0)
        advance = cols[1].number_input("Advance Salary", min_value=0.0, value=0.0, step=100.0)
        penalty = cols[2].number_input("Penalty", min_value=0.0, value=0.0, step=100.0)
        other = cols[3].number_input("Other Deductions", min_value=0.0, value=0.0, step=100.0)
        submitted = st.form_submit_button("Process Payroll", type="primary")

    if submitted:
        try:
            records = payroll_processor.process_monthly_payroll(
                month,
                Allowance(housing, transport, meal, communication, bonus),
                Deduction(loan, advance, penalty, other),
            )
            for record in records:
                payroll_processor.generate_payslip(record)
            Path("exports").mkdir(exist_ok=True)
            shutil.copyfile("data/payroll_results.csv", "exports/payroll_report.csv")
            st.success(f"Processed payroll for {len(records)} employee(s). Payslips and CSV output were generated.")
            st.cache_resource.clear()
            st.rerun()
        except Exception as error:
            st.error(str(error))

    rows = payroll_rows(payroll_processor)
    st.subheader("Payroll Results")
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Payroll CSV",
            payroll_csv_bytes(rows),
            file_name="payroll_report.csv",
            mime="text/csv",
        )
    else:
        st.info("No payroll results yet.")


def reports_page(payroll_processor: PayrollProcessor, reports: ReportGenerator) -> None:
    st.title("Reports")

    rows = payroll_rows(payroll_processor)
    report_type = st.selectbox(
        "Report Type",
        ["Payroll Summary", "Employee Payroll", "Tax", "Pension", "Department Payroll"],
    )

    if report_type == "Payroll Summary":
        text = reports.payroll_summary_report(rows)
    elif report_type == "Employee Payroll":
        text = reports.employee_payroll_report(rows)
    elif report_type == "Tax":
        text = reports.tax_report(rows)
    elif report_type == "Pension":
        text = reports.pension_report(rows)
    else:
        text = reports.department_payroll_report(rows)

    st.code(text, language="text")


def payslips_page(employee_manager: EmployeeManager, payroll_processor: PayrollProcessor) -> None:
    st.title("Payslips")

    rows = payroll_rows(payroll_processor)
    if not rows:
        st.info("Process payroll first, then generate or download payslips here.")
        return

    employee_ids = [row["employee_id"] for row in rows]
    selected_id = st.selectbox("Employee", employee_ids)
    selected_row = next(row for row in rows if row["employee_id"] == selected_id)
    employee = employee_manager.get_employee(selected_id)
    month = selected_row["month"]
    record = payroll_processor.process_employee(employee, month)
    payslip = payroll_processor.generate_payslip(record)

    st.text_area("Payslip Preview", payslip, height=480)
    st.download_button(
        "Download Payslip",
        payslip.encode("utf-8"),
        file_name=f"{selected_id}_{month}_payslip.txt",
        mime="text/plain",
    )


def import_export_page(employee_manager: EmployeeManager, payroll_processor: PayrollProcessor) -> None:
    st.title("CSV Import / Export")

    uploaded = st.file_uploader("Import Employees CSV", type=["csv"])
    overwrite = st.checkbox("Overwrite existing employees", value=True)
    if uploaded is not None:
        try:
            text = uploaded.getvalue().decode("utf-8")
            rows = list(csv.DictReader(io.StringIO(text)))
            count = employee_manager.import_rows(rows, overwrite=overwrite)
            st.success(f"Imported {count} employee(s).")
            st.cache_resource.clear()
        except Exception as error:
            st.error(str(error))

    rows = payroll_rows(payroll_processor)
    st.subheader("Export Payroll")
    if rows:
        st.download_button(
            "Download Payroll Report CSV",
            payroll_csv_bytes(rows),
            file_name="payroll_report.csv",
            mime="text/csv",
        )
    else:
        st.info("Process payroll before exporting payroll results.")


def main() -> None:
    inject_styles()
    svc = refresh_services()
    employee_manager: EmployeeManager = svc["employees"]
    attendance_manager: AttendanceManager = svc["attendance"]
    payroll_processor: PayrollProcessor = svc["payroll"]
    reports: ReportGenerator = svc["reports"]

    st.sidebar.title("Payroll System")
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Employees", "Attendance", "Payroll", "Reports", "Payslips", "Import / Export"],
    )
    st.sidebar.divider()
    st.sidebar.write("Data files")
    st.sidebar.code("data/employees.csv\ndata/attendance.csv\ndata/payroll_results.csv", language="text")

    if page == "Dashboard":
        dashboard_page(employee_manager, payroll_processor)
    elif page == "Employees":
        employees_page(employee_manager)
    elif page == "Attendance":
        attendance_page(employee_manager, attendance_manager)
    elif page == "Payroll":
        payroll_page(employee_manager, payroll_processor)
    elif page == "Reports":
        reports_page(payroll_processor, reports)
    elif page == "Payslips":
        payslips_page(employee_manager, payroll_processor)
    else:
        import_export_page(employee_manager, payroll_processor)


if __name__ == "__main__":
    main()
