from app.bale_extension import bale_updates,bale_callback
TOKEN = "708831297:S24JBAypLQgSjOWRIKPpDvyYYDZrRaSyjs0"






new_json = bale_updates(TOKEN,-1)


callback_data = bale_callback(new_json)

print(callback_data)
