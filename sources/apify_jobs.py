import os
import requests


# Replace this with your exact Apify actor ID.
# Example format: "username/google-jobs-scraper"
APIFY_ACTOR_ID = "orgupdate/google-jobs-scraper"


APIFY_SEARCHES = [
    "Senior QA Engineer",
    "Senior QA Automation",
    "SDET"
]


def normalize_apify_job(item):
    title = (
        item.get("job_title")
        or item.get("title")
        or item.get("jobTitle")
        or item.get("position")
        or ""
    )

    company = (
        item.get("company_name")
        or item.get("companyName")
        or item.get("company")
        or item.get("organization")
        or ""
    )

    location = (
        item.get("location")
        or item.get("jobLocation")
        or item.get("place")
        or ""
    )

    url = (
        item.get("URL")
        or item.get("jobUrl")
        or item.get("url")
        or item.get("link")
        or item.get("applyUrl")
        or ""
    )

    description = (
        item.get("description")
        or item.get("jobDescription")
        or item.get("snippet")
        or ""
    )

    posted_date = (
        item.get("date")
        or item.get("postedAt")
        or item.get("posted_date")
        or ""
    )

    posted_via = (
        item.get("posted_via")
        or item.get("source")
        or ""
    )

    salary = item.get("salary", "")

    return {
        "title": title,
        "company": company,
        "location": location,
        "url": url,
        "source": f"Apify / {posted_via}" if posted_via else "Apify",
        "description": description,
        "posted_date": posted_date,
        "salary": salary,
    }


def fetch_apify_jobs():
    api_token = os.getenv("APIFY_API_TOKEN")

    if not api_token:
        print("APIFY_API_TOKEN is missing, skipping Apify")
        return []

    if APIFY_ACTOR_ID == "REPLACE_WITH_YOUR_ACTOR_ID":
        print("APIFY_ACTOR_ID is not configured, skipping Apify")
        return []

    all_jobs = []

    actor_id_for_url = APIFY_ACTOR_ID.replace("/", "~")
    url = f"https://api.apify.com/v2/acts/{actor_id_for_url}/run-sync-get-dataset-items"

    for query in APIFY_SEARCHES:
        payload = {
            "query": query,
            "maxItems": 10,
        }

        params = {
            "token": api_token,
        }

        try:
            response = requests.post(
                url,
                params=params,
                json=payload,
                timeout=300,
            )
            response.raise_for_status()

            items = response.json()

            print(f"Apify query '{query}' returned {len(items)} items")

            for item in items:
                job = normalize_apify_job(item)

                if job["title"] and job["url"]:
                    all_jobs.append(job)

        except Exception as e:
            print(f"Error fetching Apify jobs for '{query}': {e}")

    return all_jobs