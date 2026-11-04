import { describe, expect, it } from "vitest";
import { bigrams, jaccard, matchQuestion, routeFor, scorePair, tokenSet, tokens } from "./rules";
import type { AnswerLite } from "./rules";
import vectorsJson from "../public/data/test-vectors.json";
import libraryJson from "../public/data/library.json";
import summaryJson from "../public/data/summary.json";

describe("text utils mirror the Python implementation", () => {
  it("tokenizes like Python: lowercase, alnum, stopwords removed, len>1", () => {
    expect(tokens("Are audit and Assurance POLICIES?")).toEqual(["audit", "assurance", "policies"]);
  });

  it("computes bigrams and jaccard", () => {
    expect(bigrams("alpha beta gamma")).toEqual(new Set(["alpha beta", "beta gamma"]));
    expect(jaccard(new Set(["x"]), new Set(["x"]))).toBe(1);
    expect(jaccard(new Set(), new Set())).toBe(1);
    expect(jaccard(new Set(["a"]), new Set())).toBe(0);
  });

  it("tokenSet dedupes", () => {
    expect(tokenSet("risk risk register").size).toBe(2);
  });
});

describe("matcher mirrors Python score_pair", () => {
  const answers = libraryJson.answers as AnswerLite[];
  const cfg = summaryJson.config;

  it("scores the known time-source pair at or above auto_ready with a domain boost", () => {
    const ans = answers.find((a) => a.id === "HL-LOG-04")!;
    const s = scorePair(
      "Is a reliable time source being used across all relevant information processing systems?",
      "LOG",
      ans,
      cfg.weights,
    );
    expect(s.score).toBeGreaterThanOrEqual(cfg.thresholds.auto_ready);
    expect(s.parts.domain_boost).toBe(15);
  });

  it("gives no domain boost outside the answer's domains", () => {
    const ans = answers.find((a) => a.id === "HL-LOG-04")!;
    const s = scorePair("Is a reliable time source being used?", "IAM", ans, cfg.weights);
    expect(s.parts.domain_boost).toBe(0);
  });
});

describe("shared contract: test-vectors.json (Python-generated)", () => {
  const answers = libraryJson.answers as AnswerLite[];
  const cfg = summaryJson.config;

  for (const v of vectorsJson.vectors) {
    it(`vector ${v.question_id}: same answer, score and route as Python`, () => {
      const m = matchQuestion(v.question, v.domain, answers, cfg.thresholds.min_match, cfg.weights);
      expect(m.answerId).toBe(v.expected_answer_id);
      expect(m.score).toBeCloseTo(v.expected_score, 1);
      const r = routeFor(m, cfg.replay_date, cfg.freshness.answer_stale_after_days, cfg.thresholds.auto_ready);
      expect(r.route).toBe(v.expected_route);
    });
  }
});

describe("routeFor mirrors the Python route node", () => {
  const stale: AnswerLite = {
    id: "A-1", domains: ["LOG"], keywords: "logging", text: "logging policy",
    response: "Yes", owner: "X", owner_title: "Y", last_reviewed: "2025-01-01", evidence: [],
  };
  const fresh: AnswerLite = { ...stale, last_reviewed: "2026-10-01" };

  it("routes strong fresh matches READY", () => {
    const r = routeFor({ answerId: "A-1", score: 80, parts: { keyword_recall: 0, exact_phrase: 0, bigram_jaccard: 0, domain_boost: 0 }, margin: 10, answer: fresh }, "2026-11-04", 180, 60);
    expect(r.route).toBe("READY");
  });

  it("routes stale answers REVERIFY even at high scores", () => {
    const r = routeFor({ answerId: "A-1", score: 95, parts: { keyword_recall: 0, exact_phrase: 0, bigram_jaccard: 0, domain_boost: 0 }, margin: 10, answer: stale }, "2026-11-04", 180, 60);
    expect(r.route).toBe("REVERIFY");
    expect(r.flags).toContain("STALE_ANSWER");
  });

  it("routes misses NEW", () => {
    const r = routeFor({ answerId: null, score: 20, parts: { keyword_recall: 0, exact_phrase: 0, bigram_jaccard: 0, domain_boost: 0 }, margin: 0, answer: null }, "2026-11-04", 180, 60);
    expect(r.route).toBe("NEW");
  });
});
