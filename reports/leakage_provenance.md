# Leakage and field-timing report

## Purpose

The Project 15 challenge is leakage under extreme imbalance. **Leakage** means that information from after the decision is accidentally given to a model as if it were available before the decision. This can make a model look accurate while making it unusable in real triage.

The supplied file has 15,420 rows and 33 columns. The historical outcome is `FraudFound`: `No` for 14,497 records and `Yes` for 923 records. `FraudFound` is therefore the target, not an input. The file has no separately named obvious post-investigation result field. No leaked column has been invented.

## Timing review

The following review uses the column names, values, the supplied project brief, and the data dictionary. The original source documentation describing the exact collection workflow was not included in the workspace, so fields with uncertain timing are explicitly marked rather than silently assumed.

| Column(s) | Timing decision | Model decision | Reason |
|---|---|---|---|
| `Month`, `WeekOfMonth`, `DayOfWeek`, `Make`, `AccidentArea` | Claim/incident description | Available feature | These describe the event or vehicle information in the supplied record. |
| `DayOfWeekClaimed`, `MonthClaimed`, `WeekOfMonthClaimed` | Claim timing fields; special `0` values need cleaning | Candidate feature after quality repair | They may be known when a claim is submitted; unknown `0` is not treated as a normal category. |
| `Sex`, `MaritalStatus`, `Age`, `AgeOfPolicyHolder` | Claimant/policy information | Candidate feature after quality and fairness review | These are supplied claimant attributes, but their use must be reviewed for unfair effects. |
| `Fault`, `PolicyType`, `VehicleCategory`, `VehiclePrice`, `BasePolicy` | Policy/claim classification | Candidate feature | These describe the claim or policy. |
| `PolicyNumber` | Identifier | Must-not-use | It identifies a record and should not be treated as fraud evidence. |
| `RepNumber` | Identifier-like representative code | Must-not-use initially | It may encode process or representative identity rather than claim evidence. It remains excluded unless provenance proves legitimate and fair use. |
| `Deductible`, `DriverRating` | Policy/rating information | Candidate feature | Supplied claim-time numeric or ordered fields. |
| `Days:Policy-Accident`, `Days:Policy-Claim` | Time bands in the claim record | Candidate feature after cleaning | They describe timing relationships; the colon is part of the source name. |
| `PastNumberOfClaims` | Historical policy/claim information | Candidate feature | It can be available from policy records, subject to the source workflow. |
| `AgeOfVehicle`, `NumberOfCars`, `AddressChange-Claim` | Vehicle/household history | Candidate feature after quality review | These are supplied attributes; ordinal bands must be encoded carefully. |
| `PoliceReportFiled`, `WitnessPresent` | Report and witness information | Candidate feature if known before triage | These can be useful, but the implementation must confirm they are available before the recommendation. |
| `AgentType` | Process/channel information | Candidate feature with bias review | It may be known at intake but can reflect process differences rather than fraud. |
| `NumberOfSuppliments` | Timing uncertain | Exclude if added after first triage; otherwise candidate feature | A supplement may be submitted after the initial claim. The production decision must follow verified timing, not an assumption. |
| `Year` | Calendar field used for evaluation order | Split-only; must-not-use feature | It creates the realistic time split but could let the model learn collection-period effects. |
| `FraudFound` | Historical investigation outcome | Target; must-not-use feature | It is known only after the historical decision and is exactly what the model must predict. |

## Chronological evaluation used for the check

- Training rows: `Year` 1994 and 1995, 11,337 rows.
- Test rows: `Year` 1996, 4,083 rows.
- Test fraud cases: 213.
- Test non-fraud cases: 3,870.
- Test majority-class baseline: 3,870 / 4,083 = **94.7832%**.
- The test set was not used to select a feature or tune a model.

## Single-column predictive check

For every non-target column, the check learned the most common target value for each training value using 1994–1995. It then predicted the 1996 test records. If a value had not appeared in training, the check predicted the training majority class `No`. This is a simple screening check, not the final model.

Results are in [`single_column_predictive_check.csv`](./single_column_predictive_check.csv). All 32 non-target columns produced:

- Accuracy: **94.7832%**
- Test majority baseline: **94.7832%**
- Precision: **0.0000**
- Recall: **0.0000**
- True positives: 0
- False positives: 0
- False negatives: 213
- True negatives: 3,870

`PolicyNumber` and `Year` each had 4,083 unseen 1996 test values under this value-based check. They therefore defaulted to `No`, reinforcing their exclusion for different reasons: `PolicyNumber` is an identifier and `Year` is split-only.

## Honest conclusion

No single column was an obvious predictive leak under the declared chronological single-column check. This does **not** mean that the combined attributes have no predictive signal. It means that the available evidence does not justify naming a separate leaked post-investigation field.

The honest production feature policy is in [`feature_policy.json`](../src/feature_policy.json). It excludes `FraudFound`, `PolicyNumber`, `RepNumber`, and `Year`. It also requires the timing of `NumberOfSuppliments` to be confirmed before final production training. If that field is found to be post-triage, it must be added to the exclusion list and the model must be retrained.

The implementation must never use `FraudFound` for cleaning, imputation, feature selection, scaling, resampling, tuning, explanation, or batch scoring.
