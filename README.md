# 🎮 X or 0 (Tic-Tac-Toe) Telegram Bot

A multiplayer Tic-Tac-Toe game bot for Telegram with language support (English & Russian).

## Features

- ✅ **Real-time Multiplayer** - Play with friends or random players
- ✅ **Room System** - Create private rooms with unique IDs
- ✅ **Random Matchmaking** - Find opponents automatically
- ✅ **Language Selection** - English & Russian support
- ✅ **Score Tracking** - Wins, losses, and draws statistics
- ✅ **Admin Panel** - Broadcast messages and view stats
- ✅ **Free Hosting** - Ready for Render.com deployment

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot & select language |
| `/play` | Start a new game |
| `/menu` | Open main menu |
| `/stats` | View your statistics |
| `/lang` | Change language |
| `/create` | Create a private room |
| `/join <ROOM_ID>` | Join a room |
| `/random` | Find random opponent |
| `/help` | Show help |

## Admin Commands

| Command | Description |
|---------|-------------|
| `/admin` | View bot statistics |
| `/broadcast <msg>` | Send message to all users |

## Deployment on Render (Free)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tic-tac-toe-bot.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) and sign up (free, no credit card)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Render will auto-detect Python
5. Set Environment Variable:
   - `WEBHOOK_URL`: Your Render service URL (e.g., `https://tic-tac-toe-bot.onrender.com`)
6. Click **Deploy**

### Step 3: Set Webhook
After deployment, set the webhook URL:
```
https://api.telegram.org/bot8985690585:AAGobmNJJ3hTlk6ZZllsEjd77LuAyIDIPjE/setWebhook?url=https://YOUR_RENDER_URL.onrender.com/8985690585:AAGobmNJJ3hTlk6ZZllsEjd77LuAyIDIPjE
```

## Game Rules

1. Players take turns placing X or O on a 3×3 grid
2. First player gets **X**, second player gets **O**
3. First to get 3 in a row (horizontal, vertical, or diagonal) wins
4. If the grid is full with no winner, it's a draw

## Project Structure

```
tic_tac_toe_bot/
├── bot.py              # Main bot application
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── Procfile            # Process file for gunicorn
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Your Telegram bot token |
| `WEBHOOK_URL` | Your Render service URL |
| `PORT` | Port number (auto-set by Render) |

## License

MIT License - Free to use and modify!

---
Made with ❤️ for Telegram gamers!
