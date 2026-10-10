# Part A — A Coding Harness, Built From Scratch (Progressively)

A real CLI **coding agent** built step by step on the **OpenRouter API** — using only the
Python standard library (no SDK, no framework). This shows what a "harness" actually is: a
loop that lets a model *read, write, and run code* through tools, check the results, and iterate.

## Why OpenRouter
OpenRouter is one OpenAI-compatible gateway in front of 300+ models (DeepSeek, Gemini, Claude,
GPT, Llama…). The same request body works for every model — you just change the `model` id — so
the harness is model-agnostic. Get a key at <https://openrouter.ai/keys>.

## The progression
| Step | File | What it adds |
|---|---|---|
| 1 | [`step1_chat.py`](./step1_chat.py) | Bare chat loop — prove we can talk to a model and keep context. |
| 2 | [`step2_one_tool.py`](./step2_one_tool.py) | **The key idea:** one tool (`run_bash`) + the tool-call loop. The model can now *act*. |
| 3 | [`coding_harness/`](./coding_harness) | Full harness: 5 tools, agentic loop, safety guard, token/cost tracking, REPL. |

### Final harness tools
`list_dir` · `read_file` · `write_file` · `edit_file` (exact unique-string replace) · `run_bash`
(workspace-scoped, with a blocklist for catastrophic commands). Mutating tools pass through an
approval guard; `--auto` approves them for hands-off runs.

## Run it
```bash
export OPENROUTER_API_KEY=sk-or-...          # your key
export HARNESS_MODEL=deepseek/deepseek-chat  # optional; any OpenRouter model id

python3 -m coding_harness --auto -t "write fizzbuzz to fizz.py and run it"
python3 -m coding_harness                    # interactive REPL (prompts before write/bash)
python3 step1_chat.py                        # step 1 only
python3 step2_one_tool.py "count the python files here"
```
No `pip install` needed — stdlib only (Python 3.8+). More tasks in [`examples/task_bank.md`](./examples/task_bank.md).

## Execution proof without a key
```bash
python3 selftest.py
```
Swaps in a scripted model and confirms the real loop executes real tools: it writes
`fizzbuzz.py` to disk, runs it, and checks the `FizzBuzz` output — so you can demonstrate the
engine working before plugging in an API key. Local result:
```
✓ done (3 steps)
PASS — harness loop executed real tools:
  • wrote …/fizzbuzz.py
  • program output tail: ['13', '14', 'FizzBuzz']
```

## How the loop works (the heart of a harness)
```
send[ conversation + tool schemas ] → model
      │
      ├─ model returns tool_calls →  run each (guarded) → append results → loop
      └─ model returns plain text →  final answer, stop
```
A step cap bounds cost/runaways; token usage → a cost estimate is printed each run.
Design informed by `simple-coding-harness`, `mini-swe-agent`, and the "build a coding agent
from scratch" references in the assignment — typed and executed here, not copied.
