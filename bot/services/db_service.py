"""
services/db_service.py -- SQLite handler untuk task management
"""
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "db" / "bot.db"


async def init_db() -> None:
    """Buat tabel kalau belum ada."""
    DB_PATH.parent.mkdir(exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT DEFAULT '',
                status      TEXT DEFAULT 'todo',
                priority    TEXT DEFAULT 'medium',
                created_by  INTEGER NOT NULL,
                assigned_to INTEGER,
                guild_id    INTEGER NOT NULL,
                due_date    TEXT,
                tags        TEXT DEFAULT '',
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            )
        """)
        await db.commit()


async def execute(query: str, params: tuple = ()) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(query, params)
        await db.commit()


async def fetchall(query: str, params: tuple = ()) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def fetchone(query: str, params: tuple = ()) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
