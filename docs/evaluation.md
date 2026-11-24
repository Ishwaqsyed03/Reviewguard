# Detector evaluation

## Run the benchmark

From the repository root, install the Python dependencies and run:

```bash
python scripts/evaluate_detector.py
```

The script reads `data/processed/real_reviews.csv`, uses the same feature extraction and model factory as the API, and prints JSON with fake-class precision, recall, F1, ROC-AUC, and a confusion matrix. It also reports a majority-class baseline.

The split keeps exact duplicate genuine reviews together and groups generated fake reviews by normalized template family. This avoids placing the same generated template in both train and test sets. The script fits the model in memory and does not replace `models/trained/detector.pkl`.

## What the result means

The checked-in dataset is a hybrid demonstration dataset: genuine-labeled Yelp polarity reviews are paired with fake reviews generated from a small set of templates in `backend/utils/real_dataset.py`. Reviewer attributes for these rows are generated too. The Yelp labels describe sentiment polarity classes; they do not establish that a review is genuine.

A grouped split measures whether the model can recognize generated fake-template families it did not see during training. It does **not** measure real-world fake-review detection, and its scores must not be presented as production accuracy. The fake class has limited linguistic diversity, so the model may learn artifacts of the generator.

## Before claiming real-world performance

A stronger benchmark needs independently collected and human-labeled deceptive and genuine reviews, clear source and license documentation, and splits that separate authors, products, campaigns, and data sources. Report false-positive and false-negative counts alongside summary metrics. Keep this generated-template benchmark as a separate stress test rather than combining it with real-world results.
