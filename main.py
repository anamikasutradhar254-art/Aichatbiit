import random
import os
import json
import html

from groq import Groq

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

client = Groq(api_key=GROQ_API_KEY)

USERS_FILE = "users.json"
GROUPS_FILE = "groups.json"
ACTIVE_FILE = "active_members.json"

COUPLE_PHOTOS = [
    "https://kommodo.ai/i/R9KpGrTzkFsw73ZbdeqV",
    "https://kommodo.ai/i/R9KpGrTzkFsw73ZbdeqV"
]

GIFS = {
    "slap": "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
    "kiss": "https://media.giphy.com/media/bGm9FuBCGg4SY/giphy.gif",
    "hug": "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
    "pat": "https://media.giphy.com/media/ARSp9T7wwxNcs/giphy.gif",
    "bite": "https://media.giphy.com/media/1Bgr0VaRnx3pCZbaJa/giphy.gif",
    "punch": "https://media.giphy.com/media/l1J3G5lf06vi58EIE/giphy.gif",
    "kill": "https://media.giphy.com/media/3ohhwfAa9rbXaZe86c/giphy.gif",
    "dance": "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    "cry": "https://media.giphy.com/media/OPU6wzx8JrHna/giphy.gif"
}


def load_data(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default


def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


users = load_data(USERS_FILE, [])
groups = load_data(GROUPS_FILE, [])
active_members = load_data(ACTIVE_FILE, {})
chatbot_status = {}


def get_name(user):
    return user.first_name or "User"


def mention_user(user):
    return f'<a href="tg://user?id={user.id}">{html.escape(user.first_name or "User")}</a>'


def mention_member(member):
    return f'<a href="tg://user?id={member["id"]}">{html.escape(member["name"])}</a>'


def track_active(update: Update):
    if not update.effective_user or not update.effective_chat:
        return

    chat = update.effective_chat
    user = update.effective_user

    uid = user.id
    if uid not in users:
        users.append(uid)
        save_data(USERS_FILE, users)

    if chat.type not in ["group", "supergroup"]:
        return

    if chat.id not in groups:
        groups.append(chat.id)
        save_data(GROUPS_FILE, groups)

    chat_id = str(chat.id)

    if chat_id not in active_members:
        active_members[chat_id] = []

    active_members[chat_id] = [
        m for m in active_members[chat_id]
        if m["id"] != user.id
    ]

    active_members[chat_id].append({
        "id": user.id,
        "name": get_name(user)
    })

    save_data(ACTIVE_FILE, active_members)


def get_random_member(chat_id, exclude_id=None):
    members = active_members.get(str(chat_id), [])
    if exclude_id:
        members = [m for m in members if m["id"] != exclude_id]
    if not members:
        return None
    return random.choice(members)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)

    await update.message.reply_text(
        """💕 Hieeeeee

I'm Ada ✨

🦋 Support Channel:
@jp_network

Use /help To Explore My Features"""
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """Available Commands

/start
/help
/chatbot on
/chatbot off
/stats
/broadcast message
/tagall message

Fun Commands:
/couples
/crush
/brain
/love

Reply Fun:
/slap
/kiss
/hug
/pat
/bite
/punch
/kill
/dance
/cry"""
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
    if not msg:
        await update.message.reply_text("Usage: /broadcast message")
        return

    sent_users = 0
    sent_groups = 0

    for uid in users:
        try:
            await context.bot.send_message(uid, msg)
            sent_users += 1
        except:
            pass

    for gid in groups:
        try:
            await context.bot.send_message(gid, msg)
            sent_groups += 1
        except:
            pass

    await update.message.reply_text(
        f"✅ Broadcast Sent\nUsers: {sent_users}\nGroups: {sent_groups}"
    )


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


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        mention = f'<a href="tg://user?id={member.id}">{html.escape(member.first_name or "User")}</a>'

        if member.id == context.bot.id:
            await update.message.reply_text(
                "💕 Thanks for adding me!\n\nUse /help to explore my features ✨"
            )
        else:
            await update.message.reply_text(
                f"""🎉 Wᴇʟᴄᴏᴍᴇ Tᴏ Tʜᴇ Gʀᴏᴜᴘ 🎉

{mention}

🆔 ID: <code>{member.id}</code>

Hᴀᴠᴇ Fᴜɴ Aɴᴅ Eɴᴊᴏʏ ✨""",
                parse_mode=ParseMode.HTML
            )


async def tagall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)

    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Ye command sirf group me chalega.")
        return

    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ["administrator", "creator"]:
            await update.message.reply_text("❌ Sirf group admin /tagall use kar sakta hai.")
            return
    except:
        return

    msg = " ".join(context.args) or "Attention everyone!"
    members = active_members.get(str(chat.id), [])

    if not members:
        await update.message.reply_text("❌ Active members nahi mile.")
        return

    text = f"🦋 {html.escape(msg)}\n\n"

    for i, m in enumerate(members, 1):
        text += mention_member(m) + " "

        if i % 5 == 0:
            text += "\n"

        if len(text) > 3500:
            await context.bot.send_message(
                chat_id=chat.id,
                text=text,
                parse_mode=ParseMode.HTML
            )
            text = ""

    if text:
        await context.bot.send_message(
            chat_id=chat.id,
            text=text,
            parse_mode=ParseMode.HTML
        )


async def couples(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)

    chat_id = update.effective_chat.id
    members = active_members.get(str(chat_id), [])

    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Ye command group me use karo.")
        return

    if len(members) < 2:
        await update.message.reply_text("❌ Active members kam hai. Group me thoda chat karo.")
        return

    user1, user2 = random.sample(members, 2)

    caption = f"""❤️ TODAY'S CUTE COUPLE ❤️

{mention_member(user1)} 🔥 💞 {mention_member(user2)}

LOVE IS IN THE AIR ❤️

~ FROM ADA WITH LOVE 💋"""

    try:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=random.choice(COUPLE_PHOTOS),
            caption=caption,
            parse_mode=ParseMode.HTML
        )
    except:
        await update.message.reply_text(caption, parse_mode=ParseMode.HTML)


async def crush(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)

    user = update.effective_user
    crush_user = get_random_member(update.effective_chat.id, exclude_id=user.id)

    if not crush_user:
        await update.message.reply_text("❌ Active members kam hai.")
        return

    percent = random.randint(1, 100)

    await update.message.reply_text(
        f"💘 {mention_user(user)}'s Sᴇᴄʀᴇᴛ Cʀᴜꜱʜ Iꜱ - {mention_member(crush_user)}\n\n"
        f"Crush level: {percent}% ❤️",
        parse_mode=ParseMode.HTML
    )


async def brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)

    iq = random.randint(1, 100)

    await update.message.reply_text(
        f"🧠 IQ Lᴇᴠᴇʟ Oꜰ {mention_user(update.effective_user)} Iꜱ {iq}% 😎",
        parse_mode=ParseMode.HTML
    )


async def love(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)

    members = active_members.get(str(update.effective_chat.id), [])

    if len(members) < 2:
        await update.message.reply_text("❌ Active members kam hai.")
        return

    user1, user2 = random.sample(members, 2)
    percent = random.randint(1, 100)

    await update.message.reply_text(
        f"""❤️ Lᴏᴠᴇ Mᴇᴛᴇʀ Rᴇᴘᴏʀᴛ ❤️

{mention_member(user1)} ❤️ {mention_member(user2)}

Lᴏᴠᴇ Cᴏᴍᴘᴀᴛɪʙɪʟɪᴛʏ: {percent}% ❤️""",
        parse_mode=ParseMode.HTML
    )


async def action_command(update: Update, context: ContextTypes.DEFAULT_TYPE, action):
    track_active(update)

    if not update.message.reply_to_message:
        await update.message.reply_text(f"Kisi ke message ko reply karke /{action} do.")
        return

    sender = mention_user(update.effective_user)
    target = mention_user(update.message.reply_to_message.from_user)

    text_map = {
        "slap": f"{sender} slapped {target} 👋",
        "kiss": f"{sender} kissed {target} 😘",
        "hug": f"{sender} hugged {target} 🤗",
        "pat": f"{sender} patted {target} 🥰",
        "bite": f"{sender} bit {target} 😈",
        "punch": f"{sender} punched {target} 👊",
        "kill": f"{sender} killed {target} ☠️",
        "dance": f"{sender} danced with {target} 💃",
        "cry": f"{sender} is crying for {target} 😭"
    }

    caption = text_map[action]

    try:
        await context.bot.send_animation(
            chat_id=update.effective_chat.id,
            animation=GIFS[action],
            caption=caption,
            parse_mode=ParseMode.HTML
        )
    except:
        await update.message.reply_text(caption, parse_mode=ParseMode.HTML)


async def slap(update, context): await action_command(update, context, "slap")
async def kiss(update, context): await action_command(update, context, "kiss")
async def hug(update, context): await action_command(update, context, "hug")
async def pat(update, context): await action_command(update, context, "pat")
async def bite(update, context): await action_command(update, context, "bite")
async def punch(update, context): await action_command(update, context, "punch")
async def kill(update, context): await action_command(update, context, "kill")
async def dance(update, context): await action_command(update, context, "dance")
async def cry(update, context): await action_command(update, context, "cry")


async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)

    sticker = update.message.sticker

    if sticker and sticker.set_name:
        try:
            sticker_set = await context.bot.get_sticker_set(sticker.set_name)
            random_sticker = random.choice(sticker_set.stickers)
            await update.message.reply_sticker(random_sticker.file_id)
        except Exception as e:
            print("Sticker Error:", e)


async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)

    chat_id = update.effective_chat.id

    if update.effective_chat.type in ["group", "supergroup"]:
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


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("chatbot", chatbot))
app.add_handler(CommandHandler(["tagall", "Tagall"], tagall))

app.add_handler(CommandHandler("couples", couples))
app.add_handler(CommandHandler("crush", crush))
app.add_handler(CommandHandler("brain", brain))
app.add_handler(CommandHandler("love", love))

app.add_handler(CommandHandler("slap", slap))
app.add_handler(CommandHandler("kiss", kiss))
app.add_handler(CommandHandler("hug", hug))
app.add_handler(CommandHandler("pat", pat))
app.add_handler(CommandHandler("bite", bite))
app.add_handler(CommandHandler("punch", punch))
app.add_handler(CommandHandler("kill", kill))
app.add_handler(CommandHandler("dance", dance))
app.add_handler(CommandHandler("cry", cry))

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.Sticker.ALL, sticker_reply))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

print("Ada Bot Started...")
app.run_polling()
