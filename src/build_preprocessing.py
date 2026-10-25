"""Create the leakage-safe modelling table, split metadata, and preprocessing comparison."""

from pathlib import Path
import json
import pickle

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.tree import DecisionTreeClassifier


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLEAN_PATH = PROJECT_ROOT / "data" / "cleaned_claims.csv"
MODEL_TABLE_PATH = PROJECT_ROOT / "data" / "modeling_claims.csv"
LABELS_TABLE_PATH = PROJECT_ROOT / "data" / "modeling_labels.csv"
SPLIT_JSON_PATH = PROJECT_ROOT / "reports" / "modelling_split.json"
SPLIT_MD_PATH = PROJECT_ROOT / "reports" / "modelling_split.md"
COMPARISON_CSV_PATH = PROJECT_ROOT / "reports" / "preprocessing_comparison.csv"
COMPARISON_MD_PATH = PROJECT_ROOT / "reports" / "preprocessing_comparison.md"
ARTIFACT_PATH = PROJECT_ROOT / "models" / "preprocessing_artifacts.pkl"

FEATURE_COLUMNS = [
    "Month", "WeekOfMonth", "DayOfWeek", "Make", "AccidentArea",
    "DayOfWeekClaimed", "MonthClaimed", "WeekOfMonthClaimed", "Sex",
    "MaritalStatus", "Age", "Fault", "VehicleCategory",
    "VehiclePrice", "Deductible", "DriverRating", "Days:Policy-Accident",
    "Days:Policy-Claim", "PastNumberOfClaims", "AgeOfVehicle",
    "AgeOfPolicyHolder", "PoliceReportFiled", "WitnessPresent", "AgentType",
    "NumberOfSuppliments", "AddressChange-Claim", "NumberOfCars", "BasePolicy",
]
METADATA_COLUMNS = ["PolicyNumber", "Year", "FraudFound"]
NUMERIC_COLUMNS = ["WeekOfMonth", "WeekOfMonthClaimed", "Age", "Deductible", "DriverRating"]
CATEGORICAL_COLUMNS = [column for column in FEATURE_COLUMNS if column not in NUMERIC_COLUMNS]


def prepare_model_table(data: pd.DataFrame) -> pd.DataFrame:
    """Use safe repaired values while retaining target and split metadata internally."""
    table = data[METADATA_COLUMNS + FEATURE_COLUMNS].copy()
    replacements = {
        "Age": "Age_clean",
        "Make": "Make_clean",
        "DayOfWeekClaimed": "DayOfWeekClaimed_clean",
        "MonthClaimed": "MonthClaimed_clean",
    }
    for feature, clean_column in replacements.items():
        if clean_column in data:
            table[feature] = data[clean_column]
    for column in NUMERIC_COLUMNS:
        table[column] = pd.to_numeric(table[column], errors="coerce")
    for column in CATEGORICAL_COLUMNS:
        table[column] = table[column].astype(object).where(table[column].notna(), np.nan)
    return table


def build_preprocessor(scale_numeric: bool = True) -> ColumnTransformer:
    """Encode categories and impute numeric values using training folds only."""
    numeric_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))
    numeric_pipeline = Pipeline(numeric_steps)
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("numeric", numeric_pipeline, NUMERIC_COLUMNS),
        ("categorical", categorical_pipeline, CATEGORICAL_COLUMNS),
    ])


def main() -> None:
    data = pd.read_csv(CLEAN_PATH, dtype="string")
    table = prepare_model_table(data)
    # Export features separately so the target cannot accidentally become an input.
    table[FEATURE_COLUMNS].to_csv(MODEL_TABLE_PATH, index=False)
    table[METADATA_COLUMNS].to_csv(LABELS_TABLE_PATH, index=False)

    train = table[table["Year"].isin(["1994", "1995"])].copy()
    test = table[table["Year"].eq("1996")].copy()
    X_train = train[FEATURE_COLUMNS]
    X_test = test[FEATURE_COLUMNS]
    y_train = train["FraudFound"].eq("Yes").astype(int)
    y_test = test["FraudFound"].eq("Yes").astype(int)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    split = {
        "train_years": [1994, 1995],
        "test_years": [1996],
        "train_rows": len(train),
        "test_rows": len(test),
        "train_fraud": int(y_train.sum()),
        "test_fraud": int(y_test.sum()),
        "target_encoding": {"No": 0, "Yes": 1},
        "excluded_from_model_features": ["FraudFound", "PolicyNumber", "RepNumber", "Year"],
        "feature_columns": FEATURE_COLUMNS,
        "random_state": 42,
        "test_used_only_for_final_comparison": True,
        "test_policy_numbers": test["PolicyNumber"].astype(str).tolist(),
    }
    SPLIT_JSON_PATH.write_text(json.dumps(split, indent=2), encoding="utf-8")
    split_lines = [
        "# Modelling split",
        "",
        "## Beginner explanation",
        "",
        "The model learns from older claims and is tested on later claims. This is a "
        "chronological split, meaning time decides the boundary. The 1996 claims are "
        "kept untouched while preprocessing choices are made.",
        "",
        "| Item | Value |",
        "|---|---|",
        f"| Training years | 1994 and 1995 ({len(train)} rows) |",
        f"| Test year | 1996 ({len(test)} rows) |",
        f"| Training fraud cases | {int(y_train.sum())} |",
        f"| Test fraud cases | {int(y_test.sum())} |",
        "| Target encoding | No = 0, Yes = 1 |",
        "| Validation | 5-fold stratified CV on training rows only, random state 42 |",
        "| Test rule | Test rows are not used for fitting, imputation, encoding, selection, or tuning |",
        "",
        "## Excluded columns",
        "",
        "`FraudFound`, `PolicyNumber`, `RepNumber`, and `Year` are not model features. "
        "`Year` creates the split but is not given to the model. `PolicyNumber` is kept "
        "only for case identification and audit traceability.",
        "",
        "## Feature handover",
        "",
        "`data/modeling_claims.csv` contains only the 28 approved feature columns. It does "
        "not contain `FraudFound`, `PolicyNumber`, or `Year`, so the target and identifiers "
        "cannot accidentally be supplied as model inputs. The matching "
        "`data/modeling_labels.csv` file stores the target and split metadata separately for "
        "training, evaluation, and case identification. The model receives the 28 columns "
        "listed in `src/feature_policy.json`. Safe repaired "
        "values replace `Age`, `DayOfWeekClaimed`, and `MonthClaimed`. Unknown age values "
        "remain missing until the training-only median imputer runs inside each pipeline.",
    ]
    SPLIT_MD_PATH.write_text("\n".join(split_lines) + "\n", encoding="utf-8")

    branches = {
        "baseline_encoded_scaled": Pipeline([
            ("preprocess", build_preprocessor(True)),
            ("model", DecisionTreeClassifier(max_depth=5, random_state=42)),
        ]),
        "pca_encoded_scaled": Pipeline([
            ("preprocess", build_preprocessor(True)),
            ("reduce", PCA(n_components=0.95, random_state=42)),
            ("model", DecisionTreeClassifier(max_depth=5, random_state=42)),
        ]),
        "select_kbest_encoded_scaled": Pipeline([
            ("preprocess", build_preprocessor(True)),
            ("select", SelectKBest(score_func=f_classif, k=20)),
            ("model", DecisionTreeClassifier(max_depth=5, random_state=42)),
        ]),
    }
    rows = []
    for name, pipeline in branches.items():
        scores = cross_validate(
            pipeline,
            X_train,
            y_train,
            cv=cv,
            scoring=["accuracy", "precision", "recall"],
            return_train_score=False,
        )
        pipeline.fit(X_train, y_train)
        predicted = pipeline.predict(X_test)
        rows.append({
            "branch": name,
            "same_model": "DecisionTreeClassifier(max_depth=5, random_state=42)",
            "cv_accuracy_mean": scores["test_accuracy"].mean(),
            "cv_accuracy_std": scores["test_accuracy"].std(),
            "cv_precision_mean": scores["test_precision"].mean(),
            "cv_precision_std": scores["test_precision"].std(),
            "cv_recall_mean": scores["test_recall"].mean(),
            "cv_recall_std": scores["test_recall"].std(),
            "test_accuracy": accuracy_score(y_test, predicted),
            "test_precision": precision_score(y_test, predicted, zero_division=0),
            "test_recall": recall_score(y_test, predicted, zero_division=0),
        })

    results = pd.DataFrame(rows)
    train_baseline = max(y_train.mean(), 1 - y_train.mean())
    test_baseline = max(y_test.mean(), 1 - y_test.mean())
    results["training_majority_baseline"] = train_baseline
    results["test_majority_baseline"] = test_baseline
    results.to_csv(COMPARISON_CSV_PATH, index=False)
    comparison_table = [
        "| branch | training majority baseline | cv accuracy mean | cv accuracy spread | test majority baseline | test accuracy | test precision | test recall |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in results.to_dict("records"):
        comparison_table.append(
            f"| {row['branch']} | {row['training_majority_baseline']:.4f} | "
            f"{row['cv_accuracy_mean']:.4f} | {row['cv_accuracy_std']:.4f} | "
            f"{row['test_majority_baseline']:.4f} | {row['test_accuracy']:.4f} | "
            f"{row['test_precision']:.4f} | {row['test_recall']:.4f} |"
        )
    comparison_lines = [
        "# Preprocessing comparison",
        "",
        "## Beginner explanation",
        "",
        "All branches use the same decision tree, the same 1994–1995 training rows, "
        "the same five training folds, and the same untouched 1996 test rows. The baseline "
        "keeps all encoded features. PCA reduces the number of columns into components. "
        "SelectKBest keeps the 20 individual encoded columns with the strongest training-only "
        "statistical scores. Accuracy, precision, and recall are reported as mean ± spread "
        "for cross-validation and once on the test set. Every accuracy is shown beside the "
        "majority-class baseline for the corresponding training or test rows.",
        "",
        *comparison_table,
        "",
        "PCA and SelectKBest are comparisons, not automatic claims that fewer columns are "
        "always better. The final model task must choose using the pre-specified metrics and "
        "the untouched test result.",
    ]
    COMPARISON_MD_PATH.write_text("\n".join(comparison_lines) + "\n", encoding="utf-8")

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("wb") as handle:
        pickle.dump({
            "feature_columns": FEATURE_COLUMNS,
            "numeric_columns": NUMERIC_COLUMNS,
            "categorical_columns": CATEGORICAL_COLUMNS,
            "preprocessor": build_preprocessor(True),
            "ordinal_note": "Ordinal bands remain categorical until a documented model-specific mapping is selected.",
        }, handle)


if __name__ == "__main__":
    main()
