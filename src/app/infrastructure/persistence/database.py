from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.domain.entities import AuditReport
from app.infrastructure.persistence.sqlalchemy_models import (
	DBDiscrepancyEntry,
	DBAuditReport,
	DBSeverity,
)


DATABASE_URL = "sqlite:///./payalign.db"

engine = create_engine(
	DATABASE_URL,
	connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def save_audit_report(db: Session, domain_report: AuditReport) -> DBAuditReport:
	db_report = DBAuditReport(
		executed_at=domain_report.executed_at,
		target_filename=domain_report.target_filename,
		is_compliant=domain_report.is_compliant,
		discrepancies=[
			DBDiscrepancyEntry(
				sheet_name=discrepancy.sheet_name,
				cell_coordinate=discrepancy.cell_coordinate,
				rule_violated=discrepancy.rule_violated,
				severity=DBSeverity(discrepancy.severity.value),
				message=discrepancy.message,
			)
			for discrepancy in domain_report.discrepancies
		],
	)
	db.add(db_report)
	db.commit()
	db.refresh(db_report)
	return db_report
