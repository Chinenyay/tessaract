# Architecture

Tessaract has three layers:

```
 your agent code
      │  canonical types (UserMessage, FunctionTool, ReasoningOptions, …)
      ▼
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Tessaract   │ ──▶ │     Adapter      │ ──▶ │     Provider     │ ──▶ vendor SDK / API
│  (client.py) │     │ (translation)    │     │ (SDK client)     │
└──────────────┘     └──────────────────┘     └──────────────────┘
      ▲                       │
      │   Response / StreamEventUnion (canonical, with .raw)
      └───────────────────────┘
```

## Providers

A **provider** (`providers/`) holds credentials and the vendor SDK client. `OpenAIProvider` builds `openai.OpenAI(...)` from its typed fields plus `provider_args`, falls back to `OPENAI_API_KEY`, and imports the SDK lazily, so Tessaract depends only on `pydantic` unless you install an extra.

## Adapters

An **adapter** (`adapters/`) translates in both directions between canonical types and one vendor's API. The `Adapter` base class defines the translation hooks:

| Method | Direction | Purpose |
| --- | --- | --- |
| `map_input_message(UserMessage)` | canonical → native | User turns |
| `map_tool_result(FunctionToolResult)` | canonical → native | Tool outputs |
| `map_function_schema(list[FunctionTool])` | canonical → native | Tool definitions |
| `map_reasoning_params(ReasoningOptions)` | canonical → native | Reasoning configuration |
| `map_reasoning(...)` | canonical → native | Reserved |

`OpenAIAdapter` also implements:

- `_normalize_output_item` / `_normalize_output`, which turn native output items into canonical ones
- `_normalize_stream_event`, which turns native stream events into canonical ones
- `_build_request_kwargs`, which merges the canonical parameters with `provider_options` (canonical wins)
- `generate_sync(request) -> Response`
- `generate_stream(request) -> Iterator[StreamEventUnion]`

## The request lifecycle

1. `Tessaract.send()` splits `"oai/gpt-…"` into the prefix and the model name, and looks up the provider and adapter.
2. `_build_request_model` converts each `input` item:
   - `str` → `UserMessage` → `adapter.map_input_message`
   - `InputType` → `item.raw(adapter)`, which calls the matching `map_*` hook
   - output items (`AssistantMessage`, `OutputItem`) → their stored `.raw` native object
3. A canonical `Request` goes to `adapter.generate_sync` or `adapter.generate_stream`.
4. The adapter calls the SDK, then normalizes the result into a `Response` or a stream of events.

## Design principles

- **Canonical first, native always available.** Every canonical object keeps the native payload (`raw`, `raw_response`, `raw_event`), so nothing is lost and you can always go down to the SDK.
- **Lossless history.** Output items replay from `.raw`, so provider-specific state such as reasoning IDs and encrypted content survives across turns.
- **Unknowns pass through.** Output items that Tessaract can't model become `ProviderOutputItem`, and stream events it can't model become `CustomProviderEvent`. Neither is dropped.
- **Canonical parameters win.** `request_options` and `provider_options` can add native parameters, but they can't override the canonical ones.

## Adding a provider

1. Subclass `Provider` and create the SDK client in `__post_init__`. Import the SDK lazily and raise a helpful `ImportError`.
2. Subclass `Adapter` and implement the `map_*` hooks, output normalization, stream normalization, `generate_sync` and `generate_stream`.
3. Register the pair in `Tessaract.register_adapter()` and add the provider type to the `send()` dispatch.
4. Add an optional dependency group to `pyproject.toml`. An `anthropic` extra is already declared.
5. Export the provider from `tessaract/__init__.py`.
