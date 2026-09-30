from datetime import date
from unittest.mock import Mock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.entities import AuditReport, DiscrepancyEntry, Severity
from app.infrastructure.persistence import database
from app.infrastructure.persistence.database import save_audit_report
from app.infrastructure.persistence.sqlalchemy_models import Base, DBAuditReport, DBSeverity


def test_save_audit_report_persists_report_and_discrepancies():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session_factory()
    domain_report = AuditReport(
        executed_at=date(2026, 9, 29),
        target_filename="payroll.xlsx",
        is_compliant=False,
        discrepancies=[
            DiscrepancyEntry(
                sheet_name="January Payslip",
                cell_coordinate="B8",
                rule_violated="Double-Entry Base Wage Invariant",
                severity=Severity.WARNING,
                message="Holiday hours exceed total hours.",
            )
        ],
    )

    try:
        saved_report = save_audit_report(db, domain_report)

        assert saved_report.id is not None
        assert saved_report.target_filename == domain_report.target_filename
        assert saved_report.is_compliant is False
        assert len(saved_report.discrepancies) == 1
        assert saved_report.discrepancies[0].severity == DBSeverity.WARNING
        assert saved_report.discrepancies[0].sheet_name == "January Payslip"
        assert db.query(DBAuditReport).count() == 1
    finally:
        db.close()


def test_get_db_yields_session_and_closes_it(monkeypatch):
    db = Mock()
    session_factory = Mock(return_value=db)
    monkeypatch.setattr(database, "SessionLocal", session_factory)

    db_generator = database.get_db()

    assert next(db_generator) is db

    db_generator.close()

    db.close.assert_called_once_with()