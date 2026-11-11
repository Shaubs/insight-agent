"""Smoke test: every interface is importable and is a Protocol."""

from typing import Protocol

from insight_agent.llm import LLMClient
from insight_agent.sandbox import Sandbox
from insight_agent.storage import DatasetStore, SessionStore
from insight_agent.worker import JobQueue


def test_interfaces_are_protocols() -> None:
    for iface in (Sandbox, JobQueue, SessionStore, DatasetStore, LLMClient):
        assert Protocol in iface.__mro__, iface
