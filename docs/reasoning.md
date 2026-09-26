# Reasoning

Reasoning models think before they answer. Tessaract lets you control that reasoning with `ReasoningOptions` and read it back as `ReasoningOutputItem`s, in both non-streaming and streaming responses.

```python
from tessaract import ReasoningOptions
```

## Requesting reasoning

```python
response = client.send(
    model="oai/gpt-5.6-luna",
    input="How many r's are in 'strawberry'? Explain.",
    reasoning=ReasoningOptions(effort="high", summary="detailed"),
)
```

If you leave out `reasoning`, Tessaract doesn't send a `reasoning` parameter, and the model uses its default.

### `ReasoningOptions`

| Field | Values | Description |
| --- | --- | --- |
| `effort` | `"none"`, `"minimal"`, `"low"`, `"medium"`, `"high"`, `"extra_high"`, `"max"` | How much the model thinks. Higher values are slower and use more tokens, and handle harder problems better. |
| `summary` | `"auto"`, `"concise"`, `"detailed"` | Asks for a readable summary of the reasoning. Leave it out and you get no summary text. |
| `mode` | `"standard"`, `"pro"` | The reasoning mode, on models that support it. |

Every field is optional. Only the fields you set are sent.

### How the fields map to OpenAI

| Canonical | OpenAI `reasoning` parameter |
| --- | --- |
| `effort="extra_high"` | `effort="xhigh"` |
| any other `effort` | sent unchanged |
| `summary` | `summary` |
| `mode` | `mode` |

Support for each effort level and mode depends on the model. The API returns an error if a model doesn't support a value.

### Choosing an effort

| Use case | Suggested effort |
| --- | --- |
| Chat, simple tool routing, extraction | `"none"`, `"minimal"` or `"low"` |
| A general agent that plans multi-step tool use | `"medium"` |
| Hard math, code, or long-horizon planning | `"high"`, `"extra_high"` or `"max"` |

## Reading reasoning output

Reasoning comes back as `ReasoningOutputItem`s in `response.output`, usually before the message or function calls that follow from it:

```python
for item in response.output:
    if item.type == "reasoning":
        print("id:      ", item.id)
        print("summary: ", item.text)     # summary text (requires `summary=`)
        print("content: ", item.content)  # raw reasoning text, if the model exposes it
```

| Field | Description |
| --- | --- |
| `id` | The provider's reasoning item ID |
| `text` | All the reasoning **summary** parts joined together. It's an empty string if you didn't ask for a summary. |
| `content` | All the raw reasoning **content** parts joined together. It's often empty, because many OpenAI models don't expose raw reasoning. |
| `raw` | The native OpenAI `ResponseReasoningItem` |

> `response.output_text` includes only assistant message text. Reasoning is never mixed into it.

## Keeping reasoning across turns

Keep the reasoning items in your history. Append **all** of `response.output`:

```python
history.extend(response.output)
```

This matters most in tool-calling agents. When a model reasons, calls a tool and then gets the result, the earlier reasoning item lets it continue its thought instead of starting over. Tessaract replays each item from its native `raw` form, so nothing is lost.

### Stateless / ZDR usage

By default OpenAI stores responses, and reasoning items are looked up by ID. If you turn storage off, ask OpenAI to return encrypted reasoning so it can travel in your history:

```python
client.send(
    model="oai/gpt-5.6-luna",
    input=history,
    reasoning=ReasoningOptions(effort="medium", summary="auto"),
    request_options={
        "store": False,
        "include": ["reasoning.encrypted_content"],
    },
)
```

## Streaming reasoning

With `stream=True`, reasoning arrives as events:

| Event `type` | When | Useful fields |
| --- | --- | --- |
| `reasoning.started` | A new reasoning summary part begins | `item_id` |
| `reasoning_summary.delta` | A chunk of the reasoning summary | `delta`, `item_id`, `output_index` |
| `reasoning_text.delta` | A chunk of raw reasoning text, on models that expose it | `delta`, `item_id`, `output_index` |
| `output_item.done` | The complete reasoning item | `item` (a `ReasoningOutputItem`) |

```python
for event in client.send(model=..., input=..., reasoning=ReasoningOptions(effort="medium", summary="auto"), stream=True):
    if event.type == "reasoning.started":
        print("\n[thinking] ", end="")
    elif event.type == "reasoning_summary.delta":
        print(event.delta, end="", flush=True)
    elif event.type == "text.delta":
        print(event.delta, end="", flush=True)
```

`reasoning.started` fires once per summary part, so a long reasoning summary can start more than once.

See [Streaming](streaming.md) for the full event list.
