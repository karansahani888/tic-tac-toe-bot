import os
import logging
import json
import random
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests

# ================== CONFIG ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8985690585:AAGobmNJJ3hTlk6ZZllsEjd77LuAyIDIPjE")
ADMIN_ID = 7456706866
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")  # Will be set after deployment
PORT = int(os.environ.get("PORT", 5000))

# ================== LOGGING ==================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== TRANSLATIONS ==================
LANG = {
    "en": {
        "welcome": "🎮 Welcome to X or 0 (Tic-Tac-Toe)!\n\nSelect your language:",
        "lang_selected": "✅ Language set to English!",
        "main_menu": "🎮 X or 0 Game\n\nChoose an option:",
        "new_game": "🆕 New Game",
        "how_to_play": "📖 How to Play",
        "leaderboard": "🏆 Leaderboard",
        "settings": "⚙️ Settings",
        "find_player": "🔍 Find Player",
        "create_room": "🏠 Create Room",
        "join_room": "🔗 Join Room",
        "random_match": "🎲 Random Match",
        "back": "⬅️ Back",
        "cancel": "❌ Cancel",
        "your_turn": "✅ Your turn! Choose a cell:",
        "opponent_turn": "⏳ Waiting for opponent...",
        "you_win": "🎉 You Win!",
        "you_lose": "😢 You Lose!",
        "draw": "🤝 It's a Draw!",
        "game_over": "Game Over!",
        "play_again": "🔄 Play Again",
        "main_menu_btn": "🏠 Main Menu",
        "room_created": "🏠 Room created!\nRoom ID: `{room_id}`\n\nShare this ID with your friend to join!",
        "enter_room_id": "🔗 Enter the Room ID to join:",
        "room_not_found": "❌ Room not found!",
        "room_full": "❌ Room is full!",
        "joined_room": "✅ You joined the room!\nGame starting...",
        "player_joined": "✅ Player joined!\nGame starting...",
        "searching": "🔍 Searching for opponent...",
        "match_found": "🎮 Match found!\nGame starting...",
        "not_your_turn": "❌ Not your turn!",
        "cell_taken": "❌ Cell already taken!",
        "invalid_move": "❌ Invalid move!",
        "how_to_text": "📖 How to Play X or 0\n\n1. Find a player or create a room\n2. Take turns placing X or 0 on the 3x3 grid\n3. First to get 3 in a row (horizontal, vertical, or diagonal) wins!\n4. If grid is full with no winner, it's a draw!",
        "no_games": "📊 No games played yet!",
        "wins": "Wins",
        "losses": "Losses",
        "draws": "Draws",
        "select_language": "🌐 Select Language:",
        "english": "🇬🇧 English",
        "russian": "🇷🇺 Russian",
        "waiting_opponent": "⏳ Waiting for opponent to join...",
        "game_started": "🎮 Game Started!\n\nYou are {symbol}\nOpponent: {opponent_name}",
        "turn": "Turn: {name} ({symbol})",
        "rule_custom": "📜 Special Rule: First player gets X, second gets 0.\nYou can only place in empty cells!",
        "stats_title": "📊 Your Stats",
    },
    "ru": {
        "welcome": "🎮 Добро пожаловать в X или 0 (Крестики-Нолики)!\n\nВыберите язык:",
        "lang_selected": "✅ Язык установлен на Русский!",
        "main_menu": "🎮 Игра X или 0\n\nВыберите опцию:",
        "new_game": "🆕 Новая игра",
        "how_to_play": "📖 Как играть",
        "leaderboard": "🏆 Таблица лидеров",
        "settings": "⚙️ Настройки",
        "find_player": "🔍 Найти игрока",
        "create_room": "🏠 Создать комнату",
        "join_room": "🔗 Присоединиться",
        "random_match": "🎲 Случайный матч",
        "back": "⬅️ Назад",
        "cancel": "❌ Отмена",
        "your_turn": "✅ Ваш ход! Выберите клетку:",
        "opponent_turn": "⏳ Ожидание соперника...",
        "you_win": "🎉 Вы победили!",
        "you_lose": "😢 Вы проиграли!",
        "draw": "🤝 Ничья!",
        "game_over": "Игра окончена!",
        "play_again": "🔄 Играть снова",
        "main_menu_btn": "🏠 Главное меню",
        "room_created": "🏠 Комната создана!\nID комнаты: `{room_id}`\n\nПоделитесь этим ID с другом, чтобы присоединиться!",
        "enter_room_id": "🔗 Введите ID комнаты для присоединения:",
        "room_not_found": "❌ Комната не найдена!",
        "room_full": "❌ Комната заполнена!",
        "joined_room": "✅ Вы присоединились к комнате!\nИгра начинается...",
        "player_joined": "✅ Игрок присоединился!\nИгра начинается...",
        "searching": "🔍 Поиск соперника...",
        "match_found": "🎮 Матч найден!\nИгра начинается...",
        "not_your_turn": "❌ Не ваш ход!",
        "cell_taken": "❌ Клетка уже занята!",
        "invalid_move": "❌ Неверный ход!",
        "how_to_text": "📖 Как играть в X или 0\n\n1. Найдите игрока или создайте комнату\n2. По очереди ставьте X или 0 на сетке 3x3\n3. Первый, кто соберет 3 в ряд (горизонтально, вертикально или по диагонали), побеждает!\n4. Если сетка заполнена без победителя — ничья!",
        "no_games": "📊 Игр пока не было!",
        "wins": "Победы",
        "losses": "Поражения",
        "draws": "Ничьи",
        "select_language": "🌐 Выберите язык:",
        "english": "🇬🇧 Английский",
        "russian": "🇷🇺 Русский",
        "waiting_opponent": "⏳ Ожидание соперника...",
        "game_started": "🎮 Игра началась!\n\nВы {symbol}\nСоперник: {opponent_name}",
        "turn": "Ход: {name} ({symbol})",
        "rule_custom": "📜 Особое правило: Первый игрок получает X, второй — 0.\nМожно ставить только в пустые клетки!",
        "stats_title": "📊 Ваша статистика",
    }
}

# ================== GAME STATE ==================
# Structure: {chat_id: {"lang": "en", "state": "menu", "game": {...}, "stats": {...}}}
user_data = {}

# Active games: {room_id: {"player1": chat_id, "player2": chat_id, "board": [...], "turn": chat_id, "symbols": {...}}}
active_games = {}

# Waiting rooms: {room_id: chat_id}
waiting_rooms = {}

# Matchmaking queue: [chat_id, ...]
matchmaking_queue = []

# ================== HELPER FUNCTIONS ==================
def get_text(chat_id, key, **kwargs):
    lang = user_data.get(chat_id, {}).get("lang", "en")
    text = LANG.get(lang, LANG["en"]).get(key, key)
    return text.format(**kwargs) if kwargs else text

def get_main_menu(chat_id):
    lang = user_data.get(chat_id, {}).get("lang", "en")
    keyboard = [
        [InlineKeyboardButton(get_text(chat_id, "new_game"), callback_data="menu_newgame")],
        [InlineKeyboardButton(get_text(chat_id, "how_to_play"), callback_data="menu_howto"),
         InlineKeyboardButton(get_text(chat_id, "leaderboard"), callback_data="menu_leaderboard")],
        [InlineKeyboardButton(get_text(chat_id, "settings"), callback_data="menu_settings")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_new_game_menu(chat_id):
    keyboard = [
        [InlineKeyboardButton(get_text(chat_id, "create_room"), callback_data="game_create")],
        [InlineKeyboardButton(get_text(chat_id, "join_room"), callback_data="game_join")],
        [InlineKeyboardButton(get_text(chat_id, "random_match"), callback_data="game_random")],
        [InlineKeyboardButton(get_text(chat_id, "back"), callback_data="menu_back")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_board_keyboard(board, chat_id, game_id):
    """Generate inline keyboard for 3x3 board"""
    keyboard = []
    symbols = {0: "⬜", 1: "❌", 2: "⭕"}

    for row in range(3):
        row_buttons = []
        for col in range(3):
            idx = row * 3 + col
            cell = board[idx]
            if cell == 0:
                row_buttons.append(InlineKeyboardButton("⬜", callback_data=f"move_{game_id}_{idx}"))
            elif cell == 1:
                row_buttons.append(InlineKeyboardButton("❌", callback_data=f"noop_{idx}"))
            else:
                row_buttons.append(InlineKeyboardButton("⭕", callback_data=f"noop_{idx}"))
        keyboard.append(row_buttons)

    # Add game control buttons
    keyboard.append([
        InlineKeyboardButton(get_text(chat_id, "cancel"), callback_data=f"game_cancel_{game_id}")
    ])

    return InlineKeyboardMarkup(keyboard)

def check_winner(board):
    """Check if there's a winner. Returns 1 (X), 2 (O), 0 (draw), or None (ongoing)"""
    wins = [
        [0,1,2], [3,4,5], [6,7,8],  # rows
        [0,3,6], [1,4,7], [2,5,8],  # cols
        [0,4,8], [2,4,6]             # diagonals
    ]

    for combo in wins:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != 0:
            return board[combo[0]]

    if 0 not in board:
        return 0  # Draw

    return None  # Game ongoing

def init_user(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {
            "lang": "en",
            "state": "menu",
            "stats": {"wins": 0, "losses": 0, "draws": 0},
            "current_game": None,
            "waiting_room": None
        }

def generate_room_id():
    return "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=6))

# ================== BOT HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    init_user(chat_id)

    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ]

    await update.message.reply_text(
        get_text(chat_id, "welcome"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    data = query.data

    init_user(chat_id)

    # Language selection
    if data == "lang_en":
        user_data[chat_id]["lang"] = "en"
        await query.edit_message_text(
            get_text(chat_id, "lang_selected"),
            reply_markup=get_main_menu(chat_id)
        )
        return
    elif data == "lang_ru":
        user_data[chat_id]["lang"] = "ru"
        await query.edit_message_text(
            get_text(chat_id, "lang_selected"),
            reply_markup=get_main_menu(chat_id)
        )
        return

    # Main menu
    if data == "menu_back":
        await query.edit_message_text(
            get_text(chat_id, "main_menu"),
            reply_markup=get_main_menu(chat_id)
        )
        return

    if data == "menu_newgame":
        await query.edit_message_text(
            get_text(chat_id, "main_menu"),
            reply_markup=get_new_game_menu(chat_id)
        )
        return

    if data == "menu_howto":
        keyboard = [[InlineKeyboardButton(get_text(chat_id, "back"), callback_data="menu_back")]]
        await query.edit_message_text(
            get_text(chat_id, "how_to_text") + "\n\n" + get_text(chat_id, "rule_custom"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data == "menu_leaderboard":
        stats = user_data[chat_id]["stats"]
        text = f"{get_text(chat_id, 'stats_title')}\n\n"
        text += f"🏆 {get_text(chat_id, 'wins')}: {stats['wins']}\n"
        text += f"💔 {get_text(chat_id, 'losses')}: {stats['losses']}\n"
        text += f"🤝 {get_text(chat_id, 'draws')}: {stats['draws']}"

        keyboard = [[InlineKeyboardButton(get_text(chat_id, "back"), callback_data="menu_back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "menu_settings":
        keyboard = [
            [InlineKeyboardButton(get_text(chat_id, "english"), callback_data="lang_en"),
             InlineKeyboardButton(get_text(chat_id, "russian"), callback_data="lang_ru")],
            [InlineKeyboardButton(get_text(chat_id, "back"), callback_data="menu_back")]
        ]
        await query.edit_message_text(
            get_text(chat_id, "select_language"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Create room
    if data == "game_create":
        room_id = generate_room_id()
        waiting_rooms[room_id] = chat_id
        user_data[chat_id]["waiting_room"] = room_id
        user_data[chat_id]["state"] = "waiting"

        keyboard = [
            [InlineKeyboardButton(get_text(chat_id, "cancel"), callback_data=f"cancel_room_{room_id}")]
        ]

        await query.edit_message_text(
            get_text(chat_id, "room_created", room_id=room_id),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    # Cancel room
    if data.startswith("cancel_room_"):
        room_id = data.split("_")[2]
        if room_id in waiting_rooms and waiting_rooms[room_id] == chat_id:
            del waiting_rooms[room_id]
        user_data[chat_id]["waiting_room"] = None
        user_data[chat_id]["state"] = "menu"

        await query.edit_message_text(
            get_text(chat_id, "main_menu"),
            reply_markup=get_new_game_menu(chat_id)
        )
        return

    # Join room
    if data == "game_join":
        user_data[chat_id]["state"] = "joining"
        await query.edit_message_text(
            get_text(chat_id, "enter_room_id"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text(chat_id, "cancel"), callback_data="menu_back")]
            ])
        )
        return

    # Random match
    if data == "game_random":
        if chat_id in matchmaking_queue:
            matchmaking_queue.remove(chat_id)

        # Try to find opponent
        opponent = None
        for pid in matchmaking_queue:
            if pid != chat_id:
                opponent = pid
                break

        if opponent:
            matchmaking_queue.remove(opponent)
            await start_game(chat_id, opponent, context)
        else:
            matchmaking_queue.append(chat_id)
            user_data[chat_id]["state"] = "matchmaking"
            await query.edit_message_text(
                get_text(chat_id, "searching"),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(get_text(chat_id, "cancel"), callback_data="cancel_matchmaking")]
                ])
            )
        return

    # Cancel matchmaking
    if data == "cancel_matchmaking":
        if chat_id in matchmaking_queue:
            matchmaking_queue.remove(chat_id)
        user_data[chat_id]["state"] = "menu"
        await query.edit_message_text(
            get_text(chat_id, "main_menu"),
            reply_markup=get_new_game_menu(chat_id)
        )
        return

    # Game moves
    if data.startswith("move_"):
        parts = data.split("_")
        game_id = parts[1]
        cell_idx = int(parts[2])

        if game_id not in active_games:
            await query.answer("Game not found!")
            return

        game = active_games[game_id]

        if game["turn"] != chat_id:
            await query.answer(get_text(chat_id, "not_your_turn"))
            return

        if game["board"][cell_idx] != 0:
            await query.answer(get_text(chat_id, "cell_taken"))
            return

        # Make move
        symbol = game["symbols"][chat_id]
        game["board"][cell_idx] = symbol

        # Check winner
        result = check_winner(game["board"])

        if result is not None:
            # Game over
            await end_game(game_id, result, context)
        else:
            # Switch turn
            game["turn"] = game["player2"] if game["turn"] == game["player1"] else game["player1"]
            await update_game_board(game_id, context)

        return

    # Cancel game
    if data.startswith("game_cancel_"):
        game_id = data.split("_")[2]
        if game_id in active_games:
            game = active_games[game_id]
            other_player = game["player2"] if chat_id == game["player1"] else game["player1"]

            # Notify other player
            try:
                await context.bot.send_message(
                    other_player,
                    get_text(other_player, "you_win") + "\n" + get_text(other_player, "opponent_left"),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(get_text(other_player, "play_again"), callback_data="menu_newgame")],
                        [InlineKeyboardButton(get_text(other_player, "main_menu_btn"), callback_data="menu_back")]
                    ])
                )
                user_data[other_player]["stats"]["wins"] += 1
            except:
                pass

            del active_games[game_id]

        user_data[chat_id]["state"] = "menu"
        user_data[chat_id]["current_game"] = None

        await query.edit_message_text(
            get_text(chat_id, "main_menu"),
            reply_markup=get_main_menu(chat_id)
        )
        return

    # Play again
    if data == "play_again":
        await query.edit_message_text(
            get_text(chat_id, "main_menu"),
            reply_markup=get_new_game_menu(chat_id)
        )
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip().upper()

    init_user(chat_id)

    # Handle room ID input for joining
    if user_data[chat_id].get("state") == "joining":
        room_id = text

        if room_id not in waiting_rooms:
            await update.message.reply_text(
                get_text(chat_id, "room_not_found"),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(get_text(chat_id, "back"), callback_data="menu_back")]
                ])
            )
            return

        if waiting_rooms[room_id] == chat_id:
            await update.message.reply_text(
                "❌ You can't join your own room!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(get_text(chat_id, "back"), callback_data="menu_back")]
                ])
            )
            return

        host_id = waiting_rooms[room_id]
        del waiting_rooms[room_id]

        await start_game(host_id, chat_id, context)
        return

    # Default: show menu
    await update.message.reply_text(
        get_text(chat_id, "main_menu"),
        reply_markup=get_main_menu(chat_id)
    )

async def start_game(player1, player2, context):
    """Start a new game between two players"""
    game_id = generate_room_id()

    # Randomly assign symbols
    symbols = {player1: 1, player2: 2}  # 1=X, 2=O

    active_games[game_id] = {
        "player1": player1,
        "player2": player2,
        "board": [0] * 9,
        "turn": player1,  # Player1 starts
        "symbols": symbols,
        "game_id": game_id
    }

    user_data[player1]["current_game"] = game_id
    user_data[player1]["state"] = "playing"
    user_data[player2]["current_game"] = game_id
    user_data[player2]["state"] = "playing"

    # Get player names
    try:
        p1_info = await context.bot.get_chat(player1)
        p2_info = await context.bot.get_chat(player2)
        p1_name = p1_info.first_name or "Player 1"
        p2_name = p2_info.first_name or "Player 2"
    except:
        p1_name = "Player 1"
        p2_name = "Player 2"

    # Send game started message to both players
    for pid, opp_name in [(player1, p2_name), (player2, p1_name)]:
        symbol = "❌" if symbols[pid] == 1 else "⭕"
        opp_symbol = "⭕" if symbols[pid] == 1 else "❌"

        is_turn = "✅ " + get_text(pid, "your_turn") if active_games[game_id]["turn"] == pid else "⏳ " + get_text(pid, "opponent_turn")

        text = f"{get_text(pid, 'game_started', symbol=symbol, opponent_name=opp_name)}\n\n"
        text += f"{get_text(pid, 'turn', name=p1_name if active_games[game_id]['turn'] == player1 else p2_name, symbol='❌' if active_games[game_id]['turn'] == player1 else '⭕')}\n\n"
        text += is_turn

        try:
            msg = await context.bot.send_message(
                pid,
                text,
                reply_markup=get_board_keyboard(active_games[game_id]["board"], pid, game_id)
            )
            user_data[pid]["game_message_id"] = msg.message_id
        except Exception as e:
            logger.error(f"Error sending game message: {e}")

async def update_game_board(game_id, context):
    """Update the game board for both players"""
    if game_id not in active_games:
        return

    game = active_games[game_id]

    try:
        p1_info = await context.bot.get_chat(game["player1"])
        p2_info = await context.bot.get_chat(game["player2"])
        p1_name = p1_info.first_name or "Player 1"
        p2_name = p2_info.first_name or "Player 2"
    except:
        p1_name = "Player 1"
        p2_name = "Player 2"

    for pid in [game["player1"], game["player2"]]:
        symbol = "❌" if game["symbols"][pid] == 1 else "⭕"
        current_player_name = p1_name if game["turn"] == game["player1"] else p2_name
        current_symbol = "❌" if game["turn"] == game["player1"] else "⭕"

        is_turn = "✅ " + get_text(pid, "your_turn") if game["turn"] == pid else "⏳ " + get_text(pid, "opponent_turn")

        text = f"{get_text(pid, 'game_started', symbol=symbol, opponent_name=p2_name if pid == game['player1'] else p1_name)}\n\n"
        text += f"{get_text(pid, 'turn', name=current_player_name, symbol=current_symbol)}\n\n"
        text += is_turn

        try:
            await context.bot.edit_message_text(
                text,
                chat_id=pid,
                message_id=user_data[pid].get("game_message_id"),
                reply_markup=get_board_keyboard(game["board"], pid, game_id)
            )
        except Exception as e:
            # If edit fails, send new message
            try:
                msg = await context.bot.send_message(
                    pid,
                    text,
                    reply_markup=get_board_keyboard(game["board"], pid, game_id)
                )
                user_data[pid]["game_message_id"] = msg.message_id
            except Exception as e2:
                logger.error(f"Error updating board: {e2}")

async def end_game(game_id, result, context):
    """End the game and show results"""
    if game_id not in active_games:
        return

    game = active_games[game_id]

    try:
        p1_info = await context.bot.get_chat(game["player1"])
        p2_info = await context.bot.get_chat(game["player2"])
        p1_name = p1_info.first_name or "Player 1"
        p2_name = p2_info.first_name or "Player 2"
    except:
        p1_name = "Player 1"
        p2_name = "Player 2"

    # Determine winner
    if result == 0:
        # Draw
        for pid in [game["player1"], game["player2"]]:
            user_data[pid]["stats"]["draws"] += 1
            symbol = "❌" if game["symbols"][pid] == 1 else "⭕"

            text = f"🎮 X or 0\n\n"
            text += f"{get_text(pid, 'game_over')}\n"
            text += f"{get_text(pid, 'draw')}\n\n"
            text += f"{p1_name} (❌) vs {p2_name} (⭕)"

            try:
                await context.bot.edit_message_text(
                    text,
                    chat_id=pid,
                    message_id=user_data[pid].get("game_message_id"),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(get_text(pid, "play_again"), callback_data="menu_newgame")],
                        [InlineKeyboardButton(get_text(pid, "main_menu_btn"), callback_data="menu_back")]
                    ])
                )
            except:
                pass
    else:
        # Someone won
        winner = game["player1"] if game["symbols"][game["player1"]] == result else game["player2"]
        loser = game["player2"] if winner == game["player1"] else game["player1"]

        user_data[winner]["stats"]["wins"] += 1
        user_data[loser]["stats"]["losses"] += 1

        winner_symbol = "❌" if result == 1 else "⭕"

        for pid in [game["player1"], game["player2"]]:
            symbol = "❌" if game["symbols"][pid] == 1 else "⭕"
            is_winner = pid == winner

            text = f"🎮 X or 0\n\n"
            text += f"{get_text(pid, 'game_over')}\n"
            text += f"{get_text(pid, 'you_win') if is_winner else get_text(pid, 'you_lose')}\n\n"
            text += f"{p1_name} (❌) vs {p2_name} (⭕)"

            try:
                await context.bot.edit_message_text(
                    text,
                    chat_id=pid,
                    message_id=user_data[pid].get("game_message_id"),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(get_text(pid, "play_again"), callback_data="menu_newgame")],
                        [InlineKeyboardButton(get_text(pid, "main_menu_btn"), callback_data="menu_back")]
                    ])
                )
            except:
                pass

    # Clean up
    for pid in [game["player1"], game["player2"]]:
        user_data[pid]["state"] = "menu"
        user_data[pid]["current_game"] = None

    del active_games[game_id]

# ================== FLASK APP FOR WEBHOOK ==================
flask_app = Flask(__name__)

# Initialize bot application
application = Application.builder().token(BOT_TOKEN).build()

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_callback))
application.add_handler(CommandHandler("play", start))
application.add_handler(CommandHandler("menu", lambda u, c: u.message.reply_text(
    get_text(u.effective_chat.id, "main_menu"),
    reply_markup=get_main_menu(u.effective_chat.id)
)))
application.add_handler(CommandHandler("stats", lambda u, c: u.message.reply_text(
    f"📊 Stats\nWins: {user_data.get(u.effective_chat.id, {}).get('stats', {}).get('wins', 0)}\n"
    f"Losses: {user_data.get(u.effective_chat.id, {}).get('stats', {}).get('losses', 0)}\n"
    f"Draws: {user_data.get(u.effective_chat.id, {}).get('stats', {}).get('draws', 0)}"
)))
application.add_handler(CommandHandler("lang", lambda u, c: u.message.reply_text(
    get_text(u.effective_chat.id, "select_language"),
    reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ])
)))
application.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text(
    "🎮 X or 0 Bot Commands:\n\n"
    "/start - Start the bot\n"
    "/play - Start a new game\n"
    "/menu - Main menu\n"
    "/stats - Your statistics\n"
    "/lang - Change language\n"
    "/help - Show this help"
)))
application.add_handler(CommandHandler("cancel", lambda u, c: u.message.reply_text(
    "❌ Cancelled.",
    reply_markup=get_main_menu(u.effective_chat.id)
)))
application.add_handler(CommandHandler("join", lambda u, c: handle_join_command(u, c)))

async def handle_join_command(update, context):
    chat_id = update.effective_chat.id
    init_user(chat_id)

    if context.args:
        room_id = context.args[0].upper()
        if room_id in waiting_rooms:
            if waiting_rooms[room_id] == chat_id:
                await update.message.reply_text("❌ You can't join your own room!")
                return
            host_id = waiting_rooms[room_id]
            del waiting_rooms[room_id]
            await start_game(host_id, chat_id, context)
        else:
            await update.message.reply_text(get_text(chat_id, "room_not_found"))
    else:
        await update.message.reply_text(
            "🔗 Usage: /join <ROOM_ID>\nExample: /join ABC123"
        )

application.add_handler(CommandHandler("create", lambda u, c: create_room_command(u, c)))

async def create_room_command(update, context):
    chat_id = update.effective_chat.id
    init_user(chat_id)
    room_id = generate_room_id()
    waiting_rooms[room_id] = chat_id
    user_data[chat_id]["waiting_room"] = room_id
    user_data[chat_id]["state"] = "waiting"

    await update.message.reply_text(
        get_text(chat_id, "room_created", room_id=room_id),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_text(chat_id, "cancel"), callback_data=f"cancel_room_{room_id}")]
        ])
    )

application.add_handler(CommandHandler("random", lambda u, c: random_match_command(u, c)))

async def random_match_command(update, context):
    chat_id = update.effective_chat.id
    init_user(chat_id)

    if chat_id in matchmaking_queue:
        matchmaking_queue.remove(chat_id)

    opponent = None
    for pid in matchmaking_queue:
        if pid != chat_id:
            opponent = pid
            break

    if opponent:
        matchmaking_queue.remove(opponent)
        await start_game(chat_id, opponent, context)
    else:
        matchmaking_queue.append(chat_id)
        user_data[chat_id]["state"] = "matchmaking"
        await update.message.reply_text(
            get_text(chat_id, "searching"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_text(chat_id, "cancel"), callback_data="cancel_matchmaking")]
            ])
        )

application.add_handler(CommandHandler("admin", lambda u, c: admin_command(u, c)))

async def admin_command(update, context):
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_ID:
        await update.message.reply_text("❌ Admin only!")
        return

    text = f"👑 Admin Panel\n\n"
    text += f"Active Games: {len(active_games)}\n"
    text += f"Waiting Rooms: {len(waiting_rooms)}\n"
    text += f"Matchmaking Queue: {len(matchmaking_queue)}\n"
    text += f"Total Users: {len(user_data)}"

    await update.message.reply_text(text)

application.add_handler(CommandHandler("broadcast", lambda u, c: broadcast_command(u, c)))

async def broadcast_command(update, context):
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_ID:
        await update.message.reply_text("❌ Admin only!")
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    message = " ".join(context.args)
    count = 0
    for uid in list(user_data.keys()):
        try:
            await context.bot.send_message(uid, f"📢 Broadcast:\n\n{message}")
            count += 1
        except:
            pass

    await update.message.reply_text(f"✅ Broadcast sent to {count} users!")

# Message handler (must be last)
application.add_handler(CommandHandler("noop", lambda u, c: None))  # Dummy handler
application.add_handler(CommandHandler("noop_", lambda u, c: None))  # Dummy handler

# Add message handler for text messages
from telegram.ext import MessageHandler, filters
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@flask_app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "✅ X or 0 Bot is running!",
        "active_games": len(active_games),
        "waiting_rooms": len(waiting_rooms),
        "matchmaking_queue": len(matchmaking_queue),
        "total_users": len(user_data)
    })

@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Handle incoming webhook updates from Telegram"""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "Error", 500

@flask_app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

# ================== MAIN ==================
if __name__ == "__main__":
    # Set webhook
    webhook_url = os.environ.get("WEBHOOK_URL", "")
    if webhook_url:
        full_webhook = f"{webhook_url}/{BOT_TOKEN}"
        try:
            requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={full_webhook}")
            logger.info(f"Webhook set to: {full_webhook}")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")

    # Initialize and start the application
    application.initialize()
    application.start()

    # Run Flask
    flask_app.run(host="0.0.0.0", port=PORT)
