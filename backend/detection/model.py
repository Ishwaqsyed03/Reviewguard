import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
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


def _class_index(model: Pipeline, label: int) -> int:
    classes = list(model.classes_)
    if label not in classes:
        raise ValueError(f"Model is missing the expected class {label}.")
    return classes.index(label)


def predict(model: Pipeline, features: np.ndarray) -> dict:
    row = features.reshape(1, -1)
    probabilities = model.predict_proba(row)[0]
    fake_index = _class_index(model, 1)
    genuine_index = _class_index(model, 0)
    label = model.predict(row)[0]
    return {
        "is_fake": bool(label == 1),
        "fake_probability": round(float(probabilities[fake_index]), 4),
        "genuine_probability": round(float(probabilities[genuine_index]), 4),
    }


def explain(model: Pipeline, named_features: dict) -> list:
    """Return per-feature local sensitivity vs the training-set mean.

    Each score is the change in fake probability when one observed feature is
    compared with that feature's training mean while all other inputs stay fixed.
    These scores are local comparisons, not causal or additive explanations.
    """
    from backend.detection.feature_extractor import FEATURE_NAMES, FEATURE_META

    scaler = model.named_steps["scaler"]
    values = np.array([named_features[name] for name in FEATURE_NAMES], dtype=float)
    reference_values = scaler.mean_
    fake_index = _class_index(model, 1)

    full_probability = float(model.predict_proba(values.reshape(1, -1))[0, fake_index])
    counterfactuals = np.repeat(values.reshape(1, -1), len(FEATURE_NAMES), axis=0)
    indices = np.arange(len(FEATURE_NAMES))
    counterfactuals[indices, indices] = reference_values
    reference_probabilities = model.predict_proba(counterfactuals)[:, fake_index]

    signals = []
    for i, name in enumerate(FEATURE_NAMES):
        signals.append({
            "feature": name,
            "label": FEATURE_META[name]["label"],
            "value": float(values[i]),
            "reference_value": float(reference_values[i]),
            "score": round(full_probability - float(reference_probabilities[i]), 4),
        })

    signals.sort(key=lambda item: abs(item["score"]), reverse=True)
    return signals[:10]


def evaluate(model: Pipeline, X_test: np.ndarray, y_test: np.ndarray) -> dict:
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, _class_index(model, 1)]
    report = classification_report(y_test, y_pred, output_dict=True)
    report["roc_auc"] = roc_auc_score(y_test, y_prob)
    return report
