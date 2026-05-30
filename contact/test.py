import requests
import json
from app.sms_extension import send_SMS,send_SMS2
  
#data = {'bodyId': 231075, 'to': '09171509800', 'args': ['arg1', 'arg2']}
#response = requests.post('https://console.melipayamak.com/api/send/shared/f5a0dadb774e454da94d8df75aebb498', json=data)
#print(response.json())

# a = send_SMS('09171509800','پارسا','002',231075)
b = send_SMS('09171509800','پارسا','002',231075)
print(b)
#url = "https://console.melipayamak.com/api/send/multiple/f5a0dadb774e454da94d8df75aebb498"
#data = { 
 # "from": "50002710009800", 
 # "to": ["09171509800", "09171500096"], 
 # "text": ["پیامک آزمایشی", "پیامک آزمایشی"],
  #"udh": ""
#}
#response = requests.post(url,data=data)
#print(response.json())