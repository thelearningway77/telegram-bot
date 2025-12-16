import os
import asyncio
import uuid
from pyrogram import Client, filters
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

app = Client(
    "postbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

POSTS = {}  # code -> (chat_id, message_id)

# 🔹 Listen posts from private group
@app.on_message(filters.chat(GROUP_ID) & ~filters.service)
async def capture_post(client, message):
    code = uuid.uuid4().hex[:8]
    POSTS[code] = (message.chat.id, message.id)

    link = f"https://t.me/{(await app.get_me()).username}?start={code}"
    print(f"New post captured → {link}")

# 🔹 User opens link
@app.on_message(filters.command("start"))
async def start_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("Invalid link ❌")

    code = message.command[1]
    if code not in POSTS:
        return await message.reply("Link expired or invalid ⛔")

    chat_id, msg_id = POSTS[code]

    sent = await client.copy_message(
        chat_id=message.chat.id,
        from_chat_id=chat_id,
        message_id=msg_id
    )

    await message.reply("⏱️ This message will be deleted in 5 minutes")

    await asyncio.sleep(300)
    await client.delete_messages(message.chat.id, sent.id)

app.run()
