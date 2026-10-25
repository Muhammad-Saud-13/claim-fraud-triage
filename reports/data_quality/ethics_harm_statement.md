# Project 15 harm and mitigation statement

## Purpose

Insurance fraud triage affects people and money. This project is therefore decision support for a claims adjuster, not an automatic legal or financial decision-maker.

> **Student project — not for financial or legal use.**

The model gives a recommendation that helps an adjuster decide what to review first. It does not prove that a claimant committed fraud, and it must never automatically deny or reject a claim.

## Who can be harmed

### Harm from a false fraud flag

A **false fraud flag** happens when the system recommends investigation for a genuine claim. This can delay payment, cause stress, require unnecessary paperwork, and wrongly make an honest claimant feel suspected.

### Harm from missed fraud

A **missed fraud case** happens when the system recommends pay or does not send a genuinely fraudulent claim for investigation. This can increase financial losses and may make honest customers bear higher costs through future premiums.

These harms are different. The first can hurt a genuine claimant directly; the second can hurt the insurer and honest customers. The system must show this trade-off instead of pretending that one score is always correct.

## Interface mitigations

The application must reduce risk in these ways:

1. **Human review remains required.** The adjuster makes the final decision. The model recommendation is never an automatic claim denial, automatic fraud finding, or automatic payment decision.
2. **A reason is shown for every prediction.** The app uses understandable claim attributes, a decision path, or comparable past claims. It must not show unexplained model language such as “node 14” or “gini 0.31”.
3. **Comparable cases are visible.** The case-file screen shows up to five similar past claims so the adjuster can inspect context rather than relying only on a number.
4. **The cost-based threshold is adjustable.** The initial cost matrix uses 100,000 for missed fraud and 5,000 for an unnecessary investigation. The Settings screen allows the adjuster to edit these values and see how the consequences change.
5. **Pay, review, and investigate are separate recommendations.** Two editable probability thresholds create three bands. An uncertain claim can go to human review rather than being treated as definitely safe or definitely fraudulent.
6. **Uncertainty is visible.** The app displays predicted fraud probability as model confidence and clearly states that probability is not proof.
7. **An audit trail is kept.** The case-file records the model recommendation and the adjuster's decision separately, with the claim identifier and decision time. A human decision must not overwrite the original model output.
8. **Privacy is protected.** The demonstration uses only the supplied public/anonymised dataset. No identifiable real person's record may be added.
9. **The warning is visible.** The exact warning appears on the main application surfaces, especially Single prediction, Batch scoring, Settings, and Case-file.

## Fairness and limitations

Some fields, such as `Sex`, `MaritalStatus`, `Age`, and `AgentType`, may reflect social or process differences rather than fraud. Their use must be documented, tested, and discussed as a limitation. A high score is an investigation priority, not a statement about a person's character.

The dataset contains historical decisions. Historical decisions can contain human bias or inconsistent investigation practices. The model can learn those patterns, so its output must be checked by a human and must not be used as the sole reason for adverse action.

## Beginner viva explanation

The model can make two important mistakes. It can wrongly flag an honest claimant, or it can miss real fraud. We reduce the first risk by showing reasons, similar claims, uncertainty, an adjustable cost threshold, and a human decision step. We reduce the second risk by measuring recall and by allowing the cost of missed fraud to be larger than the cost of an unnecessary investigation. We never let the model automatically reject a claim.
