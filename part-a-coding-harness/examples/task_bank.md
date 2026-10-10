# Example tasks to demo the harness

Single-shot (auto-approve mutating tools):
```bash
python3 -m coding_harness --auto -t "create a file primes.py that prints the first 20 primes, then run it"
python3 -m coding_harness --auto -t "scan this repo, list every python file and its line count"
python3 -m coding_harness --auto -t "write a FastAPI hello-world to app.py and a test that imports it; run the test"
```

Interactive REPL (prompts before write/edit/bash):
```bash
python3 -m coding_harness
task › what does step2_one_tool.py do? summarize it
task › add a docstring to the top of primes.py
```

Try a different model:
```bash
python3 -m coding_harness -m google/gemini-2.0-flash-001 --auto -t "refactor primes.py to use a sieve"
```
