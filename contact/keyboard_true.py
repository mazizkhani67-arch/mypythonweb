import requests
import json

TOKEN = "708831297:S24JBAypLQgSjOWRIKPpDvyYYDZrRaSyjs0"
CHAT_ID = "364622747" # آیدی که در خروجی قبلی شما بود
MAIN_URL = f"https://tapi.bale.ai/bot{TOKEN}"
METHOD1 = "sendmessage"
METHOD2 = "getupdates"
url = f"{MAIN_URL}/{METHOD1}"
url2 = f"{MAIN_URL}/{METHOD2}"

response1 = requests.post(url2)
NEW_message= json.loads(response1)
print(NEW_message)
# تعریف کی‌برد
keyboard = {
   "inline_keyboard": [
        [{"text": "ورود به سایت","url":"http://google.com"}],
        [{"text": "گزینه 1", "callback_data":"opt1"},{"text": "گزینه 2", "callback_data":"opt2"}]
    ]
}

# ساختار نهایی داده‌ها
payload = {
    "chat_id": CHAT_ID,
    "text": "لطفا یک گزینه انتخاب کنید:",
    "reply_markup": json.dumps(keyboard) 
}

# ارسال درخواست با متد post و آرگومان json
# این روش، payload را به صورت محتوای application/json ارسال می‌کند
response = requests.post(url, json=payload)


print("Status Code:", response.status_code)
print("Response JSON:", response.json())
