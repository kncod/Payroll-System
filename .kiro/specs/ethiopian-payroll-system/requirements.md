# Requirements Document

## Introduction

This document defines the requirements for an enterprise-grade Payroll Management System tailored for Ethiopian companies. The system automates the full payroll lifecycle — from employee onboarding and salary structure configuration, through monthly payroll processing and tax calculation, to payslip generation and regulatory reporting. It enforces Ethiopian labor law and tax regulations, supports multi-role approval workflows, and provides full audit traceability for all financial operations.

The system is built on Laravel 12 (backend), Vue.js (frontend), and MySQL (database), with role-based access control via Spatie Laravel Permission and authentication via Laravel Sanctum.

---

## Glossary

- **System**: The Ethiopian Payroll Management System as a whole
- **Employee**: A registered staff member whose salary is managed by the System
- **HR_Officer**: A user role responsible for managing employee records and initiating payroll
- **Payroll_Officer**: A user role responsible for processing and reviewing payroll runs
- **Finance_Manager**: A user role responsible for approving and locking payroll
- **Administrator**: A user role with full system access including configuration
- **Payroll_Run**: A single monthly payroll processing cycle for a given period
- **Gross_Salary**: The total earnings before deductions (Basic + Allowances + Overtime + Bonuses)
- **Net_Salary**: The amount paid to the employee after all deductions (Gross − Tax − Pension − Loans − Absences − Other_Deductions)
- **Tax_Engine**: The subsystem responsible for computing Ethiopian income tax using progressive brackets
- **Tax_Bracket**: A configurable income range with an associated marginal tax rate stored in the database
- **Pension_Module**: The subsystem managing employee and employer pension contributions per Ethiopian law
- **Payslip**: A per-employee PDF document showing full earnings and deductions for a payroll period
- **Audit_Log**: An immutable record of all system actions that affect employee data or financial figures
- **Salary_Structure**: The configured set of earnings components (basic, allowances, overtime rate) assigned to an employee
- **Allowance**: An additional earning component, either recurring or one-time, fixed or percentage-based
- **Deduction**: A reduction applied to gross salary, including tax, pension, loan repayments, and absence penalties
- **Loan**: An advance of funds to an employee, repaid through scheduled payroll deductions
- **Attendance_Record**: A record of working days, overtime hours, absent days, late arrivals, and early departures for an employee in a pay period
- **Leave_Record**: A record of approved leave taken by an employee, with type and payroll impact classification
- **Department**: An organisational unit to which employees are assigned
- **Position**: A job title associated with an employee and a department
- **TIN**: Tax Identification Number assigned by the Ethiopian Revenue and Customs Authority
- **Pension_Number**: The identifier assigned to an employee by the relevant pension authority
- **Bank_Transfer_Report**: A payroll export listing employee name, bank account number, bank name, and net salary for electronic payment
- **Payroll_Status**: The lifecycle state of a Payroll_Run — one of: Draft, Review, Approved, Locked, Paid

---

## Requirements

### Requirement 1: User Authentication and Session Management

**User Story:** As a system user, I want to securely log in and have my session managed, so that only authorised personnel can access payroll data.

#### Acceptance Criteria

1. WHEN a user submits valid credentials, THE System SHALL authenticate the user and issue a Sanctum session token.
2. WHEN a user submits invalid credentials, THE System SHALL reject the login attempt and return an error message without revealing which field is incorrect.
3. WHEN a session token expires, THE System SHALL require the user to re-authenticate before accessing any protected resource.
4. THE System SHALL enforce HTTPS for all authentication endpoints.
5. IF a user account is marked inactive, THEN THE System SHALL deny login and return an account-disabled message.

---

### Requirement 2: Role-Based Access Control

**User Story:** As an Administrator, I want roles and permissions enforced throughout the system, so that each user can only perform actions appropriate to their role.

#### Acceptance Criteria

1. THE System SHALL assign each user exactly one of the following roles: Administrator, Finance_Manager, Payroll_Officer, or HR_Officer.
2. WHEN a user attempts an action, THE System SHALL verify that the user's role has the required permission before executing the action.
3. IF a user attempts an action for which their role lacks permission, THEN THE System SHALL return a 403 Forbidden response and log the attempt.
4. THE Administrator SHALL configure role-to-permission mappings through the administration interface without requiring code changes.
5. THE System SHALL use Spatie Laravel Permission to store and resolve all role and permission assignments.

---

### Requirement 3: Employee Management

**User Story:** As an HR_Officer, I want to create and maintain employee records, so that payroll processing has accurate and complete employee data.

#### Acceptance Criteria

1. WHEN an HR_Officer submits a new employee form with all required fields, THE System SHALL generate a unique Employee ID and persist the employee record.
2. THE System SHALL store the following mandatory fields for each employee: full name, date of birth, gender, nationality, hire date, employment type, department, position, basic salary, TIN number, pension number, bank account number, bank name, and active status.
3. THE System SHALL store the following optional fields for each employee: housing allowance, transport allowance, meal allowance, communication allowance, emergency contact name, emergency contact phone, and profile photo.
4. WHEN an HR_Officer updates an employee's salary or personal information, THE System SHALL record the change in the Audit_Log with the previous value, new value, changed field name, and the identity of the user who made the change.
5. THE System SHALL allow HR_Officers to upload documents (PDF, JPG, PNG, maximum 10 MB per file) and associate them with an employee record.
6. WHEN an HR_Officer sets an employee status to Inactive, THE System SHALL exclude the employee from future Payroll_Runs while preserving all historical payroll records.
7. THE System SHALL enforce uniqueness of TIN number and Pension_Number across all employee records.
8. IF a required employee field is missing or invalid on submission, THEN THE System SHALL return a descriptive validation error identifying each failing field.

---

### Requirement 4: Department Management

**User Story:** As an Administrator, I want to manage departments and assign managers, so that the organisational structure is accurately reflected in payroll reporting.

#### Acceptance Criteria

1. THE System SHALL allow Administrators to create, update, and deactivate departments with a name and optional description.
2. WHEN a department is created or updated, THE System SHALL allow the Administrator to assign one active employee as the department manager.
3. THE System SHALL display the current employee count for each department, computed from active employees assigned to that department.
4. THE System SHALL generate a department payroll summary showing total gross salary, total deductions, and total net salary for all active employees in that department for a selected payroll period.
5. IF an Administrator attempts to delete a department that has active employees assigned to it, THEN THE System SHALL reject the deletion and return an explanatory error message.

---

### Requirement 5: Salary Structure Management

**User Story:** As a Payroll_Officer, I want to configure salary structures for employees, so that all earnings components are correctly captured before payroll processing.

#### Acceptance Criteria

1. THE System SHALL allow Payroll_Officers to define a salary structure for each employee comprising: basic salary, housing allowance, transport allowance, meal allowance, communication allowance, overtime hourly rate, and bonus amount.
2. WHEN a salary structure component is updated, THE System SHALL store the effective date of the change and retain the previous structure for historical payroll recalculation.
3. THE System SHALL compute Gross_Salary as the sum of basic salary, all active allowances, overtime earnings, and bonuses applicable for the pay period.
4. IF any salary structure component contains a negative value, THEN THE System SHALL reject the input and return a validation error.

---

### Requirement 6: Allowances Management

**User Story:** As a Payroll_Officer, I want to configure recurring and one-time allowances, so that all additional earnings are accurately included in payroll.

#### Acceptance Criteria

1. THE System SHALL support two allowance frequencies: Recurring (applied every pay period) and One_Time (applied to a single specified pay period).
2. THE System SHALL support two allowance value types: Fixed (a specific monetary amount) and Percentage (a percentage of the employee's basic salary).
3. WHEN a percentage-based allowance is processed, THE System SHALL compute the allowance amount as the specified percentage multiplied by the employee's current basic salary, rounded to two decimal places.
4. WHEN a pay period is processed, THE System SHALL include all active recurring allowances and all one-time allowances whose specified pay period matches the current period for each employee.
5. IF an allowance effective end date has passed, THEN THE System SHALL automatically exclude the allowance from subsequent payroll runs.

---

### Requirement 7: Deductions Management

**User Story:** As a Payroll_Officer, I want to configure and apply deductions, so that all applicable reductions are correctly subtracted from gross salary.

#### Acceptance Criteria

1. THE System SHALL support the following deduction categories: Income_Tax, Employee_Pension, Loan_Repayment, Salary_Advance, Absence_Deduction, and Other_Deduction.
2. THE System SHALL compute the Absence_Deduction as: (basic salary ÷ standard working days in the month) × number of absent days for the employee in that pay period.
3. WHEN a deduction of category Other_Deduction is created, THE System SHALL require a description field of at least 5 characters before persisting the record.
4. THE System SHALL apply deductions in the following fixed order: Income_Tax, Employee_Pension, Loan_Repayment, Salary_Advance, Absence_Deduction, Other_Deduction.
5. IF the sum of all deductions exceeds the employee's gross salary for a given period, THEN THE System SHALL flag the payroll record for manual review and prevent the record from advancing to Approved status.

---

### Requirement 8: Ethiopian Tax Engine

**User Story:** As a Payroll_Officer, I want the system to calculate Ethiopian income tax automatically, so that tax compliance is accurate and consistent with current regulations.

#### Acceptance Criteria

1. THE Tax_Engine SHALL compute income tax using progressive Tax_Brackets stored in the database, applying each bracket's marginal rate to the portion of taxable income that falls within that bracket.
2. THE System SHALL allow Administrators to add, update, and deactivate Tax_Brackets through the administration interface without requiring code or migration changes.
3. WHEN a Tax_Bracket is updated, THE System SHALL record the change in the Audit_Log with the previous and new bracket values, the effective date, and the identity of the Administrator who made the change.
4. THE System SHALL provide a tax simulation screen where any user with Payroll_Officer or higher role can enter a gross salary and receive a full tax breakdown showing each bracket, the applicable income amount, the marginal rate, and the resulting tax for that bracket.
5. THE Tax_Engine SHALL compute taxable income as Gross_Salary minus any statutory tax-exempt allowances as defined in the active Tax_Bracket configuration.
6. WHEN the Tax_Engine computes tax for a payroll record, THE System SHALL store the full bracket-by-bracket breakdown with the payroll record for audit purposes.
7. IF no active Tax_Brackets exist in the database, THEN THE System SHALL prevent payroll processing and notify the Administrator.

---

### Requirement 9: Pension Module

**User Story:** As a Finance_Manager, I want the system to calculate and report pension contributions accurately, so that the company meets its Ethiopian pension obligations.

#### Acceptance Criteria

1. THE Pension_Module SHALL compute the employee pension contribution as 7% of the employee's basic salary for each pay period.
2. THE Pension_Module SHALL compute the employer pension contribution as 11% of the employee's basic salary for each pay period.
3. WHEN a Payroll_Run is locked, THE System SHALL generate a monthly pension report listing each employee's name, pension number, basic salary, employee contribution, and employer contribution for that period.
4. THE System SHALL maintain a full pension history per employee, queryable by date range, showing all past contributions.
5. IF an employee does not have a pension number recorded, THEN THE System SHALL flag the employee record during payroll processing and require the HR_Officer to provide the pension number before the Payroll_Run can advance to Approved status.

---

### Requirement 10: Attendance Integration

**User Story:** As a Payroll_Officer, I want attendance data integrated into payroll processing, so that overtime earnings and absence deductions are computed from actual attendance records.

#### Acceptance Criteria

1. THE System SHALL allow HR_Officers to enter or import an Attendance_Record for each employee per pay period, containing: working days, overtime hours, absent days, late arrival count, and early departure count.
2. WHEN a Payroll_Run is initiated, THE System SHALL use the Attendance_Record for each employee to compute overtime earnings as: overtime hours × overtime hourly rate defined in the employee's salary structure.
3. WHEN a Payroll_Run is initiated, THE System SHALL use the Attendance_Record to compute the Absence_Deduction per Requirement 7, Acceptance Criterion 2.
4. THE System SHALL allow bulk import of attendance records via CSV file following the defined import template (columns: employee_id, period, working_days, overtime_hours, absent_days, late_arrivals, early_departures).
5. IF an Attendance_Record is not present for an employee in the current pay period, THEN THE System SHALL default to the standard working days for that month, zero overtime hours, and zero absent days, and flag the record in the payroll preview for HR_Officer review.

---

### Requirement 11: Leave Integration

**User Story:** As an HR_Officer, I want leave records to affect payroll automatically, so that leave impacts are consistently and accurately reflected in each employee's pay.

#### Acceptance Criteria

1. THE System SHALL support the following leave types: Annual_Leave, Sick_Leave, Unpaid_Leave, and Maternity_Leave.
2. WHEN a leave request is approved, THE System SHALL record the leave type, start date, end date, and total calendar days on the Leave_Record for the employee.
3. WHEN a Payroll_Run is processed for a period containing approved Unpaid_Leave days, THE System SHALL compute a deduction equal to: (basic salary ÷ standard working days) × number of unpaid leave working days.
4. WHILE an employee is on Maternity_Leave approved under Ethiopian law, THE System SHALL apply zero absence deduction for the statutory entitlement period.
5. THE System SHALL display the leave balance for each leave type on the employee's profile, updated after each payroll run.

---

### Requirement 12: Loan Management

**User Story:** As a Finance_Manager, I want to manage employee loans and automate repayment deductions, so that loan repayments are consistently deducted without manual intervention each month.

#### Acceptance Criteria

1. THE System SHALL allow Finance_Managers to create a loan record for an employee specifying: loan amount, disbursement date, number of repayment instalments, and monthly instalment amount.
2. THE System SHALL generate a repayment schedule at loan creation time, listing each instalment date and amount.
3. WHEN a Payroll_Run is processed, THE System SHALL deduct the scheduled instalment amount from the employee's payroll for any loan whose scheduled instalment falls within the pay period.
4. THE System SHALL display the outstanding loan balance for each active loan, computed as: disbursed amount minus the sum of all instalments deducted to date.
5. WHEN the final instalment is deducted, THE System SHALL automatically mark the loan as Closed and stop further deductions.
6. IF an employee has multiple active loans, THEN THE System SHALL deduct instalments for all active loans in the order of disbursement date (oldest first).

---

### Requirement 13: Payroll Processing

**User Story:** As a Payroll_Officer, I want to run and manage monthly payroll cycles, so that all employees are paid accurately and on time.

#### Acceptance Criteria

1. THE System SHALL allow a Payroll_Officer to initiate a Payroll_Run for a specified month and year, creating payroll records in Draft status for all active employees.
2. THE System SHALL prevent creation of a duplicate Payroll_Run for the same month and year for the same company.
3. WHEN a Payroll_Run is in Draft status, THE System SHALL compute for each employee: Gross_Salary, all individual deduction amounts, and Net_Salary using the formula: Net_Salary = Gross_Salary − (Income_Tax + Employee_Pension + Loan_Repayments + Absence_Deductions + Other_Deductions).
4. THE System SHALL provide a payroll preview screen showing the computed figures for all employees before any status transition.
5. WHEN a Payroll_Officer advances a Payroll_Run from Draft to Review, THE System SHALL recalculate all figures using the current salary structures, allowances, deductions, and attendance data.
6. WHEN a Finance_Manager advances a Payroll_Run from Review to Approved, THE System SHALL record the approver's identity and the approval timestamp.
7. WHEN a Finance_Manager advances a Payroll_Run from Approved to Locked, THE System SHALL prevent any further modification to the payroll records for that period.
8. WHEN a Finance_Manager advances a Payroll_Run from Locked to Paid, THE System SHALL record the payment timestamp and prevent any reversal of the Locked status.
9. IF a Net_Salary value is negative for any employee in the payroll preview, THEN THE System SHALL flag that employee's record and prevent the Payroll_Run from advancing beyond Review status until the issue is resolved.
10. THE System SHALL maintain the complete Payroll_Run history, queryable by period, status, department, and employee.

---

### Requirement 14: Payslip Generation

**User Story:** As an Employee (via HR_Officer), I want a professional payslip generated for each pay period, so that I have a clear record of my earnings and deductions.

#### Acceptance Criteria

1. WHEN a Payroll_Run reaches Locked status, THE System SHALL generate a PDF Payslip for each employee in that run.
2. THE Payslip SHALL include: company name and logo, employee full name and ID, pay period, basic salary, itemised list of allowances with amounts, itemised list of deductions with amounts, gross salary, total deductions, and net salary.
3. THE System SHALL allow HR_Officers and Finance_Managers to download individual or bulk Payslips in PDF format.
4. THE System SHALL store all generated Payslips and make them retrievable by employee and pay period indefinitely.
5. IF a Payslip is downloaded, THE System SHALL record the download event in the Audit_Log including the user identity, employee ID, and timestamp.

---

### Requirement 15: Payroll Approval Workflow

**User Story:** As a Finance_Manager, I want a structured approval workflow for payroll runs, so that payroll is reviewed and authorised before funds are disbursed.

#### Acceptance Criteria

1. THE System SHALL enforce the following Payroll_Status transition sequence: Draft → Review → Approved → Locked → Paid; no other transitions SHALL be permitted.
2. WHEN a Payroll_Run is in Draft status, THE Payroll_Officer SHALL be the only role authorised to advance it to Review.
3. WHEN a Payroll_Run is in Review status, THE Finance_Manager SHALL be the only role authorised to advance it to Approved or return it to Draft.
4. WHEN a Payroll_Run is in Approved status, THE Finance_Manager SHALL be the only role authorised to advance it to Locked.
5. WHEN a Payroll_Run is in Locked status, THE Finance_Manager SHALL be the only role authorised to advance it to Paid.
6. THE System SHALL record each status transition in the Audit_Log with the previous status, new status, acting user identity, and timestamp.
7. IF a Finance_Manager returns a Payroll_Run from Review to Draft, THEN THE System SHALL require the Finance_Manager to provide a rejection reason of at least 10 characters before the transition is executed.

---

### Requirement 16: CSV and Excel Import/Export

**User Story:** As an HR_Officer or Payroll_Officer, I want to import and export data via CSV and Excel files, so that bulk operations and regulatory submissions are efficient.

#### Acceptance Criteria

1. THE System SHALL accept CSV and Excel (.xlsx) file imports for the following data types: employees, salary structures, allowances, deductions, and attendance records.
2. WHEN an import file is submitted, THE System SHALL validate every row before persisting any data; if validation errors exist, THE System SHALL return a report listing each failing row number and the specific validation error.
3. THE System SHALL export the following reports in both CSV and Excel (.xlsx) formats: payroll summary, tax report, pension report, and bank transfer report.
4. THE Bank_Transfer_Report export SHALL contain the following columns for each employee in a Payroll_Run: employee full name, bank account number, bank name, and net salary.
5. THE System SHALL use Laravel Excel to handle all import and export operations.
6. IF an import file contains more than 5,000 rows, THEN THE System SHALL process the import as a background job and notify the initiating user via an in-app notification when the job completes.
7. THE System SHALL provide downloadable import template files for each importable data type, pre-formatted with the required column headers.

---

### Requirement 17: Bank Transfer Report

**User Story:** As a Finance_Manager, I want a bank transfer report generated for each locked payroll run, so that I can submit net salary payments to the bank efficiently.

#### Acceptance Criteria

1. WHEN a Payroll_Run reaches Locked status, THE System SHALL make available a Bank_Transfer_Report for that run.
2. THE Bank_Transfer_Report SHALL list one row per active employee in the Payroll_Run, containing: employee full name, bank account number, bank name, and net salary.
3. THE System SHALL allow the Bank_Transfer_Report to be downloaded in both CSV and Excel (.xlsx) formats.
4. IF an employee does not have a bank account number recorded, THEN THE System SHALL exclude that employee from the Bank_Transfer_Report and display the employee in a separate exceptions list.

---

### Requirement 18: Reporting Dashboard

**User Story:** As a Finance_Manager or Administrator, I want a reporting dashboard, so that I can monitor payroll costs and trends at a glance.

#### Acceptance Criteria

1. THE System SHALL display the following summary metrics on the dashboard for the most recently completed Payroll_Run: total active employees, total gross payroll cost, total income tax withheld, total pension contributions (employee and employer combined), and total net payroll paid.
2. THE System SHALL display a bar chart of department payroll costs for the selected pay period, with each department represented as a separate bar.
3. THE System SHALL display a line chart of monthly gross payroll totals for the trailing 12 months.
4. THE System SHALL display an employee cost analysis table showing, for each department, the average gross salary, average net salary, and headcount.
5. WHEN a Finance_Manager or Administrator selects a historical pay period on the dashboard, THE System SHALL update all metrics and charts to reflect the data for that period.
6. THE System SHALL allow Finance_Managers and Administrators to export dashboard summary data in PDF and Excel formats.

---

### Requirement 19: Audit Logging

**User Story:** As an Administrator, I want all significant actions logged immutably, so that the system provides a complete audit trail for compliance and investigation.

#### Acceptance Criteria

1. THE System SHALL record an Audit_Log entry for each of the following events: employee record creation or update, salary structure change, allowance creation or update, deduction creation or update, Payroll_Run status transition, Tax_Bracket configuration change, payslip download, and user login or logout.
2. EACH Audit_Log entry SHALL contain: event type, acting user identity, affected resource type, affected resource ID, previous state (if applicable), new state (if applicable), and UTC timestamp.
3. THE System SHALL make the Audit_Log queryable by event type, user, resource type, resource ID, and date range.
4. THE Audit_Log entries SHALL be immutable: no user role, including Administrator, SHALL be permitted to update or delete Audit_Log records.
5. THE System SHALL retain Audit_Log entries for a minimum of 7 years from the date of creation.

---

### Requirement 20: Data Security and Encryption

**User Story:** As an Administrator, I want sensitive employee data encrypted and access controlled, so that the company meets its data protection obligations.

#### Acceptance Criteria

1. THE System SHALL encrypt the following fields at rest using AES-256: bank account number, TIN number, and pension number.
2. THE System SHALL transmit all data between client and server exclusively over TLS 1.2 or higher.
3. WHEN a Payroll_Run reaches Locked status, THE System SHALL prevent any user, including Administrators, from modifying payroll records for that run.
4. THE System SHALL enforce that only users with the Finance_Manager or Administrator role can view decrypted bank account numbers.
5. IF a user session is idle for more than 30 minutes, THEN THE System SHALL invalidate the session token and require re-authentication.

---

### Requirement 21: Database Design and Integrity

**User Story:** As a developer, I want a well-structured database schema with referential integrity, so that data consistency is maintained across all modules.

#### Acceptance Criteria

1. THE System SHALL implement foreign key constraints between all related tables including employees, departments, positions, payroll runs, payroll records, allowances, deductions, loans, attendance records, and leave records.
2. THE System SHALL define database indexes on all foreign key columns and on columns used as query filters in reporting and payroll processing.
3. THE System SHALL include database seeders for: default roles and permissions, sample departments, sample positions, and current Ethiopian Tax_Brackets.
4. THE System SHALL provide Laravel migrations for all tables, with rollback support for each migration.
5. THE System SHALL use soft deletes on the employees, departments, salary structures, allowances, and deductions tables to preserve historical references.

---

### Requirement 22: User Interface and User Experience

**User Story:** As any system user, I want a modern, responsive user interface, so that I can use the system efficiently on desktop and tablet devices.

#### Acceptance Criteria

1. THE System SHALL provide a responsive web interface built with Vue.js that functions correctly at viewport widths of 768 px and above.
2. THE System SHALL include a payroll processing wizard that guides the Payroll_Officer through the steps of initiating, previewing, and submitting a Payroll_Run for review.
3. THE System SHALL provide a payroll calendar view showing the status of each monthly Payroll_Run for the current year.
4. THE System SHALL provide an employee directory with search and filter capabilities by name, department, position, and employment status.
5. THE System SHALL support a dark mode toggle that persists the user's preference in local storage.
6. THE System SHALL display form validation errors inline, adjacent to the relevant field, within 200 ms of the user leaving the field.

---

### Requirement 23: Performance and Scalability

**User Story:** As an Administrator, I want the system to remain responsive under realistic production loads, so that payroll processing does not degrade as the company grows.

#### Acceptance Criteria

1. WHEN a Payroll_Run is initiated for up to 1,000 active employees, THE System SHALL complete the initial computation of all payroll records within 60 seconds.
2. THE System SHALL process CSV and Excel imports of up to 5,000 rows as background jobs, ensuring the user interface remains responsive during processing.
3. WHEN any dashboard page is loaded, THE System SHALL return all required metrics within 3 seconds for datasets of up to 10,000 payroll records.
4. THE System SHALL use database query optimisation techniques including eager loading and indexed queries to prevent N+1 query problems in payroll and reporting modules.
