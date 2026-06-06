import pandas as pd
import numpy as np
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent.parent.parent / "data" / "sample" / "reviews_sample.csv"


def generate_sample_data(n_genuine=400, n_fake=100, seed=42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    genuine_texts = [
        "Great product, works exactly as described. Would buy again.",
        "Solid quality, arrived on time. Minor scratches on packaging but product is fine.",
        "Average experience. Nothing special but does the job.",
        "Really happy with this purchase. Exceeded expectations.",
        "Not bad for the price. Some features missing but overall okay.",
    ]
    fake_texts = [
        "BEST PRODUCT EVER!!! AMAZING!!! BUY NOW!!! FIVE STARS!!!",
        "Absolutely perfect in every way! Cannot find a single flaw! Perfect!!!",
        "This changed my life! Best purchase I have ever made! Incredible!!!",
        "WOW WOW WOW!! Super super super great product!!!! Love it!!!!!",
        "Perfect perfect perfect! Best seller! Must buy! Amazing quality!",
    ]

    records = []

    for i in range(n_genuine):
        records.append({
            "reviewer_id": f"user_{rng.integers(1000, 9999)}",
            "product_id": f"prod_{rng.integers(100, 999)}",
            "review_text": genuine_texts[i % len(genuine_texts)],
            "rating": float(rng.choice([3, 4, 4, 5])),
            "verified_purchase": bool(rng.choice([True, True, False])),
            "review_count": int(rng.integers(5, 200)),
            "days_since_joined": int(rng.integers(30, 2000)),
            "helpful_votes": int(rng.integers(0, 50)),
            "is_fake": 0,
        })

    for i in range(n_fake):
        records.append({
            "reviewer_id": f"bot_{rng.integers(1000, 9999)}",
            "product_id": f"prod_{rng.integers(100, 999)}",
            "review_text": fake_texts[i % len(fake_texts)],
            "rating": 5.0,
            "verified_purchase": False,
            "review_count": int(rng.integers(1, 5)),
            "days_since_joined": int(rng.integers(1, 30)),
            "helpful_votes": 0,
            "is_fake": 1,
        })

    df = pd.DataFrame(records).sample(frac=1, random_state=seed).reset_index(drop=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} sample reviews to {OUTPUT_PATH}")
    return df


if __name__ == "__main__":
    generate_sample_data()
