# Agent Guidance for Ralsei Bot

## Running the Bot

```bash
python main.py
```

Requires `.env` file with `TOKEN` key (Discord bot token).

## Dependencies

```bash
pip install discord.py aiosqlite python-dotenv requests torch
```

Note: `torch` is only needed if enabling `cogs.ai` (requires CUDA for reasonable performance).

## Project Structure

- **Entry point**: `main.py` - loads cogs, initializes database, starts bot
- **Cogs** in `cogs/` - modular command extensions (fun, actions, count, inventory, logs, exp, currency, stats, admin, ai)
- **Database** in `db/` - SQLite with aiosqlite, schema in `setup.sql`

## Important Quirks

1. **AI cog is disabled by default**: `cogs.ai` is commented out in `main.py:277` because it's very slow without a CUDA GPU and can CPU-throttle the bot.

2. **Database**: `database.db` uses WAL mode. Schema auto-created on startup via `db/setup.sql`.

3. **Bot prefix**: `r:` (e.g., `r:ping`)

4. **Hybrid commands**: Many commands work as both prefix (`r:command`) and slash (`/command`).

5. **GitHub commits feature**: Requires `GITHUB_TOKEN` in `.env` for rate-limited API access.

## Adding New Cogs

1. Create file in `cogs/`
2. Subclass `commands.Cog`
3. Add to extensions list in `main.py:272-283`

```python
await bot.load_extension("cogs.your_cog")
```