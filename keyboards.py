from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_ID, CHOICES

# Меню для клиентов
MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Новая заявка")],
        [KeyboardButton(text="Мои заявки"), KeyboardButton(text="Контакты")],
    ],
    resize_keyboard=True,
)

# Меню для админа: то же + «Статистика»
ADMIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Новая заявка")],
        [KeyboardButton(text="Мои заявки"), KeyboardButton(text="Контакты")],
        [KeyboardButton(text="Статистика")],
    ],
    resize_keyboard=True,
)


def menu_for(user_id):
    return ADMIN_MENU if user_id == ADMIN_ID else MENU


def crops_keyboard():
    kb = InlineKeyboardBuilder()
    for crop in CHOICES:
        kb.button(text=crop, callback_data=f"crop:{crop}")
    kb.adjust(2)
    return kb.as_markup()


def classes_keyboard():
    kb = InlineKeyboardBuilder()
    for c in ["3", "4", "5"]:
        kb.button(text=f"{c} класс", callback_data=f"class:{c}")
    kb.adjust(3)
    return kb.as_markup()


def confirm_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Подтвердить", callback_data="confirm:yes")
    kb.button(text="Заполнить заново", callback_data="confirm:no")
    kb.adjust(2)
    return kb.as_markup()


def take_keyboard(order_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="Взять в работу", callback_data=f"take:{order_id}")
    return kb.as_markup()
