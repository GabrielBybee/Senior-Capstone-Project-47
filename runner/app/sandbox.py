"""The one interface the rest of the system uses to run code.

Today there is only a stub. The Docker implementation comes in Phase 3, and a
Kubernetes Jobs implementation can replace it later without changing callers.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class TestCase(BaseModel):
    __test__ = False  # not a pytest test class

    name: str
    stdin: str = ""
    args: list[str] = []
    expected_exit_code: int = 0


class TestResult(BaseModel):
    __test__ = False

    name: str
    passed: bool
    exit_code: int | None
    stdout: str = ""
    stderr: str = ""


class RunResult(BaseModel):
    compiled: bool
    compiler_output: str = ""
    tests: list[TestResult] = []
    sanitizer_findings: list[str] = []
    cppcheck_findings: list[str] = []
    valgrind_findings: list[str] = []
    timed_out: bool = False


class Sandbox(ABC):
    @abstractmethod
    def run_code(self, source: str, tests: list[TestCase]) -> RunResult: ...


class NotImplementedSandbox(Sandbox):
    def run_code(self, source: str, tests: list[TestCase]) -> RunResult:
        raise NotImplementedError("The Docker sandbox is built in Phase 3.")
