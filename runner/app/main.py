from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.sandbox import NotImplementedSandbox, RunResult, Sandbox, TestCase

app = FastAPI(title="SecureCode Runner", version="0.1.0")
sandbox: Sandbox = NotImplementedSandbox()


class RunRequest(BaseModel):
    source: str
    tests: list[TestCase] = []


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "runner"}


@app.post("/run")
def run(request: RunRequest) -> RunResult:
    try:
        return sandbox.run_code(request.source, request.tests)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
