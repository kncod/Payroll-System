# Ethiopian Payroll Management System

A menu-driven Python 3 payroll application for Ethiopian companies and university-level payroll projects. It manages employees, attendance, allowances, deductions, income tax, pension, payroll processing, reports, CSV import/export, dashboards, and payslips.

## File Structure

```text
payroll/
  attendance.py        Attendance records and CSV storage
  csv_manager.py       Generic CSV import/export helpers
  dashboard.py         Payroll dashboard metrics
  employee.py          Employee model and employee CSV repository
  main.py              Menu-driven console application
  payroll.py           Payroll calculations and payslip generation
  pension.py           Employee and employer pension calculations
  report.py            Formatted console reports
  tax.py               Ethiopian progressive tax engine
  employees.csv        Short-format sample import file
  data/
    employees.csv      Full employee data
    attendance.csv     Sample attendance data
```

## How to Run

Streamlit web dashboard:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Graphical interface:

```bash
python gui.py
```

Console interface:

```bash
python main.py
```

Main menu:

```text
1. Employee Management
2. Process Payroll
3. Generate Reports
4. Import Employees
5. Export Payroll
6. Dashboard
7. Exit
```

## Module Explanation

`employee.py` defines `Employee` and `EmployeeManager`. It validates required fields, salary, status, gender, hire date, and stores employee records in `data/employees.csv`.

`tax.py` defines `EthiopianTaxEngine`. The `calculate_tax(salary)` method uses configurable monthly progressive tax brackets and can also return a breakdown with bracket, rate, deduction, and tax.

`pension.py` defines `PensionCalculator`. It calculates employee pension at 7% and employer pension at 11% by default.

`attendance.py` defines `AttendanceRecord` and `AttendanceManager`. Attendance tracks working days, absent days, overtime hours, and late days. Payroll uses these values for absence deductions, late deductions, and overtime pay.

`payroll.py` defines `Allowance`, `Deduction`, `PayrollRecord`, and `PayrollProcessor`. It calculates gross salary, income tax, pension, deductions, net salary, saves payroll results to CSV, and generates text payslips.

`report.py` defines table formatting and reports: payroll summary, employee payroll, tax, pension, department payroll, and employee list.

`csv_manager.py` imports and exports CSV files. The sample short import format is supported:

```csv
employee_id,name,department,salary
EMP001,Abebe,IT,15000
EMP002,Hana,Finance,12000
```

`dashboard.py` shows total employees, total payroll cost, tax collected, pension contributions, average salary, highest paid employee, and lowest paid employee.

`main.py` connects all modules into the console application.

## Salary Formulas

Gross Salary:

```text
Basic Salary + Allowances + Overtime Pay + Bonus
```

Total Deductions:

```text
Income Tax + Employee Pension + Loan Deductions + Other Deductions + Attendance Deductions
```

Net Salary:

```text
Gross Salary - Total Deductions
```

## Ethiopian Tax Brackets

The tax engine stores brackets in code as `TaxBracket(lower, upper, rate, deduction)`. You can update these values in `tax.py` if rates change.

## Class Diagram

```text
+------------------+          +-------------------+
| Employee         |          | EmployeeManager   |
+------------------+          +-------------------+
| employee_id      |<>------->| employees         |
| full_name        |          | load()            |
| basic_salary     |          | save()            |
| status           |          | add_employee()    |
+------------------+          | update_employee() |
                              +-------------------+

+------------------+          +-------------------+
| AttendanceRecord |          | AttendanceManager |
+------------------+          +-------------------+
| working_days     |<>------->| records           |
| absent_days      |          | set_record()      |
| overtime_hours   |          | get_record()      |
+------------------+          +-------------------+

+-------------+    +-------------+    +--------------------+
| Allowance   |    | Deduction   |    | PayrollRecord      |
+-------------+    +-------------+    +--------------------+
| housing     |    | loan        |    | gross_salary       |
| transport   |    | advance     |    | total_deductions   |
| bonus       |    | penalty     |    | net_salary         |
+-------------+    +-------------+    +--------------------+
          \             /                    ^
           \           /                     |
            +---------+              +------------------+
                                     | PayrollProcessor |
                                     +------------------+
                                     | process_employee |
                                     | process_monthly  |
                                     | generate_payslip |
                                     +------------------+

+--------------------+   +-------------------+   +-----------------+
| EthiopianTaxEngine |   | PensionCalculator |   | ReportGenerator |
+--------------------+   +-------------------+   +-----------------+
| calculate_tax()    |   | employee 7%       |   | summary report  |
| tax breakdown      |   | employer 11%      |   | tax report      |
+--------------------+   +-------------------+   +-----------------+
```

## Example Output

Payroll summary report after processing sample data for `2026-06` with default allowances of housing `1,000`, transport `700`, meal `500`, communication `300`, bonus `1,000`, and loan repayment `500`:

```text
+--------------------+-----------+
| Metric             | Value     |
+--------------------+-----------+
| Employees Paid     | 3         |
| Total Gross Salary | 58,465.91 |
| Total Net Salary   | 35,415.35 |
| Total Tax          | 15,963.06 |
+--------------------+-----------+
```

Payslips are saved to `payslips/EMP001_2026-06_payslip.txt` style files. Payroll exports are saved to `exports/payroll_report.csv` from the menu, and a verified sample export is included.
