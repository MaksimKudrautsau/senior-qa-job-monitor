import requests


GREENHOUSE_COMPANIES = {
    # Big tech / AI / data
    "Databricks": "databricks",
    "Cloudflare": "cloudflare",
    "Stripe": "stripe",
    "Figma": "figma",
    "Discord": "discord",
    "Anthropic": "anthropic",
    "Scale AI": "scaleai",
    "Airtable": "airtable",
    "Asana": "asana",
    "Dropbox": "dropbox",
    "Box": "boxinc",
    "Webflow": "webflow",

    # Fintech / payments / business software
    "Chime": "chime",
    "Brex": "brex",
    "Robinhood": "robinhood",
    "Coinbase": "coinbase",
    "Affirm": "affirm",
    "Credit Karma": "creditkarma",
    "Mercury": "mercury",
    "Rippling": "rippling",
    "Gusto": "gusto",
    "Checkr": "checkr",

    # Delivery / marketplace / consumer
    "Instacart": "instacart",
    "Lyft": "lyft",
    "Airbnb": "airbnb",
    "Nextdoor": "nextdoor",
    "Reddit": "reddit",
    "Pinterest": "pinterest",
    "TaskRabbit": "taskrabbit",

    # Security / infra / dev tools
    "Samsara": "samsara",
    "Okta": "okta",
    "Twilio": "twilio",
    "Fastly": "fastly",
    "Elastic": "elastic",
    "MongoDB": "mongodb",
    "Cockroach Labs": "cockroachlabs",
    "LaunchDarkly": "launchdarkly",
    "Tailscale": "tailscale",
    "Tanium": "tanium",

    # Media / ads / entertainment
    "Roku": "roku",
    "The Trade Desk": "thetradedesk",
    "Moloco": "moloco",

    # Health / biotech / robotics / hardware
    "Nuro": "nuro",
    "Waymo": "waymo",
    "Anduril": "andurilindustries",
    "Verkada": "verkada",
    "Natera": "natera",

    # More SaaS / enterprise
    "Amplitude": "amplitude",
    "Calendly": "calendly",
    "Intercom": "intercom",
    "Lattice": "lattice",
    "Culture Amp": "cultureamp",
    "Udemy": "udemy",
    "Coursera": "coursera",
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