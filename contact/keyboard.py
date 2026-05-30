import requests
import json

TOKEN = "708831297:S24JBAypLQgSjOWRIKPpDvyYYDZrRaSyjs0"
CHAT_ID = "364622747" #1634537954

url = f"https://tapi.bale.ai/bot{TOKEN}/sendmessage"

keyboard = {
    "inline_keyboard": [
        [{"text": "ورود به سایت","url":"http://google.com"}],
        [{"text": "گزینه 1", "callback_data":"opt1"},{"text": "گزینه 2", "callback_data":"opt2"}]
    ]
}

payload = {
    "chat_id": CHAT_ID,
    "text": "لطفا یکگزنه انتخاب کنید:",
    "reply_markup": json.dumps(keyboard)
}

response = requests.post(url, data=payload)
print(response.json())