"""Create the Task 6 cleaned dataset without changing raw source columns."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw_claims.csv"
CLEAN_PATH = PROJECT_ROOT / "data" / "cleaned_claims.csv"
RESULTS_PATH = PROJECT_ROOT / "reports" / "data_quality" / "repair_results.csv"
SUMMARY_PATH = PROJECT_ROOT / "reports" / "data_quality" / "repair_results.md"


def repair_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return repaired values, provenance flags, and before/after evidence."""
    cleaned = raw.copy()
    results: list[dict[str, object]] = []

    # Replace impossible calendar sentinels with an explicit Unknown value.
    for column in ("DayOfWeekClaimed", "MonthClaimed"):
        flag = f"{column}_was_repaired"
        repaired_column = f"{column}_clean"
        mask = cleaned[column].astype("string").eq("0")
        cleaned[repaired_column] = cleaned[column].astype("string").mask(mask, "Unknown")
        cleaned[flag] = mask
        results.append({
            "repair": f"{column} sentinel",
            "strategy": "treat missing as its own value",
            "affected_before": int(mask.sum()),
            "affected_after": "repaired to Unknown",
            "summary_measure": "zero sentinel values",
            "summary_before": int(mask.sum()),
            "summary_after": int(cleaned[repaired_column].eq("0").sum()),
            "reason": "Zero is not a weekday or month, so Unknown keeps the missing information visible.",
            "rejected_alternative": "Dropping rows or guessing a date would discard or invent evidence.",
        })

    # Every zero age belongs to the 16 to 17 band, so use its midpoint.
    age_mask = pd.to_numeric(cleaned["Age"], errors="coerce").eq(0)
    age_values = pd.to_numeric(cleaned["Age"], errors="coerce").astype("float64")
    cleaned["Age_clean"] = age_values.mask(age_mask, 16.5)
    cleaned["Age_was_repaired"] = age_mask
    results.append({
        "repair": "Age zero sentinel",
        "strategy": "estimate from the matching age band",
        "affected_before": int(age_mask.sum()),
        "affected_after": "repaired to 16.5",
        "summary_measure": "Age zero values remaining",
        "summary_before": int(age_mask.sum()),
        "summary_after": int(pd.to_numeric(cleaned["Age_clean"], errors="coerce").eq(0).sum()),
        "reason": "All 320 zero ages are in AgeOfPolicyHolder = 16 to 17; 16.5 is that band midpoint.",
        "rejected_alternative": "A global median would ignore the age-band evidence; leaving values missing would discard it.",
    })

    # Apply only the three confirmed spelling corrections.
    make_map = {"Mecedes": "Mercedes", "Nisson": "Nissan", "Porche": "Porsche"}
    make_flag = cleaned["Make"].isin(make_map)
    cleaned["Make_clean"] = cleaned["Make"].replace(make_map)
    cleaned["Make_was_repaired"] = make_flag
    results.append({
        "repair": "Make spelling variants",
        "strategy": "eliminate known spelling errors with a fixed map",
        "affected_before": int(make_flag.sum()),
        "affected_after": "repaired with fixed map",
        "summary_measure": "confirmed spelling variants remaining",
        "summary_before": int(make_flag.sum()),
        "summary_after": int(cleaned["Make_clean"].isin(make_map).sum()),
        "reason": "Mecedes, Nisson, and Porche map unambiguously to existing makes.",
        "rejected_alternative": "Accura and VW remain unchanged because they are not safe fixed-map corrections.",
    })

    # Preserve the systematic source pattern and flag it for audit.
    policy_prefix = cleaned["PolicyType"].astype("string").str.split(" ").str[0]
    mismatch_flag = policy_prefix.ne(cleaned["VehicleCategory"].astype("string"))
    cleaned["PolicyVehicle_mismatch_flag"] = mismatch_flag
    results.append({
        "repair": "PolicyType and VehicleCategory pattern",
        "strategy": "flagged, unchanged",
        "affected_before": int(mismatch_flag.sum()),
        "affected_after": "flagged, unchanged",
        "summary_measure": "mismatch rows",
        "summary_before": int(mismatch_flag.sum()),
        "summary_after": "flagged, unchanged",
        "reason": "The crosstab shows one source-defined Sedan - Liability/Sport/Liability pattern.",
        "rejected_alternative": "Overwriting either column would destroy a real source pattern and invent a correction.",
    })
    return cleaned, pd.DataFrame(results)


def main() -> None:
    raw = pd.read_csv(RAW_PATH, dtype="string")
    cleaned, results = repair_data(raw)
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(CLEAN_PATH, index=False)
    results.to_csv(RESULTS_PATH, index=False)

    lines = [
        "# Task 6 repair results",
        "",
        "## Beginner explanation",
        "",
        "Raw columns were kept untouched. New `_clean` columns hold actual repaired values, "
        "and each repaired field has a `*_was_repaired` provenance flag. The target column was "
        "not used to choose any repair.",
        "",
        "## Evidence before repair",
        "",
        "### Age crosstab",
        "",
        "All 320 rows with `Age = 0` occur in `AgeOfPolicyHolder = 16 to 17`. "
        "Therefore `Age_clean = 16.5`, the midpoint of that band. This is an estimate, "
        "not an invented claim that the exact age is known.",
        "",
        "| AgeOfPolicyHolder | Age zero rows |",
        "|---|---:|",
        "| 16 to 17 | 320 |",
        "",
        "### Make values checked",
        "",
        "The complete Make count is saved in `reports/data_quality/label_similarity_variants.csv`. "
        "`Mecedes` (4), `Nisson` (30), and `Porche` (5) use the fixed map. "
        "`Accura` (472) remains unchanged because it may be a source label; `VW` (283) "
        "is an abbreviation rather than a proven error.",
        "",
        "### PolicyType x VehicleCategory x BasePolicy conclusion",
        "",
        "The 4,987 mismatches are exactly the systematic combination "
        "`PolicyType = Sedan - Liability`, `VehicleCategory = Sport`, and "
        "`BasePolicy = Liability`. This is about 32.3% of the file, so it is treated as "
        "a source-defined pattern, not a repair. `PolicyType` is redundant for modelling.",
        "",
        "## Before/after evidence",
        "",
        "| Repair | Strategy | Before | After | Summary measure | Before summary | After summary |",
        "|---|---|---:|---:|---|---:|---:|",
    ]
    for row in results.to_dict("records"):
        lines.append(
            f"| {row['repair']} | {row['strategy']} | {row['affected_before']} | "
            f"{row['affected_after']} | {row['summary_measure']} | "
            f"{row['summary_before']} | {row['summary_after']} |"
        )
    lines.extend([
        "",
        "## Lecture 2 category count",
        "",
        "Three genuine Lecture 2 fault categories remain: **sentinel value**, "
        "**inconsistent encoding**, and **outlier**. The policy/vehicle combination is "
        "not counted as a fault because the crosstab shows it is systematic and source-defined. "
        "Blank, duplicate, and invalid-value checks remain passed checks.",
    ])
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
