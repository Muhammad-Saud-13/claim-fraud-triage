# Validation results

## Beginner explanation

This validator checks the raw file and the cleaned file using the same rules. The raw file should fail because it still contains the real faults found during the audit. The cleaned file should pass because repairs are stored in new columns and provenance flags.

## Raw data

- Overall result: **FAIL**
- Passed checks: 0
- Failed checks: 16

| Check | Result | Message |
|---|---|---|
| `age_clean_column_exists` | FAIL | Age_clean stores age with the zero sentinel made missing. |
| `age_zero_sentinel_is_removed` | FAIL | No effective age value is zero. |
| `age_repair_flag_exists` | FAIL | Age_was_repaired records the 320 age sentinel rows. |
| `age_repair_flag_has_320_true_values` | FAIL | Exactly 320 Age rows are marked as repaired. |
| `claimed_day_clean_column_exists` | FAIL | DayOfWeekClaimed_clean stores the repaired weekday field. |
| `claimed_day_zero_sentinel_is_removed` | FAIL | The effective claimed weekday has no zero sentinel. |
| `claimed_day_repair_flag_has_one_true_value` | FAIL | Exactly one claimed-weekday sentinel is marked as repaired. |
| `claimed_month_clean_column_exists` | FAIL | MonthClaimed_clean stores the repaired month field. |
| `claimed_month_zero_sentinel_is_removed` | FAIL | The effective claimed month has no zero sentinel. |
| `claimed_month_repair_flag_has_one_true_value` | FAIL | Exactly one claimed-month sentinel is marked as repaired. |
| `make_clean_column_exists` | FAIL | Make_clean stores the fixed-map spelling repairs. |
| `make_repair_flag_has_39_true_values` | FAIL | Exactly 39 fixed-map Make repairs are marked. |
| `policy_vehicle_mismatch_flag_exists` | FAIL | PolicyType/VehicleCategory disagreements are flagged, not overwritten. |
| `policy_vehicle_mismatch_flag_has_4987_true_values` | FAIL | Exactly 4,987 cross-column disagreements are flagged. |
| `repair_output_has_15420_rows` | FAIL | The repaired output keeps all 15,420 records. |
| `repair_output_has_original_target` | FAIL | The target remains present but is not used to choose repairs. |

## Cleaned data

- Overall result: **PASS**
- Passed checks: 16
- Failed checks: 0

| Check | Result | Message |
|---|---|---|
| `age_clean_column_exists` | PASS | Age_clean stores age with the zero sentinel made missing. |
| `age_zero_sentinel_is_removed` | PASS | No effective age value is zero. |
| `age_repair_flag_exists` | PASS | Age_was_repaired records the 320 age sentinel rows. |
| `age_repair_flag_has_320_true_values` | PASS | Exactly 320 Age rows are marked as repaired. |
| `claimed_day_clean_column_exists` | PASS | DayOfWeekClaimed_clean stores the repaired weekday field. |
| `claimed_day_zero_sentinel_is_removed` | PASS | The effective claimed weekday has no zero sentinel. |
| `claimed_day_repair_flag_has_one_true_value` | PASS | Exactly one claimed-weekday sentinel is marked as repaired. |
| `claimed_month_clean_column_exists` | PASS | MonthClaimed_clean stores the repaired month field. |
| `claimed_month_zero_sentinel_is_removed` | PASS | The effective claimed month has no zero sentinel. |
| `claimed_month_repair_flag_has_one_true_value` | PASS | Exactly one claimed-month sentinel is marked as repaired. |
| `make_clean_column_exists` | PASS | Make_clean stores the fixed-map spelling repairs. |
| `make_repair_flag_has_39_true_values` | PASS | Exactly 39 fixed-map Make repairs are marked. |
| `policy_vehicle_mismatch_flag_exists` | PASS | PolicyType/VehicleCategory disagreements are flagged, not overwritten. |
| `policy_vehicle_mismatch_flag_has_4987_true_values` | PASS | Exactly 4,987 cross-column disagreements are flagged. |
| `repair_output_has_15420_rows` | PASS | The repaired output keeps all 15,420 records. |
| `repair_output_has_original_target` | PASS | The target remains present but is not used to choose repairs. |

## Required conclusion

The raw run fails every repair assertion and the cleaned run passes every repair assertion. The raw failures come from the observed sentinel values and the absence of provenance and clean-value columns. No assertion uses `FraudFound` to decide a repair.
