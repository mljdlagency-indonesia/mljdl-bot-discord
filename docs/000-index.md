# 000 — Documentation Index

## Overview

**mljdl-bot-discord** is a Discord bot for scrum/project management with three core integrations:
Google Sheets, GitHub, and an internal task management system.

## Documents

| Doc | Title | Description |
|-----|-------|-------------|
| [001-architecture](001-architecture.md) | Architecture | Project structure, layers, data flow, and design decisions |
| [002-how-to-use](002-how-to-use.md) | How to Use | Setup guide, environment config, command reference |
| [003-deployment](003-deployment.md) | Deployment | Deploy guide, server comparison, Railway/Fly.io/Oracle |

## What to Improve Next

### High Priority
1. **Slash Commands Migration** — Discord is deprecating prefix commands for verified bots. Migrate from `!command` to `/command` using `discord.app_commands`. This also enables autocomplete, argument validation, and better UX.
2. **Connection Pooling for SQLite** — Currently opens a new connection per query. Use a shared `aiosqlite` connection or a pool to reduce overhead.
3. **Run Blocking Services in Executor** — `sheets_service` and `github_service` use synchronous libraries (`gspread`, `PyGithub`). Wrap calls in `asyncio.to_thread()` to avoid blocking the event loop.

### Medium Priority
4. **Error Handling & Retry Logic** — Add exponential backoff for GitHub/Sheets API calls. Currently silent failures on polling errors.
5. **GitHub Webhooks Instead of Polling** — Replace the polling loop with a lightweight webhook listener (e.g., `aiohttp` server or FastAPI) for real-time GitHub notifications with less API usage.
6. **Task Due Date Reminders** — Add a background loop that notifies users when tasks are approaching or past their due date.
7. **Pagination for Embeds** — Large task lists / appointment lists exceed embed limits. Add button-based pagination using `discord.ui.View`.

### Low Priority
8. **Logging to File Rotation** — Replace basic `FileHandler` with `RotatingFileHandler` to prevent unbounded log growth.
9. **Docker Support** — Add a `Dockerfile` and `docker-compose.yml` for easy deployment.
10. **Unit Tests** — Add tests for services and cog command logic using `pytest` + `dpytest`.
11. **Config Validation** — Validate env vars on startup (e.g., check channel ID is numeric, repo format is `owner/name`) with clear error messages instead of crashing.
12. **Rate Limit Awareness** — Add rate limit handling for GitHub API (5000 req/hour) and Google Sheets API (60 req/min).
