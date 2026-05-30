import json
setting = {
    "theme" : "dark",
    "font" : "nazanin",
    "color" : "Blue"
 }
print(setting)
with open("setting.json","w") as f:
    json.dump(setting,f,indent=4,ensure_ascii=False)


with open("setting.json","r",encoding="utf-8") as f1:
    setting2 =json.load(f1)
    print(setting2)
    print(setting2["color"])

print("I Can do it")