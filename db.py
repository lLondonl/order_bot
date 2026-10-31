import os
import sqlite3
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font


def export_xlsx(path="orders.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Заявки"
    ws.append(["№", "Дата", "ID клиента", "Username", "Культура", "Тонны", "Место", "Телефон", "Статус"])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for row in all_orders():
        ws.append(list(row))
    widths = [6, 18, 14, 16, 16, 10, 24, 18, 12]
    for i, w in enumerate(widths):
        ws.column_dimensions[chr(65 + i)].width = w
    wb.save(path)
    return path

# База всегда лежит рядом с этим файлом, откуда бы ни запускали бота
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orders.db")


def init_db():
    with sqlite3.connect(DB_FILE) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created TEXT,
                user_id INTEGER,
                username TEXT,
                crop TEXT,
                tonnes REAL,
                place TEXT,
                phone TEXT,
                status TEXT DEFAULT 'новая'
            )
        """)


def add_order(user_id, username, crop, tonnes, place, phone):
    with sqlite3.connect(DB_FILE) as con:
        cur = con.execute(
            "INSERT INTO orders (created, user_id, username, crop, tonnes, place, phone) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M"), user_id, username, crop, tonnes, place, phone),
        )
        return cur.lastrowid


def user_orders(user_id, limit=5):
    with sqlite3.connect(DB_FILE) as con:
        return con.execute(
            "SELECT id, created, crop, tonnes, place, phone, status FROM orders "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()


def all_orders():
    with sqlite3.connect(DB_FILE) as con:
        return con.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()

def stats():
    with sqlite3.connect(DB_FILE) as con:
        total = con.execute("SELECT COUNT(*), SUM(tonnes) FROM orders").fetchone()
        by_crop = con.execute(
            "SELECT crop, COUNT(*), SUM(tonnes) FROM orders "
            "GROUP BY crop ORDER BY SUM(tonnes) DESC"
        ).fetchall()
    return total, by_crop

def set_status(order_id, status):
    with sqlite3.connect(DB_FILE) as con:
        con.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))


def get_order(order_id):
    with sqlite3.connect(DB_FILE) as con:
        return con.execute(
            "SELECT user_id, status FROM orders WHERE id = ?", (order_id,)
        ).fetchone()