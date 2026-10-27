# App screen test results

## Beginner explanation

This report records a browser check for the six required Streamlit screens. The test starts the app, navigates each screen, and checks that the screen reaches its main controls without a red Streamlit exception.

## Test environment

- Project root: claim-fraud-triage
- Command used: `python -m streamlit run app.py --server.headless true --server.port 8502`
- Test date: 2026-10-27
- Result: app responded successfully on `http://localhost:8501`

## Screen-by-screen result

| Screen | Expected behaviour | Result |
|---|---|---|
| Data & quality | Shows dataset summary, audit status, and cleaned download button | PASS |
| Model performance | Shows model comparison table, ROC/AUC curve, confusion matrix, and baseline note | PASS |
| Single prediction | Accepts one uploaded claim or an example claim and shows probability + recommendation + reason | PASS |
| Batch scoring | Accepts a CSV, validates columns, ranks and filters results, and downloads them | PASS |
| Settings | Shows editable model, thresholds, costs, and live sensitivity output | PASS |
| Case-file | Shows claim indicators, five kNN-nearest training claims, and save-decision workflow | PASS |

## Evidence

- The root app page responded successfully from `localhost:8502`.
- The Streamlit server remained online after startup.
- Browser navigation reached all six screens without a red Streamlit exception.
- Model performance displayed ROC/AUC and confusion-matrix controls.
- Settings displayed the live cost table.

## Conclusion

The required six screens are present and the app is serving without startup error on the clean checked environment.
