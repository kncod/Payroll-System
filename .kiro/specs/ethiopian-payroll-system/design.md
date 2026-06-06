# Design Document

## Ethiopian Payroll Management System

---

## Overview

The Ethiopian Payroll Management System is an enterprise-grade web application that automates the full payroll lifecycle for Ethiopian companies. It enforces Ethiopian labor law and tax regulations (progressive income tax brackets, pension contributions at 7% employee / 11% employer), supports multi-role approval workflows (HR_Officer → Payroll_Officer → Finance_Manager → Administrator), and provides complete audit traceability for all financial operations.

The system is built as a monolithic Laravel 12 application with a Vue.js Single Page Application (SPA) frontend served via Inertia.js. MySQL provides the relational store. Authentication is managed by Laravel Sanctum (session-based cookies for the SPA), authorization by Spatie Laravel Permission, reporting by Laravel Excel (imports/exports) and barryvdh/laravel-dompdf (PDF payslips), and long-running jobs by Laravel Queues (database driver, upgradeable to Redis).

### Design Goals

1. **Correctness** — All financial calculations (tax, pension, allowances, deductions, net salary) must be deterministic, formula-driven, and auditable.
2. **Compliance** — Ethiopian Income Tax Proclamation brackets are database-driven so Administrators can update rates without code changes.
3. **Security** — Sensitive fields (TIN, bank account, pension number) are encrypted at rest (AES-256 via Laravel's `encrypted` cast). Role-based access enforced at every layer.
4. **Auditability** — Every state-changing operation writes an immutable audit log entry.
5. **Performance** — Payroll runs for 1,000 employees complete within 60 seconds using chunked batch processing via Laravel Queue jobs.
6. **Maintainability** — Layered architecture (Controller → Service → Repository → Model) keeps business logic testable and independent of the HTTP layer.

### Requirements Traceability Summary

| Requirement | Design Component(s) |
|---|---|
| 1 – Authentication | Sanctum middleware, `AuthController`, `UserSessionService`, `LoginRequest` |
| 2 – RBAC | Spatie Permission, `PolicyServiceProvider`, all Laravel Policies |
| 3 – Employee Management | `Employee` model, `EmployeeRepository`, `EmployeeService`, `EmployeeController` |
| 4 – Department Management | `Department` model, `DepartmentService`, `DepartmentController` |
| 5 – Salary Structure | `SalaryStructure` model, `SalaryStructureService` |
| 6 – Allowances | `Allowance` model, `AllowanceService` |
| 7 – Deductions | `Deduction` model, `DeductionService` |
| 8 – Tax Engine | `TaxBracket` model, `TaxEngineService`, `TaxSimulationController` |
| 9 – Pension Module | `PensionService`, `PensionReport` export |
| 10 – Attendance | `AttendanceRecord` model, `AttendanceService` |
| 11 – Leave Integration | `LeaveRecord` model, `LeaveService` |
| 12 – Loan Management | `Loan`, `LoanInstalment` models, `LoanService` |
| 13 – Payroll Processing | `PayrollRun`, `PayrollRecord` models, `PayrollCalculationService`, `ProcessPayrollRunJob` |
| 14 – Payslip Generation | `Payslip` model, `PayslipService`, `GeneratePayslipsJob` |
| 15 – Approval Workflow | `PayrollWorkflowService`, state machine, `PayrollRunPolicy` |
| 16 – Import/Export | Import/Export classes, `ImportController`, `ExportController` |
| 17 – Bank Transfer Report | `BankTransferReportExport`, `BankTransferController` |
| 18 – Reporting Dashboard | `DashboardService`, `DashboardController` |
| 19 – Audit Logging | `AuditLog` model, `AuditService`, `RecordsActivity` trait |
| 20 – Security | Encrypted casts, `ForceHttps` middleware, session timeout middleware |
| 21 – Database Design | All migrations, indexes, foreign keys, soft deletes |
| 22 – UI/UX | Vue.js pages/components, Inertia.js, Tailwind CSS |
| 23 – Performance | Queue jobs, chunking, eager loading, caching, DB indexes |

---

## Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────┐
│            Vue.js SPA (Inertia.js)           │  Presentation Layer
│  Pages / Components / Composables / Stores  │
└───────────────────┬─────────────────────────┘
                    │  HTTP (Inertia + Axios)
┌───────────────────▼─────────────────────────┐
│          Laravel HTTP Layer                  │  Transport Layer
│  Routes → Middleware → Form Requests         │
│  Controllers (thin – orchestrate only)       │
└───────────────────┬─────────────────────────┘
                    │  Method calls
┌───────────────────▼─────────────────────────┐
│            Service Layer                     │  Business Logic Layer
│  PayrollCalculationService                   │
│  TaxEngineService  PensionService            │
│  PayslipService    LoanService               │
│  AllowanceService  DeductionService          │
│  AuditService      PayrollWorkflowService    │
│  ImportService     DashboardService          │
└───────────────────┬─────────────────────────┘
                    │  Method calls
┌───────────────────▼─────────────────────────┐
│          Repository Layer                    │  Data Access Layer
│  EmployeeRepository  PayrollRunRepository    │
│  PayrollRecordRepository  LoanRepository     │
│  AttendanceRepository  AuditLogRepository    │
└───────────────────┬─────────────────────────┘
                    │  Eloquent ORM
┌───────────────────▼─────────────────────────┐
│            MySQL Database                    │  Persistence Layer
│  InnoDB engine, foreign keys, indexes        │
│  Encrypted sensitive columns                 │
└─────────────────────────────────────────────┘

     ┌──────────────────────┐
     │   Laravel Queue       │  Async Layer
     │  ProcessPayrollRunJob │
     │  GeneratePayslipsJob  │
     │  ImportJob            │
     │  NotificationJob      │
     └──────────────────────┘
```

### Key Architectural Decisions

1. **Inertia.js over pure API SPA** — Simplifies authentication (session cookies, no CORS complexity), leverages Laravel's built-in validation and redirects, while still allowing Vue.js reactivity and component architecture.
2. **Repository Pattern** — Decouples business logic from Eloquent so services remain testable without database dependencies. Repositories return domain objects / Eloquent models.
3. **Service Layer** — All business rules live in services, not controllers. Controllers translate HTTP to service calls and render responses.
4. **Database-Driven Tax Brackets** — Tax brackets are rows in `tax_brackets` table, not hard-coded constants. The `TaxEngineService` fetches the active bracket set at runtime, enabling zero-downtime rate changes.
5. **Queue-Based Payroll Processing** — The `ProcessPayrollRunJob` processes employees in configurable chunks (100 per chunk) using `Employee::chunk()`, keeping peak memory bounded and enabling the 60-second SLA for 1,000 employees.

### Technology Stack

| Concern | Technology | Version |
|---|---|---|
| Backend Framework | Laravel | 12.x |
| Frontend Framework | Vue.js | 3.x |
| SPA Bridge | Inertia.js | 1.x |
| CSS Framework | Tailwind CSS | 3.x |
| Database | MySQL | 8.x |
| Authentication | Laravel Sanctum | 4.x |
| Authorization | Spatie Laravel Permission | 6.x |
| PDF Generation | barryvdh/laravel-dompdf | 3.x |
| Excel/CSV | maatwebsite/laravel-excel | 3.x |
| Queue Driver | Database (Redis optional) | – |
| File Storage | Laravel Storage (local/S3) | – |
| Charts (frontend) | Chart.js + vue-chartjs | 4.x |

