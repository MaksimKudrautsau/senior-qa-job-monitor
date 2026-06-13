import os
import datetime
from urllib.parse import urlsplit, urlunsplit

from db import init_db, job_exists, save_job
from sources.greenhouse import fetch_greenhouse_jobs
from sources.lever import fetch_lever_jobs
from sources.ashby import fetch_ashby_jobs
from sources.apify_jobs import fetch_apify_jobs
from filters import score_job, NOTIFY_THRESHOLD
from telegram_bot import send_telegram_message

# Send the "ran" summary at most ~once/day at this UTC hour, PLUS whenever there
# are new jobs or a source problem. Avoids ~48 noise messages/day that train you
# to mute the channel.
DAILY_DIGEST_HOUR_UTC = 16


def normalize_url(url: str) -> str:
    """Stable dedup key: drop query/fragment and trailing slash, lowercase host.

    Prevents the same posting being treated as new when it gains a tracking
    param (e.g. ?gh_src=...) or a trailing slash.
    """
    if not url:
        return url
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc.lower(),
                       parts.path.rstrip("/"), "", ""))


def fetch_sources(run_apify: bool):
    """Fetch every source independently. One failing source must never zero out
    the whole run, and a failure must be visibly different from 'no jobs'."""
    sources = [
        ("Greenhouse", fetch_greenhouse_jobs),
        ("Lever", fetch_lever_jobs),
        ("Ashby", fetch_ashby_jobs),
    ]
    if run_apify:
        sources.append(("Apify", fetch_apify_jobs))
    else:
        print("Skipping Apify for this run")

    jobs = []
    health = []  # list of (name, count, error_or_None)
    for name, fetch in sources:
        try:
            fetched = fetch() or []
            jobs.extend(fetched)
            health.append((name, len(fetched), None))
        except Exception as exc:  # noqa: BLE001 - surface, don't swallow silently
            health.append((name, 0, repr(exc)))
            print(f"[ERROR] {name} fetch failed: {exc!r}")
    return jobs, health


def format_job_message(job, score):
    posted = job.get("posted_date") or "Unknown"
    salary = job.get("salary") or "N/A"
    return f"""
🚨 New Senior QA Job  ({score.confidence}, score {score.score})

Title: {job['title']}
Company: {job['company']}
Location: {job.get('location') or 'Unknown'}
Posted: {posted}
Salary: {salary}
Source: {job.get('source') or 'Unknown'}

{job['url']}
""".strip()


def format_run_summary(health, total, matched, new_count, run_apify):
    lines = ["✅ Job monitor ran", ""]
    for name, count, error in health:
        if error:
            lines.append(f"⚠️ {name}: ERROR ({error[:80]})")
        elif count == 0:
            lines.append(f"⚠️ {name}: 0 (check source)")
        else:
            lines.append(f"{name}: {count}")
    lines += [
        "",
        f"Total fetched: {total}",
        f"Matched: {matched}",
        f"New sent: {new_count}",
        f"Apify enabled: {run_apify}",
    ]
    return "\n".join(lines)


def should_send_summary(new_count, health, now=None) -> bool:
    """Quiet by default; speak up only when there is something to say."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    has_error = any(error for _, _, error in health)
    suspicious_zero = any(count == 0 and error is None for _, count, error in health)
    is_digest = now.hour == DAILY_DIGEST_HOUR_UTC and now.minute < 30
    return new_count > 0 or has_error or suspicious_zero or is_digest


def main():
    init_db()
    run_apify = os.getenv("RUN_APIFY", "false").lower() == "true"

    jobs, health = fetch_sources(run_apify)

    # Per-source visibility in the Actions log.
    for name, count, error in health:
        print(f"{name}: {count}" + (f"  ERROR={error}" if error else ""))
    print(f"Fetched {len(jobs)} jobs total")

    scored = [(job, score_job(job)) for job in jobs]
    matched = [(job, s) for job, s in scored if s.matched]
    print(f"Matched {len(matched)} jobs")

    # Near-misses help you tune the threshold/weights from the log.
    near = [
        (job, s) for job, s in scored
        if not s.matched and 0 < s.score >= NOTIFY_THRESHOLD - 1
    ]
    for job, s in near[:20]:
        print(f"[near-miss score={s.score}] {job.get('title')} | "
              f"{job.get('location')} | {s.reasons}")

    new_count = 0
    for job, s in matched:
        key = normalize_url(job["url"])
        if not job_exists(key):
            save_job(key, job["title"], job["company"])
            send_telegram_message(format_job_message(job, s))
            new_count += 1
            print(f"Sent: {job['title']} | {job['company']} (score={s.score})")

    print(f"New jobs sent: {new_count}")

    if should_send_summary(new_count, health):
        send_telegram_message(
            format_run_summary(health, len(jobs), len(matched), new_count, run_apify)
        )
    else:
        print("Quiet run - summary suppressed")


if __name__ == "__main__":
    main()