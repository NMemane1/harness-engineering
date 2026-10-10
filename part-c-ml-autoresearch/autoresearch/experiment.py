"""Sandboxed experiment runner — the part that makes autoresearch *empirical*.

A candidate "solution" is a self-contained Python script. We run it in its own
temp working directory as a subprocess with a timeout, passing the dataset path
and a result path via environment variables. The script must write
{"val_metric": float} to RESULT_PATH. We read that back. If the script crashes,
we capture the traceback so the researcher can debug it next round.
"""
from __future__ import annotations   # allow `float | None` annotations on Python 3.9
import json
import os
import subprocess
import tempfile
from dataclasses import dataclass


@dataclass
class RunResult:
    ok: bool
    metric: float | None
    log: str          # stdout+stderr (truncated), fed back to the model on failure
    code: str


def run_candidate(code: str, data_path: str, timeout: int = 120) -> RunResult:
    workdir = tempfile.mkdtemp(prefix="ar-run-")
    script = os.path.join(workdir, "solution.py")
    result_path = os.path.join(workdir, "result.json")
    with open(script, "w") as f:
        f.write(code)

    env = dict(os.environ, DATA_PATH=os.path.abspath(data_path),
               RESULT_PATH=result_path, PYTHONWARNINGS="ignore")
    try:
        p = subprocess.run(["python3", script], cwd=workdir, env=env,
                           capture_output=True, text=True, timeout=timeout)
        log = (p.stdout + p.stderr)[-3000:]
    except subprocess.TimeoutExpired:
        return RunResult(False, None, f"TIMEOUT after {timeout}s", code)

    if not os.path.exists(result_path):
        return RunResult(False, None,
                         f"(exit {p.returncode}) no result.json written.\n{log}", code)
    try:
        metric = float(json.load(open(result_path))["val_metric"])
    except Exception as e:
        return RunResult(False, None, f"bad result.json: {e}\n{log}", code)
    return RunResult(True, metric, log, code)
