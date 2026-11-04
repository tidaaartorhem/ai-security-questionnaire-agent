#!/usr/bin/env python3
"""Builds the seeded approved-answer + evidence libraries.

IMPORTANT (disclosed on the site and in the README): the answer and
evidence libraries describe a FICTIONAL company, Harbourline Analytics
Inc. (a Toronto B2B SaaS). Only the CAIQ question bank is real data.
Seeded entries are realistic but synthetic — exactly like a vendor
starting its first questionnaire from an approved answer library.

Run: python3 scripts/seed_library.py  -> data/raw/answer_library.json
"""
import json
from pathlib import Path

REPLAY_DATE = "2026-11-04"
COMPANY = {
    "name": "Harbourline Analytics Inc.",
    "profile": "Fictional Toronto B2B SaaS (marketing analytics platform), ~90 employees, hosts on AWS ca-central-1, Okta workforce IdP, SOC 2 Type II.",
    "fictional": True,
}

EVIDENCE = [
    {"id": "EV-SOC2-2026", "title": "SOC 2 Type II report, period ending 2026-06-30", "type": "audit report", "issued": "2026-08-20", "issuer": "Northgate Assurance LLP"},
    {"id": "EV-SOC2-2025", "title": "SOC 2 Type II report, period ending 2025-06-30", "type": "audit report", "issued": "2025-08-15", "issuer": "Northgate Assurance LLP"},
    {"id": "EV-PENTEST-2026", "title": "Annual penetration test report", "type": "test result", "issued": "2026-09-02", "issuer": "RedGate Security"},
    {"id": "EV-PENTEST-2025", "title": "Annual penetration test report", "type": "test result", "issued": "2025-08-28", "issuer": "RedGate Security"},
    {"id": "EV-VULNSCAN-Q3", "title": "Quarterly vulnerability scan summary, Q3 2026", "type": "scan result", "issued": "2026-10-15", "issuer": "Security Engineering (internal)"},
    {"id": "EV-IR-PLAN", "title": "Incident response plan v3.2", "type": "policy document", "issued": "2026-07-01", "issuer": "Security Engineering (internal)"},
    {"id": "EV-TABLETOP-2026", "title": "Incident response tabletop exercise report", "type": "test result", "issued": "2026-06-18", "issuer": "Security Engineering (internal)"},
    {"id": "EV-BCP-TEST-2026", "title": "Business continuity / DR test report", "type": "test result", "issued": "2026-05-22", "issuer": "IT Operations (internal)"},
    {"id": "EV-BACKUP-RESTORE", "title": "Backup restore test log (monthly)", "type": "log export", "issued": "2026-10-01", "issuer": "IT Operations (internal)"},
    {"id": "EV-AWS-SOC2", "title": "AWS SOC 2 Type II report (inherited control evidence)", "type": "audit report", "issued": "2026-04-01", "issuer": "AWS"},
    {"id": "EV-AWS-CAIQ", "title": "AWS CAIQ v4.0.2 self-assessment (inherited control evidence)", "type": "attestation", "issued": "2026-01-15", "issuer": "AWS"},
    {"id": "EV-POLICY-INFOSEC", "title": "Information security policy v4.0", "type": "policy document", "issued": "2026-03-10", "issuer": "CISO"},
    {"id": "EV-POLICY-DATA", "title": "Data protection and privacy policy v2.1", "type": "policy document", "issued": "2026-03-10", "issuer": "Privacy Counsel"},
    {"id": "EV-POLICY-APPSEC", "title": "Application security policy v3.0", "type": "policy document", "issued": "2026-02-15", "issuer": "Security Engineering (internal)"},
    {"id": "EV-POLICY-CHANGE", "title": "Change management policy v2.4", "type": "policy document", "issued": "2026-04-05", "issuer": "DevOps (internal)"},
    {"id": "EV-POLICY-BCP", "title": "Business continuity policy v2.0", "type": "policy document", "issued": "2026-01-20", "issuer": "IT Operations (internal)"},
    {"id": "EV-POLICY-REMOTE", "title": "Remote work and acceptable use policy v1.8", "type": "policy document", "issued": "2025-12-01", "issuer": "IT (internal)"},
    {"id": "EV-RISK-REGISTER", "title": "Risk register, Q3 2026", "type": "register", "issued": "2026-09-30", "issuer": "CISO"},
    {"id": "EV-DPIA-2026", "title": "Data protection impact assessment, analytics pipeline v2", "type": "assessment", "issued": "2026-08-01", "issuer": "Privacy Counsel"},
    {"id": "EV-DATAFLOW", "title": "Customer data flow diagrams", "type": "diagram", "issued": "2026-07-15", "issuer": "Security Engineering (internal)"},
    {"id": "EV-ACCESS-REVIEW-Q3", "title": "Quarterly user access review, Q3 2026", "type": "attestation", "issued": "2026-10-10", "issuer": "IT (internal)"},
    {"id": "EV-ACCESS-REVIEW-Q1", "title": "Quarterly user access review, Q1 2026", "type": "attestation", "issued": "2026-04-10", "issuer": "IT (internal)"},
    {"id": "EV-SUBPROCESSORS", "title": "Subprocessor list", "type": "register", "issued": "2026-09-01", "issuer": "Legal"},
    {"id": "EV-TRAINING-2026", "title": "Security awareness training completion report", "type": "report", "issued": "2026-10-25", "issuer": "HR (internal)"},
    {"id": "EV-JAMF-COMPLIANCE", "title": "Endpoint compliance export (Jamf Pro)", "type": "config export", "issued": "2026-11-01", "issuer": "IT (internal)"},
    {"id": "EV-DATADOG-LOGS", "title": "Log retention and monitoring configuration export (Datadog)", "type": "config export", "issued": "2026-10-20", "issuer": "DevOps (internal)"},
    {"id": "EV-CRYPTO-INVENTORY", "title": "Cryptographic key inventory (AWS KMS)", "type": "register", "issued": "2026-09-15", "issuer": "Security Engineering (internal)"},
    {"id": "EV-VENDOR-ASSESS", "title": "Vendor risk assessment pack, H1 2026", "type": "assessment", "issued": "2026-06-30", "issuer": "Security Engineering (internal)"},
]

# ---------------------------------------------------------------- answers
# owner, last_reviewed (ISO), response, evidence ids, domains, keywords, text
ANSWERS: list[dict] = []

def A(aid, domains, keywords, response, text, owner, last_reviewed, evidence):
    ANSWERS.append({
        "id": aid, "domains": domains, "keywords": keywords, "response": response,
        "text": text, "owner": owner, "owner_title": OWNER_TITLES.get(owner, ""),
        "last_reviewed": last_reviewed, "evidence": evidence,
    })

OWNER_TITLES = {
    "Priya Nair": "CISO",
    "Daniel Okafor": "Security Engineer",
    "Lena Fischer": "IT Manager",
    "Marcus Webb": "Privacy Counsel",
    "Sam Reyes": "DevOps Lead",
    "Aisha Bello": "HR Manager",
}

# ============================ A&A ============================
A("HL-AA-01", ["A&A"], "audit assurance policies procedures standards established documented approved communicated evaluated maintained",
  "Yes", "Harbourline maintains an Information Security Policy (v4.0) that includes audit and assurance requirements. Policies are approved by the CISO, published in the company handbook, communicated to all staff during onboarding, and evaluated for effectiveness as part of the annual SOC 2 readiness review.",
  "Priya Nair", "2026-03-10", ["EV-POLICY-INFOSEC", "EV-SOC2-2025"])
A("HL-AA-02", ["A&A"], "independent audit assurance assessment SOC 2 Type II annual external auditor",
  "Yes", "Harbourline undergoes an independent SOC 2 Type II audit annually, performed by Northgate Assurance LLP. The most recent report covers the period ending 2026-06-30 and was issued 2026-08-20. The audit is conducted under AICPA Trust Services Criteria and includes testing of security, availability, and confidentiality controls.",
  "Priya Nair", "2026-08-20", ["EV-SOC2-2026"])
A("HL-AA-03", ["A&A"], "risk-based audit plan corrective action plan remediate audit findings remediation status stakeholders",
  "Yes", "Audit findings are tracked in a risk-ranked remediation register owned by the CISO. Each finding gets a severity, an owner, and a target date; critical findings require remediation within 30 days. Remediation status is reviewed monthly by leadership and reported to the board quarterly.",
  "Priya Nair", "2026-09-30", ["EV-RISK-REGISTER", "EV-SOC2-2026"])
A("HL-AA-04", ["A&A"], "compliance verified standards regulations legal contractual statutory requirements",
  "Yes", "Compliance against SOC 2, PIPEDA, and applicable contractual security requirements is verified through the annual SOC 2 audit and quarterly internal control self-assessments. Contractual obligations from customer DPAs are mapped to controls in the GRC register and reviewed when agreements renew.",
  "Priya Nair", "2026-09-30", ["EV-SOC2-2026", "EV-RISK-REGISTER"])
A("HL-AA-05", ["A&A"], "audit management process audit planning risk analysis security control assessments conclusions remediation schedules report generation",
  "Yes", "The audit management process is defined in the Information Security Policy: annual audit planning, risk-based scoping, evidence collection with assigned owners, management review of findings, and tracked remediation. The CISO runs the cycle each year ahead of the SOC 2 fieldwork window.",
  "Priya Nair", "2026-03-10", ["EV-POLICY-INFOSEC"])

# ============================ AIS ============================
A("HL-AIS-01", ["AIS"], "application security policies procedures SDLC secure development",
  "Yes", "The Application Security Policy (v3.0) defines secure development requirements for all Harbourline services: threat modeling for new features, mandatory code review, SAST in CI, and dependency scanning. It is reviewed annually by Security Engineering.",
  "Daniel Okafor", "2026-02-15", ["EV-POLICY-APPSEC"])
A("HL-AIS-02", ["AIS"], "SDLC process application design development deployment operation security requirements",
  "Yes", "Harbourline follows a defined SDLC: design review with security sign-off, branch-protected GitHub repos, CI checks (SAST, SCA, secret scanning), staged deployment through GitHub Actions, and production change approval. The process is documented in the engineering handbook.",
  "Sam Reyes", "2026-06-01", ["EV-POLICY-APPSEC", "EV-POLICY-CHANGE"])
A("HL-AIS-03", ["AIS"], "baseline requirements secure applications established documented maintained",
  "Yes", "Baseline security requirements for applications (authentication, session management, input validation, logging, cryptography) are documented in the AppSec baseline standard. New services must meet the baseline before launch, verified by a pre-launch security checklist.",
  "Daniel Okafor", "2026-02-15", ["EV-POLICY-APPSEC"])
A("HL-AIS-04", ["AIS"], "testing strategy acceptance criteria new systems upgrades automated testing",
  "Yes", "Release acceptance criteria require green CI (unit/integration tests), SAST and dependency scans with no critical findings, and QA sign-off. Automated test suites run on every pull request via GitHub Actions; penetration testing is performed annually by an external firm.",
  "Sam Reyes", "2026-09-02", ["EV-PENTEST-2026"])
A("HL-AIS-05", ["AIS"], "deployment integration application code automated secure deployment CI/CD",
  "Yes", "All application deployments are automated through GitHub Actions pipelines with signed artifacts, staged rollouts, and automated rollback on health-check failure. Manual production deploys are not permitted.",
  "Sam Reyes", "2026-06-01", ["EV-POLICY-CHANGE"])
A("HL-AIS-06", ["AIS"], "application security vulnerabilities remediated defined processes SLA",
  "Yes", "Vulnerabilities are triaged by severity with defined SLAs: critical within 15 days, high within 30 days, tracked in the security backlog. Remediation of critical/high findings is verified by re-scan before closure. The 2026 penetration test findings were all remediated within SLA.",
  "Daniel Okafor", "2026-09-02", ["EV-PENTEST-2026", "EV-VULNSCAN-Q3"])

# ============================ BCR ============================
A("HL-BCR-01", ["BCR"], "business continuity operational resilience policies procedures",
  "Yes", "The Business Continuity Policy (v2.0) covers continuity and operational resilience for the SaaS platform and corporate operations, with defined roles, RTO/RPO targets per service tier, and annual review by IT Operations.",
  "Lena Fischer", "2026-01-20", ["EV-POLICY-BCP"])
A("HL-BCR-02", ["BCR"], "business continuity strategies reduce impact withstand recover disruption",
  "Yes", "Continuity strategies include multi-AZ deployment on AWS, automated failover for the primary database, and a documented degraded-mode runbook. Strategies are reviewed after each test or real incident.",
  "Sam Reyes", "2026-05-22", ["EV-BCP-TEST-2026"])
A("HL-BCR-03", ["BCR"], "business continuity plans exercised tested annually disaster response plan",
  "Yes", "The business continuity and disaster response plans are exercised at least annually. The most recent test (2026-05-22) covered a simulated regional AWS impairment with database failover; all RTO targets were met and lessons learned were actioned.",
  "Lena Fischer", "2026-05-22", ["EV-BCP-TEST-2026"])
A("HL-BCR-04", ["BCR"], "cloud data periodically backed up confidentiality integrity availability backup",
  "Yes", "Customer data in RDS and S3 is backed up automatically with point-in-time recovery (35-day retention for databases, versioned S3 with 90-day retention). Backups are encrypted with the same KMS keys as production and access is restricted to the platform team.",
  "Sam Reyes", "2026-10-01", ["EV-BACKUP-RESTORE"])
A("HL-BCR-05", ["BCR"], "backups restored appropriately resiliency restore test",
  "Yes", "Backup restores are tested monthly: a database snapshot is restored to an isolated environment and integrity-checked. The October 2026 test restored successfully within the 4-hour RTO.",
  "Sam Reyes", "2026-10-01", ["EV-BACKUP-RESTORE"])
A("HL-BCR-06", ["BCR"], "disaster response plan established documented approved applied evaluated maintained updated",
  "Yes", "The disaster response plan is documented, approved by the CISO, and maintained by IT Operations. It is updated at least annually and after any significant infrastructure change, most recently following the May 2026 exercise.",
  "Lena Fischer", "2026-05-22", ["EV-BCP-TEST-2026", "EV-POLICY-BCP"])
A("HL-BCR-07", ["BCR"], "local emergency authorities included exercise",
  "No", "The annual continuity exercise is a tabletop plus technical failover test run internally; local emergency authorities are not included because Harbourline operates a single Toronto office and a cloud-only platform with no physical facilities under its control.",
  "Lena Fischer", "2026-05-22", ["EV-BCP-TEST-2026"])

# ============================ CCC ============================
A("HL-CCC-01", ["CCC"], "change control approval testing process baselines risk management changing assets",
  "Yes", "All production changes go through the change management process: pull-request review, CI checks, and approval by a code owner; database migrations require DBA review. Emergency changes follow a documented break-glass path with retrospective approval within 24 hours.",
  "Sam Reyes", "2026-04-05", ["EV-POLICY-CHANGE"])
A("HL-CCC-02", ["CCC"], "unauthorized addition removal update management assets restricted change baselines",
  "Yes", "Production asset changes are restricted to the deployment pipeline — direct console/SSH access to production is disabled. Infrastructure is defined in Terraform; drift is detected by a nightly plan check and unauthorized changes are reverted.",
  "Sam Reyes", "2026-09-01", ["EV-POLICY-CHANGE"])
A("HL-CCC-03", ["CCC"], "roll back changes previously known good state rollback",
  "Yes", "Every deployment supports automated rollback: container images are immutable and tagged, database migrations are reversible, and Terraform state is versioned. Rollback was exercised successfully during the May continuity test.",
  "Sam Reyes", "2026-05-22", ["EV-POLICY-CHANGE", "EV-BCP-TEST-2026"])
A("HL-CCC-04", ["CCC"], "exceptions emergencies change configuration management procedure exception process",
  "Yes", "Emergency changes use the break-glass procedure: implement first with on-call approval, document in the change log, and obtain retrospective approval within 24 hours. Emergency changes are reviewed in the weekly engineering review.",
  "Sam Reyes", "2026-04-05", ["EV-POLICY-CHANGE"])
A("HL-CCC-05", ["CCC"], "detection measures proactive notification changes deviate established baselines drift",
  "Yes", "Configuration drift is detected by nightly Terraform plan runs and Datadog monitors on critical infrastructure settings; deviations page the on-call engineer. CloudTrail-equivalent audit logs capture all control-plane changes.",
  "Sam Reyes", "2026-10-20", ["EV-DATADOG-LOGS"])

# ============================ CEK ============================
A("HL-CEK-01", ["CEK"], "cryptography encryption key management policies procedures roles responsibilities",
  "Yes", "Cryptography and key management requirements are defined in the Information Security Policy and the AppSec baseline: approved algorithms, KMS usage, and role assignments. The Security Engineer owns the key management program; the CISO approves exceptions.",
  "Daniel Okafor", "2026-03-10", ["EV-POLICY-INFOSEC", "EV-CRYPTO-INVENTORY"])
A("HL-CEK-02", ["CEK"], "data at-rest in-transit cryptographically protected certified libraries KMS AES TLS",
  "Yes", "Data at rest is encrypted with AES-256 via AWS KMS; data in transit uses TLS 1.2+ for all external and inter-service traffic. Cryptographic operations use AWS-maintained libraries (FIPS 140-2 validated modules where applicable).",
  "Daniel Okafor", "2026-09-15", ["EV-CRYPTO-INVENTORY", "EV-PENTEST-2026"])
A("HL-CEK-03", ["CEK"], "encryption algorithms data classification appropriate",
  "Yes", "AES-256-GCM is the standard for data at rest and TLS 1.2+ with strong cipher suites for data in transit, applied uniformly including to data classified as confidential or restricted in the data classification scheme.",
  "Daniel Okafor", "2026-09-15", ["EV-CRYPTO-INVENTORY"])
A("HL-CEK-04", ["CEK"], "cryptographic keys generated industry accepted approved libraries randomness",
  "Yes", "Keys are generated by AWS KMS using FIPS 140-2 validated hardware security modules; application-level secrets are generated with cryptographically secure random number generators. No customer code implements its own key generation.",
  "Daniel Okafor", "2026-09-15", ["EV-CRYPTO-INVENTORY"])
A("HL-CEK-05", ["CEK"], "cryptographic keys rotated cryptoperiod",
  "Yes", "KMS data keys rotate automatically on the AWS-managed schedule; service credentials and API tokens rotate at least annually and on employee departure. Rotation events are logged and reviewed quarterly.",
  "Daniel Okafor", "2026-10-10", ["EV-CRYPTO-INVENTORY", "EV-ACCESS-REVIEW-Q3"])
A("HL-CEK-06", ["CEK"], "keys revoked removed cryptoperiod compromised key revocation",
  "Yes", "Compromised or departing-employee-associated keys are revoked immediately via KMS disable/delete scheduling and Okta deprovisioning. Revocation is verified in the quarterly access review.",
  "Lena Fischer", "2026-10-10", ["EV-ACCESS-REVIEW-Q3"])
A("HL-CEK-07", ["CEK"], "processes procedures technical measures destroy unneeded keys secure deletion",
  "Yes", "Unneeded KMS keys are scheduled for deletion with the minimum 7-day waiting period after confirming no encrypted data depends on them; application secrets are rotated then purged from the secrets manager.",
  "Daniel Okafor", "2026-09-15", ["EV-CRYPTO-INVENTORY"])
A("HL-CEK-08", ["CEK"], "capacity manage own data encryption keys customer managed keys BYOK",
  "No", "Harbourline does not currently offer customer-managed (BYOK) encryption keys; all tenant data is encrypted under Harbourline-managed KMS keys with per-tenant key separation. BYOK is on the roadmap for enterprise tiers.",
  "Priya Nair", "2026-08-01", ["EV-POLICY-DATA"])

# ============================ DCS ============================
A("HL-DCS-01", ["DCS"], "datacenter physical security shared responsibility AWS inherited controls",
  "Yes", "Harbourline operates no datacenters of its own; all infrastructure runs on AWS (ca-central-1). Physical security, environmental controls, and media handling for the underlying facilities are inherited from AWS and covered by AWS's SOC 2 report, which we review annually.",
  "Priya Nair", "2026-04-01", ["EV-AWS-SOC2", "EV-AWS-CAIQ"])
A("HL-DCS-02", ["DCS"], "secure disposal equipment media destruction data destruction",
  "Yes", "End-of-life laptops and drives are wiped with certified erasure software or physically destroyed by a contracted ITAD vendor with certificates of destruction. Cloud storage media sanitization is inherited from AWS.",
  "Lena Fischer", "2026-06-01", ["EV-JAMF-COMPLIANCE"])
A("HL-DCS-03", ["DCS"], "physical security perimeters authorized personnel secure areas access",
  "Yes", "The Toronto office uses badge access with visitor logging; server rooms are not applicable (cloud-only). AWS facility perimeters and access controls are inherited and attested in the AWS SOC 2 report.",
  "Lena Fischer", "2025-11-15", ["EV-AWS-SOC2"])
A("HL-DCS-04", ["DCS"], "environmental control systems utility services datacenter",
  "Yes", "Not applicable to Harbourline-operated facilities — environmental and utility controls for compute facilities are provided and attested by AWS under the shared responsibility model.",
  "Priya Nair", "2026-04-01", ["EV-AWS-SOC2"])
A("HL-DCS-05", ["DCS"], "asset catalog tracked physical logical assets",
  "Yes", "All corporate assets (laptops, monitors, mobile devices) are cataloged in Jamf Pro and the IT asset register; cloud assets are inventoried via AWS Config. The inventory is reconciled quarterly.",
  "Lena Fischer", "2026-11-01", ["EV-JAMF-COMPLIANCE"])
A("HL-DCS-06", ["DCS"], "surveillance datacenter personnel trained unauthorized access",
  "Yes", "Office entry points have badge readers with audit logs reviewed on incident; AWS datacenter surveillance and personnel controls are inherited under the shared responsibility model.",
  "Lena Fischer", "2025-11-15", ["EV-AWS-SOC2"])

# ============================ DSP ============================
A("HL-DSP-01", ["DSP"], "data security privacy policies procedures established documented approved communicated enforced evaluated maintained",
  "Yes", "The Data Protection and Privacy Policy (v2.1) governs the full data lifecycle — collection, use, retention, and deletion — for customer and personal data. It is approved by Privacy Counsel, communicated at onboarding, and reviewed annually.",
  "Marcus Webb", "2026-03-10", ["EV-POLICY-DATA"])
A("HL-DSP-02", ["DSP"], "data inventory sensitive personal information created maintained",
  "Yes", "A data inventory catalogs personal and sensitive data stores (application databases, analytics warehouse, support tooling) with data types, locations, and retention periods. It is maintained by Privacy Counsel and reviewed annually.",
  "Marcus Webb", "2026-07-15", ["EV-DATAFLOW"])
A("HL-DSP-03", ["DSP"], "data classified type sensitivity levels classification scheme",
  "Yes", "Data is classified as Public, Internal, Confidential, or Restricted per the classification scheme in the Data Protection Policy. Customer production data defaults to Confidential; credentials and keys are Restricted.",
  "Marcus Webb", "2026-03-10", ["EV-POLICY-DATA"])
A("HL-DSP-04", ["DSP"], "data flow documentation created identify processed stored transmitted reviewed",
  "Yes", "Data flow diagrams document what customer data is processed, where it is stored, and which subprocessors are involved. They are reviewed at least annually and after material architecture changes; last review 2026-07-15.",
  "Daniel Okafor", "2026-07-15", ["EV-DATAFLOW"])
A("HL-DSP-05", ["DSP"], "data protection impact assessment DPIA conducted personal data",
  "Yes", "DPIAs are conducted for new processing of personal data and material changes. The 2026 DPIA for the analytics pipeline v2 covered lawful basis, data minimization, retention, and subprocessor review, with all actions closed.",
  "Marcus Webb", "2026-08-01", ["EV-DPIA-2026"])
A("HL-DSP-06", ["DSP"], "data retention archiving deletion practices business requirements legal",
  "Yes", "Retention schedules are defined per data category (e.g., customer data retained for the contract term plus 90 days, logs 13 months) and enforced by automated lifecycle rules. Deletion requests are actioned within 30 days.",
  "Marcus Webb", "2026-03-10", ["EV-POLICY-DATA"])
A("HL-DSP-07", ["DSP"], "manage respond requests data subjects DSR procedure rights",
  "Yes", "Data subject requests (access, correction, deletion, portability) are handled through a documented DSR procedure owned by Privacy Counsel, with a 30-day response SLA. Three requests were processed in 2026, all within SLA.",
  "Marcus Webb", "2026-09-01", ["EV-POLICY-DATA"])
A("HL-DSP-08", ["DSP"], "secure data disposal storage media information irretrievable",
  "Yes", "Electronic media is sanitized per media type before disposal or reuse; paper containing personal data is cross-shredded. Cloud media sanitization is inherited from AWS; corporate devices go through the ITAD process with certificates of destruction.",
  "Lena Fischer", "2026-06-01", ["EV-JAMF-COMPLIANCE", "EV-AWS-SOC2"])

# ============================ GRC ============================
A("HL-GRC-01", ["GRC"], "information governance program policies procedures sponsored leadership",
  "Yes", "The information governance program is sponsored by the CEO and run by the CISO, covering all CCM-relevant domains. Program status is reported to leadership quarterly and the policy set is reviewed annually.",
  "Priya Nair", "2026-03-10", ["EV-POLICY-INFOSEC", "EV-RISK-REGISTER"])
A("HL-GRC-02", ["GRC"], "enterprise risk management formal documented leadership sponsored",
  "Yes", "A formal risk management program is documented in the Information Security Policy: risks are identified, assessed, and tracked in a quarterly-reviewed risk register with assigned owners and treatment plans.",
  "Priya Nair", "2026-09-30", ["EV-RISK-REGISTER"])
A("HL-GRC-03", ["GRC"], "exception process approved governance policy exception risk acceptance",
  "Yes", "Policy exceptions require a documented risk acceptance signed by the CISO with compensating controls and an expiry date (max 12 months). Exceptions are tracked in the GRC register and re-evaluated at expiry.",
  "Priya Nair", "2026-03-10", ["EV-POLICY-INFOSEC", "EV-RISK-REGISTER"])
A("HL-GRC-04", ["GRC"], "standards regulations legal contractual statutory requirements identified",
  "Yes", "Applicable requirements (SOC 2, PIPEDA, customer contractual security clauses) are identified in the compliance register and mapped to controls. New regulations are assessed by Privacy Counsel and the CISO as they emerge.",
  "Marcus Webb", "2026-09-30", ["EV-SOC2-2026", "EV-RISK-REGISTER"])

# ============================ HRS ============================
A("HL-HRS-01", ["HRS"], "background verification new employees policies procedures local laws",
  "Yes", "Background verification (identity, employment history, education; criminal check where permitted by Ontario law) is completed for all new hires before their start date, administered through a third-party provider.",
  "Aisha Bello", "2026-01-15", ["EV-TRAINING-2026"])
A("HL-HRS-02", ["HRS"], "acceptable use organizationally owned assets allowances conditions",
  "Yes", "The Acceptable Use Policy defines permitted use of company devices, data, and networks, including prohibitions on unauthorized software and data exfiltration. All employees acknowledge it at onboarding.",
  "Lena Fischer", "2025-12-01", ["EV-POLICY-REMOTE"])
A("HL-HRS-03", ["HRS"], "unattended workspaces conceal confidential data clean desk screen lock",
  "Yes", "The clean-desk and clear-screen policy requires locking devices when unattended (auto-lock enforced via Jamf at 5 minutes) and securing confidential documents. It is covered in onboarding and annual training.",
  "Aisha Bello", "2026-10-25", ["EV-TRAINING-2026", "EV-JAMF-COMPLIANCE"])
A("HL-HRS-04", ["HRS"], "protect information accessed processed stored remote sites telework",
  "Yes", "Remote work requirements (encrypted devices, VPN for admin access, no public Wi-Fi without VPN, physical security of devices) are defined in the Remote Work Policy and enforced through Jamf and Okta device trust.",
  "Lena Fischer", "2025-12-01", ["EV-POLICY-REMOTE", "EV-JAMF-COMPLIANCE"])
A("HL-HRS-05", ["HRS"], "return procedures organizationally owned assets terminated employees offboarding",
  "Yes", "Offboarding revokes all access within 24 hours of termination via the Okta-integrated checklist, and company assets must be returned within 5 business days. Asset return is tracked in the IT ticket system.",
  "Lena Fischer", "2026-10-10", ["EV-ACCESS-REVIEW-Q3"])
A("HL-HRS-06", ["HRS"], "employment agreement signed access organizational assets NDA confidentiality",
  "Yes", "Every employee signs an employment agreement with confidentiality and IP assignment clauses before receiving system access. Contractors sign equivalent agreements through the contracting process.",
  "Aisha Bello", "2026-01-15", ["EV-TRAINING-2026"])
A("HL-HRS-07", ["HRS"], "security awareness training program established documented regular updates phishing",
  "Yes", "All employees complete security awareness training at onboarding and annually, plus quarterly phishing simulations. Completion is tracked; the 2026 cycle reached 100% completion and phishing click-through fell to 4%.",
  "Aisha Bello", "2026-10-25", ["EV-TRAINING-2026"])

# ============================ IAM ============================
A("HL-IAM-01", ["IAM"], "identity access management policies procedures established documented approved",
  "Yes", "Identity and access management requirements are defined in the Information Security Policy: centralized identity via Okta, role-based access, and quarterly access reviews. The policy is reviewed annually.",
  "Priya Nair", "2026-03-10", ["EV-POLICY-INFOSEC"])
A("HL-IAM-02", ["IAM"], "strong password policies procedures MFA multi-factor authentication",
  "Yes", "Passwords must meet complexity and length requirements enforced by Okta; MFA is mandatory for all users on all applications, using authenticator apps or hardware keys. Passwordless options are being piloted for engineering.",
  "Lena Fischer", "2026-10-10", ["EV-ACCESS-REVIEW-Q3"])
A("HL-IAM-03", ["IAM"], "user access provisioning process authorizes records communicates",
  "Yes", "Access provisioning follows a documented joiner process: HR triggers Okta onboarding, managers approve role-based app assignments, and every grant is logged. Privileged access requires CISO or delegate approval.",
  "Lena Fischer", "2026-10-10", ["EV-ACCESS-REVIEW-Q3"])
A("HL-IAM-04", ["IAM"], "de-provision modify access timely manner movers leavers termination",
  "Yes", "Access is deprovisioned automatically via Okta lifecycle management: HRIS termination triggers revocation of all SSO sessions and app access within 24 hours; shared credentials are rotated immediately.",
  "Lena Fischer", "2026-10-10", ["EV-ACCESS-REVIEW-Q3"])
A("HL-IAM-05", ["IAM"], "reviews revalidation user access least privilege separation duties quarterly",
  "Yes", "User access is reviewed quarterly by application owners against least-privilege and separation-of-duties rules; the Q3 2026 review covered all production systems and resulted in 14 access removals.",
  "Lena Fischer", "2026-10-10", ["EV-ACCESS-REVIEW-Q3"])
A("HL-IAM-06", ["IAM"], "privileged access roles segregation granted managed break glass",
  "Yes", "Privileged access is segregated from standard accounts: administrators use separate privileged accounts with MFA, session recording for production access, and just-in-time elevation for break-glass scenarios.",
  "Daniel Okafor", "2026-10-10", ["EV-ACCESS-REVIEW-Q3"])
A("HL-IAM-07", ["IAM"], "least privilege principle separation duties employed access",
  "Yes", "Least privilege is enforced through role-based access profiles in Okta and AWS IAM; separation of duties is applied to financial and deployment approvals (e.g., the person deploying cannot approve their own change).",
  "Sam Reyes", "2026-06-01", ["EV-POLICY-CHANGE"])
A("HL-IAM-08", ["IAM"], "authenticate access systems applications digital certificates system identities",
  "Yes", "Human access to systems requires SSO with MFA; service-to-service authentication uses short-lived tokens and mutual TLS with certificates managed by AWS ACM. Shared service accounts are prohibited for human use.",
  "Daniel Okafor", "2026-09-15", ["EV-CRYPTO-INVENTORY"])

# ============================ IPY ============================
A("HL-IPY-01", ["IPY"], "programmatically retrieve data application interface export portability",
  "Yes", "Customers can export their data at any time via the REST API and CSV export in the product UI. Export formats are documented in the developer docs.",
  "Sam Reyes", "2026-07-01", ["EV-POLICY-DATA"])
A("HL-IPY-02", ["IPY"], "cryptographically secure standardized network protocols management migration",
  "Yes", "All management and data interfaces use TLS 1.2+ with standard protocols (HTTPS REST APIs); legacy or insecure protocols are disabled at the load balancer.",
  "Daniel Okafor", "2026-09-15", ["EV-CRYPTO-INVENTORY"])
A("HL-IPY-03", ["IPY"], "agreements provisions data access contract termination",
  "Yes", "Customer agreements include a 90-day post-termination data retrieval window and assisted export on request, after which data is deleted per the retention schedule.",
  "Marcus Webb", "2026-09-01", ["EV-POLICY-DATA", "EV-SUBPROCESSORS"])

# ============================ IVS ============================
A("HL-IVS-01", ["IVS"], "infrastructure virtualization security policies procedures network segmentation",
  "Yes", "Infrastructure security requirements (VPC design, security groups, network segmentation) are defined in the infrastructure baseline. Production, staging, and development run in separate AWS accounts with no cross-account trust except the deployment pipeline.",
  "Sam Reyes", "2026-06-01", ["EV-POLICY-INFOSEC"])
A("HL-IVS-02", ["IVS"], "communications environments monitored encrypted authenticated authorized",
  "Yes", "Inter-service traffic is encrypted with mutual TLS; VPC flow logs and security group change logs are collected centrally. Network configurations are reviewed annually and on architecture change.",
  "Daniel Okafor", "2026-10-20", ["EV-DATADOG-LOGS"])
A("HL-IVS-03", ["IVS"], "host guest OS hypervisor hardened according baselines",
  "Yes", "Container base images are minimal and scanned; EC2-equivalent hosts are AWS-managed (Fargate/RDS) so hypervisor hardening is inherited from AWS. CIS-benchmark-aligned hardening is applied to the images we build.",
  "Sam Reyes", "2026-09-01", ["EV-VULNSCAN-Q3", "EV-AWS-SOC2"])
A("HL-IVS-04", ["IVS"], "production non-production environments separated",
  "Yes", "Production and non-production environments are fully separated: distinct AWS accounts, networks, data, and access roles. Production data is never used in lower environments; staging uses synthetic data.",
  "Sam Reyes", "2026-06-01", ["EV-POLICY-INFOSEC"])
A("HL-IVS-05", ["IVS"], "secure encrypted communication channels up-to-date approved protocols",
  "Yes", "Only TLS 1.2+ with approved cipher suites is permitted for service communication; deprecated protocols are blocked at the load balancer and verified by quarterly external scans.",
  "Daniel Okafor", "2026-09-02", ["EV-PENTEST-2026"])

# ============================ LOG ============================
A("HL-LOG-01", ["LOG"], "logging monitoring policies procedures established documented approved",
  "Yes", "Logging and monitoring requirements are defined in the Information Security Policy: what is logged, centralized collection, 13-month retention, and restricted access. The policy is reviewed annually.",
  "Daniel Okafor", "2026-03-10", ["EV-POLICY-INFOSEC"])
A("HL-LOG-02", ["LOG"], "security-related events identified monitored applications infrastructure alerts stakeholders",
  "Yes", "Security-relevant events (authentication failures, privilege escalation, WAF blocks, anomalous API usage) are monitored in Datadog with alerts routed to the on-call security engineer via PagerDuty.",
  "Daniel Okafor", "2026-10-20", ["EV-DATADOG-LOGS"])
A("HL-LOG-03", ["LOG"], "access audit logs restricted authorized personnel records maintained",
  "Yes", "Audit logs are immutable (WORM S3 bucket) and access is restricted to the security and platform teams; every access to audit logs is itself logged.",
  "Daniel Okafor", "2026-10-20", ["EV-DATADOG-LOGS"])
A("HL-LOG-04", ["LOG"], "reliable time source all relevant information processing systems NTP",
  "Yes", "All systems synchronize to AWS Time Sync Service (NTP) so log timestamps are consistent across the fleet; drift is monitored.",
  "Sam Reyes", "2026-10-20", ["EV-DATADOG-LOGS"])
A("HL-LOG-05", ["LOG"], "audit records generated contain relevant security information protect unauthorized access modification deletion",
  "Yes", "Audit records capture who, what, when, and where for security-relevant actions and are protected from modification via immutable storage with restricted write access.",
  "Daniel Okafor", "2026-10-20", ["EV-DATADOG-LOGS"])
A("HL-LOG-06", ["LOG"], "key lifecycle management events logged monitored auditing reporting cryptographic",
  "Yes", "KMS key lifecycle events (creation, rotation, disable, deletion scheduling) are logged to CloudTrail and alerted to the security team.",
  "Daniel Okafor", "2026-09-15", ["EV-CRYPTO-INVENTORY"])

# ============================ SEF ============================
A("HL-SEF-01", ["SEF"], "security incident management e-discovery cloud forensics policies procedures",
  "Yes", "The Incident Response Plan (v3.2) defines roles, severity levels, escalation paths, and forensics procedures including evidence preservation for cloud workloads. It is reviewed annually.",
  "Daniel Okafor", "2026-07-01", ["EV-IR-PLAN"])
A("HL-SEF-02", ["SEF"], "security incident response plan tested updated effectiveness tabletop",
  "Yes", "The incident response plan is tested annually through a tabletop exercise; the June 2026 exercise simulated a credential-compromise scenario and produced four improvement actions, all closed.",
  "Daniel Okafor", "2026-06-18", ["EV-TABLETOP-2026"])
A("HL-SEF-03", ["SEF"], "security breach notifications defined implemented reported authorities customers",
  "Yes", "Breach notification procedures define assessment, containment, and notification timelines aligned with PIPEDA and contractual obligations (customer notification without unreasonable delay). Contact lists for regulators and law enforcement are maintained in the IR plan.",
  "Priya Nair", "2026-07-01", ["EV-IR-PLAN"])
A("HL-SEF-04", ["SEF"], "incident metrics established monitored triage",
  "Yes", "Incident metrics (time to detect, time to respond, incidents by severity) are tracked and reviewed monthly by the security team. In 2026 there were no Severity-1 incidents.",
  "Daniel Okafor", "2026-10-20", ["EV-DATADOG-LOGS"])
A("HL-SEF-05", ["SEF"], "points of contact regulation authorities law enforcement maintained",
  "Yes", "Points of contact for the Privacy Commissioner of Canada, relevant US authorities for US customers, and Toronto law enforcement are maintained in the incident response plan and verified annually.",
  "Priya Nair", "2026-07-01", ["EV-IR-PLAN"])

# ============================ STA ============================
A("HL-STA-01", ["STA"], "shared security responsibility model SSRM applied documented supply chain",
  "Yes", "Harbourline documents its shared responsibility model: AWS secures the underlying cloud infrastructure; Harbourline secures its applications, data, and configurations. The model is published in the trust center and customer security documentation.",
  "Priya Nair", "2026-04-01", ["EV-AWS-SOC2"])
A("HL-STA-02", ["STA"], "inventory supply chain relationships developed maintained subprocessors",
  "Yes", "An inventory of supply chain relationships and subprocessors (AWS, Okta, Datadog, GitHub, etc.) is maintained by Legal and published in the trust center; it is reviewed whenever a vendor is added or removed.",
  "Marcus Webb", "2026-09-01", ["EV-SUBPROCESSORS"])
A("HL-STA-03", ["STA"], "risk factors supply chain periodically reviewed vendor assessments",
  "Yes", "Vendors with access to customer data undergo a risk assessment before onboarding and annually thereafter, covering SOC 2 reports, security questionnaires, and financial viability. Findings are tracked to closure.",
  "Daniel Okafor", "2026-06-30", ["EV-VENDOR-ASSESS"])
A("HL-STA-04", ["STA"], "supply chain agreements reviewed annually security requirements",
  "Yes", "Vendor agreements include security and confidentiality requirements and are reviewed at least annually; DPAs are in place with all subprocessors processing personal data.",
  "Marcus Webb", "2026-09-01", ["EV-SUBPROCESSORS"])
A("HL-STA-05", ["STA"], "periodic security assessments supply chain organizations defined",
  "Yes", "Critical suppliers are reassessed annually via their SOC 2 reports or a security questionnaire; the H1 2026 assessment pack covered all 12 in-scope vendors with no unresolved high risks.",
  "Daniel Okafor", "2026-06-30", ["EV-VENDOR-ASSESS"])

# ============================ TVM ============================
A("HL-TVM-01", ["TVM"], "threat vulnerability management policies procedures established documented approved",
  "Yes", "Threat and vulnerability management is defined in the Information Security Policy: continuous scanning, risk-based prioritization, and defined remediation SLAs. The program is run by Security Engineering.",
  "Daniel Okafor", "2026-03-10", ["EV-POLICY-INFOSEC"])
A("HL-TVM-02", ["TVM"], "protect against malware managed assets anti-malware",
  "Yes", "Managed endpoints run CrowdStrike Falcon with real-time protection; email attachments and URLs are filtered by Google Workspace security. Malware detections are alerted to the security team.",
  "Lena Fischer", "2026-11-01", ["EV-JAMF-COMPLIANCE"])
A("HL-TVM-03", ["TVM"], "update patches managed assets vulnerability remediation prioritized risk-based",
  "Yes", "Patches are deployed via automated tooling (Jamf for endpoints, CI-built images for services) with SLAs by severity: critical within 15 days, high within 30. Compliance is tracked in the monthly vulnerability report.",
  "Daniel Okafor", "2026-10-15", ["EV-VULNSCAN-Q3"])
A("HL-TVM-04", ["TVM"], "periodically identify vulnerabilities scanning penetration testing",
  "Yes", "Vulnerability scanning runs continuously on infrastructure and weekly on applications; an external penetration test is performed annually. The September 2026 pentest found no critical issues.",
  "Daniel Okafor", "2026-09-02", ["EV-PENTEST-2026", "EV-VULNSCAN-Q3"])
A("HL-TVM-05", ["TVM"], "track report vulnerability identification remediation metrics",
  "Yes", "Vulnerability identification and remediation are tracked in the security backlog with metrics (mean time to remediate by severity) reported monthly to the CISO.",
  "Daniel Okafor", "2026-10-15", ["EV-VULNSCAN-Q3"])
A("HL-TVM-06", ["TVM"], "metrics vulnerability identification remediation established monitored reported",
  "Yes", "Vulnerability metrics — open findings by severity, SLA adherence, and mean time to remediate — are established, monitored in the monthly security report, and reviewed with engineering leadership.",
  "Priya Nair", "2026-10-15", ["EV-VULNSCAN-Q3"])

# ============================ UEM ============================
A("HL-UEM-01", ["UEM"], "endpoint management policies procedures established documented approved",
  "Yes", "Endpoint security requirements are defined in the Information Security Policy and enforced via Jamf Pro: disk encryption, auto-lock, firewall, and approved software only.",
  "Lena Fischer", "2026-03-10", ["EV-POLICY-INFOSEC"])
A("HL-UEM-02", ["UEM"], "inventory endpoints store access company data",
  "Yes", "All company endpoints are enrolled in Jamf Pro at provisioning; the inventory is reconciled monthly and unverified devices are blocked from corporate resources by Okta device trust.",
  "Lena Fischer", "2026-11-01", ["EV-JAMF-COMPLIANCE"])
A("HL-UEM-03", ["UEM"], "information protected unauthorized disclosure managed endpoints storage encryption",
  "Yes", "Full-disk encryption (FileVault/BitLocker) is enforced on all managed endpoints via Jamf; removable media is blocked by policy on devices handling customer data.",
  "Lena Fischer", "2026-11-01", ["EV-JAMF-COMPLIANCE"])
A("HL-UEM-04", ["UEM"], "interactive-use endpoints automatic lock screen",
  "Yes", "Automatic lock screen is enforced at 5 minutes of inactivity on all managed endpoints via Jamf configuration profiles.",
  "Lena Fischer", "2026-11-01", ["EV-JAMF-COMPLIANCE"])
A("HL-UEM-05", ["UEM"], "endpoint operating systems patch levels applications managed change",
  "Yes", "OS and application patches on endpoints are managed through Jamf with staged rollout rings; critical patches are pushed within 7 days. Compliance was 98% at the November 2026 check.",
  "Lena Fischer", "2026-11-01", ["EV-JAMF-COMPLIANCE"])


def build() -> dict:
    return {
        "company": COMPANY,
        "replay_date": REPLAY_DATE,
        "freshness_policy": {
            "answer_stale_after_days": 180,
            "evidence_stale_after_days": 365,
            "note": "Answers not reviewed within 180 days of the replay date route to REVERIFY even when the match is strong.",
        },
        "evidence": EVIDENCE,
        "answers": ANSWERS,
    }


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "data" / "raw" / "answer_library.json"
    payload = build()
    out.write_text(json.dumps(payload, indent=1))
    n_ans = len(payload["answers"])
    n_ev = len(payload["evidence"])
    stale = sum(1 for a in payload["answers"] if a["last_reviewed"] < "2026-05-08")
    print(f"wrote {out}: {n_ans} answers, {n_ev} evidence artifacts ({stale} stale answers by 180-day rule)")


if __name__ == "__main__":
    main()
