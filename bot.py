import os
import logging
import json
import random
import requests
from flask import Flask, request, jsonify

# ================== CONFIG ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8985690585:AAGobmNJJ3hTlk6ZZllsEjd77LuAyIDIPjE")
ADMIN_ID = 7456706866
PORT = int(os.environ.get("PORT", 5000))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")

# ================== LOGGING ==================
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
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
        "room_created": "🏠 Room created!\nRoom ID: `{room_id}`\n\nShare this ID with your friend!",
        "enter_room_id": "🔗 Enter the Room ID to join:",
        "room_not_found": "❌ Room not found!",
        "room_full": "❌ Room is full!",
        "joined_room": "✅ You joined!\nGame starting...",
        "player_joined": "✅ Player joined!\nGame starting...",
        "searching": "🔍 Searching for opponent...",
        "match_found": "🎮 Match found!\nGame starting...",
        "not_your_turn": "❌ Not your turn!",
        "cell_taken": "❌ Cell already taken!",
        "how_to_text": "📖 How to Play X or 0\n\n1. Find a player or create a room\n2. Take turns placing X or 0 on the 3x3 grid\n3. First to get 3 in a row wins!\n4. Full grid = Draw!",
        "no_games": "📊 No games played yet!",
        "wins": "Wins", "losses": "Losses", "draws": "Draws",
        "select_language": "🌐 Select Language:",
        "english": "🇬🇧 English", "russian": "🇷🇺 Russian",
        "waiting_opponent": "⏳ Waiting for opponent...",
        "game_started": "🎮 Game Started!\n\nYou are {symbol}\nOpponent: {opponent_name}",
        "turn": "Turn: {name} ({symbol})",
        "rule_custom": "📜 Rule: First player = X, Second = O.\nOnly empty cells allowed!",
        "stats_title": "📊 Your Stats",
        "opponent_left": "\n(Opponent left the game)",
    },
    "ru": {
        "welcome": "🎮 Добро пожаловать в X или 0!\n\nВыберите язык:",
        "lang_selected": "✅ Язык: Русский!",
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
        "room_created": "🏠 Комната создана!\nID: `{room_id}`\n\nПоделитесь с другом!",
        "enter_room_id": "🔗 Введите ID комнаты:",
        "room_not_found": "❌ Комната не найдена!",
        "room_full": "❌ Комната заполнена!",
        "joined_room": "✅ Вы присоединились!\nИгра начинается...",
        "player_joined": "✅ Игрок присоединился!\nИгра начинается...",
        "searching": "🔍 Поиск соперника...",
        "match_found": "🎮 Матч найден!\nИгра начинается...",
        "not_your_turn": "❌ Не ваш ход!",
        "cell_taken": "❌ Клетка занята!",
        "how_to_text": "📖 Как играть в X или 0\n\n1. Найдите игрока или создайте комнату\n2. По очереди ставьте X или 0\n3. Первый с 3 в ряд побеждает!\n4. Полная сетка = Ничья!",
        "no_games": "📊 Игр пока не было!",
        "wins": "Победы", "losses": "Поражения", "draws": "Ничьи",
        "select_language": "🌐 Выберите язык:",
        "english": "🇬🇧 Английский", "russian": "🇷🇺 Русский",
        "waiting_opponent": "⏳ Ожидание соперника...",
        "game_started": "🎮 Игра началась!\n\nВы {symbol}\nСоперник: {opponent_name}",
        "turn": "Ход: {name} ({symbol})",
        "rule_custom": "📜 Правило: Первый = X, Второй = O.\nТолько пустые клетки!",
        "stats_title": "📊 Ваша статистика",
        "opponent_left": "\n(Соперник покинул игру)",
    }
}

# ================== STATE ==================
user_data = {}
active_games = {}
waiting_rooms = {}
matchmaking_queue = []

# ================== TELEGRAM API HELPERS ==================
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def tg_api(method, data=None):
    try:
        url = f"{API_URL}/{method}"
        if data:
            resp = requests.post(url, json=data, timeout=30)
        else:
            resp = requests.get(url, timeout=30)
        return resp.json()
    except Exception as e:
        logger.error(f"TG API error: {e}")
        return {}

def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    data = {"chat_id": chat_id, "text": text}
    if parse_mode:
        data["parse_mode"] = parse_mode
    if reply_markup:
        data["reply_markup"] = reply_markup
    return tg_api("sendMessage", data)

def edit_message(chat_id, message_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
    return tg_api("editMessageText", data)

def answer_callback(query_id, text=None):
    data = {"callback_query_id": query_id}
    if text:
        data["text"] = text
    return tg_api("answerCallbackQuery", data)

def get_chat(chat_id):
    return tg_api("getChat", {"chat_id": chat_id})

def set_webhook(url):
    return tg_api("setWebhook", {"url": url})

# ================== GAME HELPERS ==================
def get_text(chat_id, key, **kwargs):
    lang = user_data.get(chat_id, {}).get("lang", "en")
    text = LANG.get(lang, LANG["en"]).get(key, key)
    return text.format(**kwargs) if kwargs else text

def init_user(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {
            "lang": "en", "state": "menu", "stats": {"wins": 0, "losses": 0, "draws": 0},
            "current_game": None, "waiting_room": None, "game_msg_id": None
        }

def generate_room_id():
    return "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=6))

def make_keyboard(buttons):
    """buttons = [[{"text": "...", "callback_data": "..."}, ...], ...]"""
    return json.dumps({"inline_keyboard": buttons})

def get_main_menu(chat_id):
    return make_keyboard([
        [{"text": get_text(chat_id, "new_game"), "callback_data": "menu_newgame"}],
        [{"text": get_text(chat_id, "how_to_play"), "callback_data": "menu_howto"},
         {"text": get_text(chat_id, "leaderboard"), "callback_data": "menu_leaderboard"}],
        [{"text": get_text(chat_id, "settings"), "callback_data": "menu_settings"}]
    ])

def get_new_game_menu(chat_id):
    return make_keyboard([
        [{"text": get_text(chat_id, "create_room"), "callback_data": "game_create"}],
        [{"text": get_text(chat_id, "join_room"), "callback_data": "game_join"}],
        [{"text": get_text(chat_id, "random_match"), "callback_data": "game_random"}],
        [{"text": get_text(chat_id, "back"), "callback_data": "menu_back"}]
    ])

def get_board_keyboard(board, game_id):
    symbols = {0: "⬜", 1: "❌", 2: "⭕"}
    keyboard = []
    for row in range(3):
        row_btns = []
        for col in range(3):
            idx = row * 3 + col
            cell = board[idx]
            if cell == 0:
                row_btns.append({"text": "⬜", "callback_data": f"move_{game_id}_{idx}"})
            elif cell == 1:
                row_btns.append({"text": "❌", "callback_data": f"noop_{idx}"})
            else:
                row_btns.append({"text": "⭕", "callback_data": f"noop_{idx}"})
        keyboard.append(row_btns)
    keyboard.append([{"text": "❌ Cancel", "callback_data": f"game_cancel_{game_id}"}])
    return json.dumps({"inline_keyboard": keyboard})

def check_winner(board):
    wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    for combo in wins:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != 0:
            return board[combo[0]]
    if 0 not in board:
        return 0
    return None

def get_player_name(chat_id):
    try:
        info = get_chat(chat_id)
        if info.get("ok"):
            return info["result"].get("first_name", f"Player {chat_id}")
    except:
        pass
    return f"Player {chat_id}"

# ================== GAME LOGIC ==================
def start_game(p1, p2):
    game_id = generate_room_id()
    symbols = {p1: 1, p2: 2}
    active_games[game_id] = {
        "player1": p1, "player2": p2, "board": [0]*9,
        "turn": p1, "symbols": symbols, "game_id": game_id
    }
    user_data[p1]["current_game"] = game_id
    user_data[p1]["state"] = "playing"
    user_data[p2]["current_game"] = game_id
    user_data[p2]["state"] = "playing"

    p1_name = get_player_name(p1)
    p2_name = get_player_name(p2)

    for pid, opp_name in [(p1, p2_name), (p2, p1_name)]:
        symbol = "❌" if symbols[pid] == 1 else "⭕"
        is_turn = "✅ " + get_text(pid, "your_turn") if active_games[game_id]["turn"] == pid else "⏳ " + get_text(pid, "opponent_turn")
        text = f"{get_text(pid, 'game_started', symbol=symbol, opponent_name=opp_name)}\n\n"
        text += f"{get_text(pid, 'turn', name=p1_name if active_games[game_id]['turn'] == p1 else p2_name, symbol='❌' if active_games[game_id]['turn'] == p1 else '⭕')}\n\n"
        text += is_turn
        resp = send_message(pid, text, get_board_keyboard(active_games[game_id]["board"], game_id))
        if resp.get("ok"):
            user_data[pid]["game_msg_id"] = resp["result"]["message_id"]

def update_game_board(game_id):
    if game_id not in active_games:
        return
    game = active_games[game_id]
    p1_name = get_player_name(game["player1"])
    p2_name = get_player_name(game["player2"])

    for pid in [game["player1"], game["player2"]]:
        symbol = "❌" if game["symbols"][pid] == 1 else "⭕"
        current_name = p1_name if game["turn"] == game["player1"] else p2_name
        current_sym = "❌" if game["turn"] == game["player1"] else "⭕"
        is_turn = "✅ " + get_text(pid, "your_turn") if game["turn"] == pid else "⏳ " + get_text(pid, "opponent_turn")
        text = f"{get_text(pid, 'game_started', symbol=symbol, opponent_name=p2_name if pid == game['player1'] else p1_name)}\n\n"
        text += f"{get_text(pid, 'turn', name=current_name, symbol=current_sym)}\n\n"
        text += is_turn
        msg_id = user_data[pid].get("game_msg_id")
        if msg_id:
            edit_message(pid, msg_id, text, get_board_keyboard(game["board"], game_id))

def end_game(game_id, result):
    if game_id not in active_games:
        return
    game = active_games[game_id]
    p1_name = get_player_name(game["player1"])
    p2_name = get_player_name(game["player2"])

    if result == 0:
        for pid in [game["player1"], game["player2"]]:
            user_data[pid]["stats"]["draws"] += 1
            text = f"🎮 X or 0\n\n{get_text(pid, 'game_over')}\n{get_text(pid, 'draw')}\n\n{p1_name} (❌) vs {p2_name} (⭕)"
            msg_id = user_data[pid].get("game_msg_id")
            if msg_id:
                edit_message(pid, msg_id, text, make_keyboard([
                    [{"text": get_text(pid, "play_again"), "callback_data": "menu_newgame"}],
                    [{"text": get_text(pid, "main_menu_btn"), "callback_data": "menu_back"}]
                ]))
    else:
        winner = game["player1"] if game["symbols"][game["player1"]] == result else game["player2"]
        loser = game["player2"] if winner == game["player1"] else game["player1"]
        user_data[winner]["stats"]["wins"] += 1
        user_data[loser]["stats"]["losses"] += 1
        for pid in [game["player1"], game["player2"]]:
            is_winner = pid == winner
            text = f"🎮 X or 0\n\n{get_text(pid, 'game_over')}\n{get_text(pid, 'you_win') if is_winner else get_text(pid, 'you_lose')}\n\n{p1_name} (❌) vs {p2_name} (⭕)"
            msg_id = user_data[pid].get("game_msg_id")
            if msg_id:
                edit_message(pid, msg_id, text, make_keyboard([
                    [{"text": get_text(pid, "play_again"), "callback_data": "menu_newgame"}],
                    [{"text": get_text(pid, "main_menu_btn"), "callback_data": "menu_back"}]
                ]))

    for pid in [game["player1"], game["player2"]]:
        user_data[pid]["state"] = "menu"
        user_data[pid]["current_game"] = None
        user_data[pid]["game_msg_id"] = None
    del active_games[game_id]

# ================== COMMAND HANDLERS ==================
def handle_start(chat_id):
    init_user(chat_id)
    keyboard = make_keyboard([
        [{"text": "🇬🇧 English", "callback_data": "lang_en"},
         {"text": "🇷🇺 Русский", "callback_data": "lang_ru"}]
    ])
    send_message(chat_id, get_text(chat_id, "welcome"), keyboard)

def handle_text(chat_id, text):
    init_user(chat_id)
    state = user_data[chat_id].get("state")
    txt = text.strip().upper()

    if state == "joining":
        room_id = txt
        if room_id not in waiting_rooms:
            send_message(chat_id, get_text(chat_id, "room_not_found"), make_keyboard([
                [{"text": get_text(chat_id, "back"), "callback_data": "menu_back"}]
            ]))
            return
        if waiting_rooms[room_id] == chat_id:
            send_message(chat_id, "❌ You can't join your own room!", make_keyboard([
                [{"text": get_text(chat_id, "back"), "callback_data": "menu_back"}]
            ]))
            return
        host_id = waiting_rooms[room_id]
        del waiting_rooms[room_id]
        user_data[host_id]["waiting_room"] = None
        user_data[host_id]["state"] = "menu"
        start_game(host_id, chat_id)
        return

    send_message(chat_id, get_text(chat_id, "main_menu"), get_main_menu(chat_id))

# ================== CALLBACK HANDLERS ==================
def handle_callback(chat_id, data, query_id):
    init_user(chat_id)
    answer_callback(query_id)

    # Language
    if data == "lang_en":
        user_data[chat_id]["lang"] = "en"
        send_message(chat_id, get_text(chat_id, "lang_selected"), get_main_menu(chat_id))
        return
    if data == "lang_ru":
        user_data[chat_id]["lang"] = "ru"
        send_message(chat_id, get_text(chat_id, "lang_selected"), get_main_menu(chat_id))
        return

    # Main menu
    if data == "menu_back":
        user_data[chat_id]["state"] = "menu"
        send_message(chat_id, get_text(chat_id, "main_menu"), get_main_menu(chat_id))
        return
    if data == "menu_newgame":
        send_message(chat_id, get_text(chat_id, "main_menu"), get_new_game_menu(chat_id))
        return
    if data == "menu_howto":
        keyboard = make_keyboard([[{"text": get_text(chat_id, "back"), "callback_data": "menu_back"}]])
        send_message(chat_id, get_text(chat_id, "how_to_text") + "\n\n" + get_text(chat_id, "rule_custom"), keyboard)
        return
    if data == "menu_leaderboard":
        stats = user_data[chat_id]["stats"]
        text = f"{get_text(chat_id, 'stats_title')}\n\n🏆 {get_text(chat_id, 'wins')}: {stats['wins']}\n💔 {get_text(chat_id, 'losses')}: {stats['losses']}\n🤝 {get_text(chat_id, 'draws')}: {stats['draws']}"
        keyboard = make_keyboard([[{"text": get_text(chat_id, "back"), "callback_data": "menu_back"}]])
        send_message(chat_id, text, keyboard)
        return
    if data == "menu_settings":
        keyboard = make_keyboard([
            [{"text": get_text(chat_id, "english"), "callback_data": "lang_en"},
             {"text": get_text(chat_id, "russian"), "callback_data": "lang_ru"}],
            [{"text": get_text(chat_id, "back"), "callback_data": "menu_back"}]
        ])
        send_message(chat_id, get_text(chat_id, "select_language"), keyboard)
        return

    # Create room
    if data == "game_create":
        room_id = generate_room_id()
        waiting_rooms[room_id] = chat_id
        user_data[chat_id]["waiting_room"] = room_id
        user_data[chat_id]["state"] = "waiting"
        keyboard = make_keyboard([[{"text": get_text(chat_id, "cancel"), "callback_data": f"cancel_room_{room_id}"}]])
        send_message(chat_id, get_text(chat_id, "room_created", room_id=room_id), keyboard, "Markdown")
        return

    # Cancel room
    if data.startswith("cancel_room_"):
        room_id = data.split("_")[2]
        if room_id in waiting_rooms and waiting_rooms[room_id] == chat_id:
            del waiting_rooms[room_id]
        user_data[chat_id]["waiting_room"] = None
        user_data[chat_id]["state"] = "menu"
        send_message(chat_id, get_text(chat_id, "main_menu"), get_new_game_menu(chat_id))
        return

    # Join room
    if data == "game_join":
        user_data[chat_id]["state"] = "joining"
        keyboard = make_keyboard([[{"text": get_text(chat_id, "cancel"), "callback_data": "menu_back"}]])
        send_message(chat_id, get_text(chat_id, "enter_room_id"), keyboard)
        return

    # Random match
    if data == "game_random":
        if chat_id in matchmaking_queue:
            matchmaking_queue.remove(chat_id)
        opponent = None
        for pid in matchmaking_queue:
            if pid != chat_id:
                opponent = pid
                break
        if opponent:
            matchmaking_queue.remove(opponent)
            start_game(chat_id, opponent)
        else:
            matchmaking_queue.append(chat_id)
            user_data[chat_id]["state"] = "matchmaking"
            keyboard = make_keyboard([[{"text": get_text(chat_id, "cancel"), "callback_data": "cancel_matchmaking"}]])
            send_message(chat_id, get_text(chat_id, "searching"), keyboard)
        return

    # Cancel matchmaking
    if data == "cancel_matchmaking":
        if chat_id in matchmaking_queue:
            matchmaking_queue.remove(chat_id)
        user_data[chat_id]["state"] = "menu"
        send_message(chat_id, get_text(chat_id, "main_menu"), get_new_game_menu(chat_id))
        return

    # Game moves
    if data.startswith("move_"):
        parts = data.split("_")
        game_id = parts[1]
        cell_idx = int(parts[2])

        if game_id not in active_games:
            answer_callback(query_id, "Game not found!")
            return
        game = active_games[game_id]

        if game["turn"] != chat_id:
            answer_callback(query_id, get_text(chat_id, "not_your_turn"))
            return
        if game["board"][cell_idx] != 0:
            answer_callback(query_id, get_text(chat_id, "cell_taken"))
            return

        symbol = game["symbols"][chat_id]
        game["board"][cell_idx] = symbol
        result = check_winner(game["board"])

        if result is not None:
            end_game(game_id, result)
        else:
            game["turn"] = game["player2"] if game["turn"] == game["player1"] else game["player1"]
            update_game_board(game_id)
        return

    # Cancel game
    if data.startswith("game_cancel_"):
        game_id = data.split("_")[2]
        if game_id in active_games:
            game = active_games[game_id]
            other = game["player2"] if chat_id == game["player1"] else game["player1"]
            try:
                user_data[other]["stats"]["wins"] += 1
                text = get_text(other, "you_win") + get_text(other, "opponent_left")
                send_message(other, text, make_keyboard([
                    [{"text": get_text(other, "play_again"), "callback_data": "menu_newgame"}],
                    [{"text": get_text(other, "main_menu_btn"), "callback_data": "menu_back"}]
                ]))
            except:
                pass
            for pid in [game["player1"], game["player2"]]:
                user_data[pid]["state"] = "menu"
                user_data[pid]["current_game"] = None
                user_data[pid]["game_msg_id"] = None
            del active_games[game_id]
        user_data[chat_id]["state"] = "menu"
        user_data[chat_id]["current_game"] = None
        send_message(chat_id, get_text(chat_id, "main_menu"), get_main_menu(chat_id))
        return

    # Play again
    if data == "play_again":
        send_message(chat_id, get_text(chat_id, "main_menu"), get_new_game_menu(chat_id))
        return

# ================== FLASK APP ==================
flask_app = Flask(__name__)

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
    try:
        update = request.get_json(force=True)
        logger.info(f"Received update: {json.dumps(update)[:200]}")

        if "message" in update:
            msg = update["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")

            if text.startswith("/start"):
                handle_start(chat_id)
            elif text.startswith("/play") or text.startswith("/menu"):
                init_user(chat_id)
                send_message(chat_id, get_text(chat_id, "main_menu"), get_main_menu(chat_id))
            elif text.startswith("/stats"):
                init_user(chat_id)
                stats = user_data[chat_id]["stats"]
                send_message(chat_id, f"📊 Stats\nWins: {stats['wins']}\nLosses: {stats['losses']}\nDraws: {stats['draws']}")
            elif text.startswith("/lang"):
                handle_start(chat_id)
            elif text.startswith("/help"):
                send_message(chat_id, "🎮 Commands:\n/start - Start\n/play - New game\n/menu - Menu\n/stats - Stats\n/lang - Language\n/help - Help")
            elif text.startswith("/cancel"):
                init_user(chat_id)
                user_data[chat_id]["state"] = "menu"
                send_message(chat_id, "❌ Cancelled.", get_main_menu(chat_id))
            elif text.startswith("/create"):
                init_user(chat_id)
                room_id = generate_room_id()
                waiting_rooms[room_id] = chat_id
                user_data[chat_id]["waiting_room"] = room_id
                user_data[chat_id]["state"] = "waiting"
                keyboard = make_keyboard([[{"text": get_text(chat_id, "cancel"), "callback_data": f"cancel_room_{room_id}"}]])
                send_message(chat_id, get_text(chat_id, "room_created", room_id=room_id), keyboard, "Markdown")
            elif text.startswith("/join"):
                init_user(chat_id)
                parts = text.split()
                if len(parts) > 1:
                    room_id = parts[1].upper()
                    if room_id in waiting_rooms:
                        if waiting_rooms[room_id] == chat_id:
                            send_message(chat_id, "❌ Can't join own room!")
                            return "OK", 200
                        host_id = waiting_rooms[room_id]
                        del waiting_rooms[room_id]
                        user_data[host_id]["waiting_room"] = None
                        start_game(host_id, chat_id)
                    else:
                        send_message(chat_id, get_text(chat_id, "room_not_found"))
                else:
                    send_message(chat_id, "🔗 Usage: /join <ROOM_ID>")
            elif text.startswith("/random"):
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
                    start_game(chat_id, opponent)
                else:
                    matchmaking_queue.append(chat_id)
                    user_data[chat_id]["state"] = "matchmaking"
                    keyboard = make_keyboard([[{"text": get_text(chat_id, "cancel"), "callback_data": "cancel_matchmaking"}]])
                    send_message(chat_id, get_text(chat_id, "searching"), keyboard)
            elif text.startswith("/admin"):
                if chat_id == ADMIN_ID:
                    text = f"👑 Admin\nActive Games: {len(active_games)}\nWaiting: {len(waiting_rooms)}\nQueue: {len(matchmaking_queue)}\nUsers: {len(user_data)}"
                    send_message(chat_id, text)
                else:
                    send_message(chat_id, "❌ Admin only!")
            elif text.startswith("/broadcast"):
                if chat_id == ADMIN_ID:
                    msg_text = text[11:].strip()
                    if msg_text:
                        count = 0
                        for uid in list(user_data.keys()):
                            try:
                                send_message(uid, f"📢 Broadcast:\n\n{msg_text}")
                                count += 1
                            except:
                                pass
                        send_message(chat_id, f"✅ Broadcast to {count} users!")
                    else:
                        send_message(chat_id, "Usage: /broadcast <message>")
                else:
                    send_message(chat_id, "❌ Admin only!")
            else:
                handle_text(chat_id, text)

        elif "callback_query" in update:
            cq = update["callback_query"]
            chat_id = cq["message"]["chat"]["id"]
            data = cq["data"]
            query_id = cq["id"]
            handle_callback(chat_id, data, query_id)

        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "Error", 500

@flask_app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

# ================== MAIN ==================
if __name__ == "__main__":
    if WEBHOOK_URL:
        webhook_full = f"{WEBHOOK_URL}/{BOT_TOKEN}"
        result = set_webhook(webhook_full)
        logger.info(f"Webhook set result: {result}")
    flask_app.run(host="0.0.0.0", port=PORT)
