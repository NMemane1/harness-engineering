# DSH Demo Prompts (for the video)

Type these into a DeepSeek Harness session after you've set an API key and installed the plugins.

## second-brain plugin
```
Use the remember tool to save this note: "The OpenRouter base URL is https://openrouter.ai/api/v1" with tags api,openrouter.
```
```
Remember: "DSH web UI runs on http://127.0.0.1:3080" tagged dsh.
```
```
Now use recall to find everything I saved about "openrouter".
```
Expected: the agent calls `remember` (returns `Remembered note #1 …`) then `recall` and reads
back the saved note. Open a **new session** and `recall "dsh"` to show the memory *persists*
across sessions (it's stored in `~/.dsh-second-brain.json`).

## project-scout plugin
```
Use scan_project to summarize this repository: how many files, which languages, and list any TODO/FIXME markers.
```
Expected: the agent calls `scan_project` and reports file counts by language, total LOC, and any TODOs.

## Showing the official plugins
```
Search the web for the latest DeepSeek model names.        # Web search plugin
Spin up a subagent to draft a README outline for this repo. # Subagent plugin
```

## Creator mode talking points (while on camera)
- Open **Plugins** → point out the 7 enabled official plugins + the 2 custom ones.
- Open the **trajectory / event stream** of a run to show each tool call (remember, recall,
  scan_project) as an append-only event — then note you can fork/replay from any turn.
- Mention the plugin contract: `apply(ctx)` + `inject: ['tools']` + `defineTool()` +
  `ctx.tools.register()`, and that disposing the plugin auto-unregisters the tools.
