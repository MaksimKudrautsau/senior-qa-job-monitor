import re


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
]

SENIOR_PATTERNS = [
    r"\bsenior\b",
    r"\bsr\.?\b",
    r"\bstaff\b",
    r"\blead\b",
    r"\bprincipal\b",
]

EXCLUDE_PATTERNS = [
    r"\bsearch quality\b",
    r"\bdata quality\b",
    r"\bprogram manager\b",
    r"\bmanager\b",
    r"\banalyst\b",
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

BAY_AREA_LOCATIONS = [
    "san francisco",
    "bay area",
    "oakland",
    "hayward",
    "fremont",
    "san jose",
    "mountain view",
    "palo alto",
    "sunnyvale",
    "redwood city",
    "menlo park",
    "santa clara",
    "berkeley",
    "san mateo",
    "burlingame",
    "milpitas",
    "cupertino",
    "south san francisco",
    "emeryville",
    "alameda",
    "dublin",
    "pleasanton",
    "san ramon",
]


def matches_any_pattern(text, patterns):
    return any(re.search(pattern, text) for pattern in patterns)


def is_senior_qa_job(job):
    title = job.get("title", "").lower()
    location = job.get("location", "").lower()

    has_qa_in_title = matches_any_pattern(title, QA_TITLE_PATTERNS)
    has_senior_in_title = matches_any_pattern(title, SENIOR_PATTERNS)
    is_excluded = matches_any_pattern(title, EXCLUDE_PATTERNS)
    location_match = any(city in location for city in BAY_AREA_LOCATIONS)

    return (
        has_qa_in_title
        and has_senior_in_title
        and location_match
        and not is_excluded
    )