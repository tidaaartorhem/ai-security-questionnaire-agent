import { useState } from "react";
import type { AnswerLite, MatchResult } from "../rules";
import { matchQuestion, routeFor } from "../rules";
import type { QuestDeskData } from "../types";
import { FlagBadge, RouteBadge, ScoreBar } from "./shared";

/** Paste-a-question: runs the same matcher in the browser (TS mirror). */
export default function PasteView({ data }: { data: QuestDeskData }) {
  const [text, setText] = useState("");
  const [domain, setDomain] = useState("LOG");
  const [result, setResult] = useState<MatchResult | null>(null);

  const cfg = data.summary.config;
  const answers = data.library.answers as AnswerLite[];

  const runMatch = () => {
    if (!text.trim()) return;
    const m = matchQuestion(text.trim(), domain, answers, cfg.thresholds.min_match, cfg.weights);
    setResult(m);
  };

  const route = result
    ? routeFor(result, cfg.replay_date, cfg.freshness.answer_stale_after_days, cfg.thresholds.auto_ready)
    : null;

  return (
    <div>
      <div className="card">
        <h2>Paste a question</h2>
        <p className="muted">
          Paste any security-questionnaire question. The in-browser matcher (the
          exact TypeScript mirror of the Python pipeline, verified against{" "}
          {data.vectors.vectors.length} shared test vectors) scores it against
          all {answers.length} approved answers and predicts the route.
        </p>
        <div className="filter-row">
          <select value={domain} onChange={(e) => setDomain(e.target.value)} aria-label="Question domain">
            {Object.keys(data.summary.findings.domain_table).sort().map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>
        <textarea
          rows={4}
          placeholder="e.g. Is multi-factor authentication enforced for all remote access?"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <div style={{ marginTop: 8 }}>
          <button className="primary" onClick={runMatch}>Match it</button>
        </div>
      </div>

      {result && route && (
        <div className="card match-card">
          <div className="match-head">
            <RouteBadge route={route.route} />
            {route.flags.map((f) => (
              <FlagBadge key={f} flag={f} />
            ))}
            <span className="pill gate">human gate required</span>
          </div>
          <div className="match-body">
            <ScoreBar value={result.score} />
            <div className="match-detail">
              {result.answer ? (
                <>
                  <div>
                    <b>{result.answer.id}</b>
                    <span className={`pill neutral ${result.answer.response === "Yes" ? "ok" : "bad"}`} style={{ marginLeft: 8 }}>
                      {result.answer.response}
                    </span>
                  </div>
                  <p className="answer-text">{result.answer.text}</p>
                  <div className="muted">
                    Owner: {result.answer.owner} ({result.answer.owner_title}) · last reviewed {result.answer.last_reviewed}
                  </div>
                  {result.answer.evidence.length > 0 && (
                    <div className="muted">Evidence: {result.answer.evidence.join(", ")}</div>
                  )}
                  <div className="muted">
                    keyword {result.parts.keyword_recall}
                    {result.parts.exact_phrase > 0 ? " · exact phrase" : ""}
                    {result.parts.domain_boost > 0 ? " · domain boost" : ""} · margin {result.margin}
                  </div>
                </>
              ) : (
                <p className="answer-text">
                  No approved answer reaches the match bar (score {result.score} &lt;{" "}
                  {cfg.thresholds.min_match}). Draft this one from scratch with the
                  control owner.
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
