import os
import random
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw, ImageOps
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

# Bestie aesthetic emojis for fun vibes
FUN_EMOJIS = ["🌸", "🎀", "🧸", "🌷", "✨", "🍓", "🍧", "🍒", "💐", "🤍", "💖", "💘", "💌", "🦋"]

def create_circular_avatar(img: Image.Image, size=(300, 300)) -> Image.Image:
    img = img.resize(size, Image.Resampling.LANCZOS).convert("RGBA")
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output

async def generate_couple_image(client: Client, user1, user2) -> BytesIO:
    bg_width, bg_height = 800, 420
    canvas = Image.new("RGBA", (bg_width, bg_height), (24, 25, 32, 255))
    
    # User 1 PFP
    u1_pfp = None
    try:
        photos1 = [p async for p in client.get_chat_photos(user1.id, limit=1)]
        if photos1:
            f1 = await client.download_media(photos1[0].file_id, in_memory=True)
            u1_pfp = Image.open(f1)
    except Exception:
        pass

    # User 2 PFP
    u2_pfp = None
    try:
        photos2 = [p async for p in client.get_chat_photos(user2.id, limit=1)]
        if photos2:
            f2 = await client.download_media(photos2[0].file_id, in_memory=True)
            u2_pfp = Image.open(f2)
    except Exception:
        pass

    if not u1_pfp:
        u1_pfp = Image.new("RGBA", (300, 300), (255, 105, 180, 255))
    if not u2_pfp:
        u2_pfp = Image.new("RGBA", (300, 300), (138, 43, 226, 255))

    circle1 = create_circular_avatar(u1_pfp, (260, 260))
    circle2 = create_circular_avatar(u2_pfp, (260, 260))

    canvas.paste(circle1, (80, 80), circle1)
    canvas.paste(circle2, (460, 80), circle2)

    # Circle heart highlight background in middle
    draw = ImageDraw.Draw(canvas)
    draw.ellipse((360, 170, 440, 250), fill=(255, 75, 130, 255))

    output = BytesIO()
    output.name = "couple.png"
    canvas.save(output, format="PNG")
    output.seek(0)
    return output

# ==================== .couple / .ship ====================
@Client.on_message(filters.command(["couple", "ship"], prefixes=[".", "/"]) & filters.group)
async def couple_command(client: Client, message: Message):
    chat_id = message.chat.id
    
    msg = await message.reply_text("<blockquote>🌸 <i>Zoya is finding the cutest match for today...</i> 💖</blockquote>", parse_mode=ParseMode.HTML)
    
    members = []
    try:
        async for m in client.get_chat_members(chat_id, limit=80):
            if not m.user.is_bot and not m.user.is_deleted:
                members.append(m.user)
    except Exception:
        pass

    if len(members) < 2:
        return await msg.edit_text("<blockquote>⚠️ Match dhundne ke liye group me kam se kam 2 active members hone chahiye!</blockquote>", parse_mode=ParseMode.HTML)

    user1, user2 = random.sample(members, 2)
    percentage = random.randint(55, 100)
    emoji = random.choice(FUN_EMOJIS)
    
    filled = int(percentage / 10)
    bar = "▰" * filled + "▱" * (10 - filled)

    u1_mention = f"<a href='tg://user?id={user1.id}'>{user1.first_name or 'User'}</a>"
    u2_mention = f"<a href='tg://user?id={user2.id}'>{user2.first_name or 'User'}</a>"

    caption = (
        f"<blockquote>{emoji} <b>𝙏𝙤𝙙𝙖𝙮'𝙨 𝘾𝙤𝙪𝙥𝙡𝙚 𝙈𝙖𝙩𝙘𝙝</b> 💌\n"
        "✦ ━━━━━━━━━━━━━━━━━━ ✦\n"
        f"👑 {u1_mention} <b>+</b> {u2_mention} 👑\n\n"
        f"💖 <b>Compatibility:</b> <code>{percentage}%</code>\n"
        f"✨ <b>Progress:</b> <code>[{bar}]</code>\n\n"
        "🎀 <i>Rab ne bana di jodi! Happy shipping!</i> 🍓</blockquote>"
    )

    try:
        photo = await generate_couple_image(client, user1, user2)
        await message.reply_photo(photo=photo, caption=caption, parse_mode=ParseMode.HTML)
        await msg.delete()
    except Exception:
        await msg.edit_text(caption, parse_mode=ParseMode.HTML)

# ==================== Mini Games ====================
@Client.on_message(filters.command(["dice"], prefixes=[".", "/"]) & filters.group)
async def dice_game(client: Client, message: Message):
    sent = await client.send_dice(message.chat.id, emoji="🎲")
    await asyncio.sleep(3)
    val = sent.dice.value
    await sent.reply_text(f"<blockquote>🎲 <b>Dice Roll Result:</b> <code>{val}/6</code> ✨</blockquote>", parse_mode=ParseMode.HTML)

@Client.on_message(filters.command(["dart"], prefixes=[".", "/"]) & filters.group)
async def dart_game(client: Client, message: Message):
    sent = await client.send_dice(message.chat.id, emoji="🎯")
    await asyncio.sleep(3)
    val = sent.dice.value
    status = "Bullseye! 🎯🔥" if val == 6 else f"Score: {val}/6"
    await sent.reply_text(f"<blockquote>🎯 <b>Dart Result:</b> <code>{status}</code></blockquote>", parse_mode=ParseMode.HTML)

@Client.on_message(filters.command(["basket", "ball"], prefixes=[".", "/"]) & filters.group)
async def basket_game(client: Client, message: Message):
    sent = await client.send_dice(message.chat.id, emoji="🏀")
    await asyncio.sleep(3)
    val = sent.dice.value
    status = "Basket Goal!! 🏀🔥" if val in [4, 5] else "Missed! 🙈"
    await sent.reply_text(f"<blockquote>🏀 <b>Basket Result:</b> <code>{status}</code></blockquote>", parse_mode=ParseMode.HTML)

@Client.on_message(filters.command(["football", "goal"], prefixes=[".", "/"]) & filters.group)
async def football_game(client: Client, message: Message):
    sent = await client.send_dice(message.chat.id, emoji="⚽")
    await asyncio.sleep(3)
    val = sent.dice.value
    status = "GOALLL!! ⚽🔥" if val in [3, 4, 5] else "Defended / Missed! 🧤"
    await sent.reply_text(f"<blockquote>⚽ <b>Football Result:</b> <code>{status}</code></blockquote>", parse_mode=ParseMode.HTML)

@Client.on_message(filters.command(["slot", "jackpot"], prefixes=[".", "/"]) & filters.group)
async def slot_game(client: Client, message: Message):
    sent = await client.send_dice(message.chat.id, emoji="🎰")
    await asyncio.sleep(3)
    val = sent.dice.value
    status = "JACKPOT 777!! 🥳🎉" if val == 64 else f"Spin Score: {val}"
    await sent.reply_text(f"<blockquote>🎰 <b>Slot Machine:</b> <code>{status}</code> ✨</blockquote>", parse_mode=ParseMode.HTML)
    
