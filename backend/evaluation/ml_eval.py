"""
Nexus Mind — Machine Learning Risk Engine Evaluation Suite
Measures:
- Train/Validation/Test Split Performance
- Baseline (Logistic Regression) vs Candidate (Random Forest) Comparison
- Accuracy, Precision, Recall, F1-Score, and ROC-AUC
- Global Tree Feature Importances (Explainable AI / XAI)
- Saves benchmark output to artifacts/ml_evaluation.json
"""
import json
import os
import sys
from datetime import datetime

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ["DATABASE_URL"] = "sqlite:///./nexusmind.db"

from app.database import SessionLocal
from app.services.ml_risk_service import MODEL_METADATA, predict_task_risk, train_ml_pipeline
from seed_data import seed


def run_ml_evaluation():
    seed()
    db = SessionLocal()

    print("\n========================================================")
    print("RUNNING MACHINE LEARNING RISK MODEL EVALUATION")
    print("========================================================")

    meta = train_ml_pipeline()
    metrics = meta.get("metrics", {})
    base_m = metrics.get("baseline_logistic_regression", {})
    cand_m = metrics.get("candidate_random_forest", {})
    feat_imp = meta.get("feature_importances", {})

    print(f"[MODEL] Version: {meta.get('model_version')} ({meta.get('model_type')})")
    print(f"[BASELINE] Logistic Regression — Accuracy: {base_m.get('accuracy')}, F1: {base_m.get('f1_score')}, ROC-AUC: {base_m.get('roc_auc')}")
    print(f"[CANDIDATE] Random Forest — Accuracy: {cand_m.get('accuracy')}, F1: {cand_m.get('f1_score')}, ROC-AUC: {cand_m.get('roc_auc')}")
    print(f"[XAI IMPORTANCES] {feat_imp}")

    # Test Task Prediction with XAI
    pred = predict_task_risk(db, "TASK-102")
    assert pred.predicted_risk is not None, "Failed to predict task risk"
    assert len(pred.contributing_factors) >= 4, "XAI factor breakdown missing"
    print(f"[TASK-102] Predicted Risk: {pred.predicted_risk * 100}% (Level: {pred.risk_level})")
    print(f"[TASK-102 XAI FACTORS] {pred.contributing_factors}")

    eval_summary = {
        "benchmark_timestamp": datetime.utcnow().isoformat(),
        "model_version": meta.get("model_version"),
        "model_type": meta.get("model_type"),
        "metrics": metrics,
        "feature_importances": feat_imp,
        "sample_prediction": {
            "task_id": "TASK-102",
            "predicted_risk": pred.predicted_risk,
            "risk_level": pred.risk_level,
            "xai_factors": pred.contributing_factors,
            "recommendation": pred.recommendation,
        },
        "status": "PASSED",
    }

    # Save artifact
    artifacts_dir = os.path.join(backend_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    artifact_path = os.path.join(artifacts_dir, "ml_evaluation.json")

    with open(artifact_path, "w") as f:
        json.dump(eval_summary, f, indent=2)

    print(f"[SAVED] Evaluation metrics saved to {artifact_path}")
    print("========================================================\n")

    db.close()
    return eval_summary


if __name__ == "__main__":
    run_ml_evaluation()
