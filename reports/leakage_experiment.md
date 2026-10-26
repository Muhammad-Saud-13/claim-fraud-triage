# Leakage experiment

## Beginner explanation

The project did not identify a separate post-investigation field. The honest production model therefore keeps the target and identifiers out of training and uses the same 1994-1995/1996 split as the final evaluation. The result is a fair test that does not invent a leak.

| model | included field | accuracy | majority baseline | precision | recall | ROC AUC | note |
|---|---|---:|---:|---:|---:|---:|---|
| gaussian_nb | honest_model_excluding_target_and_identifiers | 0.4964 | 0.9478 | 0.0851 | 0.8873 | 0.6922 | No separate post-investigation field was identified, so the honest production model excludes FraudFound, PolicyNumber, RepNumber, and Year. |

The complete field-timing review is recorded in the provenance report; no separate leak was found above the target. FraudFound remains excluded as a feature and is never used during cleaning, scaling, selection, or tuning.
