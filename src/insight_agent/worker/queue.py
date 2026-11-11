"""JobQueue interface: decouples accepting a request from running it."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class Job:
    id: str
    kind: str
    payload: dict[str, Any]
    status: JobStatus
    created_at: datetime
    attempts: int = 0
    error: str | None = None
    result: dict[str, Any] | None = None


@runtime_checkable
class JobQueue(Protocol):
    """At-least-once job queue.

    A dequeued job is leased to one worker. If the worker neither acks nor
    nacks before the lease expires, the job becomes visible again, so job
    handlers must be idempotent.
    """

    async def enqueue(self, kind: str, payload: dict[str, Any]) -> str:
        """Add a job; return its id."""
        ...

    async def dequeue(self, *, lease_s: float = 60.0) -> Job | None:
        """Lease the next queued job, or return None if the queue is empty."""
        ...

    async def ack(self, job_id: str, result: dict[str, Any] | None = None) -> None:
        """Mark a leased job as succeeded."""
        ...

    async def nack(self, job_id: str, error: str, *, retry: bool = True) -> None:
        """Mark a leased job as failed, optionally re-queueing it."""
        ...

    async def get(self, job_id: str) -> Job | None:
        """Look up a job's current state (for status polling)."""
        ...
