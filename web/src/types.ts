export type Route = "READY" | "REVIEW" | "REVERIFY" | "NEW";

import type { Weights } from "./rules";

export interface ScoreParts {
  keyword_recall: number;
  exact_phrase: number;
  bigram_jaccard: number;
  domain_boost: number;
}

export interface Draft {
  response: string | null;
  text: string;
  evidence: string[];
  owner?: string;
  owner_title?: string;
  last_reviewed?: string;
  action: string;
}

export interface MatchRow {
  question_id: string;
  question: string;
  domain: string;
  domain_name: string;
  route: Route;
  flags: string[];
  answer_id: string | null;
  score: number;
  score_parts: ScoreParts;
  margin: number;
  draft: Draft;
  pending_approval: boolean;
}

export interface DomainStat {
  total: number;
  ready: number;
  review: number;
  reverify: number;
  new: number;
  coverage_pct: number;
}

export interface Summary {
  findings: {
    question_count: number;
    routes: Record<string, number>;
    ready_pct: number;
    flags: Record<string, number>;
    mean_match_confidence: number;
    domain_table: Record<string, DomainStat>;
    worst_domains: [string, DomainStat][];
    effort_minutes: number;
    effort_hours: number;
    sme_queue_owners: Record<string, number>;
  };
  eval: {
    n: number;
    routing_accuracy: number;
    precision: number;
    recall: number;
  };
  eval_misses: { question_id: string; expected: string | null; got: string | null; score: number }[];
  config: {
    weights: Weights;
    thresholds: { min_match: number; review: number; auto_ready: number };
    freshness: Record<string, number>;
    effort_minutes: Record<string, number>;
    replay_date: string;
    tuning_note?: string;
  };
  company: { name: string; profile: string; fictional: boolean };
  data_note: string;
}

export interface AnswerEntry {
  id: string;
  domains: string[];
  keywords: string;
  response: string;
  text: string;
  owner: string;
  owner_title: string;
  last_reviewed: string;
  evidence: string[];
  age_days: number;
  stale: boolean;
}

export interface EvidenceEntry {
  id: string;
  title: string;
  type: string;
  issued: string;
  issuer: string;
  age_days: number;
  stale: boolean;
}

export interface Library {
  answers: AnswerEntry[];
  evidence: EvidenceEntry[];
}

export interface TestVector {
  question_id: string;
  domain: string;
  question: string;
  expected_answer_id: string | null;
  expected_route: Route;
  expected_score: number;
}

export interface Stamp {
  repo: string;
  git_sha: string;
  built_utc: string;
  pipeline: string;
}

export interface QuestDeskData {
  summary: Summary;
  matches: MatchRow[];
  library: Library;
  vectors: { vectors: TestVector[] };
  stamp: Stamp | null;
}
