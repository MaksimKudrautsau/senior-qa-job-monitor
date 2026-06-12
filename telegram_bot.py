import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(text: str):
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing")
    if not CHAT_ID:
        raise ValueError("TELEGRAM_CHAT_ID is missing")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": False
    }

    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()