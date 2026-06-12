"""The Argus LangGraph: plan (model) -> act (tools) -> synthesize.

The model node binds the shared tool layer and decides whether to call tools.
The tools node executes each requested tool against the canonical functions,
accumulating artifacts and citations into state. The loop ends when the model
returns a final answer with no further tool calls.
"""

from __future__ import annotations

import json

from langchain_core.messages import ToolMessage
from langgraph.graph import END, StateGraph

from .state import AgentState
from .tools import as_langchain_tools, get_spec


def _compact(result: dict) -> dict:
    """Trim bulky fields before handing a tool result back to the model."""
    return {k: v for k, v in result.items() if k != "artifacts"}


def build_graph(model):
    """Compile the agent graph around a bound chat model."""
    bound = model.bind_tools(as_langchain_tools())

    def call_model(state: AgentState) -> dict:
        return {"messages": [bound.invoke(state["messages"])]}

    def run_tools(state: AgentState) -> dict:
        last = state["messages"][-1]
        messages, artifacts, citations = [], [], []
        for call in last.tool_calls:
            spec = get_spec(call["name"])
            result = spec.fn(**call["args"])
            artifacts.extend(result.get("artifacts", []))
            citations.extend(result.get("citations", []))
            messages.append(
                ToolMessage(
                    content=json.dumps(_compact(result)),
                    tool_call_id=call["id"],
                    name=call["name"],
                )
            )
        return {"messages": messages, "artifacts": artifacts, "citations": citations}

    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        return "tools" if getattr(last, "tool_calls", None) else END

    graph = StateGraph(AgentState)
    graph.add_node("model", call_model)
    graph.add_node("tools", run_tools)
    graph.set_entry_point("model")
    graph.add_conditional_edges("model", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "model")
    return graph.compile()
