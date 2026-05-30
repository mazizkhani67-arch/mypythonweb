import requests
import json
from datetime import datetime

# ==========================
# تنظیمات (اطلاعات خودت را وارد کن)
# ==========================

MELIPAYAMAK_USERNAME = "09171509800"
MELIPAYAMAK_PASSWORD = "f5a0dadb774e454da94d8df75aebb498"
SMS_FROM = "50004000980096"

BALE_TOKEN = "708831297:S24JBAypLQgSjOWRIKPpDvyYYDZrRaSyjs0"
EITA_TOKEN = "bot479281:93bb445d-f0b7-4812-b7b3-a1c08b8f0cc9"

# ==========================
# دریافت اطلاعات از کاربر
# ==========================

name = input("نام را وارد کنید: ")
phone = input("شماره تلفن را وارد کنید: ")
chat_id = input("Chat ID بله/ایتا را وارد کنید: ")

message = f"{name} عزیز، ثبت‌نام شما با موفقیت انجام شد ✅"

# ==========================
# ارسال پیامک با ملی پیامک
# ==========================

def send_sms(phone, message):
    url = f"https://console.melipayamak.com/api/send/simple/{MELIPAYAMAK_PASSWORD}"
    data = {
        "from": SMS_FROM,
        "to": phone,
        "text": message
        }
    
    response = requests.post(url, json=data)
    print("SMS Response:", response.text)


# ==========================
# ارسال پیام در بله
# ==========================
chat_id = "@Karnikhelpbot"
def send_bale(chat_id, message):
    url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendmessage"
    
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post (url, json=payload)
    print("Bale Response:", response.text)


# ==========================
# ارسال پیام در ایتا
# ==========================
chat_id = "@karnik_group"
def send_eita(chat_id, message):
    url = f"https://eitaayar.ir/api/{EITA_TOKEN}/sendmessage"
    
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(url, json=payload)

    print("Eita Response:", response.text)


# ==========================
# ذخیره در فایل txt
# ==========================

def save_to_file(name, phone):
    with open("contacts.txt", "a", encoding="utf-8") as file:
        file.write(f"{datetime.now()} - {name} - {phone}\n")


# ==========================
# اجرای برنامه
# ==========================

send_sms(phone, message)
# send_bale(chat_id, message)
#send_eita(chat_id, message)
# save_to_file(name, phone)

# print("✅ همه پیام‌ها ارسال شد و اطلاعات ذخیره شد.")
