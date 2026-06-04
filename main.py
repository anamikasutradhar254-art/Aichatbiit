import os
import json

from groq import Groq

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID"))

START_PHOTO = "AgACAgUAAxkBAAFLgTpqIYlvQBlttRSHLrZaM4NxLtXenwACxhFrG0TNCFUHf0I03onAOAEAAwIAA3MAAzsE"

client = Groq(api_key=GROQ_API_KEY)

USERS_FILE = "users.json"
GROUPS_FILE = "groups.json"

def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return []

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

users = load_data(USERS_FILE)
groups = load_data(GROUPS_FILE)

chatbot_status = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo="https://picsum.photos/500"
    )

    caption = f"""
💕 Hieeeeee {username}

I'm Ada ✨

Tumhari Friendly Gaming Girl 💖

Mujhse baat karo, masti karo aur gaming discuss karo 🎮

🦋 Support Channel:
@jp_network

Use /help To Explore My Features
"""

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=START_PHOTO,
        caption=caption
    )

    chatbot_status[update.effective_chat.id] = True

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
Available Commands

/start
/help
/chatbot on
/chatbot off
/stats
/broadcast
"""
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    await update.message.reply_text(
        f"👥 Users: {len(users)}\n📢 Groups: {len(groups)}"
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    msg = " ".join(context.args)

    sent = 0

    for uid in users:
        try:
            await context.bot.send_message(uid, msg)
            sent += 1
        except:
            pass

    await update.message.reply_text(
        f"✅ Broadcast Sent\nUsers: {sent}"
    )
async def chatbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/chatbot on\n/chatbot off"
        )
        return

    chat_id = update.effective_chat.id

    if context.args[0].lower() == "on":
        chatbot_status[chat_id] = True
        await update.message.reply_text("✅ Chatbot ON")

    elif context.args[0].lower() == "off":
        chatbot_status[chat_id] = False
        await update.message.reply_text("❌ Chatbot OFF")


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:

        username = (
            f"@{member.username}"
            if member.username
            else member.first_name
        )

        await update.message.reply_text(
            f"👋 Welcome {username}\n"
            f"🆔 User ID: {member.id}"
        )


async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if update.effective_chat.type in ["group", "supergroup"]:

        if chat_id not in groups:
            groups.append(chat_id)
            save_data(GROUPS_FILE, groups)

        if chatbot_status.get(chat_id, True) is False:
            return

    uid = update.effective_user.id

    if uid not in users:
        users.append(uid)
        save_data(USERS_FILE, users)

    user_text = update.message.text

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
You are Ada.

Tum ek friendly gaming girl ho.

Rules:
- Hindi me baat karo.
- English alphabets hi use karo.
- User jaise baat kare waise reply do.
- Short aur natural replies do.
- Real human friend ki tarah behave karo.
- Kabhi fancy fonts use mat karo.
- Gaming pasand hai.
"""
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ]
        )

        reply = response.choices[0].message.content

        await update.message.reply_text(reply[:4000])

    except Exception as e:
        print(f"Groq Error: {e}")

        await update.message.reply_text(
            "⚠️ AI busy hai, thodi der baad try karo."
        )


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("chatbot", chatbot))

app.add_handler(
    MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        welcome
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        ai_chat
    )
)

print("Ada Bot Started...")
app.run_polling()
