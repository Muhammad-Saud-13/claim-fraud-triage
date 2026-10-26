# Case-file workflow test results

## Beginner explanation

This report checks the case-file screen, which combines a claim, a recommendation, an explanation, comparable past claims, and an adjuster decision record. The purpose is to show that the human remains responsible for the final action even while the model offers a support recommendation.

## Test case

- Policy number used for the check: a sample claim from the 1996 holdout set
- Model view: selected model from the trained bundle
- Recommendation: pay, review, or investigate depending on the score
- Comparable past claims: at least one matching record or an explicit no-results message
- Decision saved: yes, the adjuster decision and timestamp are written to `reports/case_decisions.csv`

## Expected result and outcome

| Check | Result |
|---|---|
| Display a single claim record | PASS |
| Show indicators and probability | PASS |
| Give a plain-language reason | PASS |
| Show comparable past claims or explicit none-found message | PASS |
| Save human decision and timestamp | PASS |

## Conclusion

The case-file workflow is implemented and saves the human decision alongside the model recommendation without overwriting the model output. This meets the ethics and audit requirement for decision support.
