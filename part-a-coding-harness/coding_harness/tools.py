"""The tool belt the agent can use, plus a safety guard.

Each tool is a plain Python function that returns a string. `SCHEMAS` exposes
them to the model in OpenAI function-calling format; `dispatch()` runs the one
the model asked for. Mutating tools (write/edit/bash) go through `guard()`.
"""
import os
import subprocess

WORKSPACE = os.environ.get("HARNESS_WORKSPACE", os.getcwd())

# Commands we refuse outright, even with approval, to avoid footguns.
_BLOCKED = ("rm -rf /", "mkfs", ":(){", "dd if=", "> /dev/sda", "shutdown", "reboot")


def _safe_path(path):
    full = os.path.abspath(os.path.join(WORKSPACE, path))
    if not full.startswith(os.path.abspath(WORKSPACE)):
        raise ValueError(f"Path escapes the workspace: {path}")
    return full


def read_file(path, limit=400):
    full = _safe_path(path)
    with open(full, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    body = "".join(f"{i+1}\t{ln}" for i, ln in enumerate(lines[:limit]))
    if len(lines) > limit:
        body += f"\n… ({len(lines)-limit} more lines)"
    return body or "(empty file)"


def write_file(path, content):
    full = _safe_path(path)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Wrote {len(content)} bytes to {path}"


def edit_file(path, old, new):
    """Exact-string replacement (like a precise find/replace)."""
    full = _safe_path(path)
    with open(full, encoding="utf-8") as f:
        text = f.read()
    if text.count(old) == 0:
        return f"ERROR: `old` string not found in {path}"
    if text.count(old) > 1:
        return f"ERROR: `old` string appears {text.count(old)}× in {path}; make it unique"
    with open(full, "w", encoding="utf-8") as f:
        f.write(text.replace(old, new, 1))
    return f"Edited {path} (1 replacement)"


def list_dir(path="."):
    full = _safe_path(path)
    entries = []
    for name in sorted(os.listdir(full)):
        if name.startswith(".git"):
            continue
        tag = "/" if os.path.isdir(os.path.join(full, name)) else ""
        entries.append(name + tag)
    return "\n".join(entries) or "(empty)"


def run_bash(command, timeout=90):
    low = command.lower()
    if any(b in low for b in _BLOCKED):
        return "ERROR: command blocked by safety policy"
    p = subprocess.run(command, shell=True, cwd=WORKSPACE,
                       capture_output=True, text=True, timeout=timeout)
    out = (p.stdout + p.stderr).strip()
    return f"(exit {p.returncode})\n{out[:6000]}" or f"(exit {p.returncode}, no output)"


# ---- model-facing schemas ----
SCHEMAS = [
    {"type": "function", "function": {
        "name": "list_dir", "description": "List files/folders in a directory.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Directory (default '.')"}}}}},
    {"type": "function", "function": {
        "name": "read_file", "description": "Read a text file (with line numbers).",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "limit": {"type": "integer"}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "write_file", "description": "Create or overwrite a file with content.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"]}}},
    {"type": "function", "function": {
        "name": "edit_file", "description": "Replace one exact unique string in a file.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "old": {"type": "string"}, "new": {"type": "string"}},
            "required": ["path", "old", "new"]}}},
    {"type": "function", "function": {
        "name": "run_bash", "description": "Run a shell command in the workspace.",
        "parameters": {"type": "object", "properties": {
            "command": {"type": "string"}}, "required": ["command"]}}},
]

_FUNCS = {"list_dir": list_dir, "read_file": read_file, "write_file": write_file,
          "edit_file": edit_file, "run_bash": run_bash}
MUTATING = {"write_file", "edit_file", "run_bash"}


def dispatch(name, args):
    if name not in _FUNCS:
        return f"ERROR: unknown tool {name}"
    try:
        return str(_FUNCS[name](**args))
    except Exception as e:  # tool errors are data for the model, not crashes
        return f"ERROR running {name}: {e}"
