from __future__ import annotations

import json
import pickle
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
MODELS_DIR = ROOT / "models"


@st.cache_resource
def load_model_bundle() -> dict:
    with (MODELS_DIR / "trained_models.pkl").open("rb") as handle:
        return pickle.load(handle)


bundle = load_model_bundle()
FEATURE_COLUMNS = bundle["feature_columns"]
NUMERIC_COLUMNS = bundle["numeric_columns"]
CATEGORICAL_COLUMNS = bundle["categorical_columns"]
TRAIN_DF = bundle["train"]
TEST_DF = bundle["test"]
MODEL_MAP = bundle["models"]
BEST_MODEL_NAME = bundle["best_model_name"]


def get_warning() -> str:
    return "This is a student project and is not for financial or legal use. The model is decision support only; a human adjuster must review the recommendation."


def recommend_from_probability(prob: float, review_threshold: float, investigate_threshold: float) -> str:
    if prob < review_threshold:
        return "Pay"
    if prob < investigate_threshold:
        return "Review"
    return "Investigate"


def probability_to_percent(prob: float) -> str:
    return f"{prob * 100:.1f}%"


def get_model_probability(model_name: str, record: pd.Series) -> float:
    model = MODEL_MAP[model_name]
    prepared = pd.DataFrame([record[FEATURE_COLUMNS]])
    prob = model.predict_proba(prepared)[0, 1]
    return float(prob)


def simple_explanation(model_name: str, record: pd.Series, prob: float, review_threshold: float, investigate_threshold: float) -> str:
    if model_name == "decision_tree":
        signals = []
        if record.get("Deductible", 0) >= 500:
            signals.append("a high deductible")
        if record.get("Age", 0) <= 30:
            signals.append("a younger claimant age")
        if str(record.get("WitnessPresent", "No")).strip().lower() == "yes":
            signals.append("a witness being present")
        if str(record.get("PoliceReportFiled", "No")).strip().lower() == "yes":
            signals.append("a police report being filed")
        if not signals:
            signals.append("a low-risk pattern with few warning signs")
        risk_text = ", ".join(signals[:3])
        return (
            f"This claim looks {risk_text}. The model gives a {probability_to_percent(prob)} fraud probability, which falls in the "
            f"{recommend_from_probability(prob, review_threshold, investigate_threshold).lower()} band. The recommendation is support only and must be reviewed by a human adjuster."
        )
    if model_name == "knn":
        return (
            f"This claim is close to past claims that looked similar in the training file, especially around {record.get('VehicleCategory', 'the vehicle profile')}, "
            f"{record.get('AccidentArea', 'the accident area')}, and {record.get('AgeOfPolicyHolder', 'the policy-holder age')}. The model therefore gives a "
            f"{probability_to_percent(prob)} fraud probability and recommends {recommend_from_probability(prob, review_threshold, investigate_threshold)}."
        )
    return (
        f"The model balances a number of small signals, such as claim timing, claim amount, and the policy profile, and estimates a "
        f"{probability_to_percent(prob)} fraud probability. This sits in the {recommend_from_probability(prob, review_threshold, investigate_threshold).lower()} band, so it should be treated as a decision-support signal rather than proof."
    )


def load_report_csv(name: str) -> pd.DataFrame:
    path = REPORTS_DIR / name
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def show_model_performance() -> None:
    st.header("Model performance")
    st.warning(get_warning())
    model_table = load_report_csv("modeling/model_comparison.csv")
    if not model_table.empty:
        st.dataframe(model_table, use_container_width=True)
    else:
        st.info("Model comparison CSV not generated yet.")

    labels = pd.read_csv(DATA_DIR / "modeling_labels.csv")
    test_data = labels[labels["Year"] == 1996].copy()
    test_target = test_data["FraudFound"].eq("Yes").astype(int)
    fig, ax = plt.subplots(figsize=(7, 5))
    for model_name, estimator in MODEL_MAP.items():
        probs = estimator.predict_proba(pd.read_csv(DATA_DIR / "modeling_claims.csv"))[:, 1]
        # keep only 1996 rows
        x_test = pd.read_csv(DATA_DIR / "modeling_claims.csv")
        x_test = x_test[test_data.index.to_numpy()]
        model_probs = estimator.predict_proba(x_test)[:, 1]
        from sklearn.metrics import roc_curve, roc_auc_score
        fpr, tpr, _ = roc_curve(test_target.to_numpy(), model_probs)
        ax.plot(fpr, tpr, label=f"{model_name} (AUC={roc_auc_score(test_target.to_numpy(), model_probs):.3f})")
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title("ROC curve for the three models")
    ax.legend()
    st.pyplot(fig)

    st.subheader("Confusion matrix")
    selected_model = st.selectbox("Choose model", list(MODEL_MAP.keys()), index=list(MODEL_MAP.keys()).index(BEST_MODEL_NAME))
    threshold = st.slider("Investigation threshold", 0.05, 0.95, 0.5, 0.01)
    y_test = TEST_DF["FraudFound"].eq("Yes").astype(int)
    y_prob = MODEL_MAP[selected_model].predict_proba(TEST_DF[FEATURE_COLUMNS])[:, 1]
    from sklearn.metrics import confusion_matrix
    pred = (y_prob >= threshold).astype(int)
    cm = confusion_matrix(y_test, pred, labels=[0, 1])
    st.dataframe(pd.DataFrame(cm, index=["Actual No", "Actual Yes"], columns=["Pred No", "Pred Yes"]))


def show_single_prediction() -> None:
    st.header("Single prediction")
    st.warning(get_warning())
    df = pd.read_csv(DATA_DIR / "modeling_claims.csv")
    labels = pd.read_csv(DATA_DIR / "modeling_labels.csv")
    merged = df.copy()
    merged["PolicyNumber"] = labels["PolicyNumber"]
    merged["Year"] = labels["Year"]
    merged["FraudFound"] = labels["FraudFound"]
    sample_ids = merged["PolicyNumber"].dropna().astype(str).tolist()
    claim_id = st.selectbox("Choose a claim to review", sample_ids[:min(50, len(sample_ids))])
    row = merged[merged["PolicyNumber"].astype(str) == str(claim_id)].iloc[0].to_dict()
    selected_model = st.selectbox("Choose model for explanation", list(MODEL_MAP.keys()), index=list(MODEL_MAP.keys()).index(BEST_MODEL_NAME))
    review_threshold = st.slider("Review threshold", 0.05, 0.8, 0.20, 0.01)
    investigate_threshold = st.slider("Investigate threshold", 0.2, 0.95, 0.60, 0.01)
    prob = get_model_probability(selected_model, pd.Series(row))
    recommendation = recommend_from_probability(prob, review_threshold, investigate_threshold)
    st.metric("Predicted fraud probability", probability_to_percent(prob))
    st.metric("Recommendation", recommendation)
    st.markdown(simple_explanation(selected_model, pd.Series(row), prob, review_threshold, investigate_threshold))
    st.subheader("Claim indicators")
    display_row = {key: value for key, value in row.items() if key in FEATURE_COLUMNS}
    st.dataframe(pd.DataFrame([display_row]).T.rename({0: "value"}), use_container_width=True)


def show_data_quality() -> None:
    st.header("Data & quality")
    st.warning(get_warning())
    raw = pd.read_csv(DATA_DIR / "raw_claims.csv", dtype={"PolicyNumber": "string"})
    cleaned = pd.read_csv(DATA_DIR / "cleaned_claims.csv", dtype={"PolicyNumber": "string"})
    st.subheader("Dataset snapshot")
    st.write(f"Raw rows: {len(raw)} | Cleaned rows: {len(cleaned)} | Target counts: {cleaned['FraudFound'].value_counts().to_dict()}")
    st.dataframe(cleaned.head(10), use_container_width=True)
    st.subheader("Audit status")
    validation = json.loads((REPORTS_DIR / "data_quality" / "validation_results.json").read_text()) if (REPORTS_DIR / "data_quality" / "validation_results.json").exists() else {}
    if validation:
        for label, result in validation.items():
            st.write(f"{label.title()}: {result['passed_count']} checks passed, {result['failed_count']} failed.")
    else:
        st.info("Validation results file not yet generated.")
    st.download_button("Download cleaned CSV", data=cleaned.to_csv(index=False).encode("utf-8"), file_name="cleaned_claims.csv", mime="text/csv")


def validate_batch_columns(uploaded_csv: pd.DataFrame) -> tuple[bool, str]:
    required = set(FEATURE_COLUMNS)
    present = set(uploaded_csv.columns)
    if uploaded_csv.empty:
        return False, "The uploaded file is empty. Provide a CSV with at least one claim row."
    if "FraudFound" in present:
        return False, "FraudFound must not be included in user-uploaded batch inputs. Remove the target column before scoring."
    missing = sorted(required - present)
    if missing:
        return False, f"Missing required columns: {', '.join(missing)}."
    return True, "OK"


def show_batch_scoring() -> None:
    st.header("Batch scoring")
    st.warning(get_warning())
    uploaded = st.file_uploader("Upload a claim CSV", type=["csv"])
    if uploaded is None:
        st.info("Upload a CSV for batch fraud review.")
        return
    batch = pd.read_csv(uploaded)
    valid, message = validate_batch_columns(batch)
    if not valid:
        st.error(message)
        return
    model_name = st.selectbox("Select scoring model", list(MODEL_MAP.keys()), index=list(MODEL_MAP.keys()).index(BEST_MODEL_NAME))
    review_threshold = st.slider("Review threshold", 0.05, 0.8, 0.20, 0.01, key="batch_review")
    investigate_threshold = st.slider("Investigate threshold", 0.2, 0.95, 0.60, 0.01, key="batch_investigate")
    scored = batch.copy()
    scored = scored[FEATURE_COLUMNS].copy()
    probs = MODEL_MAP[model_name].predict_proba(scored)[0:len(scored)]
    scored["fraud_probability"] = probs[:, 1]
    scored["recommendation"] = scored["fraud_probability"].apply(lambda p: recommend_from_probability(float(p), review_threshold, investigate_threshold))
    scored["reason"] = scored["fraud_probability"].apply(lambda p: f"Probability {probability_to_percent(float(p))}; risk band {recommend_from_probability(float(p), review_threshold, investigate_threshold)}.")
    scored = scored.sort_values("fraud_probability", ascending=False)
    st.dataframe(scored[["fraud_probability", "recommendation", "reason"]], use_container_width=True)
    csv_download = scored.to_csv(index=False).encode("utf-8")
    st.download_button("Download batch results", data=csv_download, file_name="fraud_batch_results.csv", mime="text/csv")


def show_settings() -> None:
    st.header("Settings")
    st.warning(get_warning())
    selected_model = st.selectbox("Selected model", list(MODEL_MAP.keys()), index=list(MODEL_MAP.keys()).index(BEST_MODEL_NAME))
    review_threshold = st.slider("Pay / Review cut-off", 0.05, 0.8, 0.20, 0.01)
    investigate_threshold = st.slider("Review / Investigate cut-off", 0.2, 0.95, 0.60, 0.01)
    missed_cost = st.number_input("Missed fraud cost", min_value=1000.0, value=100000.0, step=1000.0)
    unnecessary_cost = st.number_input("Unnecessary investigation cost", min_value=100.0, value=5000.0, step=100.0)

    y_test = TEST_DF["FraudFound"].eq("Yes").astype(int)
    y_prob = MODEL_MAP[selected_model].predict_proba(TEST_DF[FEATURE_COLUMNS])[:, 1]
    rows = []
    for threshold in np.linspace(0.05, 0.95, 19):
        pred = (y_prob >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_test, pred, labels=[0, 1]).ravel()
        cost = fp * unnecessary_cost + fn * missed_cost
        rows.append({
            "threshold": round(float(threshold), 2),
            "expected_cost": float(cost),
            "precision": precision_score(y_test, pred, zero_division=0),
            "recall": recall_score(y_test, pred, zero_division=0),
            "investigations": int(pred.sum()),
        })
    sensitivity = pd.DataFrame(rows)
    st.dataframe(sensitivity.sort_values("expected_cost").head(10), use_container_width=True)
    chosen = sensitivity.sort_values("expected_cost").iloc[0]
    st.write(f"Current operating threshold from expected cost: {chosen['threshold']:.2f} with expected cost {chosen['expected_cost']:,.0f}.")


def show_case_file() -> None:
    st.header("Case-file")
    st.warning(get_warning())
    labels = pd.read_csv(DATA_DIR / "modeling_labels.csv")
    df = pd.read_csv(DATA_DIR / "modeling_claims.csv")
    merged = df.copy()
    merged["PolicyNumber"] = labels["PolicyNumber"]
    merged["Year"] = labels["Year"]
    merged["FraudFound"] = labels["FraudFound"]
    policy_number = st.selectbox("Choose case file", merged["PolicyNumber"].astype(str).tolist()[:min(50, len(merged))])
    row = merged[merged["PolicyNumber"].astype(str) == str(policy_number)].iloc[0]
    selected_model = st.selectbox("Model for this case", list(MODEL_MAP.keys()), index=list(MODEL_MAP.keys()).index(BEST_MODEL_NAME), key="case_model")
    review_threshold = st.slider("Review threshold", 0.05, 0.8, 0.20, 0.01, key="case_review")
    investigate_threshold = st.slider("Investigate threshold", 0.2, 0.95, 0.60, 0.01, key="case_investigate")
    prob = get_model_probability(selected_model, row)
    recommendation = recommend_from_probability(prob, review_threshold, investigate_threshold)
    compare = merged.dropna(subset=["PolicyNumber"]).copy()
    compare = compare[compare["PolicyNumber"].astype(str) != str(policy_number)]
    diff = compare.apply(lambda r: sum(1 for f in FEATURE_COLUMNS if str(r[f]).lower() == str(row[f]).lower()), axis=1)
    comparable = compare.assign(match_score=diff).sort_values("match_score", ascending=False).head(5)
    st.subheader("Policy indicators")
    st.dataframe(pd.DataFrame([row[FEATURE_COLUMNS].to_dict()]).T.rename({0: "value"}), use_container_width=True)
    st.subheader("Recommendation")
    st.write(f"Prediction: {recommendation} | probability: {probability_to_percent(prob)}")
    st.markdown(simple_explanation(selected_model, row, prob, review_threshold, investigate_threshold))
    st.subheader("Comparable past claims")
    if comparable.empty:
        st.write("No comparable past claims were found for this case.")
    else:
        st.dataframe(comparable[["PolicyNumber"] + FEATURE_COLUMNS[:5]].head(5), use_container_width=True)
    with st.form("case_decision_form"):
        decision = st.radio("Adjuster decision", ["Pay", "Review", "Investigate", "No action taken"], index=1)
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Save decision")
    if submitted:
        record = {
            "PolicyNumber": str(policy_number),
            "Model": selected_model,
            "Recommendation": recommendation,
            "Probability": prob,
            "Decision": decision,
            "Notes": notes,
            "Timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }
        decision_path = REPORTS_DIR / "case_decisions.csv"
        if decision_path.exists():
            decisions = pd.read_csv(decision_path)
        else:
            decisions = pd.DataFrame()
        decisions = pd.concat([decisions, pd.DataFrame([record])], ignore_index=True)
        decisions.to_csv(decision_path, index=False)
        st.success("Decision saved to case_decisions.csv.")


def main() -> None:
    st.set_page_config(page_title="Claim Fraud Triage", page_icon="🛡️", layout="wide")
    st.title("Insurance Claim Fraud Triage")
    st.caption("Decision support for a claims adjuster. This is a student project and is not for financial or legal use.")
    screens = [
        "Data & quality",
        "Model performance",
        "Single prediction",
        "Batch scoring",
        "Settings",
        "Case-file",
    ]
    choice = st.sidebar.selectbox("Screen", screens)
    if choice == "Data & quality":
        show_data_quality()
    elif choice == "Model performance":
        show_model_performance()
    elif choice == "Single prediction":
        show_single_prediction()
    elif choice == "Batch scoring":
        show_batch_scoring()
    elif choice == "Settings":
        show_settings()
    else:
        show_case_file()


if __name__ == "__main__":
    main()
