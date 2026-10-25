# Project 15 implementation tasks — Insurance Claim Fraud Triage

This is the implementation task list for the project. The implementation agent must read this file, complete each task end to end, and produce the stated real project artifact or working feature. A task is not complete when a design or plan is written; it is complete only when its output exists, is exercised, and passes the stated check. The owners are the three team roles: **data**, **models**, and **app**. When a task has two owners, the first owner is accountable and the second provides the required input.

## Dataset facts to carry forward

- File supplied: `carclaims.csv`.
- Observed shape: 15,420 records × 33 columns.
- Apparent target: `FraudFound`, values `No` and `Yes`.
- Observed target counts: `No` = 14,497; `Yes` = 923; raw majority baseline = 14,497 / 15,420 ≈ 94.0%; fraud prevalence ≈ 6.0%.
- Observed raw missing-value count: zero in every column.
- Columns: `Month`, `WeekOfMonth`, `DayOfWeek`, `Make`, `AccidentArea`, `DayOfWeekClaimed`, `MonthClaimed`, `WeekOfMonthClaimed`, `Sex`, `MaritalStatus`, `Age`, `Fault`, `PolicyType`, `VehicleCategory`, `VehiclePrice`, `PolicyNumber`, `RepNumber`, `Deductible`, `DriverRating`, `Days:Policy-Accident`, `Days:Policy-Claim`, `PastNumberOfClaims`, `AgeOfVehicle`, `AgeOfPolicyHolder`, `PoliceReportFiled`, `WitnessPresent`, `AgentType`, `NumberOfSuppliments`, `AddressChange-Claim`, `NumberOfCars`, `Year`, `BasePolicy`, `FraudFound`.
- The file mixes categorical/text fields, integer-looking fields, and binary/ordinal-like fields. Confirm measurement types rather than assuming that every numeric-looking field is continuous.

## Numbered tasks

### 1. Confirm scope, roles, and repository rules

- **Status:** COMPLETE — implementation folders and `requirements.txt` created; scope checked against the brief and `AGENTS.md`.
- **Goal:** Lock Project 15 and prevent scope drift.
- **Exact steps:** Read the common specification and Project 15 brief. Confirm the user is a claims adjuster, the task is binary fraud-investigation triage, the output ranks claims with indicators and recommends pay/review/investigate, and the assigned challenge is leakage under extreme imbalance. Read `AGENTS.md`. Create the implementation folders and dependency manifest needed by later tasks, but do not skip directly to a later phase.
- **Input:** `DSC306_Data_Mining_Semester_Projects.md`, `AGENTS.md`, `carclaims.csv`.
- **Output file:** Project folder structure and `requirements.txt`.
- **How to check:** Every Stage A–G item, six screens, ethics, README, other-machine test, and viva task appears below.
- **Marks affected:** All components; prevents missing-scope penalties.
- **Owner:** data.

### 2. Create the complete data dictionary (Stage A)

- **Status:** COMPLETE — `reports/data_dictionary.md` documents all 33 columns using the observed schema and values.
- **Goal:** Document every real column and its role at the time of triage.
- **Exact steps:** For all 33 columns, record measurement type (nominal, ordinal, interval, or ratio where justified), allowed values or plausible range, missing/special values, and role. Specifically assess `PolicyNumber` as identifier; treat `FraudFound` as target; assess `Year`, `Month`, `DayOfWeek`, `MonthClaimed`, `WeekOfMonthClaimed`, `Fault`, `PoliceReportFiled`, `WitnessPresent`, and all other fields for whether they are explanatory and available at first triage. Do not silently treat `0` as a normal category.
- **Input:** `carclaims.csv` and dataset facts above.
- **Output file:** `reports/data_dictionary.md`.
- **How to check:** It has 33 entries, uses exact names, states a role for each, and has no unexplained field.
- **Marks affected:** A–B / 15.
- **Owner:** data.

### 3. Establish field-timing and leakage provenance (Project 15 challenge)

- **Status:** COMPLETE — `reports/leakage_provenance.md`, `reports/single_column_predictive_check.csv`, and `src/feature_policy.json` were produced and verified against all 33 columns.
- **Goal:** Identify what is known before investigation and prove what must not be used.
- **Exact steps:** Trace the dataset documentation/source if available. Inspect every real column for whether it is known when the adjuster first asks for triage. Mark `FraudFound` (outcome), `PolicyNumber` (identifier), `Year` (split-only calendar field), and `RepNumber` (identifier-like code unless provenance proves otherwise) as must-not-use. Do not invent a post-investigation field. Run the single-column majority-value predictive check using 1994–1995 as training and 1996 as test for every non-target column. Report accuracy, majority baseline, precision, recall, and unseen test values.
- **Input:** source metadata, `carclaims.csv`, data dictionary, `DECISIONS.md`.
- **Output file:** `reports/leakage_provenance.md`, `reports/single_column_predictive_check.csv`, and the implemented feature-exclusion configuration used by training and prediction.
- **How to check:** The report has a field-by-field timing table, a final excluded-feature list, the single-column results for every column, and an honest statement if no separate leak is identified.
- **Marks affected:** Stage A (15), assigned challenge (10), evaluation honesty (20).
- **Owner:** data.

### 4. Write the harm and mitigation statement

- **Status:** COMPLETE — `reports/ethics_harm_statement.md` and `src/ethics_content.json` contain the harm statement, visible warning, and all required interface mitigations.
- **Goal:** Meet the Project 15 ethics requirement before building a user interface.
- **Exact steps:** State that a false fraud flag can delay or wrongly investigate a genuine claimant, while missed fraud can increase losses and shift costs to honest customers. State that the system is student decision support, not an automatic denial or legal/financial decision. Specify mitigations: human adjuster decision, visible reasons and comparable cases, adjustable cost-based threshold, uncertainty/confidence, audit trail, no identifiable real-person demo records, and a warning on screen.
- **Input:** Project 15 ethics requirement and intended workflow.
- **Output file:** `reports/ethics_harm_statement.md` and the visible warning/mitigation text used by the application.
- **How to check:** Both harm directions and each interface mitigation are present; the exact warning “student project, not for financial or legal use” is included for reuse in the app.
- **Marks affected:** Ethics requirement, Stage G / 20, demo/viva / 10.
- **Owner:** app (data reviews).

### 5. Run the raw-data quality audit with six fault categories (Stage B)

- **Status:** COMPLETE — re-audited with the requested Lecture 2 vocabulary; `reports/raw_profile.csv`, `reports/raw_quality_audit_lecture2.csv`, `reports/raw_quality_audit_lecture2.md`, `reports/label_similarity_variants.csv`, and `src/audit_raw_data.ps1` contain the executed profile and audit evidence.
- **Goal:** Find at least six genuine faults using Lecture 2 vocabulary.
- **Exact steps:** Define detection expressions and counts for at least six distinct categories, such as missing values, special/unknown `0` values, invalid ranges (for example impossible `Age`), inconsistent category spelling/casing, inconsistent category combinations, duplicate records or duplicate identifiers, and outliers/impossible values. Do not claim a category without evidence. Include checks for all exact columns, including colon/hyphen names.
- **Input:** raw `carclaims.csv`, data dictionary.
- **Output file:** `reports/raw_quality_audit_lecture2.md` and `reports/raw_quality_audit_lecture2.csv`.
- **How to check:** At least six categories each have an expression, affected-record count, example values, and a decision to repair, retain, or document.
- **Marks affected:** Stage A–B / 15.
- **Owner:** data.

### 6. Apply repairs and provenance columns (Stage B)

- **Status:** COMPLETE — revised repairs create `Make_clean` with a fixed map, estimate all zero ages from their single age band, preserve the systematic policy pattern, and record one provenance flag per repaired field.
- **Goal:** Make cleaning traceable and defensible.
- **Exact steps:** For each approved repair, define the rule, replacement method, and why it is safe. Add one provenance indicator per repaired field (for example `<field>_was_repaired`), preserve the raw source, and avoid target-based imputation. Define how duplicate records/IDs and special values are handled. Produce a numeric before/after table with rows changed, missing/special values, invalid values, duplicates, and final rows/columns.
- **Input:** quality-audit findings.
- **Output file:** `data/cleaned_claims.csv`, with provenance columns, and `reports/repair_results.csv` plus `reports/repair_results.md`.
- **How to check:** Every repair has a before count, after count, rule, provenance field, and reproducible test.
- **Marks affected:** Stage A–B / 15.
- **Owner:** data.

### 7. Implement `validate()` and raw-versus-clean evidence (Stage B)

- **Status:** COMPLETE — `src/validate_data.py` ran 16 repair-focused assertions on both files; raw data failed all 16 and cleaned data passed all 16. Results are saved in `reports/validation_results.json` and `reports/validation_results.md`.
- **Goal:** Prove data quality rather than only describing it.
- **Exact steps:** Implement at least ten repair-focused assertions tied directly to the audited faults: sentinel removal, explicit missing treatment, spelling-variant flags, cross-column mismatch flags, provenance counts, preserved row count, and retained target column. Run the same validator against raw data and cleaned data. Every assertion must fail on raw data and pass on cleaned data.
- **Input:** raw data and completed repair results.
- **Output file:** Implemented `validate()` function, `reports/validation_results.json`, and `reports/validation_results.md`.
- **How to check:** There are 10+ named repair assertions; the raw run has 0 passes and the cleaned run has 0 failures.
- **Marks affected:** Stage A–B / 15.
- **Owner:** data.

### 8. Build the honest modelling table and freeze the evaluation split (Stages C/E)

- **Status:** COMPLETE — `src/build_preprocessing.py` created `data/modeling_claims.csv`, froze the 1994–1995 training and 1996 test split, saved split identifiers/metadata, and documented the excluded feature list.
- **Goal:** Prevent leakage and make the evaluation reflect actual use.
- **Exact steps:** Define target encoding for `FraudFound`; exclude `FraudFound`, `PolicyNumber`, `Year`, `RepNumber` unless later provenance proves legitimate use, and every post-investigation field. Use the chosen chronological split: 1994 and 1995 for training, 1996 for the untouched test. Freeze the test set before tuning and do not duplicate fraud into the test set.
- **Input:** cleaned data, leakage report, `DECISIONS.md`.
- **Output file:** Implemented preprocessing/split module, saved split identifiers or reproducible split metadata, and `reports/modelling_split.md`.
- **How to check:** The feature list, excluded list, split rule, seed, and untouched-test-set rule are explicit.
- **Marks affected:** Stage C / 10, Stage E / 20, challenge / 10.
- **Owner:** models (data supplies timing evidence).

### 9. Implement scaling, encoding, discretization, and representation comparison (Stage C)

- **Status:** COMPLETE — implemented training-fold-only imputation, one-hot encoding, numeric scaling, saved `models/preprocessing_artifacts.pkl`, and compared full encoded features, PCA, and SelectKBest using the same decision tree, folds, and untouched test set.
- **Goal:** Satisfy preprocessing requirements for all model families.
- **Exact steps:** State rescaling separately for decision tree/rule-based, nearest neighbour, naïve Bayes, and neural network families selected. Define categorical encoding and handling of ordinal fields. Apply discretization/binarization only where a chosen model requires it, with bin boundaries and justification. Compare dimensionality reduction versus feature subset selection on the same model, same training folds, and same test set; pre-specify the comparison metrics and selection procedure.
- **Input:** data dictionary, completed split decisions, selected decision tree, kNN, and naïve Bayes families.
- **Output file:** Implemented preprocessing pipelines, saved preprocessing artifacts, `reports/preprocessing_comparison.csv`, and `reports/preprocessing_comparison.md`.
- **How to check:** A reviewer can reproduce each preprocessing branch without using test data or the target as an input feature.
- **Marks affected:** Stage C / 10.
- **Owner:** models.

### 10. Train and tune three classifier families fairly (Stage D)

- **Goal:** Build the required comparable model set.
- **Exact steps:** Train a decision tree, k-nearest neighbours model, and naïve Bayes model on identical prepared training data and compare them on the identical held-out test set. Use grid search on training data only, with 5-fold stratified cross-validation inside the search. Record the searched parameter grid, selection metric, class-imbalance policy, and tie-breaking rule before final test scoring.
- **Input:** implemented preprocessing pipelines and training split.
- **Output file:** At least three saved trained model artifacts, the shared training code, `reports/hyperparameter_results.csv`, and `reports/model_comparison.csv`.
- **How to check:** Three different families, fair inputs, tuning procedure, and explainable-model requirement are all documented.
- **Marks affected:** Stage D / 15.
- **Owner:** models.

### 11. Run cross-validation and metrics reporting (Stage E)

- **Goal:** Measure performance honestly under extreme imbalance.
- **Exact steps:** Use 5-fold stratified cross-validation on the training portion only. Report mean and standard deviation. Report recall and precision as the two required metrics beyond accuracy, and justify them for missed fraud and unnecessary investigations. For every accuracy in tables, charts, screens, and README, place the majority-class baseline beside it and identify which subset supplies that baseline.
- **Input:** completed split decisions and trained-model configuration.
- **Output file:** `reports/cross_validation_results.csv`, `reports/test_metrics.csv`, and `reports/evaluation_results.md`.
- **How to check:** No accuracy appears without its matching baseline; CV spread is present; metric reasons are written in plain language.
- **Marks affected:** Stage E / 20.
- **Owner:** models.

### 12. Run ROC/AUC and cost-matrix threshold selection (Stages E and Project 15)

- **Goal:** Choose an operational threshold based on consequences, not 0.5.
- **Exact steps:** Start with a missed-fraud cost of 100,000 and unnecessary-investigation cost of 5,000, both editable in Settings. Generate ROC curve and AUC, explaining both simply. Evaluate expected cost over thresholds and choose the operating threshold from the cost matrix rather than 0.5. Use two editable thresholds for Pay (`<0.20`), Review (`0.20` to `<0.60`), and Investigate (`>=0.60`) as the initial three-band defaults, then show the validation cost table and sensitivity table. Record recall, precision, workload, and confusion-matrix consequences.
- **Input:** validation predictions, completed evaluation outputs, harm statement.
- **Output file:** `reports/roc_curve.png`, `reports/confusion_matrix.png`, `reports/cost_threshold_results.csv`, `reports/cost_matrix.md`, and the saved threshold configuration used by the app.
- **How to check:** The selected threshold is numerically tied to the matrix, is not silently 0.5, and its consequences are visible.
- **Marks affected:** Stage E / 20, challenge / 10, Stage G / 20.
- **Owner:** models (app exposes it).

### 13. Run the leakage experiment with and without the suspected field (Project 15)

- **Goal:** Evidence the assigned technical challenge.
- **Exact steps:** Do not invent a leaked field. Use the field-timing table and single-column check for every column. If a genuinely post-investigation field is identified, run the controlled included/excluded experiment using the same split, preprocessing, grid search, metrics, baseline, ROC/AUC, cost-selected threshold, and 5-fold CV; label the included version diagnostic-only. If no separate field is identified, report that honestly, show the complete single-column check, and explain why `FraudFound` cannot be used as a feature.
- **Input:** leakage provenance, frozen split, completed evaluation code and outputs.
- **Output file:** `reports/leakage_experiment.csv`, `reports/leakage_experiment.md`, and an honest production model that excludes the field.
- **How to check:** The report has side-by-side accuracy plus baseline, two additional metrics, AUC, cost-selected threshold, CV mean ± spread, and a clear honest-model decision.
- **Marks affected:** Assigned challenge / 10; Stage E / 20.
- **Owner:** models (data verifies field timing).

### 14. Implement plain-language explanations (Stage F)

- **Goal:** Make every displayed prediction understandable.
- **Exact steps:** Implement a plain-language explanation for every prediction. Use a decision path for the tree, five similar training claims for kNN, and understandable feature comparisons for naïve Bayes where it is selected. Use the predicted fraud probability as confidence, include actual feature labels and values, and ban model jargon in the user-facing sentence.
- **Input:** chosen explainable model and feature names.
- **Output file:** Implemented explanation generator, `reports/explanation_examples.md`, and explanation output included in every prediction result.
- **How to check:** Example outputs exist for pay, review, and investigate; each states a reason and does not say “node”, “gini”, or an unexplained internal number.
- **Marks affected:** Stage F / 10.
- **Owner:** models (app renders).

### 15. Implement and test the six-screen application (Stage G)

- **Goal:** Ensure a stranger can use the complete product unaided.
- **Exact steps:** Implement and manually test: (1) Data & quality showing load/audit/download cleaned file; (2) Model performance showing three-model comparison, ROC/AUC, confusion matrix, and baseline beside every accuracy; (3) Single prediction form with prediction/confidence/reason; (4) Batch scoring CSV upload, ranked/filterable results, download; (5) Settings with model, threshold, cost matrix, live consequences; (6) Case-file showing one claim’s indicators, comparable past claims, and recorded adjuster decision against recommendation.
- **Input:** all completed reports and model artifacts.
- **Output file:** Working application with all six screens and `reports/app_screen_test_results.md`.
- **How to check:** A manual script tests each screen from a clean start and records pass/fail without student narration.
- **Marks affected:** Stage G / 20.
- **Owner:** app.

### 16. Build the case-file workflow and audit trail

- **Goal:** Deliver Project 15’s domain-specific screen safely.
- **Exact steps:** Implement selection of one claim, display of its indicators and prediction reason, retrieval of comparable past claims, recommendation pay/review/investigate, and an adjuster decision field. Record the human decision and timestamp/identifier without overwriting the model output. Show the harm warning and make clear that the adjuster remains responsible.
- **Input:** explanation output, comparable-case implementation, ethics statement.
- **Output file:** Working case-file screen, implemented comparable-claims lookup, implemented adjuster-decision record, and `reports/case_file_test_results.md`.
- **How to check:** A test case shows indicators, at least one comparable result or an explicit “none found”, recommendation, and saved human decision.
- **Marks affected:** Project 15 challenge / 10, Stage G / 20, ethics.
- **Owner:** app.

### 17. Implement batch input/output safeguards

- **Goal:** Make batch scoring useful without silently accepting unsafe data.
- **Exact steps:** Define required columns, allowed values, missing/unknown handling, exclusion of `FraudFound` from user inputs, rejection messages, ranking field, filter fields, recommendation labels, reason text, and download schema. Ensure uploaded data cannot replace the shipped training data or change the final test evaluation.
- **Input:** data dictionary, implemented validation rules, explanation output format.
- **Output file:** Implemented batch validation/scoring/download behavior and `reports/batch_test_results.md`.
- **How to check:** Valid, invalid, empty, and target-containing uploads each have an expected visible outcome.
- **Marks affected:** Stage G / 20 and evaluation honesty / 20.
- **Owner:** app (data reviews).

### 18. Write the README and one-command clean-machine instructions

- **Goal:** Make the product runnable by the marker outside the authors’ machines.
- **Exact steps:** Document purpose/user, ethics warning, dataset provenance and shipping location, environment setup, one documented start command, expected URL, all six screens, feature exclusions/leakage, data-quality evidence, models, metrics with baselines, cost threshold, explanations, limitations, and troubleshooting. Ensure every dependency is in `requirements.txt` and no path editing is required.
- **Input:** completed reports and final dependency list.
- **Output file:** `README.md`, updated `requirements.txt`, and the runnable application entry point.
- **How to check:** A new machine can follow only the README and run the app; the command uses relative paths and the dataset is present in the project.
- **Marks affected:** Stage G / 20, demo/viva / 10.
- **Owner:** app (all members review).

### 19. Run and record the other-machine test

- **Goal:** Verify the clean-machine requirement before freezing.
- **Exact steps:** On a machine or clean environment not used for development, clone/copy the project, install only the documented requirements, run the one documented command, open the app, test all six screens, score one case and a small batch, download outputs, and record any fix. Do not edit paths or install unlisted packages.
- **Input:** final project directory, `README.md`, `requirements.txt`.
- **Output file:** `reports/other_machine_test.md` with the actual test command, results, failures, fixes, and successful rerun.
- **How to check:** Test environment, command, date, screens tested, result, errors, and fixes are recorded; a second run passes.
- **Marks affected:** Stage G / 20, demo/viva / 10.
- **Owner:** app (data/models support diagnosis).

### 20. Assemble and verify the final evidence package

- **Goal:** Preserve proof for marking and viva.
- **Exact steps:** Freeze the data dictionary, six-fault audit, repair before/after table, provenance columns, raw-fail/clean-pass validator result, preprocessing comparison, three-model comparison, CV mean/spread, accuracy baselines, two extra metrics, ROC/AUC, cost matrix/threshold, leakage comparison, explanations, app screenshots or test record, and ethics warning. Remove unneeded generated files and confirm no secrets or absolute paths.
- **Input:** all reports, app, README.
- **Output file:** Complete final project under `data/`, `src/` or equivalent, `models/`, `reports/`, `README.md`, and the working application.
- **How to check:** A marker can trace every mark to an artifact and every artifact to the real dataset columns.
- **Marks affected:** All 100 marks.
- **Owner:** all members; app coordinates.

### 21. Prepare and rehearse the twelve-minute demonstration

- **Goal:** Show a useful product to someone who has never taken the course.
- **Exact steps:** Rehearse: purpose and user; load/audit; cleaned download; model comparison with baselines; single prediction explanation; batch ranking/download; threshold/cost change; case file and human decision; leakage evidence; limitations and ethics warning. Keep the product usable without narration during the marker’s independent test.
- **Input:** final application and evidence package.
- **Output file:** `reports/demo_script.md` and a completed timed rehearsal record.
- **How to check:** Timed rehearsal is at most 12 minutes and includes all six screens and the Project 15 challenge.
- **Marks affected:** Demo/viva / 10 and Stage G / 20.
- **Owner:** app leads; all members present.

### 22. Prepare and rehearse the eight-minute viva

- **Goal:** Ensure each of the three members can explain the part they built.
- **Exact steps:** Prepare simple answers for KDD, four measurement types, each six-fault detection/repair, provenance, leakage timing, train/test choice, imbalance and baseline, metric choices, scaling by family, reduction versus selection, tuning, ROC/AUC, cost threshold, CV spread, explanation reason, case-file harm mitigation, and clean-machine startup. Assign ownership but rehearse cross-questions so no member says only “the model did it”.
- **Input:** all reports and code documentation.
- **Output file:** `reports/viva_questions.md` with each member’s answered preparation questions.
- **How to check:** Each member answers questions about their own component and can explain every technical term in beginner language.
- **Marks affected:** Demo/viva / 10; supports all technical components.
- **Owner:** all members.

## Mark coverage summary

- **Data quality work (Stages A–B): 15:** Tasks 2, 5, 6, 7.
- **Pre-processing (Stage C): 10:** Task 9.
- **Models (Stage D): 15:** Task 10.
- **Evaluation honesty (Stage E): 20:** Tasks 8, 11, 12, 13.
- **Explanation quality (Stage F): 10:** Task 14.
- **Application (Stage G): 20:** Tasks 15–19.
- **Assigned challenge: 10:** Tasks 3, 4, 12, 13, 16.
- **Demo and viva: 10:** Tasks 21–22.

## Three-day checkpoints from the brief

- Saturday evening: data on screen, shape known, exclusions listed, work divided.
- Sunday morning: six fault categories repaired with provenance and `validate()` passes.
- Sunday afternoon: one end-to-end model with accuracy beside baseline.
- Sunday evening: all six screens open, even if some are placeholders.
- Monday morning: three families compared on identical data and justified split.
- Monday afternoon: baseline, metrics, ROC/AUC, cost threshold, and CV spread complete.
- Monday evening: explanations first, then case-file screen.
- Tuesday morning: freeze, README, other-machine test, and viva rehearsal; no new features.
- Tuesday: 12-minute demo, 8-minute viva, all three members present and able to answer.

## Previously unclear items — now resolved

The original brief left these choices open. They are now fixed in [DECISIONS.md](<D:/saud/Data Mining labs/lab_project/DECISIONS.md>) and must not be re-decided during implementation:

1. No separate post-investigation leak will be invented. Every column will be checked for claim-time availability, and the complete single-column predictive check will be reported.
2. The application framework is Streamlit.
3. The initial cost matrix uses 100,000 for missed fraud and 5,000 for unnecessary investigation; both are editable and a sensitivity table is required.
4. The chronological split is 1994–1995 for training and 1996 for the untouched test set.
5. Cross-validation is 5-fold stratified CV on training data only.
6. The three models are decision tree, kNN, and naïve Bayes.
7. Hyperparameters are selected by grid search on training data only.
8. Recall and precision are the required metrics beyond accuracy.
9. Predicted fraud probability is displayed as confidence, with a warning that it is not proof.
10. The case-file screen shows five similar past claims.
11. The initial action bands are Pay below 0.20, Review from 0.20 to below 0.60, and Investigate at 0.60 or above. Both thresholds remain editable and the operating fraud threshold must still be justified by the cost matrix.
