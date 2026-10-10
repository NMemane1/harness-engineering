"""The agentic loop: the part that makes it a *harness*, not just a chatbot.

The loop is deliberately simple and auditable:
    1. send conversation + tool schemas to the model
    2. if the model returns tool calls, run each (through a safety guard), append
       the results, and loop
    3. if it returns plain text, that's the final answer — stop
A step cap bounds cost and prevents runaways.
"""
import json
from . import tools
from .llm import LLM

SYSTEM_PROMPT = """You are a capable coding agent operating in a real workspace.

You have tools: list_dir, read_file, write_file, edit_file, run_bash.
Principles:
- Investigate before you act: read files / list dirs before editing.
- Make the smallest change that solves the task; prefer edit_file over rewriting.
- After writing code, run it (run_bash) to verify it works.
- Think step by step, call one or a few tools at a time, and check results.
- When the task is complete and verified, reply with a short final summary and NO tool call.
"""

# ANSI colors
C = dict(dim="\033[2m", b="\033[1m", g="\033[32m", y="\033[33m",
         c="\033[36m", r="\033[31m", x="\033[0m")


class Agent:
    def __init__(self, model=None, max_steps=25, approve=None, verbose=True):
        self.llm = LLM(model=model)
        self.max_steps = max_steps
        self.verbose = verbose
        # approve(name, args) -> bool. Default: auto-approve (non-interactive).
        self.approve = approve or (lambda name, args: True)
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def _log(self, *a):
        if self.verbose:
            print(*a)

    def run(self, task):
        self.messages.append({"role": "user", "content": task})
        self._log(f"{C['b']}▶ task:{C['x']} {task}\n")
        for step in range(1, self.max_steps + 1):
            msg = self.llm.chat(self.messages, tools=tools.SCHEMAS)
            self.messages.append(msg)
            calls = msg.get("tool_calls") or []
            if not calls:
                final = msg.get("content", "").strip()
                self._log(f"\n{C['g']}{C['b']}✓ done{C['x']} "
                          f"{C['dim']}({step} steps, ~${self.llm.cost_estimate():.4f}, "
                          f"{self.llm.prompt_tokens + self.llm.completion_tokens} tokens){C['x']}")
                return final
            for tc in calls:
                name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"] or "{}")
                except json.JSONDecodeError:
                    args = {}
                self._log(f"{C['c']}  ⚙ {name}{C['x']} {C['dim']}{_preview(args)}{C['x']}")
                if name in tools.MUTATING and not self.approve(name, args):
                    result = "DENIED by user. Choose a different approach."
                else:
                    result = tools.dispatch(name, args)
                self._log(f"{C['dim']}    → {result.splitlines()[0][:100] if result else ''}{C['x']}")
                self.messages.append(
                    {"role": "tool", "tool_call_id": tc["id"], "content": result})
        return f"{C['y']}⚠ reached step limit ({self.max_steps}).{C['x']}"


def _preview(args):
    s = json.dumps(args)
    return s if len(s) < 90 else s[:87] + "…"
