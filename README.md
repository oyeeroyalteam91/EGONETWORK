# AZAI — EGO NETWORK

AZAI is the official EGO NETWORK community automation system.

**Network:** EGO NETWORK  
**Established:** 2026  
**Main Purpose:** Telegram group protection, verification, stylish community replies, moderation, leaderboard, custom pics, owner controls, and future Mini App dashboard.

## Core Direction

This repository is being built from zero using the AZAI blueprint.

AZAI works as:

- A Telegram community automation bot
- A strict group verification gate
- A moderation and warning system
- A stylish Hinglish conversational assistant for allowed interactions
- An owner-controlled management system
- A leaderboard and activity point system
- A custom picture storage system
- A group welcome/start image control system
- A Mini App / web dashboard starter

## Critical Rules

- No user, old or new, may interact in protected groups without verification when verification is enabled.
- Commands, logs, debug text, raw API output, and secrets must stay in normal text.
- Visible bot messages should use Raj's saved stylish text system where technically safe.
- AZAI must not expose owner secrets, API keys, MongoDB URI, bot token, or admin internals.
- AZAI should refer to Aliza only as `Bhabhi Ji` or `Ma’am` in user-facing replies.
- AZAI must not claim to be a real human. It may use natural human-like Hinglish tone.

## Added Commands

### User Commands

- `/start` — main welcome/menu
- `/help` — show command list
- `/commands` — show command list
- `/setup` — profile onboarding
- `/profile` — show saved profile
- `/leaderboard` — show group leaderboard
- `/top` — alias for leaderboard
- `/setpic [name]` — save custom photo by sending or replying to a photo
- `/getpic [name]` — retrieve saved custom photo
- `/pics` — list saved custom photo names

### Owner Commands

- `/owner` — owner panel
- `/group` — group settings panel
- `/verifyon` — enable group verification
- `/verifyoff` — disable group verification
- `/setwelcome` — save group welcome picture by replying to a photo
- `/setstartpic` — save start/menu picture by replying to a photo
- `/restrict user_id reason` — add global restriction record
- `/allow user_id` — remove global restriction record
- `/mute user_id` — pause member send access
- `/unmute user_id` — restore member send access
- `/warns user_id` — show warning count
- `/clearwarns user_id` — clear warning count
- `/broadcast message` — send owner message to saved groups
- `/addpoints user_id amount` — manually update leaderboard points

## Current Status

Completed modules:

- Environment template
- Python dependency file
- Configuration loader
- MongoDB helper layer
- Stylish font utility
- Strict verification guard
- Verification on/off group setting
- Basic moderation guard
- Warning count and clear tools
- Profile onboarding
- Custom pic storage
- Group welcome/start image controls
- Leaderboard points
- Basic chat reply logic
- Owner panel and admin controls
- Broadcast base
- Mini App dashboard placeholder
- Deployment process file
- Main bot entrypoint

## Pending / Next Upgrade

- Real AI provider integration
- Full web dashboard with login
- Better leaderboard display using names instead of only user IDs
- Better role system beyond owner-only
- Rich welcome messages using saved welcome pictures
- Automated channel update posts
- Production deployment testing

Real tokens and private keys must be added only through environment variables, never committed to GitHub.
