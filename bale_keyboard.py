from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = "708831297:S24JBAypLQgSjOWRIKPpDvyYYDZrRaSyjs0"
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"

# ارسال پیام معمولی
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, json=data)

# ارسال پیام همراه با دکمه‌ها
def send_keyboard(chat_id, text, keyboard):
    url = f"{BASE_URL}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": keyboard
    }
    requests.post(url, json=data)

@app.route("/", methods=["POST"])
def webhook():
    update = request.json

    if "message" not in update:
        return "ok"

    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "")

    # واکنش به دکمه‌ها یا دستورات
    if text == "/start":
        keyboard = {
            "keyboard": [
                [{"text": "👋 معرفی"}],
                [{"text": "ℹ️ کمک"}],
                [{"text": "🎮 تست دکمه"}]
            ],
            "resize_keyboard": True
        }
        send_keyboard(chat_id, "سلام! به بات خوش آمدید.", keyboard)
    
    elif text == "👋 معرفی":
        send_message(chat_id, "این یک بات نمونه بله است که با Python ساخته شده.")

    elif text == "ℹ️ کمک":
        send_message(chat_id, "دکمه‌ها را امتحان کنید یا /start را بزنید.")

    elif text == "🎮 تست دکمه":
        inline_keyboard = {
            "inline_keyboard": [
                [{"text": "باز کردن وب‌سایت", "url": "https://bale.ai"}],
                [{"text": "دریافت پیام", "callback_data": "get_message"}]
            ]
        }
        send_keyboard(chat_id, "یک گزینه را انتخاب کنید:", inline_keyboard)

    # واکنش به callback_data
    elif update["message"].get("data") == "get_message":
        send_message(chat_id, "شما یک دکمه Inline را فشار دادید!")

    else:
        send_message(chat_id, "پیام دریافت شد: " + text)

    return "ok"

if __name__ == "__main__":
    app.run(port=5000)
