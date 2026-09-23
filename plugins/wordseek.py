import time
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# Active game state per group
GAMES = {}

# Word Dictionaries for 4, 5, 6 letter modes
WORDS_4 = [
    "SPIN", "GRID", "FINE", "SHIN", "LOVE", "FIRE", "WIND", "RAIN", "SNOW", "STAR",
    "MOON", "GAME", "PLAY", "TIME", "LIFE", "DARK", "WARM", "COLD", "GOLD", "BLUE",
    "PINK", "ROSE", "LILY", "BIRD", "FISH", "LION", "BEAR", "WOLF", "FROG", "DUCK",
    "BOOK", "PAGE", "WORD", "SONG", "BEAT", "ROCK", "TREE", "LEAF", "WOOD", "DOOR",
    "WALL", "ROOM", "HOME", "CITY", "TOWN", "ROAD", "PATH", "HERO", "KING", "ZOYA",
    "CODE", "CHAT", "FAST", "SLOW", "COOL", "NICE", "GOOD", "LUCK", "MIND", "SOUL",
    "HOPE", "WISH", "TRUE", "FREE", "WAVE", "SAND", "SHIP", "BOAT", "PEAK", "HILL"
]

WORDS_5 = [
    "HEART", "LIGHT", "NIGHT", "DREAM", "SMILE", "LAUGH", "WATER", "EARTH", "MUSIC",
    "DANCE", "SWEET", "HONEY", "MAGIC", "POWER", "TIGER", "PANDA", "APPLE", "MANGO",
    "OCEAN", "RIVER", "CLOUD", "STORM", "PEACE", "ANGEL", "QUEEN", "ROYAL", "BRAVE",
    "SMART", "SHINE", "SPARK", "VIBES", "STORY", "GHOST", "BLAZE", "FAITH", "GRACE",
    "HAPPY", "LUCKY", "SOLAR", "SPACE", "WORLD", "TRACK", "PLANT", "BLOOM", "CANDY"
]

WORDS_6 = [
    "FRIEND", "SPRING", "SUMMER", "WINTER", "FLOWER", "GARDEN", "CASTLE", "DRAGON",
    "KNIGHT", "BEAUTY", "SILENT", "PURPLE", "YELLOW", "ORANGE", "SHADOW", "GOLDEN",
    "SILVER", "MASTER", "WINNER", "PLAYER", "ACTION", "STREAM", "PLANET", "GALAXY",
    "CHANCE", "NATURE", "SPIRIT", "BREEZE", "SUNSET", "FOREST", "ISLAND", "CANDLE"
]

def check_guess_colors(guess: str, secret: str):
    """
    Wordle evaluation logic:
    Green: Correct letter in correct spot
    Orange: Correct letter in wrong spot
    Red: Letter not in word
    """
    n = len(secret)
    result = ["🟥"] * n
    secret_chars = list(secret)
    guess_chars = list(guess)

    # 1. Exact matches (Green)
    for i in range(n):
        if guess_chars[i] == secret_chars[i]:
            result[i] = "🟩"
            secret_chars[i] = None
            guess_chars[i] = None

    # 2. Letter exists elsewhere (Orange)
    for i in range(n):
        if guess_chars[i] is not None and guess_chars[i] in secret_chars:
            result[i] = "🟧"
            secret_chars[secret_chars.index(guess_chars[i])] = None

    return "".join(result)

def format_board(game):
    lines = []
    lines.append("<blockquote><b>WordSeek</b>")
    lines.append(f"<i>{game['size']}-letter mode • {len(game['history'])}/30</i>\n")

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
                f"Koi bhi word nahi dhoondh paya 🥲\n\n"
                f"🎯 <b>Secret Word Tha:</b> <code>{game['secret']}</code></blockquote>"
            )
        except Exception:
            pass

@Client.on_message(filters.command(["new4", "new5", "new6"], prefixes=["/", "."]))
async def start_wordseek(client: Client, message: Message):
    chat_id = message.chat.id
    cmd = message.command[0].lower()

    if chat_id in GAMES:
        remaining = int(GAMES[chat_id]["end_time"] - time.time())
        if remaining > 0:
            await message.reply(
                f"<blockquote>⚠️ Game chal raha hai! Time remaining: <b>{remaining}s</b></blockquote>",
                quote=True
            )
            return

    if cmd == "new4":
        size = 4
        minutes = 5
        secret = random.choice(WORDS_4)
    elif cmd == "new5":
        size = 5
        minutes = 8
        secret = random.choice(WORDS_5)
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
        "max_guesses": 30
    }

    asyncio.create_task(auto_stop_timer(client, chat_id, duration_sec, secret))

    intro_text = (
        f"<blockquote>🎮 <b>WordSeek ({size}-Letter Mode) Started!</b>\n"
        f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"⏱️ <b>Time Limit:</b> {minutes} Minutes\n"
        f"🎯 <b>Length:</b> {size} Letters Word\n\n"
        f"🟩 = Sahi jagah par hai\n"
        f"🟧 = Word mein hai par galat jagah\n"
        f"🟥 = Word mein nahi hai\n\n"
        f"Apna {size}-letter guess bhejo!</blockquote>"
    )
    await message.reply(intro_text)

# Chat listener for WordSeek guesses
@Client.on_message(filters.group & filters.text & ~filters.bot, group=12)
async def wordseek_guess_checker(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id not in GAMES:
        return

    guess = message.text.strip().upper()

    # Commands ya multi-word text ko skip karein
    if guess.startswith(("/", ".", "!", "#")) or len(guess.split()) > 1:
        return

    game = GAMES[chat_id]
    size = game["size"]

    # Agar word game size se match na kare
    if len(guess) != size or not guess.isalpha():
        return

    secret = game["secret"]
    colors = check_guess_colors(guess, secret)

    game["history"].append({
        "word": guess,
        "colors": colors,
        "user": message.from_user.first_name
    })

    board_text = format_board(game)

    # Check WIN
    if guess == secret:
        GAMES.pop(chat_id)
        mention = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
        win_text = (
            f"{board_text}\n\n"
            f"<blockquote>🎉 <b>CONGRATULATIONS!</b>\n"
            f"🏆 {mention} ne sahi word <code>{secret}</code> guess kar liya! 🥳</blockquote>"
        )
        await message.reply(win_text, quote=True)
        return

    # Check MAX GUESSES
    if len(game["history"]) >= game["max_guesses"]:
        GAMES.pop(chat_id)
        lose_text = (
            f"{board_text}\n\n"
            f"<blockquote>⌛ <b>GAME OVER!</b> Guesses khatam ho gaye.\n"
            f"🎯 <b>Correct Word Tha:</b> <code>{secret}</code></blockquote>"
        )
        await message.reply(lose_text, quote=True)
        return

    # Normal Guess Clue Output
    await message.reply(board_text, quote=True)
        
