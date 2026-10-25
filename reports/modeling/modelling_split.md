# Modelling split

## Beginner explanation

The model learns from older claims and is tested on later claims. This is a chronological split, meaning time decides the boundary. The 1996 claims are kept untouched while preprocessing choices are made.

| Item | Value |
|---|---|
| Training years | 1994 and 1995 (11337 rows) |
| Test year | 1996 (4083 rows) |
| Training fraud cases | 710 |
| Test fraud cases | 213 |
| Target encoding | No = 0, Yes = 1 |
| Validation | 5-fold stratified CV on training rows only, random state 42 |
| Test rule | Test rows are not used for fitting, imputation, encoding, selection, or tuning |

## Excluded columns

`FraudFound`, `PolicyNumber`, `RepNumber`, and `Year` are not model features. `Year` creates the split but is not given to the model. `PolicyNumber` is kept only for case identification and audit traceability.

## Feature handover

`data/modeling_claims.csv` contains only the 28 approved feature columns. It does not contain `FraudFound`, `PolicyNumber`, or `Year`, so the target and identifiers cannot accidentally be supplied as model inputs. The matching `data/modeling_labels.csv` file stores the target and split metadata separately for training, evaluation, and case identification. The model receives the 28 columns listed in `config/feature_policy.json`. Safe repaired values replace `Age`, `DayOfWeekClaimed`, and `MonthClaimed`. Unknown age values remain missing until the training-only median imputer runs inside each pipeline.
