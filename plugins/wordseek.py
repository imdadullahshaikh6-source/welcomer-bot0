import time
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# Alag word data file se dictionaries import karna
try:
    from plugins.word_data import WORDS_4, WORDS_5, WORDS_6
except ImportError:
    try:
        from word_data import WORDS_4, WORDS_5, WORDS_6
    except ImportError:
        WORDS_4 = ["SPIN", "GRID", "FINE", "SHIN", "LOVE", "FIRE", "STAR", "GAME"]
        WORDS_5 = ["HEART", "LIGHT", "NIGHT", "DREAM", "SMILE", "WATER", "MUSIC"]
        WORDS_6 = ["FRIEND", "SPRING", "SUMMER", "WINTER", "FLOWER", "CASTLE"]

# Active games tracking per chat
GAMES = {}

def check_guess_colors(guess: str, secret: str):
    """
    Green  = Correct letter & position
    Orange = Correct letter & wrong position
    Red    = Letter not present in word
    Har color block ke beech clean space
    """
    n = len(secret)
    result = ["🟥"] * n
    secret_chars = list(secret)
    guess_chars = list(guess)

    # 1. Exact matches check
    for i in range(n):
        if guess_chars[i] == secret_chars[i]:
            result[i] = "🟩"
            secret_chars[i] = None
            guess_chars[i] = None

    # 2. Wrong spot matches check
    for i in range(n):
        if guess_chars[i] is not None and guess_chars[i] in secret_chars:
            result[i] = "🟧"
            secret_chars[secret_chars.index(guess_chars[i])] = None

    return " ".join(result)

def format_board(game):
    lines = [
        "<blockquote><b>WordSeek</b>",
        f"<b>{game['size']}-letter mode</b>  •  <b>{len(game['history'])}/30</b>\n"
    ]
    for h in game["history"]:
        lines.append(f"{h['colors']}   <b>{h['word']}</b>")
    lines.append("</blockquote>")
    return "\n".join(lines)

async def auto_stop_timer(client: Client, chat_id: int, duration_sec: int, secret_word: str):
    await asyncio.sleep(duration_sec)
    if chat_id in GAMES and GAMES[chat_id]["secret"] == secret_word:
        game = GAMES.pop(chat_id)
        try:
            await client.send_message(
                chat_id,
                f"<blockquote>⌛ <b>TIME UP!</b>\n"
                f"🎯 <b>The secret word was:</b> <code>{game['secret']}</code></blockquote>"
            )
        except Exception:
            pass

@Client.on_message(filters.command(["new", "new4", "new5", "new6"], prefixes=["/", "."]))
async def start_wordseek(client: Client, message: Message):
    chat_id = message.chat.id
    cmd = message.command[0].lower()

    if chat_id in GAMES:
        remaining = int(GAMES[chat_id]["end_time"] - time.time())
        if remaining > 0:
            await message.reply(
                f"<blockquote>⚠️ There is already a game in progress in this chat. Use <code>.end</code> to stop it.\nTime remaining: <b>{remaining}s</b></blockquote>",
                quote=True
            )
            return

    # Mode selection
    if cmd in ["new", "new5"]:
        size = 5
        minutes = 8
        secret = random.choice(WORDS_5)
    elif cmd == "new4":
        size = 4
        minutes = 5
        secret = random.choice(WORDS_4)
    else:  # new6
        size = 6
        minutes = 10
        secret = random.choice(WORDS_6)

    duration_sec = minutes * 60
    end_time = time.time() + duration_sec

    GAMES[chat_id] = {
        "size": size,
        "secret": secret,
        "end_time": end_time,
        "history": [],
        "guessed_words": set(),
        "max_guesses": 30
    }

    asyncio.create_task(auto_stop_timer(client, chat_id, duration_sec, secret))
    await message.reply(f"<blockquote>🎮 <b>Started new{size} wordseek!</b></blockquote>")

# Game end command (.end / /end) - Secret word reveal nahi hoga
@Client.on_message(filters.command(["end", "stopgame"], prefixes=["/", "."]))
async def end_wordseek(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id not in GAMES:
        await message.reply("<blockquote>There is no active game to end.</blockquote>", quote=True)
        return

    GAMES.pop(chat_id)
    await message.reply("<blockquote>🛑 <b>Game ended.</b></blockquote>", quote=True)

# Active chat message listener
@Client.on_message(filters.group & filters.text & ~filters.bot, group=0)
async def wordseek_guess_checker(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id not in GAMES:
        return

    if not message.text:
        return

    guess = message.text.strip().upper()

    # Commands ya multiple words ignore karein
    if guess.startswith(("/", ".", "!", "#")) or len(guess.split()) > 1:
        return

    game = GAMES[chat_id]
    size = game["size"]

    if len(guess) != size or not guess.isalpha():
        return

    if guess in game["guessed_words"]:
        await message.reply(
            "<blockquote><b>WordSeek</b>\nSomeone has already guessed your word. Please try another one!</blockquote>",
            quote=True
        )
        return

    valid_pool = WORDS_4 if size == 4 else (WORDS_5 if size == 5 else WORDS_6)
    if guess not in valid_pool:
        await message.reply(
            f"<blockquote><b>WordSeek</b>\n<code>{message.text.strip()}</code> is not a valid {size}-letter word.</blockquote>",
            quote=True
        )
        return

    secret = game["secret"]
    colors = check_guess_colors(guess, secret)

    game["guessed_words"].add(guess)
    game["history"].append({
        "word": guess,
        "colors": colors,
        "user": message.from_user.first_name if message.from_user else "User"
    })

    board_text = format_board(game)

    # WIN CHECK
    if guess == secret:
        GAMES.pop(chat_id)
        mention = message.from_user.mention if message.from_user else "Winner"
        win_text = (
            f"{board_text}\n\n"
            f"<blockquote>🎉 <b>CONGRATULATIONS!</b>\n"
            f"🏆 {mention} won! The word was <code>{secret}</code> 🥳</blockquote>"
        )
        await message.reply(win_text, quote=True)
        return

    # MAX GUESSES REACHED
    if len(game["history"]) >= game["max_guesses"]:
        GAMES.pop(chat_id)
        lose_text = (
            f"{board_text}\n\n"
            f"<blockquote>⌛ <b>GAME OVER!</b> Max guesses reached.\n"
            f"🎯 <b>Correct word was:</b> <code>{secret}</code></blockquote>"
        )
        await message.reply(lose_text, quote=True)
        return

    await message.reply(board_text, quote=True)
    
