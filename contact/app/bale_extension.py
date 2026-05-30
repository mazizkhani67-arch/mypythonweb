# bale extension
import requests
import json

def bale_updates(TOKEN:str,OFFSET:int):
    try :
        MAIN_URL = f"https://tapi.bale.ai/bot{TOKEN}"
        METHOD = "getupdates"
        GET_URL = f"{MAIN_URL}/{METHOD}"
        if OFFSET == None:
            OFFSET = -1
        data = {
            "offset":OFFSET
        }
    except TOKEN == None:
        return False
    else:
        response = requests.post(GET_URL,data=data)
        get_json = response.json()
        return get_json



def bale_callback(GET_JSON:json):
    try:
        callback_data = GET_JSON["result"][0]["callback_query"]["data"]
    except GET_JSON == None:
        return False
    else:
        return callback_data

def bale_answer(TOKEN:str,OFFSET:int):
    try :
        MAIN_URL = f"https://tapi.bale.ai/bot{TOKEN}"
        METHOD = "getupdates"
        GET_URL = f"{MAIN_URL}/{METHOD}"
        if OFFSET == None:
            OFFSET = -1
        data = {
            "offset":OFFSET
        }
    except TOKEN == None:
        return False
    else:
        response = requests.post(GET_URL,data=data)
        get_json = response.json()
        result_json = get_json["result"][0]
        keys = result_json.keys()
        upate_ID = get_json["result"][0]["update_id"]
        for key in keys:
            if key == "message":
                answer = {
                         "TYPE":"text",
                         "ID": result_json[key]["from"]["id"],
                         "data" :result_json[key]["text"],
                         "update_ID" : upate_ID
                }
            elif key == "callback_query":
                answer = {
                          "TYPE":"opt",
                          "ID":result_json[key]["from"]["id"],
                          "data": result_json[key]["data"],
                          "update_ID" : upate_ID
                }
            else:
                answer = False
        
        return answer
if __name__ == "__main__":
    print("You should have bale token at least")