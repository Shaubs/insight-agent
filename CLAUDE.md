# Insight Agent

A data analyst AI agent: user uploads a CSV, asks questions in plain English, the agent
writes and runs Python to answer, with charts. Built as an interview showcase for
systems thinking, observability and token efficiency.

Read docs/REQUIREMENTS.md for functional and non-functional requirements (FR-x, NFR-x).

## Principles
- Every external dependency sits behind an interface: LLMClient, Sandbox, DatasetStore,
  SessionStore, TelemetryStore. Local implementations now, scalable ones later.
- LLM access is OpenAI-compatible only (base_url + model + api_key). No provider-specific SDKs.
- Telemetry is built in as we go, never retrofitted. Telemetry failures must not break a run.
- Prompts live in prompts/*.md, not inline strings.
- Never log or persist API keys.

## Conventions
- Python 3.11+, type hints everywhere, dataclasses or pydantic for data shapes.
- ruff for lint/format, pytest for tests. Tests must not need a real API key (use FakeLLMClient).
- Package lives in src/insight_agent/.
- Small commits, one slice at a time, conventional commit messages.
- Record significant decisions in docs/adr/NNNN-title.md (Context, Decision, Alternatives, Trade-offs).

## Working style
- Plan before coding; wait for approval on the plan.
- Only build the slice requested. Don't implement future slices.
- I'm learning: briefly explain non-obvious decisions.