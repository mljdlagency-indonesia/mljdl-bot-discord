"""
cogs/sheets.py -- Commands untuk Google Sheets integration
"""
import discord
from discord.ext import commands
from bot.services import sheets_service


class SheetsCog(commands.Cog, name="Sheets"):
    """Commands untuk baca data dari Google Sheets."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="lastappointment", aliases=["la"])
    async def last_appointment(self, ctx: commands.Context) -> None:
        """Tampilkan appointment terakhir dari spreadsheet."""
        async with ctx.typing():
            try:
                row = sheets_service.get_last_row()
            except Exception as e:
                await ctx.send(f"❌ Gagal baca sheet: `{e}`")
                return

        if not row:
            await ctx.send("Sheet kosong atau tidak ada data.")
            return

        embed = discord.Embed(
            title="📅 Last Appointment",
            color=discord.Color.blue(),
        )
        for key, value in row.items():
            if value:  # skip kolom kosong
                embed.add_field(name=key, value=value or "-", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="appointments", aliases=["apps"])
    async def list_appointments(self, ctx: commands.Context, limit: int = 5) -> None:
        """
        Tampilkan N appointment terakhir.
        Usage: !appointments [limit]
        Default limit: 5, max: 20
        """
        limit = min(limit, 20)
        async with ctx.typing():
            try:
                rows = sheets_service.get_all_rows(limit=limit)
            except Exception as e:
                await ctx.send(f"❌ Gagal baca sheet: `{e}`")
                return

        if not rows:
            await ctx.send("Tidak ada data di sheet.")
            return

        embed = discord.Embed(
            title=f"📋 {limit} Appointment Terakhir",
            color=discord.Color.blue(),
        )
        for i, row in enumerate(reversed(rows), 1):
            # Ambil beberapa kolom penting buat preview (sesuaikan key-nya)
            summary = " | ".join(f"{k}: {v}" for k, v in row.items() if v)[:200]
            embed.add_field(name=f"#{i}", value=summary or "-", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="findappointment", aliases=["find"])
    async def find_appointment(
        self, ctx: commands.Context, column: str, *, value: str
    ) -> None:
        """
        Cari appointment berdasarkan nilai kolom tertentu.
        Usage: !findappointment Email john@example.com
        """
        async with ctx.typing():
            try:
                rows = sheets_service.search_by_column(column, value)
            except Exception as e:
                await ctx.send(f"❌ Error: `{e}`")
                return

        if not rows:
            await ctx.send(f"Tidak ditemukan data dengan `{column}` = `{value}`")
            return

        embed = discord.Embed(
            title=f"🔍 Hasil Pencarian: {column} = {value}",
            color=discord.Color.green(),
        )
        for row in rows[:5]:  # max 5 hasil
            summary = "\n".join(f"**{k}**: {v}" for k, v in row.items() if v)
            embed.add_field(name=f"Row", value=summary[:1024], inline=False)

        if len(rows) > 5:
            embed.set_footer(text=f"Menampilkan 5 dari {len(rows)} hasil.")

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SheetsCog(bot))
