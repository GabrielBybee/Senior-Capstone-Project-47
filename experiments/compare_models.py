"""
compare_models.py

Sends the SAME prompt (experiments/prompt.txt) to several MindRouter models and
saves each model's full response to experiments/results/. Purpose: compare which
model writes the best secure-coding teaching example for our capstone tutor.

"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---- The 5 models we are comparing ----------------------------------------
MODELS = [
    "qwen2.5-coder:32b",
    "qwen3-coder:30b",
    "llama3.3:70b",
    "openai/gpt-oss-120b",
    "mistral-large:123b",
]

TEMPERATURE = 0.2   # low -> more deterministic, fairer comparison
TIMEOUT = 180       # seconds per request


def load_env(env_path):
    """Minimal .env loader so we don't need python-dotenv."""
    env = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip("\"'")
    # allow real environment variables to override the file
    for k in ("MINDROUTER_API_KEY", "MINDROUTER_BASE_URL"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


def ask_model(base_url, api_key, model, prompt):
    """Send one chat-completion request. Returns (text, raw_json)."""
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = json.loads(resp.read().decode("utf-8"))

    # OpenAI-compatible shape
    text = raw["choices"][0]["message"]["content"]
    return text, raw


def main():
    env = load_env(HERE / ".env")
    api_key = env.get("MINDROUTER_API_KEY")
    base_url = env.get("MINDROUTER_BASE_URL")

    if not api_key or api_key == "your_key_here":
        sys.exit("ERROR: set MINDROUTER_API_KEY in experiments/.env first.")
    if not base_url:
        sys.exit("ERROR: set MINDROUTER_BASE_URL in experiments/.env first.")

    prompt = (HERE / "prompt.txt").read_text(encoding="utf-8")

    results_dir = HERE / "results"
    results_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    summary_lines = [
        "# Model comparison run",
        f"Timestamp: {stamp}",
        f"Endpoint: {base_url}",
        f"Temperature: {TEMPERATURE}",
        "",
        "## Prompt",
        "```",
        prompt.strip(),
        "```",
        "",
        "## Responses",
        "",
    ]

    for model in MODELS:
        print(f"-> Querying {model} ...")
        safe_name = model.replace("/", "_").replace(":", "_")
        started = time.time()
        try:
            text, raw = ask_model(base_url, api_key, model, prompt)
            elapsed = time.time() - started

            out_file = results_dir / f"{stamp}__{safe_name}.md"
            out_file.write_text(
                f"# {model}\n\n(latency: {elapsed:.1f}s)\n\n{text}\n",
                encoding="utf-8",
            )
            # keep the raw JSON too, for token counts etc.
            (results_dir / f"{stamp}__{safe_name}.json").write_text(
                json.dumps(raw, indent=2), encoding="utf-8"
            )
            print(f"   ok  ({elapsed:.1f}s)  -> {out_file.name}")
            summary_lines.append(f"- **{model}** — {elapsed:.1f}s — `{out_file.name}`")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            msg = f"HTTP {e.code}: {body[:300]}"
            print(f"   FAILED: {msg}")
            summary_lines.append(f"- **{model}** — FAILED — {msg}")
        except Exception as e:  # noqa: BLE001
            print(f"   FAILED: {e}")
            summary_lines.append(f"- **{model}** — FAILED — {e}")

    summary_file = results_dir / f"{stamp}__SUMMARY.md"
    summary_file.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print(f"\nDone. Summary: {summary_file}")
    print("Open the results/ folder to read each model's answer side by side.")


if __name__ == "__main__":
    main()
