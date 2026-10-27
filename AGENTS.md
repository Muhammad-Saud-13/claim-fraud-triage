 # Permanent project rules

These rules apply to every later change in Project 15, **Insurance Claim Fraud Triage**.

## Beginner-first explanations

- Write simple code with short comments on every meaningful step.
- Put a Markdown explanation immediately before every code block in notebooks, reports, and documentation. Each explanation must say:
  - what the code does;
  - why the step is needed; and
  - what the output means.
- Explain each technical term in simple words the first time it appears. For example, define “precision” as the share of claims flagged as fraud that really are fraud.
- Keep names, tables, charts, and messages understandable to a claims adjuster and to a complete beginner preparing for a viva.

## Reproducibility and files

- Use relative paths only, such as `data/carclaims.csv`; never use absolute paths in code, configuration, or instructions.
- The shipped dataset must be inside the project and the application must not depend on a student’s machine.
- Every library used must be added to `requirements.txt` immediately when it is first used.
- The app must start on a clean machine with one documented command. The exact command and clean-machine steps must be in `README.md`.
- Do not write project code until the task plan has been completed and checked.
- Do not add notebooks, generated outputs, or secrets unless they are required deliverables.

## Dataset and leakage discipline

- The supplied dataset is `carclaims.csv` (15,420 rows, 33 columns). Later documentation and code must use the real column names, including names containing `:` and `-`.
- Treat `FraudFound` as the binary target (`No`/`Yes`) unless the data audit proves otherwise. It is the investigation outcome and must never be an input feature.
- Investigate every column for whether it would be known when an adjuster first asks for triage. A field recorded after investigation, adjudication, payment, or a fraud decision must not be a feature.
- The dataset appears to have no separate obvious post-investigation field besides the target. Do not invent one: document the provenance finding, ask the team to confirm it, and use an explicitly justified leakage proxy only if the audit identifies one.
- Prove leakage with an experiment that reports the same evaluation metrics using the suspected leaked field and again without it. The honest production model must exclude it. The comparison must not leak test information into training.
- Keep identifiers such as `PolicyNumber` out of predictive features unless a documented, reproducible reason proves they are legitimate explanatory attributes; normally use them only to identify a case in the interface.
- Never use the target or any post-investigation field during cleaning, feature selection, scaling, resampling, tuning, explanation, or batch scoring.

## Data quality and preprocessing

- Complete Stage A’s data dictionary for every column: measurement type, plausible range or allowed values, and role (identifier, explanatory attribute, target, or must-not-use).
- Complete Stage B with at least six distinct Lecture 2 fault categories. For each category record the detection expression and affected-record count.
- Every repaired field needs a provenance column. Include a numeric before-and-after repair table.
- Implement `validate()` with at least ten assertions. It must fail on raw data and pass on cleaned data; show both results.
- Decide and justify rescaling separately for each model family.
- Compare dimensionality reduction and feature subset selection on the same model and same split. Do not claim a comparison from unrelated runs.
- Discretize or bin only where a chosen model needs it, and document why the bins were selected.

## Models, evaluation, and threshold

- Train at least three classifiers from three different allowed families: decision tree, rule-based, nearest neighbour, naïve Bayes, or neural network.
- Include a decision tree or rule set so the product can explain itself.
- Choose hyperparameters using a stated repeatable procedure, not by trying values until a result looks good.
- Use a train/test split that matches real use. If a reliable date exists, split by time and explicitly justify the choice; otherwise document why a stratified split is appropriate.
- Report the majority-class baseline beside **every** accuracy value. The current raw baseline is approximately 94.0% (`No`: 14,497/15,420); recompute it for each evaluation subset.
- Report at least two metrics beyond accuracy and explain why they suit fraud triage, for example precision, recall, F1, balanced accuracy, or PR-AUC.
- Show a ROC curve and AUC. Explain AUC as how well the model ranks positive cases above negative cases across thresholds.
- Define a cost matrix for missed fraud and unnecessary investigation. Choose the operating threshold from expected cost, never automatically from `0.5`, and show the consequence of changing it.
- Use k-fold cross-validation on the training portion only and report both mean and spread (for example mean ± standard deviation).
- Keep the test set untouched until final comparison.

## Explanations, ethics, and user experience

- Every prediction shown in the app must include a plain-language reason. Use a decision path, rule, similar training claims, or understandable contributing attributes.
- Never show model jargon such as “node 14, gini 0.31” as the user’s reason.
- The product is decision support, not an automatic rejection tool. Show a clear warning that this is a student project and is **not for financial or legal use**.
- Include Project 15’s harm statement: a false fraud flag can delay or wrongly investigate a genuine claimant; a missed fraud case can increase losses and make honest customers bear costs. Explain interface mitigations such as human review, visible reasons, adjustable cost-based threshold, confidence/uncertainty, no automatic claim denial, and an audit trail for the adjuster’s decision.
- Protect privacy: use only the public/anonymised dataset and never place an identifiable real person’s record in the demo.

## Required application surfaces

The web app must have all six screens:

1. **Data & quality:** load data, show the audit report, and let the user download the cleaned file.
2. **Model performance:** compare the three models, show ROC/AUC and confusion matrix, and place the majority baseline beside every accuracy figure.
3. **Single prediction:** accept one case and show prediction, confidence, and explanation.
4. **Batch scoring:** accept a CSV, produce a ranked/filterable table, and allow downloading results.
5. **Settings:** choose model, move threshold, edit cost matrix, and update consequences live.
6. **Case-file:** show one claim’s indicators, comparable past claims found by the model, and record the adjuster’s decision against the recommendation.

The triage output must rank claims by fraud indicators and give a recommendation such as pay, review, or investigate. Do not present the model as the final legal or financial decision-maker.

