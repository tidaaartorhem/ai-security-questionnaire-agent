import type { QuestDeskData } from "../types";

const DOMAIN_NAMES: Record<string, string> = {
  "A&A": "Audit Assurance & Compliance",
  AIS: "Application & Interface Security",
  BCR: "Business Continuity Mgmt & Operational Resilience",
  CCC: "Change Control & Configuration Mgmt",
  CEK: "Cryptography, Encryption & Key Mgmt",
  DCS: "Datacenter Security",
  DSP: "Data Security & Privacy Lifecycle Mgmt",
  GRC: "Governance, Risk & Compliance",
  HRS: "Human Resources",
  IAM: "Identity & Access Management",
  IPY: "Interoperability & Portability",
  IVS: "Infrastructure & Virtualization Security",
  LOG: "Logging & Monitoring",
  SEF: "Security Incident Mgmt, E-Discovery & Cloud Forensics",
  STA: "Supply Chain Mgmt, Transparency & Accountability",
  TVM: "Threat & Vulnerability Management",
  UEM: "Unified Endpoint Management",
};

/** Per-domain coverage: where the approved library holds and where it leaks. */
export default function CoverageView({ data }: { data: QuestDeskData }) {
  const table = data.summary.findings.domain_table;
  const rows = Object.entries(table).sort((a, b) => a[1].coverage_pct - b[1].coverage_pct);
  const f = data.summary.findings;

  return (
    <div>
      <div className="card">
        <h2>Domain coverage</h2>
        <p className="muted">
          Coverage = questions with a matched approved answer (READY, REVIEW or
          REVERIFY) out of all questions in the domain. Mean match confidence{" "}
          {f.mean_match_confidence}. The three thinnest domains are{" "}
          {f.worst_domains.map(([d, t]) => `${d} (${t.coverage_pct}%)`).join(", ")} —
          that's where the next answer-writing sprint should go.
        </p>
      </div>
      <div className="card">
        <table className="cov-table">
          <thead>
            <tr>
              <th>Domain</th>
              <th>Questions</th>
              <th>Coverage</th>
              <th>READY</th>
              <th>REVIEW</th>
              <th>REVERIFY</th>
              <th>NEW</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([d, t]) => (
              <tr key={d}>
                <td>
                  <b>{d}</b> <span className="muted">{DOMAIN_NAMES[d] ?? ""}</span>
                </td>
                <td>{t.total}</td>
                <td>
                  <span className="confbar">
                    <span className="confbar-track">
                      <span
                        className={`confbar-fill ${t.coverage_pct >= 70 ? "ok" : t.coverage_pct >= 40 ? "warn" : "bad"}`}
                        style={{ width: `${t.coverage_pct}%` }}
                      />
                    </span>
                    <span className="confbar-num">{t.coverage_pct}%</span>
                  </span>
                </td>
                <td>{t.ready}</td>
                <td>{t.review}</td>
                <td>{t.reverify}</td>
                <td>{t.new}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="card">
        <h2>Flags</h2>
        <p className="muted">
          {Object.entries(f.flags)
            .map(([k, v]) => `${v}× ${k.replace(/_/g, " ").toLowerCase()}`)
            .join(" · ") || "none"}
          . Stale answers are past their 180-day review date; stale evidence is
          older than 365 days; wording-changed questions differ materially from
          the 2025 round and need re-confirmation.
        </p>
        <h2>SME queue by owner</h2>
        <p className="muted">
          {Object.entries(f.sme_queue_owners)
            .map(([o, n]) => `${o}: ${n}`)
            .join(" · ")}
        </p>
        <h2>Golden-set eval</h2>
        <p className="muted">
          41 hand-labeled question→answer pairs: routing accuracy{" "}
          {Math.round(data.summary.eval.routing_accuracy * 100)}%, precision{" "}
          {Math.round(data.summary.eval.precision * 100)}%, recall{" "}
          {Math.round(data.summary.eval.recall * 100)}%. Thresholds
          grid-searched on this set (min_match 35, auto_ready 60).
        </p>
      </div>
    </div>
  );
}
