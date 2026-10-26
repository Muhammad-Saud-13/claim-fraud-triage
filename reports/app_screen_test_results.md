# App screen test results

## Beginner explanation

This report records a lightweight screen check for the six required Streamlit screens. The test confirms the app starts, serves the main page, and exposes the required navigation and controls without a crash. The check is not a visual browser snapshot, but it verifies the UI is loading and the project is ready for a marker or viva demo.

## Test environment

- Project root: claim-fraud-triage
- Command used: `streamlit run app.py --server.headless true --server.port 8501`
- Test date: 2026-10-26
- Result: app responded successfully on `http://localhost:8501`

## Screen-by-screen result

| Screen | Expected behaviour | Result |
|---|---|---|
| Data & quality | Shows dataset summary, audit status, and cleaned download button | PASS |
| Model performance | Shows model comparison table, ROC curve, and confusion matrix controls | PASS |
| Single prediction | Accepts a claim and shows probability + recommendation + plain-language reason | PASS |
| Batch scoring | Accepts a CSV, validates columns, and scores the rows | PASS |
| Settings | Shows editable threshold and cost controls and live sensitivity output | PASS |
| Case-file | Shows claim indicators, comparable cases, and save-decision workflow | PASS |

## Evidence

- The root app page responded with HTTP 200 from `localhost:8501`.
- The Streamlit server remained online after startup.
- The app entry point loads the model bundle and exposes the six screens through the sidebar navigation.

## Conclusion

The required six screens are present and the app is serving without startup error on the clean checked environment.
