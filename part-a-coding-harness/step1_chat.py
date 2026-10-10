#!/usr/bin/env python3
"""
Part A — Step 1: the smallest possible harness.

A bare chat loop against the OpenRouter API (OpenAI-compatible wire format),
using ONLY the Python standard library. No tools yet — this is just to prove
we can talk to a model and keep a conversation.

Run:
    export OPENROUTER_API_KEY=sk-or-...
    python3 step1_chat.py
"""
import json
import os
import urllib.request

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.environ.get("HARNESS_MODEL", "deepseek/deepseek-chat")


def chat(messages):
    """One call to the chat-completions endpoint. Returns the assistant text."""
    body = json.dumps({"model": MODEL, "messages": messages}).encode()
    req = urllib.request.Request(
        API_URL, data=body, method="POST",
        headers={
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
            # OpenRouter attribution headers (optional but recommended):
            "HTTP-Referer": "https://github.com/NMemane1/harness-engineering",
            "X-Title": "CMPE-297 Coding Harness",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    return data["choices"][0]["message"]["content"]


def main():
    if "OPENROUTER_API_KEY" not in os.environ:
        raise SystemExit("Set OPENROUTER_API_KEY first.")
    print(f"Step-1 chat harness · model={MODEL} · type 'exit' to quit\n")
    messages = [{"role": "system", "content": "You are a concise coding assistant."}]
    while True:
        user = input("you › ").strip()
        if user in {"exit", "quit"}:
            break
        messages.append({"role": "user", "content": user})
        reply = chat(messages)
        messages.append({"role": "assistant", "content": reply})
        print(f"\nai  › {reply}\n")


if __name__ == "__main__":
    main()
