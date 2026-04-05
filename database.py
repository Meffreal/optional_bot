import aiosqlite
import os

DB_PATH = "data.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                log_channel_id INTEGER,
                mute_role_id INTEGER
            )
        """)
        await db.commit()


async def add_warning(guild_id: int, user_id: int, moderator_id: int, reason: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO warnings (guild_id, user_id, moderator_id, reason) VALUES (?, ?, ?, ?)",
            (guild_id, user_id, moderator_id, reason)
        )
        await db.commit()
        return cursor.lastrowid


async def get_warnings(guild_id: int, user_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM warnings WHERE guild_id = ? AND user_id = ? ORDER BY created_at DESC",
            (guild_id, user_id)
        ) as cursor:
            return await cursor.fetchall()


async def clear_warnings(guild_id: int, user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM warnings WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        )
        await db.commit()
        return cursor.rowcount


async def get_guild_setting(guild_id: int, key: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            f"SELECT {key} FROM guild_settings WHERE guild_id = ?",
            (guild_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def set_guild_setting(guild_id: int, key: str, value):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"""INSERT INTO guild_settings (guild_id, {key}) VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET {key} = excluded.{key}""",
            (guild_id, value)
        )
        await db.commit()
