"""
generate.py

Send one prompt to one MindRouter model and print/save the generated code.
Reuses the .env loader and request helper from compare_models.py.

Usage:
    python experiments/generate.py "Write a C function that safely copies a string"
    python experiments/generate.py -f experiments/prompt.txt -m llama3.3:70b
    python experiments/generate.py --list-models

No third-party packages required (uses only the Python standard library).
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from compare_models import HERE, TEMPERATURE, TIMEOUT, ask_model, load_env

DEFAULT_MODEL = "qwen3-coder:30b"


def list_models(base_url, api_key):
    req = urllib.request.Request(base_url.rstrip("/") + "/models")
    req.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    for model_id in sorted(m["id"] for m in raw.get("data", [])):
        print(model_id)


def main():
    parser = argparse.ArgumentParser(description="Generate code with a MindRouter model.")
    parser.add_argument("prompt", nargs="?", help="prompt text (or use -f)")
    parser.add_argument("-f", "--file", help="read the prompt from a file")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, help=f"default: {DEFAULT_MODEL}")
    parser.add_argument("-o", "--output", help="output .md path (default: results/<timestamp>__gen__<model>.md)")
    parser.add_argument("--list-models", action="store_true", help="list available models and exit")
    args = parser.parse_args()

    env = load_env(HERE / ".env")
    api_key = env.get("MINDROUTER_API_KEY")
    base_url = env.get("MINDROUTER_BASE_URL")
    if not api_key or api_key == "your_key_here":
        sys.exit("ERROR: set MINDROUTER_API_KEY in experiments/.env first.")
    if not base_url:
        sys.exit("ERROR: set MINDROUTER_BASE_URL in experiments/.env first.")

    try:
        if args.list_models:
            list_models(base_url, api_key)
            return

        if args.file:
            prompt = open(args.file, encoding="utf-8").read()
        elif args.prompt:
            prompt = args.prompt
        else:
            parser.error("give a prompt or -f FILE")

        text, raw = ask_model(base_url, api_key, args.model, prompt)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.output:
        out_file = Path(args.output)
    else:
        safe_name = args.model.replace("/", "_").replace(":", "_")
        out_file = HERE / "results" / f"{stamp}__gen__{safe_name}.md"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    # aliases like default-coder resolve to a real model; record which one answered
    resolved = raw.get("model", args.model)
    header = f"# {args.model}\n\n- Resolved model: `{resolved}`\n- Generated: {stamp}\n- Temperature: {TEMPERATURE}\n"
    out_file.write_text(
        f"{header}\n## Prompt\n\n```text\n{prompt.strip()}\n```\n\n# Response\n\n{text}\n",
        encoding="utf-8",
    )
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows console defaults to cp1252
    print(text)
    print(f"\n[saved to {out_file}]", file=sys.stderr)


if __name__ == "__main__":
    main()
