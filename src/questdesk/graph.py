"""QuestDesk LangGraph pipeline.

StateGraph: intake -> match -> freshness -> route -> draft -> gate

- intake:      load the 261-question CAIQ round + the approved answer library.
- match:       score every question against every answer (261 x 99 pairs),
               keep the best match above min_match.
- freshness:   flag stale answers (>180d since last_reviewed), stale linked
               evidence (>365d), and wording changes vs the previous round.
- route:       READY (>=75, fresh) / REVIEW (50-74 or wording changed) /
               REVERIFY (strong match but stale answer) / NEW (<50).
- draft:       assemble the draft response from the approved answer + evidence
               refs; NEW questions get an SME drafting brief instead.
- gate:        every response requires human approval before export;
               nothing is marked final automatically.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from .matcher import load_bank, load_config, load_library, match_question
from .text import jaccard, token_set

REPLAY_DATE = date(2026, 11, 4)


def _days_between(iso: str) -> int:
    return (REPLAY_DATE - date.fromisoformat(iso)).days


# ------------------------------------------------------------------ nodes

def node_intake(state: dict) -> dict:
    bank = load_bank()
    lib = load_library()
    cfg = load_config()
    prev = state.get("previous_round", {})
    return {
        **state,
        "questions": bank["questions"],
        "answers": lib["answers"],
        "evidence": {e["id"]: e for e in lib["evidence"]},
        "config": cfg,
        "previous_round": prev,
    }


def node_match(state: dict) -> dict:
    cfg, questions, answers = state["config"], state["questions"], state["answers"]
    return {**state, "matches": [match_question(q, answers, cfg) for q in questions]}


def node_freshness(state: dict) -> dict:
    cfg = state["config"]
    stale_after = cfg["freshness"]["answer_stale_after_days"]
    ev_stale_after = cfg["freshness"]["evidence_stale_after_days"]
    word_thr = cfg["freshness"]["wording_change_jaccard_below"]
    cutoff = (REPLAY_DATE.toordinal() - stale_after)
    ev_cutoff = REPLAY_DATE.toordinal() - ev_stale_after

    enriched = []
    for m in state["matches"]:
        ans = m["best_answer"]
        flags: list[str] = []
        if ans is None:
            enriched.append({**m, "flags": flags})
            continue
        if date.fromisoformat(ans["last_reviewed"]).toordinal() < cutoff:
            flags.append("STALE_ANSWER")
        stale_ev = [
            eid for eid in ans.get("evidence", [])
            if eid in state["evidence"]
            and date.fromisoformat(state["evidence"][eid]["issued"]).toordinal() < ev_cutoff
        ]
        if stale_ev:
            flags.append("STALE_EVIDENCE")
            m = {**m, "stale_evidence": stale_ev}
        prev_text = state["previous_round"].get(m["question_id"])
        if prev_text:
            sim = jaccard(token_set(prev_text), token_set(next(
                q["question"] for q in state["questions"] if q["id"] == m["question_id"])))
            m = {**m, "wording_similarity": round(sim, 3)}
            if sim < word_thr:
                flags.append("WORDING_CHANGED")
        enriched.append({**m, "flags": flags})
    return {**state, "matches": enriched}


def node_route(state: dict) -> dict:
    th = state["config"]["thresholds"]
    routed = []
    for m in state["matches"]:
        if m["answer_id"] is None:
            route = "NEW"
        elif "STALE_ANSWER" in m["flags"] or "STALE_EVIDENCE" in m["flags"]:
            route = "REVERIFY"
        elif m["score"] >= th["auto_ready"] and "WORDING_CHANGED" not in m["flags"]:
            route = "READY"
        else:
            route = "REVIEW"
        routed.append({**m, "route": route})
    return {**state, "matches": routed}


def node_draft(state: dict) -> dict:
    by_answer = {a["id"]: a for a in state["answers"]}
    by_question = {q["id"]: q for q in state["questions"]}
    drafts = []
    for m in state["matches"]:
        q = by_question[m["question_id"]]
        if m["route"] == "NEW":
            drafts.append({
                **m,
                "draft": {
                    "response": None,
                    "text": "No approved answer covers this question. SME drafting brief: answer from first principles, "
                            "cite the control owner, and attach fresh evidence before this response can be approved.",
                    "evidence": [],
                    "action": "Draft a new approved answer with the control owner, then re-run the matcher.",
                },
            })
            continue
        ans = by_answer[m["answer_id"]]
        drafts.append({
            **m,
            "draft": {
                "response": ans["response"],
                "text": ans["text"],
                "evidence": ans.get("evidence", []),
                "owner": ans["owner"],
                "owner_title": ans["owner_title"],
                "last_reviewed": ans["last_reviewed"],
                "action": _action_for(m),
            },
        })
    return {**state, "matches": drafts}


def _action_for(m: dict) -> str:
    if m["route"] == "READY":
        return "Approve and export as-is."
    if m["route"] == "REVERIFY":
        reasons = []
        if "STALE_ANSWER" in m["flags"]:
            reasons.append("answer is past its 180-day review date")
        if "STALE_EVIDENCE" in m["flags"]:
            reasons.append(f"linked evidence is stale: {', '.join(m.get('stale_evidence', []))}")
        return "Re-verify with the control owner (" + "; ".join(reasons) + "), then approve."
    if "WORDING_CHANGED" in m["flags"]:
        return "Question wording changed since the last round — confirm the approved answer still applies, then approve."
    return f"SME review: confirm the matched answer (score {m['score']}, margin {m['margin']}) fits, then approve."


def node_gate(state: dict) -> dict:
    # Human gate: nothing is final until approved. The export pack marks
    # every item pending_approval=True.
    pack = [
        {
            "question_id": m["question_id"],
            "route": m["route"],
            "flags": m["flags"],
            "answer_id": m["answer_id"],
            "score": m["score"],
            "draft": m["draft"],
            "pending_approval": True,
        }
        for m in state["matches"]
    ]
    return {**state, "export_pack": pack}


NODES = [node_intake, node_match, node_freshness, node_route, node_draft, node_gate]


# ------------------------------------------------- LangGraph / fallback

def build_graph():
    """Return a compiled LangGraph StateGraph; fall back to a sequential
    runner when langgraph is not installed (same node order, same state)."""
    try:
        from langgraph.graph import StateGraph  # type: ignore

        g: Any = StateGraph(dict)
        prev = None
        for i, fn in enumerate(NODES):
            name = fn.__name__.replace("node_", "")
            g.add_node(name, fn)
            if prev:
                g.add_edge(prev, name)
            else:
                g.set_entry_point(name)
            prev = name
        g.add_edge(prev, "__end__")
        return g.compile()
    except ImportError:
        return None


def run(previous_round: dict | None = None) -> dict:
    graph = build_graph()
    initial = {"previous_round": previous_round or {}}
    if graph is not None:
        return graph.invoke(initial)
    state = dict(initial)
    for fn in NODES:
        state = fn(state)
    return state
