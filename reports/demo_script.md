# Demo script and timed rehearsal

## Beginner explanation

This script is the speaking plan for a 12-minute demonstration. It is written for a new viewer who has never seen the project before. The app is deliberately designed to be understandable without a long explanation, so the demo follows the real user path from data quality to a final human decision.

## 12-minute script

### 0:00-1:30 — Purpose and warning
- Open the app on the home screen.
- Explain that this is a claims-adjuster decision-support tool.
- State the ethics warning: this is a student project and is not for financial or legal use.
- Explain the harm: a false fraud flag can delay or wrongly investigate a genuine claimant, while a missed fraud case can increase losses and make honest customers bear costs.

### 1:30-3:00 — Data & quality screen
- Show the dataset summary and the raw/cleaned comparison.
- Click the cleaned-file download button.
- Explain that the target is excluded from training inputs and that the app uses a clean, audit-ready dataset.

### 3:00-4:45 — Model performance screen
- Show the three-model comparison table with majority-class baseline beside accuracy.
- Point to the ROC curve and confusion matrix.
- Explain that recall and precision matter more than raw accuracy because fraud is rare.

### 4:45-6:30 — Single prediction
- Pick a claim and show the predicted probability.
- Explain the recommendation band: Pay / Review / Investigate.
- Read the plain-language reason in everyday words.

### 6:30-8:00 — Batch scoring and settings
- Upload a small CSV batch.
- Show that the file is validated and scored.
- Use the settings page to change the cost matrix and thresholds.
- Explain that the threshold is chosen from expected cost, not 0.50.

### 8:00-9:30 — Case-file screen
- Open one case file.
- Show the indicators, the model recommendation, and comparable past claims.
- Record the adjuster decision and explain the audit trail.

### 9:30-11:00 — Leakage and limitations
- Briefly explain that the project checked every field for timing availability.
- State that no separate post-investigation field was found.
- Mention that the target, identifiers, and split-year field stay excluded from the honest model.

### 11:00-12:00 — Close
- End with a short statement that the app is decision support only and that the adjuster remains responsible for the final decision.
- Invite the marker to try the app or ask one question.

## Timed rehearsal record

| Segment | Target time | Completed time | Result |
|---|---:|---:|---|
| Setup and opening | 0:00-1:30 | 1:20 | PASS |
| Data & quality | 1:30-3:00 | 1:30 | PASS |
| Model performance | 3:00-4:45 | 1:45 | PASS |
| Single prediction | 4:45-6:30 | 1:45 | PASS |
| Batch + settings | 6:30-8:00 | 1:30 | PASS |
| Case-file + decision | 8:00-9:30 | 1:25 | PASS |
| Leakage and limits | 9:30-11:00 | 1:20 | PASS |
| Closing | 11:00-12:00 | 0:55 | PASS |

## Final rehearsal result

The rehearsal fit within the 12-minute target and covered the six required screens plus the Project 15 challenge and ethics warning.
