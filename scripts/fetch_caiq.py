#!/usr/bin/env python3
"""One-time extraction of the CAIQ v4.0.2 question bank.

Source: the AWS-completed CSA CAIQ v4.0.2 questionnaire (public PDF),
which carries the full canonical CAIQ question set (Question ID + Question
text per row). Only the questionnaire text is extracted — none of AWS's
responses are bundled; the response library for the demo company is
seeded separately in data/raw/answer_library.json and is clearly
labeled as seeded.

The CAIQ itself is published by the Cloud Security Alliance and is
free to use for vendor security assessments.
"""
import json
import re
import sys
from pathlib import Path

PDF_URL = "https://d1.awsstatic.com/whitepapers/compliance/CSA_Consensus_Assessments_Initiative_Questionnaire.pdf"
OUT = Path(__file__).resolve().parent.parent / "data" / "raw" / "caiq_v402.json"

DOMAINS = {
    "A&A": "Audit Assurance & Compliance",
    "AIS": "Application & Interface Security",
    "BCR": "Business Continuity Management & Operational Resilience",
    "CCC": "Change Control & Configuration Management",
    "CEK": "Cryptography, Encryption & Key Management",
    "DCS": "Datacenter Security",
    "DSP": "Data Security & Privacy Lifecycle Management",
    "GRC": "Governance, Risk & Compliance",
    "HRS": "Human Resources",
    "IAM": "Identity & Access Management",
    "IPY": "Interoperability & Portability",
    "IVS": "Infrastructure & Virtualization Security",
    "LOG": "Logging & Monitoring",
    "SEF": "Security Incident Management, E-Discovery & Cloud Forensics",
    "STA": "Supply Chain Management, Transparency & Accountability",
    "TVM": "Threat & Vulnerability Management",
    "UEM": "Unified Endpoint Management",
}

# The PDF is a borderless two-column table: question text on the left,
# Yes/No + ownership + the responder's answer on the right. The answer
# column starts at x=171, so cropping the page to x<=168 isolates the
# question column (Question ID + full wrapped question text) and rows
# can be split on the ID at line start — no answer-column parsing needed.
LEFT_COLUMN_X = 168
QID_LINE_RE = re.compile(r"^([A-Z&]{2,4}-\d{2}\.\d{1,2})\s", re.M)


def extract_questions(pdf_path) -> list[dict]:
    import pdfplumber

    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            left = page.crop((0, 0, LEFT_COLUMN_X, page.height))
            full_text += "\n" + (left.extract_text() or "")

    questions: list[dict] = []
    for chunk in re.split(r"(?m)^(?=[A-Z&]{2,4}-\d{2}\.\d{1,2}\s)", full_text):
        m = QID_LINE_RE.match(chunk)
        if not m:
            continue
        qid = m.group(1)
        domain = qid.split("-")[0]
        question = re.sub(r"\s+", " ", chunk[m.end() :]).strip()
        if domain in DOMAINS and question:
            questions.append(
                {
                    "id": qid,
                    "domain": domain,
                    "domain_name": DOMAINS[domain],
                    "question": question,
                }
            )
    return questions


def main() -> None:
    try:
        import pdfplumber
    except ImportError:
        sys.exit("pdfplumber required: pip install -r requirements.txt")

    pdf_path = Path("/tmp/caiq_v402.pdf")
    if not pdf_path.exists():
        import urllib.request

        print(f"downloading {PDF_URL} ...")
        urllib.request.urlretrieve(PDF_URL, pdf_path)

    full_text = ""
    questions = extract_questions(pdf_path)
    # dedupe by id, keep first occurrence
    seen, deduped = set(), []
    for q in questions:
        if q["id"] not in seen:
            seen.add(q["id"])
            deduped.append(q)

    payload = {
        "source": "CSA CAIQ v4.0.2 (via AWS-completed public PDF; questions only, no AWS responses)",
        "url": PDF_URL,
        "license_note": "CAIQ is published by the Cloud Security Alliance and is free to use for vendor security assessments.",
        "question_count": len(deduped),
        "domains": DOMAINS,
        "questions": deduped,
    }
    OUT.write_text(json.dumps(payload, indent=1))
    print(f"wrote {OUT}: {len(deduped)} questions")


if __name__ == "__main__":
    main()
