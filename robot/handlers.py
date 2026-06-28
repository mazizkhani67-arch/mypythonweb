import re
from datetime import datetime, date, timedelta
from balebot.models.messages import TextMessage, DocumentMessage
from config import Config
from database import Database
from excel_report import ExcelReporter

db = Database(Config.DB_PATH)
excel_reporter = ExcelReporter(db, Config.REPORTS_DIR)

def handle_message(bot, update):
    """مدیریت پیام‌های دریافتی"""
    try:
        user_id = update.get_effective_user().peer_id
        user_name = update.get_effective_user().first_name
        chat_id = update.get_effective_chat().peer_id
        
        # بررسی گروه
        if Config.GROUP_ID and str(chat_id) != Config.GROUP_ID:
            return
        
        # بررسی دسترسی
        if str(user_id) not in Config.ALLOWED_USERS:
            response = TextMessage("⛔ شما مجاز به ثبت هزینه نیستید!")
            bot.send_message(response, user_id)
            return
        
        if not update.message or not update.message.text:
            return
        
        text = update.message.text
        
        # بررسی دستورات
        if text.startswith('/'):
            handle_commands(bot, update, text)
            return
        
        # بررسی فرمت جدید هزینه
        expense_data = extract_expense_info(text)
        
        if expense_data:
            amount, description = expense_data
            
            # ثبت در دیتابیس
            expense_id, category = db.add_expense(
                user_id=str(user_id),
                username=user_name,
                amount=amount,
                description=description
            )
            
            # پاسخ تایید
            response = TextMessage(
                f"✅ هزینه ثبت شد:\n"
                f"💰 مبلغ: {amount:,} تومان\n"
                f"📝 توضیحات: {description}\n"
                f"📂 دسته‌بندی: {category}\n"
                f"🕐 زمان: {datetime.now().strftime('%H:%M')}"
            )
            bot.send_message(response, user_id)
        else:
            # اگر فرمت هزینه نبود، پیام راهنما
            if '#هزینه' in text or '# هزینه' in text:
                response = TextMessage(
                    "❌ فرمت پیام صحیح نیست!\n"
                    "لطفاً به این شکل پیام دهید:\n\n"
                    "# هزینه\n"
                    "مبلغ [عدد] تومان [توضیحات]\n\n"
                    "مثال:\n"
                    "# هزینه\n"
                    "مبلغ 1000 تومان بابت سیمان"
                )
                bot.send_message(response, user_id)
            
    except Exception as e:
        print(f"Error in handle_message: {e}")

def extract_expense_info(text):
    """استخراج اطلاعات هزینه از متن"""
    # الگوی کامل با دو خط
    pattern1 = re.compile(Config.EXPENSE_PATTERN, re.MULTILINE | re.DOTALL)
    match = pattern1.search(text)
    
    if match:
        amount_str = match.group(1).replace(',', '').replace('،', '')
        description = match.group(2).strip()
        try:
            amount = int(amount_str)
            if amount > 0 and description:
                return amount, description
        except:
            pass
    
    # الگوی ساده‌تر (یک خط)
    pattern2 = re.compile(Config.EXPENSE_PATTERN_SIMPLE)
    match = pattern2.search(text)
    
    if match:
        amount_str = match.group(1).replace(',', '').replace('،', '')
        description = match.group(2).strip()
        try:
            amount = int(amount_str)
            if amount > 0 and description:
                return amount, description
        except:
            pass
    
    return None

def handle_commands(bot, update, text):
    """مدیریت دستورات"""
    user_id = update.get_effective_user().peer_id
    
    commands = {
        '/start': show_start_message,
        '/help': show_help_message,
        '/today': show_today_report,
        '/week': show_weekly_report,
        '/total': show_total_today,
        '/export': export_weekly_report
    }
    
    for cmd, handler in commands.items():
        if text.startswith(cmd):
            handler(bot, user_id)
            break

def show_start_message(bot, user_id):
    response = TextMessage(
        "🤖 ربات مدیریت هزینه بله\n\n"
        "برای ثبت هزینه پیام را به این شکل ارسال کنید:\n\n"
        "# هزینه\n"
        "مبلغ [عدد] تومان [توضیحات]\n\n"
        "مثال:\n"
        "# هزینه\n"
        "مبلغ 1000 تومان بابت سیمان\n\n"
        "📊 دستورات:\n"
        "/today - گزارش امروز (دسته‌بندی شده)\n"
        "/week - گزارش هفتگی\n"
        "/total - مجموع امروز\n"
        "/export - خروجی اکسل هفتگی\n"
        "/help - راهنما"
    )
    bot.send_message(response, user_id)

def show_help_message(bot, user_id):
    response = TextMessage(
        "📖 **راهنمای استفاده**\n\n"
        "🔹 ثبت هزینه:\n"
        "# هزینه\n"
        "مبلغ [مبلغ] تومان [توضیحات]\n\n"
        "🔹 مثال:\n"
        "# هزینه\n"
        "مبلغ 35000 تومان تاکسی\n\n"
        "🔹 دستورات:\n"
        "/today - گزارش امروز\n"
        "/week - گزارش هفتگی\n"
        "/total - مجموع امروز\n"
        "/export - خروجی اکسل هفتگی\n"
        "/help - راهنما"
    )
    bot.send_message(response, user_id)

def show_today_report(bot, user_id=None):
    """نمایش گزارش امروز با دسته‌بندی"""
    today_data = db.get_daily_summary()
    
    if not today_data['category_summary'] and not today_data['user_summary']:
        response = TextMessage("📊 گزارش امروز:\nهیچ هزینه‌ای ثبت نشده است.")
        if user_id:
            bot.send_message(response, user_id)
        return
    
    report = "📊 **گزارش هزینه‌های امروز**\n"
    report += "═" * 30 + "\n\n"
    
    # دسته‌بندی‌ها
    if today_data['category_summary']:
        report += "📂 **دسته‌بندی‌ها:**\n"
        for category, total, count in today_data['category_summary']:
            report += f"   {category}: {total:,} تومان ({count} مورد)\n"
        report += "\n"
    
    # کاربران
    if today_data['user_summary']:
        report += "👤 **کاربران:**\n"
        for username, total, count in today_data['user_summary']:
            report += f"   {username}: {total:,} تومان ({count} مورد)\n"
        report += "\n"
    
    report += "═" * 30 + "\n"
    report += f"💰 **جمع کل: {today_data['total']:,} تومان**"
    
    response = TextMessage(report)
    if user_id:
        bot.send_message(response, user_id)
    elif Config.GROUP_ID:
        bot.send_message(response, Config.GROUP_ID)

def show_weekly_report(bot, user_id):
    """نمایش گزارش هفتگی"""
    today = date.today()
    week_start = today - timedelta(days=7)
    
    expenses = db.get_expenses_by_date_range(
        week_start.isoformat(),
        today.isoformat()
    )
    
    if not expenses:
        response = TextMessage("📊 گزارش هفتگی:\nهیچ هزینه‌ای در هفته جاری ثبت نشده است.")
        bot.send_message(response, user_id)
        return
    
    report = "📊 **گزارش هفتگی**\n"
    report += f"📅 از {week_start.strftime('%Y/%m/%d')} تا {today.strftime('%Y/%m/%d')}\n"
    report += "═" * 30 + "\n\n"
    
    # گروه‌بندی بر اساس روز
    daily_totals = {}
    daily_details = {}
    
    for username, amount, description, category, expense_date in expenses:
        if expense_date not in daily_totals:
            daily_totals[expense_date] = 0
            daily_details[expense_date] = []
        daily_totals[expense_date] += amount
        daily_details[expense_date].append((category, amount, description))
    
    for expense_date, total in sorted(daily_totals.items()):
        report += f"📅 **{expense_date}**: {total:,} تومان\n"
        # نمایش جزئیات
        for category, amount, description in daily_details[expense_date]:
            report += f"   • {category}: {amount:,} تومان ({description})\n"
        report += "\n"
    
    report += "═" * 30 + "\n"
    total_all = sum(daily_totals.values())
    report += f"💰 **جمع کل هفته: {total_all:,} تومان**"
    
    response = TextMessage(report)
    bot.send_message(response, user_id)

def show_total_today(bot, user_id):
    total = db.get_total_today()
    response = TextMessage(f"💰 مجموع هزینه‌های امروز: {total:,} تومان")
    bot.send_message(response, user_id)

def export_weekly_report(bot, user_id):
    """ارسال گزارش اکسل هفتگی"""
    today = date.today()
    week_start = today - timedelta(days=7)
    
    try:
        filepath = excel_reporter.generate_weekly_report(week_start, today)
        
        if filepath:
            # ارسال فایل اکسل
            with open(filepath, 'rb') as f:
                document = DocumentMessage(
                    file_name=os.path.basename(filepath),
                    file_data=f.read()
                )
                bot.send_message(document, user_id)
        else:
            response = TextMessage("هیچ داده‌ای برای گزارش هفتگی وجود ندارد.")
            bot.send_message(response, user_id)
            
    except Exception as e:
        response = TextMessage(f"خطا در تولید گزارش: {str(e)}")
        bot.send_message(response, user_id)