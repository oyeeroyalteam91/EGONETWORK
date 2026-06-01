# AZAI — EGO NETWORK

AZAI is the official EGO NETWORK community automation system.

**Network:** EGO NETWORK  
**Established:** 2026  
**Main Purpose:** Telegram group protection, verification, stylish community replies, moderation, leaderboard, custom pics, and owner-controlled automation.

## Core Direction

This repository is being built from zero using the AZAI blueprint.

AZAI must work as:

- A Telegram community automation bot
- A strict group verification gate
- A moderation and warning system
- A stylish Hinglish conversational assistant for allowed interactions
- An owner-controlled management system
- A leaderboard and activity point system
- A custom picture storage system
- A future-ready Mini App / web dashboard project

## Critical Rules

- No user, old or new, may interact in protected groups without verification.
- Commands, logs, debug text, raw API output, and secrets must stay in normal text.
- Visible bot messages should use Raj's saved stylish text system where technically safe.
- AZAI must not expose owner secrets, API keys, MongoDB URI, bot token, or admin internals.
- AZAI should refer to Aliza only as `Bhabhi Ji` or `Ma’am` in user-facing replies.
- AZAI must not claim to be a real human. It may use natural human-like Hinglish tone.

## Added Commands

### User Commands

- `/start` — main welcome/menu
- `/setup` — profile onboarding
- `/profile` — show saved profile
- `/leaderboard` — show group leaderboard
- `/top` — alias for leaderboard
- `/setpic [name]` — save custom photo by sending or replying to a photo
- `/getpic [name]` — retrieve saved custom photo
- `/pics` — list saved custom photo names

### Admin / Owner Pending

- Owner panel
- Global restriction command
- Advanced warning reset system
- Group settings panel
- Broadcast system
- Full Mini App dashboard

## Current Status

Completed base modules:

- Environment template
- Python dependency file
- Configuration loader
- MongoDB helper layer
- Stylish font utility
- Strict verification guard
- Basic moderation guard
- Profile onboarding
- Custom pic storage
- Leaderboard points
- Basic chat reply logic
- Main bot entrypoint

Real tokens and private keys must be added only through environment variables, never committed to GitHub.
