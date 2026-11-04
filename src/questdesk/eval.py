"""Golden-set evaluation + threshold calibration for the matcher.

Metrics (all on the 41 hand-labeled pairs in data/raw/golden_set.json):
  - routing accuracy: fraction where the matcher picks the labeled answer,
    or correctly returns no answer when the label is null.
  - precision: correct non-null picks / all non-null picks.
  - recall:    correct non-null picks / all non-null labels.

Thresholds are grid-searched on the golden set and written back to
scoring-config.json (documented as tuned on the golden set).
"""
import itertools
import json
from pathlib import Path

from .matcher import load_bank, load_config, load_library, match_question

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"


def evaluate(cfg: dict) -> dict:
    bank = {q["id"]: q for q in load_bank()["questions"]}
    answers = load_library()["answers"]
    golden = json.loads((DATA_DIR / "golden_set.json").read_text())["pairs"]
    correct = tp = fp = 0
    fn_labels = sum(1 for p in golden if p["expected"])
    misses = []
    for p in golden:
        q = bank[p["question_id"]]
        m = match_question(q, answers, cfg)
        got = m["answer_id"]
        if got == p["expected"]:
            correct += 1
            if got:
                tp += 1
        else:
            misses.append({"question_id": p["question_id"], "expected": p["expected"], "got": got,
                           "score": m["score"]})
            if got:
                fp += 1
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / fn_labels if fn_labels else 1.0
    return {
        "n": len(golden),
        "routing_accuracy": round(correct / len(golden), 3),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "misses": misses,
    }


def calibrate() -> dict:
    cfg = load_config()
    best = None
    for min_match, auto_ready in itertools.product(range(25, 61, 5), range(60, 91, 5)):
        if auto_ready <= min_match:
            continue
        trial = {**cfg, "thresholds": {"min_match": min_match, "review": min_match, "auto_ready": auto_ready}}
        ev = evaluate(trial)
        key = (ev["routing_accuracy"], ev["precision"])
        if best is None or key > best[0]:
            best = (key, min_match, auto_ready, ev)
    _, min_match, auto_ready, ev = best
    cfg["thresholds"] = {"min_match": min_match, "review": min_match, "auto_ready": auto_ready}
    cfg["tuning_note"] = (f"Thresholds grid-searched on the 41-pair golden set "
                          f"(min_match={min_match}, auto_ready={auto_ready}); "
                          f"routing_accuracy={ev['routing_accuracy']}, precision={ev['precision']}, recall={ev['recall']}.")
    (DATA_DIR / "scoring-config.json").write_text(json.dumps(cfg, indent=1))
    return {"thresholds": cfg["thresholds"], **ev}


def main() -> None:
    res = calibrate()
    print(f"thresholds: {res['thresholds']}")
    print(f"routing_accuracy={res['routing_accuracy']} precision={res['precision']} recall={res['recall']}")
    print(f"misses ({len(res['misses'])}):")
    for m in res["misses"]:
        print(f"  {m['question_id']}: expected {m['expected']}, got {m['got']} (score {m['score']})")


if __name__ == "__main__":
    main()
