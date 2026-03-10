"""
cogs/tasks.py -- ClickUp-like task management system di Discord
"""
from datetime import datetime

import discord
from discord.ext import commands

from bot.models.task import TaskStatus, TaskPriority, PRIORITY_EMOJI, STATUS_EMOJI
from bot.services import db_service


def _format_task(row: dict) -> discord.Embed:
    """Convert task row ke Discord embed."""
    status = TaskStatus(row["status"])
    priority = TaskPriority(row["priority"])

    embed = discord.Embed(
        title=f"{STATUS_EMOJI[status]} [{row['id']}] {row['title']}",
        description=row["description"] or "_No description_",
        color=_priority_color(priority),
    )
    embed.add_field(name="Status", value=f"{STATUS_EMOJI[status]} {status.value}", inline=True)
    embed.add_field(name="Priority", value=f"{PRIORITY_EMOJI[priority]} {priority.value}", inline=True)

    assigned = f"<@{row['assigned_to']}>" if row.get("assigned_to") else "Unassigned"
    embed.add_field(name="Assigned", value=assigned, inline=True)

    if row.get("due_date"):
        embed.add_field(name="Due Date", value=row["due_date"], inline=True)

    if row.get("tags"):
        embed.add_field(name="Tags", value=row["tags"], inline=True)

    embed.set_footer(text=f"Created by user {row['created_by']} | ID: {row['id']}")
    return embed


def _priority_color(priority: TaskPriority) -> discord.Color:
    return {
        TaskPriority.LOW: discord.Color.blue(),
        TaskPriority.MEDIUM: discord.Color.yellow(),
        TaskPriority.HIGH: discord.Color.orange(),
        TaskPriority.URGENT: discord.Color.red(),
    }[priority]


class TasksCog(commands.Cog, name="Tasks"):
    """ClickUp-like task management langsung di Discord."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ---------- Create ----------

    @commands.command(name="taskcreate", aliases=["tc"])
    async def create_task(
        self,
        ctx: commands.Context,
        priority: str = "medium",
        *,
        title: str,
    ) -> None:
        """
        Buat task baru.
        Usage: !taskcreate [low|medium|high|urgent] <judul task>
        Example: !taskcreate high Fix login bug
        """
        if priority not in TaskPriority._value2member_map_:
            # Kalau priority gak valid, treat sebagai bagian dari title
            title = f"{priority} {title}"
            priority = "medium"

        now = datetime.utcnow().isoformat()
        await db_service.execute(
            """
            INSERT INTO tasks (title, status, priority, created_by, guild_id, created_at, updated_at)
            VALUES (?, 'todo', ?, ?, ?, ?, ?)
            """,
            (title, priority, ctx.author.id, ctx.guild.id, now, now),
        )
        row = await db_service.fetchone(
            "SELECT * FROM tasks WHERE rowid = last_insert_rowid()"
        )
        embed = _format_task(row)
        embed.color = discord.Color.green()
        await ctx.send("✅ Task dibuat!", embed=embed)

    # ---------- View ----------

    @commands.command(name="task", aliases=["t"])
    async def get_task(self, ctx: commands.Context, task_id: int) -> None:
        """
        Lihat detail task.
        Usage: !task <id>
        """
        row = await db_service.fetchone(
            "SELECT * FROM tasks WHERE id = ? AND guild_id = ?",
            (task_id, ctx.guild.id),
        )
        if not row:
            await ctx.send(f"❌ Task `#{task_id}` tidak ditemukan.")
            return
        await ctx.send(embed=_format_task(row))

    @commands.command(name="tasklist", aliases=["tl"])
    async def list_tasks(
        self, ctx: commands.Context, filter_by: str = "all"
    ) -> None:
        """
        List semua tasks.
        Usage: !tasklist [all|todo|in_progress|review|done|@user]
        """
        base = "SELECT * FROM tasks WHERE guild_id = ?"
        params: list = [ctx.guild.id]

        if filter_by in TaskStatus._value2member_map_:
            base += " AND status = ?"
            params.append(filter_by)
        elif filter_by.startswith("<@") and filter_by.endswith(">"):
            user_id = filter_by.strip("<@!>")
            base += " AND assigned_to = ?"
            params.append(int(user_id))
        elif filter_by != "all":
            await ctx.send("Filter: `all`, `todo`, `in_progress`, `review`, `done`, atau `@user`")
            return

        base += " AND status != 'cancelled' ORDER BY priority DESC, created_at DESC LIMIT 20"
        rows = await db_service.fetchall(base, tuple(params))

        if not rows:
            await ctx.send("Tidak ada task.")
            return

        embed = discord.Embed(
            title=f"📋 Tasks [{filter_by}] — {len(rows)} task",
            color=discord.Color.blurple(),
        )
        for row in rows:
            status = TaskStatus(row["status"])
            priority = TaskPriority(row["priority"])
            assigned = f"<@{row['assigned_to']}>" if row.get("assigned_to") else "unassigned"
            embed.add_field(
                name=f"{PRIORITY_EMOJI[priority]} #{row['id']} {row['title']}",
                value=f"{STATUS_EMOJI[status]} {status.value} | {assigned}",
                inline=False,
            )
        await ctx.send(embed=embed)

    # ---------- Update ----------

    @commands.command(name="taskstatus", aliases=["ts"])
    async def update_status(
        self, ctx: commands.Context, task_id: int, status: str
    ) -> None:
        """
        Update status task.
        Usage: !taskstatus <id> <todo|in_progress|review|done|cancelled>
        """
        if status not in TaskStatus._value2member_map_:
            valid = ", ".join(f"`{s}`" for s in TaskStatus._value2member_map_)
            await ctx.send(f"Status valid: {valid}")
            return

        row = await db_service.fetchone(
            "SELECT * FROM tasks WHERE id = ? AND guild_id = ?",
            (task_id, ctx.guild.id),
        )
        if not row:
            await ctx.send(f"❌ Task `#{task_id}` tidak ditemukan.")
            return

        await db_service.execute(
            "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
            (status, datetime.utcnow().isoformat(), task_id),
        )
        row["status"] = status
        await ctx.send(f"✅ Status task `#{task_id}` diupdate ke `{status}`", embed=_format_task(row))

    @commands.command(name="taskassign", aliases=["ta"])
    async def assign_task(
        self, ctx: commands.Context, task_id: int, member: discord.Member
    ) -> None:
        """
        Assign task ke member.
        Usage: !taskassign <id> @user
        """
        row = await db_service.fetchone(
            "SELECT * FROM tasks WHERE id = ? AND guild_id = ?",
            (task_id, ctx.guild.id),
        )
        if not row:
            await ctx.send(f"❌ Task `#{task_id}` tidak ditemukan.")
            return

        await db_service.execute(
            "UPDATE tasks SET assigned_to = ?, updated_at = ? WHERE id = ?",
            (member.id, datetime.utcnow().isoformat(), task_id),
        )
        row["assigned_to"] = member.id
        await ctx.send(
            f"✅ Task `#{task_id}` di-assign ke {member.mention}",
            embed=_format_task(row),
        )

    @commands.command(name="taskdesc", aliases=["td"])
    async def set_description(
        self, ctx: commands.Context, task_id: int, *, description: str
    ) -> None:
        """
        Set/update deskripsi task.
        Usage: !taskdesc <id> <deskripsi>
        """
        row = await db_service.fetchone(
            "SELECT id FROM tasks WHERE id = ? AND guild_id = ?",
            (task_id, ctx.guild.id),
        )
        if not row:
            await ctx.send(f"❌ Task `#{task_id}` tidak ditemukan.")
            return

        await db_service.execute(
            "UPDATE tasks SET description = ?, updated_at = ? WHERE id = ?",
            (description, datetime.utcnow().isoformat(), task_id),
        )
        await ctx.send(f"✅ Deskripsi task `#{task_id}` diupdate.")

    # ---------- Delete ----------

    @commands.command(name="taskdelete", aliases=["tdelete"])
    async def delete_task(self, ctx: commands.Context, task_id: int) -> None:
        """
        Hapus task (soft delete via cancelled).
        Usage: !taskdelete <id>
        """
        row = await db_service.fetchone(
            "SELECT created_by FROM tasks WHERE id = ? AND guild_id = ?",
            (task_id, ctx.guild.id),
        )
        if not row:
            await ctx.send(f"❌ Task `#{task_id}` tidak ditemukan.")
            return

        # Hanya creator atau admin yang bisa delete
        is_admin = ctx.author.guild_permissions.administrator
        if row["created_by"] != ctx.author.id and not is_admin:
            await ctx.send("❌ Hanya creator task atau admin yang bisa delete.")
            return

        await db_service.execute(
            "UPDATE tasks SET status = 'cancelled', updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), task_id),
        )
        await ctx.send(f"🗑️ Task `#{task_id}` dihapus.")

    # ---------- Help ----------

    @commands.command(name="taskhelp", aliases=["th"])
    async def task_help(self, ctx: commands.Context) -> None:
        """Tampilkan semua task commands."""
        embed = discord.Embed(
            title="📋 Task Commands",
            color=discord.Color.blurple(),
        )
        commands_list = [
            ("!taskcreate [priority] <title>", "Buat task baru\nEx: `!tc high Fix bug`"),
            ("!task <id>", "Lihat detail task"),
            ("!tasklist [filter]", "List tasks\nFilter: `all`, `todo`, `in_progress`, `review`, `done`, `@user`"),
            ("!taskstatus <id> <status>", "Update status task"),
            ("!taskassign <id> @user", "Assign task ke member"),
            ("!taskdesc <id> <desc>", "Set deskripsi task"),
            ("!taskdelete <id>", "Hapus task"),
        ]
        for name, value in commands_list:
            embed.add_field(name=f"`{name}`", value=value, inline=False)

        embed.add_field(
            name="Priority",
            value=" | ".join(f"{v} `{k}`" for k, v in PRIORITY_EMOJI.items()),
            inline=False,
        )
        embed.add_field(
            name="Status",
            value=" | ".join(f"{v} `{k}`" for k, v in STATUS_EMOJI.items()),
            inline=False,
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TasksCog(bot))
