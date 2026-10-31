import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeChat

import db
from config import ADMIN_ID, BOT_TOKEN
from handlers import router


async def main():
    db.init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    # Меню для всех клиентов
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="cancel", description="Отменить заявку"),
    ])
    # Расширенное меню только для админа
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Главное меню"),
            BotCommand(command="cancel", description="Отменить заявку"),
            BotCommand(command="stats", description="Статистика заявок"),
            BotCommand(command="export", description="Все заявки в Excel"),
        ],
        scope=BotCommandScopeChat(chat_id=ADMIN_ID),
    )
    print("Бот заявок запущен. Остановить: Ctrl+C")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
