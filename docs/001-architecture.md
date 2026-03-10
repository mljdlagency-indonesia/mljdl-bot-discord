# 001 — Architecture

## Project Structure

```
mljdl-bot-discord/
├── run.py                      # Entry point — python run.py
├── .env                        # Environment variables (not committed)
├── .env.example                # Template for .env
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview
│
├── bot/                        # Main application package
│   ├── __init__.py
│   ├── main.py                 # MyBot class, logging, cog loading
│   ├── config.py               # Config class — loads from .env
│   │
│   ├── cogs/                   # Command handlers (discord.py extensions)
│   │   ├── __init__.py
│   │   ├── sheets.py           # Google Sheets commands
│   │   ├── github.py           # GitHub commands + auto-polling loop
│   │   └── tasks.py            # Task management CRUD commands
│   │
│   ├── services/               # Business logic & external API clients
│   │   ├── __init__.py
│   │   ├── db_service.py       # SQLite async handler (aiosqlite)
│   │   ├── sheets_service.py   # Google Sheets reader (gspread)
│   │   └── github_service.py   # GitHub API client (PyGithub)
│   │
│   ├── models/                 # Data models & enums
│   │   ├── __init__.py
│   │   └── task.py             # TaskStatus, TaskPriority enums + emoji maps
│   │
│   └── utils/                  # Shared utilities (future use)
│       └── __init__.py
│
├── db/                         # SQLite database (auto-created at runtime)
│   └── bot.db
│
└── docs/                       # Documentation
    ├── 000-index.md
    ├── 001-architecture.md
    └── 002-how-to-use.md
```

## Layers

The bot follows a **3-layer architecture**:

```
┌─────────────────────────────────────────┐
│              Discord (User)             │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│          Cogs (Presentation)            │
│  sheets.py │ github.py │ tasks.py       │
│  - Parse commands & arguments           │
│  - Format responses as Embeds           │
│  - Handle errors for user display       │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         Services (Business Logic)       │
│  db_service │ sheets_service │ github   │
│  - External API communication           │
│  - Data transformation                  │
│  - Connection management                │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         Models (Data Definitions)       │
│  task.py                                │
│  - Enums (TaskStatus, TaskPriority)     │
│  - Constants (emoji maps)              │
└─────────────────────────────────────────┘
```

## Data Flow

### Command Flow (e.g., `!taskcreate high Fix login`)
```
User sends message
  → discord.py routes to TasksCog.create_task()
    → Validates priority via TaskPriority enum
    → Calls db_service.execute() to INSERT
    → Calls db_service.fetchone() to get created row
    → Formats with _format_task() → Discord Embed
  → Bot sends embed response
```

### GitHub Polling Flow
```
tasks.loop(seconds=300) triggers poll_github()
  → Calls github_service.get_events_since(last_poll)
    → PyGithub fetches repo events from GitHub API
  → Converts each event to Discord Embed via _event_to_embed()
  → Sends embeds to configured notification channel
  → Updates last_poll timestamp
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Prefix commands** (`!cmd`) | Simple setup, no slash command registration needed |
| **SQLite via aiosqlite** | Zero-config database, async-compatible, good for single-server bots |
| **Soft delete for tasks** | Sets status to `cancelled` instead of DELETE — preserves history |
| **Lazy-init for API clients** | `_get_client()` / `_get_repo()` pattern avoids init errors if API is unreachable at startup |
| **Guild-scoped tasks** | Each Discord server has isolated task lists via `guild_id` |
| **Polling over webhooks** | Simpler deployment — no need for a public endpoint or webhook server |

## Database Schema

### `tasks` table
| Column | Type | Default | Description |
|--------|------|---------|-------------|
| id | INTEGER | autoincrement | Primary key |
| title | TEXT | — | Task title (required) |
| description | TEXT | '' | Optional description |
| status | TEXT | 'todo' | One of: todo, in_progress, review, done, cancelled |
| priority | TEXT | 'medium' | One of: low, medium, high, urgent |
| created_by | INTEGER | — | Discord user ID of creator |
| assigned_to | INTEGER | NULL | Discord user ID of assignee |
| guild_id | INTEGER | — | Discord server ID |
| due_date | TEXT | NULL | ISO date string |
| tags | TEXT | '' | Comma-separated tags |
| created_at | TEXT | — | ISO datetime |
| updated_at | TEXT | — | ISO datetime |

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| discord.py | 2.3.2 | Discord bot framework |
| gspread | 6.1.2 | Google Sheets API |
| google-auth | 2.29.0 | Google service account auth |
| aiosqlite | 0.20.0 | Async SQLite |
| PyGithub | 2.3.0 | GitHub REST API |
| python-dotenv | 1.0.1 | Load .env files |
| aiohttp | 3.9.5 | Async HTTP (discord.py dependency) |
