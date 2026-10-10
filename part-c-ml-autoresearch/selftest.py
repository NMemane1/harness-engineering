#!/usr/bin/env python3
"""
Offline self-test for the autoresearch engine — NO API key needed.

Instead of asking a model for candidates, we feed three HAND-WRITTEN candidate
scripts of increasing quality (a broken one, a weak baseline, a strong model) and
confirm the harness: (1) runs each in the sandbox, (2) parses the real CV metric,
(3) captures the failure, and (4) selects the best-scoring working solution on the
real churn dataset.

Run:
    python3 selftest.py
"""
import os
from autoresearch.experiment import run_candidate

DATA = os.path.join(os.path.dirname(__file__), "tasks", "customer_churn", "train.csv")

BROKEN = "import pandas as pd\nraise ValueError('oops, undefined column')\n"

BASELINE = r'''
import os, json, pandas as pd, numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
df = pd.read_csv(os.environ["DATA_PATH"])
X = df.drop(columns=["churn"]); y = df["churn"]
cv = StratifiedKFold(5, shuffle=True, random_state=0)
auc = cross_val_score(LogisticRegression(max_iter=1000), X, y, cv=cv, scoring="roc_auc").mean()
json.dump({"val_metric": float(auc)}, open(os.environ["RESULT_PATH"], "w"))
print("baseline AUC", round(auc, 4))
'''

STRONG = r'''
import os, json, pandas as pd, numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score
df = pd.read_csv(os.environ["DATA_PATH"]).drop(columns=["noise_a", "noise_b"])
# engineered features that expose the data's nonlinear structure to a linear model:
df["age_u"] = (df["age"] - 45) ** 2                              # U-shaped age effect
df["m2m_charges"] = (df["contract_type"] == 0) * df["monthly_charges"]   # contract x charges
df["oneyr_charges"] = (df["contract_type"] == 1) * df["monthly_charges"]
X = df.drop(columns=["churn"]); y = df["churn"]
cv = StratifiedKFold(5, shuffle=True, random_state=0)
m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
auc = cross_val_score(m, X, y, cv=cv, scoring="roc_auc").mean()
json.dump({"val_metric": float(auc)}, open(os.environ["RESULT_PATH"], "w"))
print("engineered AUC", round(auc, 4))
'''


def main():
    assert os.path.exists(DATA), "run tasks/customer_churn/make_data.py first"
    results = {}
    for name, code in [("broken", BROKEN), ("baseline", BASELINE), ("strong", STRONG)]:
        r = run_candidate(code, DATA, timeout=90)
        status = f"AUC {r.metric:.4f}" if r.ok else f"FAILED ({r.log.splitlines()[-1][:50]})"
        print(f"  candidate '{name}': {status}")
        results[name] = r

    assert not results["broken"].ok, "broken candidate should have failed"
    assert results["baseline"].ok and results["strong"].ok
    best = max((r for r in results.values() if r.ok), key=lambda r: r.metric)
    assert best is results["strong"], "harness should pick the engineered model"
    gain = results["strong"].metric - results["baseline"].metric
    assert gain > 0.01, "engineered features should measurably beat the baseline"
    print(f"\n\033[32m\033[1mPASS\033[0m — harness ran real experiments and selected the best:")
    print(f"  • broken candidate correctly caught as a failure")
    print(f"  • baseline AUC {results['baseline'].metric:.4f} → engineered AUC "
          f"{results['strong'].metric:.4f}  (+{gain:.4f} from feature engineering)")
    print(f"  • selected: engineered model")


if __name__ == "__main__":
    main()
