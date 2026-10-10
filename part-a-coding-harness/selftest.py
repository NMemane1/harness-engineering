#!/usr/bin/env python3
"""
Offline self-test — proves the harness loop + tools actually execute, with NO
API key required. It swaps in a scripted "fake model" that emits tool calls in
sequence, then checks the real tools ran: a file is written to disk and a real
shell command runs it.

Run:
    python3 selftest.py
"""
import json
import os
import tempfile
import types

import coding_harness.tools as tools
from coding_harness.agent import Agent


def _tool_call(cid, name, args):
    return {"id": cid, "type": "function",
            "function": {"name": name, "arguments": json.dumps(args)}}


def main():
    workspace = tempfile.mkdtemp(prefix="harness-selftest-")
    tools.WORKSPACE = workspace  # point the tool belt at a throwaway dir

    # Scripted model: write fizzbuzz, run it, then finish.
    script = [
        {"role": "assistant", "content": None, "tool_calls": [_tool_call(
            "c1", "write_file", {"path": "fizzbuzz.py",
                                 "content": "for i in range(1,16):\n"
                                            "    print('FizzBuzz' if i%15==0 else "
                                            "'Fizz' if i%3==0 else 'Buzz' if i%5==0 else i)\n"})]},
        {"role": "assistant", "content": None, "tool_calls": [_tool_call(
            "c2", "run_bash", {"command": "python3 fizzbuzz.py"})]},
        {"role": "assistant", "content": "Created and ran fizzbuzz.py successfully."},
    ]

    agent = Agent.__new__(Agent)           # build without constructing a real LLM
    agent.max_steps = 10
    agent.verbose = True
    agent.approve = lambda name, args: True
    agent.messages = [{"role": "system", "content": "test"}]

    step = {"i": 0}
    fake_llm = types.SimpleNamespace(prompt_tokens=0, completion_tokens=0,
                                     cost_estimate=lambda: 0.0)

    def fake_chat(messages, tools=None):
        m = script[step["i"]]
        step["i"] += 1
        return m
    fake_llm.chat = fake_chat
    agent.llm = fake_llm

    result = agent.run("Write FizzBuzz (1..15) to fizzbuzz.py and run it.")

    # Assertions: did the real tools actually do the work?
    path = os.path.join(workspace, "fizzbuzz.py")
    assert os.path.exists(path), "write_file did not create the file"
    produced = open(path).read()
    assert "FizzBuzz" in produced, "file content wrong"
    # run the produced program ourselves to confirm it's valid and prints FizzBuzz
    import subprocess
    out = subprocess.run(["python3", path], capture_output=True, text=True).stdout
    assert out.strip().splitlines()[-1] == "FizzBuzz", f"program output wrong: {out!r}"
    assert "successfully" in result

    print("\n\033[32m\033[1mPASS\033[0m — harness loop executed real tools:")
    print(f"  • wrote {path}")
    print(f"  • program output tail: {out.strip().splitlines()[-3:]}")
    print(f"  • agent final message: {result}")


if __name__ == "__main__":
    main()
