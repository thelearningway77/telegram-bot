import os
import uuid
import asyncio
from pyrogram import Client, filters
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "post_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# In-memory storage (later DB add kar sakte hain)
POSTS = {}  # code -> (chat_id, message_id)

# 🔹 Capture posts from ANY group where bot is ADMIN
@app.on_message(filters.group & ~filters.service)
async def capture_post(client, message):
    try:
        me = await client.get_me()
        member = await client.get_chat_member(message.chat.id, me.id)

        if member.status not in ("administrator", "creator"):
            return

        code = uuid.uuid4().hex[:8]
        POSTS[code] = (message.chat.id, message.id)

        link = f"https://t.me/{me.username}?start={code}"
        print(f"📌 New Post Captured [{message.chat.title}]")
        print(f"🔗 Link: {link}")

    except Exception as e:
        print("Error:", e)


# 🔹 User opens link
@app.on_message(filters.command("start"))
async def start_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Invalid or missing link")

    code = message.command[1]

    if code not in POSTS:
        return await message.reply("⛔ Link expired or invalid")

    chat_id, msg_id = POSTS[code]

    try:
        sent = await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=chat_id,
            message_id=msg_id
        )

        await message.reply("⏱️ This post will be deleted in 5 minutes")

        await asyncio.sleep(300)  # 5 minutes
        await client.delete_messages(message.chat.id, sent.id)

    except Exception as e:
        await message.reply("❌ Unable to send post")
        print("Send Error:", e)


print("🤖 Bot Started...")
app.run()
