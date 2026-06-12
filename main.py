import os
import re

from db import init_db, job_exists, save_job
from sources.greenhouse import fetch_greenhouse_jobs
from sources.lever import fetch_lever_jobs
from sources.ashby import fetch_ashby_jobs
from sources.apify_jobs import fetch_apify_jobs
from filters import is_senior_qa_job
from telegram_bot import send_telegram_message


def format_job_message(job):
    posted_date = job.get("posted_date") or "Unknown"
    salary = job.get("salary") or "N/A"

    return f"""
🚨 New Senior QA Job

Title: {job["title"]}
Company: {job["company"]}
Location: {job["location"]}
Posted: {posted_date}
Salary: {salary}
Source: {job["source"]}

{job["url"]}
""".strip()


def format_run_summary(
    greenhouse_count,
    lever_count,
    ashby_count,
    apify_count,
    total_count,
    matched_count,
    new_jobs_count,
    run_apify,
):
    return f"""
✅ Job monitor ran

Greenhouse jobs: {greenhouse_count}
Lever jobs: {lever_count}
Ashby jobs: {ashby_count}
Apify jobs: {apify_count}
Total fetched: {total_count}
Matched jobs: {matched_count}
New jobs sent: {new_jobs_count}
Apify enabled: {run_apify}
""".strip()


def main():
    init_db()

    run_apify = os.getenv("RUN_APIFY", "false").lower() == "true"

    greenhouse_jobs = fetch_greenhouse_jobs()
    lever_jobs = fetch_lever_jobs()
    ashby_jobs = fetch_ashby_jobs()

    if run_apify:
        apify_jobs = fetch_apify_jobs()
    else:
        print("Skipping Apify for this run")
        apify_jobs = []

    jobs = greenhouse_jobs + lever_jobs + ashby_jobs + apify_jobs

    possible_qa_jobs = [
        job for job in jobs
        if any(re.search(pattern, job["title"].lower()) for pattern in [
            r"\bqa\b",
            r"\bquality assurance\b",
            r"\bsdet\b",
            r"\btest automation\b",
            r"\bquality engineer\b",
            r"\btest engineer\b",
            r"\bsoftware test engineer\b",
            r"\bsoftware engineer in test\b",
        ])
    ]

    print(f"Possible QA jobs anywhere: {len(possible_qa_jobs)}")

    for job in possible_qa_jobs[:50]:
        print(
            job["title"],
            "|",
            job["company"],
            "|",
            job["location"],
            "|",
            job["source"],
        )

    matched_jobs = [job for job in jobs if is_senior_qa_job(job)]

    print(f"Greenhouse jobs: {len(greenhouse_jobs)}")
    print(f"Lever jobs: {len(lever_jobs)}")
    print(f"Ashby jobs: {len(ashby_jobs)}")
    print(f"Apify jobs: {len(apify_jobs)}")
    print(f"Fetched {len(jobs)} jobs")
    print(f"Matched {len(matched_jobs)} jobs")

    new_jobs_count = 0

    for job in matched_jobs:
        if not job_exists(job["url"]):
            save_job(job["url"], job["title"], job["company"])
            send_telegram_message(format_job_message(job))
            new_jobs_count += 1
            print(f"Sent: {job['title']} | {job['company']}")

    print(f"New jobs sent: {new_jobs_count}")

    summary_message = format_run_summary(
        greenhouse_count=len(greenhouse_jobs),
        lever_count=len(lever_jobs),
        ashby_count=len(ashby_jobs),
        apify_count=len(apify_jobs),
        total_count=len(jobs),
        matched_count=len(matched_jobs),
        new_jobs_count=new_jobs_count,
        run_apify=run_apify,
    )

    send_telegram_message(summary_message)


if __name__ == "__main__":
    main()