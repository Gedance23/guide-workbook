from fastapi import Depends, FastAPI, UploadFile, File, Query, HTTPException
from datetime import date
import os
from pathlib import Path
import shutil
from tempfile import NamedTemporaryFile

from sqlalchemy.orm import Session

from app.domain.entities import EmployeeProfile, StatutoryGuideline, AuditReport
from app.infrastructure.persistence.database import engine, get_db, save_audit_report
from app.infrastructure.persistence.sqlalchemy_models import Base
from app.infrastructure.parsers.excel_parser import ExcelPayrollParser

app = FastAPI(
    title="PayAlign Compliance API",
    version="1.0.0",
    description=(
        "Audit payroll workbooks against Basel-Stadt compliance rules. "
        "Upload a workbook or configure a preloaded default workbook."
    ),
)
DEFAULT_PAYROLL_FILE = Path(
    os.getenv("PAYALIGN_DEFAULT_PAYROLL_FILE", "data/Payslip_2026.xlsx")
).expanduser()


@app.get("/")
def root():
    return {
        "message": "Welcome to PayAlign.",
        "next_step": "Visit /docs for interactive compliance tools.",
        "audit_options": [
            "Upload a payroll workbook to /audit.",
            "Use the configured preloaded workbook by omitting the upload.",
        ],
    }


@app.on_event("startup")
def initialize_database():
    Base.metadata.create_all(bind=engine)

@app.get("/health", tags=["system"], summary="Check API health")
def health_check():
    return {"status": "healthy", "timestamp": date.today().isoformat()}

@app.post(
    "/audit",
    response_model=AuditReport,
    tags=["compliance"],
    summary="Audit a payroll workbook",
    description=(
        "Provide an Excel payroll workbook, or omit the file to use the configured "
        "preloaded workbook. The audit report is saved to the database."
    ),
    responses={404: {"description": "No uploaded or preloaded workbook is available."}},
)
async def upload_and_audit_payroll(
    first_name: str = Query(..., min_length=1, description="Employee's first name"),
    last_name: str = Query(..., min_length=1, description="Employee's last name"),
    dob: str = Query(..., description="Employee's date of birth (YYYY-MM-DD)"),
    target_year: int = Query(2026, ge=2000, le=2100, description="Payroll calendar year"),
    file: UploadFile | None = File(
        None, description="Optional Payslip_2026.xlsx file; defaults to the configured workbook"
    ),
    db: Session = Depends(get_db),
):
    # 1. Parse Input Date of Birth
    try:
        birth_date = date.fromisoformat(dob)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid date of birth in YYYY-MM-DD format.",
        ) from exc

    # 2. Build In-Memory Domain Profiles
    employee = EmployeeProfile(
        first_name=first_name,
        last_name=last_name,
        date_of_birth=birth_date,
        weekly_hours_target=42.0  # Context baseline default
    )
    
    guideline = StatutoryGuideline(year=target_year)

    temp_file_path = None
    try:
        if file is None:
            if not DEFAULT_PAYROLL_FILE.is_file():
                raise HTTPException(
                    status_code=404,
                    detail=("No payroll workbook is available. Upload an Excel file or configure "
                            "PAYALIGN_DEFAULT_PAYROLL_FILE."),
                )
            parser_file_path = str(DEFAULT_PAYROLL_FILE)
            original_filename = DEFAULT_PAYROLL_FILE.name
        else:
            # Cache the upload in a private temporary file without trusting its name.
            original_filename = Path(file.filename or "payroll.xlsx").name
            suffix = Path(original_filename).suffix or ".xlsx"
            if suffix.lower() not in {".xlsx", ".xlsm", ".xls"}:
                raise HTTPException(
                    status_code=400,
                    detail="Please upload an Excel workbook (.xlsx, .xlsm, or .xls).",
                )
            with NamedTemporaryFile(prefix="payalign_", suffix=suffix, delete=False) as buffer:
                temp_file_path = buffer.name
                shutil.copyfileobj(file.file, buffer)
            parser_file_path = temp_file_path

        # 4. Invoke Ingestion Parser Pipeline
        parser = ExcelPayrollParser(parser_file_path)
        report = parser.parse_and_audit(employee, guideline)
        report.target_filename = original_filename
    finally:
        # 5. Guaranteed Cleanup of Temporary Workspace Files
        if temp_file_path:
            Path(temp_file_path).unlink(missing_ok=True)
        if file is not None:
            await file.close()

    save_audit_report(db, report)
    return report
