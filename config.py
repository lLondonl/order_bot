import os

from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# ===== Тексты и варианты — всё, что меняется под клиента =====
COMPANY = "Агро-закупки"
WELCOME = "Здравствуйте! Я приму вашу заявку на продажу урожая."
ASK_CHOICE = "Что хотите продать?"
CHOICES = ["Пшеница", "Ячмень", "Кукуруза", "Подсолнечник"]
ASK_AMOUNT = "Какой объём, в тоннах?"
ASK_PLACE = "Где находится товар?"
ASK_PHONE = "Ваш телефон для связи?"
CONTACTS = "Звоните: +7 900 000-00-00"
