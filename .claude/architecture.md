---
name: Architektura Optional Bot
description: Struktura projektu, technologie, prehled cogs a databaze
type: project
---

# Optional Bot - Architektura

**Jazyk:** Python 3.11+
**Knihovna:** discord.py 2.x
**Databaze:** SQLite pres aiosqlite
**Hosting:** Cybrancee (VPS)
**Prefix:** `.`
**Slash commands:** ano

## Struktura souboru

```
optional_bot/
├── bot.py           # entry point, OptionalBot class, .help command
├── database.py      # vsechny DB operace (warnings, guild_settings)
├── requirements.txt
├── .env             # TOKEN, PREFIX, GUILD_ID
├── data.db          # SQLite databaze (generovana automaticky)
└── cogs/
    ├── moderation.py  # ban, kick, timeout, warn, warnings, clearwarns, purge, slowmode, lock, unlock
    ├── fun.py         # 8ball, roll, coinflip, rps, roast, joke, rate
    ├── utility.py     # ping, uptime, serverinfo, userinfo, avatar
    └── admin.py       # reload (owner only), setlog
```

## DB tabulky

- `warnings` - id, guild_id, user_id, moderator_id, reason, created_at
- `guild_settings` - guild_id, log_channel_id, mute_role_id

## Poznamky

- Slash commands se syncuji pri startu automaticky (global sync)
- Timeout pouziva Discord native timeout (timedelta), ne mute roli
- parse_duration() v moderation.py parsuje formaty: 10s, 5m, 2h, 1d
