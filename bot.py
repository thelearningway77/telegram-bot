import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()


# START command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Yeh bot private posts ko secure link ke through bhejta hai.\n"
        "Link open karte hi content milega ⏳"
    )

    # Auto delete after 5 minutes
    await asyncio.sleep(300)
    try:
        await msg.delete()
    except:
        pass


telegram_app.add_handler(CommandHandler("start", start))


@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return "ok"


@app.route("/")
def index():
    return "Bot is running 🚀"


async def main():
    await telegram_app.initialize()
    await telegram_app.start()


if __name__ == "__main__":
    asyncio.run(main())
