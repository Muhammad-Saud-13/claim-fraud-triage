# Cost threshold summary

## Beginner explanation

A missed fraud case is assumed to cost 100,000 because it may be a hidden loss. An unnecessary investigation costs 5,000 because the claim is genuine but still uses staff time. These are compared across a set of thresholds to find the cheaper operating point.

The chosen default operating threshold is **0.95** for the selected model **gaussian_nb**, with an expected cost of **12,560,000** on the 1996 test set.

| threshold | precision | recall | investigations | expected cost |
|---:|---:|---:|---:|---:|
| 0.95 | 0.0851 | 0.8873 | 2221 | 12560000 |
| 0.90 | 0.0824 | 0.8873 | 2295 | 12930000 |
| 0.85 | 0.0812 | 0.8967 | 2353 | 13010000 |
| 0.80 | 0.0806 | 0.9061 | 2396 | 13015000 |
| 0.75 | 0.0799 | 0.9108 | 2428 | 13070000 |
| 0.70 | 0.0789 | 0.9108 | 2458 | 13220000 |
| 0.65 | 0.0780 | 0.9108 | 2487 | 13365000 |
| 0.60 | 0.0772 | 0.9155 | 2525 | 13450000 |
| 0.55 | 0.0762 | 0.9155 | 2560 | 13625000 |
| 0.50 | 0.0753 | 0.9155 | 2591 | 13780000 |
