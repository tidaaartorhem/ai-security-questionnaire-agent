import { useMemo, useState } from "react";
import type { QuestDeskData, Route } from "../types";
import { MatchCard } from "./shared";

type RouteFilter = "all" | Route;

const ROUTES: Route[] = ["READY", "REVIEW", "REVERIFY", "NEW"];

/** The response queue: every question, its route, and the draft behind a human gate. */
export default function QueueView({ data }: { data: QuestDeskData }) {
  const [route, setRoute] = useState<RouteFilter>("all");
  const [domain, setDomain] = useState<string>("all");
  const [query, setQuery] = useState("");

  const domains = useMemo(
    () => [...new Set(data.matches.map((m) => m.domain))].sort(),
    [data]
  );

  const shown = data.matches.filter(
    (m) =>
      (route === "all" || m.route === route) &&
      (domain === "all" || m.domain === domain) &&
      (query.trim() === "" ||
        (m.question + " " + m.question_id).toLowerCase().includes(query.trim().toLowerCase()))
  );

  return (
    <div>
      <div className="card">
        <h2>Response queue</h2>
        <p className="muted">
          {shown.length} of {data.matches.length} questions shown. READY responses
          can be exported as-is; REVIEW needs an SME check; REVERIFY means the
          matched answer or its evidence is stale; NEW has no approved answer and
          must be drafted from scratch. Every response needs human approval —
          nothing is final until a person signs off.
        </p>
        <div className="filters">
          <div className="seg">
            {(["all", ...ROUTES] as const).map((f) => (
              <button key={f} className={route === f ? "active" : ""} onClick={() => setRoute(f)}>
                {f === "all" ? `All (${data.matches.length})` : `${f} (${data.matches.filter((m) => m.route === f).length})`}
              </button>
            ))}
          </div>
          <div className="filter-row">
            <select value={domain} onChange={(e) => setDomain(e.target.value)} aria-label="Domain filter">
              <option value="all">All domains</option>
              {domains.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
            <input
              type="search"
              placeholder="Search questions…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
        </div>
      </div>
      {shown.map((m) => (
        <MatchCard key={m.question_id} m={m} />
      ))}
    </div>
  );
}
