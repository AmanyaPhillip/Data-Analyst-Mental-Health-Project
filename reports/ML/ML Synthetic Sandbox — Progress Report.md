# ML Synthetic Sandbox — Progress Report

## Overview

The `05_ml_synthetic_sandbox.ipynb` notebook has been completed and runs cleanly **end-to-end with 0 errors**.

The notebook provides a complete machine-learning workflow using the synthetic mental-health dataset, from data exploration and preprocessing through model training, evaluation, interpretation, and model export.

As part of this work, the required `scikit-learn` and `joblib` packages were installed and added to `requirements.txt`.

---

## What Was Completed

### 1. Setup

- Imported the required libraries.
- Added a `find_root()` helper for reliable project-path handling.
- Set `RANDOM_STATE = 42` for reproducibility.
- Configured the `models/` directory for saved model artifacts.

### 2. Data Exploration

The dataset was examined to understand its structure and quality, including:

- Dataset shape and data types
- Missing values
- Duplicate records
- Target-class distribution
- Numeric summary statistics
- Correlations with the target
- Grouped means
- Categorical cross-tabulations

The `mental_health_risk` target is imbalanced:

| Risk Level | Distribution |
|---|---:|
| Medium | 59% |
| High | 24% |
| Low | 17% |

This imbalance was taken into consideration during the modelling process.

### 3. Feature Binning

Several variables were converted into interpretable bands using:

- `pd.cut()` for fixed ranges:
  - Age
  - Sleep
  - Activity
  - Depression
  - Anxiety
- `pd.qcut()` for social-support tertiles

Risk rates were then calculated by each band and visualized using stacked bar charts.

### 4. Train / Validation / Test Split

The data was divided using a **stratified 60 / 20 / 20 split**:

- 60% training
- 20% validation
- 20% testing

Class distributions were printed for each dataset to verify that the target imbalance was preserved.

### 5. Machine-Learning Pipeline

A reusable preprocessing and modelling pipeline was implemented using `ColumnTransformer`.

The pipeline:

1. Scales numeric features.
2. One-hot encodes categorical features.
3. Trains and evaluates multiple models.

Models tested:

- Dummy Classifier
- Logistic Regression
- Random Forest
- HistGradientBoosting

A validation comparison table was created to compare model performance.

### 6. Model Interpretation

Permutation importance was calculated on the validation set to understand which features contributed to the model's predictions.

The strongest features were:

| Feature | Approx. Importance |
|---|---:|
| Depression score | 0.57 |
| Anxiety score | 0.44 |
| Other features | ≈ 0 |

This showed that the model's predictions were overwhelmingly driven by depression and anxiety scores.

### 7. Final Test Evaluation

After model selection, the best-performing model was evaluated **once on the held-out test set**.

The model achieved approximately **100% macro-F1** on the synthetic target.

### 8. Model Artifacts

The trained model and evaluation metrics were saved:

- `models/05_mental_health_risk_model.joblib`
- `models/05_metrics.json`

The `.joblib` model files are excluded from Git because they are binary artifacts, while the JSON metrics file is tracked.

### 9. Treatment-Seeking Contrast

The same modelling pipeline was also tested against `seeks_treatment`.

The result showed essentially no useful predictive signal:

- Random Forest: **0.582**
- Dummy baseline: **0.601**

Since the model did not outperform the baseline, there is no meaningful evidence that `seeks_treatment` can be predicted from the available synthetic features.

### 10. Findings and Caveats

The most important finding is that the near-perfect `mental_health_risk` performance **does not represent a genuinely strong machine-learning model**.

The synthetic data generator creates the `mental_health_risk` target almost directly from:

- Depression score
- Anxiety score
- Productivity score

Therefore, the model is effectively learning the formula used to generate the target.

The notebook explicitly documents this limitation and makes clear that:

> A near-perfect score on this synthetic dataset means the target is largely a formula of the input variables, rather than demonstrating real-world predictive performance.

For the real MHACS data, we should expect the relationships to be **weaker, noisier, and more realistic**.

---

## Key Takeaways

1. The ML sandbox notebook is complete and runs successfully with **0 errors**.
2. The full ML workflow has been implemented from EDA through model export.
3. The synthetic `mental_health_risk` target is almost perfectly predictable because of how the synthetic data was generated.
4. Depression and anxiety are the dominant predictors in the synthetic data.
5. Other demographic and lifestyle variables contributed essentially no additional predictive signal.
6. `seeks_treatment` did not outperform the baseline and therefore does not show useful predictive signal in this synthetic dataset.
7. The results should **not** be interpreted as real mental-health findings.
8. The notebook is now ready to be adapted/tested against the real MHACS dataset.

---

## Git / Repository Housekeeping

One issue was identified during the work:

### `data/raw/` is currently tracked by Git

The `data/raw/` directory contains approximately **69 MB** of data, including CSV files of approximately **36 MB** and **24 MB**.

This can significantly increase repository size and clone times. GitHub also warns when individual files exceed 50 MB.

If tracking the raw data is an intentional team decision, no action is required.

If it was added accidentally, the recommended cleanup is:

```bash
git rm -r --cached data/raw
```

Then restore the `data/raw/` rule in `.gitignore`.

The raw data should generally remain locally available while avoiding unnecessary storage of large datasets directly in the Git repository.