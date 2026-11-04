"""QuestDesk pipeline tests. All deterministic; no network, no LLM."""
import json
from pathlib import Path

import pytest

from questdesk import graph, matcher, report, text
from questdesk.text import bigrams, jaccard, token_set, tokens

DATA = Path(__file__).resolve().parent.parent / "data" / "raw"


@pytest.fixture(scope="module")
def cfg():
    return matcher.load_config()


@pytest.fixture(scope="module")
def lib():
    return matcher.load_library()


@pytest.fixture(scope="module")
def bank():
    return matcher.load_bank()


@pytest.fixture(scope="module")
def full_state():
    prev = json.loads((DATA / "previous_round.json").read_text())["previous"]
    return graph.run(previous_round=prev)


# ------------------------------------------------------------- text utils

def test_tokens_strip_stopwords_and_case():
    assert tokens("Are audit and Assurance POLICIES?") == ["audit", "assurance", "policies"]


def test_bigrams_and_jaccard():
    assert bigrams("alpha beta gamma") == {("alpha", "beta"), ("beta", "gamma")}
    assert jaccard({1, 2}, {2, 3}) == pytest.approx(1 / 3)
    assert jaccard(set(), set()) == 1.0
    assert jaccard({1}, set()) == 0.0


# -------------------------------------------------------------- data shape

def test_question_bank_is_real_caiq(bank):
    assert len(bank["questions"]) == 261
    ids = [q["id"] for q in bank["questions"]]
    assert len(set(ids)) == 261
    assert sum(1 for q in bank["questions"] if q["domain"] == "CEK") == 23


def test_library_labels_fictional(lib):
    assert lib["company"]["fictional"] is True
    assert len(lib["answers"]) == 99
    assert len(lib["evidence"]) == 28
    for a in lib["answers"]:
        assert a["response"] in ("Yes", "No")
        assert a["domains"] and a["text"] and a["owner"]


def test_config_thresholds(cfg):
    assert cfg["thresholds"]["min_match"] == 35
    assert cfg["thresholds"]["auto_ready"] == 60
    assert cfg["freshness"]["answer_stale_after_days"] == 180


# --------------------------------------------------------------- pipeline

def test_intake_loads_everything():
    s = graph.node_intake({"previous_round": {}})
    assert len(s["questions"]) == 261
    assert len(s["answers"]) == 99
    assert len(s["evidence"]) == 28


def test_match_covers_all_questions(full_state):
    assert len(full_state["matches"]) == 261
    routes = {m["route"] for m in full_state["matches"]}
    assert routes == {"READY", "REVIEW", "REVERIFY", "NEW"}


def test_route_distribution_sums(full_state):
    assert sum(1 for _ in full_state["matches"]) == 261


def test_gate_marks_everything_pending(full_state):
    pack = full_state["export_pack"]
    assert len(pack) == 261
    assert all(p["pending_approval"] for p in pack)
    assert all("action" in p["draft"] for p in pack)


def test_stale_answer_routes_to_reverify(full_state):
    # HL-AA-01 was last reviewed 2026-03-10 (>180d before replay) but matches
    # strongly, so its questions must route REVERIFY, never READY.
    by_q = {m["question_id"]: m for m in full_state["matches"]}
    m = by_q["A&A-01.2"]
    assert m["answer_id"] == "HL-AA-01"
    assert m["route"] == "REVERIFY"
    assert "STALE_ANSWER" in m["flags"]


def test_unmatched_question_routes_new(full_state):
    by_q = {m["question_id"]: m for m in full_state["matches"]}
    m = by_q["UEM-12.1"]  # geolocation: no seeded answer covers it
    assert m["route"] == "NEW"
    assert m["answer_id"] is None


def test_wording_change_forces_review(full_state):
    by_q = {m["question_id"]: m for m in full_state["matches"]}
    flagged = [qid for qid, m in by_q.items() if "WORDING_CHANGED" in m["flags"]]
    assert len(flagged) >= 2
    for qid in flagged:
        assert by_q[qid]["route"] in ("REVIEW", "REVERIFY", "NEW")


def test_stale_evidence_detected():
    # synthetic: answer citing a 2024 artifact must flag STALE_EVIDENCE
    state = {
        "config": matcher.load_config(),
        "evidence": {"EV-OLD": {"id": "EV-OLD", "issued": "2024-01-01"}},
        "questions": [{"id": "Q-1", "domain": "LOG", "question": "logging policy question"}],
        "matches": [{
            "question_id": "Q-1", "answer_id": "A-1", "score": 80.0,
            "best_answer": {"id": "A-1", "last_reviewed": "2026-10-01", "evidence": ["EV-OLD"]},
            "flags": [],
        }],
        "previous_round": {},
    }
    out = graph.node_freshness(state)
    assert "STALE_EVIDENCE" in out["matches"][0]["flags"]


def test_known_strong_match_scores_high(cfg, lib):
    bank = {q["id"]: q for q in matcher.load_bank()["questions"]}
    answers = {a["id"]: a for a in lib["answers"]}
    q = bank["LOG-06.1"]  # time source question
    s = matcher.score_pair(q["question"], q["domain"], answers["HL-LOG-04"], cfg)
    assert s["score"] >= cfg["thresholds"]["auto_ready"]
    assert s["parts"]["domain_boost"] == 15


# ----------------------------------------------------------------- report

def test_findings_structure(full_state):
    f = report.findings(full_state)
    assert f["question_count"] == 261
    assert sum(f["routes"].values()) == 261
    assert f["effort_hours"] > 0
    assert len(f["domain_table"]) == 17
    for d, t in f["domain_table"].items():
        assert t["total"] == t["ready"] + t["review"] + t["reverify"] + t["new"]
