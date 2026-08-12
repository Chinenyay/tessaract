# Tessaract — Canonical Layer Review

**Reviewed:** 11 Aug 2026 · **Commit:** `6157b01` · **Scope:** `canonical/`, `adapters/`, `client.py`, `models.py`

> Tessaract is aimed at the right target and modelled from the wrong end. The response and
> streaming models are genuinely good work. The tool layer inverted the abstraction, and the
> request model — the hardest part of this problem — has not been started yet. Both are much
> cheaper to fix now than after two adapters exist.

---

## Verdict

**You are on track on intent and off track on layering.** The premise is sound and your instincts on the response side are better than most libraries in this space: keeping `raw_response` on every object, splitting canonical fields from a `provider_metadata` escape hatch, preserving reasoning `signature` and `encrypted_content`, and separating cache-read from cache-write tokens in `Usage`. Those are decisions people usually get wrong on the first attempt and then cannot undo.

The problem is concentrated in `canonical/tools/`. There, the provider-specific types *are* the model and the canonical type is a union of them. That inverts the whole point of the project — it hands provider branching back to the developer at exactly the place agent code is most complex. You already invented the correct pattern one directory up, in `Annotation` and `ProviderOutputItem`. Apply your own pattern to tools.

Separately: `canonical/` does not currently import. There is a circular import between `responses.py` and `output_types.py`, several classes that were meant to be models are plain classes, and `models.py` has a syntax error. These are quick fixes, but they mean nothing in the package has ever been executed — which is why the modelling mistakes below survived. Get one import-and-round-trip test running before writing another type.

---

## Contract surface coverage

Against your own Phase 1 checklist in `implementation_plan.md`:

| Phase 1 item | Status | Notes |
|---|---|---|
| Generation response | **Solid** | Good shape. Status, finish reason, usage, telemetry, raw passthrough, per-provider subclasses. |
| Streaming events | **Good start** | Six events defined; four more you listed in your own notes are missing, plus inconsistent naming. |
| Usage | **Solid** | Correctly splits cache read from cache write. Most libraries collapse these and lose cost accuracy. |
| Message / content types | **Broken** | Field annotations on non-dataclass subclasses; no part actually holds data. `TextPart("hi")` raises. |
| Tool definitions and calls | **Inverted** | Provider unions instead of canonical shapes. Definitions and calls conflated in one hierarchy. |
| Generation request | **Absent** | No request type at all. No sampling params, reasoning controls, tool_choice, or caching hooks. |
| Error hierarchy | **Absent** | One bare `GatewayError`. No status, retryability, or request id. |
| Provider interface | **Absent** | No Protocol or ABC anywhere. Adapters have no contract to implement. |
| Fake provider | **Absent** | `tests/fake_provider.py` is empty. No tests exist. |
| Model capabilities | **Absent** | In your architecture sketch, not yet in code. This is what prevents silent feature-dropping. |

Phase 1's stated deliverable is "the domain model and contract tests compile and make sense." Neither half is true yet, and the four absent items are the load-bearing ones — the request model and the provider interface are what the adapters in Phase 2 will be written *against*.

---

## Blocking defects

All of these were reproduced against your checked-out tree.

### 1. Circular import — no module in `canonical/` can be imported

`canonical/responses.py:7`, `canonical/output_types.py:5` — **blocking**

`responses.py` imports `OutputItem` from `output_types.py`, which imports `Provider` back from `responses.py`. Either entry point fails:

```
$ python -c "import canonical.responses"
ImportError: cannot import name 'Provider' from partially
initialized module 'canonical.responses'
(most likely due to a circular import)
```

The fix is also the structural fix: `Provider`, `FinishReason`, and the other shared leaf types belong in a `canonical/types.py` that imports nothing from the package. Note that `FinishDetails` and `ResponseTelemetry` are currently defined **twice**, in both files, with different shapes — a symptom of the same missing base module.

### 2. Content parts silently have no fields

`canonical/input_types.py:9–45` — **blocking**

`ContentPart` is a frozen dataclass, but `TextPart`, `ImagePart`, `FilePart`, `AudioPart`, and `ToolResult` are not decorated. Their annotations are inert — Python records them in `__annotations__` and generates nothing:

```pycon
>>> dataclasses.fields(TextPart)
()
>>> TextPart("hello")
TypeError: ContentPart.__init__() takes 1 positional argument but 2 were given
>>> hasattr(TextPart(), "text")
False
```

The desired shape you wrote in the file's closing comment — `Message(TextPart("hello"), ImagePart(...))` — cannot run. This is the clearest single sign that nothing here has been executed yet.

### 3. Pydantic models with plain-class fields fail at schema build

`canonical/tools/anthropic/computer_use.py`, `canonical/tools/openai/computer_use.py` — **blocking**

Same root cause, other library. `AnthropicComputerUseTool` inherits from `ProviderTool(BaseModel)`, so it is a Pydantic model, but its `input` field is a union of fifteen *plain* classes. Only `AnthropicZoom` and `AnthropicHoldKey` extend `BaseModel`:

```
$ python -c "import canonical.tools"
pydantic.errors.PydanticSchemaGenerationError: Unable to generate
pydantic-core schema for <class 'AnthropicScreenshot'>
```

The OpenAI side has the same defect via `SafetyCheck` and `Agent`. And `OpenAIComputerUseToolResult` is itself a plain class, so it will never validate or serialize.

Related: `AnthropicZoom.region` is `tuple[int, int, int, int] = Field(gt=0)` — a numeric constraint cannot apply to a tuple, so it is either an error or silently dropped. Put the per-field bounds on a nested model, or validate the tuple explicitly.

### 4. `models.py` does not parse

`models.py:46` — **blocking**

`registerOpenAIModel` has a signature and no body: `IndentationError: expected an indented block after function definition on line 46`.

Worth reconsidering the file's premise while you are in there. Hardcoding model IDs into enums means every new model release requires a Tessaract version bump before anyone can use it — the opposite of the frictionlessness you are selling. Model IDs should be opaque strings; keep a *separate* optional registry for capability metadata and pricing, keyed by ID and loadable from data, with unknown IDs passing through rather than raising.

### 5. Three bugs in the one adapter, and one anti-pattern to not carry forward

`adapters/openai_adapter.py:8, 19, 23` — **high**

This file still imports from `rough/` so I assume it is scratch, but the mistakes in it are exactly the ones to design out of the real adapters:

- `OpenAI(*self._client_args.model_dump(...))` — single star over a dict iterates **keys** and passes the strings positionally. Needs `**`.
- `OpenAIResponse(response)` — a Pydantic model takes no positional args. Mapping must be an explicit function, not a constructor call.
- `instructions=None` is hardcoded, so the `instructions` parameter is silently ignored.
- `except Exception: raise GatewayError("failed to generate a response.")` destroys the HTTP status, the request ID, and the rate-limit headers. For a gateway that is the worst possible error handling — retry and fallback logic is precisely a function of *which* error occurred. Map to a typed hierarchy (`RateLimitError`, `AuthError`, `OverloadedError`, `ContextLengthError`, `InvalidRequestError`), each carrying `status_code`, `request_id`, `retry_after`, `provider`, and a `retryable` flag, and always chain with `raise ... from exc`.

### 6. Pydantic is undeclared, and the Python floor is high

`pyproject.toml:7–11` — **high**

Every model in `canonical/` depends on Pydantic, but it appears nowhere in `dependencies`. It resolves today only because the OpenAI and Anthropic SDKs happen to pull it in — so a future SDK release that drops or bounds Pydantic differently breaks Tessaract with no signal. Declare it directly with a floor (`pydantic>=2.7`).

Also reconsider `requires-python = ">=3.13"`. You need 3.12 for `type X = ...` statements and 3.11 for `StrEnum`, but nothing here needs 3.13. A library asking for 3.13 excludes most production deployments today; 3.11 with `TypeAlias` would cost you very little and widen adoption considerably.

---

## The structural problem: the canonical layer is not canonical

This is the part of the review that matters most, because it is the part that gets expensive after the adapters exist.

Here is the whole public contract for computer use and shell tools:

```python
# canonical/tools/__init__.py
type ShellTool = (AnthropicBashTool | OpenAILocalShellTool | OpenAIHostedShellTool)
type ComputerUse = (OpenAIComputerUseToolCall | AnthropicComputerUseTool)
```

A union of provider types is not an abstraction — it is a tagged passthrough. Consider what a developer must write to handle a computer-use call, which is the single hottest loop in a computer-use agent:

```python
# what your current model forces
if isinstance(call, AnthropicComputerUseTool):
    action = call.input                 # .coordinate: tuple[int, int]
    if action.action == "left_click":
        x, y = action.coordinate
elif isinstance(call, OpenAIComputerUseToolCall):
    action = call.action                # .x: int, .y: int — and maybe .actions
    if action.type == "click":
        x, y = action.x, action.y
```

Field name differs (`input` vs `action`), discriminator key differs (`action` vs `type`), discriminator value differs (`left_click` vs `click`), coordinate encoding differs (tuple vs two ints). Every one of those differences reaches the developer. Adding Gemini adds a third branch to every such site — which is exactly the failure your own Phase 3 deliverable is written to catch ("the third provider does not require provider conditionals"). You will discover this in Phase 3 and pay to fix it then, with adapters and users already depending on the shape.

### You already solved this

Look at what you did in `output_types.py`. `Annotation` has canonical fields (`source`, `title`, `cited_text`) *plus* `provider`, `provider_annotation_type`, and `provider_metadata`. `ProviderOutputItem` is a clean typed hole for things with no cross-provider meaning. That is the right pattern, and it is the pattern the tool layer is missing.

Applied to computer use, the canonical shape is the intersection — because the underlying thing genuinely *is* the same, both providers are describing a mouse and a keyboard:

```python
# canonical — one shape, provider-agnostic, with an escape hatch
class Click(BaseModel):
    type: Literal["click"] = "click"
    button: Literal["left", "right", "middle", "back", "forward"]
    x: int
    y: int
    modifiers: list[str] = Field(default_factory=list)

type ComputerAction = Click | DoubleClick | TypeText | KeyPress | Scroll \
                    | Drag | MoveMouse | Screenshot | Wait | CursorPosition

class ComputerUseCall(BaseModel):
    call_id: str
    action: ComputerAction
    provider: Provider
    provider_action_type: str          # "left_click" / "click"
    safety_checks: list[SafetyCheck] = Field(default_factory=list)
    provider_metadata: dict[str, Any] = Field(default_factory=dict)
    raw: Any | None = Field(default=None, exclude=True, repr=False)
```

Provider-only actions (Anthropic's `zoom`, `hold_key`, `left_mouse_down`/`up`) go in a `ProviderComputerAction` variant carrying `provider_action_type` and a payload dict — visible, typed as "unportable", and not forcing a branch on the 90% path.

The provider-specific classes you have written are not wasted; they become the adapter's internal wire models. Move them under `providers/openai/` and `providers/anthropic/`, out of `canonical/`. The directory boundary is the design: **nothing under `canonical/` should have a provider name in it.**

### Tool definitions and tool calls are two different things

The hierarchy currently conflates them, which is why the names read oddly. `AnthropicComputerUseTool` extends `ComputerUseTool` — but its fields are `type: Literal["tool_use"]`, `id`, and `input`. That is not a tool *definition*, it is a tool *use block* from a response. Meanwhile `AnthropicComputerUseToolParams` — the actual definition, with `display_width_px` and the dated type version — inherits from nothing in the hierarchy at all. On the OpenAI side, `OpenAIComputerUseToolCall` extends `ClientExecutedProviderTool`, so a call is a subtype of a tool.

These have different lifecycles and different directions of travel. Split them explicitly into three families:

- **Definitions** — request-side, what you declare in `tools=[...]`.
- **Calls** — response-side, what the model emitted.
- **Results** — request-side again, what you send back.

Your four-way taxonomy in `rough/tools.py` (developer-defined/developer-executed, provider/provider, provider/developer, MCP) is a good axis and worth keeping — but it classifies *definitions* only. It does not belong in the call hierarchy.

### Two modelling libraries, no boundary

Messages and content parts are frozen dataclasses; responses, streams, and tools are Pydantic. The seam produces real bugs: `FunctionTool(ContentPart, ClientTool)` inherits from a dataclass and a plain class, declares `name`, `description`, and `input_schema`, and is therefore neither validated nor constructible from those fields. Pick one — Pydantic, given that you want JSON round-tripping, discriminated unions, and schema generation — and use it everywhere. A mixed codebase will keep generating this class of error.

### Smaller items in the same area

- `AnthropicDoubleClick.action` is `Literal['left_click']`. Copy-paste; it also makes the union ambiguous against `AnthropicLeftClick`.
- `OpenAIComputerUseToolCall` has both `action` and `actions`, both optional — so "neither set" and "both set" are representable. Pick one representation and make it required.
- `OpenAIDrag` has only `keys`. OpenAI's drag action carries a `path` of coordinate points; without it the action cannot be executed.
- `OpenAIScreenshot.type` has no default, unlike every sibling — so it must be passed explicitly.
- Verify the modifier-key field on Anthropic's click actions against the reference you cited in `computer_use.py`; I believe it is `text`, not `key`.
- `provider` is a discriminator on `AnthropicBashTool` and `OpenAILocalShellTool` but absent from `OpenAIHostedShellTool`. Put it on the base.
- `Provider` means two unrelated things: a `Literal["anthropic","openai"]` in `responses.py` and a client-config `BaseModel` in `data_models.py`. Rename the latter to `ProviderConfig`. Its field types are also wrong — `default_headers: str` should be a mapping and `default_query: int` should be a mapping.
- `ResponseTelemetry` in `output_types.py` ends with a stray `raw_annotation` field that belongs on `Annotation`.

---

## The missing centre: there is no request model

Nothing in `canonical/` mentions `temperature`, `max_tokens`, `top_p`, `tool_choice`, reasoning effort, thinking budget, stop sequences, response format, or cache control. `FinishReason.MAX_TOKENS` exists; the parameter that causes it does not.

This is the highest-value thing you can do next, and it should happen *before* either adapter, for one reason: **the request model is where the two APIs actually disagree.** Responses are easy to unify because both providers converged on similar output shapes. Requests did not converge. Every hard call in this project lives here:

| Concern | OpenAI Responses | Anthropic Messages | The design question |
|---|---|---|---|
| Output cap | `max_output_tokens`, optional | `max_tokens`, **required** | Canonical optional means you must invent a default for Anthropic. Whatever you pick will surprise someone. Decide and document it. |
| System prompt | `instructions`, or a developer message | top-level `system` param, not a role | You have `Role.system` and `Role.developer` in the enum. Which one is canonical, and how does the other translate? |
| Reasoning | `reasoning.effort` — an ordinal | `thinking.budget_tokens` — a number | Not interconvertible. Either expose both and validate per-provider, or map effort to budget with a stated table. Do not pretend one API. |
| Prompt caching | automatic on prefix | explicit `cache_control` breakpoints | No canonical representation means Anthropic users get *no caching*. See below — the biggest cost regression in the design. |
| Tool choice | `auto`, `none`, `required`, named | `auto`, `any`, `tool`, `none` | Nearly isomorphic. Easy win; just needs writing down. |
| Conversation state | `previous_response_id`, `store` | stateless; resend history | Ignoring this forces every OpenAI user onto the slow, expensive path. See below. |
| Structured output | `text.format` json_schema, strict mode | different mechanism and guarantees | Do not paper over the strictness difference — surface it through the capability model. |

Write this model now, in the abstract, and let it force those decisions while they are still cheap. If you write the OpenAI adapter first, the request model will quietly become "the OpenAI request with fields renamed," and the Anthropic adapter will spend its life apologising for that.

> ### The rule that saves this project
>
> **Never silently drop a parameter.** This is the single failure that kills unified-API libraries. A developer sets `thinking_budget=8000`, points at a non-reasoning model, gets a plausible answer, and never learns it was ignored.
>
> Pair the request model with a capability descriptor per provider and model, and make unsupported-feature behaviour an explicit, configurable policy — `raise` (default), `warn`, or `ignore` — surfaced on the response as a list of dropped features. This is a feature no native SDK can offer you, and it is a genuinely good reason to adopt a layer like this.

---

## Developer friendliness

Judged on the API surface visible in `rough/api.py` and `rough/tessaract-request.py`, the ergonomic instincts are good — `Tessaract({"oai": OpenAIProvider(...)})` with `model="oai/gpt-5.5"` is clean, and letting the alias be user-chosen rather than a fixed provider name is a nicer touch than most gateways manage. Specific friction points:

- **Two response accessors compete.** You have both `Response.output_text` (a concatenating property — good, matches what people reach for) and provider subclasses requiring `isinstance` narrowing. But `send()` is annotated to return `Response`, so a user cannot reach `previous_response_id` without an unchecked cast. Either make the client generic over the provider type, or expose narrowing accessors on the base (`response.as_openai()` returning `OpenAIResponse | None`) so the type checker can follow.

- **Content parts are too verbose for the common case.** If `Message(role, content: Iterable[ContentPart])` is the only constructor, the 80% case — a string — costs a wrapper. Accept `str | Sequence[ContentPart]` and normalise, and add `user()`, `assistant()`, and `system()` helpers. Compare the two-line hello-world in your own rough script against what a first-time reader would have to write today.

- **`Iterable` is the wrong type for `Message.content`.** It is a real footgun on a frozen object, because generators are single-use:

  ```pycon
  >>> m = Message(role="user", content=(p for p in parts))
  >>> list(m.content)   # [part1, part2]
  >>> list(m.content)   # [] — silently empty on retry
  ```

  A retry or a fallback to a second provider re-reads the message and sends nothing. Use `Sequence`, and coerce to `tuple` in a validator.

- **`role: str | Role` gives up the benefit of the enum.** Accept the string at the boundary and coerce to `Role` internally, so downstream code has one type to match on.

- **Streaming event names are inconsistent.** `"response_started"` uses an underscore while `"response.completed"`, `"text.delta"`, and `"tool_arguments.delta"` use dots. Anyone matching on `event.type` will get this wrong once. Pick dotted throughout.

- **`raw_event` is declared four different ways** across the six stream events — required on `ResponseStartedEvent` and `ResponseCompletedEvent`, optional elsewhere, `exclude=True` on five and serialized on `TextDeltaEvent`. Define one `RawCarrier` mixin and inherit it.

- **No async anywhere.** Both native SDKs offer async clients, and agent workloads are I/O-bound with parallel tool calls. Adding async after the fact means duplicating every adapter method. Define the provider Protocol with both from the start.

- **Missing stream events you already identified.** Your notes in `rough/streaming-rough-notes.txt` list `UsageUpdatedEvent`, `ProviderEvent`, and `AnnotationAddedEvent` as needed; none exist. Also missing: the `.done` counterparts (text, tool arguments, reasoning) and a signature-delta channel. The `ProviderEvent` catch-all matters most — without it, `ping`, `response.queued`, and every future event type has nowhere to go, and adapters will silently swallow them.

- **A high-level tool-call accumulator is the feature people will actually want.** Reassembling streamed `tool_arguments.delta` fragments into parsed arguments is fiddly and identical for every provider. Doing it once, well, in the canonical layer is a stronger selling point than the type unification itself.

---

## Native parity and performance

You asked specifically whether the abstraction costs you what you would get natively. I measured the part everyone assumes is the problem, and it is not.

| Constructing one stream delta event | µs/event | per 1k tokens |
|---|---:|---:|
| Your `TextDeltaEvent`, full validation | 1.38 | 1.4 ms |
| Equivalent `slots=True` frozen dataclass | 0.99 | 1.0 ms |
| `model_construct()` (validation skipped) | 3.50 | 3.5 ms |

**Do not micro-optimise the model layer.** Pydantic v2 validation costs 1.4× a slotted dataclass and about 1.4 ms across a thousand-token stream — noise beside a network round trip. Note the counterintuitive third row: `model_construct()` is *slower* than validating, because it runs in Python rather than in pydantic-core. Reaching for it as an optimisation would make things worse.

The real parity risks are all architectural, and all in the request path:

- **Prompt caching is the big one.** Anthropic's cache is driven by explicit `cache_control` breakpoints on content blocks. With no canonical representation for them, Anthropic users of Tessaract lose prompt caching entirely — a large cost increase and a large latency increase on exactly the long-system-prompt, many-tool agent workloads this library targets. It is not a rounding error; it is the difference between a viable and a non-viable gateway. The canonical model needs a cache-breakpoint concept (a marker on content parts and tool definitions) that OpenAI's adapter can safely ignore, since its caching is automatic.

- **Cache-key stability is a hidden requirement of your mapping code.** Both providers cache on exact prefix match. If your request mapper serializes with nondeterministic key ordering, or reorders tool definitions, or emits `null` fields inconsistently between calls, you will silently destroy hit rates. Make byte-stable serialization an explicit invariant with a test, not an accident of `model_dump`.

- **Server-side conversation state.** OpenAI's `previous_response_id` lets you send one turn instead of the whole history. A canonical model that only knows how to resend everything forces every OpenAI user onto more tokens and more latency than native — and the gap compounds over a long agent run. You expose `previous_response_id` read-only on `OpenAIResponse`; it needs a request-side counterpart, even if Anthropic's adapter emulates it by keeping history client-side.

- **Reasoning-block round-tripping is a correctness cliff, not a performance one.** Anthropic requires that thinking blocks be passed back unmodified — with their `signature` — on subsequent turns in a tool-use loop, and OpenAI reasoning items carry `encrypted_content` that must survive intact. You got the response side right by keeping both fields on `ReasoningOutputItem`. The danger is the return trip: if canonical → provider mapping regenerates these blocks instead of echoing them verbatim, multi-turn reasoning with tools breaks, and it breaks in a way that looks like a model quality problem rather than a serialization bug. Note that `ReasoningDeltaEvent` currently has no channel for signature deltas or redacted thinking, so a streamed reasoning turn cannot be reassembled into a valid follow-up request.

- **Connection reuse.** Instantiate one long-lived provider client per config and share it. `OpenAIAdapter.__init__` currently builds a fresh client, and `Tessaract.send` constructs a fresh adapter on every call — that discards the connection pool and adds a TLS handshake per request, which will dwarf everything else in this section.

The overall shape of the answer: a well-built layer here costs essentially nothing in CPU and nothing in fidelity *as long as* the escape hatches are real and the request model is expressive enough that nobody needs to reach past it. Your `raw_response` and `provider_metadata` decisions mean the response side already passes that test. The request side has not been designed yet, and that is where parity is won or lost.

---

## What I would do before writing a single adapter

1. **Make the package import, and keep it that way.** Break the `responses` ↔ `output_types` cycle with a dependency-free `types.py`, de-duplicate `FinishDetails` and `ResponseTelemetry`, fix `models.py`. Then add the most boring test in the world — `import tessaract` — and a CI job that runs it. Every defect in the blocking section above would have been caught by that one test.

2. **Commit to Pydantic everywhere.** Convert the dataclass content parts and messages. This fixes the inert-annotation bugs and the `FunctionTool` inheritance problem at the same time, and gives you discriminated unions with `Field(discriminator=...)` for free — which is what the action unions want.

3. **Write the canonical `Request` model.** Before any adapter. Force the seven decisions in the table above and write down each answer as a comment where the field lives. This is the artifact that determines whether Tessaract is a real abstraction or a renaming layer.

4. **Add the capability descriptor and the unsupported-feature policy.** Small, and it is the thing that makes the abstraction trustworthy rather than lossy.

5. **Define the provider Port as a Protocol, sync and async.** Four methods is plenty: `generate`, `stream`, and their async twins. Then fill in `tests/fake_provider.py` against it. A fake provider written before the real ones is what stops OpenAI's shape leaking into the contract.

6. **Rebuild the tool layer canonical-shape-first.** Move everything with a provider name in it out of `canonical/` into `providers/<name>/`, and split definitions from calls from results. Enforce the boundary with a test that greps `canonical/` for provider names — a cheap guard that keeps holding as the project grows.

7. **Write the round-trip contract test, then the adapters.** This is the test that matters most, and it should exist before the adapters do:

   ```
   canonical Request
     → provider payload → provider Response
     → canonical Response
     → appended to history → canonical Request
     → provider payload
   ```

   Assert the second payload is byte-identical in its overlapping prefix, and that Anthropic thinking signatures and OpenAI reasoning IDs survive verbatim. Run it against the fake provider and against recorded fixtures from the real ones — you already have the raw payloads captured in `rough/` and at the repo root, which is a good habit and exactly what this test needs. Any agent loop that runs more than one turn depends on this invariant, and nothing else you can write will catch its violation.

---

## Housekeeping

- Root `__init__.py` does `from .main import Tessaract`; there is no `main.py`. The `tessaract/` package is empty while the real code sits in top-level `canonical/`, `adapters/`, and loose `client.py` / `models.py` / `hello.py`. Move everything under `src/tessaract/` and let the layout match the architecture diagram you already drew.
- `rough/` is in `.gitignore` but 16 of its files are tracked — the ignore was added after they were committed, so it has no effect. Either `git rm --cached` them or drop the ignore rule; right now the intent and the reality disagree. `.DS_Store` is also tracked. (`.env` is correctly untracked — good.)
- `README.md` is empty and `pyproject.toml` still says "Add your description here". For a library whose entire pitch is developer friendliness, the README is a functional component. Even now, the two-provider hello-world from `rough/api.py` plus the honest capability table would do real work.
- No LICENSE, no CI, no tests. The license especially — nobody adopts an unlicensed gateway.
- The project is spelled *tessaract*; the English word is *tesseract*. Worth deciding deliberately now rather than after a PyPI name and a docs site exist, since the near-miss spelling will cost you search traffic and get typo'd in every install command.

---

*Findings reproduced against the working tree at `6157b01` with Python 3.13 / Pydantic 2.13. No source files were modified.*
