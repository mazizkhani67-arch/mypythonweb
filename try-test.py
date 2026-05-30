import sys
try: 
    with open("data.txt","r",encoding="utf-8") as f:
        print(f.read())
except FileNotFoundError:
    print("not found")
finally:
    print("Finally......")