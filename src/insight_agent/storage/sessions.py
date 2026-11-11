"""SessionStore interface: durable conversation state."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, runtime_checkable

from insight_agent.llm.base import Message


@dataclass
class Session:
    id: str
    created_at: datetime
    updated_at: datetime
    dataset_ids: list[str] = field(default_factory=list)
    messages: list[Message] = field(default_factory=list)


@runtime_checkable
class SessionStore(Protocol):
    """Stores sessions so any API or worker process can resume one."""

    async def create(self, dataset_ids: list[str] | None = None) -> Session:
        ...

    async def get(self, session_id: str) -> Session | None:
        ...

    async def append_messages(self, session_id: str, messages: list[Message]) -> None:
        """Append to a session's history. Never rewrites earlier messages."""
        ...

    async def delete(self, session_id: str) -> None:
        ...
