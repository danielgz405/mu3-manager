# AGENTS.md — mu3-list

## Quick start

```bash
pip install google-generativeai requests python-dotenv
python main.py
```

## Architecture

Modular IPTV M3U playlist manager. No package manager — bare Python, deps installed globally or via `venv`.

| File | Role |
|------|------|
| `main.py` | CLI menu: 1) merge raw lists → 2) clean/dedupe/test with AI → 3) terminal player |
| `config.py` | Env, paths (`m3u-list/`, `m3u-procesadas/`, `m3u-logs/`), allowed categories |
| `manager_module.py` | Merge M3Us (dedup by URL) → clean + AI categorize + stream-test → sort by category |
| `ai_module.py` | Calls Google Gemini API in batches of 40, retries on 429 with 60s backoff, 6s pause between batches |
| `stream_module.py` | Tests each URL: download 512KB with 3s connect / 5s read timeout |
| `player_module.py` | Category-browsing terminal player using `mpv` (preferred) or VLC |
| `utils.py` | Dir setup, daily logs, M3U parser |

## Key facts

- **No tests** — none exist, do not write them unless asked.
- **No lint/format/typecheck config** — no `pyproject.toml`, `ruff`, `black`, `mypy`.
- **`.env` required** with `GEMINI_API_KEY`. A real key is currently committed — do not expose it further.
- **M3U files** in `m3u-list/` are sample/development data, committed to repo despite `.gitignore` pattern. Assume they exist.
- **Player dependencies**: `mpv` (`brew install mpv`) or VLC.
- `.env.local` is a template; `.env` is the real config (intentionally committed but should rotate the key).
