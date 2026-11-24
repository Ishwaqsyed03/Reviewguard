"""Evaluate the detector while keeping duplicate reviews/template families together.

Run from the repository root:
    python scripts/evaluate_detector.py
"""
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit

from backend.detection.feature_extractor import build_feature_vector
from backend.detection.model import build_model

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "real_reviews.csv"

# These are the substitutions used by backend/utils/real_dataset.py. Normalizing
# them groups generated variants of the same template into one holdout family.
PRODUCT_TERMS = (
    "phone case", "coffee maker", "headphones", "mattress",
    "blender", "vacuum", "product", "purchase", "item", "watch",
)


def _group_key(row: pd.Series) -> str:
    text = re.sub(r"\s+", " ", str(row["review_text"]).strip().lower())
    if int(row["is_fake"]) == 1:
        for term in PRODUCT_TERMS:
            text = re.sub(rf"\b{re.escape(term)}\b", "{product}", text)
        return "generated-template:" + text

    # Keep exact duplicate genuine examples on the same side of the split.
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return "genuine-review:" + digest


def _reviewer_data(row: pd.Series) -> dict:
    return {
        "review_count": row.get("review_count", 0),
        "avg_rating": row.get("rating", 3.0),
        "rating_std": 0.0,
        "days_since_joined": row.get("days_since_joined", 0),
        "reviews_per_day": 0.0,
        "verified_purchase": row.get("verified_purchase", False),
        "helpful_votes": row.get("helpful_votes", 0),
        "profile_completeness": 0.5,
    }


def _metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> dict:
    report = classification_report(
        y_true,
        y_pred,
        labels=[0, 1],
        target_names=["genuine", "fake"],
        output_dict=True,
        zero_division=0,
    )
    return {
        "precision": report["fake"]["precision"],
        "recall": report["fake"]["recall"],
        "f1": report["fake"]["f1-score"],
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
        "confusion_matrix_genuine_fake": confusion_matrix(
            y_true, y_pred, labels=[0, 1]
        ).tolist(),
        "classification_report": report,
    }


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit(
            f"Dataset not found: {DATA_PATH}. See backend/utils/real_dataset.py "
            "for the dataset generation step."
        )

    df = pd.read_csv(DATA_PATH)
    required = {"review_text", "is_fake"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Dataset is missing columns: {sorted(missing)}")

    df = df.dropna(subset=["review_text", "is_fake"]).reset_index(drop=True)
    y = df["is_fake"].astype(int).to_numpy()
    if set(np.unique(y)) != {0, 1}:
        raise SystemExit("Evaluation requires both genuine (0) and fake (1) rows.")

    X = np.vstack([
        build_feature_vector(str(row["review_text"]), _reviewer_data(row))
        for _, row in df.iterrows()
    ])
    groups = np.asarray([_group_key(row) for _, row in df.iterrows()])

    splitter = GroupShuffleSplit(n_splits=100, test_size=0.25, random_state=42)
    split = next(
        (
            (train_idx, test_idx)
            for train_idx, test_idx in splitter.split(X, y, groups)
            if len(np.unique(y[train_idx])) == 2
            and len(np.unique(y[test_idx])) == 2
        ),
        None,
    )
    if split is None:
        raise SystemExit(
            "Could not make a grouped split containing both classes. "
            "Add more independent examples or template families."
        )

    train_idx, test_idx = split
    model = build_model()
    model.fit(X[train_idx], y[train_idx])
    predictions = model.predict(X[test_idx])
    probabilities = model.predict_proba(X[test_idx])[:, 1]

    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(X[train_idx], y[train_idx])
    baseline_predictions = baseline.predict(X[test_idx])
    baseline_probabilities = baseline.predict_proba(X[test_idx])[:, 1]

    fake_test_groups = sorted({
        groups[i] for i in test_idx if y[i] == 1
    })
    output = {
        "dataset": str(DATA_PATH.relative_to(ROOT)),
        "rows": int(len(df)),
        "class_counts": {
            "genuine": int((y == 0).sum()),
            "fake": int((y == 1).sum()),
        },
        "split": {
            "method": "GroupShuffleSplit; normalized generated fake templates and exact genuine duplicates stay together",
            "train_rows": int(len(train_idx)),
            "test_rows": int(len(test_idx)),
            "train_groups": int(len(set(groups[train_idx]))),
            "test_groups": int(len(set(groups[test_idx]))),
            "held_out_fake_template_families": fake_test_groups,
            "overlap_groups": int(len(set(groups[train_idx]) & set(groups[test_idx]))),
        },
        "majority_baseline": _metrics(
            y[test_idx], baseline_predictions, baseline_probabilities
        ),
        "detector": _metrics(y[test_idx], predictions, probabilities),
        "caveat": (
            "This dataset pairs genuine Yelp polarity reviews with generated fake "
            "templates. Template holdout tests generalization to unseen generated "
            "templates; it does not establish performance on real-world deceptive reviews."
        ),
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
