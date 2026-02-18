# Todoist Shopping List Skill

Fetches the **Einkaufsliste** (shopping list) from Todoist and outputs a formatted bullet list suitable for Signal messaging.

## Usage

```bash
python3 todoist_shopping.py
```

Output goes to stdout, grouped by section:

```
🛒 *Einkaufsliste*

📦 *Haushalt & Reinigung*
  • Backpapier

📦 *Tiefkühlprodukte*
  • Crushed Ice
```

## Requirements

- Python 3.10+
- `requests` library (`pip install requests`)
- `gopass` with `openclaw/todoist-api-token` configured
- Todoist account with a project named "Einkaufsliste"

## API

Uses Todoist REST API v1 (`https://api.todoist.com/api/v1/`).

## Automation

Intended for Friday morning Signal messages. Example cron/heartbeat integration:

```bash
# Send shopping list via Signal
python3 skills/todoist/todoist_shopping.py | openclaw signal send --to goern ...
```

## License

GPL-3.0-or-later
