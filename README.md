# Student Life Helper Bot

A Telegram bot for students — task management with MongoDB backend.

## Project Structure

src/
├── main.py                — Entry point, bot initialization
├── models/                — Entity classes & repository interfaces
│   ├── task.py            — Task entity (dataclass, enums)
│   ├── user.py            — User entity (dataclass, enums)
│   └── repositories.py   — Abstract repository interfaces (ABC)
├── use_cases/             — Business logic
│   └── task_use_cases.py  — Create, Update, Delete, Get tasks
├── repositories/          — MongoDB data access
│   ├── mongodb_task_repository.py  — Task CRUD operations
│   └── mongodb_user_repository.py  — User CRUD operations
├── database/              — Database configuration
│   └── config.py          — MongoDB connection & indexes
└── handlers/              — Telegram bot handlers
    ├── task_handler.py    — Command & callback handlers
    └── i18n.py            — Internationalization (RO/EN/RU)


## Commands

| Command | Description |
| `/tasks` | View all your tasks |
| `/add_task <title>` | Add a new task |
| `/deadline <days>` | View upcoming deadlines |
| `/search <keyword>` | Search tasks |
| `/help` | Show available commands |

## Setup

1. Copy `.env.example` to `.env` and set your `TELEGRAM_BOT_TOKEN` and `MONGODB_URI`
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python -m src.main`
