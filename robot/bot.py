import os
import sys
import json
import time
import logging
import requests
import threading
import re
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

load_dotenv()

from config import Config
from database import Database
from excel_report import ExcelReporter
from utils import to_jalali, to_jalali_with_time, get_jalali_today, get_jalali_month_name, format_jalali_date_range

# تنظیم لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ایجاد نمونه‌ها
db = Database(Config.DB_PATH)
excel_reporter = ExcelReporter(db, Config.REPORTS_DIR)

# تنظیمات API بله
BALE_API_URL = "https://tapi.bale.ai/bot{}/"
BOT_TOKEN = Config.BOT_TOKEN

class BaleBot:
    def __init__(self, token):
        self.token = token
        self.base_url = BALE_API_URL.format(token)
        self.offset = 0
        self.running = True
        
    def send_message(self, chat_id, text):
        """ارسال پیام به بله"""
        url = self.base_url + "sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    def send_document(self, chat_id, file_path, caption=""):
        """ارسال فایل به بله با استفاده از sendDocument"""
        url = self.base_url + "sendDocument"
        
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
            
            with open(file_path, 'rb') as file:
                files = {
                    'document': (os.path.basename(file_path), file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                }
                data = {
                    'chat_id': chat_id,
                    'caption': caption
                }
                
                response = requests.post(url, files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    logger.info(f"File sent successfully to {chat_id}: {os.path.basename(file_path)}")
                    return response.json()
                else:
                    logger.error(f"Error sending file: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error sending document: {e}")
            return None
    
    def get_updates(self):
        """دریافت پیام‌های جدید"""
        url = self.base_url + "getUpdates"
        payload = {
            "offset": self.offset,
            "timeout": 30
        }
        try:
            response = requests.post(url, json=payload, timeout=35)
            if response.status_code == 200:
                return response.json().get('result', [])
            return []
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []
    
    def run(self):
        """حلقه اصلی دریافت پیام‌ها"""
        logger.info("Bot started successfully!")
        logger.info("Listening to all groups and private chats...")
        
        while self.running:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        message = update['message']
                        self.process_message(message)
                        
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(5)
    
    def process_message(self, message):
        """پردازش پیام دریافتی"""
        try:
            chat_id = str(message['chat']['id'])
            user_id = str(message['from']['id'])
            username = message['from'].get('first_name', 'کاربر')
            text = message.get('text', '')
            
            chat_type = message['chat'].get('type', 'private')
            chat_title = message['chat'].get('title', f'گروه {chat_id}')
            
            if chat_type == 'private':
                self.send_message(chat_id, "👋 لطفاً برای ثبت هزینه از یک گروه استفاده کنید.")
                return
            
            if chat_type not in ['group', 'supergroup']:
                return
            
            logger.info(f"Message from group: {chat_title} (ID: {chat_id}) by {username}")
            
            if user_id not in Config.ALLOWED_USERS:
                self.send_message(chat_id, "⛔ شما مجاز به ثبت هزینه نیستید!")
                return
            
            if text.startswith('/'):
                self.handle_command(chat_id, text, user_id, chat_title)
                return
            
            expense_data = self.extract_expense_info(text)
            
            if expense_data:
                amount, description = expense_data
                
                expense_id, category = db.add_expense(
                    user_id=user_id,
                    username=username,
                    group_id=chat_id,
                    group_name=chat_title,
                    amount=amount,
                    description=description
                )
                
                # تاریخ شمسی
                jalali_date = get_jalali_today()
                jalali_time = datetime.now().strftime('%H:%M')
                
                response = (
                    f"✅ هزینه ثبت شد:\n"
                    f"📍 {chat_title}\n"
                    f"💰 مبلغ: {amount:,} تومان\n"
                    f"📝 توضیحات: {description}\n"
                    f"📂 دسته‌بندی: {category}\n"
                    f"📅 تاریخ: {jalali_date}\n"
                    f"🕐 زمان: {jalali_time}\n"
                    f"👤 ثبت کننده: {username}"
                )
                self.send_message(chat_id, response)
            else:
                if '#' in text and 'هزینه' in text:
                    self.send_message(chat_id, 
                        "❌ فرمت پیام صحیح نیست!\n"
                        "لطفاً به این شکل پیام دهید:\n\n"
                        "# هزینه\n"
                        "مبلغ [عدد] تومان [توضیحات]\n\n"
                        "مثال:\n"
                        "# هزینه\n"
                        "مبلغ 1000 تومان بابت سیمان"
                    )
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def extract_expense_info(self, text):
        """استخراج اطلاعات هزینه از متن"""
        patterns = [
            r'^#\s*هزینه\s*\n?\s*مبلغ\s*([\d,]+)\s*تومان?\s*(.+)$',
            r'^#\s*هزینه\s+مبلغ\s*([\d,]+)\s*تومان?\s*(.+)$',
            r'^هزینه\s+([\d,]+)\s+(.+)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '').replace('،', '').strip()
                    description = match.group(2).strip()
                    amount = int(amount_str)
                    if amount > 0 and description:
                        return amount, description
                except:
                    continue
        return None
    
    def handle_command(self, chat_id, text, user_id, group_name):
        """مدیریت دستورات با توجه به گروه"""
        if text == '/start':
            self.send_message(chat_id,
                f"🤖 ربات مدیریت هزینه در گروه {group_name}\n\n"
                "برای ثبت هزینه:\n"
                "# هزینه\n"
                "مبلغ [عدد] تومان [توضیحات]\n\n"
                "مثال:\n"
                "# هزینه\n"
                "مبلغ 1000 تومان بابت سیمان\n\n"
                "📊 دستورات گروه:\n"
                "/today - گزارش امروز این گروه\n"
                "/week - گزارش هفتگی این گروه\n"
                "/month - گزارش ماهانه این گروه\n"
                "/total - مجموع امروز این گروه\n"
                "/groups - لیست گروه‌های فعال\n"
                "/export - خروجی اکسل این گروه\n"
                "/help - راهنما"
            )
        elif text == '/help':
            self.send_message(chat_id,
                "📖 راهنمای استفاده\n\n"
                "🔹 ثبت هزینه:\n"
                "# هزینه\n"
                "مبلغ [مبلغ] تومان [توضیحات]\n\n"
                "🔹 مثال:\n"
                "# هزینه\n"
                "مبلغ 35000 تومان تاکسی\n\n"
                "🔹 دستورات گروه:\n"
                "/today - گزارش امروز (متن)\n"
                "/week - گزارش هفتگی (متن)\n"
                "/month - گزارش ماهانه (متن)\n"
                "/total - مجموع امروز (متن)\n"
                "/groups - لیست گروه‌های فعال (متن)\n"
                "/export - خروجی اکسل (فایل)\n"
                "/help - راهنما (متن)"
            )
        elif text == '/today':
            self.send_today_report(chat_id, group_name)
        elif text == '/week':
            self.send_weekly_report(chat_id, group_name)
        elif text == '/month':
            self.send_monthly_report(chat_id, group_name)
        elif text == '/total':
            total = db.get_total_today(chat_id)
            jalali_date = get_jalali_today()
            self.send_message(chat_id, f"💰 مجموع هزینه‌های امروز گروه {group_name} ({jalali_date}): {total:,} تومان")
        elif text == '/export':
            self.export_weekly_report(chat_id, group_name)
        elif text == '/groups':
            self.show_all_groups(chat_id)
    
    def send_today_report(self, chat_id, group_name):
        """ارسال گزارش امروز برای یک گروه خاص (فقط متن)"""
        today_data = db.get_daily_summary(chat_id)
        jalali_today = get_jalali_today()
        
        if not today_data['category_summary'] and not today_data['user_summary']:
            self.send_message(chat_id, f"📊 گزارش امروز گروه {group_name} ({jalali_today}):\nهیچ هزینه‌ای ثبت نشده است.")
            return
        
        report = f"📊 **گزارش هزینه‌های امروز گروه {group_name}**\n"
        report += f"📅 تاریخ: {jalali_today}\n"
        report += "═" * 30 + "\n\n"
        
        if today_data['category_summary']:
            report += "📂 **دسته‌بندی‌ها:**\n"
            for category, total, count in today_data['category_summary']:
                report += f"   {category}: {total:,} تومان ({count} مورد)\n"
            report += "\n"
        
        if today_data['user_summary']:
            report += "👤 **کاربران:**\n"
            for username, total, count in today_data['user_summary']:
                report += f"   {username}: {total:,} تومان ({count} مورد)\n"
            report += "\n"
        
        report += "═" * 30 + "\n"
        report += f"💰 **جمع کل گروه: {today_data['total']:,} تومان**"
        
        self.send_message(chat_id, report)
    
    def send_weekly_report(self, chat_id, group_name):
        """ارسال گزارش هفتگی برای یک گروه خاص (فقط متن)"""
        today = date.today()
        week_start = today - timedelta(days=7)
        
        jalali_week_start = to_jalali(week_start)
        jalali_today = to_jalali(today)
        
        expenses = db.get_expenses_by_date_range(
            chat_id,
            week_start.isoformat(),
            today.isoformat()
        )
        
        if not expenses:
            self.send_message(chat_id, f"📊 گزارش هفتگی گروه {group_name} ({jalali_week_start} تا {jalali_today}):\nهیچ هزینه‌ای ثبت نشده است.")
            return
        
        # ============ گزارش متنی (فقط در گروه) ============
        report = f"📊 **گزارش هفتگی گروه {group_name}**\n"
        report += f"📅 از {jalali_week_start} تا {jalali_today}\n"
        report += "═" * 30 + "\n\n"
        
        # آماده‌سازی داده‌ها
        daily_totals = {}
        daily_details = {}
        total_all = 0
        category_totals = {}
        user_totals = {}
        
        for username, amount, description, category, expense_date in expenses:
            if expense_date not in daily_totals:
                daily_totals[expense_date] = 0
                daily_details[expense_date] = []
            daily_totals[expense_date] += amount
            daily_details[expense_date].append((category, amount, description, username))
            total_all += amount
            category_totals[category] = category_totals.get(category, 0) + amount
            user_totals[username] = user_totals.get(username, 0) + amount
        
        # نمایش خلاصه روزانه
        report += "📅 **خلاصه روزانه:**\n"
        for expense_date, total in sorted(daily_totals.items()):
            jalali_date = to_jalali(datetime.strptime(expense_date, '%Y-%m-%d').date())
            report += f"   {jalali_date}: {total:,} تومان\n"
        report += "\n"
        
        # نمایش جزئیات هر روز (۳ مورد اول)
        report += "📋 **جزئیات هزینه‌ها:**\n"
        for expense_date, details in sorted(daily_details.items()):
            jalali_date = to_jalali(datetime.strptime(expense_date, '%Y-%m-%d').date())
            report += f"   📅 {jalali_date}:\n"
            for category, amount, description, username in details[:3]:
                report += f"      • {category}: {amount:,} تومان - {description} ({username})\n"
            if len(details) > 3:
                report += f"      • و {len(details) - 3} مورد دیگر...\n"
            report += "\n"
        
        # نمایش دسته‌بندی‌های برتر
        if category_totals:
            report += "📂 **دسته‌بندی‌های برتر:**\n"
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            for category, total in sorted_categories[:5]:
                percentage = (total / total_all * 100) if total_all > 0 else 0
                report += f"   {category}: {total:,} تومان ({percentage:.1f}%)\n"
            report += "\n"
        
        # نمایش کاربران برتر
        if user_totals:
            report += "👤 **کاربران برتر:**\n"
            sorted_users = sorted(user_totals.items(), key=lambda x: x[1], reverse=True)
            for username, total in sorted_users[:5]:
                percentage = (total / total_all * 100) if total_all > 0 else 0
                report += f"   {username}: {total:,} تومان ({percentage:.1f}%)\n"
            report += "\n"
        
        report += "═" * 30 + "\n"
        report += f"💰 **جمع کل هفته: {total_all:,} تومان**\n"
        report += f"📝 **تعداد کل هزینه‌ها: {len(expenses)} مورد**"
        
        # ارسال گزارش متنی فقط به گروه
        self.send_message(chat_id, report)
    
    def send_monthly_report(self, chat_id, group_name):
        """ارسال گزارش ماهانه برای یک گروه خاص (فقط متن)"""
        today = date.today()
        month_start = date(today.year, today.month, 1)
        
        # تاریخ شمسی
        jalali_month_start = to_jalali(month_start)
        jalali_today = to_jalali(today)
        
        expenses = db.get_expenses_by_date_range(
            chat_id,
            month_start.isoformat(),
            today.isoformat()
        )
        
        if not expenses:
            self.send_message(chat_id, f"📊 گزارش ماهانه گروه {group_name} ({jalali_month_start} تا {jalali_today}):\nهیچ هزینه‌ای ثبت نشده است.")
            return
        
        report = f"📊 **گزارش ماهانه گروه {group_name}**\n"
        report += f"📅 از {jalali_month_start} تا {jalali_today}\n"
        report += "═" * 30 + "\n\n"
        
        # محاسبه آمار
        total_all = 0
        daily_totals = {}
        category_totals = {}
        user_totals = {}
        
        for username, amount, description, category, expense_date in expenses:
            total_all += amount
            daily_totals[expense_date] = daily_totals.get(expense_date, 0) + amount
            category_totals[category] = category_totals.get(category, 0) + amount
            user_totals[username] = user_totals.get(username, 0) + amount
        
        # خلاصه ماهانه
        report += f"💰 **جمع کل ماه: {total_all:,} تومان**\n"
        report += f"📝 **تعداد هزینه‌ها: {len(expenses)} مورد**\n"
        report += f"📅 **تعداد روزهای فعال: {len(daily_totals)} روز**\n\n"
        
        # میانگین روزانه
        avg_daily = total_all // len(daily_totals) if daily_totals else 0
        report += f"📊 **میانگین روزانه: {avg_daily:,} تومان**\n\n"
        
        # دسته‌بندی‌های برتر
        if category_totals:
            report += "📂 **دسته‌بندی‌های برتر:**\n"
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            for category, total in sorted_categories[:5]:
                percentage = (total / total_all * 100) if total_all > 0 else 0
                report += f"   {category}: {total:,} تومان ({percentage:.1f}%)\n"
            report += "\n"
        
        # کاربران برتر
        if user_totals:
            report += "👤 **کاربران برتر:**\n"
            sorted_users = sorted(user_totals.items(), key=lambda x: x[1], reverse=True)
            for username, total in sorted_users[:5]:
                percentage = (total / total_all * 100) if total_all > 0 else 0
                report += f"   {username}: {total:,} تومان ({percentage:.1f}%)\n"
        
        # ارسال گزارش متنی فقط به گروه
        self.send_message(chat_id, report)
    
    def show_all_groups(self, chat_id):
        """نمایش لیست تمام گروه‌های فعال (فقط متن)"""
        groups = db.get_all_groups()
        
        if not groups:
            self.send_message(chat_id, "📊 هیچ گروه فعالی یافت نشد.")
            return
        
        report = "📊 **لیست گروه‌های فعال**\n"
        report += "═" * 30 + "\n\n"
        
        for group_id, group_name in groups:
            expenses = db.get_expenses_by_date_range(
                group_id,
                (date.today() - timedelta(days=30)).isoformat(),
                date.today().isoformat()
            )
            count = len(expenses)
            report += f"📍 {group_name}\n"
            report += f"   🆔 {group_id}\n"
            report += f"   📝 تعداد هزینه‌ها: {count}\n\n"
        
        self.send_message(chat_id, report)
    
    def export_weekly_report(self, chat_id, group_name):
        """دستور /export - فقط ارسال فایل اکسل (بدون گزارش متنی)"""
        today = date.today()
        week_start = today - timedelta(days=7)
        
        jalali_week_start = to_jalali(week_start)
        jalali_today = to_jalali(today)
        
        try:
            # تولید فایل اکسل
            filepath = excel_reporter.generate_weekly_report(chat_id, week_start, today, group_name)
            
            if filepath:
                caption = f"📊 گزارش اکسل هفتگی گروه {group_name}\nاز {jalali_week_start} تا {jalali_today}"
                
                # ارسال به گروه
                self.send_document(chat_id, filepath, caption)
                logger.info(f"Excel sent to group: {group_name}")
                
                # ارسال به آیدی‌های مشخص شده
                if Config.EXCEL_RECIPIENTS:
                    for recipient_id in Config.EXCEL_RECIPIENTS:
                        if recipient_id.strip():
                            self.send_document(
                                recipient_id.strip(), 
                                filepath, 
                                f"📊 گزارش هفتگی گروه {group_name}\nاز {jalali_week_start} تا {jalali_today}"
                            )
                            logger.info(f"Excel sent to recipient: {recipient_id}")
                
                # ارسال پیام تایید به گروه
                self.send_message(chat_id, f"✅ فایل اکسل گزارش هفتگی گروه {group_name} ارسال شد.")
                
            else:
                self.send_message(chat_id, f"❌ هیچ داده‌ای برای تولید اکسل گروه {group_name} وجود ندارد.")
                
        except Exception as e:
            self.send_message(chat_id, f"❌ خطا در تولید فایل اکسل: {str(e)}")
            logger.error(f"Error in export_weekly_report: {e}")
    
    def send_weekly_reports_to_all_groups(self):
        """ارسال گزارش هفتگی به تمام گروه‌ها (فقط متن)"""
        try:
            groups = db.get_all_groups()
            
            if not groups:
                logger.info("No groups found for weekly report")
                return
            
            for group_id, group_name in groups:
                try:
                    # فقط گزارش متنی به گروه ارسال می‌شود
                    self.send_weekly_report(group_id, group_name)
                    logger.info(f"Weekly text report sent to group: {group_name}")
                    
                    # تاخیر بین ارسال به گروه‌ها
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error sending weekly report to group {group_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in send_weekly_reports_to_all_groups: {e}")
    
    def stop(self):
        """توقف ربات"""
        self.running = False

def send_weekly_job():
    """کار زمان‌بندی شده برای گزارش هفتگی (فقط متن)"""
    try:
        bot = BaleBot(BOT_TOKEN)
        bot.send_weekly_reports_to_all_groups()
        logger.info("Weekly text reports sent successfully")
    except Exception as e:
        logger.error(f"Error in weekly job: {e}")

def send_auto_report_to_all_groups():
    """ارسال گزارش خودکار روزانه به همه گروه‌ها (فقط متن)"""
    try:
        groups = db.get_groups_with_setting()
        
        if not groups:
            logger.info("No groups configured for auto report")
            return
        
        bot = BaleBot(BOT_TOKEN)
        
        for group_id, group_name, hour, minute, auto_report in groups:
            if auto_report == 1:
                now = datetime.now(pytz.timezone('Asia/Tehran'))
                if now.hour == hour and now.minute == minute:
                    bot.send_today_report(group_id, group_name)
                    logger.info(f"Auto report sent to group: {group_name} ({group_id})")
        
        logger.info("Daily auto reports sent successfully")
    except Exception as e:
        logger.error(f"Error in auto reports: {e}")

def main():
    """تابع اصلی"""
    try:
        scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Tehran'))
        
        # گزارش روزانه - هر ۱ دقیقه یکبار چک می‌کند
        scheduler.add_job(
            send_auto_report_to_all_groups,
            'cron',
            minute='*/1'
        )
        
        # گزارش هفتگی (فقط متن) - هر جمعه ساعت ۲۳:۵۹
        scheduler.add_job(
            send_weekly_job,
            'cron',
            day_of_week='fri',
            hour=23,
            minute=59
        )
        
        scheduler.start()
        logger.info("Scheduler started - Daily reports every minute, Weekly text report on Friday 23:59")
        
        bot = BaleBot(BOT_TOKEN)
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        if 'bot' in locals():
            bot.stop()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()