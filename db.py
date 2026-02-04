import aiosqlite
import time

DB = "data.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            last_used INTEGER
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT
        )
        """)
        await db.commit()

async def can_use(user_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT last_used FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        now = int(time.time())

        if not row:
            await db.execute(
                "INSERT INTO users (user_id, last_used) VALUES (?,?)",
                (user_id, now)
            )
            await db.commit()
            return True

        if now - row[0] >= 86400:
            await db.execute(
                "UPDATE users SET last_used=? WHERE user_id=?",
                (now, user_id)
            )
            await db.commit()
            return True

        return False

async def add_stock(lines):
    async with aiosqlite.connect(DB) as db:
        for line in lines:
            if line.strip():
                await db.execute(
                    "INSERT INTO stock (data) VALUES (?)",
                    (line.strip(),)
                )
        await db.commit()

async def get_stock():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT id, data FROM stock LIMIT 1")
        row = await cur.fetchone()
        if not row:
            return None
        await db.execute("DELETE FROM stock WHERE id=?", (row[0],))
        await db.commit()
        return row[1]

async def stock_count():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT COUNT(*) FROM stock")
        return (await cur.fetchone())[0]
