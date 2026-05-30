import json
with open("json_api.json","r",encoding= "utf-8") as f:
    api = f.read()
print(api)
api_test = json.loads(api)
print(type(api_test))
print(api_test[0]["price"])
