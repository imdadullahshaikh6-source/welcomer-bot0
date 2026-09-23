import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# Active games tracking per chat
ACTIVE_GAMES = {}

WORD_LIST = [
    "PYTHON", "TELEGRAM", "BOT", "ZOYA", "MUSIC", "GAMES", 
    "AESTHETIC", "LOVE", "HEART", "FIRE", "MAGIC", "SILENT",
    "CODE", "RAILWAY", "MONGO", "GROUP", "CHAT", "VIBES"
]

@Client.on_message(filters.command(["wordseek", "findword"], prefixes=["/", "."]))
async def wordseek_game(client: Client, message: Message):
    chat_id = message.chat.id
    
    if chat_id in ACTIVE_GAMES and ACTIVE_GAMES[chat_id]:
        await message.reply("<blockquote>⚠️ Ek game pehle se hi is group mein chal raha hai! Pehle use khatam hone dein.</blockquote>", quote=True)
        return

    ACTIVE_GAMES[chat_id] = True
    
    # Random word chunte hain
    target_word = random.choice(WORD_LIST)
    
    # Grid letters generate karte hain (target word + kuch random letters)
    letters = list(target_word)
    while len(letters) < 9:
        letters.append(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    random.shuffle(letters)
    
    # 3x3 grid formatting
    grid_display = f" 🔠  {letters[0]} | {letters[1]} | {letters[2]} \n" \
                   f" 🔠  {letters[3]} | {letters[4]} | {letters[5]} \n" \
                   f" 🔠  {letters[6]} | {letters[7]} | {letters[8]} "

    start_text = (
        "<blockquote>🎮 <b>WORD SEEK GAME STARTED!</b> ✨\n"
        "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"{grid_display}\n\n"
        "🎯 <b>Neeche diye letters ko milakar sahi word dhoondho aur chat mein bhejo!</b>\n"
        "⏱️ <i>Aapke paas 30 seconds hain!</i></blockquote>"
    )

    msg = await message.reply(start_text)

    # 30 seconds ka timer loop
    found_winner = None
    
    # Simple message listener inner function
    @Client.on_message(filters.chat(chat_id) & filters.text & ~filters.bot)
    async def guess_listener(c: Client, m: Message):
        nonlocal found_winner
        if not ACTIVE_GAMES.get(chat_id):
            return
        
        user_guess = m.text.strip().upper()
        if user_guess == target_word and not found_winner:
            found_winner = m.from_user
            ACTIVE_GAMES[chat_id] = False
            try:
                mention = f"<a href='tg://user?id={found_winner.id}'>{found_winner.first_name}</a>"
                await m.reply(f"<blockquote>🎉 <b>BINGO! {mention} ne sahi word dhoond liya!</b>\n\n🎯 <b>Correct Word:</b> <code>{target_word}</code> 🏆</blockquote>", quote=True)
            except Exception:
                pass

    # 30 seconds wait timer
    for _ in range(30):
        if not ACTIVE_GAMES.get(chat_id):
            break
        await asyncio.sleep(1)

    if ACTIVE_GAMES.get(chat_id):
        ACTIVE_GAMES[chat_id] = False
        try:
            await msg.edit_text(
                f"<blockquote>⌛ <b>TIME UP! Kisi ne sahi word nahi dhoondha.</b>\n\n"
                f"🎯 <b>The hidden word was:</b> <code>{target_word}</code></blockquote>"
            )
        except Exception:
            pass
          
