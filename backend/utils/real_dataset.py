"""
Hybrid dataset: real Yelp reviews (genuine) + research-pattern fake reviews.

Method:
  - Genuine: 1500 real Yelp reviews from HuggingFace yelp_polarity dataset
  - Fake: 500 reviews generated using patterns from academic literature
    (Jindal & Liu 2008, Lim et al. 2010, Mukherjee et al. 2012)

Fake patterns used:
  - Burstiness: many reviews in short time, new account
  - Linguistic: excessive punctuation, superlatives, low content diversity
  - Rating: extreme 5-star with no verified purchase
"""
import pandas as pd
import numpy as np
from pathlib import Path

PROCESSED_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "real_reviews.csv"

FAKE_TEMPLATES = [
    "BEST {product} EVER!!! Absolutely AMAZING!!! Must buy immediately!!!",
    "This {product} changed my life! Perfect in every way! Five stars!!!",
    "Incredible {product}! I love love love it! Best purchase EVER!!!",
    "WOW just WOW! This {product} is PERFECT! Buy it NOW you will NOT regret!",
    "Amazing quality! Fast shipping! GREAT {product}! 100% recommend!!!!",
    "FANTASTIC {product}! Exceeded ALL expectations! Will buy again and again!",
    "Super super great {product}! Best seller! Number one! Perfect perfect!",
    "Love this {product} so much! Perfect perfect perfect! Five stars always!",
    "Absolutely wonderful {product}! The BEST on the market! Buy it today!!",
    "This {product} is simply OUTSTANDING! Better than I ever imagined!! 5 stars!",
    "GREAT product arrived fast works perfect love it would buy again 5 stars!",
    "Best product I have ever purchased in my entire life! Highly recommended!!!",
    "This is THE product everyone needs! Perfect! Amazing! Incredible! BUY NOW!",
    "I am so happy with this {product}! Perfect condition! Super fast delivery!!!",
    "Outstanding quality! Best {product} on the market! Absolutely love it!!!!",
]

PRODUCTS = [
    "product", "item", "purchase", "blender", "headphones",
    "phone case", "watch", "mattress", "coffee maker", "vacuum",
]


def _generate_fake_reviews(n: int, rng: np.random.Generator) -> list:
    records = []
    for i in range(n):
        template = FAKE_TEMPLATES[int(rng.integers(0, len(FAKE_TEMPLATES)))]
        product  = PRODUCTS[int(rng.integers(0, len(PRODUCTS)))]
        text     = template.format(product=product)

        records.append({
            "reviewer_id":       f"bot_{rng.integers(1000, 9999)}",
            "product_id":        f"biz_{rng.integers(1, 200):03d}",
            "review_text":       text,
            "rating":            5.0,
            "verified_purchase": False,
            "review_count":      int(rng.integers(1, 5)),
            "days_since_joined": int(rng.integers(1, 25)),
            "helpful_votes":     0,
            "is_fake":           1,
        })
    return records


def download_and_process(n_genuine: int = 1500, n_fake: int = 500) -> pd.DataFrame:
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)

    print("Loading real Yelp reviews from HuggingFace datasets (genuine set)...")
    from datasets import load_dataset
    ds   = load_dataset("yelp_polarity", split="train")
    df_hf = ds.to_pandas().sample(n=min(n_genuine, len(ds)), random_state=42)

    genuine_records = []
    for _, row in df_hf.iterrows():
        stars = int(row["label"]) + 1
        genuine_records.append({
            "reviewer_id":       f"user_{rng.integers(1000, 9999)}",
            "product_id":        f"biz_{rng.integers(1, 200):03d}",
            "review_text":       str(row["text"])[:800],
            "rating":            float(stars),
            "verified_purchase": bool(rng.random() > 0.25),
            "review_count":      int(rng.integers(10, 300)),
            "days_since_joined": int(rng.integers(60, 3000)),
            "helpful_votes":     int(rng.integers(0, 80)),
            "is_fake":           0,
        })

    print(f"Generating {n_fake} fake reviews using research-backed patterns...")
    fake_records = _generate_fake_reviews(n_fake, rng)

    df = pd.DataFrame(genuine_records + fake_records).sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(PROCESSED_PATH, index=False)

    fake    = int(df["is_fake"].sum())
    genuine = len(df) - fake
    print(f"Saved {len(df)} reviews ({fake} fake / {genuine} genuine) -> {PROCESSED_PATH}")
    return df


def load_real_dataset() -> pd.DataFrame:
    if PROCESSED_PATH.exists():
        print(f"Loading cached dataset from {PROCESSED_PATH}")
        return pd.read_csv(PROCESSED_PATH)
    return download_and_process()


if __name__ == "__main__":
    df = download_and_process()
    print(df["is_fake"].value_counts())
    print(df.head(3))
