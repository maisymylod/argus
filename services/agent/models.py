"""Pluggable chat model: real Claude when ANTHROPIC_API_KEY is set, otherwise a
deterministic scripted driver so the orchestration runs offline and in CI.

Both implementations satisfy the minimal interface the graph needs:
  - bind_tools(tools) -> model
  - invoke(messages) -> AIMessage
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable

from langchain_core.messages import AIMessage, ToolMessage

SYSTEM_PROMPT = (
    "You are Argus, an earth-observation analyst. Use the available tools to "
    "inspect public satellite imagery and the knowledge base, then answer the "
    "user concisely. Always ground claims in tool results and cite the source "
    "scene ids and knowledge-base passages you used."
)


class ScriptedModel:
    """Drives a fixed sequence of tool calls, then synthesizes a grounded answer.

    Used when no API key is present. It proves the full graph path (plan, call
    tools over the shared tool layer, collect artifacts and citations,
    synthesize) without any network or model dependency.
    """

    def __init__(self, planned_calls: list[dict], answer_fn: Callable[[list[dict]], str]):
        self._planned = planned_calls
        self._answer_fn = answer_fn

    def bind_tools(self, tools) -> ScriptedModel:  # noqa: ARG002 - tools unused by the script
        return self

    def invoke(self, messages) -> AIMessage:
        issued = sum(1 for m in messages if isinstance(m, AIMessage) and m.tool_calls)
        if issued < len(self._planned):
            call = self._planned[issued]
            return AIMessage(
                content="",
                tool_calls=[{"name": call["name"], "args": call["args"], "id": f"call_{issued}"}],
            )
        results = [json.loads(m.content) for m in messages if isinstance(m, ToolMessage)]
        return AIMessage(content=self._answer_fn(results))


def get_model(planned_calls: list[dict] | None = None, answer_fn=None):
    """Return ChatAnthropic if an API key is configured, else a ScriptedModel."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        from langchain_anthropic import ChatAnthropic

        model_id = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        return ChatAnthropic(model=model_id, temperature=0, max_tokens=1024)

    if planned_calls is None or answer_fn is None:
        raise RuntimeError(
            "No ANTHROPIC_API_KEY set. Provide planned_calls and answer_fn for the scripted model."
        )
    return ScriptedModel(planned_calls, answer_fn)
