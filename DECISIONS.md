# Project 15 decisions

This file records the choices that the implementation must follow. Each choice says what we selected, why it is suitable, and what reasonable alternative we did not select. The explanations use simple words so every team member can repeat them in the viva.

## 1. Application framework

- **Chosen:** Streamlit.
- **Why:** Streamlit lets us build a web application from Python with a small amount of beginner-friendly code. It supports forms, tables, charts, file uploads, downloads, and interactive controls without requiring a separate front end.
- **Alternative:** Gradio, Flask, or Django. Gradio is also simple, but Streamlit is better suited to six connected screens, tables, settings, and live charts. Flask and Django give more control but require more web code than this three-day project needs.
- **Implementation consequence:** The app will start with one documented command, `streamlit run app.py`, and `streamlit` must be listed in `requirements.txt`.

## 2. Dataset and target

- **Chosen:** Ship the supplied `carclaims.csv` inside the project and use `FraudFound` as the binary target. `No` means the historical record was not marked fraudulent and `Yes` means it was marked fraudulent.
- **Why:** The file has 15,420 rows and 33 columns, which meets the brief. The target has 14,497 `No` records and 923 `Yes` records, so fraud is a small minority (about 6.0%).
- **Alternative:** Build a synthetic register. We will not do that because the public dataset already meets the size requirement and does not require us to invent a fraud mechanism.
- **Implementation consequence:** `FraudFound` is never an input feature, and the raw majority-class accuracy baseline is 14,497 / 15,420, about 94.0%.

## 3. Chronological train/test split

- **Chosen:** Train on `Year` 1994 and 1995; test once on `Year` 1996.
- **Why:** The dataset contains exactly three years: 1994 (6,142 claims), 1995 (5,195 claims), and 1996 (4,083 claims). A chronological split imitates the real use case: learn from earlier claims and triage later claims. The 1996 test set remains untouched until final evaluation.
- **Alternative:** A random stratified split. It would preserve the fraud percentage, but it could mix later claims into training and earlier claims into testing, which is less realistic when time is available.
- **Caution:** `Year` is used to create the split, not as a model feature. `Year` is excluded from production features because it is a calendar field in this historical sample and could act as a proxy for collection period rather than claim evidence.

## 4. Cross-validation

- **Chosen:** 5-fold stratified cross-validation on the 1994–1995 training portion only.
- **Why:** Five folds means the training data is divided into five parts. Each part is used once for validation while the other four are used for learning. “Stratified” means each fold keeps a similar fraud/non-fraud ratio, which is important because fraud is rare. We will report the mean and standard deviation, not only the mean.
- **Alternative:** Ordinary k-fold validation or a different value of k. Ordinary folds might contain very different numbers of fraud cases; 5 folds gives a useful balance between stable estimates and reasonable run time.

## 5. Model families

- **Chosen:** Decision tree, k-nearest neighbours (kNN), and naïve Bayes.
- **Why:** They are three different allowed families. The decision tree can explain a result using understandable rules. kNN compares a claim with similar training claims. Naïve Bayes estimates the probability using each feature while making a simple independence assumption. Together they provide three distinct approaches.
- **Alternative:** Rule-based classifier or neural network. A rule set could also explain results, but the decision tree already satisfies the explainability requirement. A neural network is less transparent and is not necessary for this small tabular product.
- **Implementation consequence:** All three models receive the same training/test rows and the same honest feature policy.

## 6. Hyperparameter tuning

- **Chosen:** Grid search on the training data only, with 5-fold stratified cross-validation inside the grid search.
- **Why:** A grid search tries a declared set of parameter combinations systematically. Using only the training years prevents the 1996 test year from influencing model choices. The final comparison uses the untouched 1996 test set only once.
- **Alternative:** Manual trial-and-error or tuning on the test set. Those alternatives can make the test result look better than the model really is and would violate honest evaluation.

## 7. Extra evaluation metrics

- **Chosen:** Recall and precision, in addition to accuracy.
- **Why:** Recall answers “of all historical fraud cases, how many did we flag for investigation?” Missing fraud is costly. Precision answers “of the claims we flagged, how many were actually fraud?” Low precision would send too many genuine claimants into unnecessary investigation. Accuracy alone is misleading because always predicting `No` already gives about 94.0% on the raw data.
- **Alternative:** F1, balanced accuracy, or PR-AUC. These are useful possible additions, but recall and precision directly explain the two harms the adjuster must balance and satisfy the brief’s requirement for two additional metrics.

## 8. Costs and editable cost matrix

- **Chosen initial costs:**
  - Missed fraud (false negative): **100,000**
  - Unnecessary investigation of a genuine claim (false positive): **5,000**
  - Correct decisions: **0** in the simple operating matrix
- **Why:** Missing organized fraud is assumed to be much more expensive than reviewing a genuine claim. The ratio is 20 to 1, which reflects the Project 15 problem while remaining editable by the user.
- **Alternative:** Equal costs or costs chosen only to maximize accuracy. Equal costs would ignore the stated business harm; accuracy optimization would usually favor the majority class and miss fraud.
- **Implementation consequence:** The Settings screen will allow both costs to be edited and will show a sensitivity table with several cost settings, expected total cost, recall, precision, and the number of claims sent for investigation.

## 9. Three recommendation bands and two thresholds

- **Chosen:** Use two probability thresholds:
  - probability `< 0.20`: **Pay**
  - probability `0.20` to `< 0.60`: **Review**
  - probability `>= 0.60`: **Investigate**
- **Why:** Predicted probability is the model’s estimated chance that the claim belongs to the fraud class. Three bands are more useful to an adjuster than a single yes/no label: low risk can be paid, uncertain cases can receive human review, and high-risk cases can be investigated. The initial 0.20 and 0.60 values are clear starting points; final operating values must also be checked against the validation cost table.
- **Alternative:** One threshold at 0.50. That would force a binary action and would ignore the different levels of uncertainty and workload.
- **Implementation consequence:** Both thresholds are editable in Settings. The app must show how changing them changes pay/review/investigate counts, recall, precision, and estimated cost. The final fraud flag threshold must be justified using the cost matrix rather than assumed to be 0.50.

## 10. Confidence

- **Chosen:** Use the selected model’s predicted probability for the fraud class as confidence, and display it as a percentage with a plain-language caution.
- **Why:** A predicted probability gives a consistent numeric indication of how strongly the model favors fraud. It is easy to display and compare with the two thresholds.
- **Alternative:** A model-specific score or an uncalibrated margin. Those values are harder for a beginner and adjuster to interpret consistently.
- **Caution:** Probability is model confidence, not proof that a claim is fraudulent. The interface must retain the human-review warning.

## 11. Comparable past claims

- **Chosen:** Show the **five most similar past claims** in the case-file screen.
- **Why:** Five examples provide context without overwhelming the adjuster. Similarity will use the kNN/preprocessed feature representation and will exclude the target, identifiers, and any post-investigation field.
- **Alternative:** Show one example or every similar claim. One example is too fragile, while every example creates an unreadable screen and may expose unnecessary records.
- **Implementation consequence:** If fewer than five valid comparable training claims exist, the app must say how many were found instead of pretending there are five.

## 12. Leakage and field-timing decision

- **Chosen:** Do not invent a leaked column. Inspect every column for whether it is known at claim time, mark identifiers and outcomes as must-not-use, and run a single-column predictive check.
- **Why:** The supplied file contains `FraudFound` as the outcome and no separately named obvious post-investigation field. It would be dishonest to label an ordinary claim field as post-investigation just to create a dramatic result.
- **Field-timing result:** The claim description, incident timing, policy, vehicle, claimant, report, witness, agent, supplement, address-change, and other claim attributes are treated as available at or before initial triage unless source documentation proves otherwise. `FraudFound` is recorded after the outcome and is the target, so it is never a feature. `PolicyNumber` is an identifier, not evidence, and is must-not-use. `Year` is used only for the chronological split and is also excluded from features. `RepNumber` is treated as an identifier-like representative code and excluded unless later provenance proves it is a legitimate claim-time explanatory attribute.
- **Single-column predictive check performed:** For every non-target column, learn the majority target within each value using 1994–1995 and evaluate on 1996. Every column achieved the 1996 majority baseline of **94.78% accuracy, 0.00% precision, and 0.00% recall** under this intentionally simple one-column check. `PolicyNumber` and `Year` had unseen 1996 values in this check and therefore defaulted to the training majority.
- **What this means:** This check found no single column that acts as an obvious perfect leak. It is not proof that the fields have no useful combined signal; it only says that no one field alone exposed the target under this honest temporal test. The full model comparison will still exclude the target, identifiers, and fields that cannot be known at claim time.
- **Alternative:** Invent or force a leakage field. Rejected because it would make the evidence false and would teach the wrong data-mining practice.
- **Implementation consequence:** Produce `reports/data_quality/leakage_provenance.md` and `reports/data_quality/single_column_predictive_check.csv`, include the same metrics with and without any legitimately identified suspect field, and report “no separate leak identified” if that remains the result.

## 13. Ethics and product position

- **Chosen:** Present the app as student decision support, never as an automatic claim denial or legal/financial decision.
- **Why:** A false fraud flag can delay or wrongly investigate an honest claimant; a missed fraud case can increase losses and shift costs to honest customers. Reasons, comparable claims, editable costs, uncertainty, and an adjuster decision record reduce the risk but do not remove it.
- **Alternative:** Let the model automatically reject or pay claims. Rejected because the brief requires a product for an adjuster and the model cannot establish legal fraud.
- **Implementation consequence:** Every relevant screen visibly states: “Student project — not for financial or legal use.” The case-file stores the adjuster’s decision separately from the model recommendation.

## 14. Required dependency and startup decision

- **Chosen:** Use a `requirements.txt` file and document one startup command.
- **Why:** A clean machine must not depend on hidden packages or paths. Every imported library is added immediately.
- **Alternative:** Depend on a preconfigured laptop or an undocumented environment. Rejected because it fails the product requirement.
- **Implementation consequence:** The README will document installation, `streamlit run app.py`, relative dataset loading, expected URL, and the other-machine test.

## 15. Data handover preprocessing decision

- **Chosen:** Use the repaired values for `Age`, `DayOfWeekClaimed`, and `MonthClaimed`; impute missing numeric values with a median learned inside each training fold; one-hot encode categorical fields; scale numeric fields for distance-based models; and keep ordinal text bands as categorical until a model-specific mapping is justified.
- **Why:** This keeps the safe repairs in the modelling table without guessing an age. Training-only imputation prevents information from the 1996 test set entering training. One-hot encoding prevents category names from being treated as numbers. Scaling is important for kNN distances, while it is not needed by a decision tree.
- **Representation comparison:** The same decision tree, chronological split, five stratified training folds, and untouched test set were used for the full encoded representation, PCA, and SelectKBest. The comparison reports accuracy, precision, and recall with cross-validation mean and spread.
- **Alternative:** Fill age using the whole dataset, encode all categories as arbitrary integers, or choose PCA from a separate split. Rejected because these choices can leak test information or invent false numeric order.
- **Implementation consequence:** The model handover consists of `data/modeling_claims.csv`, `reports/modeling/modelling_split.md`, `reports/modeling/modelling_split.json`, `reports/modeling/preprocessing_comparison.csv`, `reports/modeling/preprocessing_comparison.md`, and `models/preprocessing_artifacts.pkl`.
