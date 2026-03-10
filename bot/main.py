"""
bot/main.py -- Bot class dan setup
"""
import logging
import sys

import discord
from discord.ext import commands

from bot.config import config
from bot.services import db_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("bot")

COGS = [
    "bot.cogs.sheets",
    "bot.cogs.github",
    "bot.cogs.tasks",
]


class MyBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True  # wajib untuk prefix commands
        super().__init__(
            command_prefix=config.COMMAND_PREFIX,
            intents=intents,
            help_command=commands.DefaultHelpCommand(no_category="General"),
        )

    async def setup_hook(self) -> None:
        await db_service.init_db()
        log.info("Database initialized.")

        for cog in COGS:
            try:
                await self.load_extension(cog)
                log.info(f"Loaded cog: {cog}")
            except Exception as e:
                log.error(f"Failed to load cog {cog}: {e}", exc_info=True)

    async def on_ready(self) -> None:
        log.info(f"Bot ready: {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{config.COMMAND_PREFIX}help | {config.GITHUB_REPO}",
            )
        )

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing argument: `{error.param.name}`\nCek `!help {ctx.command}` untuk usage.")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Argumen tidak valid: {error}")
            return

        log.error(f"Unhandled error in {ctx.command}: {error}", exc_info=True)
        await ctx.send(f"❌ Terjadi error: `{error}`")
