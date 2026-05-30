import requests
import json
from  app.bale_extension import bale_updates,bale_answer

import time

ADMIN_ID = 364622747
TOKEN = "708831297:S24JBAypLQgSjOWRIKPpDvyYYDZrRaSyjs0"

MAIN_URL = f"https://tapi.bale.ai/bot{TOKEN}"
METHOD1 = "sendmessage"





answer = bale_answer(TOKEN,-1)
last_answer1 = 0
while True:
    answer = bale_answer(TOKEN,-1)
    last_answer0 = answer["update_ID"] 
    if last_answer0 == last_answer1:
        url1 = f"{MAIN_URL}/{METHOD1}" 
        payload = {
                        "chat_id": ADMIN_ID,
                        "text":" خدا نگهدار ",
                        }
        response = requests.post(url1, data=payload)
        print(response.json())
        break
    if answer != False:
        ANSWER_TYPE = answer["TYPE"]
        if ANSWER_TYPE == "text":
            if answer["ID"]== ADMIN_ID and answer["data"] == "/start":
                url1 = f"{MAIN_URL}/{METHOD1}" 
                keyboard = {
                    "inline_keyboard": [
                        
                        [{"text": "ثبت مشتری", "callback_data":"opt1"},
                         {"text": "لیست مشتریان ", "callback_data":"opt2"}],
                         [{"text":"عملیات","callback_data":"opt3"}]
                    ]   
                }
                payload = {
                "chat_id": ADMIN_ID,
                "text": "لطفا یک گزینه انتخاب کنید:",
                "reply_markup": json.dumps(keyboard)
                }
                response = requests.post(url1, data=payload)
                print(response.json())
            else:
                print("not admin or not start")
        elif ANSWER_TYPE == "opt":
                if answer["data"] == "opt1":
                    url1 = f"{MAIN_URL}/{METHOD1}" 
                    keyboard = {
                        "inline_keyboard":[
                            [{"text": "خروج","callback_data":"exit"}]
                        ]
                    }
                    payload = {
                        "chat_id": ADMIN_ID,
                        "text": "ورود شماره تلفن:",
                        "reply_markup":json.dumps(keyboard)
                        }
                    response = requests.post(url1, data=payload)
                    time.sleep(10)  
                    answer = bale_answer(TOKEN,-1)
                    ANSWER_TYPE = answer["TYPE"]
                    if ANSWER_TYPE == "text":
                        phone = answer["data"]
                        
                    elif answer["data"] == "exit":
                        payload = {
                            "chat_id": ADMIN_ID,
                            "text": "خدانگهدار",
                        }
                        response = requests.post(url1,data=payload)
                        break
                    time.sleep(5)
                    payload = {
                        "chat_id": ADMIN_ID,
                        "text":"نام و نام خانوادگی:",
                        "reply_markup":json.dumps(keyboard)
                    }
                    response=requests.post(url1,data=payload)
                    time.sleep(10)
                    answer = bale_answer(TOKEN , -1)
                    ANSWER_TYPE = answer["TYPE"]
                    if ANSWER_TYPE=="text":
                        name = answer["data"]
                    elif answer["data"]=="exit": 
                        payload = {
                            "chat_id": ADMIN_ID,
                            "text": "خدانگهدار",
                        }
                        response=requests.post(url1,data=payload)
                        break
                    #a = send_SMS(phone,name,"001","231075")
                    try:
                        with open("call.txt","a",encoding="utf-8") as f :
                            text = f"001,{phone},{name}\n"
                            f.write(text)
                    except phone == "" or name == "":
                        payload = {
                            "chat_id": ADMIN_ID,
                            "text": "ورودی ناقص"
                        }
                        response = requests.post(url1,data=payload)
                        break
                elif answer["data"] == "opt2":
                    url1 = f"{MAIN_URL}/{METHOD1}" 
                    payload = {
                        "chat_id": ADMIN_ID,
                        "text": "ارسال شد!!",
                        }
                    response = requests.post(url1, data=payload)
                    print(response.json())  
                elif answer["data"] == "opt3":
                    url1 = f"{MAIN_URL}/{METHOD1}"
                    keyboard = {
                        "inline_keyboard": [
                         [{"text": "ورود به سایت","url":"http://google.com"}],
                         [{"text": "گزینه 1", "callback_data":"opt1"},{"text": "گزینه 2", "callback_data":"opt2"}]
                        ]
                    }
                    payload = {
                        "chat_id": ADMIN_ID,
                        "text": "درحال بروز رسانی",
                        "reply_markup": json.dumps(keyboard)
                    }
                    response = requests.post(url1,data = payload)
                      
    else:
        print("Continue")
    time.sleep(10)
    last_answer1 = last_answer0

