# 002 — How to Use

## Prerequisites

- Python 3.10+
- A Discord bot token ([Discord Developer Portal](https://discord.com/developers/applications))
- A Google Cloud service account with Sheets API enabled
- A GitHub Personal Access Token

## Setup

### 1. Clone & Install

```bash
git clone <repo-url>
cd mljdl-bot-discord
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_TOKEN` | Yes | Bot token from Discord Developer Portal |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Yes | Path to service account JSON file, or the JSON string itself |
| `SPREADSHEET_ID` | Yes | Google Sheets ID (from the URL) |
| `SHEET_NAME` | No | Tab name, default: `Sheet1` |
| `GITHUB_TOKEN` | Yes | GitHub Personal Access Token |
| `GITHUB_REPO` | Yes | Repository in `owner/repo` format |
| `GITHUB_POLL_INTERVAL` | No | Polling interval in seconds, default: `300` |
| `GITHUB_NOTIF_CHANNEL_ID` | Yes | Discord channel ID for GitHub notifications |
| `COMMAND_PREFIX` | No | Bot command prefix, default: `!` |

### 3. Run the Bot

```bash
python run.py
```

The bot will:
- Initialize the SQLite database in `db/bot.db`
- Load all cogs (Sheets, GitHub, Tasks)
- Start the GitHub polling loop
- Go online in Discord

## Command Reference

### Google Sheets

| Command | Alias | Description |
|---------|-------|-------------|
| `!lastappointment` | `!la` | Show the last row from the spreadsheet |
| `!appointments [N]` | `!apps` | Show last N appointments (default 5, max 20) |
| `!findappointment <column> <value>` | `!find` | Search by column value |

**Examples:**
```
!la
!apps 10
!find Email john@example.com
```

### GitHub

| Command | Alias | Description |
|---------|-------|-------------|
| `!ghcommits [N]` | `!commits` | Show recent commits (default 5, max 10) |
| `!ghprs` | `!prs` | Show open pull requests |
| `!ghissues [state]` | `!issues` | Show issues (open/closed) |

**Examples:**
```
!commits 3
!prs
!issues closed
```

GitHub also auto-posts notifications to the configured channel for:
- Push events
- Pull request events (opened, closed, merged)
- Issue events (opened, closed)
- Branch/tag creation

### Task Management

| Command | Alias | Description |
|---------|-------|-------------|
| `!taskcreate [priority] <title>` | `!tc` | Create a new task |
| `!task <id>` | `!t` | View task details |
| `!tasklist [filter]` | `!tl` | List tasks |
| `!taskstatus <id> <status>` | `!ts` | Update task status |
| `!taskassign <id> @user` | `!ta` | Assign task to member |
| `!taskdesc <id> <description>` | `!td` | Set task description |
| `!taskdelete <id>` | `!tdelete` | Delete task (soft delete) |
| `!taskhelp` | `!th` | Show task command help |

**Priority levels:** `low`, `medium` (default), `high`, `urgent`

**Status values:** `todo`, `in_progress`, `review`, `done`, `cancelled`

**Filter options:** `all` (default), `todo`, `in_progress`, `review`, `done`, `@user`

**Examples:**
```
!tc high Fix login bug
!tc Deploy to staging
!t 1
!tl in_progress
!tl @John
!ts 1 done
!ta 1 @John
!td 1 This needs to be fixed ASAP
!tdelete 1
```

## Permissions

- **Task deletion** — Only the task creator or server admins can delete tasks
- **All other commands** — Available to all server members
- **Bot requires** — `Send Messages`, `Embed Links`, `Read Message History` permissions in Discord

## Hosting

Recommended free/cheap options:
- **Railway** — Easy deploy with GitHub integration
- **Fly.io** — Free tier with always-on machines
- **Render** — Free tier with auto-deploy
- **VPS** — Use `systemd` or `pm2` to keep the bot running

For production, use a process manager:
```bash
# With systemd (Linux)
# Create /etc/systemd/system/discord-bot.service

# With screen
screen -S bot python run.py
```
