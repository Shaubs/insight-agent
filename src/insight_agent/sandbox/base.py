"""Sandbox interface: runs untrusted, LLM-generated code in isolation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class ExecutionResult:
    """Outcome of running one code snippet in a sandbox."""

    stdout: str
    stderr: str
    exit_code: int
    duration_s: float
    timed_out: bool = False
    # Files produced by the run (e.g. charts), keyed by path inside the sandbox.
    artifacts: dict[str, bytes] = field(default_factory=dict)


@runtime_checkable
class Sandbox(Protocol):
    """Executes code in an isolated environment.

    Implementations might be a local subprocess, a container, or a remote
    microVM. Callers must not assume anything about where the code runs.
    """

    async def execute(
        self,
        code: str,
        *,
        session_id: str,
        timeout_s: float = 30.0,
    ) -> ExecutionResult:
        """Run `code` in the sandbox bound to `session_id`.

        State (variables, loaded dataframes) persists between calls with the
        same `session_id` until `close` is called.
        """
        ...

    async def mount_dataset(self, session_id: str, dataset_id: str) -> str:
        """Make a dataset available to the session; return its in-sandbox path."""
        ...

    async def close(self, session_id: str) -> None:
        """Release all resources held for `session_id`."""
        ...
