"""
Job matching for the senior-QA monitor.

Additive scoring model: each signal contributes points and a job is notified
when its score reaches NOTIFY_THRESHOLD.

Design note: a QA term must appear in the TITLE for a job to qualify at all.
An earlier version also accepted a QA mention in the description, but generic
engineering posts ("partner with the QA team", "write tests") tripped that and
produced false positives like "Senior Python Engineer". Role type is reliably
in the title; description is not used as a qualifier.

Expected job fields: title, location.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

QA_TITLE_PATTERNS = [
    r"\bqa\b",
    r"\bquality assurance\b",
    r"\bsdet\b",
    r"\btest automation\b",
    r"\bqa automation\b",
    r"\bquality engineer\b",
    r"\btest engineer\b",
    r"\btesting engineer\b",
    r"\bsoftware engineer in test\b",
    r"\bsoftware development engineer in test\b",
    r"\bquality analyst\b"
]

SENIOR_PATTERNS = [
    r"\bsenior\b",
    r"\bsr\.?\b",
    r"\bstaff\b",
    r"\blead\b",
    r"\bprincipal\b",
]

# Title tokens that disqualify a posting outright (hard veto). Note:
# \banalyst\b drops "QA Analyst" roles -- remove it if you want those.
EXCLUDE_PATTERNS = [
    r"\bsearch quality\b",
    r"\bdata quality\b",
    r"\bprogram manager\b",
    r"\bmanager\b",
    r"\bassociate\b",
    r"\brecruiting\b",
    r"\bpeople analytics\b",
    r"\bcompliance\b",
    r"\bcredit\b",
    r"\bcollections\b",
    r"\bmachine learning\b",
    r"\bml engineer\b",
    r"\bmobile platform\b",
]

REMOTE_PATTERNS = [
    r"\bremote\b",
    r"\banywhere\b",
    r"\bus[- ]remote\b",
    r"\bremote[- ]us\b",
]

BAY_AREA_LOCATIONS = [
    "san francisco", "bay area", "oakland", "hayward", "fremont",
    "san jose", "mountain view", "palo alto", "sunnyvale", "redwood city",
    "menlo park", "santa clara", "berkeley", "san mateo", "burlingame",
    "milpitas", "cupertino", "south san francisco", "emeryville",
    "alameda", "dublin", "pleasanton", "san ramon", "sf bay",
]

# --- scoring weights (tune here) --------------------------------------------
W_QA_TITLE = 3
W_SENIOR_TITLE = 2
W_LOC_BAY = 2
W_LOC_REMOTE = 1
W_LOC_UNKNOWN = 0      # empty location -> neutral, do NOT punish
W_LOC_OTHER = -1       # named location, clearly not bay/remote -> small penalty

NOTIFY_THRESHOLD = 5   # raise to 6-7 for stricter, lower to 4 for wider reach


def _matches(text: str, patterns) -> bool:
    return any(re.search(p, text) for p in patterns)


@dataclass
class JobScore:
    score: int
    matched: bool
    confidence: str
    reasons: list = field(default_factory=list)


def score_job(job) -> JobScore:
    """Score a single job dict. Returns a JobScore; .matched drives notify."""
    title = (job.get("title") or "").lower()
    location = (job.get("location") or "").strip().lower()

    # Hard veto: excluded title tokens (manager, analyst, ...).
    if _matches(title, EXCLUDE_PATTERNS):
        return JobScore(0, False, "none", ["excluded title token"])

    # Hard requirement: must be a QA role BY TITLE.
    if not _matches(title, QA_TITLE_PATTERNS):
        return JobScore(0, False, "none", ["no QA signal in title"])

    score = W_QA_TITLE
    reasons = ["qa:title"]

    if _matches(title, SENIOR_PATTERNS):
        score += W_SENIOR_TITLE
        reasons.append("senior:title")

    # Location is a soft signal, not a gate.
    if not location:
        score += W_LOC_UNKNOWN
        reasons.append("loc:unknown")
    elif any(city in location for city in BAY_AREA_LOCATIONS):
        score += W_LOC_BAY
        reasons.append("loc:bay")
    elif _matches(location, REMOTE_PATTERNS):
        score += W_LOC_REMOTE
        reasons.append("loc:remote")
    else:
        score += W_LOC_OTHER
        reasons.append("loc:other")

    matched = score >= NOTIFY_THRESHOLD
    confidence = "high" if score >= 7 else "medium" if score >= 5 else "low"
    return JobScore(score, matched, confidence, reasons)


def is_senior_qa_job(job) -> bool:
    """Backwards-compatible boolean wrapper around score_job()."""
    return score_job(job).matched