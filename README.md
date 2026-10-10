# 🛠️ Harness Engineering

**CMPE-297 · Assignment 2 — Build a harness from scratch, customize the DeepSeek Harness in creator mode, and build a custom ML harness.**

Three agent "harnesses", each built and documented from scratch:

| Part | What it is | Status | Live demo needs |
|---|---|---|---|
| **[A — Coding Harness](./part-a-coding-harness)** | A CLI coding agent (read/write/run code via tools) built progressively on **OpenRouter**, stdlib-only. | ✅ built + self-test passing | OpenRouter key |
| **[B — DeepSeek Harness](./part-b-deepseek-harness)** | Install **DSH**, run creator mode, enable 7 plugins, **author 2 plugins from scratch**. | ✅ DSH run locally, 2 plugins built + smoke-test passing | DeepSeek key |
| **[C — ML Autoresearch Harness](./part-c-ml-autoresearch)** | An AIDE-style loop that auto-researches ML solutions: propose → run → evaluate → improve. | ✅ built + self-test passing | OpenRouter key |

Built with an AI coding assistant; the exact prompts are in **[PROMPTS.md](./PROMPTS.md)**.

---

## 📹 Video walkthroughs (one per part)

Full code walkthrough + execution demo for each part (see **[VIDEO_SCRIPTS.md](./VIDEO_SCRIPTS.md)** for the scripts):

- **Part A — Coding harness:** _<!-- PART_A_YOUTUBE --> add link_
- **Part B — DeepSeek harness + plugins:** _<!-- PART_B_YOUTUBE --> add link_
- **Part C — ML autoresearch harness:** _<!-- PART_C_YOUTUBE --> add link_

---

## 🚀 Quick start

```bash
git clone https://github.com/NMemane1/harness-engineering.git
cd harness-engineering

# --- Part A: coding harness (stdlib only) ---
python3 part-a-coding-harness/selftest.py            # proves the loop runs real tools (no key)
export OPENROUTER_API_KEY=sk-or-...                  # get one at https://openrouter.ai/keys
python3 -m coding_harness --auto -t "write fizzbuzz to fizz.py and run it"   # (run inside part-a-coding-harness/)

# --- Part B: DeepSeek harness plugins ---
node part-b-deepseek-harness/tests/plugin-smoke.mjs  # proves both custom plugins run (no key)
npx -y @deepseek-ai/dsh@latest web                   # launch DSH at http://127.0.0.1:3080

# --- Part C: ML autoresearch ---
pip install -r part-c-ml-autoresearch/requirements.txt
python3 part-c-ml-autoresearch/selftest.py           # proves the research loop runs (no key)
```

Each part has its own README with full detail.

---

## 🎯 What each part demonstrates

**A — what a harness *is*.** Step 1 is a chat loop; step 2 adds a single tool and the tool-call
loop (the moment a chatbot becomes an *agent*); step 3 is a full harness with 5 tools, a guarded
agentic loop, and cost tracking. Model-agnostic via OpenRouter.

**B — extending a real harness.** DSH treats *everything as a plugin* (Cordis kernel). I ran it
locally, enabled 7 official plugins, and wrote two plugins from scratch against the real API
(`apply(ctx)` + `defineTool` + `ctx.tools.register`): **second-brain** (persistent `remember`/`recall`
memory) and **project-scout** (`scan_project` repo summarizer).

**C — a harness that does science.** An empirical ML research loop: the model proposes training
scripts, the harness *runs* them in a sandbox, reads the real cross-validated metric, and iterates —
keeping the best. On a churn task it takes a 0.77-AUC linear baseline to ~0.81 via engineered features.

Every part ships an **offline self-test** that executes the real engine without an API key, so the
machinery is demonstrable before you plug in a key.

---

## 🔑 What's real vs. what you finish
- **Real & verified here:** all code, all three self-tests passing, DSH installed and run on this
  machine (screenshots in Part B), both custom plugins executing.
- **Needs your API keys + a camera (your part):** the *live model-driven* runs and the three
  YouTube videos. OpenRouter key for A & C; DeepSeek key for B. See each part's README.

---

_Nikita Memane · CMPE-297 · built & executed with an AI coding assistant._
