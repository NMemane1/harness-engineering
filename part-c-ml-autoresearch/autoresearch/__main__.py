import argparse, os, time
from .researcher import Researcher

def main():
    p = argparse.ArgumentParser(prog="autoresearch",
        description="Automated ML research loop over executable solutions (OpenRouter).")
    p.add_argument("--task", default="tasks/customer_churn", help="task directory (task.md + train.csv)")
    p.add_argument("--steps", type=int, default=6)
    p.add_argument("--model", default=os.environ.get("HARNESS_MODEL"))
    p.add_argument("--timeout", type=int, default=120)
    p.add_argument("--out", default=None, help="output dir (default runs/<timestamp>)")
    a = p.parse_args()
    out = a.out or os.path.join("runs", time.strftime("%Y%m%d-%H%M%S"))
    r = Researcher(model=a.model, steps=a.steps, timeout=a.timeout)
    best, journal = r.run(a.task)
    r.write_report(a.task, best, journal, out)

if __name__ == "__main__":
    main()
