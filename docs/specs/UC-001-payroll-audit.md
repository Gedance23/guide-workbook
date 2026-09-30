# Executable Specification: UC-001 - Run Payroll Audit

## 1. Intent & Business Value
**Intent:** Provide an automated enterprise validation engine to audit an uploaded housekeeper Excel workbook (`Payslip_2026.xlsx`) against Basel-Stadt statutory rules (`NAV Haushalt BS 215.700`) and the companion contract guide.
**Value:** Prevents silent underpayments and ensures the employer complies with regulatory limits before submitting simplified tax declarations.

## 2. Actors & Preconditions
- **Primary Actor:** Household Employer / Compliance Auditor
- **Preconditions:**
  - The system has access to the active Basel-Stadt statutory targets for the 2026 calendar year.
  - The user has provided a valid, uncorrupted Excel `.xlsx` payroll workbook matching the standard monthly calculation tab layout.

## 3. Scope Boundaries
- **IN:** Ingesting monthly spreadsheet metrics via Pandas, verifying public holiday additive premiums, validating global household salary caps, verifying age-tiered holiday allocations based on employee date of birth.
- **OUT:** Modifying or writing data back into the user's Excel file, calculating custom currencies outside of CHF, processing automated tax filing transmissions.

## 4. Normal Flow
1. **Upload:** The actor submits the target spreadsheet file through the interface.
2. **Ingestion:** The infrastructure parser extracts parameters from the `Rates` configuration tab and individual monthly tracking sheets (`Jan Payslip` through `Dec Payslip`).
3. **Mapping:** The data is transformed into pure domain entities.
4. **Evaluation:** The domain validation service executes compliance checks against statutory invariants.
5. **Reporting:** The system constructs a comprehensive `AuditReport` containing all generated `DiscrepancyEntry` records.

## 5. Explicit Acceptance Criteria (AC)
- **AC-1 (Public Holiday Double-Entry Rule):** 
  - **Given** an ingested monthly tab contains public holiday hours worked (`B12 > 0`).
  - **When** the sheet is evaluated.
  - **Then** the system must assert that those exact hours are also included in the general hours worked cell (`B8`). 
  - **Missing Rule Behavior:** If `B8` does not include `B12` hours, generate a `Warning` discrepancy mapping to the affected month, indicating that base wages are silently omitted.

- **AC-2 (Household Cumulative Payroll Cap):**
  - **Given** one or multiple employee workbooks are processed for the employer.
  - **When** the system totals the combined gross annual payroll across all sheets.
  - **Then** it must check if the sum exceeds the simplified procedure ceiling of **CHF 60,480**.
  - **Breach Behavior:** If the total exceeds CHF 60,480, append an `Error` discrepancy entry alerting that the employer is ineligible for the simplified procedure.

- **AC-3 (Age-Tiered Vacation Weeks Allocation):**
  - **Given** an employee profile with an active date of birth.
  - **When** the employee is ≤ 20 or ≥ 50 years old on the calculation boundary date.
  - **Then** the configuration cell `Rates!B15` must equal **5 weeks**. For all other ages, it defaults to **4 weeks**.
  - **Mismatch Behavior:** If the cell value does not match the age tier requirement, append an `Error` discrepancy highlighting a breach of § 28 Abs. 1 NAV.

## 6. Target Test Intent
- **Unit Layer (Domain):** Validate the edge-case age tiering equations using fixed test birthdates (e.g., exactly on their 20th or 50th birthdays) independent of Pandas or file parsers.
- **Integration Layer (Infrastructure):** Inject an isolated mock Excel sheet where `B12 = 2` and `B8 = 0` to verify that the Pandas ingestion mechanism catches coordinate violations and bubbles up the correct discrepancy state.
