# schoolbot

> **Archived**. A project I wrote in 2022–2024, back when I was still in school.
> It is no longer maintained and most likely no longer works: the APIs it relied on have probably changed since.
> Kept as is, as a look back at my younger self.

A Telegram bot built with [aiogram 3](https://github.com/aiogram/aiogram).

## What it did

- `/task <link>` — fetched a Skysmart assignment and extracted the correct answers from it
  (tests, text inputs, dropdowns, drag-and-drop, strike-outs, matching).
- `/gpt <text>` — sent a prompt to ChatGPT. (unavailable)
- `/status` — checked that the bot was alive.
- `/schedule` — school timetable. Never finished.

## Structure

```
src/
├── __main__.py        # entry point: config, sessions, polling
├── config.py          # reads config.ini
├── bot/
│   ├── commands.py    # bot commands
│   └── handlers/      # aiogram routers: task, gpt, status, schedule, start
└── skysmart/
    ├── session.py     # Skysmart auth and API requests
    ├── models/        # pydantic models for API responses
    └── parser/        # parses assignment XML and finds the correct answers
```

## Running (historical)

```bash
cp config.ini.example config.ini   # fill in login, password and tokens
poetry install
poetry run python -m src
```

Or use the `Dockerfile`.
