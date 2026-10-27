# Model comparison

## Beginner explanation

This model comparison uses the same clean feature table, the same 1994-1995 training rows, the same five-fold stratified training split, and the same untouched 1996 test rows. Cross-validation metrics use the training-only cost-selected threshold for that model. The majority-class baseline is shown beside every accuracy value so the fraud-class performance is not hidden by the simple majority rule.

| model | train baseline | cv accuracy mean ± std | test baseline | test accuracy | precision | recall | F1 | roc_auc | selected cost threshold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| decision_tree | 0.9374 | 0.8291 ± 0.0126 | 0.9478 | 0.8320 | 0.1117 | 0.3192 | 0.1655 | 0.5919 | 0.05 |
| knn | 0.9374 | 0.8239 ± 0.0087 | 0.9478 | 0.8241 | 0.0799 | 0.2254 | 0.1179 | 0.5414 | 0.20 |
| gaussian_nb | 0.9374 | 0.4228 ± 0.1164 | 0.9478 | 0.4964 | 0.0851 | 0.8873 | 0.1553 | 0.6922 | 0.95 |

The chosen operating threshold is selected by expected cost, not by the default 0.50 decision boundary. The model results therefore reflect the real imbalance in the claim file and the cost of missing fraud versus unnecessary reviews.
