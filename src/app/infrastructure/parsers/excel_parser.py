import pandas as pd
from datetime import date
from typing import List
from app.domain.entities import EmployeeProfile, StatutoryGuideline, DiscrepancyEntry, AuditReport
from app.domain.services import PayrollValidationService

class ExcelPayrollParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.excel_file = pd.ExcelFile(file_path)

    def parse_and_audit(self, employee: EmployeeProfile, guideline: StatutoryGuideline) -> AuditReport:
        all_discrepancies: List[DiscrepancyEntry] = []
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        try:
            rates_df = pd.read_excel(self.excel_file, sheet_name="Rates", header=None)
            configured_weeks = int(rates_df.iloc[14, 1])
            weeks_discrepancies = PayrollValidationService.verify_holiday_entitlement(
                employee, guideline, configured_weeks
            )
            all_discrepancies.extend(weeks_discrepancies)
        except Exception:
            pass

        for month in months:
            sheet_name = f"{month} Payslip"
            if sheet_name in self.excel_file.sheet_names:
                try:
                    df = pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None)
                    hours_worked = float(df.iloc[7, 1])
                    holiday_hours = float(df.iloc[11, 1])
                    
                    monthly_discrepancies = PayrollValidationService.verify_holiday_hours_double_entry(
                        month, hours_worked, holiday_hours
                    )
                    all_discrepancies.extend(monthly_discrepancies)
                except Exception:
                    pass

        is_compliant = len([d for d in all_discrepancies if d.severity == "ERROR"]) == 0

        return AuditReport(
            executed_at=date.today(),
            target_filename=self.file_path.split("/")[-1],
            is_compliant=is_compliant,
            discrepancies=all_discrepancies
        )
