# Decisions

Short records of choices that affect the whole project, newest first. Add an
entry when you choose a library, change the architecture or reverse an earlier
decision.

Format: **Decision**, then *why*, then the alternatives considered.

---

## 2026-10-28: oxlint instead of ESLint for the frontend

**Decision:** Lint TypeScript with oxlint, which is what the Vite React template
now uses, and format with Prettier.

*Why:* The template ships TypeScript 7. typescript-eslint only supports
TypeScript below 6.1, so installing ESLint failed with a peer-dependency
conflict. oxlint works with TypeScript 7 and includes the React hooks rules.

*Alternatives:* Pin TypeScript to 6.0 and use ESLint, which is the original
plan. Revisit when typescript-eslint supports TypeScript 7.

## 2026-10-28: Branch flow main ← test ← feature branches

**Decision:** `main` only receives PRs from `test`. All work branches off `test`
and merges back into it. Dependabot targets `test`.

*Why:* Keeps `main` deployable once CD is set up. `test` is where things are
integrated and tried together.

## 2026-10-28: Model experiments moved off main

**Decision:** Removed `experiments/` from `main`. The scripts and results stay
on the `AI-testing` branch.

*Why:* A clean `main` for the project skeleton. The comparison results still
inform the choice of default model.

## 2026-10: Sandbox runs in throwaway Docker containers behind one interface

**Decision:** One short-lived container per run: no network, read-only,
non-root, no capabilities, with CPU, memory, process and time limits. Callers
use `Sandbox.run_code(source, tests)`.

*Why:* Student and LLM-generated C code is untrusted. One interface lets us
swap Docker for Kubernetes Jobs if we deploy to OIT's cluster.

*Alternatives:* Running code in-process or in a long-lived container (not safe
enough). Using a hosted code-execution API (data leaves the university, and
it costs money).

## 2026-10: Tools grade, not the LLM

**Decision:** A fix is correct when the tests pass, ASan/UBSan are clean and
there are no new Cppcheck or Valgrind findings. The LLM only generates
exercises and hints.

*Why:* LLM judgments aren't reliable or reproducible enough for grading.

## 2026-10: Stack

**Decision:** React + TypeScript + Vite frontend. Python 3.12 + FastAPI backend.
PostgreSQL. uv for Python packages. The OpenAI SDK pointed at MindRouter, with
no LangChain. Docker Compose for local development, GitHub Actions for CI,
GHCR for images.

*Why:* The team knows Python, and FastAPI and Pydantic suit typed APIs and
structured LLM output. MindRouter is OpenAI-compatible, so the official SDK is
enough. LangChain adds abstraction we don't need.

## 2026-10: Hosting: ask OIT for a VM

**Decision:** Request a university VM (4–8 vCPU, 16 GB RAM, 80–100 GB disk)
running Docker Compose, with a self-hosted GitHub Actions runner for deploys.

*Alternatives:* An OIT Kubernetes namespace with Argo CD (fallback), or a
cloud provider (FERPA and cost concerns).

## Open (to decide at the team meeting)

- Default MindRouter model (see results on `AI-testing`)
- Auth: university SSO (Entra ID) vs. class join code + own accounts
- First bug types to support
- C only, or C and C++
- Frontend design
- Who owns which part
