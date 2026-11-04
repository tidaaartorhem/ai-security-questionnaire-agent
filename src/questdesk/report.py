"""Headline findings computed from a pipeline run. Numbers are measured,
not invented."""
import json
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"


def findings(state: dict) -> dict:
    matches = state["matches"]
    cfg = state["config"]
    by_q = {q["id"]: q for q in state["questions"]}
    routes = Counter(m["route"] for m in matches)
    flags = Counter(f for m in matches for f in m["flags"])

    per_domain: dict[str, dict] = {}
    for m in matches:
        d = by_q[m["question_id"]]["domain"]
        per_domain.setdefault(d, Counter())[m["route"]] += 1
    domain_table = {
        d: {
            "total": sum(c.values()),
            "ready": c.get("READY", 0),
            "review": c.get("REVIEW", 0),
            "reverify": c.get("REVERIFY", 0),
            "new": c.get("NEW", 0),
            "coverage_pct": round(100 * (sum(c.values()) - c.get("NEW", 0)) / sum(c.values()), 1),
        }
        for d, c in sorted(per_domain.items())
    }

    effort = cfg["effort_minutes"]
    total_minutes = sum(effort[m["route"]] for m in matches)
    scores = [m["score"] for m in matches if m["answer_id"]]
    mean_conf = round(sum(scores) / len(scores), 1) if scores else 0.0

    owners = Counter()
    for m in matches:
        if m["route"] in ("REVIEW", "REVERIFY", "NEW") and m.get("draft", {}).get("owner"):
            owners[m["draft"]["owner"]] += 1

    return {
        "question_count": len(matches),
        "routes": dict(routes),
        "ready_pct": round(100 * routes.get("READY", 0) / len(matches), 1),
        "flags": dict(flags),
        "mean_match_confidence": mean_conf,
        "domain_table": domain_table,
        "worst_domains": sorted(domain_table.items(), key=lambda kv: kv[1]["coverage_pct"])[:3],
        "effort_minutes": total_minutes,
        "effort_hours": round(total_minutes / 60, 1),
        "sme_queue_owners": dict(owners.most_common(6)),
    }


def main() -> None:
    from .graph import run

    prev = json.loads((DATA_DIR / "previous_round.json").read_text())["previous"]
    state = run(previous_round=prev)
    f = findings(state)
    out = DATA_DIR.parent / "outputs" / "findings.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"findings": f, "export_pack": state["export_pack"]}, indent=1))
    r = f["routes"]
    print(
        f"{f['question_count']} questions -> READY {r.get('READY',0)} | REVIEW {r.get('REVIEW',0)} | "
        f"REVERIFY {r.get('REVERIFY',0)} | NEW {r.get('NEW',0)} | "
        f"effort {f['effort_hours']}h | mean confidence {f['mean_match_confidence']}"
    )
    print("worst coverage:", [(d, t["coverage_pct"]) for d, t in f["worst_domains"]])


if __name__ == "__main__":
    main()
