import random
import os
import json
import time
from collections import defaultdict

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

# ---------------- DATA FILES ----------------
USERS_FILE = "users.json"
GROUPS_FILE = "groups.json"

def load(file):
    if os.path.exists(file):
        return json.load(open(file))
    return []

def save(file, data):
    json.dump(data, open(file, "w"))

users = load(USERS_FILE)
groups = load(GROUPS_FILE)

# ---------------- AI + STATUS ----------------
chatbot_status = {}

# ---------------- GAMES ----------------
word_seek_game = {}
word_chain_game = {}
leaderboard = defaultdict(int)

user_cooldown = {}
daily_reset = time.time()

words_4 = ["game", "lion", "tree", "milk"]
words_5 = ["apple", "tiger", "chair", "water"]
words_6 = ["banana", "rocket", "planet", "orange"]

# ---------------- ANTI SPAM ----------------
def anti_spam(uid):
    now = time.time()
    if uid in user_cooldown:
        if now - user_cooldown[uid] < 2:
            return False
    user_cooldown[uid] = now
    return True

# ---------------- WORDLE ENGINE ----------------
def get_result(secret, guess):
    res = []
    for i in range(len(secret)):
        if guess[i] == secret[i]:
            res.append("🟩")
        elif guess[i] in secret:
            res.append("🟨")
        else:
            res.append("🟥")
    return " ".join(res)

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chatbot_status[chat_id] = True

    await update.message.reply_text(
        "💕 Hieeeeee\n\nI'm Ada ✨\n\nUse /help"
    )

# ---------------- HELP ----------------
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎮 Games", callback_data="games")]]

    await update.message.reply_text(
        "📌 Help Menu",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- STATS ----------------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text(f"👥 Users: {len(users)}\n📢 Groups: {len(groups)}")

# ---------------- BROADCAST ----------------
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    msg = " ".join(context.args)
    sent = 0

    for u in users:
        try:
            await context.bot.send_message(u, msg)
            sent += 1
        except:
            pass

    await update.message.reply_text(f"Sent: {sent}")

# ---------------- CHATBOT ON/OFF ----------------
async def chatbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    chat_id = update.effective_chat.id

    if context.args[0] == "on":
        chatbot_status[chat_id] = True
        await update.message.reply_text("ON")

    elif context.args[0] == "off":
        chatbot_status[chat_id] = False
        await update.message.reply_text("OFF")

# ---------------- WORD SEEK START ----------------
async def ws_start(update, context, mode):
    chat_id = update.effective_chat.id

    words = words_4 if mode == 4 else words_5 if mode == 5 else words_6

    word_seek_game[chat_id] = {
        "word": random.choice(words),
        "history": [],
        "attempts": 0,
        "end": time.time() + 120
    }

    await update.message.reply_text(f"🔍 {mode}-LETTER GAME STARTED")

# ---------------- WORD SEEK CHECK ----------------
async def check_wordseek(update, context):
    chat_id = update.effective_chat.id
    text = update.message.text.lower()
    user = update.effective_user.first_name

    if chat_id in word_seek_game:
        game = word_seek_game[chat_id]

        if time.time() > game["end"]:
            await update.message.reply_text("⏰ Game Over")
            del word_seek_game[chat_id]
            return

        secret = game["word"]

        if len(text) != len(secret):
            return

        game["attempts"] += 1

        result = get_result(secret, text)

        game["history"].append(f"{result} {text.upper()} - {user}")

        if text == secret:
            leaderboard[user] += 3
            await update.message.reply_text(f"🎉 {user} WON!")
            del word_seek_game[chat_id]
            return

        await update.message.reply_text("\n".join(game["history"][-5:]))
        return

    await chain_play(update, context)

# ---------------- WORD CHAIN ----------------
async def chain_start(update, context):
    chat_id = update.effective_chat.id

    word_chain_game[chat_id] = {
        "players": [],
        "turn": 0,
        "word": "apple",
        "scores": {},
        "start": time.time() + 60,
        "active": False
    }

    await update.message.reply_text("🎮 Join within 60 sec (/join)")

# ---------------- JOIN ----------------
async def join_game(update, context):
    chat_id = update.effective_chat.id
    user = update.effective_user.first_name

    if chat_id not in word_chain_game:
        return

    game = word_chain_game[chat_id]

    if user not in game["players"]:
        game["players"].append(user)
        game["scores"][user] = 0
        await update.message.reply_text(f"{user} joined")

# ---------------- CHAIN PLAY ----------------
async def chain_play(update, context):
    chat_id = update.effective_chat.id
    text = update.message.text.lower()
    user = update.effective_user.first_name

    if chat_id not in word_chain_game:
        return

    game = word_chain_game[chat_id]

    if not game["players"]:
        return

    if not game["active"] and time.time() > game["start"]:
        game["active"] = True

    if not game["active"]:
        return

    current = game["players"][game["turn"]]

    if user != current:
        return

    last = game["word"]

    if text[0] != last[-1]:
        await update.message.reply_text("❌ Wrong letter")
        return

    game["word"] = text
    game["scores"][user] += 1
    leaderboard[user] += 1

    game["turn"] = (game["turn"] + 1) % len(game["players"])
    next_user = game["players"][game["turn"]]

    await update.message.reply_text(f"Next: {next_user}")

# ---------------- LEADERBOARD ----------------
async def lb(update, context):
    global leaderboard

    if time.time() - daily_reset > 86400:
        leaderboard.clear()

    data = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)

    text = "🏆 LEADERBOARD\n\n"

    for i, (u, s) in enumerate(data[:10]):
        text += f"{i+1}. {u} - {s}\n"

    await update.message.reply_text(text)

# ---------------- CALLBACK MENU ----------------
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    await q.answer()

    if data == "games":
        keyboard = [
            [InlineKeyboardButton("🔍 Word Seek", callback_data="seek")],
            [InlineKeyboardButton("🔗 Word Chain", callback_data="chain")]
        ]
        await q.edit_message_text("Games", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "seek":
        keyboard = [
            [InlineKeyboardButton("4", callback_data="ws4")],
            [InlineKeyboardButton("5", callback_data="ws5")],
            [InlineKeyboardButton("6", callback_data="ws6")]
        ]
        await q.edit_message_text("Select", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "ws4":
        await ws_start(update, context, 4)
    elif data == "ws5":
        await ws_start(update, context, 5)
    elif data == "ws6":
        await ws_start(update, context, 6)

    elif data == "chain":
        await chain_start(update, context)

# ---------------- AI CHAT ----------------
async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    if update.effective_chat.type in ["group", "supergroup"]:
        if chat_id not in groups:
            groups.append(chat_id)
            save(GROUPS_FILE, groups)

    uid = update.effective_user.id

    if uid not in users:
        users.append(uid)
        save(USERS_FILE, users)

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Friendly Hindi English replies short"},
                {"role": "user", "content": update.message.text}
            ]
        )

        await update.message.reply_text(res.choices[0].message.content[:4000])

    except:
        await update.message.reply_text("AI busy")

# ---------------- APP ----------------
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("chatbot", chatbot))

app.add_handler(CommandHandler("chain", chain_start))
app.add_handler(CommandHandler("join", join_game))
app.add_handler(CommandHandler("lb", lb))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_wordseek))
app.add_handler(CallbackQueryHandler(callback))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai))

print("BOT STARTED 🚀")
app.run_polling()
