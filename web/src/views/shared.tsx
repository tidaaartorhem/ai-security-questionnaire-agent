import type { MatchRow, Route } from "../types";

const ROUTE_CLASS: Record<Route, string> = {
  READY: "ok",
  REVIEW: "warn",
  REVERIFY: "orange",
  NEW: "gray",
};

export function RouteBadge({ route }: { route: Route }) {
  return <span className={`pill ${ROUTE_CLASS[route]}`}>{route}</span>;
}

const FLAG_LABEL: Record<string, string> = {
  STALE_ANSWER: "stale answer",
  STALE_EVIDENCE: "stale evidence",
  WORDING_CHANGED: "wording changed",
};

export function FlagBadge({ flag }: { flag: string }) {
  return <span className="pill orange">{FLAG_LABEL[flag] ?? flag}</span>;
}

export function ScoreBar({ value }: { value: number }) {
  const cls = value >= 60 ? "ok" : value >= 35 ? "warn" : "gray";
  return (
    <span className="confbar" title={`${value}`}>
      <span className="confbar-track">
        <span className={`confbar-fill ${cls}`} style={{ width: `${Math.min(100, value)}%` }} />
      </span>
      <span className="confbar-num">{value}</span>
    </span>
  );
}

export function MatchCard({ m, showQuestion = true }: { m: MatchRow; showQuestion?: boolean }) {
  return (
    <div className="card match-card">
      <div className="match-head">
        <span className="req-id">
          {m.question_id} · {m.domain}
        </span>
        <RouteBadge route={m.route} />
        {m.flags.map((f) => (
          <FlagBadge key={f} flag={f} />
        ))}
        <span className="pill gate">human gate required</span>
      </div>
      {showQuestion && <p className="req-text">{m.question}</p>}
      <div className="match-body">
        <ScoreBar value={m.score} />
        <div className="match-detail">
          {m.answer_id ? (
            <>
              <div>
                <b>{m.answer_id}</b>
                {m.draft.response && (
                  <span className={`pill neutral ${m.draft.response === "Yes" ? "ok" : "bad"}`} style={{ marginLeft: 8 }}>
                    {m.draft.response}
                  </span>
                )}
              </div>
              <p className="answer-text">{m.draft.text}</p>
              <div className="muted">
                Owner: {m.draft.owner} ({m.draft.owner_title}) · last reviewed {m.draft.last_reviewed}
              </div>
              {m.draft.evidence.length > 0 && (
                <div className="muted">Evidence: {m.draft.evidence.join(", ")}</div>
              )}
              <div className="muted">
                Why this answer: keyword {m.score_parts.keyword_recall}
                {m.score_parts.exact_phrase > 0 ? " · exact phrase" : ""}
                {m.score_parts.bigram_jaccard > 0 ? ` · bigram ${m.score_parts.bigram_jaccard}` : ""}
                {m.score_parts.domain_boost > 0 ? " · domain boost" : ""} · margin {m.margin}
              </div>
              <div className="action-line">
                <b>Recommended action:</b> {m.draft.action}
              </div>
            </>
          ) : (
            <>
              <p className="answer-text">{m.draft.text}</p>
              <div className="action-line">
                <b>Recommended action:</b> {m.draft.action}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
