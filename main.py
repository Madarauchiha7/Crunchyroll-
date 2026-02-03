import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db import *

BOT_TOKEN = "8347380502:AAEB0BFbEC6F1JOLy2ORFTQgqYXe9_Av4bI"
ADMIN_IDS = {8124463994, 8333326568}
SUPPORT = "@XxSirBmgoxX"
CHANNELS = ["@PREMIUMPERKS1"]

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ---------- KEYBOARDS ----------

def join_kb():
    kb = InlineKeyboardBuilder()
    for ch in CHANNELS:
        kb.button(text="📢 Join Channel", url=f"https://t.me/{ch.replace('@','')}")
    kb.button(text="✅ CHECK", callback_data="check")
    kb.adjust(1)
    return kb.as_markup()

def menu(is_admin=False):
    kb = InlineKeyboardBuilder()
    kb.button(text="⚡GENERATE ⚡", callback_data="gen")
    kb.button(text="📦 STOCK", callback_data="stock")
    kb.button(text="🆘 SUPPORT", callback_data="support")
    if is_admin:
        kb.button(text="🛠 ADMIN PANEL", callback_data="admin")
    kb.adjust(1)
    return kb.as_markup()

def admin_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ ADD STOCK", callback_data="add_stock")
    kb.button(text="👥 TOTAL USERS", callback_data="users")
    kb.button(text="📣 BROADCAST", callback_data="broadcast")
    kb.button(text="⬅️ BACK", callback_data="back")
    kb.adjust(1)
    return kb.as_markup()

# ---------- FUNCTIONS ----------

async def joined(user_id):
    for ch in CHANNELS:
        try:
            m = await bot.get_chat_member(ch, user_id)
            if m.status == "left":
                return False
        except:
            return False
    return True

# ---------- START ----------

@dp.message(F.text == "/start")
async def start(m: Message):
    if not await joined(m.from_user.id):
        await m.answer(
            "must join all required channels first❌",
            reply_markup=join_kb()
        )
        return

    await m.answer(
        "Wealcom our bot 🎉",
        reply_markup=menu(is_admin=m.from_user.id == ADMIN_ID)
    )

@dp.callback_query(F.data == "check")
async def check_join(c: CallbackQuery):
    if not await joined(c.from_user.id):
        await c.answer("❌ Still not joined", show_alert=True)
        return
    await c.message.edit_text(
        "Wealcom our bot 🎉",
        reply_markup=menu(is_admin=c.from_user.id == ADMIN_ID)
    )

# ---------- USER OPTIONS ----------

@dp.callback_query(F.data == "gen")
async def gen(c: CallbackQuery):
    if not await joined(c.from_user.id):
        await c.message.answer("must join all required channels first❌", reply_markup=join_kb())
        return

    if not await can_use(c.from_user.id):
        await c.message.answer(
            "You have already redeemed once and can generate an account again after 24 hours ✅"
        )
        return

    acc = await get_stock()
    if not acc:
        await c.message.answer("❌ Stock out!")
        return

    text = f"""✅ Withdrawal Successful!



🎁 Crunchyroll Account Details:
📧 {acc.split('|')[0].strip()}
🔑 {acc.split('|')[1].strip()}

🌍 {acc.split('|')[2].strip()}

📲 Use official Crunchyroll app to log in.
⚠️ Do not change the password.

📸 Please send a screenshot after successful login here 
{SUPPORT} to get featured in our proofs channel!
"""
    await c.message.answer(text)

@dp.callback_query(F.data == "stock")
async def stock(c: CallbackQuery):
    await c.message.answer(f"📦 Total stock: {await stock_count()}")

@dp.callback_query(F.data == "support")
async def sup(c: CallbackQuery):
    await c.message.answer(
        f"● Iғ Yᴏᴜ Hᴀᴠᴇ A Mᴀᴊᴏʀ Pʀᴏʙʟᴇᴍ\nCᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ:- {SUPPORT}"
    )

# ---------- ADMIN PANEL ----------

@dp.callback_query(F.data == "admin")
async def admin_panel(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID:
        return
    await c.message.edit_text("🛠 ADMIN PANEL", reply_markup=admin_menu())

@dp.callback_query(F.data == "back")
async def back(c: CallbackQuery):
    await c.message.edit_text(
        "Wealcom our bot 🎉",
        reply_markup=menu(is_admin=True)
    )

ADD_MODE = set()
BROADCAST_MODE = set()

@dp.callback_query(F.data == "add_stock")
async def addstock_btn(c: CallbackQuery):
    ADD_MODE.add(c.from_user.id)
    await c.message.answer("📥 Send stock lines (one per line)")

@dp.callback_query(F.data == "users")
async def users(c: CallbackQuery):
    await c.message.answer("👥 Feature ready (user count can be added later)")

@dp.callback_query(F.data == "broadcast")
async def bc(c: CallbackQuery):
    BROADCAST_MODE.add(c.from_user.id)
    await c.message.answer("📣 Send broadcast message")

@dp.message()
async def admin_text(m: Message):
    if m.from_user.id in ADD_MODE:
        ADD_MODE.remove(m.from_user.id)
        await add_stock(m.text.splitlines())
        await m.answer("✅ Stock added")

    elif m.from_user.id in BROADCAST_MODE:
        BROADCAST_MODE.remove(m.from_user.id)
        await m.answer("📣 Broadcast sent (logic add later)")

# ---------- RUN ----------

async def main():
    await init_db()
    await dp.start_polling(bot)

asyncio.run(main())
