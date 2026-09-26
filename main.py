import os
import asyncio
import yt_dlp

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable missing!")


YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch",
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


def get_audio(query):
    with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
        info = ydl.extract_info(query, download=False)

        if "entries" in info:
            info = info["entries"][0]

        return {
            "title": info.get("title", "Unknown"),
            "url": info["url"],
        }


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Welcome to Music Bot!\n\n"
        "Commands:\n"
        "/play <song name> - Search/play a song\n"
        "/stop - Stop music\n"
        "/help - Help"
    )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Song name do.\n\nExample:\n/play Alan Walker Faded"
        )
        return

    query = " ".join(context.args)

    await update.message.reply_text(
        f"🔎 Searching: {query}"
    )

    try:
        song = await asyncio.to_thread(get_audio, query)

        # Telegram bot API alone cannot join a voice chat.
        # This version retrieves the audio information.
        await update.message.reply_text(
            f"🎵 Found:\n\n"
            f"{song['title']}\n\n"
            f"Audio source ready."
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error:\n{e}"
        )


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏹️ Music stopped.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Music Bot Commands\n\n"
        "/start - Start bot\n"
        "/play <song> - Search song\n"
        "/stop - Stop music\n"
        "/help - Show help"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("help", help_command))

    print("🎵 Music Bot Started...")
    app.run_polling()


if name == "main":
    main()