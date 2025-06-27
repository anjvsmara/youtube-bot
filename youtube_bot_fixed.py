
import os
import yt_dlp
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Read from environment variable

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Kirim link YouTube ke saya, lalu pilih format unduhan.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "youtube.com" in text or "youtu.be" in text:
        context.user_data["yt_url"] = text
        keyboard = [
            [InlineKeyboardButton("🎵 Audio", callback_data="audio"),
             InlineKeyboardButton("🎥 Video", callback_data="video")]
        ]
        await update.message.reply_text("Pilih format:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    url = context.user_data.get("yt_url")

    if not url:
        await query.edit_message_text("URL tidak ditemukan. Kirim ulang link YouTube-nya.")
        return

    try:
        folder = "downloads"
        os.makedirs(folder, exist_ok=True)

        if choice == "audio":
            output = f"{folder}/audio.%(ext)s"
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            output = f"{folder}/video.%(ext)s"
            ydl_opts = {
                'format': 'best[ext=mp4]',
                'outtmpl': output
            }

        await query.edit_message_text("⏬ Sedang mendownload...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Kirim file
        for file in os.listdir(folder):
            if file.startswith(choice):
                path = os.path.join(folder, file)
                await query.message.reply_document(document=open(path, "rb"))
                os.remove(path)
                break
        else:
            await query.message.reply_text("Gagal mengirim file.")

    except Exception as e:
        await query.message.reply_text(f"Terjadi error: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()
