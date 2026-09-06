"""Inspect the adapter's actual SDK request serialization without network calls.

Run from the repository root: .venv/bin/python inspect_reasoning.py

The real Tessaract client, adapter, and OpenAI SDK run normally. MockTransport
replaces only HTTP delivery, capturing the serialized body and returning a fake
API response. This verifies serialization, not whether OpenAI accepts a setting.
"""

import json
from typing import Any

import httpx
import openai

from src.client import Tessaract
from src.providers.openai_provider import OpenAIProvider
from src.types.request import ReasoningOptions


def main() -> None:
    captured: list[dict[str, Any]] = []

    def handle_request(request: httpx.Request) -> httpx.Response:
        # This is the body AFTER the installed SDK has serialized the request.
        # Reading it here checks more than mocking responses.create() would.
        assert request.method == "POST"
        assert request.url.path == "/v1/responses"
        body = json.loads(request.content)
        captured.append(body)

        # The SDK parses this JSON into its real response model classes.
        return httpx.Response(
            200,
            json={
                "id": "resp_mock",
                "object": "response",
                "created_at": 0,
                "status": "completed",
                "model": body["model"],
                "parallel_tool_calls": True,
                "tool_choice": "auto",
                "tools": [],
                "output": [
                    {
                        "id": "rs_mock",
                        "type": "reasoning",
                        "summary": [
                            {"type": "summary_text", "text": "Mock reasoning summary."}
                        ],
                    },
                    {
                        "id": "msg_mock",
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [
                            {
                                "type": "output_text",
                                "text": "Mock answer.",
                                "annotations": [],
                            }
                        ],
                    },
                ],
            },
        )

    # Every HTTP request is handled in memory; no API credentials are loaded.
    with httpx.Client(
        transport=httpx.MockTransport(handle_request), trust_env=False
    ) as http_client:
        provider = OpenAIProvider(
            api_key="mock-key-no-network",
            provider_args={
                "http_client": http_client,
                "base_url": "https://openai.mock.invalid/v1",
                "max_retries": 0,
            },
        )
        client = Tessaract({"oai": provider})
        response = client.send(
            model="oai/gpt-5.6-luna",
            input=["Hello"],
            reasoning=ReasoningOptions(
                effort="high", summary="detailed", mode="pro"
            ),
        )

        assert len(captured) == 1
        assert captured[0]["reasoning"] == {
            "effort": "high", "summary": "detailed", "mode": "pro"
        }
        assert response is not None
        assert response.output_text == "Mock answer."

        print(f"Installed OpenAI SDK: {openai.__version__}")
        print("\nSerialized request JSON:")
        print(json.dumps(captured[0], indent=2))
        print("\nRaw SDK summary:", response.raw_response.output[0].summary[0].text)
        print("Adapter's response.reasoning:", repr(response.reasoning))

        # Observe defaults and translations without asserting that bugs should
        # persist. Rerunning after a fix will show the changed outgoing values.
        print("\nOther configurations -> serialized reasoning:")
        for label, options in [
            ("no config", None),
            ("empty config", ReasoningOptions()),
            ("summary only", ReasoningOptions(summary="detailed")),
            ("mode only", ReasoningOptions(mode="pro")),
            ("extra_high", ReasoningOptions(effort="extra_high")),
        ]:
            client.send(model="oai/gpt-5.6-luna", input=["Hello"], reasoning=options)
            print(f"{label}: {json.dumps(captured[-1].get('reasoning'))}")

        print(f"\nCaptured {len(captured)} requests in memory. No network calls made.")


if __name__ == "__main__":
    main()
