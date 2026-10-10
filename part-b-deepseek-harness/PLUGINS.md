# DSH Plugin Catalog (Part B)

## Official plugins I enabled (seen in the Plugins manager on this machine)

| Plugin | What it does | Why enable it |
|---|---|---|
| **Shell** | Limits how long each command may run and how much it may output. | Core guardrail for the agent's bash. |
| **Web search** | Sets up the DeepSeek search provider. | Lets the agent look things up. |
| **Agent loop** | Controls how the agent dispatches tool calls. | Tunes the core reasoning loop. |
| **Subagent** | Sets subagent recursion depth, count, and models. | Enables multi-agent decomposition. |
| **Automation tasks** | Run tasks in sessions at a set time / on a repeating schedule. | Scheduled/recurring runs. |
| **Agent Teams** | Team collaboration: team tools, member roster, shared task board. | Multi-model team workflows. |
| **Auto Authorization Review** | Model-assessed authorization before running actions. | Safety / permission gating. |

> That's 7 official plugins toggled on — satisfies the "5–7 plugins" requirement before the
> two custom ones below.

## Community plugins (from the ecosystem catalogs, add via *Add plugin*)

The *Add plugin* dialog accepts an **npm package name**, a **GitHub URL**, or a **local path**.
The assignment lists several catalogs — e.g. `bruc3van/awesome-dsh-plugin` (TOP200),
`whyihaveyou/dsh-suite`, `Ephemeral-AI-Lab/dsh-plugins` (loop/sessions/mock/preset-builder).
The official demo plugin is `dsh-plugin-whale-pet` (a floating pet). Install one or two to show
the community-add flow:

```
Add plugin → dsh-plugin-whale-pet → Install
```

> ⚠️ Only install plugins you trust — they run with your permissions. Pin a commit when
> installing from GitHub.

## My two from-scratch plugins

| Plugin | Tool(s) | Demo prompt |
|---|---|---|
| **dsh-second-brain** | `remember`, `recall` | `Remember that my demo runs on port 3080, then recall "port".` |
| **dsh-project-scout** | `scan_project` | `Scan this project and tell me the languages and any TODOs.` |

Both are installable bundles under [`plugins/`](./plugins) and pass the offline smoke test
(`node tests/plugin-smoke.mjs`).
