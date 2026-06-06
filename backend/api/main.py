from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import numpy as np

from backend.detection.feature_extractor import build_feature_vector, get_named_features
from backend.detection.model import load_model, predict, explain
from backend.utils.database import get_db, init_db, Review

app = FastAPI(title="Fake Review Detector API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


class ReviewRequest(BaseModel):
    reviewer_id: str
    product_id: str
    review_text: str
    rating: float
    verified_purchase: bool = False
    review_count: int = 0
    days_since_joined: int = 0
    helpful_votes: int = 0
    avg_rating: float = 3.0
    rating_std: float = 0.0
    reviews_per_day: float = 0.0
    profile_completeness: float = 0.5


class ReviewResponse(BaseModel):
    is_fake: bool
    fake_probability: float
    genuine_probability: float
    review_id: int
    explanation: list


@app.post("/api/detect", response_model=ReviewResponse)
def detect_fake_review(req: ReviewRequest, db: Session = Depends(get_db)):
    try:
        model = load_model()
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Model not trained yet. POST /api/train first.")

    reviewer_data = {
        "review_count":      req.review_count,
        "avg_rating":        req.avg_rating,
        "rating_std":        req.rating_std,
        "days_since_joined": req.days_since_joined,
        "reviews_per_day":   req.reviews_per_day,
        "verified_purchase": req.verified_purchase,
        "helpful_votes":     req.helpful_votes,
        "profile_completeness": req.profile_completeness,
    }

    named  = get_named_features(req.review_text, reviewer_data)
    result = predict(model, np.array(list(named.values())))
    top_features = explain(model, named)

    review = Review(
        reviewer_id=req.reviewer_id,
        product_id=req.product_id,
        review_text=req.review_text,
        rating=req.rating,
        is_fake=result["is_fake"],
        fake_probability=result["fake_probability"],
        verified_purchase=req.verified_purchase,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return ReviewResponse(review_id=review.id, explanation=top_features, **result)


@app.post("/api/train")
def train_model(use_real: bool = True):
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from backend.detection.model import train, evaluate
    from backend.detection.feature_extractor import extract_text_features, extract_behavioral_features
    from pathlib import Path

    if use_real:
        try:
            from backend.utils.real_dataset import load_real_dataset
            df = load_real_dataset()
            dataset_used = "Yelp Reviews (real) + research-pattern fake reviews"
        except Exception as e:
            from backend.utils.sample_data import generate_sample_data
            df = generate_sample_data()
            dataset_used = f"synthetic (real dataset failed: {e})"
    else:
        data_path = Path("data/sample/reviews_sample.csv")
        if not data_path.exists():
            from backend.utils.sample_data import generate_sample_data
            df = generate_sample_data()
        else:
            df = pd.read_csv(data_path)
        dataset_used = "synthetic"

    X, y = [], []
    for _, row in df.iterrows():
        reviewer_data = {
            "review_count": row.get("review_count", 0),
            "avg_rating": row.get("rating", 3.0),
            "rating_std": 0.0,
            "days_since_joined": row.get("days_since_joined", 0),
            "reviews_per_day": 0.0,
            "verified_purchase": row.get("verified_purchase", False),
            "helpful_votes": row.get("helpful_votes", 0),
            "profile_completeness": 0.5,
        }
        features = build_feature_vector(str(row["review_text"]), reviewer_data)
        X.append(features)
        y.append(row["is_fake"])

    X, y = np.array(X), np.array(y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = train(X_train, y_train)
    metrics = evaluate(model, X_test, y_test)

    return {
        "status": "trained",
        "dataset": dataset_used,
        "total_samples": len(df),
        "fake_samples": int(df["is_fake"].sum()),
        "genuine_samples": int((df["is_fake"] == 0).sum()),
        "metrics": metrics,
    }


@app.get("/api/reviews")
def list_reviews(limit: int = 50, db: Session = Depends(get_db)):
    reviews = db.query(Review).order_by(Review.created_at.desc()).limit(limit).all()
    return reviews


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Review).count()
    fake = db.query(Review).filter(Review.is_fake == True).count()
    genuine = db.query(Review).filter(Review.is_fake == False).count()
    return {"total": total, "fake": fake, "genuine": genuine, "fake_rate": fake / max(total, 1)}


@app.get("/api/timeline")
def review_bombing_timeline(product_id: str = "biz_001"):
    from backend.utils.timeline import generate_timeline
    return generate_timeline(product_id=product_id)


@app.get("/api/recommendations")
def recommendations(top_n: int = 6):
    from backend.utils.recommender import get_recommendations
    return get_recommendations(top_n=top_n)


@app.get("/health")
def health():
    return {"status": "ok"}
