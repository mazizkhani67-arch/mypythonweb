# utils/sms.py
from melipayamak import Api
from flask import current_app

def send_project_sms(phone_number, project_code, step_name, progress_percent):
    """
    ارسال پیامک با استفاده از سرویس پترن (الگو) ملی پیامک
    """
    try:
        username = current_app.config.get('MELIPAYAMAK_USERNAME')
        password = current_app.config.get('MELIPAYAMAK_PASSWORD')
        pattern_code = current_app.config.get('MELIPAYAMAK_PATTERN_CODE')
        from_number = current_app.config.get('MELIPAYAMAK_FROM')
        
        if not all([username, password, pattern_code]):
            return {
                "success": False, 
                "error": "تنظیمات پیامک کامل نیست (نام کاربری، رمز عبور یا کد الگو)"
            }
        
        if not phone_number:
            return {
                "success": False, 
                "error": "شماره تلفن گیرنده معتبر نیست"
            }
        
        # ایجاد نمونه از کلاس Api
        api = Api(username, password)
        sms = api.sms()
        
        # مقادیر متغیرهای الگو (به ترتیب {0}, {1}, {2}, ...)
        pattern_values = [
            project_code,           # {0} - کد پروژه
            str(progress_percent),   # {1} - درصد پیشرفت
            step_name               # {2} - نام مرحله
        ]
        
        # ارسال پیامک با استفاده از متد send_by_base_number
        response = sms.send_by_base_number(pattern_code, [phone_number], pattern_values)
        
        # بررسی پاسخ
        # در صورت موفقیت، شناسه پیام (recId) برگشت داده می‌شود
        if isinstance(response, str) and response.isdigit() and int(response) >= 0:
            return {
                "success": True, 
                "message_id": response,
                "message": "پیامک با موفقیت ارسال شد"
            }
        else:
            # کدهای خطا بر اساس مستندات ملی پیامک
            error_messages = {
                "-1": "دسترسی به وب سرویس پترن غیرفعال است",
                "-2": "نام کاربری یا رمز عبور اشتباه است",
                "-3": "خطا در اتصال به سرور ملی پیامک",
                "-4": "کد پترن (الگو) اشتباه یا تأیید نشده است",
                "-5": "تعداد متغیرها با الگو مطابقت ندارد",
                "-6": "شماره گیرنده نامعتبر است",
                "-7": "خطا در شماره فرستنده",
                "-9": "اعتبار حساب کاربری کافی نیست",
                "-10": "ارسال لینک، آیپی یا ایمیل به جای متغیر مجاز نیست",
                "-11": "شماره گیرنده در لیست سیاه است",
                "-111": "آیپی درخواست‌کننده نامعتبر است"
            }
            
            error_msg = error_messages.get(str(response), f"خطای ناشناخته (کد: {response})")
            return {
                "success": False, 
                "error": f"خطا در ارسال پیامک: {error_msg}"
            }
            
    except Exception as e:
        print(f"❌ خطا در ارسال پیامک: {e}")
        return {"success": False, "error": str(e)}