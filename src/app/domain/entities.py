from datetime import date
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class Severity(str, Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"

class EmployeeProfile(BaseModel):
    id: Optional[int] = None
    first_name: str
    last_name: str
    date_of_birth: date
    weekly_hours_target: float

class StatutoryGuideline(BaseModel):
    id: Optional[int] = None
    year: int = 2026
    holiday_premium_rate: float = 0.5  # 50% floor
    simplified_procedure_individual_cap: float = 22680.0
    simplified_procedure_employer_cap: float = 60480.0
    nbu_weekly_hours_threshold: float = 8.0

class PayrollPeriod(BaseModel):
    id: Optional[int] = None
    month_name: str  # e.g., "Jan"
    calendar_year: int

class DiscrepancyEntry(BaseModel):
    id: Optional[int] = None
    sheet_name: str
    cell_coordinate: str
    rule_violated: str
    severity: Severity
    message: str

class AuditReport(BaseModel):
    id: Optional[int] = None
    executed_at: date
    target_filename: str
    is_compliant: bool
    discrepancies: List[DiscrepancyEntry] = []
