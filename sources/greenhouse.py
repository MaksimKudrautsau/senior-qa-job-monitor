import requests


GREENHOUSE_COMPANIES = {
    "Databricks": "databricks",
    "Cloudflare": "cloudflare",
    "Stripe": "stripe",
    "Figma": "figma",
    "Discord": "discord",
    "Checkr": "checkr",
    "Chime": "chime",
    "Nextdoor": "nextdoor",
    "Instacart": "instacart",
    "Samsara": "samsara"
}


def fetch_greenhouse_jobs():
    all_jobs = []

    for company_name, board_token in GREENHOUSE_COMPANIES.items():
        url = f"https://api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            for job in data.get("jobs", []):
                all_jobs.append({
                    "title": job.get("title", ""),
                    "company": company_name,
                    "location": job.get("location", {}).get("name", ""),
                    "url": job.get("absolute_url", ""),
                    "source": "Greenhouse",
                    "description": job.get("content", ""),
                })

        except Exception as e:
            print(f"Error fetching {company_name}: {e}")

    return all_jobs