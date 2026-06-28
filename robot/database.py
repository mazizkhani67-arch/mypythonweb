import sqlite3
from datetime import datetime, date
import json
import os

class Database:
    def __init__(self, db_path='expenses.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """دریافت اتصال به دیتابیس"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def init_db(self):
        """ایجاد جداول مورد نیاز"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # جدول اصلی هزینه‌ها با فیلد group_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                username TEXT,
                group_id TEXT,
                group_name TEXT,
                amount INTEGER,
                description TEXT,
                category TEXT,
                expense_date TEXT,
                created_at TEXT
            )
        ''')
        
        # جدول دسته‌بندی‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                keywords TEXT
            )
        ''')
        
        # جدول تنظیمات گروه‌ها (برای ارسال گزارش خودکار)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_settings (
                group_id TEXT PRIMARY KEY,
                group_name TEXT,
                report_hour INTEGER DEFAULT 23,
                report_minute INTEGER DEFAULT 59,
                auto_report INTEGER DEFAULT 1
            )
        ''')
        
        # اضافه کردن دسته‌بندی‌های پیش‌فرض
        default_categories = [
            ('خوراک', 'غذا,نهار,شام,صبحانه,میوه,سبزی,نان,برنج'),
            ('حمل و نقل', 'تاکسی,بنزین,گازوئیل,بلیط,اتوبوس,قطار,هواپیما'),
            ('مسکن', 'اجاره,قبوض,برق,آب,گاز,تلفن,شارژ'),
            ('خرید', 'لباس,کفش,لوازم,خانگی,دیجیتال,موبایل'),
            ('درمان', 'دارو,دکتر,بیمارستان,آزمایش,فیزیوتراپی'),
            ('تفریح', 'سینما,رستوران,کافه,گردش,تفریح,ورزش'),
            ('آموزش', 'کتاب,کلاس,آموزش,دانشگاه,شهریه'),
            ('متفرقه', 'سایر,متفرقه,هدیه,سرویس')
        ]
        
        for name, keywords in default_categories:
            try:
                cursor.execute(
                    'INSERT OR IGNORE INTO categories (name, keywords) VALUES (?, ?)',
                    (name, keywords)
                )
            except sqlite3.IntegrityError:
                pass
        
        conn.commit()
        conn.close()
    
    def detect_category(self, description):
        """تشخیص دسته‌بندی بر اساس توضیحات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, keywords FROM categories')
        categories = cursor.fetchall()
        conn.close()
        
        description_lower = description.lower()
        
        for category_name, keywords in categories:
            if keywords:
                for keyword in keywords.split(','):
                    if keyword.strip() in description_lower:
                        return category_name
        
        return 'متفرقه'
    
    def add_group_setting(self, group_id, group_name):
        """افزودن یا به‌روزرسانی تنظیمات گروه"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO group_settings (group_id, group_name)
            VALUES (?, ?)
        ''', (group_id, group_name))
        
        conn.commit()
        conn.close()
    
    def add_expense(self, user_id, username, group_id, group_name, amount, description):
        """ثبت هزینه جدید با دسته‌بندی و گروه"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = date.today().isoformat()
        now = datetime.now().isoformat()
        
        # تشخیص دسته‌بندی
        category = self.detect_category(description)
        
        # ثبت گروه در تنظیمات
        self.add_group_setting(group_id, group_name)
        
        cursor.execute('''
            INSERT INTO expenses 
            (user_id, username, group_id, group_name, amount, description, category, expense_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, group_id, group_name, amount, description, category, today, now))
        
        expense_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return expense_id, category
    
    def get_today_expenses_grouped(self, group_id):
        """دریافت هزینه‌های امروز برای یک گروه به صورت دسته‌بندی شده"""
        conn = self.get_connection()
        cursor = conn.cursor()
        today = date.today().isoformat()
        
        cursor.execute('''
            SELECT 
                category,
                SUM(amount) as total,
                COUNT(*) as count,
                GROUP_CONCAT(description, ' | ') as descriptions
            FROM expenses
            WHERE expense_date = ? AND group_id = ?
            GROUP BY category
            ORDER BY total DESC
        ''', (today, group_id))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_daily_summary(self, group_id, target_date=None):
        """گزارش خلاصه روزانه برای یک گروه با دسته‌بندی"""
        if target_date is None:
            target_date = date.today().isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # دریافت مجموع هر دسته‌بندی
        cursor.execute('''
            SELECT 
                category,
                SUM(amount) as total,
                COUNT(*) as count
            FROM expenses
            WHERE expense_date = ? AND group_id = ?
            GROUP BY category
            ORDER BY total DESC
        ''', (target_date, group_id))
        
        category_summary = cursor.fetchall()
        
        # دریافت جزئیات هر کاربر
        cursor.execute('''
            SELECT 
                username,
                SUM(amount) as total,
                COUNT(*) as count
            FROM expenses
            WHERE expense_date = ? AND group_id = ?
            GROUP BY username
            ORDER BY total DESC
        ''', (target_date, group_id))
        
        user_summary = cursor.fetchall()
        
        # دریافت کل هزینه‌ها
        cursor.execute('''
            SELECT SUM(amount) FROM expenses WHERE expense_date = ? AND group_id = ?
        ''', (target_date, group_id))
        
        total = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'category_summary': category_summary,
            'user_summary': user_summary,
            'total': total
        }
    
    def get_weekly_data(self, group_id, start_date, end_date):
        """دریافت داده‌های هفتگی برای یک گروه"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                expense_date,
                username,
                category,
                amount,
                description,
                created_at
            FROM expenses
            WHERE group_id = ? AND expense_date BETWEEN ? AND ?
            ORDER BY expense_date DESC, created_at DESC
        ''', (group_id, start_date, end_date))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_expenses_by_date_range(self, group_id, start_date, end_date):
        """دریافت هزینه‌ها در بازه زمانی برای یک گروه"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, amount, description, category, expense_date
            FROM expenses
            WHERE group_id = ? AND expense_date BETWEEN ? AND ?
            ORDER BY expense_date DESC, created_at DESC
        ''', (group_id, start_date, end_date))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_all_groups(self):
        """دریافت لیست تمام گروه‌های فعال"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT group_id, group_name 
            FROM expenses 
            ORDER BY group_name
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_groups_with_setting(self):
        """دریافت گروه‌هایی که تنظیمات دارند"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT group_id, group_name, report_hour, report_minute, auto_report
            FROM group_settings
            WHERE auto_report = 1
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def delete_expense(self, expense_id, group_id):
        """حذف هزینه با شناسه و گروه"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'DELETE FROM expenses WHERE id = ? AND group_id = ?', 
            (expense_id, group_id)
        )
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_total_today(self, group_id):
        """مجموع هزینه‌های امروز برای یک گروه"""
        conn = self.get_connection()
        cursor = conn.cursor()
        today = date.today().isoformat()
        
        cursor.execute('''
            SELECT SUM(amount) FROM expenses 
            WHERE expense_date = ? AND group_id = ?
        ''', (today, group_id))
        
        total = cursor.fetchone()[0] or 0
        conn.close()
        
        return total