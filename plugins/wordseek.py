import time
import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# Active game state per group:
# chat_id: {
#   "grid": [[]],
#   "letters": [],
#   "size": 4,
#   "end_time": timestamp,
#   "scores": {user_id: {"name": str, "points": int}},
#   "found_words": set(),
#   "task": asyncio.Task
# }
GAMES = {}

# Common English dictionary words (3 to 8 letters) jo grid me ban sakte hain
VALID_WORDS = {
    # 3-Letter Words
    "CAT", "DOG", "BAT", "RAT", "SUN", "RUN", "FUN", "WIN", "WAR", "RED",
    "PEN", "PIN", "PAN", "BOX", "BOY", "TOY", "FOX", "FLY", "CRY", "DRY",
    "SKY", "SEA", "TEA", "ICE", "HOT", "HAT", "CAP", "CUP", "MUG", "CAR",
    "BUS", "VAN", "BED", "BAD", "BAG", "BIG", "PIG", "COW", "OWL", "BEE",
    "ANT", "AIR", "ARM", "LEG", "EYE", "EAR", "LIP", "DAY", "WAY", "SAY",
    "MAY", "NOW", "HOW", "WHO", "WHY", "YOU", "OUR", "OUT", "OFF", "FOR",
    "AND", "BUT", "NOT", "YES", "GOD", "MAN", "MEN", "OLD", "NEW", "TOP",
    
    # 4-Letter Words
    "LOVE", "HATE", "FIRE", "WIND", "RAIN", "SNOW", "STAR", "MOON", "GAME",
    "PLAY", "TIME", "LIFE", "DARK", "WARM", "COLD", "GOLD", "BLUE", "PINK",
    "ROSE", "LILY", "BIRD", "FISH", "LION", "BEAR", "WOLF", "FROG", "DUCK",
    "BOOK", "PAGE", "WORD", "SONG", "BEAT", "ROCK", "TREE", "LEAF", "WOOD",
    "DOOR", "WALL", "ROOM", "HOME", "CITY", "TOWN", "ROAD", "PATH", "HERO",
    "KING", "ZOYA", "CODE", "CHAT", "FAST", "SLOW", "COOL", "NICE", "GOOD",
    
    # 5-Letter Words
    "HEART", "LIGHT", "NIGHT", "DREAM", "SMILE", "LAUGH", "WATER", "EARTH",
    "MUSIC", "DANCE", "SWEET", "HONEY", "MAGIC", "POWER", "TIGER", "PANDA",
    "APPLE", "MANGO", "OCEAN", "RIVER", "CLOUD", "STORM", "PEACE", "ANGEL",
    "QUEEN", "ROYAL", "BRAVE", "SMART", "SHINE", "SPARK", "VIBES", "STORY",
    
    # 6+ Letter Words
    "FRIEND", "SPRING", "SUMMER", "WINTER", "FLOWER", "GARDEN", "CASTLE",
    "DRAGON", "KNIGHT", "BEAUTY", "SILENT", "PURPLE", "YELLOW", "ORANGE",
    "SHADOW", "GOLDEN", "SILVER", "MASTER", "WINNER", "PLAYER", "ACTION"
}

# Grid display formatter
def render_grid(matrix):
    lines = []
    for row in matrix:
        lines.append("  " + "   ".join(row))
    return "\n".join(lines)

# Grid ke andar letters check karne ke liye logic
def can_form_from_letters(word, available_letters):
    temp = list(available_letters)
    for ch in word:
        if ch in temp:
            temp.remove(ch)
        else:
            return False
    return True

async def stop_game_after_timer(client: Client, chat_id: int, duration_sec: int):
    await asyncio.sleep(duration_sec)
    if chat_id in GAMES:
        game = GAMES.pop(chat_id)
        scores = game["scores"]
        
        if not scores:
            text = (
                "<blockquote>⌛ <b>WORD SEEK FINISHED!</b>\n"
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                "Koi bhi valid word nahi dhoondh paya! 🥲</blockquote>"
            )
        else:
            sorted_scores = sorted(scores.values(), key=lambda x: x["points"], reverse=True)
            leaderboard = ""
            medals = ["🥇", "🥈", "🥉", "🎖️", "🎖️"]
            for idx, s in enumerate(sorted_scores[:5]):
                medal = medals[idx] if idx < len(medals) else "🎖️"
                leaderboard += f"{medal} <b>{s['name']}</b> — <code>{s['points']} pts</code>\n"
            
            text = (
                "<blockquote>🏆 <b>WORD SEEK ROUND OVER!</b>\n"
                "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
                f"Total Words Found: <b>{len(game['found_words'])}</b>\n\n"
                f"<b>Final Leaderboard:</b>\n{leaderboard}</blockquote>"
            )
        
        try:
            await client.send_message(chat_id, text)
        except Exception:
            pass

@Client.on_message(filters.command(["new4", "new5", "new6"], prefixes=["/", "."]))
async def start_new_game(client: Client, message: Message):
    chat_id = message.chat.id
    cmd = message.command[0].lower()

    if chat_id in GAMES:
        remaining = int(GAMES[chat_id]["end_time"] - time.time())
        if remaining > 0:
            await message.reply(
                f"<blockquote>⚠️ Pehle se ek game chal raha hai!\nBache huye time: <b>{remaining} seconds</b></blockquote>",
                quote=True
            )
            return

    # Size and Time mapping
    if cmd == "new4":
        size = 4
        minutes = 5
    elif cmd == "new5":
        size = 5
        minutes = 8
    else:  # new6
        size = 6
        minutes = 10

    duration_sec = minutes * 60

    # Vowels + Consonants balance taaki words ban sakein
    vowels = "AEIOU" * (size * 2)
    consonants = "BCDFGHJKLMNPQRSTVWXYZ" * (size * 2)
    pool = list(vowels + consonants)
    random.shuffle(pool)

    total_cells = size * size
    letters = [pool.pop() for _ in range(total_cells)]
    
    # 2D Matrix Grid
    matrix = [letters[i * size:(i + 1) * size] for i in range(size)]
    grid_str = render_grid(matrix)

    start_text = (
        f"<blockquote>🎮 <b>WORD SEEK ({size}x{size}) STARTED!</b> ✨\n"
        f"✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"<code>{grid_str}</code>\n\n"
        f"⏱️ <b>Time Limit:</b> {minutes} Minutes\n"
        f"🎯 <b>Rules:</b> Grid me banne wale 3+ letter words chat me bhejte jao!\n"
        f"Har sahi word par points milenge!</blockquote>"
    )

    sent_msg = await message.reply(start_text)

    # Timer Task
    timer_task = asyncio.create_task(stop_game_after_timer(client, chat_id, duration_sec))

    GAMES[chat_id] = {
        "grid": matrix,
        "letters": letters,
        "size": size,
        "end_time": time.time() + duration_sec,
        "scores": {},
        "found_words": set(),
        "task": timer_task
    }

# Global word guess detector for active games
@Client.on_message(filters.group & filters.text & ~filters.bot, group=10)
async def word_guess_checker(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id not in GAMES:
        return

    text = message.text.strip().upper()

    # Commands ya lambi chat ko ignore karein
    if text.startswith(("/", ".", "!", "#")) or len(text.split()) > 1:
        return

    # Sahi format: sirf 3 ya usse zyada letters ka single word
    if len(text) < 3 or not text.isalpha():
        return

    game = GAMES[chat_id]

    # Check agar word pehle dhoondha ja chuka ho
    if text in game["found_words"]:
        return

    # Check agar word valid dictionary me ho aur grid ke letters se banta ho
    if text in VALID_WORDS and can_form_from_letters(text, game["letters"]):
        game["found_words"].add(text)
        user_id = message.from_user.id
        user_name = message.from_user.first_name

        pts = len(text)  # 3 letter = 3 pts, 4 letter = 4 pts...
        if user_id not in game["scores"]:
            game["scores"][user_id] = {"name": user_name, "points": 0}
        game["scores"][user_id]["points"] += pts

        total_pts = game["scores"][user_id]["points"]
        mention = f"<a href='tg://user?id={user_id}'>{user_name}</a>"

        await message.reply(
            f"<blockquote>✨ <b>Bingo!</b> {mention} found <code>{text}</code> (+{pts} pts)\n"
            f"Total: <b>{total_pts} pts</b></blockquote>",
            quote=True
        )
        
