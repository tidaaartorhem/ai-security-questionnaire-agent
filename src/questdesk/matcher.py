"""Deterministic question -> approved-answer matcher.

Disclosed scoring (0-100), same family as the Bidboard RFP matcher:
  - keyword token recall      x55  (|question tokens ∩ answer tokens| / |question tokens|)
  - exact 3-gram phrase hit   x20  (1.0 if any answer-keyword 3-gram appears verbatim in the question)
  - bigram Jaccard            x10
  - domain boost              x15  (answer tagged to the question's CAIQ domain)

No LLM calls. Thresholds live in data/raw/scoring-config.json.
"""
import json
from pathlib import Path

from .text import bigrams, jaccard, token_set, tokens

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"


def load_config() -> dict:
    return json.loads((DATA_DIR / "scoring-config.json").read_text())


def load_bank() -> dict:
    return json.loads((DATA_DIR / "caiq_v402.json").read_text())


def load_library() -> dict:
    return json.loads((DATA_DIR / "answer_library.json").read_text())


def _answer_corpus(answer: dict) -> str:
    return f"{answer['text']} {answer['keywords']}"


def score_pair(question: str, q_domain: str, answer: dict, cfg: dict) -> dict:
    w = cfg["weights"]
    q_toks = token_set(question)
    a_toks = token_set(_answer_corpus(answer))

    recall = len(q_toks & a_toks) / len(q_toks) if q_toks else 0.0
    keyword_score = recall * w["keyword_recall"]

    # exact 3-gram phrase hit from the answer's keyword field
    kw_toks = tokens(answer["keywords"])
    phrase_hit = 0.0
    q_low = question.lower()
    for i in range(len(kw_toks) - 2):
        phrase = " ".join(kw_toks[i : i + 3])
        if phrase in q_low:
            phrase_hit = 1.0
            break
    phrase_score = phrase_hit * w["exact_phrase"]

    bigram_score = jaccard(bigrams(question), bigrams(_answer_corpus(answer))) * w["bigram_jaccard"]

    domain_score = w["domain_boost"] if q_domain in answer.get("domains", []) else 0.0

    total = keyword_score + phrase_score + bigram_score + domain_score
    return {
        "score": round(total, 2),
        "parts": {
            "keyword_recall": round(keyword_score, 2),
            "exact_phrase": round(phrase_score, 2),
            "bigram_jaccard": round(bigram_score, 2),
            "domain_boost": round(domain_score, 2),
        },
    }


def match_question(question: dict, answers: list[dict], cfg: dict) -> dict:
    """Return the best answer for a question with its score breakdown."""
    scored = [
        (a, score_pair(question["question"], question["domain"], a, cfg)) for a in answers
    ]
    scored.sort(key=lambda p: p[1]["score"], reverse=True)
    best, best_score = scored[0]
    runner_up = scored[1][1]["score"] if len(scored) > 1 else 0.0
    return {
        "question_id": question["id"],
        "answer_id": best["id"] if best_score["score"] >= cfg["thresholds"]["min_match"] else None,
        "score": best_score["score"],
        "score_parts": best_score["parts"],
        "margin": round(best_score["score"] - runner_up, 2),
        "best_answer": best if best_score["score"] >= cfg["thresholds"]["min_match"] else None,
    }
