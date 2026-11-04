import { useState } from "react";
import type { QuestDeskData } from "../types";

/** The approved answer library and evidence register, with staleness badges. */
export default function LibraryView({ data }: { data: QuestDeskData }) {
  const [tab, setTab] = useState<"answers" | "evidence">("answers");
  const [staleOnly, setStaleOnly] = useState(false);

  const answers = data.library.answers.filter((a) => !staleOnly || a.stale);
  const evidence = data.library.evidence.filter((e) => !staleOnly || e.stale);

  return (
    <div>
      <div className="card">
        <h2>Answer library</h2>
        <p className="muted">
          {data.library.answers.length} approved answers for the fictional
          Harbourline Analytics Inc. (seeded demo data). {data.library.answers.filter((a) => a.stale).length} are
          past their 180-day review date — every question matched to one routes
          to REVERIFY until a human re-confirms it.
        </p>
        <div className="seg">
          <button className={tab === "answers" ? "active" : ""} onClick={() => setTab("answers")}>
            Answers ({data.library.answers.length})
          </button>
          <button className={tab === "evidence" ? "active" : ""} onClick={() => setTab("evidence")}>
            Evidence ({data.library.evidence.length})
          </button>
          <button className={staleOnly ? "active" : ""} onClick={() => setStaleOnly(!staleOnly)}>
            Stale only
          </button>
        </div>
      </div>

      {tab === "answers" &&
        answers.map((a) => (
          <div className="card" key={a.id}>
            <div className="match-head">
              <span className="req-id">{a.id}</span>
              {a.domains.map((d) => (
                <span key={d} className="pill neutral">{d}</span>
              ))}
              <span className={`pill neutral ${a.response === "Yes" ? "ok" : "bad"}`}>{a.response}</span>
              {a.stale && <span className="pill orange">stale · reviewed {a.last_reviewed}</span>}
            </div>
            <p className="answer-text">{a.text}</p>
            <div className="muted">
              Owner: {a.owner} ({a.owner_title}) · reviewed {a.last_reviewed} ({a.age_days}d ago)
            </div>
            {a.evidence.length > 0 && <div className="muted">Evidence: {a.evidence.join(", ")}</div>}
          </div>
        ))}

      {tab === "evidence" &&
        evidence.map((e) => (
          <div className="card" key={e.id}>
            <div className="match-head">
              <span className="req-id">{e.id}</span>
              <span className="pill neutral">{e.type}</span>
              {e.stale && <span className="pill orange">stale · issued {e.issued}</span>}
            </div>
            <p className="answer-text">{e.title}</p>
            <div className="muted">
              Issuer: {e.issuer} · issued {e.issued} ({e.age_days}d ago)
            </div>
          </div>
        ))}
    </div>
  );
}
