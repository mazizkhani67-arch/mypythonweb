import requests
import json
import time

BOT_TOKEN = "708831297:Lg3xTzpPStEcybYSqnluwjpJ_l9VJdGk9n4"  # توکن ربات بله خود را اینجا قرار دهید
BASE_URL = f"https://api.bale.ai/bot{BOT_TOKEN}"

def send_message(chat_id, text, reply_markup=None):
    url = f"{BASE_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status() # بررسی خطاهای HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"خطا در ارسال پیام به {chat_id}: {e}")
        return None

def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"offset": offset}
    try:
        # اضافه کردن timeout و بررسی خطاهای HTTP
        response = requests.get(url, params=params, timeout=15) 
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.Timeout:
        print("خطا: درخواست دریافت آپدیت‌ها با خطا مواجه شد (Timeout).")
    except requests.exceptions.HTTPError as e:
        print(f"خطا: خطای HTTP در دریافت آپدیت‌ها: {e.response.status_code} - {e.response.text}")
        # در اینجا می‌توانی منطق مدیریت خطای 503 را اضافه کنی
        if e.response.status_code == 503:
            print("خطا 503 دریافت شد. سرور بله موقتاً در دسترس نیست. چند لحظه بعد دوباره امتحان می‌کنم.")
            time.sleep(10) # صبر بیشتر برای خطای 503
    except requests.exceptions.RequestException as e:
        print(f"خطای کلی در دریافت آپدیت‌ها: {e}")
    
    return {"result": []} # در صورت خطا، لیست خالی برگردان

def main():
    print("ربات بله فعال شد...")
    last_update_id = None

    custom_keyboard = {
        "keyboard": [
            [{"text": "اطلاعات تماس 📞"}],
            [{"text": "درباره ما ℹ️"}],
            [{"text": "راهنمای استفاده ❓"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

    while True:
        updates = get_updates(offset=last_update_id)
        results = updates.get("result", [])

        if not results:
            # اگر هیچ آپدیتی نبود، کمی صبر کن و دوباره چک کن
            time.sleep(5) 
            continue

        for update in results:
            # بروزرسانی آخرین آپدیت
            last_update_id = update["update_id"] + 1

            if "message" in update:
                message = update["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                if text.startswith("/start") or text.startswith("منو"):
                    send_message(chat_id, "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", custom_keyboard)
                
                elif text == "اطلاعات تماس 📞":
                    response = "شماره تماس پشتیبانی: 021-12345678\nایمیل: support@example.com"
                    send_message(chat_id, response)
                    send_message(chat_id, "گزینه دیگری انتخاب می‌کنید؟", custom_keyboard)

                elif text == "درباره ما ℹ️":
                    response = "این ربات برای ارائه اطلاعات مفید در بله طراحی شده است."
                    send_message(chat_id, response)
                    send_message(chat_id, "گزینه دیگری انتخاب می‌کنید؟", custom_keyboard)
                    
                elif text == "راهنمای استفاده ❓":
                    response = "برای شروع، /start را تایپ کنید یا کلمه 'منو' را بفرستید تا گزینه‌ها نمایش داده شوند."
                    send_message(chat_id, response)
                    send_message(chat_id, "گزینه دیگری انتخاب می‌کنید؟", custom_keyboard)

            # در صورت استفاده از اینلاین کیبورد، بخش callback_query را فعال کنید
            # elif "callback_query" in update:
            #     callback_query = update["callback_query"]
            #     chat_id = callback_query["message"]["chat"]["id"]
            #     data = callback_query["data"]
            #     last_update_id = update["update_id"] + 1
            #     # ... منطق پاسخ به callback ...
            #     requests.post(f"{BASE_URL}/answerCallbackQuery", data={"callback_query_id": callback_query["id"], "text": "در حال پردازش..."})

        # کمی صبر کن قبل از چک کردن مجدد آپدیت‌ها
        time.sleep(5) 

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nربات با موفقیت متوقف شد.")
