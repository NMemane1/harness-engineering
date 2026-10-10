# 🎬 Video Recording Scripts (3 videos)

The assignment wants **a YouTube video for each part** with a full code walkthrough *and*
execution. Record three short videos (5–8 min each) and paste the links into the top-level
[README.md](./README.md). Use QuickTime (`⌘⇧5`), Loom, or OBS.

> Speak to *why* it's engineered this way (the loop, leakage/safety, the plugin contract) — that's
> what's being graded, not just "here's a file".

---

## 🎥 Video 1 — Part A: Coding harness (≈6 min)

1. **(0:00) Intro** — "I built a coding agent harness from scratch on the OpenRouter API, stdlib only, progressively."
2. **(0:30) Step 1** — open `step1_chat.py`, explain the raw chat-completions call via `urllib`. Run it, send one message.
3. **(1:30) Step 2** — open `step2_one_tool.py`. "This is the key idea" — show the `TOOLS` schema and the loop: model requests `run_bash` → we execute → feed the result back. Run: `python3 step2_one_tool.py "count the python files here"`.
4. **(3:00) Step 3 — full harness** — walk `coding_harness/`: `llm.py` (OpenRouter + cost), `tools.py` (5 tools + safety guard/blocklist), `agent.py` (the agentic loop + step cap), `cli.py`.
5. **(4:30) Execute without a key** — run `python3 selftest.py`; show it writes `fizzbuzz.py`, runs it, prints `FizzBuzz`.
6. **(5:00) Live run** — `export OPENROUTER_API_KEY=…`, then `python3 -m coding_harness --auto -t "create primes.py that prints the first 20 primes and run it"`. Show the tool calls scrolling and the final file.
7. **(5:45) Wrap** — mention it's model-agnostic (swap `-m google/gemini-2.0-flash-001`).

## 🎥 Video 2 — Part B: DeepSeek Harness + plugins (≈8 min)

1. **(0:00) Intro** — "DSH = everything is a plugin, on the Cordis kernel. I'll run it, enable plugins, and show two plugins I wrote from scratch."
2. **(0:40) Install & launch** — `npx -y @deepseek-ai/dsh@latest web`, open `http://127.0.0.1:3080`, add your DeepSeek API key.
3. **(1:40) Creator mode** — enable developer/creator features in Settings; mention the Cordis inspection tools.
4. **(2:30) Plugins manager** — open **Plugins**, toggle on 7 official ones (Shell, Web search, Agent loop, Subagent, Automation tasks, Agent Teams, Auto Authorization Review). Add a community one via **Add plugin** (e.g. `dsh-plugin-whale-pet`).
5. **(4:00) Custom plugins — code** — open `plugins/dsh-second-brain/index.js` and `plugins/dsh-project-scout/index.js`; explain the contract: `apply(ctx)`, `inject:['tools']`, `defineTool`, `ctx.tools.register`, and the bundle `package.json`.
6. **(5:30) Prove they run offline** — `node tests/plugin-smoke.mjs` (registers + executes both).
7. **(6:00) Install into DSH** — `dsh plugin --profile demo add ./plugins/dsh-second-brain` (and project-scout), boot, then in a session run the prompts from `demo-prompts.md`: `remember` a fact → `recall` it → open a NEW session and recall again (persists) → `scan_project` this repo.
8. **(7:30) Wrap** — show the run's trajectory/event stream with each tool call.

## 🎥 Video 3 — Part C: ML autoresearch harness (≈6 min)

1. **(0:00) Intro** — "A harness that does ML research: propose → run → evaluate → improve, keeping the best model."
2. **(0:40) The task** — open `tasks/customer_churn/task.md` + `make_data.py`; explain the nonlinear structure and the CV-AUC metric. Run `make_data.py`.
3. **(1:40) The engine** — walk `autoresearch/experiment.py` (sandboxed subprocess runner + result contract) and `researcher.py` (the greedy loop + feedback + journal/report).
4. **(3:00) Prove it runs offline** — `python3 selftest.py`; show broken caught, baseline 0.77 → engineered 0.81, best selected.
5. **(3:45) Live run** — `export OPENROUTER_API_KEY=…`, then `python3 -m autoresearch --task tasks/customer_churn --steps 6`. Narrate the trajectory as AUC climbs across steps.
6. **(5:15) Report** — open `runs/<timestamp>/report.md` + `best_solution.py`; show the winning script the harness discovered.
7. **(5:45) Wrap** — note it's dataset-agnostic (add a new `tasks/<name>/`).

---

## After recording
Paste each link into README.md at `<!-- PART_A_YOUTUBE -->`, `<!-- PART_B_YOUTUBE -->`,
`<!-- PART_C_YOUTUBE -->`, then:
```bash
git add README.md && git commit -m "Add YouTube walkthrough links" && git push
```
