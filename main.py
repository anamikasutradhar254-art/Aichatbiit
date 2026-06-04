import os
import json
import google.generativeai as genai

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID"))

START_PHOTO = "AgACAgUAAxkBAAFLgTpqIYlvQBlttRSHLrZaM4NxLtXenwACxhFrG0TNCFUHf0I03onAOAEAAwIAA3MAAzsE"

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="""
You are Ada, a friendly gaming girl chatbot.

Rules:
- Reply like a real human friend.
- Keep replies short.
- Use normal English alphabet only.
- No fancy fonts.
- Be friendly and playful.
"""
)

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
    uid = update.effective_user.id

    if uid not in users:
        users.append(uid)
        save_data(USERS_FILE, users)

    username = (
        f"@{update.effective_user.username}"
        if update.effective_user.username
        else update.effective_user.first_name
    )

    caption = f"""
💕 Hieeeeee {username}

I'm Ada ✨

Your Friendly Gaming And Chatting Girl,
Ready To Talk, Chat And Have Fun With You 💖

🦋 Support Channel:
@jp_network

Use /help To Explore My Features
"""

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=START_PHOTO,
        caption=caption
    )
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
        prompt = f"""
You are Ada.

Reply naturally like a human friend.
Keep replies short.
Use simple language.

User: {user_text}
"""

        response = model.generate_content(prompt)

        await update.message.reply_text(
            response.text[:4000]
        )

    except Exception as e:
        await update.message.reply_text(
            f"Error: {e}"
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

