#!/usr/bin/env python3
"""Build script: runs the QuestDesk pipeline and assembles the web payload.

Writes web/public/data/*.json:
  summary.json  - headline findings + golden-set eval + scoring disclosure
  matches.json  - per-question export pack (route, flags, draft, evidence)
  library.json  - approved answers + evidence artifacts with staleness flags
  test-vectors.json - shared Python/TS matcher contract
Exits non-zero if the pipeline produced no matches.
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB_DATA = ROOT / "web" / "public" / "data"
RAW = ROOT / "data" / "raw"


def fail(msg: str) -> None:
    print(f"build_web: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from questdesk import eval as quest_eval
    from questdesk.graph import run
    from questdesk.report import findings

    prev = json.loads((RAW / "previous_round.json").read_text())["previous"]
    state = run(previous_round=prev)
    if not state["matches"]:
        fail("pipeline produced no matches")

    f = findings(state)
    ev = quest_eval.evaluate(state["config"])
    lib = json.loads((RAW / "answer_library.json").read_text())

    replay = date(2026, 11, 4)
    stale_ev_after = state["config"]["freshness"]["evidence_stale_after_days"]
    evidence = []
    for e in lib["evidence"]:
        age = (replay - date.fromisoformat(e["issued"])).days
        evidence.append({**e, "age_days": age, "stale": age > stale_ev_after})

    stale_after = state["config"]["freshness"]["answer_stale_after_days"]
    answers = []
    for a in lib["answers"]:
        age = (replay - date.fromisoformat(a["last_reviewed"])).days
        answers.append({**a, "age_days": age, "stale": age > stale_after})

    by_q = {q["id"]: q for q in state["questions"]}
    matches = [
        {
            "question_id": m["question_id"],
            "question": by_q[m["question_id"]]["question"],
            "domain": by_q[m["question_id"]]["domain"],
            "domain_name": by_q[m["question_id"]]["domain_name"],
            "route": m["route"],
            "flags": m["flags"],
            "answer_id": m["answer_id"],
            "score": m["score"],
            "score_parts": m["score_parts"],
            "margin": m["margin"],
            "draft": m["draft"],
            "pending_approval": True,
        }
        for m in state["matches"]
    ]

    WEB_DATA.mkdir(parents=True, exist_ok=True)
    (WEB_DATA / "summary.json").write_text(json.dumps({
        "findings": f,
        "eval": {k: v for k, v in ev.items() if k != "misses"},
        "eval_misses": ev["misses"],
        "config": state["config"],
        "company": lib["company"],
        "data_note": ("Questions: real CSA CAIQ v4.0.2 question bank (261 questions, 17 domains). "
                      "Answers and evidence describe the FICTIONAL Harbourline Analytics Inc. and are seeded demo data."),
    }, indent=1))
    (WEB_DATA / "matches.json").write_text(json.dumps(matches, indent=1))
    (WEB_DATA / "library.json").write_text(json.dumps({"answers": answers, "evidence": evidence}, indent=1))
    shutil.copy(RAW / "test-vectors.json", WEB_DATA / "test-vectors.json")
    print(f"build_web: {len(matches)} matches, {len(answers)} answers, {len(evidence)} evidence -> {WEB_DATA}")


if __name__ == "__main__":
    main()
