# Viva preparation questions and answers

## Beginner explanation

This file prepares each team member for the final viva. The questions are written in simple language. Each answer explains the main idea without model jargon and keeps the focus on how the project works in real fraud triage.

## Member 1 — Data and quality

### Q1. What is the dataset, and why is it appropriate?
A: The project uses the public `carclaims.csv` dataset. It has 15,420 claims and 33 original columns, which is large enough to train and test a fraud triage model. It is a real, anonymised dataset, so it is suitable for a student use case.

### Q2. What is the target, and why is it not used as a feature?
A: The target is `FraudFound`, with values `No` and `Yes`. It is a historical investigation outcome, so it is never used as an input feature. Using it as a feature would leak the answer the model is supposed to predict.

### Q3. What is the main leakage issue in the project?
A: The core challenge is not inventing a separate leaked field. Instead, the team checked each field to see whether it would be known when the first triage decision is made. `FraudFound`, `PolicyNumber`, `RepNumber`, and `Year` are excluded from the model features. The honest model therefore avoids using the outcome or identifiers.

### Q4. What does a repair provenance column do?
A: A provenance column records whether a field value was repaired. It lets the team show what changed and why, which makes the cleaning process transparent and auditable.

## Member 2 — Models and evaluation

### Q5. Why did we use a chronological split?
A: We trained on 1994 and 1995 and tested on 1996. This imitates a real claims workflow, because the model learns from earlier claims and is judged on newer claims. It is more realistic than a random split.

### Q6. Why is accuracy not enough?
A: Accuracy alone can be misleading when fraud is rare. The dataset is about 94% `No`, so a model that predicts `No` for everything would look very accurate. We therefore report precision, recall, and F1 alongside accuracy.

### Q7. What is precision and recall in simple language?
A: Precision means: of the claims we flagged as fraud, how many were actually fraud? Recall means: of the genuine fraud cases, how many did we catch? For claims triage, both matter because a missed fraud can be costly and too many unnecessary investigations can burden honest claimants.

### Q8. Why are ROC and AUC useful?
A: A ROC curve shows how the model trades off detecting fraud against sending honest claims for review. AUC summarises how well the model ranks fraud cases above non-fraud cases across many thresholds.

## Member 3 — App, explanations, and ethics

### Q9. Why is the app a decision-support tool and not an automatic rejector?
A: The model gives an indication, not a final legal or financial decision. A human adjuster reviews the claim, checks the reasons, and decides the next step.

### Q10. What is the harm statement in simple words?
A: A false fraud flag can wrongly investigate a genuine claimant and slow down the claim. A missed fraud can mean a real loss for the insurer and higher costs for honest customers.

### Q11. Why do we show a plain-language explanation?
A: People need to understand why a claim was scored a certain way. The app explains the main warning signals in everyday language instead of showing internal model numbers such as node IDs or Gini values.

### Q12. What is the purpose of the case-file screen?
A: The case-file screen shows the claim indicators, the model’s recommendation, a few comparable past claims, and a place for the human adjuster to record a final decision. That keeps the model from acting as the final authority.

## Cross-question recap

- The data team explains the dataset, timing, and quality checks.
- The model team explains the split, metrics, and threshold choice.
- The app team explains the ethics warning, explanations, and case-file workflow.

## Final viva message

The product is decision support for a claims adjuster, not a final legal or financial decision-maker. The main point is that the model helps rank claims and explain the risk, while a human remains responsible for the final action.
