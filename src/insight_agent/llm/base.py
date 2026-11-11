"""LLMClient interface: a provider-neutral view of a chat model with tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable

Role = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True)
class ToolCall:
    """A model's request to invoke a tool."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class Message:
    """One turn in a conversation."""

    role: Role
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    # Set when role == "tool": which ToolCall this message answers.
    tool_call_id: str | None = None


@dataclass(frozen=True)
class ToolSpec:
    """A tool the model may call, described by a JSON Schema."""

    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass(frozen=True)
class LLMResponse:
    """The model's reply plus accounting data for telemetry and cost tracking."""

    message: Message
    stop_reason: str
    input_tokens: int
    output_tokens: int
    model: str


@runtime_checkable
class LLMClient(Protocol):
    """Sends a conversation to a model and returns its next message."""

    async def complete(
        self,
        messages: list[Message],
        *,
        tools: list[ToolSpec] | None = None,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        ...
