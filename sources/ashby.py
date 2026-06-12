import requests


ASHBY_COMPANIES = {
    "Notion": "notion",
    "Linear": "linear",
    "Vanta": "vanta",
    "Harvey": "harvey",
    "Replit": "replit",
    "Cursor": "cursor",
}


def fetch_ashby_jobs():
    all_jobs = []

    for company_name, company_slug in ASHBY_COMPANIES.items():
        url = f"https://api.ashbyhq.com/posting-api/job-board/{company_slug}?includeCompensation=true"

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            for job in data.get("jobs", []):
                location = (
                    job.get("locationName")
                    or job.get("location")
                    or ""
                )

                if isinstance(location, dict):
                    location = location.get("name", "")

                all_jobs.append({
                    "title": job.get("title", ""),
                    "company": company_name,
                    "location": location,
                    "url": job.get("jobUrl", ""),
                    "source": "Ashby",
                    "description": job.get("descriptionHtml", "") or job.get("descriptionPlain", ""),
                })

        except Exception as e:
            print(f"Error fetching {company_name}: {e}")

    return all_jobs