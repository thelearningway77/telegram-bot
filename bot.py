import os
import json
import asyncio
import random
import string
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "posts.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def generate_code(length=6):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        code = context.args[0]
        data = load_data()

        if code not in data:
            await update.message.reply_text("❌ Invalid or expired code.")
            return

        post = data[code]
        msg = await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=post["chat_id"],
            message_id=post["message_id"],
        )

        await update.message.reply_text("⏳ This post will delete in 5 minutes.")

        await asyncio.sleep(300)
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=msg.message_id,
        )
    else:
        await update.message.reply_text(
            "👋 Welcome!\n\n"
            "Click the link you received to view content.\n"
            "Messages auto-delete after 5 minutes ⏳"
        )

async def save_private_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type not in ["group", "supergroup", "channel"]:
        return

    code = generate_code()
    data = load_data()

    data[code] = {
        "chat_id": update.message.chat.id,
        "message_id": update.message.message_id,
    }

    save_data(data)

    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={code}"

    await context.bot.send_message(
        chat_id=update.message.chat.id,
        text=f"🔐 Post link generated:\n\n{link}",
        reply_to_message_id=update.message.message_id,
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, save_private_post))

app.run_polling()
