"""QuestDesk — the security-questionnaire response desk.

A deterministic LangGraph pipeline that answers an incoming 261-question
CSA CAIQ v4.0.2 vendor security questionnaire from a seeded approved-answer
library: intake -> match -> freshness -> route -> draft -> gate.
Zero LLM calls. Every response is human-gated before export.
"""
from .graph import build_graph, run

__all__ = ["build_graph", "run"]
