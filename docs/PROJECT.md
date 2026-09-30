# Project Context & Architecture: PayAlign

## System Purpose
PayAlign is an enterprise-grade automated payroll auditing system. It ingests housekeeper employment text contracts/guides and corresponding monthly Excel payroll spreadsheets to validate complete compliance against Basel-Stadt statutory framework rules (NAV Haushalt BS 215.700).

## Technical Stack
- **Language & Runtime:** Python 3.11+
- **API Framework:** FastAPI
- **Data Ingestion Engine:** Pandas & openpyxl
- **Database & ORM:** PostgreSQL (Production) / SQLite (Local Dev & CI) via SQLAlchemy
- **Test Suite:** pytest, pytest-cov, httpx

## Domain Model (Entities)
1. **EmployeeProfile:** Stores employee metadata, date of birth, and contractual baseline targets.
2. **StatutoryGuideline:** Holds the statutory minimums and financial thresholds (e.g., NAV clauses).
3. **PayrollPeriod:** Encompasses month, year, and target tracking dates.
4. **AuditReport:** Houses structural outcomes, pass ratios, and execution timestamps.
5. **DiscrepancyEntry:** Models specific discrepancies found, tracking text context vs sheet cell values.

## Architectural Architecture (Clean Layers)
Following the inward-dependency rule (`domain ← application ← interfaces ← infrastructure`):
- `src/app/domain`: Core domain models (Entities, business rule invariants, validation logic).
- `src/app/application`: Use Case Services orchestration (e.g., `RunPayrollAuditUseCase`, `ExportAuditReportUseCase`).
- `src/app/interfaces`: HTTP Rest Controllers (FastAPI Routers), DTO Request/Response Schemas, and the Static Web UI.
- `src/app/infrastructure`: File parser engine (Pandas/openpyxl), SQLAlchemy Models, Repository Implementations, and configuration parsers.

## Core Local Commands
### Local Application Execution
```bash
export PYTHONPATH=\$PWD/src
python -m uvicorn app.main:app --reload
```

### Run Test Suite
```bash
export PYTHONPATH=\$PWD/src
export DATABASE_URL=sqlite:///:memory:
pytest -v
```
