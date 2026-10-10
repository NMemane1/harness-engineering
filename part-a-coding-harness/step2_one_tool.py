#!/usr/bin/env python3
"""
Part A — Step 2: give the model its first tool.

This is the conceptual heart of a harness: the model can now *request an action*
(a shell command) via function/tool calling, we execute it, feed the result back,
and let the model continue. One tool, one loop — still stdlib only.

Run:
    export OPENROUTER_API_KEY=sk-or-...
    python3 step2_one_tool.py "list the python files here and count their lines"
"""
import json
import os
import subprocess
import sys
import urllib.request

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.environ.get("HARNESS_MODEL", "deepseek/deepseek-chat")

# One tool, described in the OpenAI function-calling schema the model understands.
TOOLS = [{
    "type": "function",
    "function": {
        "name": "run_bash",
        "description": "Run a shell command in the current directory and return its output.",
        "parameters": {
            "type": "object",
            "properties": {"command": {"type": "string", "description": "The shell command"}},
            "required": ["command"],
        },
    },
}]


def call_model(messages):
    body = json.dumps({"model": MODEL, "messages": messages, "tools": TOOLS}).encode()
    req = urllib.request.Request(
        API_URL, data=body, method="POST",
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                 "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["choices"][0]["message"]


def run_bash(command):
    print(f"  ⚙  $ {command}")
    p = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
    return (p.stdout + p.stderr)[:4000] or "(no output)"


def main():
    task = " ".join(sys.argv[1:]) or "What files are in this directory?"
    messages = [
        {"role": "system", "content": "You are a coding agent. Use run_bash to inspect the system. "
                                       "When the task is done, reply with a final summary and no tool call."},
        {"role": "user", "content": task},
    ]
    for step in range(10):  # cap the loop so it can't run forever
        msg = call_model(messages)
        messages.append(msg)
        tool_calls = msg.get("tool_calls")
        if not tool_calls:
            print(f"\n✅ {msg.get('content', '')}")
            return
        for tc in tool_calls:
            args = json.loads(tc["function"]["arguments"])
            result = run_bash(args["command"])
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
    print("\n⚠ hit step limit")


if __name__ == "__main__":
    main()
