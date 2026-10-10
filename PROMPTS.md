# Prompts Used (AI Coding Assistant)

The prompts I used to build each harness with an AI coding assistant. The point of the
assignment is to *type and execute* the code, so each part was built iteratively — generate,
run, read the error/metric, refine — not copied from a reference.

## Part A — Coding harness
```
Build a coding agent harness from scratch on the OpenRouter API, using ONLY the Python stdlib.
Do it progressively: (1) a bare chat loop; (2) add a single run_bash tool with the tool-call
loop; (3) a full harness with list_dir/read_file/write_file/edit_file/run_bash, an agentic loop
with a step cap, a safety guard + approval for mutating tools, token/cost tracking, and a CLI
with both single-task and REPL modes.
```
```
Add an offline self-test that swaps in a scripted fake model and proves the loop executes the
REAL tools (writes a file, runs it, checks the output) — so I can demo it without an API key.
```
```
Make run_bash workspace-scoped and block catastrophic commands (rm -rf /, mkfs, fork bombs).
```

## Part B — DeepSeek Harness plugins
```
Research the DeepSeek Harness (DSH) plugin API from its repo docs (cordis-tutorial, cookbook/
adding-a-tool, user/develop/basic). Then write TWO plugins from scratch as installable JS
bundles: (1) "second-brain" with remember/recall tools backed by a JSON file in the home dir;
(2) "project-scout" with a scan_project tool that reports language stats, LOC, and TODO/FIXME.
Use the real contract: export apply(ctx), inject:['tools'], defineTool(...) + ctx.tools.register.
```
```
Package each as a dsh bundle (package.json with dsh.bundle + cordis.patch.yml) so it installs
with `dsh plugin add ./dir`, and add a peerDependency on @deepseek-ai/dsh-tools.
```
```
Write an offline smoke test that shims @deepseek-ai/dsh-tools, loads each plugin's apply(ctx)
against a fake ctx, and invokes the registered tools to confirm they execute.
```
```
Install and launch DSH locally, enable 5-7 official plugins, and capture screenshots of the UI,
the plugin manager, and the add-plugin dialog.
```

## Part C — ML autoresearch harness
```
Build a custom ML autoresearch harness (AIDE-style, see WecoAI/awesome-autoresearch): an
empirical loop where the model writes a self-contained training script, a sandbox subprocess
runs it with a timeout and reads {"val_metric": ...}, and the harness feeds the metric/traceback
back so the model improves the best solution over N steps. Keep the best, write a report.
```
```
Create a realistic churn task where a linear baseline (~0.77 AUC) is clearly beaten by feature
engineering / trees (~0.81+). Tune the synthetic data until that gap is real (broad interaction +
non-monotonic effect, not rare conjunctions).
```
```
Add an offline self-test with three hand-written candidates (broken, baseline, engineered) that
proves the sandbox runs them, parses the metric, catches the failure, and selects the best.
```

## Cross-cutting
```
Keep Parts A and C dependency-light (stdlib HTTP via urllib for OpenRouter) so they run with no
pip install beyond scikit-learn for C. Make every part demonstrable offline via a self-test.
Then write per-part READMEs, a master README, and a per-part video recording script; publish to
a public GitHub repo.
```
