"""The autoresearch loop: propose → run → evaluate → reflect → keep the best.

This is a compact, AIDE-style (see WecoAI/awesome-autoresearch) greedy tree
search over *executable* solutions. Each iteration the model either improves the
best working solution so far or debugs the last failure, using the real metric /
traceback from the sandbox as feedback. The empirical loop — not the model alone —
is what finds a good model.
"""
from __future__ import annotations
import json
import os
import time
from dataclasses import dataclass, asdict
from .experiment import run_candidate, RunResult
from .llm import LLM, extract_code

C = dict(b="\033[1m", g="\033[32m", y="\033[33m", c="\033[36m", r="\033[31m",
         dim="\033[2m", x="\033[0m")

SYSTEM = """You are an expert ML research engineer running an automated experiment loop.
You write a SINGLE self-contained Python script each turn. Rules for the script:
- Read the CSV from os.environ['DATA_PATH']; target column is given in the task.
- Use scikit-learn / pandas / numpy (already installed). No internet, no extra installs.
- Estimate performance with 5-fold StratifiedKFold cross-validation (ROC-AUC).
- Write {"val_metric": <auc_float>} as JSON to os.environ['RESULT_PATH'].
- Print one concise line with the CV AUC. Keep runtime under ~60s.
Reply with ONLY one ```python code block, no prose."""


@dataclass
class Node:
    step: int
    metric: float | None
    ok: bool
    summary: str


def _build_prompt(task_desc, best: RunResult | None, last: RunResult | None):
    parts = [f"TASK:\n{task_desc}\n"]
    if best and best.ok:
        parts.append(f"BEST SOLUTION SO FAR (CV AUC = {best.metric:.4f}):\n"
                     f"```python\n{best.code}\n```\n"
                     "Improve it: better model, feature engineering, drop noise columns, "
                     "tune hyperparameters, handle the class imbalance. Keep what works.")
    if last and not last.ok:
        parts.append(f"The LAST attempt FAILED with this log — fix it:\n{last.log[-1500:]}")
    if not best:
        parts.append("Start with a clean, correct baseline (e.g. a gradient-boosting "
                     "classifier with basic preprocessing) that satisfies the contract.")
    return "\n\n".join(parts)


class Researcher:
    def __init__(self, model=None, steps=6, timeout=120, verbose=True):
        self.llm = LLM(model=model)
        self.steps = steps
        self.timeout = timeout
        self.verbose = verbose

    def _log(self, *a):
        if self.verbose:
            print(*a)

    def run(self, task_dir):
        task_desc = open(os.path.join(task_dir, "task.md")).read()
        data_path = os.path.join(task_dir, "train.csv")
        best: RunResult | None = None
        last: RunResult | None = None
        journal: list[Node] = []

        self._log(f"{C['b']}🔬 Autoresearch on {os.path.basename(task_dir)} "
                  f"· model={self.llm.model} · {self.steps} steps{C['x']}\n")
        for step in range(1, self.steps + 1):
            prompt = _build_prompt(task_desc, best, last)
            reply = self.llm.complete(SYSTEM, prompt)
            code = extract_code(reply)
            t0 = time.time()
            res = run_candidate(code, data_path, timeout=self.timeout)
            dt = time.time() - t0
            last = res

            if res.ok:
                improved = best is None or res.metric > best.metric
                tag = f"{C['g']}AUC {res.metric:.4f}{C['x']}" + (
                    f" {C['g']}★ new best{C['x']}" if improved else f" {C['dim']}(no gain){C['x']}")
                if improved:
                    best = res
                summary = f"ran ok, AUC={res.metric:.4f}"
            else:
                tag = f"{C['r']}failed{C['x']} {C['dim']}{res.log.splitlines()[-1][:60] if res.log else ''}{C['x']}"
                summary = "failed: " + (res.log.splitlines()[-1][:80] if res.log else "")
            self._log(f"  step {step}/{self.steps} {C['dim']}({dt:.1f}s){C['x']}  {tag}")
            journal.append(Node(step, res.metric, res.ok, summary))

        self._log(f"\n{C['b']}{C['g']}✓ best CV AUC = "
                  f"{best.metric:.4f}{C['x']}" if best else f"\n{C['r']}no working solution{C['x']}")
        return best, journal

    def write_report(self, task_dir, best: RunResult, journal, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        if best:
            with open(os.path.join(out_dir, "best_solution.py"), "w") as f:
                f.write(best.code)
        with open(os.path.join(out_dir, "journal.json"), "w") as f:
            json.dump([asdict(n) for n in journal], f, indent=2)
        lines = ["# Autoresearch Report", "",
                 f"Task: `{os.path.basename(task_dir)}`  ",
                 f"Model: `{self.llm.model}`  ·  Tokens: {self.llm.tokens}", "",
                 "## Trajectory", "", "| Step | Status | CV AUC |", "|---|---|---|"]
        for n in journal:
            lines.append(f"| {n.step} | {'ok' if n.ok else 'failed'} | "
                         f"{n.metric:.4f} |" if n.metric is not None else
                         f"| {n.step} | {'ok' if n.ok else 'failed'} | — |")
        if best:
            lines += ["", f"## Best solution — CV AUC {best.metric:.4f}", "",
                      "```python", best.code, "```"]
        with open(os.path.join(out_dir, "report.md"), "w") as f:
            f.write("\n".join(lines))
        self._log(f"{C['dim']}report → {out_dir}/report.md{C['x']}")
