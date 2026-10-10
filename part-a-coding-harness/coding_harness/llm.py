"""OpenRouter LLM client (OpenAI-compatible wire format), stdlib only.

OpenRouter is a single gateway in front of 300+ models (DeepSeek, Gemini,
Claude, GPT, Llama, ...). Because its API mirrors OpenAI's, the same request
body works for every model — you just change the `model` id.
"""
import json
import os
import time
import urllib.error
import urllib.request

API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = os.environ.get("HARNESS_MODEL", "deepseek/deepseek-chat")

# Rough per-million-token USD prices for the cost estimator (input, output).
# These are ballpark; OpenRouter returns real usage, we just price it.
PRICES = {
    "deepseek/deepseek-chat": (0.27, 1.10),
    "google/gemini-2.0-flash-001": (0.10, 0.40),
    "google/gemini-flash-1.5": (0.075, 0.30),
    "anthropic/claude-3.5-sonnet": (3.0, 15.0),
    "openai/gpt-4o-mini": (0.15, 0.60),
}


class LLM:
    def __init__(self, model=None, api_key=None, temperature=0.0):
        self.model = model or DEFAULT_MODEL
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "No API key. Set OPENROUTER_API_KEY (get one at https://openrouter.ai/keys).")
        self.temperature = temperature
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def chat(self, messages, tools=None):
        """Single completion. Returns the assistant `message` dict (may contain tool_calls)."""
        payload = {"model": self.model, "messages": messages, "temperature": self.temperature}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        body = json.dumps(payload).encode()
        req = urllib.request.Request(
            API_URL, data=body, method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/NMemane1/harness-engineering",
                "X-Title": "CMPE-297 Coding Harness",
            },
        )
        data = self._post_with_retry(req)
        usage = data.get("usage", {})
        self.prompt_tokens += usage.get("prompt_tokens", 0)
        self.completion_tokens += usage.get("completion_tokens", 0)
        return data["choices"][0]["message"]

    def _post_with_retry(self, req, attempts=3):
        for i in range(attempts):
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    return json.loads(r.read())
            except urllib.error.HTTPError as e:
                detail = e.read().decode(errors="ignore")[:500]
                if e.code in (429, 500, 502, 503) and i < attempts - 1:
                    time.sleep(2 ** i)
                    continue
                raise RuntimeError(f"OpenRouter HTTP {e.code}: {detail}")
            except urllib.error.URLError as e:
                if i < attempts - 1:
                    time.sleep(2 ** i)
                    continue
                raise RuntimeError(f"Network error reaching OpenRouter: {e}")

    def cost_estimate(self):
        pin, pout = PRICES.get(self.model, (0.0, 0.0))
        return (self.prompt_tokens / 1e6) * pin + (self.completion_tokens / 1e6) * pout
