# Insurance Claim Fraud Triage

This project is a student decision-support application for triaging insurance claims for possible fraud. It is designed for a claims adjuster to review a claim, compare it with past cases, and understand why the model is giving a fraud signal. It is not a legal or financial decision system and it is not meant for production use.

## Project purpose

The app uses the public anonymised `data/carclaims.csv` dataset. The model learns only from the claim-time information that would be available when a claim is first reviewed. It excludes the historical outcome column and identifiers from the feature set, and it keeps a clear audit trail for human review.

## Ethics warning

This is a student project and is not for financial or legal use. A false fraud flag can delay or wrongly investigate a genuine claimant. A missed fraud case can increase losses and make honest customers bear costs. The app therefore shows the recommendation as decision support only, requires a human adjuster to review the outcome, presents reasons for the recommendation, and keeps an audit trail of the human decision.

## Dataset provenance and location

- Dataset: `data/raw_claims.csv`
- Cleaned data: `data/cleaned_claims.csv`
- Model-ready inputs: `data/modeling_claims.csv`
- Labels: `data/modeling_labels.csv`

The shipped dataset is included in the repository so the application works on a clean machine without any path edits.

## Clean-machine setup

1. Clone or copy this repository.
2. Open a terminal in the project root.
3. Create a virtual environment if you want one.
4. Install the dependencies from the project file:

   python -m pip install -r requirements.txt

## One-command start

From the project root, run:

streamlit run app.py

Expected browser URL:

http://localhost:8501

## Screens included

The app includes six screens:

1. Data & quality
2. Model performance
3. Single prediction
4. Batch scoring
5. Settings
6. Case-file

## Leakage and feature policy

The production model excludes:

- `FraudFound`
- `PolicyNumber`
- `RepNumber`
- `Year`

The chronological split is 1994 and 1995 for training and 1996 for the untouched final test set. This protects the evaluation from accidental leakage and matches a realistic claims workflow.

## Data-quality evidence

The project includes the audit evidence in `reports/data_quality/`:

- `data_dictionary.md`
- `raw_quality_audit_lecture2.md`
- `repair_results.md`
- `validation_results.md`
- `leakage_provenance.md`

The raw file fails the validation checks because it contains real quality faults. The cleaned file passes the validation checks and keeps repaired values in provenance columns.

## Model choice and evaluation summary

The project compares three model families:

- Decision tree
- k-nearest neighbours
- Gaussian naïve Bayes

The model comparison is documented in `reports/modeling/model_comparison.csv` and `reports/evaluation_results.md`. All accuracy values are shown with the matching majority-class baseline. Recall and precision are reported because they directly help the adjuster balance missed fraud against unnecessary review.

## Threshold and costs

The default operating costs are:

- missed fraud: 100,000
- unnecessary investigation: 5,000

The threshold is selected from expected cost rather than fixed at 0.5, and the settings screen lets the user adjust the thresholds and cost matrix in real time.

## Explanations and case-file workflow

Every prediction is accompanied by a plain-language reason. The case-file screen shows a claim, the model’s recommendation, comparable past claims, and a place for the human adjuster to record their final decision. The user is always told that the case is decision support only and not final legal or financial action.

## Troubleshooting

- If the browser does not open, make sure the virtual environment is active and that the package install succeeded.
- If port 8501 is already in use, stop the active app or rerun on a free port with a command such as `streamlit run app.py --server.port 8502`.
- If the app cannot find the dataset, run the command from the project root and keep all files in the repository.

## Files to review

- `app.py` — Streamlit app
- `scripts/train_models.py` — model training and report generation
- `reports/modeling/` — comparison and tuning outputs
- `reports/data_quality/` — audit and repair evidence
- `reports/` — evaluation and app test reports
