from db import init_db, job_exists, save_job
from sources.greenhouse import fetch_greenhouse_jobs
from sources.lever import fetch_lever_jobs
from filters import is_senior_qa_job
from telegram_bot import send_telegram_message
from sources.ashby import fetch_ashby_jobs
from sources.apify_jobs import fetch_apify_jobs
import re


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


def main():
    init_db()

    greenhouse_jobs = fetch_greenhouse_jobs()
    lever_jobs = fetch_lever_jobs()
    ashby_jobs = fetch_ashby_jobs()
    apify_jobs = fetch_apify_jobs()
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
            r"\bsoftware engineer in test\b",
        ])
    ]

    print(f"Possible QA jobs anywhere: {len(possible_qa_jobs)}")

    for job in possible_qa_jobs[:50]:
        print(job["title"], "|", job["company"], "|", job["location"], "|", job["source"])

    matched_jobs = [job for job in jobs if is_senior_qa_job(job)]

    print(f"Greenhouse jobs: {len(greenhouse_jobs)}")
    print(f"Lever jobs: {len(lever_jobs)}")
    print(f"Ashby jobs: {len(ashby_jobs)}")
    print(f"Fetched {len(jobs)} jobs")
    print(f"Matched {len(matched_jobs)} jobs")
    print(f"Apify jobs: {len(apify_jobs)}")

    new_jobs_count = 0

    for job in matched_jobs:
        if not job_exists(job["url"]):
            save_job(job["url"], job["title"], job["company"])
            send_telegram_message(format_job_message(job))
            new_jobs_count += 1
            print(f"Sent: {job['title']} | {job['company']}")

    print(f"New jobs sent: {new_jobs_count}")


if __name__ == "__main__":
    main()