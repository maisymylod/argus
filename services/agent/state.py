"""LangGraph state for the Argus agent."""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    artifacts: Annotated[list[dict], operator.add]
    citations: Annotated[list[dict], operator.add]
