# Model-team handover

## What is complete

The data team completed the raw audit, repairs, validation, leakage review, and
modelling handover for Project 15: Insurance Claim Fraud Triage.

The canonical cleaned dataset is `data/cleaned_claims.csv`. It keeps the original
columns and adds repaired values and provenance flags. The model feature table is
`data/modeling_claims.csv`; it has 28 approved input columns and does not contain
`FraudFound`, `PolicyNumber`, or `Year`. The separate
`data/modeling_labels.csv` file contains `PolicyNumber`, `Year`, and `FraudFound`
for splitting, training labels, evaluation, and case identification only.

## Evidence to read first

1. `AGENTS.md` — permanent project rules and marking constraints.
2. `TASKS.md` — the numbered implementation checklist.
3. `DECISIONS.md` — approved model, split, cost, threshold, and application choices.
4. `reports/data_quality/repair_results.md` — actual repairs and provenance.
5. `reports/data_quality/validation_results.md` — raw-versus-cleaned assertions.
6. `reports/data_quality/leakage_provenance.md` — field timing and exclusions.
7. `reports/modeling/modelling_split.md` — frozen chronological split.
8. `config/feature_policy.json` — the enforced feature policy.
9. `reports/modeling/preprocessing_comparison.md` — representation comparison.

## Current preprocessing decision

`data/modeling_claims.csv` is a clean feature handover, not a scaled numeric
matrix. The pipelines in `scripts/build_preprocessing.py` perform training-fold-only
imputation, one-hot encoding, and numeric scaling. No binning is used because the
selected decision tree, k-nearest neighbours, and Gaussian Naive Bayes models do
not require arbitrary bins; this decision must be documented in the final model
report.

## Start here: Task 10

Implement Task 10 end to end:

1. Read the files listed above before writing model code.
2. Use 1994 and 1995 for training and keep 1996 untouched until final comparison.
3. Train and tune a decision tree, k-nearest neighbours model, and Gaussian Naive Bayes.
4. Use declared parameter grids and five-fold stratified cross-validation on training rows only.
5. Use the same feature policy and comparable preprocessing for all three models.
6. Save trained model and preprocessing artifacts under `models/`.
7. Write `reports/modeling/hyperparameter_results.csv` and
   `reports/modeling/model_comparison.csv`.
8. Report accuracy beside the matching majority baseline every time, plus precision,
   recall, F1, ROC/AUC, confusion matrices, and cross-validation mean ± standard deviation.
9. Select the operating threshold from the expected-cost matrix, not automatically from 0.5.
10. Update `TASKS.md` only after the outputs exist and have been checked.

## Required modelling safety rules

- Never use `FraudFound` as a feature.
- Never fit imputation, encoding, scaling, feature selection, or tuning using test rows.
- Never use `PolicyNumber`, `RepNumber`, or `Year` as model inputs.
- Preserve plain-language explanations for the decision-tree model.
- Keep the model as decision support; it must not automatically deny a claim.
