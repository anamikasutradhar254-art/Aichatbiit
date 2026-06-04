import random
import os
import json

from groq import Groq

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)

# ---------------- CONFIG ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID"))

client = Groq(api_key=GROQ_API_KEY)

# ---------------- FILES ----------------
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

# ---------------- GAME DATA ----------------
word_seek = {}
word_chain = {}

words_4 = ["game", "lion", "tree", "milk"]
words_5 = ["apple", "tiger", "chair", "water"]
words_6 = ["banana", "rocket", "planet", "orange"]

chatbot_status = {}

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chatbot_status[chat_id] = True

    await update.message.reply_text(
        """
💕 Hieeeeee

I'm Ada ✨

🦋 Support Channel:
@jp_network

Use /help To Explore My Features
"""
    )

# ---------------- HELP ----------------
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Games", callback_data="games_menu")]
    ]

    await update.message.reply_text(
        """
📌 Help Menu

/start
/help
/chatbot on
/chatbot off
/stats
/broadcast

🎮 Games available 👇
""",
        reply_markup=InlineKeyboardMarkup(keyboard)
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

    chat_id = update.effective_chat.id

    if not context.args:
        await update.message.reply_text("Use: /chatbot on or off")
        return

    if context.args[0].lower() == "on":
        chatbot_status[chat_id] = True
        await update.message.reply_text("✅ Chatbot ON")

    elif context.args[0].lower() == "off":
        chatbot_status[chat_id] = False
        await update.message.reply_text("❌ Chatbot OFF")

# ---------------- WELCOME ----------------
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        name = f"@{member.username}" if member.username else member.first_name
        await update.message.reply_text(f"👋 Welcome {name}")

# ---------------- STICKER ----------------
async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker = update.message.sticker

    if sticker and sticker.set_name:
        try:
            sset = await context.bot.get_sticker_set(sticker.set_name)
            r = random.choice(sset.stickers)
            await update.message.reply_sticker(r.file_id)
        except:
            pass

# ---------------- WORD SEEK ----------------
async def check_wordseek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.lower()

    if chat_id in word_seek:
        correct = word_seek[chat_id]

        if text == correct:
            await update.message.reply_text("🎉 Correct Answer!")
            del word_seek[chat_id]
        else:
            await update.message.reply_text("❌ Wrong guess!")
        return

    # WORD CHAIN
    if chat_id in word_chain:
        last = word_chain[chat_id]

        if text[0] == last[-1]:
            word_chain[chat_id] = text
            await update.message.reply_text("✅ Correct! Next word...")
        else:
            await update.message.reply_text(f"❌ Word must start with '{last[-1]}'")
        return

    # AI CHAT
    await ai_chat(update, context)

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

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are Ada. Friendly Hindi (English letters). Short replies."
                },
                {"role": "user", "content": update.message.text}
            ]
        )

        await update.message.reply_text(res.choices[0].message.content[:4000])

    except:
        await update.message.reply_text("⚠️ AI busy")

# ---------------- WORD SEEK STARTERS ----------------
async def ws4(update, context):
    chat_id = update.effective_chat.id
    word_seek[chat_id] = random.choice(words_4)
    await update.message.reply_text("🔍 4-Letter Word Seek Started!")

async def ws5(update, context):
    chat_id = update.effective_chat.id
    word_seek[chat_id] = random.choice(words_5)
    await update.message.reply_text("🔍 5-Letter Word Seek Started!")

async def ws6(update, context):
    chat_id = update.effective_chat.id
    word_seek[chat_id] = random.choice(words_6)
    await update.message.reply_text("🔍 6-Letter Word Seek Started!")

# ---------------- WORD CHAIN ----------------
async def word_chain_start(update, context):
    chat_id = update.effective_chat.id
    word_chain[chat_id] = "apple"
    await update.message.reply_text("🔗 Word Chain Started!\nFirst word: apple")

# ---------------- CALLBACK MENU ----------------
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "games_menu":
        keyboard = [
            [InlineKeyboardButton("🔍 Word Seek", callback_data="seek_menu")],
            [InlineKeyboardButton("🔗 Word Chain", callback_data="chain")]
        ]
        await query.edit_message_text("🎮 Games Menu", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "seek_menu":
        keyboard = [
            [InlineKeyboardButton("4 Letter", callback_data="ws4")],
            [InlineKeyboardButton("5 Letter", callback_data="ws5")],
            [InlineKeyboardButton("6 Letter", callback_data="ws6")]
        ]
        await query.edit_message_text("🔍 Select Mode", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "ws4":
        chat_id = query.message.chat_id
        word_seek[chat_id] = random.choice(words_4)
        await query.edit_message_text("🔍 4-Letter Game Started!")

    elif data == "ws5":
        chat_id = query.message.chat_id
        word_seek[chat_id] = random.choice(words_5)
        await query.edit_message_text("🔍 5-Letter Game Started!")

    elif data == "ws6":
        chat_id = query.message.chat_id
        word_seek[chat_id] = random.choice(words_6)
        await query.edit_message_text("🔍 6-Letter Game Started!")

    elif data == "chain":
        chat_id = query.message.chat_id
        word_chain[chat_id] = "apple"
        await query.edit_message_text("🔗 Word Chain Started!\napple")

# ---------------- APP ----------------
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("chatbot", chatbot))

app.add_handler(CommandHandler("ws4", ws4))
app.add_handler(CommandHandler("ws5", ws5))
app.add_handler(CommandHandler("ws6", ws6))
app.add_handler(CommandHandler("chain", word_chain_start))

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.Sticker.ALL, sticker_reply))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_wordseek))

app.add_handler(CallbackQueryHandler(callback_handler))

print("Ada Bot Started...")
app.run_polling()
