"""
cogs/github.py -- Commands + auto-polling GitHub activity
"""
from datetime import datetime, timezone

import discord
from discord.ext import commands, tasks

from bot.config import config
from bot.services import github_service


class GitHubCog(commands.Cog, name="GitHub"):
    """Commands dan notifikasi otomatis untuk GitHub repo."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._last_poll: datetime = datetime.now(tz=timezone.utc)
        self.poll_github.start()

    def cog_unload(self) -> None:
        self.poll_github.cancel()

    # ---------- Auto-polling ----------

    @tasks.loop(seconds=config.GITHUB_POLL_INTERVAL)
    async def poll_github(self) -> None:
        """Polling events GitHub dan kirim notifikasi ke channel."""
        channel = self.bot.get_channel(config.GITHUB_NOTIF_CHANNEL_ID)
        if not channel:
            return

        try:
            events = github_service.get_events_since(self._last_poll)
        except Exception:
            return  # jangan crash kalau GitHub API timeout

        self._last_poll = datetime.now(tz=timezone.utc)

        for event in reversed(events):  # oldest first
            embed = self._event_to_embed(event)
            if embed:
                await channel.send(embed=embed)

    @poll_github.before_loop
    async def before_poll(self) -> None:
        await self.bot.wait_until_ready()

    def _event_to_embed(self, event: dict) -> discord.Embed | None:
        """Convert GitHub event payload ke Discord embed."""
        etype = event["type"]
        actor = event["actor"]
        payload = event["payload"]
        color = discord.Color.dark_gray()
        title = ""
        description = ""

        if etype == "PushEvent":
            commits = payload.get("commits", [])
            color = discord.Color.green()
            title = f"🚀 Push by {actor}"
            description = "\n".join(
                f"• `{c['sha'][:7]}` {c['message'].splitlines()[0]}"
                for c in commits[:5]
            )
        elif etype == "PullRequestEvent":
            pr = payload.get("pull_request", {})
            action = payload.get("action", "")
            color = discord.Color.purple()
            title = f"🔀 PR {action.capitalize()} by {actor}"
            description = f"[#{pr.get('number')} {pr.get('title')}]({pr.get('html_url')})"
        elif etype == "IssuesEvent":
            issue = payload.get("issue", {})
            action = payload.get("action", "")
            color = discord.Color.orange()
            title = f"🐛 Issue {action.capitalize()} by {actor}"
            description = f"[#{issue.get('number')} {issue.get('title')}]({issue.get('html_url')})"
        elif etype == "CreateEvent":
            ref_type = payload.get("ref_type", "")
            ref = payload.get("ref", "")
            color = discord.Color.teal()
            title = f"✨ New {ref_type} by {actor}"
            description = f"`{ref}`"
        else:
            return None  # skip event yang gak relevan

        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=config.GITHUB_REPO)
        return embed

    # ---------- Manual commands ----------

    @commands.command(name="ghcommits", aliases=["commits"])
    async def recent_commits(self, ctx: commands.Context, limit: int = 5) -> None:
        """Tampilkan N commit terbaru. Usage: !ghcommits [limit]"""
        async with ctx.typing():
            try:
                commits = github_service.get_recent_commits(min(limit, 10))
            except Exception as e:
                await ctx.send(f"❌ GitHub error: `{e}`")
                return

        embed = discord.Embed(
            title=f"🚀 {len(commits)} Commit Terbaru — {config.GITHUB_REPO}",
            color=discord.Color.green(),
        )
        for c in commits:
            embed.add_field(
                name=f"`{c['sha']}` by {c['author']}",
                value=f"[{c['message']}]({c['url']})",
                inline=False,
            )
        await ctx.send(embed=embed)

    @commands.command(name="ghprs", aliases=["prs"])
    async def open_prs(self, ctx: commands.Context) -> None:
        """Tampilkan open pull requests."""
        async with ctx.typing():
            try:
                prs = github_service.get_open_prs()
            except Exception as e:
                await ctx.send(f"❌ GitHub error: `{e}`")
                return

        if not prs:
            await ctx.send("Tidak ada open PR saat ini.")
            return

        embed = discord.Embed(
            title=f"🔀 Open PRs — {config.GITHUB_REPO}",
            color=discord.Color.purple(),
        )
        for pr in prs:
            reviewers = ", ".join(pr["reviewers"]) or "none"
            embed.add_field(
                name=f"#{pr['number']} {pr['title']}",
                value=f"by **{pr['author']}** | reviewers: {reviewers}\n[Open PR]({pr['url']})",
                inline=False,
            )
        await ctx.send(embed=embed)

    @commands.command(name="ghissues", aliases=["issues"])
    async def open_issues(self, ctx: commands.Context, state: str = "open") -> None:
        """Tampilkan issues. Usage: !ghissues [open|closed]"""
        if state not in ("open", "closed"):
            await ctx.send("State harus `open` atau `closed`.")
            return

        async with ctx.typing():
            try:
                issues = github_service.get_recent_issues(state=state)
            except Exception as e:
                await ctx.send(f"❌ GitHub error: `{e}`")
                return

        if not issues:
            await ctx.send(f"Tidak ada {state} issues.")
            return

        embed = discord.Embed(
            title=f"🐛 {state.capitalize()} Issues — {config.GITHUB_REPO}",
            color=discord.Color.orange(),
        )
        for issue in issues:
            labels = ", ".join(issue["labels"]) or "no labels"
            embed.add_field(
                name=f"#{issue['number']} {issue['title']}",
                value=f"by **{issue['author']}** | {labels}\n[Open Issue]({issue['url']})",
                inline=False,
            )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GitHubCog(bot))
