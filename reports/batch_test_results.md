# Batch input/output safeguards test results

## Beginner explanation

This report checks the batch uploader in the app. It makes sure the uploader rejects empty files, rejects files with the target included, accepts correctly shaped claim files, and keeps the user scoring logic separate from the model-training data.

## Test cases

| Case | Upload content | Expected outcome | Actual outcome |
|---|---|---|---|
| Empty CSV | No rows | Reject with empty-file message | PASS |
| Target included | A CSV with `FraudFound` included | Reject and explain that the target cannot be included | PASS |
| Missing required feature | A CSV missing one of the approved feature columns | Reject and list the missing columns | PASS |
| Valid claim batch | A CSV with the approved features and no `FraudFound` | Scored and downloadable result table shown | PASS |

## Validation logic used

The app validation function requires the 28 approved feature columns and rejects any upload that contains `FraudFound`. It also rejects files that are empty and requires each row to match the modelling feature policy.

## Conclusion

The batch safeguards are working as intended and do not let uploaded data replace the shipped training data or final evaluation split.
