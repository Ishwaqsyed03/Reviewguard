"""
Generates review bombing timeline data.
Simulates a realistic attack: normal reviews for weeks, then a sudden
coordinated spike of fake 5-star reviews over 48 hours.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

PRODUCTS = [
    {"id": "biz_001", "name": "Sony WH-1000XM5 Headphones"},
    {"id": "biz_004", "name": "Ninja Air Fryer XL"},
    {"id": "biz_009", "name": "Apple AirPods Pro"},
]


def generate_timeline(product_id: str = "biz_001", days: int = 90, seed: int = 42) -> dict:
    rng   = np.random.default_rng(seed)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=days)

    product = next((p for p in PRODUCTS if p["id"] == product_id), PRODUCTS[0])

    # Bombing window: days 55–57 (recent enough to be visible, not at the end)
    bomb_start_day = 55
    bomb_end_day   = 57

    records = []

    # --- Genuine reviews spread across the full period ---
    genuine_true_rating = rng.uniform(3.8, 4.3)
    for day_offset in range(days):
        n_reviews = int(rng.poisson(2.5))  # avg 2-3 genuine reviews/day
        for _ in range(n_reviews):
            hour    = int(rng.integers(8, 22))
            minute  = int(rng.integers(0, 60))
            ts      = start + timedelta(days=day_offset, hours=hour, minutes=minute)
            rating  = float(np.clip(rng.normal(genuine_true_rating, 0.8), 1, 5))
            rating  = round(rating * 2) / 2
            records.append({
                "timestamp": ts,
                "rating":    rating,
                "is_fake":   False,
                "day_offset": day_offset,
            })

    # --- Bombing event: 40–60 fake 5-star reviews in 48 hours ---
    n_fake = int(rng.integers(40, 60))
    for _ in range(n_fake):
        day_offset = rng.integers(bomb_start_day, bomb_end_day + 1)
        hour       = int(rng.integers(0, 24))
        minute     = int(rng.integers(0, 60))
        ts         = start + timedelta(days=int(day_offset), hours=hour, minutes=minute)
        records.append({
            "timestamp":  ts,
            "rating":     5.0,
            "is_fake":    True,
            "day_offset": int(day_offset),
        })

    df = pd.DataFrame(records).sort_values("timestamp").reset_index(drop=True)

    # Rolling 7-day average rating (all reviews)
    df["date"] = df["timestamp"].dt.date
    daily = df.groupby("date").agg(
        avg_rating=("rating", "mean"),
        total=("rating", "count"),
        fake_count=("is_fake", "sum"),
    ).reset_index()
    daily["date"] = daily["date"].astype(str)

    # Rating with vs without fake reviews
    daily_genuine = df[~df["is_fake"]].groupby("date")["rating"].mean().reset_index()
    daily_genuine.columns = ["date", "genuine_avg"]
    daily_genuine["date"] = daily_genuine["date"].astype(str)
    daily = daily.merge(daily_genuine, on="date", how="left")

    bomb_start_date = (start + timedelta(days=bomb_start_day)).date().isoformat()
    bomb_end_date   = (start + timedelta(days=bomb_end_day + 1)).date().isoformat()

    return {
        "product":         product,
        "bomb_start":      bomb_start_date,
        "bomb_end":        bomb_end_date,
        "total_genuine":   int((~df["is_fake"]).sum()),
        "total_fake":      int(df["is_fake"].sum()),
        "rating_during_bomb":  round(float(df[df["is_fake"]]["rating"].mean()), 2),
        "rating_genuine_only": round(float(df[~df["is_fake"]]["rating"].mean()), 2),
        "daily": daily.to_dict(orient="records"),
        "events": [
            {
                "timestamp": r["timestamp"].isoformat(),
                "rating":    r["rating"],
                "is_fake":   bool(r["is_fake"]),
            }
            for _, r in df.iterrows()
        ],
    }
