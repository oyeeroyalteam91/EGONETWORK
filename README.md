# AZAI — EGO NETWORK

AZAI is the official EGO NETWORK community automation system.

**Network:** EGO NETWORK  
**Established:** 2026  
**Main Purpose:** Telegram group protection, verification, stylish community replies, moderation, economy, quizzes, games, shop, leaderboard, custom pics, owner controls, and future Mini App dashboard.

## Core Direction

AZAI works as:

- A Telegram community automation bot
- A strict group verification gate
- A moderation and warning system
- A stylish Hinglish conversational assistant for allowed interactions
- An owner-controlled management system
- An economy wallet system
- Auto anime/GK quiz system
- Telegram dice game command system
- Shop and inventory system
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
- Start media must attach with the start caption in one message, not as a separate message.
- Shop purchase media should use saved photo/GIF file IDs when available.

## Added Commands

### User Commands

- `/start` — main welcome/menu with saved media if configured
- `/help` — show command list
- `/commands` — show command list
- `/setup` — profile onboarding
- `/profile` — show saved profile
- `/balance` — show coin balance
- `/daily` — claim daily coins
- `/leaderboard` — show group leaderboard
- `/top` — alias for leaderboard
- `/animequiz` — send anime quiz with 4 option buttons
- `/gkquiz` — send GK quiz with 4 option buttons
- `/dice` — Telegram dice game
- `/dart` — Telegram dart game
- `/basketball` — Telegram basketball game
- `/football` — Telegram football game
- `/bowling` — Telegram bowling game
- `/shop` — show shop with buy buttons
- `/inventory` — show purchased items
- `/items` — alias for inventory
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
- `/setstartmedia` — save start photo/video/GIF for `/start`
- `/startmedia` — show saved start media type
- `/setshopmedia item_key` — attach photo/GIF media to a shop item
- `/autoquizon` — enable auto anime/GK quiz every 30 minutes
- `/autoquizoff` — disable auto quiz
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
- Python dependency file with job queue support
- Configuration loader
- MongoDB helper layer
- Stylish font utility
- Strict verification guard
- Verification on/off group setting
- Basic moderation guard
- Warning count and clear tools
- Profile onboarding
- Economy wallet and daily reward
- Anime/GK quiz with 4 buttons, one chance, and coin reward
- Auto quiz job every 30 minutes for enabled groups
- Telegram dice games: dice, dart, basketball, football, bowling
- Shop with buy buttons, inventory, and media/GIF support
- Custom pic storage
- Start media saved as photo/video/GIF and sent with start caption in one message
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
- Rich welcome messages using saved welcome pictures on member join
- Automated channel update posts
- Production deployment testing

Real tokens and private keys must be added only through environment variables, never committed to GitHub.
