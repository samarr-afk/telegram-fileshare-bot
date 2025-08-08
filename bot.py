import logging
import os
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

conn = sqlite3.connect("files.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id TEXT,
    file_name TEXT,
    file_size INTEGER,
    share_code TEXT
)""")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a file and I'll give you a download link!")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    file_id = file.file_id
    file_name = file.file_name
    file_size = file.file_size
    share_code = str(abs(hash(file_id)))[:8]

    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("INSERT INTO files (file_id, file_name, file_size, share_code) VALUES (?, ?, ?, ?)",
              (file_id, file_name, file_size, share_code))
    conn.commit()

    await context.bot.send_document(chat_id=CHANNEL_ID, document=file.file_id)
    await update.message.reply_text(f"Here’s your public link: https://yourdomain.com/download/{share_code}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

app.run_polling()
