# Insight Agent
Goal: a data analyst AI agent, built to showcase systems thinking at scale.
Principles:
- Every external dependency sits behind an interface (Sandbox, JobQueue,
  SessionStore, DatasetStore, LLMClient) with a local implementation.
- Observability (OpenTelemetry) is built in from the start, not added later.
- Explain trade-offs in docs/adr/ (short: Context, Decision, Alternatives, Trade-off).
- Small commits, one vertical slice at a time.
- I'm learning: explain non-obvious decisions briefly as you go.