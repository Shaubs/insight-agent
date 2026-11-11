# Insight Agent: Requirements

Scope note: Phase 1 (1 hour) = the product. Phase 2 = harness, evals, load tests, scaling.
Priority: P0 = must ship in Phase 1, P1 = Phase 1 if time allows, P2 = Phase 2.

## 1. Functional Requirements

### FR-1 Dataset ingestion
- FR-1.1 (P0) User uploads a CSV (later: Parquet/Excel). Max 50 MB.
- FR-1.2 (P0) System profiles it: columns, dtypes, row count, null %, 5 sample rows.
- FR-1.3 (P0) Datasets are stored behind a `DatasetStore` interface (local disk now).
- Acceptance: upload -> profile returned in < 2 s for a 10 MB file.

### FR-2 Natural-language analysis
- FR-2.1 (P0) User asks a question in plain English about the dataset.
- FR-2.2 (P0) Agent plans, writes Python (pandas/matplotlib), executes, inspects
  results, and iterates until it can answer.
- FR-2.3 (P0) Final answer = short text summary + any generated charts/tables.
- FR-2.4 (P1) Multi-turn: follow-up questions use prior context ("now break that down by region").
- Acceptance: 8 of 10 benchmark questions answered correctly on a sample dataset.

### FR-3 Tools available to the agent
- FR-3.1 (P0) `describe_data`: returns schema/profile (never the raw rows beyond a sample).
- FR-3.2 (P0) `run_python`: executes code in an isolated environment, returns
  truncated stdout, errors, and artifacts (files/plots).
- FR-3.3 (P1) `make_report`: compiles findings into a themed HTML/PDF report.
- FR-3.4 (P1) Tool definitions are declarative (name, JSON schema, handler) so new tools plug in without touching the loop.

### FR-4 Pluggable LLM provider
- FR-4.1 (P0) A single `LLMClient` interface: `complete(messages, tools, system, **opts) -> LLMResponse`.
- FR-4.2 (P0) One adapter: OpenAI-compatible (OpenAI, Groq, OpenRouter, Gemini, Ollama,
  Anthropic compat endpoint). Selected by base_url + model + api_key.
- FR-4.3 (P0) Provider, model, API key and base URL set via .env or the UI, never hardcoded.
- FR-4.4 (P0) `LLMResponse` is provider-neutral: text, tool_calls, usage
  (input/output/cached tokens), latency_ms, stop_reason.
- FR-4.5 (P0) Provider profiles declare capabilities: supports_tools,
  reports_cached_tokens, supports_streaming, max_context, price per 1M tokens.
- FR-4.6 (P2) Native Anthropic adapter for explicit prompt caching.

### FR-5.1 (revised)
- FR-5.1 (P0) Static prompt prefix (system prompt + tool defs) is byte-stable across calls
  so provider-side caching can hit. Cached tokens are recorded when the provider reports them.

### FR-7 Analyst UI (page 1)
- FR-7.1 (P0) Upload a CSV and see the profile (schema, nulls, sample rows).
- FR-7.2 (P0) Chat: ask questions, see the answer, charts and result tables inline.
- FR-7.3 (P0) Expandable "agent steps" per answer: code generated, tool outputs, errors.
- FR-7.4 (P0) Settings sidebar: base_url, model, API key (masked, session-only).
- FR-7.5 (P1) Download generated charts/tables.
- FR-7.6 (P0) UI is a thin layer over the core; everything also works via Python/CLI.

### FR-8 Session management
- FR-8.1 (P0) A session = dataset + conversation history + its runs, behind a `SessionStore`
  interface (SQLite now).
- FR-8.2 (P0) Create a new session, switch between sessions, resume one after restart.
- FR-8.3 (P1) Rename and delete sessions.

### FR-9 Telemetry store (data layer for the dashboard)
- FR-9.1 (P0) Every run, LLM call and tool call is written as a structured record to SQLite
  behind a `TelemetryStore` interface.
- FR-9.2 (P0) Records:
  - run: run_id, session_id, question, status, steps, total tokens, cost, latency, timestamps
  - llm_call: run_id, step, model, input/output/cached tokens, cost, latency_ms, stop_reason
  - tool_call: run_id, step, tool name, args (truncated), duration_ms, success/error,
    output size before/after truncation
- FR-9.3 (P0) Structured logs (JSON) with run_id/session_id on every line, also stored.
- FR-9.4 (P0) Secrets are redacted before anything is written.
- FR-9.5 (P2) Same records exported via OpenTelemetry (traces + metrics).

### FR-10 Observability dashboard (page 2)
- FR-10.1 (P0) Overview cards: total runs, total tokens, total cost, avg latency, success rate.
- FR-10.2 (P0) Token panel: input vs output vs cached per run, cache hit rate,
  tokens per successful answer.
- FR-10.3 (P0) Efficiency panel: tokens saved by truncation (output size before vs after),
  avg steps per run.
- FR-10.4 (P0) Tools panel: call counts per tool, error rate per tool, avg duration.
- FR-10.5 (P0) Run explorer: pick a run, see its step-by-step timeline
  (LLM call -> tool call -> ...) with tokens and latency per step.
- FR-10.6 (P0) Log viewer: filter by session, run, level.
- FR-10.7 (P1) Filter everything by session, model and time range.
- FR-10.8 (P1) Latency panel: p50/p95 per run and per step type.
- FR-10.9 (P2) Alert rules evaluated over these metrics (Phase 2).

## 2. Non-Functional Requirements

Targets are for a single node in Phase 1; the "At scale" column is the design intent for Phase 2 docs.

| ID | Category | Requirement | Phase 1 target | At scale (design) |
|----|----------|-------------|----------------|-------------------|
| NFR-1 | Latency | Time to first visible agent event | < 2 s | < 2 s via streaming |
| NFR-2 | Latency | End-to-end simple question | p95 < 30 s | p95 < 30 s under load |
| NFR-3 | Latency | Single sandbox execution | < 10 s hard timeout | warm sandbox pool, < 500 ms start |
| NFR-4 | Cost | Cost per question | < $0.05 (Haiku-class) | per-tenant budgets |
| NFR-5 | Token efficiency | Raw dataset tokens in prompt | 0 | 0 |
| NFR-6 | Token efficiency | Cache hit rate on static prefix | > 80% after the first call | monitored, alert on drop |
| NFR-7 | Reliability | Retry transient LLM errors (429/5xx) with backoff | 3 retries | + circuit breaker, fallback model |
| NFR-8 | Reliability | Agent run always terminates | max 12 steps, max token budget | enforced by harness |
| NFR-9 | Security | Generated code is untrusted | timeout + restricted dir | Docker/gVisor, no network |
| NFR-10 | Security | Secrets never logged or committed | .env + redaction in logs | secret manager |
| NFR-11 | Modularity | Every external dependency behind an interface | LLM, Sandbox, DatasetStore, SessionStore | swap for S3, Redis, K8s jobs |
| NFR-12 | Observability | Structured logs with a run_id on every line | yes | OTel traces + metrics (Phase 2) |
| NFR-13 | Observability | Per-call usage captured in a uniform record | yes | exported as metrics |
| NFR-14 | Testability | Core runs without a real LLM (fake client) | yes | enables deterministic evals |
| NFR-15 | Portability | One-command start | `streamlit run` / docker compose | Helm/K8s |
| NFR-16 | Maintainability | Type hints, ruff, pytest smoke tests | yes | CI |
| NFR-17 | Observability | Telemetry writes never block or fail the agent run | best-effort, errors logged | async export via OTel collector |
| NFR-18 | Performance | Dashboard loads with 1,000 runs stored | < 2 s | metrics backend (Prometheus/Grafana) |
| NFR-19 | Privacy | API keys never persisted; question text stored only locally | yes | configurable retention |

## 3. Out of scope for Phase 1
Auth/multi-tenancy, job queue + workers, Docker sandbox, OTel/alerts, load testing, evals harness.
These get designed in docs/SCALING.md and built in Phase 2.