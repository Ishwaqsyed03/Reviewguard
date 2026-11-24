import hmac
import os
from datetime import datetime

import numpy as np
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from backend.detection.feature_extractor import get_named_features
from backend.detection.model import load_model, predict, explain
from backend.utils.database import get_db, init_db, Review

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120/minute"],
    storage_uri=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
)
app = FastAPI(title="Fake Review Detector API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

bearer_auth = HTTPBearer(auto_error=False)


@app.on_event("startup")
def startup():
    init_db()


class ReviewRequest(BaseModel):
    reviewer_id: str = Field(min_length=1, max_length=100)
    product_id: str = Field(min_length=1, max_length=100)
    review_text: str = Field(min_length=1, max_length=10_000)
    rating: float = Field(ge=1, le=5)
    verified_purchase: bool = False
    review_count: int = Field(default=0, ge=0, le=1_000_000)
    days_since_joined: int = Field(default=0, ge=0, le=36_500)
    helpful_votes: int = Field(default=0, ge=0, le=10_000_000)
    avg_rating: float = Field(default=3.0, ge=1, le=5)
    rating_std: float = Field(default=0.0, ge=0, le=5)
    reviews_per_day: float = Field(default=0.0, ge=0, le=10_000)
    profile_completeness: float = Field(default=0.5, ge=0, le=1)


class ReviewResponse(BaseModel):
    is_fake: bool
    fake_probability: float
    genuine_probability: float
    review_id: int
    explanation: list


class ReviewHistoryItem(BaseModel):
    id: int
    rating: float
    is_fake: bool
    fake_probability: float
    verified_purchase: bool
    created_at: datetime


def require_admin_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_auth),
):
    expected_token = os.getenv("REVIEWGUARD_ADMIN_TOKEN")
    if not expected_token:
        raise HTTPException(
            status_code=503,
            detail="Model training is disabled because no admin token is configured.",
        )
    if credentials is None or not hmac.compare_digest(
        credentials.credentials, expected_token
    ):
        raise HTTPException(
            status_code=401,
            detail="A valid admin bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/api/detect", response_model=ReviewResponse)
@limiter.limit("10/minute")
def detect_fake_review(
    request: Request,
    req: ReviewRequest,
    db: Session = Depends(get_db),
):
    try:
        model = load_model()
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Model not trained yet. POST /api/train first.")

    reviewer_data = {
        "review_count": req.review_count,
        "avg_rating": req.avg_rating,
        "rating_std": req.rating_std,
        "days_since_joined": req.days_since_joined,
        "reviews_per_day": req.reviews_per_day,
        "verified_purchase": req.verified_purchase,
        "helpful_votes": req.helpful_votes,
        "profile_completeness": req.profile_completeness,
    }

    named = get_named_features(req.review_text, reviewer_data)
    result = predict(model, np.array(list(named.values())))
    top_features = explain(model, named)

    # Persist only the classification summary; submitted text and IDs are not
    # needed for the public history, aggregate stats, or recommendations.
    review = Review(
        reviewer_id=None,
        product_id=None,
        review_text=None,
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
@limiter.limit("2/hour")
def train_model(
    request: Request,
    use_real: bool = True,
    _admin: HTTPAuthorizationCredentials | None = Depends(require_admin_token),
):
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from backend.detection.model import train, evaluate
    from backend.detection.feature_extractor import build_feature_vector
    from pathlib import Path

    if use_real:
        try:
            from backend.utils.real_dataset import load_real_dataset
            df = load_real_dataset()
            dataset_used = "Yelp polarity reviews + generated fake-review templates"
        except Exception:
            from backend.utils.sample_data import generate_sample_data
            df = generate_sample_data()
            dataset_used = "synthetic fallback dataset"
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
        X.append(build_feature_vector(str(row["review_text"]), reviewer_data))
        y.append(row["is_fake"])

    X, y = np.array(X), np.array(y)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

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


@app.get("/api/reviews", response_model=list[ReviewHistoryItem])
@limiter.limit("30/minute")
def list_reviews(
    request: Request,
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    reviews = db.query(Review).order_by(Review.created_at.desc()).limit(limit).all()
    return [
        ReviewHistoryItem(
            id=review.id,
            rating=review.rating,
            is_fake=review.is_fake,
            fake_probability=review.fake_probability,
            verified_purchase=review.verified_purchase,
            created_at=review.created_at,
        )
        for review in reviews
    ]


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
