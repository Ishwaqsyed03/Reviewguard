"""
Content-based recommendation engine using product ratings.
Demonstrates the impact of fake review filtering on recommendation quality.
"""
import numpy as np
import pandas as pd
from pathlib import Path

# Seeded product catalog with realistic names and categories
PRODUCTS = [
    {"id": "biz_001", "name": "Sony WH-1000XM5 Headphones",    "category": "Electronics"},
    {"id": "biz_002", "name": "Instant Pot Duo 7-in-1",         "category": "Kitchen"},
    {"id": "biz_003", "name": "Kindle Paperwhite",              "category": "Electronics"},
    {"id": "biz_004", "name": "Ninja Air Fryer XL",             "category": "Kitchen"},
    {"id": "biz_005", "name": "Logitech MX Master 3 Mouse",     "category": "Electronics"},
    {"id": "biz_006", "name": "Hydro Flask Water Bottle",       "category": "Sports"},
    {"id": "biz_007", "name": "Casper Original Mattress",       "category": "Home"},
    {"id": "biz_008", "name": "Dyson V15 Vacuum",               "category": "Home"},
    {"id": "biz_009", "name": "Apple AirPods Pro",              "category": "Electronics"},
    {"id": "biz_010", "name": "Vitamix Blender 5200",           "category": "Kitchen"},
    {"id": "biz_011", "name": "Fitbit Charge 6",                "category": "Sports"},
    {"id": "biz_012", "name": "Nespresso Vertuo Coffee Maker",  "category": "Kitchen"},
]


def _seed_reviews(n_genuine: int = 300, n_fake: int = 80, seed: int = 99) -> pd.DataFrame:
    """Generate a seeded review pool with known fake/genuine labels."""
    rng = np.random.default_rng(seed)
    records = []

    # Genuine reviews: normally distributed ratings per product
    true_ratings = {p["id"]: rng.uniform(3.2, 4.6) for p in PRODUCTS}
    for _ in range(n_genuine):
        prod = PRODUCTS[int(rng.integers(0, len(PRODUCTS)))]
        true_avg = true_ratings[prod["id"]]
        rating = float(np.clip(rng.normal(true_avg, 0.7), 1, 5))
        records.append({
            "product_id":   prod["id"],
            "rating":       round(rating * 2) / 2,
            "is_fake":      False,
            "reviewer_id":  f"user_{rng.integers(1000, 9999)}",
        })

    # Fake reviews: always 5 stars, concentrated on a few products (paid campaigns)
    boosted = [p["id"] for p in PRODUCTS[:4]]  # first 4 products are "boosted"
    for _ in range(n_fake):
        prod_id = boosted[int(rng.integers(0, len(boosted)))]
        records.append({
            "product_id":   prod_id,
            "rating":       5.0,
            "is_fake":      True,
            "reviewer_id":  f"bot_{rng.integers(1000, 9999)}",
        })

    return pd.DataFrame(records)


def get_recommendations(top_n: int = 6) -> dict:
    """
    Returns product recommendations with and without fake reviews.
    Shows how fake reviews distort rankings.
    """
    df = _seed_reviews()
    product_map = {p["id"]: p for p in PRODUCTS}

    def rank_products(review_df: pd.DataFrame) -> list:
        stats = (
            review_df.groupby("product_id")["rating"]
            .agg(avg_rating="mean", review_count="count")
            .reset_index()
        )
        # Bayesian average: weight toward global mean for low-count products
        global_mean = review_df["rating"].mean()
        m = 5  # min reviews for full weight
        stats["bayesian_score"] = (
            (stats["review_count"] * stats["avg_rating"] + m * global_mean)
            / (stats["review_count"] + m)
        )
        stats = stats.sort_values("bayesian_score", ascending=False).head(top_n)

        results = []
        for _, row in stats.iterrows():
            prod = product_map.get(row["product_id"], {})
            results.append({
                "product_id":     row["product_id"],
                "name":           prod.get("name", row["product_id"]),
                "category":       prod.get("category", "Unknown"),
                "avg_rating":     round(float(row["avg_rating"]), 2),
                "review_count":   int(row["review_count"]),
                "bayesian_score": round(float(row["bayesian_score"]), 3),
            })
        return results

    with_fake    = rank_products(df)
    without_fake = rank_products(df[df["is_fake"] == False])

    # Compute rank changes
    rank_map_before = {r["product_id"]: i + 1 for i, r in enumerate(with_fake)}
    rank_map_after  = {r["product_id"]: i + 1 for i, r in enumerate(without_fake)}

    for r in without_fake:
        before = rank_map_before.get(r["product_id"], top_n + 1)
        after  = rank_map_after[r["product_id"]]
        r["rank_change"] = before - after   # positive = moved up after cleaning

    fake_count   = int(df["is_fake"].sum())
    genuine_count = int((~df["is_fake"]).sum())

    return {
        "with_fake":     with_fake,
        "without_fake":  without_fake,
        "fake_count":    fake_count,
        "genuine_count": genuine_count,
        "total_reviews": len(df),
    }
