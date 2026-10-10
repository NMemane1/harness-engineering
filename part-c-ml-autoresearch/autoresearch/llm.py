"""Minimal OpenRouter chat client (stdlib only) for the autoresearch harness.

Here the model's job is to WRITE and IMPROVE a training script, so we use plain
chat completions and parse the ```python code block out of the reply.
"""
import json
import os
import re
import time
import urllib.error
import urllib.request

API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = os.environ.get("HARNESS_MODEL", "deepseek/deepseek-chat")


class LLM:
    def __init__(self, model=None):
        self.model = model or DEFAULT_MODEL
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("Set OPENROUTER_API_KEY (https://openrouter.ai/keys).")
        self.tokens = 0

    def complete(self, system, user, temperature=0.3):
        payload = {"model": self.model, "temperature": temperature, "messages": [
            {"role": "system", "content": system}, {"role": "user", "content": user}]}
        req = urllib.request.Request(
            API_URL, data=json.dumps(payload).encode(), method="POST",
            headers={"Authorization": f"Bearer {self.api_key}",
                     "Content-Type": "application/json",
                     "X-Title": "CMPE-297 ML Autoresearch Harness"})
        for i in range(3):
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    data = json.loads(r.read())
                self.tokens += data.get("usage", {}).get("total_tokens", 0)
                return data["choices"][0]["message"]["content"]
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503) and i < 2:
                    time.sleep(2 ** i); continue
                raise RuntimeError(f"OpenRouter HTTP {e.code}: {e.read().decode()[:300]}")


def extract_code(text):
    """Pull the first python code block out of a model reply."""
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    return (m.group(1) if m else text).strip()
