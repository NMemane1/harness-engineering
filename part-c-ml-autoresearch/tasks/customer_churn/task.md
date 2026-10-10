# Task: Customer Churn Prediction

**Goal:** Train the best possible binary classifier to predict `churn` (0/1).

**Data:** `train.csv` — 800 rows, 9 feature columns + `churn` target.
Two columns (`noise_a`, `noise_b`) are irrelevant distractors. There are
nonlinear interactions (e.g. fiber customers with high charges churn more).

**Metric:** ROC-AUC, estimated with 5-fold stratified cross-validation on `train.csv`.

**Contract for each candidate solution (a self-contained Python script):**
- Read `train.csv` from the path given in the environment variable `DATA_PATH`.
- Do any feature engineering / model choice you like (scikit-learn is available).
- Compute 5-fold stratified CV ROC-AUC.
- Write the result as JSON to the path in `RESULT_PATH`: `{"val_metric": <float>}`.
- Print a one-line summary. Must finish within the time limit.

The autoresearch harness runs each candidate, reads `val_metric`, and keeps the
best. A trivial baseline (plain LogisticRegression, no engineering) scores ~0.80 AUC;
good solutions (gradient boosting + interaction features, dropping noise) reach ~0.88+.
