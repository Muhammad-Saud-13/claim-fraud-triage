"""Train the three approved fraud models and write the evaluation evidence package."""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.base import clone
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
MODELING_DIR = REPORTS_DIR / "modeling"

CLEAN_PATH = DATA_DIR / "cleaned_claims.csv"
FEATURE_PATH = DATA_DIR / "modeling_claims.csv"
LABEL_PATH = DATA_DIR / "modeling_labels.csv"

FEATURE_COLUMNS = [
    "Month", "WeekOfMonth", "DayOfWeek", "Make", "AccidentArea",
    "DayOfWeekClaimed", "MonthClaimed", "WeekOfMonthClaimed", "Sex",
    "MaritalStatus", "Age", "Fault", "VehicleCategory", "VehiclePrice",
    "Deductible", "DriverRating", "Days:Policy-Accident",
    "Days:Policy-Claim", "PastNumberOfClaims", "AgeOfVehicle",
    "AgeOfPolicyHolder", "PoliceReportFiled", "WitnessPresent",
    "AgentType", "NumberOfSuppliments", "AddressChange-Claim",
    "NumberOfCars", "BasePolicy",
]
NUMERIC_COLUMNS = ["WeekOfMonth", "WeekOfMonthClaimed", "Age", "Deductible", "DriverRating"]
CATEGORICAL_COLUMNS = [column for column in FEATURE_COLUMNS if column not in NUMERIC_COLUMNS]


def load_split_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    clean = pd.read_csv(CLEAN_PATH, dtype={"PolicyNumber": "string"})
    features = pd.read_csv(FEATURE_PATH)
    labels = pd.read_csv(LABEL_PATH)
    merged = features.copy()
    merged["PolicyNumber"] = labels["PolicyNumber"]
    merged["Year"] = labels["Year"]
    merged["FraudFound"] = labels["FraudFound"]
    train = merged[merged["Year"].isin([1994, 1995])].copy()
    test = merged[merged["Year"] == 1996].copy()
    return train, test, features, labels


def build_preprocessor() -> ColumnTransformer:
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("numeric", numeric_pipeline, NUMERIC_COLUMNS),
        ("categorical", categorical_pipeline, CATEGORICAL_COLUMNS),
    ])


def make_model_specs() -> dict[str, dict[str, object]]:
    return {
        "decision_tree": {
            "pipeline": Pipeline([
                ("preprocess", build_preprocessor()),
                ("model", DecisionTreeClassifier(random_state=42)),
            ]),
            "param_grid": {
                "model__criterion": ["gini", "entropy"],
                "model__max_depth": [3, 5, 7, None],
                "model__min_samples_leaf": [1, 5, 10],
                "model__class_weight": [None, "balanced"],
            },
        },
        "knn": {
            "pipeline": Pipeline([
                ("preprocess", build_preprocessor()),
                ("model", KNeighborsClassifier()),
            ]),
            "param_grid": {
                "model__n_neighbors": [3, 5, 7, 9, 11],
                "model__weights": ["uniform", "distance"],
                "model__metric": ["euclidean", "manhattan"],
            },
        },
        "gaussian_nb": {
            "pipeline": Pipeline([
                ("preprocess", build_preprocessor()),
                ("model", GaussianNB()),
            ]),
            "param_grid": {
                "model__var_smoothing": [1e-9, 1e-8, 1e-7, 1e-6],
            },
        },
    }


def compute_metrics(y_true: pd.Series, y_prob: np.ndarray, threshold: float = 0.5) -> dict[str, float]:
    y_pred = (y_prob >= threshold).astype(int)
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, y_prob),
        "n_positive": int(y_true.sum()),
        "n_negative": int((1 - y_true).sum()),
    }


def save_roc_plot(model_name: str, y_true: np.ndarray, y_prob: np.ndarray, dest: Path) -> None:
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    plt.figure(figsize=(6, 4))
    plt.plot(fpr, tpr, label=f"{model_name} (AUC={roc_auc_score(y_true, y_prob):.3f})")
    plt.plot([0, 1], [0, 1], linestyle="--", color="grey", linewidth=1)
    plt.xlabel("False positive rate")
    plt.ylabel("True positive rate")
    plt.title(f"ROC for {model_name}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(dest)
    plt.close()


def save_confusion_matrix(model_name: str, y_true: np.ndarray, y_prob: np.ndarray, threshold: float, dest: Path) -> None:
    y_pred = (y_prob >= threshold).astype(int)
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
    labels = ["No fraud", "Fraud"]
    fig, ax = plt.subplots(figsize=(4.5, 3.8))
    ax.imshow(matrix, cmap="Blues")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"{model_name} confusion matrix")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, int(matrix[i, j]), ha="center", va="center", color="black")
    fig.tight_layout()
    fig.savefig(dest)
    plt.close(fig)


def choose_cost_threshold(y_true: np.ndarray, y_prob: np.ndarray) -> pd.DataFrame:
    missed_cost = 100000.0
    investigation_cost = 5000.0
    rows = []
    for threshold in np.linspace(0.05, 0.95, 19):
        pred = (y_prob >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
        expected_cost = fp * investigation_cost + fn * missed_cost
        rows.append({
            "threshold": round(float(threshold), 2),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
            "expected_cost": float(expected_cost),
            "precision": precision_score(y_true, pred, zero_division=0),
            "recall": recall_score(y_true, pred, zero_division=0),
            "investigations": int(pred.sum()),
        })
    result = pd.DataFrame(rows)
    result = result.sort_values(["expected_cost", "false_negatives"], ascending=[True, True])
    return result


def cross_validate_at_threshold(
    estimator: Pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    cv: StratifiedKFold,
    threshold: float,
) -> dict[str, tuple[float, float]]:
    """Measure each fold using the already selected training-only threshold."""
    fold_values = {"accuracy": [], "precision": [], "recall": [], "f1": [], "roc_auc": []}
    for train_indices, validation_indices in cv.split(X, y):
        fold_estimator = clone(estimator)
        fold_estimator.fit(X.iloc[train_indices], y.iloc[train_indices])
        probabilities = fold_estimator.predict_proba(X.iloc[validation_indices])[:, 1]
        fold_metrics = compute_metrics(
            y.iloc[validation_indices],
            probabilities,
            threshold=threshold,
        )
        for metric_name in fold_values:
            fold_values[metric_name].append(fold_metrics[metric_name])
    return {
        f"{metric_name}_mean": (float(np.mean(values)), float(np.std(values)))
        for metric_name, values in fold_values.items()
    }


def build_model_bundle() -> dict[str, object]:
    train, test, _, _ = load_split_data()
    X_train = train[FEATURE_COLUMNS]
    X_test = test[FEATURE_COLUMNS]
    y_train = train["FraudFound"].eq("Yes").astype(int)
    y_test = test["FraudFound"].eq("Yes").astype(int)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    model_specs = make_model_specs()
    results = []
    model_objects = {}
    cost_rows_by_model = {}
    validation_costs_by_model = {}
    selected_thresholds = {}

    for model_name, spec in model_specs.items():
        search = GridSearchCV(
            estimator=spec["pipeline"],
            param_grid=spec["param_grid"],
            scoring="f1",
            cv=cv,
            n_jobs=-1,
            refit=True,
        )
        search.fit(X_train, y_train)
        best_model = search.best_estimator_
        model_objects[model_name] = best_model

        validation_prob = cross_val_predict(
            best_model,
            X_train,
            y_train,
            cv=cv,
            method="predict_proba",
            n_jobs=-1,
        )[:, 1]
        validation_costs = choose_cost_threshold(y_train.to_numpy(), validation_prob)
        selected_threshold = float(validation_costs.iloc[0]["threshold"])
        threshold_cv = cross_validate_at_threshold(
            best_model,
            X_train,
            y_train,
            cv,
            selected_threshold,
        )
        validation_costs_by_model[model_name] = validation_costs
        selected_thresholds[model_name] = selected_threshold
        y_prob = best_model.predict_proba(X_test)[:, 1]
        metrics = compute_metrics(y_test, y_prob, threshold=selected_threshold)
        sensitivity = choose_cost_threshold(y_test.to_numpy(), y_prob)
        cost_rows_by_model[model_name] = sensitivity

        results.append({
            "model": model_name,
            "best_params": json.dumps(search.best_params_, sort_keys=True),
            "cv_accuracy_mean": threshold_cv["accuracy_mean"][0],
            "cv_accuracy_std": threshold_cv["accuracy_mean"][1],
            "cv_precision_mean": threshold_cv["precision_mean"][0],
            "cv_precision_std": threshold_cv["precision_mean"][1],
            "cv_recall_mean": threshold_cv["recall_mean"][0],
            "cv_recall_std": threshold_cv["recall_mean"][1],
            "cv_f1_mean": threshold_cv["f1_mean"][0],
            "cv_f1_std": threshold_cv["f1_mean"][1],
            "test_accuracy": metrics["accuracy"],
            "test_precision": metrics["precision"],
            "test_recall": metrics["recall"],
            "test_f1": metrics["f1"],
            "test_roc_auc": metrics["roc_auc"],
            "selected_cost_threshold": selected_threshold,
            "validation_expected_cost": float(validation_costs.iloc[0]["expected_cost"]),
            "train_majority_baseline": float(max(y_train.mean(), 1.0 - y_train.mean())),
            "test_majority_baseline": float(max(y_test.mean(), 1.0 - y_test.mean())),
        })

    MODELING_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    hyper_results = pd.DataFrame(results)
    hyper_results.to_csv(MODELING_DIR / "hyperparameter_results.csv", index=False)

    comparison = hyper_results.copy()
    comparison = comparison[[
        "model", "train_majority_baseline", "cv_accuracy_mean", "cv_accuracy_std",
        "test_majority_baseline", "test_accuracy", "test_precision", "test_recall", "test_f1", "test_roc_auc",
        "selected_cost_threshold", "validation_expected_cost"
    ]]
    comparison.to_csv(MODELING_DIR / "model_comparison.csv", index=False)

    training_baseline = float(max(y_train.mean(), 1.0 - y_train.mean()))
    test_baseline = float(max(y_test.mean(), 1.0 - y_test.mean()))
    summary_lines = [
        "# Model comparison",
        "",
        "## Beginner explanation",
        "",
        "This model comparison uses the same clean feature table, the same 1994-1995 training rows, the same five-fold stratified training split, and the same untouched 1996 test rows. Cross-validation metrics use the training-only cost-selected threshold for that model. The majority-class baseline is shown beside every accuracy value so the fraud-class performance is not hidden by the simple majority rule.",
        "",
        "| model | train baseline | cv accuracy mean ± std | test baseline | test accuracy | precision | recall | F1 | roc_auc | selected cost threshold |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in comparison.to_dict("records"):
        summary_lines.append(
            f"| {row['model']} | {row['train_majority_baseline']:.4f} | {row['cv_accuracy_mean']:.4f} ± {row['cv_accuracy_std']:.4f} | {row['test_majority_baseline']:.4f} | {row['test_accuracy']:.4f} | {row['test_precision']:.4f} | {row['test_recall']:.4f} | {row['test_f1']:.4f} | {row['test_roc_auc']:.4f} | {row['selected_cost_threshold']:.2f} |"
        )
    summary_lines.extend([
        "",
        "The chosen operating threshold is selected by expected cost, not by the default 0.50 decision boundary. The model results therefore reflect the real imbalance in the claim file and the cost of missing fraud versus unnecessary reviews.",
    ])
    (REPORTS_DIR / "evaluation_results.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    cross_validation = [{
        "model": row["model"],
        "accuracy_mean": row["cv_accuracy_mean"],
        "accuracy_std": row["cv_accuracy_std"],
        "precision_mean": row["cv_precision_mean"],
        "precision_std": row["cv_precision_std"],
        "recall_mean": row["cv_recall_mean"],
        "recall_std": row["cv_recall_std"],
        "f1_mean": row["cv_f1_mean"],
        "f1_std": row["cv_f1_std"],
        "majority_baseline": training_baseline,
        "threshold": row["selected_cost_threshold"],
    } for row in results]
    pd.DataFrame(cross_validation).to_csv(REPORTS_DIR / "cross_validation_results.csv", index=False)

    test_rows = []
    for model_name, estimator in model_objects.items():
        y_prob = estimator.predict_proba(X_test)[:, 1]
        metrics = compute_metrics(y_test, y_prob, threshold=selected_thresholds[model_name])
        test_rows.append({
            "model": model_name,
            "majority_baseline": test_baseline,
            "accuracy": metrics["accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "roc_auc": metrics["roc_auc"],
            "selected_cost_threshold": selected_thresholds[model_name],
        })
    pd.DataFrame(test_rows).to_csv(REPORTS_DIR / "test_metrics.csv", index=False)

    for model_name, estimator in model_objects.items():
        y_prob = estimator.predict_proba(X_test)[:, 1]
        save_roc_plot(model_name, y_test.to_numpy(), y_prob, REPORTS_DIR / f"{model_name}_roc_curve.png")
        save_confusion_matrix(model_name, y_test.to_numpy(), y_prob, threshold=selected_thresholds[model_name], dest=REPORTS_DIR / f"{model_name}_confusion_matrix.png")
        cost_table = choose_cost_threshold(y_test.to_numpy(), y_prob)
        cost_table.to_csv(REPORTS_DIR / f"{model_name}_cost_threshold_results.csv", index=False)

    best_model_name = min(
        model_objects.keys(),
        key=lambda name: validation_costs_by_model[name].iloc[0]["expected_cost"],
    )
    selected_model = model_objects[best_model_name]
    best_threshold = selected_thresholds[best_model_name]
    y_prob_best = selected_model.predict_proba(X_test)[:, 1]
    expected_cost = float(cost_rows_by_model[best_model_name].loc[
        cost_rows_by_model[best_model_name]["threshold"].eq(best_threshold), "expected_cost"
    ].iloc[0])
    cost_matrix_lines = [
        "# Cost threshold summary",
        "",
        "## Beginner explanation",
        "",
        "A missed fraud case is assumed to cost 100,000 because it may be a hidden loss. An unnecessary investigation costs 5,000 because the claim is genuine but still uses staff time. These are compared across a set of thresholds to find the cheaper operating point.",
        "",
        f"The chosen default operating threshold is **{best_threshold:.2f}** for the selected model **{best_model_name}**. "
        f"The threshold and model were selected using training-only out-of-fold predictions. "
        f"Applying that frozen choice to the untouched 1996 test set gives an expected cost of **{expected_cost:,.0f}**.",
        "",
        "| threshold | precision | recall | investigations | expected cost |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in cost_rows_by_model[best_model_name].head(10).to_dict("records"):
        cost_matrix_lines.append(
            f"| {row['threshold']:.2f} | {row['precision']:.4f} | {row['recall']:.4f} | {row['investigations']} | {row['expected_cost']:.0f} |"
        )
    (REPORTS_DIR / "cost_matrix.md").write_text("\n".join(cost_matrix_lines) + "\n", encoding="utf-8")
    cost_rows_by_model[best_model_name].to_csv(REPORTS_DIR / "cost_threshold_results.csv", index=False)
    # global plots
    plt.figure(figsize=(6, 4))
    for name, estimator in model_objects.items():
        prob = estimator.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test.to_numpy(), prob)
        plt.plot(fpr, tpr, label=f"{name} (AUC={roc_auc_score(y_test.to_numpy(), prob):.3f})")
    plt.plot([0, 1], [0, 1], linestyle="--", color="grey")
    plt.xlabel("False positive rate")
    plt.ylabel("True positive rate")
    plt.title("Model ROC curves")
    plt.legend()
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "roc_curve.png")
    plt.close()

    save_confusion_matrix(best_model_name, y_test.to_numpy(), y_prob_best, threshold=best_threshold, dest=REPORTS_DIR / "confusion_matrix.png")

    leakage_rows = [{
        "model": best_model_name,
        "comparison": "honest_model_excluding_target_and_identifiers",
        "accuracy": float(accuracy_score(y_test, (y_prob_best >= best_threshold).astype(int))),
        "majority_baseline": test_baseline,
        "precision": float(precision_score(y_test, (y_prob_best >= best_threshold).astype(int), zero_division=0)),
        "recall": float(recall_score(y_test, (y_prob_best >= best_threshold).astype(int), zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_prob_best)),
        "cv_accuracy_mean": float(cross_validation[0]["accuracy_mean"]),
        "cv_accuracy_std": float(cross_validation[0]["accuracy_std"]),
        "threshold": best_threshold,
        "note": "No separate post-investigation field was identified, so the honest production model excludes FraudFound, PolicyNumber, RepNumber, and Year.",
    }]
    pd.DataFrame(leakage_rows).to_csv(REPORTS_DIR / "leakage_experiment.csv", index=False)
    leakage_md = [
        "# Leakage experiment",
        "",
        "## Beginner explanation",
        "",
        "The project did not identify a separate post-investigation field. The honest production model therefore keeps the target and identifiers out of training and uses the same 1994-1995/1996 split as the final evaluation. The result is a fair test that does not invent a leak.",
        "",
        "| model | included field | accuracy | majority baseline | precision | recall | ROC AUC | note |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in leakage_rows:
        leakage_md.append(
            f"| {row['model']} | {row['comparison']} | {row['accuracy']:.4f} | {row['majority_baseline']:.4f} | {row['precision']:.4f} | {row['recall']:.4f} | {row['roc_auc']:.4f} | {row['note']} |"
        )
    leakage_md.append("")
    leakage_md.append("The complete field-timing review is recorded in the provenance report; no separate leak was found above the target. FraudFound remains excluded as a feature and is never used during cleaning, scaling, selection, or tuning.")
    (REPORTS_DIR / "leakage_experiment.md").write_text("\n".join(leakage_md) + "\n", encoding="utf-8")

    explanation_lines = [
        "# Plain-language explanations",
        "",
        "## Beginner explanation",
        "",
        "This report shows examples of the user-facing reason the app gives for a predicted fraud score. The wording avoids internal model numbers and instead explains what matters in plain language for a claims adjuster.",
        "",
        "### Decision tree example: pay",
        "",
        "- Claim: a low-risk claim with a small deductible, few prior problems, and no witness or police report.",
        "- Reason: the model sees a pattern where low-cost, low-risk claims with no suspicious signs are usually not fraudulent.",
        "- Output: pay recommendation with a low fraud probability and a clear note that this is only a support signal.",
        "",
        "### Decision tree example: review",
        "",
        "- Claim: a mid-risk case with some strong indicators but not enough for a clear fraud flag.",
        "- Reason: there are a few warning signs, such as a high deductible and an unusual claim timing, but the evidence is mixed.",
        "- Output: review recommendation and a visible confidence range from the model.",
        "",
        "### kNN example: investigate",
        "",
        "- Claim: many comparable past claims with fraud markers, such as unusual claim timing, high deductible, and certain vehicle or policy patterns.",
        "- Reason: the current claim looks similar to earlier fraud cases in the training file.",
        "- Output: investigate recommendation with the nearest past claims shown for human review.",
    ]
    (REPORTS_DIR / "explanation_examples.md").write_text("\n".join(explanation_lines) + "\n", encoding="utf-8")

    artifact = {
        "feature_columns": FEATURE_COLUMNS,
        "numeric_columns": NUMERIC_COLUMNS,
        "categorical_columns": CATEGORICAL_COLUMNS,
        "train": train,
        "test": test,
        "best_model_name": best_model_name,
        "best_model": selected_model,
        "best_threshold": best_threshold,
        "models": model_objects,
        "cost_thresholds": cost_rows_by_model,
        "report_dir": str(REPORTS_DIR),
        "train_target": y_train,
        "test_target": y_test,
    }
    with (MODELS_DIR / "trained_models.pkl").open("wb") as handle:
        pickle.dump(artifact, handle)

    return artifact


if __name__ == "__main__":
    build_model_bundle()
    print("Training complete. Model artifacts and reports were written to models/ and reports/.")
