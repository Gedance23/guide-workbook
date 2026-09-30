from datetime import date

import pytest

from app.domain.entities import EmployeeProfile, Severity, StatutoryGuideline
from app.domain.services import PayrollValidationService


def test_standard_age_entitlement_is_four_weeks():
	employee = EmployeeProfile(
		first_name="Alex",
		last_name="Standard",
		date_of_birth=date(1995, 6, 15),
		weekly_hours_target=40,
	)
	guideline = StatutoryGuideline(year=2026)

	discrepancies = PayrollValidationService.verify_holiday_entitlement(
		employee, guideline, configured_weeks=4
	)

	assert discrepancies == []


def test_youth_age_entitlement_is_five_weeks():
	employee = EmployeeProfile(
		first_name="Alex",
		last_name="Youth",
		date_of_birth=date(2007, 6, 15),
		weekly_hours_target=40,
	)
	guideline = StatutoryGuideline(year=2026)

	discrepancies = PayrollValidationService.verify_holiday_entitlement(
		employee, guideline, configured_weeks=5
	)

	assert discrepancies == []


def test_employee_turning_twenty_during_guideline_year_requires_five_weeks():
	employee = EmployeeProfile(
		first_name="Alex",
		last_name="TurningTwenty",
		date_of_birth=date(2006, 6, 15),
		weekly_hours_target=40,
	)
	guideline = StatutoryGuideline(year=2026)

	discrepancies = PayrollValidationService.verify_holiday_entitlement(
		employee, guideline, configured_weeks=4
	)

	assert len(discrepancies) == 1
	assert discrepancies[0].severity == Severity.ERROR
	assert "at least 5 weeks" in discrepancies[0].message


def test_employee_turning_fifty_during_guideline_year_requires_five_weeks():
	employee = EmployeeProfile(
		first_name="Alex",
		last_name="TurningFifty",
		date_of_birth=date(1976, 6, 15),
		weekly_hours_target=40,
	)
	guideline = StatutoryGuideline(year=2026)

	discrepancies = PayrollValidationService.verify_holiday_entitlement(
		employee, guideline, configured_weeks=4
	)

	assert len(discrepancies) == 1
	assert discrepancies[0].severity == Severity.ERROR


@pytest.mark.parametrize(
	("hours_worked", "holiday_hours_worked"),
	[(8, 8), (7, 8)],
)
def test_holiday_hours_not_strictly_below_total_hours_triggers_warning(
	hours_worked, holiday_hours_worked
):
	discrepancies = PayrollValidationService.verify_holiday_hours_double_entry(
		month_name="January",
		hours_worked=hours_worked,
		holiday_hours_worked=holiday_hours_worked,
	)

	assert len(discrepancies) == 1
	assert discrepancies[0].severity == Severity.WARNING
	assert discrepancies[0].sheet_name == "January Payslip"
	assert discrepancies[0].rule_violated == "Double-Entry Base Wage Invariant"
	assert "base wage" in discrepancies[0].message.lower()
	assert "B8" in discrepancies[0].message