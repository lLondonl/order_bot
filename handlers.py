from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

import db
from config import ADMIN_ID
from keyboards import classes_keyboard, confirm_keyboard, crops_keyboard, menu_for, take_keyboard
from states import Order

router = Router()


# ===== Команды и меню (всегда выше шагов анкеты) =====
@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Здравствуйте! Я приму вашу заявку.", reply_markup=menu_for(message.from_user.id))


@router.message(Command("cancel"))
@router.message(F.text == "Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Заявка отменена", reply_markup=menu_for(message.from_user.id))


@router.message(F.text == "Новая заявка")
async def new_order(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Что хотите продать?", reply_markup=crops_keyboard())


@router.message(F.text == "Мои заявки")
async def my_orders(message: Message):
    rows = db.user_orders(message.from_user.id)
    if not rows:
        await message.answer("У вас пока нет заявок")
        return
    lines = ["Ваши последние заявки:"]
    for order_id, created, crop, tonnes, place, phone, status in rows:
        lines.append(
            f"\n№{order_id} от {created} — {status}\n"
            f"{crop}, {tonnes:g} т, {place}\n"
            f"Телефон: {phone}"
        )
    await message.answer("\n".join(lines))


@router.message(F.text == "Контакты")
async def contacts(message: Message):
    await message.answer("Звоните: +7 900 000-00-00\nПишите: @your_username")


# ===== Выбор культуры и класса =====
@router.callback_query(F.data.startswith("crop:"))
async def crop_chosen(callback: CallbackQuery, state: FSMContext):
    crop = callback.data.split(":")[1]
    if crop == "Пшеница":
        await callback.message.answer("Какой класс?", reply_markup=classes_keyboard())
    else:
        await state.update_data(crop=crop)
        await state.set_state(Order.tonnes)
        await callback.message.answer(f"{crop}. Какой объём, в тоннах?")
    await callback.answer()


@router.callback_query(F.data.startswith("class:"))
async def class_chosen(callback: CallbackQuery, state: FSMContext):
    grain_class = callback.data.split(":")[1]
    crop = f"Пшеница {grain_class} кл"
    await state.update_data(crop=crop)
    await state.set_state(Order.tonnes)
    await callback.message.answer(f"{crop}. Какой объём, в тоннах?")
    await callback.answer()

@router.message(Command("stats"))
@router.message(F.text == "Статистика")
async def stats_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    (count, tonnes), by_crop = db.stats()
    if not count:
        await message.answer("Заявок пока нет")
        return
    lines = [f"Всего заявок: {count}, объём: {tonnes:g} т", ""]
    for crop, n, t in by_crop:
        lines.append(f"{crop}: {n} шт., {t:g} т")
    await message.answer("\n".join(lines))


@router.message(Command("export"))
async def export(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    path = db.export_xlsx()
    await message.answer_document(FSInputFile(path), caption="Все заявки")

# ===== Шаги анкеты =====
@router.message(Order.tonnes)
async def got_tonnes(message: Message, state: FSMContext):
    text = (message.text or "").replace(",", ".").replace(" ", "")
    try:
        tonnes = float(text)
    except ValueError:
        await message.answer("Напишите число, например 60")
        return
    await state.update_data(tonnes=tonnes)
    await state.set_state(Order.place)
    await message.answer("Где находится товар? Район или населённый пункт")


@router.message(Order.place)
async def got_place(message: Message, state: FSMContext):
    await state.update_data(place=message.text)
    await state.set_state(Order.phone)
    await message.answer("Ваш телефон для связи?")


@router.message(Order.phone)
async def got_phone(message: Message, state: FSMContext):
    # Здесь заявку НЕ сохраняем — только показываем сводку для проверки
    await state.update_data(phone=message.text)
    data = await state.get_data()
    await state.set_state(Order.confirm)
    await message.answer(
        "Проверьте заявку:\n\n"
        f"Культура: {data['crop']}\n"
        f"Объём: {data['tonnes']:g} т\n"
        f"Место: {data['place']}\n"
        f"Телефон: {data['phone']}",
        reply_markup=confirm_keyboard(),
    )


# ===== Подтверждение =====
@router.callback_query(Order.confirm, F.data == "confirm:yes")
async def confirm_yes(callback: CallbackQuery, state: FSMContext):
    # Сохраняем в базу только после «Подтвердить»
    data = await state.get_data()
    order_id = db.add_order(
        callback.from_user.id,
        callback.from_user.username or "",
        data["crop"], data["tonnes"], data["place"], data["phone"],
    )
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"Заявка №{order_id} принята! Мы свяжемся с вами в ближайшее время.",
        reply_markup=menu_for(callback.from_user.id),
    )
    await callback.answer()

    # Уведомление менеджеру
    user = callback.from_user
    await callback.bot.send_message(
        ADMIN_ID,
        f"Новая заявка №{order_id}\n"
        f"{data['crop']}, {data['tonnes']:g} т\n"
        f"Место: {data['place']}\n"
        f"Телефон: {data['phone']}\n"
        f"Клиент: {user.full_name} @{user.username or '-'}",
        reply_markup=take_keyboard(order_id),
    )

@router.callback_query(Order.confirm, F.data == "confirm:no")
async def confirm_no(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Хорошо, заполним заново. Что хотите продать?",
                                  reply_markup=crops_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("take:"))
async def take_order(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Только для менеджера", show_alert=True)
        return
    order_id = int(callback.data.split(":")[1])
    order = db.get_order(order_id)
    if order is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return
    client_id, status = order
    if status != "новая":
        await callback.answer(f"Заявка уже в статусе: {status}")
        return
    db.set_status(order_id, "в работе")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"Заявка №{order_id} взята в работу")
    await callback.bot.send_message(
        client_id,
        f"Ваша заявка №{order_id} взята в работу. Скоро с вами свяжемся.",
    )
    await callback.answer()

@router.message(Order.confirm)
async def confirm_text(message: Message):
    await message.answer("Нажмите кнопку под заявкой: «Подтвердить» или «Заполнить заново».")
