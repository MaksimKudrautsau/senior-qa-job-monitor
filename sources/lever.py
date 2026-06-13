import requests


LEVER_COMPANIES = {
    "Netflix": "netflix",
    "Medium": "medium",
    "Color": "color"
}


def fetch_lever_jobs():
    all_jobs = []

    for company_name, company_slug in LEVER_COMPANIES.items():
        url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            jobs = response.json()

            for job in jobs:
                all_jobs.append({
                    "title": job.get("text", ""),
                    "company": company_name,
                    "location": job.get("categories", {}).get("location", ""),
                    "url": job.get("hostedUrl", ""),
                    "source": "Lever",
                    "description": job.get("descriptionPlain", "") or job.get("description", ""),
                })

        except Exception as e:
            print(f"Error fetching {company_name}: {e}")

    return all_jobs