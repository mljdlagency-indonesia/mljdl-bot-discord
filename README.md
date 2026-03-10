# Discord Bot — Sheets + GitHub + Task Manager

Bot modular Discord dengan fitur:
- 📅 **Google Sheets** — baca appointment dari spreadsheet
- 🚀 **GitHub** — notifikasi otomatis + manual query activity
- 📋 **Task Manager** — ClickUp-like task system native di Discord

---

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env dengan nilai yang sesuai
python run.py
```

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/000-index.md](docs/000-index.md) | Index & improvement roadmap |
| [docs/001-architecture.md](docs/001-architecture.md) | Architecture, layers, data flow, schema |
| [docs/002-how-to-use.md](docs/002-how-to-use.md) | Full setup guide & command reference |

---

## Project Structure

```
mljdl-bot-discord/
├── run.py                      # Entry point
├── .env.example
├── requirements.txt
├── bot/
│   ├── main.py                 # Bot class, logging, cog loader
│   ├── config.py               # Config from .env
│   ├── cogs/
│   │   ├── sheets.py           # Google Sheets commands
│   │   ├── github.py           # GitHub commands + auto-polling
│   │   └── tasks.py            # Task management CRUD
│   ├── services/
│   │   ├── db_service.py       # Async SQLite
│   │   ├── sheets_service.py   # Google Sheets API
│   │   └── github_service.py   # GitHub API
│   ├── models/
│   │   └── task.py             # TaskStatus, TaskPriority enums
│   └── utils/
├── db/                         # Auto-created SQLite database
├── docs/                       # Documentation
└── README.md
```

---

## Commands Overview

### 📅 Sheets
| Command | Alias | Description |
|---------|-------|-------------|
| `!lastappointment` | `!la` | Last row from sheet |
| `!appointments [N]` | `!apps` | Last N appointments |
| `!findappointment <col> <val>` | `!find` | Search by column |

### 🚀 GitHub
| Command | Alias | Description |
|---------|-------|-------------|
| `!ghcommits [N]` | `!commits` | Recent commits |
| `!ghprs` | `!prs` | Open pull requests |
| `!ghissues [state]` | `!issues` | Issues (open/closed) |

### 📋 Tasks
| Command | Alias | Description |
|---------|-------|-------------|
| `!taskcreate [priority] <title>` | `!tc` | Create task |
| `!task <id>` | `!t` | View task |
| `!tasklist [filter]` | `!tl` | List tasks |
| `!taskstatus <id> <status>` | `!ts` | Update status |
| `!taskassign <id> @user` | `!ta` | Assign task |
| `!taskdesc <id> <desc>` | `!td` | Set description |
| `!taskdelete <id>` | `!tdelete` | Delete task |
| `!taskhelp` | `!th` | Help |

**Priority:** `low` 🔵 `medium` 🟡 `high` 🟠 `urgent` 🔴
**Status:** `todo` ⬜ `in_progress` 🔄 `review` 👀 `done` ✅ `cancelled` ❌
