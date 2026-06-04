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

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

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

    await update.message.reply_text(
        "🤖 Gemini AI Bot Online!"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    await update.message.reply_text(
        f"👥 Users: {len(users)}\n"
        f"📢 Groups: {len(groups)}"
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

        username = member.username
        if username:
            username = "@" + username
        else:
            username = member.first_name

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
        response = model.generate_content(user_text)

        await update.message.reply_text(
            response.text[:4000]
        )

    except Exception as e:
        await update.message.reply_text(
            f"Error: {e}"
        )

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
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

print("Bot Started...")
app.run_polling()
