# Task 6 repair results

## Beginner explanation

Raw columns were kept untouched. New `_clean` columns hold actual repaired values, and each repaired field has a `*_was_repaired` provenance flag. The target column was not used to choose any repair.

## Evidence before repair

### Age crosstab

All 320 rows with `Age = 0` occur in `AgeOfPolicyHolder = 16 to 17`. Therefore `Age_clean = 16.5`, the midpoint of that band. This is an estimate, not an invented claim that the exact age is known.

| AgeOfPolicyHolder | Age zero rows |
|---|---:|
| 16 to 17 | 320 |

### Make values checked

The complete Make count is saved in `reports/label_similarity_variants.csv`. `Mecedes` (4), `Nisson` (30), and `Porche` (5) use the fixed map. `Accura` (472) remains unchanged because it may be a source label; `VW` (283) is an abbreviation rather than a proven error.

### PolicyType x VehicleCategory x BasePolicy conclusion

The 4,987 mismatches are exactly the systematic combination `PolicyType = Sedan - Liability`, `VehicleCategory = Sport`, and `BasePolicy = Liability`. This is about 32.3% of the file, so it is treated as a source-defined pattern, not a repair. `PolicyType` is redundant for modelling.

## Before/after evidence

| Repair | Strategy | Before | After | Summary measure | Before summary | After summary |
|---|---|---:|---:|---|---:|---:|
| DayOfWeekClaimed sentinel | treat missing as its own value | 1 | repaired to Unknown | zero sentinel values | 1 | 0 |
| MonthClaimed sentinel | treat missing as its own value | 1 | repaired to Unknown | zero sentinel values | 1 | 0 |
| Age zero sentinel | estimate from the matching age band | 320 | repaired to 16.5 | Age zero values remaining | 320 | 0 |
| Make spelling variants | eliminate known spelling errors with a fixed map | 39 | repaired with fixed map | confirmed spelling variants remaining | 39 | 0 |
| PolicyType and VehicleCategory pattern | flagged, unchanged | 4987 | flagged, unchanged | mismatch rows | 4987 | flagged, unchanged |

## Lecture 2 category count

Three genuine Lecture 2 fault categories remain: **sentinel value**, **inconsistent encoding**, and **outlier**. The policy/vehicle combination is not counted as a fault because the crosstab shows it is systematic and source-defined. Blank, duplicate, and invalid-value checks remain passed checks.
