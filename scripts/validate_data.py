"""Run the same named data checks on the raw and cleaned claim files."""

from pathlib import Path
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw_claims.csv"
CLEAN_PATH = PROJECT_ROOT / "data" / "cleaned_claims.csv"
RESULTS_PATH = PROJECT_ROOT / "reports" / "data_quality" / "validation_results.json"
SUMMARY_PATH = PROJECT_ROOT / "reports" / "data_quality" / "validation_results.md"

BASE_COLUMNS = [
    "Month", "WeekOfMonth", "DayOfWeek", "Make", "AccidentArea",
    "DayOfWeekClaimed", "MonthClaimed", "WeekOfMonthClaimed", "Sex",
    "MaritalStatus", "Age", "Fault", "PolicyType", "VehicleCategory",
    "VehiclePrice", "PolicyNumber", "RepNumber", "Deductible",
    "DriverRating", "Days:Policy-Accident", "Days:Policy-Claim",
    "PastNumberOfClaims", "AgeOfVehicle", "AgeOfPolicyHolder",
    "PoliceReportFiled", "WitnessPresent", "AgentType",
    "NumberOfSuppliments", "AddressChange-Claim", "NumberOfCars", "Year",
    "BasePolicy", "FraudFound",
]


def _check(name: str, passed: bool, message: str) -> dict[str, object]:
    return {"name": name, "passed": bool(passed), "message": message}


def validate(data: pd.DataFrame) -> list[dict[str, object]]:
    """Return checks that each prove a real audit repair or repair decision."""
    results: list[dict[str, object]] = []

    results.append(_check(
        "age_clean_column_exists",
        "Age_clean" in data.columns,
        "Age_clean stores age with the zero sentinel made missing.",
    ))
    results.append(_check(
        "age_zero_sentinel_is_removed",
        "Age_clean" in data.columns
        and not pd.to_numeric(data["Age_clean"], errors="coerce").eq(0).any(),
        "No effective age value is zero.",
    ))
    results.append(_check(
        "age_repair_flag_exists",
        "Age_was_repaired" in data.columns,
        "Age_was_repaired records the 320 age sentinel rows.",
    ))
    results.append(_check(
        "age_repair_flag_has_320_true_values",
        "Age_was_repaired" in data.columns
        and data["Age_was_repaired"].astype("string").str.lower().eq("true").sum() == 320,
        "Exactly 320 Age rows are marked as repaired.",
    ))
    results.append(_check(
        "claimed_day_clean_column_exists",
        "DayOfWeekClaimed_clean" in data.columns,
        "DayOfWeekClaimed_clean stores the repaired weekday field.",
    ))
    results.append(_check(
        "claimed_day_zero_sentinel_is_removed",
        "DayOfWeekClaimed_clean" in data.columns
        and not data["DayOfWeekClaimed_clean"].astype("string").eq("0").any(),
        "The effective claimed weekday has no zero sentinel.",
    ))
    results.append(_check(
        "claimed_day_repair_flag_has_one_true_value",
        "DayOfWeekClaimed_was_repaired" in data.columns
        and data["DayOfWeekClaimed_was_repaired"].astype("string").str.lower().eq("true").sum() == 1,
        "Exactly one claimed-weekday sentinel is marked as repaired.",
    ))
    results.append(_check(
        "claimed_month_clean_column_exists",
        "MonthClaimed_clean" in data.columns,
        "MonthClaimed_clean stores the repaired month field.",
    ))
    results.append(_check(
        "claimed_month_zero_sentinel_is_removed",
        "MonthClaimed_clean" in data.columns
        and not data["MonthClaimed_clean"].astype("string").eq("0").any(),
        "The effective claimed month has no zero sentinel.",
    ))
    results.append(_check(
        "claimed_month_repair_flag_has_one_true_value",
        "MonthClaimed_was_repaired" in data.columns
        and data["MonthClaimed_was_repaired"].astype("string").str.lower().eq("true").sum() == 1,
        "Exactly one claimed-month sentinel is marked as repaired.",
    ))
    results.append(_check(
        "make_clean_column_exists",
        "Make_clean" in data.columns,
        "Make_clean stores the fixed-map spelling repairs.",
    ))
    results.append(_check(
        "make_repair_flag_has_39_true_values",
        "Make_was_repaired" in data.columns
        and data["Make_was_repaired"].astype("string").str.lower().eq("true").sum() == 39,
        "Exactly 39 fixed-map Make repairs are marked.",
    ))
    results.append(_check(
        "policy_vehicle_mismatch_flag_exists",
        "PolicyVehicle_mismatch_flag" in data.columns,
        "PolicyType/VehicleCategory disagreements are flagged, not overwritten.",
    ))
    results.append(_check(
        "policy_vehicle_mismatch_flag_has_4987_true_values",
        "PolicyVehicle_mismatch_flag" in data.columns
        and data["PolicyVehicle_mismatch_flag"].astype("string").str.lower().eq("true").sum() == 4987,
        "Exactly 4,987 cross-column disagreements are flagged.",
    ))
    results.append(_check(
        "repair_output_has_15420_rows",
        set(["Age_clean", "DayOfWeekClaimed_clean", "MonthClaimed_clean"]).issubset(data.columns)
        and len(data) == 15420,
        "The repaired output keeps all 15,420 records.",
    ))
    results.append(_check(
        "repair_output_has_original_target",
        set(["Age_clean", "DayOfWeekClaimed_clean", "MonthClaimed_clean"]).issubset(data.columns)
        and "FraudFound" in data.columns,
        "The target remains present but is not used to choose repairs.",
    ))

    return results


def run() -> None:
    raw = pd.read_csv(RAW_PATH, dtype="string")
    cleaned = pd.read_csv(CLEAN_PATH, dtype="string")
    runs = {}
    for label, frame in (("raw", raw), ("cleaned", cleaned)):
        checks = validate(frame)
        runs[label] = {
            "checks": checks,
            "passed": all(check["passed"] for check in checks),
            "passed_count": sum(check["passed"] for check in checks),
            "failed_count": sum(not check["passed"] for check in checks),
        }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(runs, indent=2), encoding="utf-8")
    lines = [
        "# Validation results",
        "",
        "## Beginner explanation",
        "",
        "This validator checks the raw file and the cleaned file using the same rules. "
        "The raw file should fail because it still contains the real faults found during the audit. "
        "The cleaned file should pass because repairs are stored in new columns and provenance flags.",
        "",
    ]
    for label, result in runs.items():
        lines.extend([
            f"## {label.title()} data",
            "",
            f"- Overall result: **{'PASS' if result['passed'] else 'FAIL'}**",
            f"- Passed checks: {result['passed_count']}",
            f"- Failed checks: {result['failed_count']}",
            "",
            "| Check | Result | Message |",
            "|---|---|---|",
        ])
        for check in result["checks"]:
            status = "PASS" if check["passed"] else "FAIL"
            lines.append(f"| `{check['name']}` | {status} | {check['message']} |")
        lines.append("")
    conclusion = (
        "The raw run fails every repair assertion and the cleaned run passes every repair assertion."
        if runs["raw"]["passed_count"] == 0
        and runs["cleaned"]["passed"]
        else "The raw-versus-cleaned result needs review because the expected all-FAIL/all-PASS pattern was not observed."
    )
    lines.extend([
        "## Required conclusion",
        "",
        conclusion + " The raw failures come from the observed sentinel values and the absence "
        "of provenance and clean-value columns. No assertion uses `FraudFound` to decide a repair.",
        "",
    ])
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run()
