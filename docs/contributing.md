# Contributing

## Branches

```
main      ← stable. Only updated by PRs from test. Deploys from here (later).
  test    ← integration. All feature work merges here first.
    your-branch  ← one branch per piece of work, branched off test
```

1. Start from an up-to-date `test`:
   ```bash
   git switch test && git pull
   git switch -c feature/hint-filter
   ```
2. Name branches `feature/...`, `fix/...`, `docs/...` or `chore/...`.
3. Push and open a PR **into `test`**: `gh pr create --base test`.
4. Get one review and green CI, then merge.
5. When `test` is stable, someone opens a PR from `test` into `main`.

Never push directly to `main` or `test`.

Gabriel's original model experiments live on the `AI-testing` branch.

## Before you push

Run the checks for whatever you touched. CI runs the same ones.

```bash
cd backend  && uv run ruff check . && uv run ruff format . && uv run pytest
cd runner   && uv run ruff check . && uv run ruff format . && uv run pytest
cd frontend && npm run lint && npm run format && npx vitest run && npm run build
sandbox/smoke-test.sh      # if you changed sandbox/
```

## Code style

- **Python:** Ruff handles linting and formatting (config in each `pyproject.toml`).
  Use type hints on public functions and Pydantic models for request and response bodies.
- **TypeScript:** oxlint for linting and Prettier for formatting (no semicolons,
  single quotes, 100 columns).
- **C samples:** compile cleanly with `-Wall -Wextra`. Mark the intended bug with a comment.
- Add or update tests with every behavior change.

## Dependencies

- Python: `uv add <pkg>` (or `uv add --dev <pkg>`) inside `backend/` or `runner/`.
  Commit `uv.lock`.
- Frontend: `npm install <pkg>` inside `frontend/`. Commit `package-lock.json`.
- Dependabot opens weekly update PRs against `test`. Review them like any other PR.

## Commits and PRs

- Write commit messages in the imperative, with a short subject:
  `Add hint leak filter`, not `added stuff`.
- Keep PRs small and focused, and fill in the PR template.
- Record significant choices (new library, architecture change) in
  [decisions.md](decisions.md).

## Secrets

- Real keys go only in `.env`, which is gitignored. When you add a new variable,
  add it to `.env.example` with an empty or placeholder value.
- If a key is ever committed, tell the team and rotate it right away. Deleting
  the commit isn't enough.
