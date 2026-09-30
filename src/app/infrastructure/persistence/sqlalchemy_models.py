from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()

class DBSeverity(enum.Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"

class DBEmployeeProfile(Base):
    __tablename__ = "employee_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    weekly_hours_target = Column(Float, nullable=False)

class DBStatutoryGuideline(Base):
    __tablename__ = "statutory_guidelines"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, unique=True, nullable=False)
    holiday_premium_rate = Column(Float, default=0.5)
    simplified_procedure_individual_cap = Column(Float, default=22680.0)
    simplified_procedure_employer_cap = Column(Float, default=60480.0)
    nbu_weekly_hours_threshold = Column(Float, default=8.0)

class DBPayrollPeriod(Base):
    __tablename__ = "payroll_periods"
    
    id = Column(Integer, primary_key=True, index=True)
    month_name = Column(String, nullable=False)
    calendar_year = Column(Integer, nullable=False)

class DBAuditReport(Base):
    __tablename__ = "audit_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    executed_at = Column(Date, nullable=False)
    target_filename = Column(String, nullable=False)
    is_compliant = Column(Boolean, default=True)
    
    discrepancies = relationship("DBDiscrepancyEntry", back_populates="report", cascade="all, delete-orphan")

class DBDiscrepancyEntry(Base):
    __tablename__ = "discrepancy_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("audit_reports.id"), nullable=False)
    sheet_name = Column(String, nullable=False)
    cell_coordinate = Column(String, nullable=False)
    rule_violated = Column(String, nullable=False)
    severity = Column(SQLEnum(DBSeverity), nullable=False)
    message = Column(String, nullable=False)
    
    report = relationship("DBAuditReport", back_populates="discrepancies")
