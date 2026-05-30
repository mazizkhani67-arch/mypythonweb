# نوشتن (اگر فایل باشد، پاک می‌شود)
with open("my_file.txt", "w", encoding="utf-8") as f:
    f.write("خط اول.\n")
    f.write("خط دوم.\n")

# اضافه کردن به انتها
with open("my_file.txt", "a", encoding="utf-8") as f:
    f.write("این خط اضافه شده است.\n")

# خواندن کل محتوا
with open("my_file.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)
with open("my_file.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(f"خط خوانده شده: {line.strip()}") # .strip() برای حذف \n آخر خط