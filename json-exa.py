import json

# ۱. دیکشنری پایتون به JSON string
data_dict = {
    "name": "سارا",
    "age": 25,
    "is_student": True,
    "courses": ["ریاضی", "فیزیک"],
    "address": {
        "street": "خیابان اصلی",
        "city": "شهر"
    }
}

# تبدیل دیکشنری به رشته JSON
json_string = json.dumps(data_dict, indent=4, ensure_ascii=False)
# indent=4 برای خوانایی بهتر (فاصله‌گذاری)
# ensure_ascii=False برای نمایش درست کاراکترهای فارسی

print("--- JSON String ---")
print(json_string)

# ۲. JSON string به دیکشنری پایتون
python_dict = json.loads(json_string)
print("\n--- Python Dictionary ---")
print(python_dict)
print(python_dict["courses"][0]) # دسترسی به عناصر

# ۳. ذخیره داده در فایل JSON
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data_dict, f, indent=4, ensure_ascii=False)
    # json.dump مستقیماً دیکشنری را در فایل می‌نویسد

# ۴. خواندن داده از فایل JSON
with open("data.json", "r", encoding="utf-8") as f:
    loaded_data = json.load(f)
    print("\n--- Data loaded from file ---")
    print(loaded_data)
