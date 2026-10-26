# Plain-language explanations

## Beginner explanation

This report shows examples of the user-facing reason the app gives for a predicted fraud score. The wording avoids internal model numbers and instead explains what matters in plain language for a claims adjuster.

### Decision tree example: pay

- Claim: a low-risk claim with a small deductible, few prior problems, and no witness or police report.
- Reason: the model sees a pattern where low-cost, low-risk claims with no suspicious signs are usually not fraudulent.
- Output: pay recommendation with a low fraud probability and a clear note that this is only a support signal.

### Decision tree example: review

- Claim: a mid-risk case with some strong indicators but not enough for a clear fraud flag.
- Reason: there are a few warning signs, such as a high deductible and an unusual claim timing, but the evidence is mixed.
- Output: review recommendation and a visible confidence range from the model.

### kNN example: investigate

- Claim: many comparable past claims with fraud markers, such as unusual claim timing, high deductible, and certain vehicle or policy patterns.
- Reason: the current claim looks similar to earlier fraud cases in the training file.
- Output: investigate recommendation with the nearest past claims shown for human review.
