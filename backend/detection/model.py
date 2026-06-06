import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent.parent / "models" / "trained" / "detector.pkl"


def build_model() -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", GradientBoostingClassifier(n_estimators=200, max_depth=5, random_state=42)),
    ])


def train(X_train: np.ndarray, y_train: np.ndarray) -> Pipeline:
    model = build_model()
    model.fit(X_train, y_train)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model


def load_model() -> Pipeline:
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model not trained yet. Run train first.")
    return joblib.load(MODEL_PATH)


def predict(model: Pipeline, features: np.ndarray) -> dict:
    prob = model.predict_proba(features.reshape(1, -1))[0]
    label = model.predict(features.reshape(1, -1))[0]
    return {
        "is_fake": bool(label),
        "fake_probability": round(float(prob[1]), 4),
        "genuine_probability": round(float(prob[0]), 4),
    }


def explain(model: Pipeline, named_features: dict) -> list:
    from backend.detection.feature_extractor import FEATURE_NAMES, FEATURE_META

    importances = model.named_steps["clf"].feature_importances_
    scaler      = model.named_steps["scaler"]

    values = np.array([named_features[k] for k in FEATURE_NAMES])
    scaled = scaler.transform(values.reshape(1, -1))[0]

    contributions = []
    for i, fname in enumerate(FEATURE_NAMES):
        meta      = FEATURE_META[fname]
        raw_val   = float(values[i])
        scaled_v  = float(scaled[i])
        imp       = float(importances[i])

        # Direction: positive contribution = toward fake
        direction = 1 if meta["fake_when"] == "high" else -1
        score     = round(imp * scaled_v * direction, 4)

        contributions.append({
            "feature":     fname,
            "label":       meta["label"],
            "value":       raw_val,
            "importance":  round(imp, 4),
            "score":       score,           # positive = suspicious, negative = genuine signal
            "fake_when":   meta["fake_when"],
        })

    contributions.sort(key=lambda x: abs(x["score"]), reverse=True)
    return contributions[:10]


def evaluate(model: Pipeline, X_test: np.ndarray, y_test: np.ndarray) -> dict:
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    report = classification_report(y_test, y_pred, output_dict=True)
    report["roc_auc"] = roc_auc_score(y_test, y_prob)
    return report
