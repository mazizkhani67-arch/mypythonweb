from datetime import date, datetime, timedelta
import re

def to_jalali(date_obj):
    """
    تبدیل تاریخ میلادی به شمسی
    ورودی: datetime.date یا datetime.datetime
    خروجی: رشته تاریخ شمسی
    """
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    # محاسبه دستی تاریخ شمسی با استفاده از الگوریتم تبدیل
    return _gregorian_to_jalali(date_obj.year, date_obj.month, date_obj.day)

def _gregorian_to_jalali(gy, gm, gd):
    """
    تبدیل تاریخ میلادی به شمسی با الگوریتم ساده
    """
    # آرایه‌های کمکی
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
    
    # محاسبه روزهای گذشته از ابتدای سال میلادی
    gy = gy - 1600
    gm = gm - 1
    gd = gd - 1
    
    g_day_no = 365 * gy + (gy + 3) // 4 - (gy + 99) // 100 + (gy + 399) // 400
    
    for i in range(gm):
        g_day_no += g_days_in_month[i]
    
    if gm > 1 and ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
        g_day_no += 1
    
    g_day_no += gd
    
    # محاسبه روزهای گذشته از ابتدای سال شمسی
    j_day_no = g_day_no - 79
    
    # محاسبه سال شمسی
    j_np = j_day_no // 12053
    j_day_no = j_day_no % 12053
    
    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no = j_day_no % 1461
    
    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365
    
    # محاسبه ماه و روز شمسی
    for i in range(12):
        if j_day_no < j_days_in_month[i]:
            jm = i + 1
            jd = j_day_no + 1
            break
        j_day_no -= j_days_in_month[i]
    
    return f"{jy:04d}/{jm:02d}/{jd:02d}"

def _jalali_to_gregorian(jy, jm, jd):
    """
    تبدیل تاریخ شمسی به میلادی
    """
    j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
    
    jy = jy - 979
    jm = jm - 1
    jd = jd - 1
    
    j_day_no = 365 * jy + (jy // 33) * 8 + ((jy % 33) + 3) // 4
    
    for i in range(jm):
        j_day_no += j_days_in_month[i]
    
    j_day_no += jd
    
    g_day_no = j_day_no + 79
    
    gy = 1600 + 400 * (g_day_no // 146097)
    g_day_no = g_day_no % 146097
    
    leap = True
    while True:
        if g_day_no < 365:
            break
        if g_day_no < 366:
            if leap:
                break
            else:
                g_day_no -= 365
                break
        if leap:
            g_day_no -= 366
        else:
            g_day_no -= 365
        
        gy += 1
        leap = (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)
    
    g_days_in_month = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    for i in range(12):
        if g_day_no < g_days_in_month[i]:
            gm = i + 1
            gd = g_day_no + 1
            break
        g_day_no -= g_days_in_month[i]
    
    return date(gy, gm, gd)

def to_jalali_with_time(datetime_obj):
    """
    تبدیل datetime میلادی به شمسی با زمان
    """
    jalali_date = to_jalali(datetime_obj)
    time_str = datetime_obj.strftime("%H:%M")
    return f"{jalali_date} {time_str}"

def get_jalali_today():
    """دریافت تاریخ شمسی امروز"""
    return to_jalali(date.today())

def get_jalali_month_name(month_num):
    """دریافت نام ماه شمسی"""
    months = [
        'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
    ]
    return months[month_num - 1] if 1 <= month_num <= 12 else ''

def format_jalali_date_range(start_date, end_date):
    """فرمت‌بندی بازه تاریخ شمسی"""
    start = to_jalali(start_date)
    end = to_jalali(end_date)
    
    start_parts = start.split('/')
    end_parts = end.split('/')
    
    if start_parts[0] == end_parts[0] and start_parts[1] == end_parts[1]:
        return f"{start_parts[0]}/{start_parts[1]} از {start_parts[2]} تا {end_parts[2]}"
    
    return f"{start} تا {end}"

def get_jalali_month_range(year, month):
    """دریافت بازه یک ماه شمسی"""
    # اولین روز ماه شمسی
    jalali_start = date(year, month, 1)
    gregorian_start = _jalali_to_gregorian(year, month, 1)
    
    # آخرین روز ماه شمسی
    if month == 12:
        gregorian_end = _jalali_to_gregorian(year + 1, 1, 1) - timedelta(days=1)
    else:
        gregorian_end = _jalali_to_gregorian(year, month + 1, 1) - timedelta(days=1)
    
    return gregorian_start, gregorian_end