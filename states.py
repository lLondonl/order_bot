from aiogram.fsm.state import State, StatesGroup


class Order(StatesGroup):
    crop = State()
    tonnes = State()
    place = State()
    phone = State()
    confirm = State()
