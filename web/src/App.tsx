import { useState } from "react";
import { useQuestDeskData } from "./data";
import CoverageView from "./views/CoverageView";
import QueueView from "./views/QueueView";
import LibraryView from "./views/LibraryView";
import PasteView from "./views/PasteView";
import "./styles.css";

const REPO_URL = "https://github.com/tidaaartorhem/ai-security-questionnaire-agent";
const LIVE_URL = "https://ai-security-questionnaire-agent.web.app";

type Tab = "queue" | "coverage" | "library" | "paste";

const TABS: { id: Tab; label: string }[] = [
  { id: "queue", label: "Response queue" },
  { id: "coverage", label: "Domain coverage" },
  { id: "library", label: "Answer library" },
  { id: "paste", label: "Paste a question" },
];

export default function App() {
  const { data, error } = useQuestDeskData();
  const [tab, setTab] = useState<Tab>("queue");

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>
            <span className="mark">Qd</span>QuestDesk
          </h1>
          <p className="sub">
            The security-questionnaire response desk: 261 real CAIQ v4.0.2
            questions answered from a seeded approved-answer library with
            disclosed scoring, freshness checks, and a human gate on every
            response. Nothing ships without approval.
          </p>
          <div className="badges">
            <span className="badge neutral">
              <a href={REPO_URL} target="_blank" rel="noreferrer">
                GitHub repo
              </a>
            </span>
            <span className="badge neutral">
              <a href={LIVE_URL} target="_blank" rel="noreferrer">
                Live site
              </a>
            </span>
          </div>
        </div>
      </header>

      <div className="disclosure banner">
        <b>Deterministic, no LLM.</b> Keyword recall (55) + exact phrase (20) +
        bigram (10) + domain boost (15), capped at 100. Routes: ≥60 READY ·
        35–59 REVIEW · stale answer/evidence REVERIFY · &lt;35 NEW (no answer).
        Answers past their 180-day review date and evidence older than 365 days
        are flagged automatically. The in-browser matcher mirrors the Python
        pipeline exactly.
      </div>

      {error && <div className="card error">Failed to load data: {error}</div>}
      {!data && !error && <div className="card">Loading…</div>}

      {data && (
        <>
          <div className="stat-row">
            {(
              [
                ["READY", "ok", data.summary.findings.routes.READY ?? 0],
                ["REVIEW", "warn", data.summary.findings.routes.REVIEW ?? 0],
                ["REVERIFY", "orange", data.summary.findings.routes.REVERIFY ?? 0],
                ["NEW", "gray", data.summary.findings.routes.NEW ?? 0],
              ] as const
            ).map(([label, cls, n]) => (
              <div className="card stat" key={label}>
                <div className="stat-num">{n}</div>
                <div className={`pill ${cls}`}>{label}</div>
              </div>
            ))}
            <div className="card stat">
              <div className="stat-num">{data.summary.findings.effort_hours}h</div>
              <div className="muted small">estimated SME effort</div>
            </div>
            <div className="card stat">
              <div className="stat-num">{Math.round(data.summary.eval.routing_accuracy * 100)}%</div>
              <div className="muted small">matcher routing accuracy (41-pair golden set)</div>
            </div>
          </div>

          <div className="tabs">
            {TABS.map((t) => (
              <button
                key={t.id}
                className={tab === t.id ? "active" : ""}
                onClick={() => setTab(t.id)}
              >
                {t.label}
              </button>
            ))}
          </div>

          {tab === "queue" && <QueueView data={data} />}
          {tab === "coverage" && <CoverageView data={data} />}
          {tab === "library" && <LibraryView data={data} />}
          {tab === "paste" && <PasteView data={data} />}

          <footer className="footer muted small">
            Questions: the real CSA CAIQ v4.0.2 question bank (261 questions, 17
            domains; free to use per CSA). Answers and evidence describe the
            fictional Harbourline Analytics Inc. and are seeded demo data — the
            product's input, disclosed as such. Built{" "}
            {data.stamp ? `from ${data.stamp.git_sha} at ${data.stamp.built_utc}` : "locally"} ·
            no LLMs were used.
          </footer>
        </>
      )}
    </div>
  );
}
