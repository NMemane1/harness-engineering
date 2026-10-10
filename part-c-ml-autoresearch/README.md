# Part C — A Custom ML Autoresearch Harness

A harness that does **automated machine-learning research**: given a dataset and a goal, it
runs an empirical loop — *propose a solution → execute it → read the metric → reflect → improve* —
and keeps the best model it finds. Inspired by the autoresearch agents catalogued in
[WecoAI/awesome-autoresearch](https://github.com/WecoAI/awesome-autoresearch) (AIDE-style greedy
search over executable solutions), implemented from scratch on the OpenRouter API.

## What makes it a *harness* (not just a prompt)
The model only writes code; the **harness makes it empirical**:
1. **propose** — the model writes a single self-contained training script;
2. **execute** — the script runs in a sandboxed subprocess with a timeout
   ([`experiment.py`](./autoresearch/experiment.py)); it must write `{"val_metric": …}`;
3. **evaluate** — the harness reads the real cross-validated metric (or captures the traceback);
4. **reflect & improve** — the metric/error is fed back; the model improves the best solution;
5. **select** — the best-scoring working solution is kept; a report is written.

```
┌────────── researcher loop (greedy, N steps) ──────────┐
│  LLM writes script → sandbox runs it → metric/error    │
│         ▲                                   │          │
│         └────────── feedback (best + last) ─┘          │
└───────────────── keep best → report.md ────────────────┘
```

## The task it attacks
[`tasks/customer_churn/`](./tasks/customer_churn) — a synthetic but non-trivial churn dataset
(4,000 rows) with **broad nonlinear structure**: a continuous×categorical interaction (the effect
of monthly charges depends on contract type) and a **non-monotonic U-shaped age effect**, plus two
distractor columns. This is built so a plain linear baseline (~0.77 AUC) is clearly beaten by
feature engineering / tree models (~0.81+ AUC) — making the loop's improvements real and measurable.
Metric: 5-fold stratified CV **ROC-AUC**.

## Run it
```bash
pip install -r requirements.txt
python3 tasks/customer_churn/make_data.py          # regenerate the dataset (seeded)

export OPENROUTER_API_KEY=sk-or-...
python3 -m autoresearch --task tasks/customer_churn --steps 6
# → prints the trajectory and writes runs/<timestamp>/{report.md,best_solution.py,journal.json}
```

## Execution proof without a key
```bash
python3 selftest.py
```
Feeds three hand-written candidates (a broken one, a weak baseline, a strong engineered model)
through the real sandbox and confirms the harness runs them, parses the metric, catches the
failure, and selects the best. Local result:
```
candidate 'broken':   FAILED (ValueError: oops, undefined column)
candidate 'baseline': AUC 0.7710
candidate 'strong':   AUC 0.8088
PASS — baseline 0.7710 → engineered 0.8088 (+0.0378); selected the engineered model
```

## Extending it
Point it at a new problem by adding a `tasks/<name>/` folder with a `task.md` (the contract) and
a `train.csv`. The harness is dataset-agnostic — the task description tells the model the target
column and metric.
