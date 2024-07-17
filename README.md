# Makishima

Planned features:
- [ ] AniList
    - [x] Search
    - [ ] Recommendations
    - [ ] Rate function
    - [ ] Watched/read up to chapter X
    - [ ] Change status
    - [ ] Profile overview/stats
    - [ ] Random based on preferences, planning, etc.
    - [ ] AWC tracking (?)
- [ ] Google Books (?)
- [ ] Time/Planning
    - [ ] Timestamps
    - [ ] Reminders
    - [ ] Calendar

## Running

There are some required environment variables that need to be set up prior to
running the bot. The environment variables below can be defined in a `.env`
file.

- `MAKISHIMA_TOKEN`
    - The Discord bot token that can be retrieved in the Discord developer
      portal.
- `BIBLE_DB`
    - The sqlite database URL to be used for the bible command group.

You can then run makishima by typing `python3 src/makishima.py` in your
terminal. This script also contains a shebang, so you can also run it like an
executable.
