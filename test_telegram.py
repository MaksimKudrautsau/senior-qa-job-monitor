import requests

BOT_TOKEN = "8723530903:AAHVD3UK4odMyGQP2EqgSQ5tCYHrngbmK6Q"
CHAT_ID = "5147627622"

message = "🚀 Senior QA Job Monitor is online!"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(url, json=payload)

print(response.json())