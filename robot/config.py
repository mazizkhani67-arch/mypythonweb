import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ALLOWED_USERS = os.getenv('ALLOWED_USERS', '').split(',')
    EXCEL_RECIPIENTS = os.getenv('EXCEL_RECIPIENTS', '').split(',')
    REPORT_HOUR = int(os.getenv('REPORT_HOUR', '23'))
    REPORT_MINUTE = int(os.getenv('REPORT_MINUTE', '59'))
    DB_PATH = os.getenv('DB_PATH', 'expenses.db')
    REPORTS_DIR = os.getenv('REPORTS_DIR', 'reports')