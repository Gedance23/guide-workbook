from datetime import date
from typing import List
from app.domain.entities import EmployeeProfile, StatutoryGuideline, DiscrepancyEntry, Severity

class PayrollValidationService:
    @staticmethod
    def verify_holiday_entitlement(employee: EmployeeProfile, guideline: StatutoryGuideline, configured_weeks: int) -> List[DiscrepancyEntry]:
        discrepancies = []
        
        year_start = date(guideline.year, 1, 1)
        year_end = date(guideline.year, 12, 31)

        def age_on(reference_date: date) -> int:
            return reference_date.year - employee.date_of_birth.year - (
                (reference_date.month, reference_date.day)
                < (employee.date_of_birth.month, employee.date_of_birth.day)
            )

        age_at_start = age_on(year_start)
        age_at_end = age_on(year_end)
        qualifies_for_five_weeks = age_at_start <= 20 or age_at_end >= 50
        expected_weeks = 5 if qualifies_for_five_weeks else 4
            
        has_invalid_entitlement = (
            configured_weeks < 5
            if qualifies_for_five_weeks
            else configured_weeks != expected_weeks
        )
        if has_invalid_entitlement:
            discrepancies.append(
                DiscrepancyEntry(
                    sheet_name="Rates",
                    cell_coordinate="B15",
                    rule_violated="§ 28 Abs. 1 NAV Haushalt BS",
                    severity=Severity.ERROR,
                    message=(
                        f"Employee age during {guideline.year} ranges from {age_at_start} "
                        f"to {age_at_end}. Statutory entitlement requires at least "
                        f"{expected_weeks} weeks, but sheet config has {configured_weeks} weeks."
                    )
                )
            )
        return discrepancies

    @staticmethod
    def verify_holiday_hours_double_entry(month_name: str, hours_worked: float, holiday_hours_worked: float) -> List[DiscrepancyEntry]:
        discrepancies = []
        # AC-1: Holiday hours must be additive to the normal hours worked.
        if holiday_hours_worked > 0 and hours_worked <= holiday_hours_worked:
            discrepancies.append(
                DiscrepancyEntry(
                    sheet_name=f"{month_name} Payslip",
                    cell_coordinate="B8",
                    rule_violated="Double-Entry Base Wage Invariant",
                    severity=Severity.WARNING,
                    message=(
                        f"Public holiday hours worked ({holiday_hours_worked}h) are not "
                        f"additive to recorded total hours worked ({hours_worked}h). "
                        "Base wage is silently missing from cell B8."
                    )
                )
            )
        return discrepancies
