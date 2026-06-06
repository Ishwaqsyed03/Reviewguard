import numpy as np
from textblob import TextBlob
import re

FEATURE_NAMES = [
    "review_length",
    "word_count",
    "avg_word_length",
    "sentiment_polarity",
    "sentiment_subjectivity",
    "exclamation_count",
    "uppercase_ratio",
    "has_url",
    "unique_word_ratio",
    "review_count",
    "avg_rating_given",
    "rating_deviation",
    "days_since_joined",
    "reviews_per_day",
    "verified_purchase",
    "helpful_votes",
    "profile_completeness",
]

# Human-readable labels and which direction is suspicious (high=fake or low=fake)
FEATURE_META = {
    "review_length":          {"label": "Review length",          "fake_when": "low"},
    "word_count":             {"label": "Word count",             "fake_when": "low"},
    "avg_word_length":        {"label": "Avg word length",        "fake_when": "low"},
    "sentiment_polarity":     {"label": "Sentiment polarity",     "fake_when": "high"},
    "sentiment_subjectivity": {"label": "Subjectivity score",     "fake_when": "high"},
    "exclamation_count":      {"label": "Exclamation marks (!)",  "fake_when": "high"},
    "uppercase_ratio":        {"label": "UPPERCASE ratio",        "fake_when": "high"},
    "has_url":                {"label": "Contains URL",           "fake_when": "high"},
    "unique_word_ratio":      {"label": "Vocabulary diversity",   "fake_when": "low"},
    "review_count":           {"label": "Reviewer total reviews", "fake_when": "low"},
    "avg_rating_given":       {"label": "Avg rating given",       "fake_when": "high"},
    "rating_deviation":       {"label": "Rating consistency",     "fake_when": "low"},
    "days_since_joined":      {"label": "Account age (days)",     "fake_when": "low"},
    "reviews_per_day":        {"label": "Reviews per day",        "fake_when": "high"},
    "verified_purchase":      {"label": "Verified purchase",      "fake_when": "low"},
    "helpful_votes":          {"label": "Helpful votes received", "fake_when": "low"},
    "profile_completeness":   {"label": "Profile completeness",   "fake_when": "low"},
}


def extract_text_features(review_text: str) -> dict:
    blob = TextBlob(review_text)
    words = review_text.split()
    return {
        "review_length":          len(review_text),
        "word_count":             len(words),
        "avg_word_length":        np.mean([len(w) for w in words]) if words else 0,
        "sentiment_polarity":     blob.sentiment.polarity,
        "sentiment_subjectivity": blob.sentiment.subjectivity,
        "exclamation_count":      review_text.count("!"),
        "uppercase_ratio":        sum(1 for c in review_text if c.isupper()) / max(len(review_text), 1),
        "has_url":                int(bool(re.search(r"http[s]?://", review_text))),
        "unique_word_ratio":      len(set(words)) / max(len(words), 1),
    }


def extract_behavioral_features(reviewer_data: dict) -> dict:
    return {
        "review_count":        reviewer_data.get("review_count", 0),
        "avg_rating_given":    reviewer_data.get("avg_rating", 3.0),
        "rating_deviation":    reviewer_data.get("rating_std", 0.0),
        "days_since_joined":   reviewer_data.get("days_since_joined", 0),
        "reviews_per_day":     reviewer_data.get("reviews_per_day", 0.0),
        "verified_purchase":   int(reviewer_data.get("verified_purchase", False)),
        "helpful_votes":       reviewer_data.get("helpful_votes", 0),
        "profile_completeness": reviewer_data.get("profile_completeness", 0.0),
    }


def get_named_features(review_text: str, reviewer_data: dict) -> dict:
    text = extract_text_features(review_text)
    behavioral = extract_behavioral_features(reviewer_data)
    return {**text, **behavioral}


def build_feature_vector(review_text: str, reviewer_data: dict) -> np.ndarray:
    named = get_named_features(review_text, reviewer_data)
    return np.array([named[k] for k in FEATURE_NAMES])
