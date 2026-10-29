# Setup

How to get the project running on your machine. If something here is wrong or
missing, fix it in a PR.

## 1. Prerequisites

We develop on **Linux** (Ubuntu on WSL2 if you're on Windows). On WSL, keep the
repo in your Linux home (`~/code`), **not** under `/mnt/c`. File watching and
Docker are much slower and less reliable there.

| Tool | Version | Used for |
|---|---|---|
| git, curl | any | |
| Docker Engine + Compose v2 | Compose 2.24+ | running the whole stack |
| [uv](https://docs.astral.sh/uv/) | 0.13+ | Python packages (installs Python 3.12 for you) |
| Node.js (via [nvm](https://github.com/nvm-sh/nvm)) | 22 | frontend |
| GitHub CLI (`gh`) | any | cloning, PRs |
| gcc, clang, cppcheck, valgrind, gdb | distro versions | optional locally: the sandbox image has them |

Ubuntu, quickly:

```bash
sudo apt-get install -y build-essential git curl clang cppcheck valgrind gdb \
  docker.io docker-compose-v2 docker-buildx
sudo usermod -aG docker "$USER"     # then log out and back in (WSL: wsl --shutdown)
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
nvm install 22
```

For the GitHub CLI, follow <https://github.com/cli/cli/blob/trunk/docs/install_linux.md>, then:

```bash
gh auth login
gh auth setup-git
```

Check everything:

```bash
docker run --rm hello-world
docker compose version && uv --version && node --version && gh auth status
```

## 2. Clone and configure

```bash
mkdir -p ~/code && cd ~/code
gh repo clone GabrielBybee/Senior-Capstone-Project-47
cd Senior-Capstone-Project-47
git switch test
cp .env.example .env    # then put your MindRouter API key in .env
```

`.env` is gitignored. Never commit it, and never paste keys into issues or PRs.

## 3. Run the stack

```bash
docker compose up --build
```

| URL | What |
|---|---|
| <http://localhost:5173> | frontend (Vite dev server) |
| <http://localhost:8000/api/health> | backend |
| <http://localhost:8000/docs> | backend API docs (Swagger) |
| <http://localhost:8001/health> | runner |

Postgres runs too, but on purpose it has no port on your machine. Only the other
containers can reach it.

Edits to `backend/app`, `runner/app` and `frontend/` reload automatically. After
changing dependencies (`pyproject.toml`, `package.json`), run
`docker compose up --build` again.

Stop with `Ctrl+C`, or `docker compose down`. To also wipe the database, run
`docker compose down -v`.

## 4. Run checks without Docker

These are the same commands CI runs.

```bash
# backend (same for runner/)
cd backend
uv sync                      # creates .venv with Python 3.12
uv run ruff check .
uv run ruff format .
uv run pytest
uv run uvicorn app.main:app --reload   # run it on its own at :8000

# frontend
cd frontend
npm install
npm run lint
npm run format
npx vitest run               # `npm test` for watch mode
npm run dev                  # :5173, proxies /api to localhost:8000
```

Sandbox smoke test (builds the sandbox image, about a minute the first time):

```bash
sandbox/smoke-test.sh
```

## 5. VS Code

Open the folder through WSL (`code .` from Ubuntu). Recommended extensions:
Python, Ruff, C/C++, Docker, GitHub Actions, Prettier and
[oxc](https://marketplace.visualstudio.com/items?itemName=oxc.oxc-vscode) (oxlint).

Point the Python interpreter at `backend/.venv` or `runner/.venv`
(*Python: Select Interpreter*).

## Troubleshooting

- **`permission denied ... docker.sock`**: you're not in the `docker` group yet.
  Run `sudo usermod -aG docker $USER`, then restart WSL (`wsl --shutdown` in PowerShell).
- **Port already in use**: something else is on 5173/8000/8001. Stop it, or
  change the left side of the port mapping in `docker-compose.yml` locally.
- **Frontend doesn't hot reload**: make sure the repo is under `~/code`, not `/mnt/c`.
