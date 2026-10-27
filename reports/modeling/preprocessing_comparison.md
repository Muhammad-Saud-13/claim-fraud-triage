# Preprocessing comparison

## Beginner explanation

All branches use the same decision tree, the same 1994–1995 training rows, the same five training folds, and the same untouched 1996 test rows. The baseline keeps all encoded features. PCA reduces the number of columns into components. SelectKBest keeps the 20 individual encoded columns with the strongest training-only statistical scores. Accuracy, precision, and recall are reported as mean ± spread for cross-validation and once on the test set. Every accuracy is shown beside the majority-class baseline for the corresponding training or test rows.

| branch | training majority baseline | cv accuracy mean | cv accuracy spread | test majority baseline | test accuracy | test precision | test recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline_encoded_scaled | 0.9374 | 0.9395 | 0.0008 | 0.9478 | 0.9495 | 0.8889 | 0.0376 |
| pca_encoded_scaled | 0.9374 | 0.9361 | 0.0014 | 0.9478 | 0.9466 | 0.3529 | 0.0282 |
| select_kbest_encoded_scaled | 0.9374 | 0.9372 | 0.0006 | 0.9478 | 0.9466 | 0.3529 | 0.0282 |

PCA and SelectKBest are comparisons, not automatic claims that fewer columns are always better. The final model task must choose using the pre-specified metrics and the untouched test result.

## Binning decision

No arbitrary numeric bins are used. A decision tree learns its own numeric split
points, k-nearest neighbours needs continuous scaled distances, and Gaussian
Naive Bayes models continuous numeric values. Binning would discard information
without a demonstrated benefit, so the numeric fields remain continuous after
training-fold median imputation and scaling.
