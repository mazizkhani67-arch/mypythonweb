import re
from datetime import datetime, date
import json

def is_valid_amount(amount_str):
    """بررسی معتبر بودن مبلغ"""
    try:
        # حذف کاما و فاصله
        clean = re.sub(r'[,،\s]', '', amount_str)
        amount = int(clean)
        return amount > 0
    except:
        return False

def format_currency(amount):
    """فرمت‌بندی مبلغ با کاما"""
    return f"{amount:,}"

def get_persian_date():
    """دریافت تاریخ شمسی (نیاز به نصب persiantools)"""
    # می‌توانید از persiantools یا jdatetime استفاده کنید
    return date.today().isoformat()

def validate_expense_format(text):
    """بررسی فرمت پیام هزینه"""
    patterns = [
        r'^هزینه\s+(\d[\d,]*)\s+(.+)$',  # با کاما
        r'^هزینه\s+([\d,]+)\s+(.+)$',     # اعداد با کاما
    ]
    
    for pattern in patterns:
        match = re.match(pattern, text.strip())
        if match:
            amount_str = match.group(1).replace(',', '').replace('،', '')
            description = match.group(2).strip()
            if description and is_valid_amount(amount_str):
                return int(amount_str), description
    
    return None, None