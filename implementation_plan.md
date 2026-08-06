

### Phase 1: Canonical core

Message and content types

Tool definitions and calls

Generation request

Generation response

Streaming events

Usage

Error hierarchy

Provider interface

Fake provider


Deliverable: the domain model and contract tests compile and make sense.

### Phase 2: First two providers

OpenAI adapter

Anthropic adapter

Text generation

Streaming

Tool calling

Usage mapping

Error mapping

Timeouts


Deliverable: one demonstration agent works unchanged against both providers.


### Phase 3: Third provider and abstraction correction

Add Gemini

Deliverable: the third provider does not require provider conditionals in gateway services.

### Phase 4: Reliability

Retry policies

Backoff and jitter

Fallback classification

Stream timeout

Request identifiers

Observability hooks

Exact request caching

Pricing metadata

Deliverable: fault-injection test suite.

### Phase 5: Adoption interface

Python client

OpenAI-compatible HTTP server

Configuration file

Docker image

Examples

Migration guides

Provider capability table

Deliverable: an existing small OpenAI-based application can point to your gateway with minimal changes.

### Phase 6: Ecosystem integration

Model Context Protocol tool conversion

OpenTelemetry integration

Batch requests

Replay testing

Community provider plugin interface

TypeScript client

### Optional: Advanced routing

Model aliases
Weighted routing
Cost-aware routing
Latency-aware routing
Circuit breakers
Health scoring
Budget limits

A circuit breaker temporarily stops sending requests to a repeatedly failing provider, allowing it time to recover.


CODE ARCHITECTURE

gateway/
  canonical/
    messages.py
    input_types
    output_types
    tools.py
    responses.py
    streaming.py *
    model_capabilities

  providers/
    base.py
    openai/
      adapter.py
      request_mapper.py
      response_mapper.py
      stream_mapper.py
      errors.py
    anthropic/
    google/

  reliability/
    retry.py
    timeout.py
    circuit_breaker.py

  pricing/
    catalog.py
    calculator.py

  observability/
    hooks.py
    logging.py
    tracing.py

  validation/
    capabilities.py
    schemas.py
    requests.py

PROJECT ARCHITECTURE
┌─────────────────────────────────────────────────┐
│ Public clients                                 │
│ Python library / HTTP server / command line     │
├─────────────────────────────────────────────────┤
│ Application services                           │
│ Generation, routing, fallback, retries          │
├─────────────────────────────────────────────────┤
│ Canonical domain model                         │
│ Requests, messages, content, tools, responses   │
├─────────────────────────────────────────────────┤
│ Provider ports                                 │
│ Provider interface contracts                    │
├─────────────────────────────────────────────────┤
│ Provider adapters                              │
│ OpenAI / Anthropic / Gemini                     │
├─────────────────────────────────────────────────┤
│ Infrastructure                                 │
│ HTTP transport, telemetry, cache, credentials   │
└─────────────────────────────────────────────────┘