"""Generate a realistic tabular churn dataset for the autoresearch harness to attack.

Signal is intentionally non-trivial (nonlinear interactions + noise + a couple of
weak/irrelevant columns) so that smarter modeling choices actually move the metric —
which is what makes the autoresearch loop's improvements visible.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
N = 5000


def make():
    tenure = rng.integers(0, 72, N)                       # months as customer
    monthly = rng.normal(70, 25, N).clip(15, 150)         # monthly charges
    contract = rng.choice([0, 1, 2], N, p=[.5, .3, .2])   # 0 month,1 year,2 two-year
    support_tickets = rng.poisson(1.2, N)
    has_fiber = rng.integers(0, 2, N)
    auto_pay = rng.integers(0, 2, N)
    age = rng.normal(45, 15, N).clip(18, 90)

    # Churn logit built from BROAD nonlinear structure that an additive linear
    # model provably under-fits but trees / engineered features capture:
    #   (1) a continuous x categorical INTERACTION — the effect of monthly charges
    #       depends on contract type (hurts month-to-month, neutral for 2-year);
    #   (2) a NON-MONOTONIC (U-shaped) age effect — the young and the old churn more.
    # Both apply to the whole population, so the AUC ceiling is high (~0.90) and the
    # linear-vs-tree / feature-engineering gap is large and reliable.
    m2m = (contract == 0).astype(float)
    one_yr = (contract == 1).astype(float)
    two_yr = (contract == 2).astype(float)
    logit = (
        -0.3
        # weak global main effects
        - 0.025 * tenure
        + 0.30 * support_tickets
        - 0.45 * auto_pay
        # (1) charges slope DEPENDS on contract (interaction)
        + m2m * (0.055 * (monthly - 60))
        + one_yr * (0.015 * (monthly - 60))
        + two_yr * (-1.4)                           # 2-year customers rarely churn
        + 0.7 * has_fiber * m2m
        # (2) U-shaped age effect (non-monotonic): min churn near 45
        + 0.0016 * (age - 45) ** 2
        + rng.normal(0, 0.40, N))                    # moderate noise
    p = 1 / (1 + np.exp(-logit))
    churn = (rng.random(N) < p).astype(int)

    df = pd.DataFrame({
        "tenure_months": tenure, "monthly_charges": monthly.round(2),
        "contract_type": contract, "support_tickets": support_tickets,
        "has_fiber": has_fiber, "auto_pay": auto_pay, "age": age.round(0),
        "noise_a": rng.normal(0, 1, N).round(3),           # irrelevant columns
        "noise_b": rng.integers(0, 5, N),
        "churn": churn,
    })
    return df


if __name__ == "__main__":
    df = make()
    ntr = 4000
    df.iloc[:ntr].to_csv("train.csv", index=False)
    df.iloc[ntr:].to_csv("test.csv", index=False)
    print(f"wrote train.csv ({(df.iloc[:ntr].churn.mean()*100):.0f}% churn, {ntr} rows) "
          f"and test.csv ({N-ntr} rows)")
