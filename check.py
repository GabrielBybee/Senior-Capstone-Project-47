#!/usr/bin/env python3
"""Quality gate: runs every check CI runs, from one command.

    python3 check.py                    full gate (what CI runs)
    python3 check.py --fast             skip slow checks (used by the pre-push hook)
    python3 check.py --fix              auto-fix formatting and lint first, then check
    python3 check.py backend frontend   only some areas
    python3 check.py --list             show every check, including planned ones
    python3 check.py --install-hook     run --fast automatically before every git push

Uses only the Python standard library. Docker-based tools (gitleaks, shellcheck,
hadolint, Trivy) run from their official images, so nothing extra to install.
"""

from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent

GITLEAKS = "ghcr.io/gitleaks/gitleaks:v8.30.1"
SHELLCHECK = "koalaman/shellcheck:v0.11.0"
HADOLINT = "hadolint/hadolint:v2.15.1"
TRIVY = "aquasec/trivy:0.76.1"

SHELL_SCRIPTS = ["sandbox/smoke-test.sh", "sandbox/smoke/check.sh", ".githooks/pre-push"]
DOCKERFILES = [
    "backend/Dockerfile",
    "runner/Dockerfile",
    "frontend/Dockerfile",
    "sandbox/Dockerfile",
]
# (tag, build context, extra docker build args)
IMAGES = [
    ("securecode-backend:check", "backend", []),
    ("securecode-runner:check", "runner", []),
    ("securecode-frontend:check", "frontend", ["--target", "prod"]),
    ("securecode-sandbox:check", "sandbox", []),
]


@dataclass
class Check:
    area: str
    name: str
    steps: list[list[str]]
    cwd: str = "."
    slow: bool = False
    needs: list[str] = field(default_factory=list)  # tools that must be on PATH
    fix: list[list[str]] = field(default_factory=list)  # run first with --fix


def docker_run(image: str, *args: str, mount: str = "/repo") -> list[str]:
    return [
        "docker",
        "run",
        "--rm",
        "--quiet",
        "-v",
        f"{ROOT}:{mount}:ro",
        "-w",
        mount,
        image,
        *args,
    ]


def python_checks(service: str) -> list[Check]:
    uv = ["uv", "run", "--locked"]
    return [
        Check(service, "lockfile up to date", [["uv", "lock", "--check"]], service, needs=["uv"]),
        Check(
            service,
            "ruff lint",
            [[*uv, "ruff", "check", "."]],
            service,
            needs=["uv"],
            fix=[[*uv, "ruff", "check", "--fix", "."]],
        ),
        Check(
            service,
            "ruff format",
            [[*uv, "ruff", "format", "--check", "."]],
            service,
            needs=["uv"],
            fix=[[*uv, "ruff", "format", "."]],
        ),
        Check(service, "mypy types", [[*uv, "mypy", "."]], service, needs=["uv"]),
        Check(service, "pytest", [[*uv, "pytest", "-q"]], service, needs=["uv"]),
        Check(
            service,
            "dependency audit",
            [[*uv, "pip-audit", "--progress-spinner", "off"]],
            service,
            slow=True,
            needs=["uv"],
        ),
    ]


def image_steps() -> list[list[str]]:
    steps: list[list[str]] = []
    for tag, context, extra in IMAGES:
        steps.append(["docker", "build", "-q", "-t", tag, *extra, context])
    for tag, _, _ in IMAGES:
        steps.append(
            [
                "docker",
                "run",
                "--rm",
                "--quiet",
                "-v",
                "/var/run/docker.sock:/var/run/docker.sock",
                "-v",
                "securecode-trivy-cache:/root/.cache",
                TRIVY,
                "image",
                "--quiet",
                "--exit-code",
                "1",
                "--ignore-unfixed",
                "--severity",
                "HIGH,CRITICAL",
                tag,
            ]
        )
    return steps


CHECKS: list[Check] = [
    *python_checks("backend"),
    *python_checks("runner"),
    Check(
        "frontend",
        "oxlint (incl. jsx-a11y)",
        [["npm", "run", "-s", "lint"]],
        "frontend",
        needs=["npm"],
        fix=[["npx", "oxlint", "--fix"]],
    ),
    Check(
        "frontend",
        "prettier",
        [["npm", "run", "-s", "format:check"]],
        "frontend",
        needs=["npm"],
        fix=[["npm", "run", "-s", "format"]],
    ),
    Check(
        "frontend",
        "typescript types",
        [["npm", "run", "-s", "typecheck"]],
        "frontend",
        needs=["npm"],
    ),
    Check(
        "frontend", "vitest (incl. axe WCAG)", [["npx", "vitest", "run"]], "frontend", needs=["npm"]
    ),
    Check(
        "frontend", "build", [["npm", "run", "-s", "build"]], "frontend", slow=True, needs=["npm"]
    ),
    Check(
        "frontend",
        "dependency audit",
        [["npm", "audit", "--audit-level=high"]],
        "frontend",
        slow=True,
        needs=["npm"],
    ),
    Check(
        "repo",
        "secrets (gitleaks)",
        [docker_run(GITLEAKS, "git", "/repo", "--no-banner", "--redact")],
        needs=["docker"],
    ),
    Check(
        "repo",
        "shell scripts (shellcheck)",
        [docker_run(SHELLCHECK, *SHELL_SCRIPTS)],
        needs=["docker"],
    ),
    Check(
        "repo",
        "Dockerfiles (hadolint)",
        [docker_run(HADOLINT, "hadolint", "--no-color", *DOCKERFILES)],
        needs=["docker"],
    ),
    Check(
        "repo", "docker-compose.yml", [["docker", "compose", "config", "--quiet"]], needs=["docker"]
    ),
    Check(
        "repo",
        "check.py lint",
        [
            [
                "uv",
                "run",
                "--project",
                "backend",
                "ruff",
                "check",
                "--config",
                "backend/pyproject.toml",
                "check.py",
            ],
            [
                "uv",
                "run",
                "--project",
                "backend",
                "ruff",
                "format",
                "--config",
                "backend/pyproject.toml",
                "--check",
                "check.py",
            ],
        ],
        needs=["uv"],
        fix=[
            [
                "uv",
                "run",
                "--project",
                "backend",
                "ruff",
                "format",
                "--config",
                "backend/pyproject.toml",
                "check.py",
            ]
        ],
    ),
    Check("sandbox", "smoke test", [["sandbox/smoke-test.sh"]], slow=True, needs=["docker"]),
    Check("images", "build + Trivy scan", image_steps(), slow=True, needs=["docker"]),
]

# Shown by --list so nobody forgets them. Add each as a real check when its code lands.
PLANNED = [
    ("backend", "rule 1: the reference fix never appears in any API response", "Phase 3"),
    ("backend", "hint leak + guardrail prompts are refused", "Phase 3"),
    ("backend", "alembic check: models and migrations match", "Phase 3"),
    ("backend", "coverage minimum (pytest-cov)", "Phase 3"),
    ("runner", "sandbox escape tests: fork/memory bomb, file writes, network", "Phase 3"),
    ("frontend", "API types in sync with backend OpenAPI schema", "Phase 3"),
    ("frontend", "Playwright end-to-end + axe on real pages (contrast, focus)", "Phase 3"),
    ("ci only", "CodeQL code scanning", "runs in .github/workflows/codeql.yml"),
]

AREAS = sorted({c.area for c in CHECKS})

# ---------------------------------------------------------------------------

COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def paint(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if COLOR else text


GREEN, RED, YELLOW, DIM, BOLD = "32", "31", "33", "2", "1"


def tool_path() -> str:
    """PATH plus nvm's newest Node, so npm works from hooks and editors too."""
    path = os.environ.get("PATH", "")
    if shutil.which("npm", path=path):
        return path
    nvm_bins = sorted(glob.glob(os.path.expanduser("~/.nvm/versions/node/*/bin")))
    extra = [nvm_bins[-1]] if nvm_bins else []
    extra.append(os.path.expanduser("~/.local/bin"))  # uv's default install location
    return os.pathsep.join([*extra, path])


def run(cmd: list[str], cwd: Path, env: dict[str, str]) -> tuple[int, str]:
    # Commands come from the CHECKS table in this file, never from user input.
    proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, check=False)  # noqa: S603
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the quality gate.")
    parser.add_argument("areas", nargs="*", metavar="AREA", help=f"only: {', '.join(AREAS)}")
    parser.add_argument("--fast", action="store_true", help="skip slow checks")
    parser.add_argument("--fix", action="store_true", help="auto-fix formatting and lint first")
    parser.add_argument("--list", action="store_true", help="list checks and exit")
    parser.add_argument("--install-hook", action="store_true", help="install the pre-push hook")
    args = parser.parse_args()
    unknown = sorted(set(args.areas) - set(AREAS))
    if unknown:
        parser.error(f"unknown area {', '.join(unknown)} (choose from {', '.join(AREAS)})")

    if args.install_hook:
        git = ["git", "config", "core.hooksPath", ".githooks"]
        subprocess.run(git, cwd=ROOT, check=True)  # noqa: S603, S607
        print("Installed: git push now runs `python3 check.py --fast` first.")
        print("Skip it once with `git push --no-verify`.")
        return 0

    selected = [
        c for c in CHECKS if (not args.areas or c.area in args.areas) and not (args.fast and c.slow)
    ]

    if args.list:
        for c in CHECKS:
            tag = paint(" (slow)", DIM) if c.slow else ""
            print(f"  {c.area:<9} {c.name}{tag}")
        print(paint("\nPlanned:", BOLD))
        for area, name, when in PLANNED:
            print(f"  {area:<9} {name}  " + paint(f"[{when}]", DIM))
        return 0

    env = {**os.environ, "PATH": tool_path(), "NO_COLOR": "1"}
    results: list[tuple[Check, str, float]] = []

    for check in selected:
        label = f"{check.area:<9} {check.name}"
        missing = [t for t in check.needs if not shutil.which(t, path=env["PATH"])]
        if missing:
            print(f"{label:<48} {paint('SKIP', YELLOW)}  missing: {', '.join(missing)}")
            results.append((check, "skip", 0.0))
            continue

        cwd = ROOT / check.cwd
        if check.cwd == "frontend" and not (cwd / "node_modules").exists():
            print(paint("  installing frontend dependencies (npm ci)…", DIM))
            run(["npm", "ci", "--no-fund", "--no-audit"], cwd, env)

        print(f"{label:<48} ", end="", flush=True)
        start = time.monotonic()
        if args.fix:
            for cmd in check.fix:
                run(cmd, cwd, env)
        code, output = 0, ""
        for cmd in check.steps:
            code, out = run(cmd, cwd, env)
            output += out
            if code != 0:
                break
        elapsed = time.monotonic() - start

        if code == 0:
            print(f"{paint('PASS', GREEN)}  {elapsed:5.1f}s")
            results.append((check, "pass", elapsed))
        else:
            print(f"{paint('FAIL', RED)}  {elapsed:5.1f}s")
            lines = output.strip().splitlines()
            for line in lines[-60:]:
                print(paint("    │ ", DIM) + line)
            results.append((check, "fail", elapsed))

    failed = [c for c, status, _ in results if status == "fail"]
    skipped = [c for c, status, _ in results if status == "skip"]
    total = sum(t for _, _, t in results)
    print()
    if failed:
        names = ", ".join(f"{c.area} {c.name}" for c in failed)
        print(paint(f"{len(failed)} of {len(results)} checks failed: {names}", RED))
    else:
        print(paint(f"All {len(results) - len(skipped)} checks passed in {total:.0f}s.", GREEN))
    if skipped:
        print(
            paint(f"{len(skipped)} skipped because a tool is missing (see docs/setup.md).", YELLOW)
        )
    if args.fast:
        print(paint("Fast mode: slow checks were skipped. Run `python3 check.py` for all.", DIM))
    return 1 if failed or (skipped and os.environ.get("CI")) else 0


if __name__ == "__main__":
    sys.exit(main())
