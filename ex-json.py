import json
import datetime
import jdatetime
user_comment = "yes"
tip_dict = []
while user_comment != "No"  :
    nowtime =  datetime.datetime.now()

    jdate = jdatetime.date.fromgregorian(date=nowtime)
    t = nowtime.time()

    nowtime = f" {str(jdate)}  {str(t)}"
    print(f"{str(jdate)} {str(t)} ")


    print("No for exit!!!")
    user_comment = input("type your tip:")
    tip_dict1 = [
           { "time": nowtime,
            "UserComment" : user_comment}
    ]
    print(tip_dict1)
    tip_dict.append(tip_dict1)
    print(tip_dict)
    with  open("log.txt","a",encoding="utf-8") as f:
        tip = f"Time : {nowtime} ---> Tip: {user_comment}\n "
        f.write(tip)
with open("jsontip.json","w",encoding="utf-8") as f2:
    json.dump(tip_dict,f2,indent=4,ensure_ascii=False)