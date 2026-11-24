# Prediction explanations

The displayed label uses the classifier's predicted class. The same `is_fake` value is returned by the API and used for history and aggregate fake/genuine counts.

For each displayed feature, ReviewGuard compares the model's fake probability for the submitted inputs with a second prediction where only that feature is replaced by its training-set mean:

```
signal = probability(submitted inputs) - probability(inputs with one feature set to its training mean)
```

A positive signal means that observed feature value raised the model's fake probability relative to that reference; a negative signal means it lowered it. The signal is local to this one prediction. These comparisons are not causal, are not additive, and do not explain all interactions among features.

The probability is the model's output, not a calibrated estimate of the real-world chance that a review is fake. The current training data is synthetic in the fake class, so neither the label nor the displayed signals should be treated as proof about a real reviewer.
