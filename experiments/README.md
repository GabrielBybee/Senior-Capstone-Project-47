# Model comparison — secure-coding teaching examples

Compares how well different MindRouter models generate an introductory
secure-coding example (a stack buffer overflow and its fix) for our tutoring agent.

## Setup

1. Create a key in MindRouter and copy the example env file:
   ```powershell
   Copy-Item experiments\.env.example experiments\.env
   ```
2. Open `experiments\.env` and paste your key into `MINDROUTER_API_KEY`.
   `MINDROUTER_BASE_URL` should be `https://mindrouter.uidaho.edu/v1`
   (not `/api/v1`, which returns 404).
3. Check it works:
   ```powershell
   python experiments\generate.py --list-models
   ```

## Generate code with one model

```powershell
python experiments\generate.py "Write a C function that safely copies a string"
python experiments\generate.py -f experiments\prompt.txt -m llama3.3:70b
```

Output is printed and also saved as `experiments\results\<timestamp>__gen__<model>.md`.

## Compare all models

```powershell
python experiments\compare_models.py
```

Each model's answer is saved under `experiments\results\`:
- `<timestamp>__<model>.md`   — the readable answer
- `<timestamp>__<model>.json` — raw response (token counts, etc.)
- `<timestamp>__SUMMARY.md`   — one-line status per model

## Models compared

- `qwen2.5-coder:32b`
- `qwen3-coder:30b`
- `llama3.3:70b`
- `openai/gpt-oss-120b`
- `mistral-large:123b`

## Notes

- The prompt lives in `experiments\prompt.txt` — edit it once and every model
  gets the identical prompt, which keeps the comparison fair.
- `.env` is gitignored so your key never gets pushed to the shared repo.
- If a model refuses or errors, that shows up in the summary — useful data when
  choosing a model for the tutor.
