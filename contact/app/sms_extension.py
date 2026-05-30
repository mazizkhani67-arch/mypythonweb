import json
import requests


def send_SMS(Phone:str,Name:str,C_ID:str,M_ID:str):
    MELLI_URL = "https://api.payamak-panel.com/post/Send.asmx/SendByBaseNumber"
    USERNAME = "09171509800"
    PASSCODE = "b4ff108c-1217-45fc-a1db-b7b57ab06a45"
    #COUSTOMER = ["000","زهرا عزیزخانی","09171509800"]
    # MESSAGE_ID = "231075"
    data = {
        "username": USERNAME ,
        "password": PASSCODE ,
        "text": [Name,C_ID] ,
        "to" : Phone,
        "bodyId" : M_ID
    }
    response = requests.post(MELLI_URL,data = data)
    return response

def send_SMS2(Phone:str,Name:str,C_ID:str,M_ID:int):
    url = "https://console.melipayamak.com/api/send/shared/f5a0dadb774e454da94d8df75aebb498"
    data = {'bodyId': M_ID, 
            'to': Phone , 
            'args': [Name,C_ID]} 
    response = requests.post(url, json=data)

if __name__ == "__main__":
    print("You should use in code!!")