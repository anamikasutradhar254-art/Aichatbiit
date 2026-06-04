import random
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


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
💕 Hieeeeee

I'm Ada ✨

🦋 Support Channel:
@jp_network

Use /help To Explore My Features
"""
    )
    chatbot_status[update.effective_chat.id] = True


# ---------------- HELP ----------------
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


# ---------------- STATS ----------------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    await update.message.reply_text(
        f"👥 Users: {len(users)}\n📢 Groups: {len(groups)}"
    )


# ---------------- BROADCAST ----------------
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

    await update.message.reply_text(f"✅ Broadcast Sent\nUsers: {sent}")


# ---------------- CHATBOT ON/OFF ----------------
async def chatbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage:\n/chatbot on\n/chatbot off")
        return

    chat_id = update.effective_chat.id

    if context.args[0].lower() == "on":
        chatbot_status[chat_id] = True
        await update.message.reply_text("✅ Chatbot ON")

    elif context.args[0].lower() == "off":
        chatbot_status[chat_id] = False
        await update.message.reply_text("❌ Chatbot OFF")


# ---------------- WELCOME ----------------
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        username = f"@{member.username}" if member.username else member.first_name

        await update.message.reply_text(
            f"👋 Welcome {username}\n🆔 User ID: {member.id}"
        )


# ---------------- STICKER REPLY ----------------
async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker = update.message.sticker

    if sticker and sticker.set_name:
        try:
            sticker_set = await context.bot.get_sticker_set(sticker.set_name)
            random_sticker = random.choice(sticker_set.stickers)

            await update.message.reply_sticker(random_sticker.file_id)

        except Exception as e:
            print("Sticker Error:", e)


# ---------------- AI CHAT ----------------
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

Rules:
- Sabse friendly tareeke se baat karo.
- Hindi me baat karo lekin English alphabets me.
- Short aur natural replies do.
- User jaise baat kare waise reply do.
- Human friend ki tarah behave karo.
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
        print("Groq Error:", e)
        await update.message.reply_text("⚠️ AI busy hai, thodi der baad try karo.")


# ---------------- APP ----------------
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("chatbot", chatbot))

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.Sticker.ALL, sticker_reply))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

print("Ada Bot Started...")
app.run_polling()
