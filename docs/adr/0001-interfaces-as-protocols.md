# 0001: External dependencies behind async Protocol interfaces

**Context.** The agent depends on five external systems: code execution, a job
queue, session storage, dataset storage, and an LLM provider. Each needs a local
implementation for development and tests, and a production one later.

**Decision.** Each dependency is a `typing.Protocol` with `async` methods, living
in the package that owns it (`sandbox`, `worker`, `storage`, `llm`). Inputs and
outputs are plain dataclasses, not provider types.

**Alternatives.**
- `abc.ABC` base classes: implementations must inherit, so a test fake is tied
  to the hierarchy. Protocols are checked structurally by mypy instead.
- Sync interfaces: simpler, but LLM calls, sandbox runs and storage are all I/O
  bound, and the API server will be async.
- Using provider SDK types directly (e.g. an LLM SDK's message class): less
  code now, but every module would then depend on that provider.

**Trade-off.** Protocols give no runtime enforcement unless checked with
`isinstance` (they are marked `@runtime_checkable`, which only checks method
names, not signatures). We rely on mypy in strict mode to catch mismatches.
