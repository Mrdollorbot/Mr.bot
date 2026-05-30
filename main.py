import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# Тіркелген мәліметтер автоматты түрде енгізілді
TOKEN = "8905449996:AAHhQ0Ajd0vijlBjZc03x0gJQ7V5Mw8C7aE"
ADMIN_ID = 7536197008

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Үйлердің бағасы мен табысы
HOUSE_PRICES = {
    1: {"name": "Обычный дом", "price": 100000, "income": 500},
    2: {"name": "Коттедж", "price": 500000, "income": 2500},
    3: {"name": "Вилла", "price": 2500000, "income": 10000},
    4: {"name": "Остров", "price": 10000000, "income": 15000}
}

# Бизнес бағалары мен табыстары
BIZ_PRICES = {
    1: {"name": "Минимаркет", "price": 50000, "income": 1000},
    2: {"name": "Супермаркет", "price": 450000, "income": 10000},
    3: {"name": "Транспортная компания", "price": 1500000, "income": 25000},
    4: {"name": "IT компания", "price": 15000000, "income": 350000},
    5: {"name": "Туристическая компания государства", "price": 35000000, "income": 1000000}
}

# Мемлекеттік лауазымдар жүйесі
JOBS = {
    1: {"name": "Всемирный Президент", "salary": 10000000000},
    2: {"name": "Президент", "salary": 10000000}, 
    3: {"name": "Депутат", "salary": 1000000},
    4: {"name": "Судья", "salary": 850000},
    5: {"name": "Мэр", "salary": 800000},
    6: {"name": "FBI", "salary": 700000},
    7: {"name": "Полиция", "salary": 100000},
    8: {"name": "Работник Супермаркета", "salary": 10000},
    9: {"name": "Курьер", "salary": 2000},
    10: {"name": "Бомж", "salary": 100}
}

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        balance INTEGER DEFAULT 0,
        last_bonus TEXT,
        last_income TEXT,
        last_biz_income TEXT,
        last_job_income TEXT,
        job_id INTEGER DEFAULT 10,
        job_title TEXT DEFAULT 'Бомж',
        houses INTEGER DEFAULT 0,
        cottages INTEGER DEFAULT 0,
        villas INTEGER DEFAULT 0,
        islands INTEGER DEFAULT 0,
        minimarket INTEGER DEFAULT 0,
        supermarket INTEGER DEFAULT 0,
        transport INTEGER DEFAULT 0,
        it_company INTEGER DEFAULT 0,
        tourism INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect("users.db")

def register_user_if_not_exists(user_id, username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO users (user_id, username, balance, last_bonus, last_income, last_biz_income, last_job_income,
            job_id, job_title, houses, cottages, villas, islands, minimarket, supermarket, transport, it_company, tourism) 
            VALUES (?, ?, 100, None, None, None, ?, 10, 'Бомж', 0, 0, 0, 0, 0, 0, 0, 0, 0)
        """, (user_id, username, current_time_str))
        conn.commit()
    conn.close()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    register_user_if_not_exists(user_id, message.from_user.username or "User")
    await message.reply(
        f"👋 Привет, {message.from_user.full_name}!\n\n"
        f"🤖 Вы зарегистрированы! Баланс: **100 $**\n"
        f"💼 Проверить баланс: **Баланс** или **Б**\n"
        f"🛒 Магазин недвижимости: **Магазин**\n"
        f"🏢 Открыть бизнес: **Бизнес**\n"
        f"💵 Сбор дохода бизнеса: **БД**\n"
        f"👔 Получить зарплату по должности: **Зарплата** или **Зп**"
    )

@dp.message(F.text.lower().startswith("дать работу"))
async def give_job_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ Вы не являетесь Всемирным Президентом (Админом)!")
        return

    if not message.reply_to_message:
        await message.reply("❌ Ответьте на сообщение пользователя, которому хотите дать работу!")
        return

    parts = message.text.split()
    if len(parts) < 3 or not parts[2].isdigit():
        await message.reply("❌ Неверный формат. Пример: `Дать работу 3` или `Дать работу 2 ОАЭ`")
        return

    job_id = int(parts[2])
    if job_id not in JOBS:
        await message.reply("❌ Неверный номер должности. Выберите от 1 до 10.")
        return

    target_user_id = message.reply_to_message.from_user.id
    target_username = message.reply_to_message.from_user.first_name
    register_user_if_not_exists(target_user_id, message.reply_to_message.from_user.username or "User")

    job_title = JOBS[job_id]["name"]
    if job_id == 2:
        country = " ".join(parts[3:]) if len(parts) >= 4 else "страны"
        job_title = f"Президент {country}"

    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET job_id = ?, job_title = ?, last_job_income = ? 
        WHERE user_id = ?
    """, (job_id, job_title, current_time_str, target_user_id))
    conn.commit()
    conn.close()

    await message.reply(f"👑 Всемирный Президент назначил {target_username} на должность: **{job_title}**!")

@dp.message(F.text.in_({"Зарплата", "зарплата", "Зп", "зп"}))
async def collect_salary_cmd(message: types.Message):
    user_id = message.from_user.id
    current_time = datetime.now()
    register_user_if_not_exists(user_id, message.from_user.username or "User")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance, last_job_income, job_id, job_title FROM users WHERE user_id = ?", (user_id,))
    balance, last_job_str, job_id, job_title = cursor.fetchone()

    salary_per_hour = JOBS[job_id]["salary"]
    last_job_time = datetime.strptime(last_job_str, "%Y-%m-%d %H:%M:%S")
    hours_passed = int((current_time - last_job_time).total_seconds() // 3600)

    if hours_passed < 1:
        minutes_remaining = 60 - int(((current_time - last_job_time).total_seconds() % 3600) // 60)
        await message.reply(f"⏳ Ваша зарплата капает! Вы работаете как **{job_title}**. Приходите через **{minutes_remaining} мин.**")
        conn.close()
        return

    total_salary = salary_per_hour * hours_passed
    new_balance = balance + total_salary
    new_job_time_str = (last_job_time + timedelta(hours=hours_passed)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("UPDATE users SET balance = ?, last_job_income = ? WHERE user_id = ?", (new_balance, new_job_time_str, user_id))
    conn.commit()
    conn.close()

    await message.reply(f"💼 Вы получили зарплату за **{hours_passed} ч.** на должности **{job_title}** в размере **{total_salary:,} $**!\n💰 Баланс: **{new_balance:,} $**")

@dp.message(F.text.in_({"Баланс", "баланс", "Б", "б"}))
async def balance_cmd(message: types.Message):
    user_id = message.from_user.id
    register_user_if_not_exists(user_id, message.from_user.username or "User")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance, job_title, job_id FROM users WHERE user_id = ?", (user_id,))
    balance, job_title, job_id = cursor.fetchone()
    conn.close()
    
    salary = JOBS[job_id]["salary"]
    await message.reply(
        f"💰 **Ваш текущий баланс:** {balance:,} $\n"
        f"👔 **Должность:** {job_title} ({salary:,} $/час)"
    )

@dp.message(F.text.in_({"Бизнес", "бизнес", "Биз", "биз"}))
async def biz_shop_cmd(message: types.Message):
    text = (
        "🏢 **Магазин Бизнеса:**\n\n"
        f"1. {BIZ_PRICES[1]['name']} - {BIZ_PRICES[1]['price']:,} $ (+{BIZ_PRICES[1]['income']:,} $/ч)\n"
        f"2. {BIZ_PRICES[2]['name']} - {BIZ_PRICES[2]['price']:,} $ (+{BIZ_PRICES[2]['income']:,} $/ч)\n"
        f"3. {BIZ_PRICES[3]['name']} - {BIZ_PRICES[3]['price']:,} $ (+{BIZ_PRICES[3]['income']:,} $/ч)\n"
        f"4. {BIZ_PRICES[4]['name']} - {BIZ_PRICES[4]['price']:,} $ (+{BIZ_PRICES[4]['income']:,} $/ч)\n"
        f"5. {BIZ_PRICES[5]['name']} - {BIZ_PRICES[5]['price']:,} $ (+{BIZ_PRICES[5]['income']:,} $/ч)\n\n"
        "💼 Чтобы открыть бизнес, напишите: `Открыть бизнес [номер]`"
    )
    await message.reply(text, parse_mode="Markdown")

@dp.message(F.text.lower().startswith("открыть бизнес"))
async def buy_business_cmd(message: types.Message):
    user_id = message.from_user.id
    parts = message.text.split()
    if len(parts) < 3 or not parts[2].isdigit(): return
    choice = int(parts[2])
    if choice not in BIZ_PRICES: return
    register_user_if_not_exists(user_id, message.from_user.username or "User")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    balance = cursor.fetchone()[0]
    if balance < BIZ_PRICES[choice]["price"]: await message.reply("❌ Недостаточно средств!"); conn.close(); return
    new_balance = balance - BIZ_PRICES[choice]["price"]
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cols = ["minimarket", "supermarket", "transport", "it_company", "tourism"]
    cursor.execute(f"UPDATE users SET balance = ?, {cols[choice-1]} = {cols[choice-1]} + 1 WHERE user_id = ?", (new_balance, user_id))
    cursor.execute("SELECT last_biz_income FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone()[0] is None: cursor.execute("UPDATE users SET last_biz_income = ? WHERE user_id = ?", (current_time_str, user_id))
    conn.commit(); conn.close()
    await message.reply(f"🎉 Вы успешно открыли бизнес: **{BIZ_PRICES[choice]['name']}**!")

@dp.message(F.text.in_({"БД", "бд", "Бизнес доход"}))
async def collect_biz_income_cmd(message: types.Message):
    user_id = message.from_user.id
    current_time = datetime.now()
    register_user_if_not_exists(user_id, message.from_user.username or "User")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance, last_biz_income, minimarket, supermarket, transport, it_company, tourism FROM users WHERE user_id = ?", (user_id,))
    balance, last_biz_income_str, minimarket, supermarket, transport, it_company, tourism = cursor.fetchone()
    hourly_income = (minimarket * 1000) + (supermarket * 10000) + (transport * 25000) + (it_company * 350000) + (tourism * 1000000)
    if hourly_income == 0: await message.reply("❌ У вас еще нет работающего бизнеса."); conn.close(); return
    last_income_time = datetime.strptime(last_biz_income_str, "%Y-%m-%d %H:%M:%S")
    hours_passed = int((current_time - last_income_time).total_seconds() // 3600)
    if hours_passed < 1: await message.reply("⏳ Доход еще не накопился!"); conn.close(); return
    total_earned = hourly_income * hours_passed
    new_income_time_str = (last_income_time + timedelta(hours=hours_passed)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE users SET balance = balance + ?, last_biz_income = ? WHERE user_id = ?", (total_earned, new_income_time_str, user_id))
    conn.commit(); conn.close()
    await message.reply(f"💵 Собрана прибыль с бизнеса: **{total_earned:,} $**!")

@dp.message(F.text.in_({"Мой бизнес", "мой бизнес"}))
async def my_business_cmd(message: types.Message):
    user_id = message.from_user.id
    register_user_if_not_exists(user_id, message.from_user.username or "User")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT minimarket, supermarket, transport, it_company, tourism FROM users WHERE user_id = ?", (user_id,))
    minimarket, supermarket, transport, it_company, tourism = cursor.fetchone()
    conn.close()
    hourly_income = (minimarket * 1000) + (supermarket * 10000) + (transport * 25000) + (it_company * 350000) + (tourism * 1000000)
    text = (
        f"🏢 **Ваш бизнес ({message.from_user.first_name}):**\n\n"
        f"🏪 Минимаркеты: {minimarket}\n"
        f"🛒 Супермаркеты: {supermarket}\n"
        f"🚛 Транспортные компании: {transport}\n"
        f"💻 IT компании: {it_company}\n"
        f"🌍 Туристические компании: {tourism}\n\n"
        f"📈 Общая прибыль: **{hourly_income:,} $/час**\n"
        " Напишите **БД**, чтобы собрать кассу."
    )
    await message.reply(text, parse_mode="Markdown")

@dp.message(F.text.lower().startswith(("перевод ", "п ")))
async def transfer_money_cmd(message: types.Message):
    if not message.reply_to_message: return
    sender_id, recipient_id = message.from_user.id, message.reply_to_message.from_user.id
    if sender_id == recipient_id: return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit(): return
    amount = int(parts[1])
    register_user_if_not_exists(sender_id, message.from_user.username or "User")
    register_user_if_not_exists(recipient_id, message.reply_to_message.from_user.username or "User")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (sender_id,))
    if cursor.fetchone()[0] < amount: conn.close(); return
    cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, sender_id))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, recipient_id))
    conn.commit(); conn.close()
    await message.reply(f"💸 Переведено **{amount:,} $** для {message.reply_to_message.from_user.first_name}!")

@dp.message(F.text.in_({"Магазин", "магазин", "М", "м"}))
async def shop_cmd(message: types.Message):
    text = f"🏠 **Магазин недвижимости**:\n\n1. {HOUSE_PRICES[1]['name']} — {HOUSE_PRICES[1]['price']:,} $\n2. {HOUSE_PRICES[2]['name']} — {HOUSE_PRICES[2]['price']:,} $\n3. {HOUSE_PRICES[3]['name']} — {HOUSE_PRICES[3]['price']:,} $\n4. {HOUSE_PRICES[4]['name']} — {HOUSE_PRICES[4]['price']:,} $\n\n🛒 Напишите: `Купить дом [номер]`"
    await message.reply(text, parse_mode="Markdown")

@dp.message(F.text.lower().startswith("купить дом"))
async def buy_house_cmd(message: types.Message):
    user_id = message.from_user.id
    parts = message.text.split()
    if len(parts) < 3 or not parts[2].isdigit(): return
    choice = int(parts[2])
    if choice not in HOUSE_PRICES: return
    register_user_if_not_exists(user_id, message.from_user.username or "User")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone()[0] < HOUSE_PRICES[choice]["price"]: await message.reply("❌ Нет денег"); conn.close(); return
    cols = ["houses", "cottages", "villas", "islands"]
    cursor.execute(f"UPDATE users SET balance = balance - ?, {cols[choice-1]} = {cols[choice-1]} + 1 WHERE user_id = ?", (HOUSE_PRICES[choice]["price"], user_id))
    conn.commit(); conn.close()
    await message.reply(f"🎉 Вы купили **{HOUSE_PRICES[choice]['name']}**!")

@dp.message(F.text.in_({"Имущество", "имущество", "И", "и"}))
async def inventory_cmd(message: types.Message):
    user_id = message.from_user.id
    register_user_if_not_exists(user_id, message.from_user.username or "User")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT houses, cottages, villas, islands FROM users WHERE user_id = ?", (user_id,))
    houses, cottages, villas, islands = cursor.fetchone()
    conn.close()
    total_income = (houses * 500) + (cottages * 2500) + (villas * 10000) + (islands * 15000)
    await message.reply(f"💼 **Ваше имущество:**\n\n🏠 Дома: {houses}\n🏡 Коттеджи: {cottages}\n🏰 Виллы: {villas}\n🏝 Острова: {islands}\n\n💵 Доход: **{total_income:,} $/день**")

@dp.message(Command("bonus"))
async def bonus_cmd(message: types.Message):
    user_id = message.from_user.id
    current_time = datetime.now()
    register_user_if_not_exists(user_id, message.from_user.username or "User")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance, last_bonus FROM users WHERE user_id = ?", (user_id,))
    balance, last_bonus_str = cursor.fetchone()
    if last_bonus_str and current_time - datetime.strptime(last_bonus_str, "%Y-%m-%d %H:%M:%S") < timedelta(hours=12):
        await message.reply("❌ Бонус еще недоступен!"); conn.close(); return
    cursor.execute("UPDATE users SET balance = balance + 2500, last_bonus = ? WHERE user_id = ?", (current_time.strftime("%Y-%m-%d %H:%M:%S"), user_id))
    conn.commit(); conn.close()
    await message.reply("🎁 Получено **2500 $**!")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
