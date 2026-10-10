"""CLI entrypoint for the coding harness.

    python3 -m coding_harness -t "write fizzbuzz to fizz.py and run it"
    python3 -m coding_harness           # interactive REPL
    python3 -m coding_harness -t "..." --auto    # don't prompt for approval
"""
import argparse
import os
import sys
from .agent import Agent, C


def make_approver(auto):
    if auto:
        return lambda name, args: True

    def ask(name, args):
        print(f"{C['y']}  ⚠ approve {name}? {args}{C['x']}")
        return input("    [y/N] ").strip().lower() == "y"
    return ask


def main(argv=None):
    p = argparse.ArgumentParser(prog="coding_harness",
                                description="A from-scratch coding agent on OpenRouter.")
    p.add_argument("-t", "--task", help="run a single task and exit")
    p.add_argument("-m", "--model", default=os.environ.get("HARNESS_MODEL"),
                   help="OpenRouter model id (default deepseek/deepseek-chat)")
    p.add_argument("--max-steps", type=int, default=25)
    p.add_argument("--auto", action="store_true",
                   help="auto-approve mutating tools (write/edit/bash)")
    p.add_argument("-q", "--quiet", action="store_true")
    args = p.parse_args(argv)

    approve = make_approver(args.auto)

    def new_agent():
        return Agent(model=args.model, max_steps=args.max_steps,
                     approve=approve, verbose=not args.quiet)

    if args.task:
        print(new_agent().run(args.task))
        return

    print(f"{C['b']}Coding Harness{C['x']} {C['dim']}· interactive · "
          f"model={args.model or 'deepseek/deepseek-chat'} · 'exit' to quit{C['x']}\n")
    agent = new_agent()  # one agent keeps conversation memory across tasks
    while True:
        try:
            task = input(f"{C['b']}task ›{C['x']} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if task in {"exit", "quit"}:
            break
        if not task:
            continue
        print(agent.run(task), "\n")


if __name__ == "__main__":
    sys.exit(main())
