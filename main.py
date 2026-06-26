import random
import os
import json
import html
import asyncio

from groq import Groq

from telegram import (
    Update,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env variable missing")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

USERS_FILE = "users.json"
GROUPS_FILE = "groups.json"
ACTIVE_FILE = "active_members.json"
GAME_BAN_FILE = "connect_game_banned.json"
CONNECT_LB_FILE = "connect_leaderboard.json"

START_PHOTO = "https://cdn.phototourl.com/free/2026-06-26-1603715b-e554-4bd0-bf1d-b02cc52201ce.jpg"
HELP_PHOTO = START_PHOTO
FORCE_CHANNEL = "@jp_network"
SUPPORT_LINK = "https://t.me/jp_network"

JOIN_TIME = 30
MAX_LEVELS = 10

COUPLE_PHOTOS = [
    "https://kommodo.ai/i/zxgdh45YyX2vk9HaNBlE",
    "https://kommodo.ai/i/bBggBx9cyGNz2iEBkaSg"
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

CHAIN_WORDS = [
    ["foot","print","photo","album","cover","up","group"],
    ["rain","bow","tie","knot","hole","dark","room"],
    ["table","tennis","ball","room","mate","ship","yard"],
    ["book","mark","market","place","holder","cup","cake"],
    ["phone","call","center","stage","coach","class","room"],
    ["fire","wall","paper","boat","race","track","suit"],
    ["school","bus","stop","watch","tower","clock","work"],
    ["gold","fish","tank","top","hat","trick","shot"],
    ["light","house","boat","deck","chair","lift","off"],
    ["chain","link","battle","field","trip","wire","less"],
    ["game","over","time","keeper","bell","boy","friend"],
    ["note","book","worm","wood","pecker","head","phone"],
    ["road","map","quest","ion","mark","down","load"],
    ["file","name","plate","glass","door","bell","ring"],
    ["heart","beat","boxer","ring","tone","down","fall"],
    ["side","walk","way","back","pack","age","old"],
    ["red","hand","shake","down","load","speed","boat"],
    ["answer","key","board","game","night","mare","land"],
    ["screen","shot","gun","powder","room","temperature","scale"],
    ["leader","board","exam","paper","plane","ticket","counter"],
    ["team","work","flow","chart","paper","clip","board"],
    ["master","key","hole","cover","story","line","dance"],
    ["floor","plan","earth","worm","hole","card","game"],
    ["power","bank","note","pad","lock","down","hill"],
    ["test","match","stick","figure","head","light","bulb"],
    ["idea","box","office","work","space","ship","yard"],
    ["cut","scene","shot","clock","wise","guy","line"],
    ["date","base","ball","park","ing","lottery","ticket"],
    ["shop","cart","wheel","chair","person","album","cover"],
    ["page","number","plate","form","fill","in","side"],
    ["kick","start","menu","card","holder","name","tag"],
    ["support","channel","join","button","click","help","menu"],
    ["chat","bot","user","group","admin","ban","mute"],
    ["love","meter","report","card","game","score","board"],
    ["crush","level","brain","test","case","study","group"],
    ["dance","floor","show","case","closed","door","handle"],
    ["car","wash","room","service","charge","sheet","metal"],
    ["gear","box","office","party","animal","farm","house"],
    ["mirror","image","search","engine","room","mate","choice"],
    ["pass","word","game","play","station","master","piece"],
    ["work","shop","keeper","key","chain","link","battle"],
    ["weight","loss","leader","board","top","soil","test"],
    ["strike","rate","card","holder","cup","cake","walk"],
    ["talk","show","case","study","guide","line","up"],
    ["up","date","base","camp","fire","fly","paper"],
    ["paper","back","cover","page","view","point","blank"],
    ["blank","space","bar","code","red","alert","box"],
    ["black","board","room","light","year","book","club"],
    ["club","house","party","time","table","cloth","line"],
    ["water","fall","out","side","kick","box","ing"],
    ["dream","land","lord","ship","wreck","age","group"],
    ["frame","work","load","balancer","beam","light","house"],
    ["friend","ship","shape","shift","key","note","book"],
    ["battle","field","work","force","field","trip","wire"],
    ["charge","back","bone","fire","wall","paper","weight"],
    ["plane","ticket","counter","strike","rate","card","holder"],
    ["paper","boat","race","track","suit","case","closed"],
    ["wood","pecker","head","phone","call","center","stage"],
    ["clock","work","place","mat","match","box","office"],
    ["kind","heart","beat","boxer","ring","tone","down"],
    ["way","back","pack","age","old","gold","fish"],
    ["hat","trick","shot","gun","fire","fly","paper"],
    ["tennis","ball","room","mate","date","line","up"],
    ["down","town","hall","mark","sheet","music","note"],
    ["life","guard","rail","road","map","quest","ion"],
    ["market","place","holder","cup","cake","walk","talk"],
    ["service","station","master","piece","work","shop","keeper"],
    ["short","cut","off","line","man","power","bank"],
    ["match","stick","figure","head","phone","call","center"],
    ["sale","point","blank","space","bar","code","red"],
    ["hand","shake","down","load","speed","boat","man"],
    ["law","book","mark","market","place","matter","rain"],
    ["bow","tie","knot","hole","punch","bag","pack"],
    ["rat","race","car","petrol","pump","king","pin"],
    ["drop","box","ing","day","dream","land","lord"],
    ["photo","frame","work","load","beam","light","year"],
    ["bell","boy","friend","ship","shape","shift","key"],
    ["cover","story","line","dance","floor","plan","earth"],
    ["pad","lock","screen","shot","gun","powder","room"],
    ["model","answer","key","chain","link","battle","field"],
    ["wire","less","charge","back","bone","fire","wall"],
    ["exam","paper","plane","ticket","counter","strike","rate"],
    ["name","tag","team","work","flow","chart","paper"],
    ["door","bell","ring","master","key","note","book"],
    ["light","bulb","idea","box","office","work","space"],
    ["stick","man","power","cut","scene","shot","clock"],
    ["wise","guy","line","up","date","base","ball"],
    ["cart","wheel","chair","person","album","cover","page"],
    ["glass","door","handle","bar","soap","box","office"],
    ["deck","chair","lift","off","road","side","mirror"],
    ["search","engine","room","service","charge","sheet","metal"],
    ["choice","board","exam","hall","pass","word","game"],
    ["night","mare","land","mark","spot","light","weight"],
    ["lifting","belt","line","control","room","chat","bot"],
    ["telegram","group","help","command","list","button","support"],
    ["owner","profile","link","join","verify","start","photo"],
    ["message","reply","fun","slap","kiss","hug","pat"],
    ["bite","punch","kill","dance","cry","gif","caption"],
    ["couple","photo","love","air","meter","report","score"],
    ["active","member","tag","all","broadcast","stats","owner"],
    ["mute","user","permission","admin","group","help","bot"],
    ["connect","win","chain","word","battle","level","winner"],
    ["join","time","player","score","point","leader","board"],
    ["correct","answer","first","win","game","over","score"],
    ["random","chain","blank","word","guess","level","next"],
    ["support","chat","channel","button","verify","force","join"],
]


OPPOSITE_PAIRS = [
    ("good", "bad"),
    ("hot", "cold"),
    ("big", "small"),
    ("up", "down"),
    ("open", "shut"),
    ("day", "night"),
    ("rich", "poor"),
    ("fast", "slow"),
    ("new", "old"),
    ("yes", "no"),
    ("true", "false"),
    ("high", "low"),
    ("near", "far"),
    ("left", "right"),
    ("in", "out"),
    ("top", "bottom"),
    ("full", "empty"),
    ("wet", "dry"),
    ("hard", "soft"),
    ("clean", "dirty"),
    ("long", "short"),
    ("light", "dark"),
    ("weak", "strong"),
    ("black", "white"),
    ("sweet", "bitter"),
    ("happy", "sad"),
    ("brave", "fear"),
    ("kind", "cruel"),
    ("safe", "risk"),
    ("loud", "quiet"),
    ("fresh", "stale"),
    ("real", "fake"),
    ("same", "other"),
    ("alive", "dead"),
    ("awake", "sleep"),
    ("start", "end"),
    ("come", "go"),
    ("front", "back"),
    ("early", "late"),
    ("easy", "hard"),
    ("right", "wrong"),
    ("calm", "angry"),
    ("sharp", "blunt"),
    ("cheap", "dear"),
    ("rare", "common"),
    ("clear", "cloudy"),
    ("polite", "rude"),
    ("pure", "impure"),
    ("known", "unknown"),
    ("upper", "lower"),
    ("inner", "outer"),
    ("fair", "unfair"),
    ("lucky", "unlucky"),
    ("useful", "useless"),
    ("first", "last"),
    ("past", "future"),
    ("north", "south"),
    ("east", "west"),
    ("single", "double"),
    ("even", "odd"),
    ("raw", "cooked"),
    ("host", "guest"),
    ("win", "lose"),
    ("buy", "sell"),
    ("give", "take"),
    ("send", "get"),
    ("sit", "stand"),
    ("push", "pull"),
    ("hide", "show"),
    ("add", "remove"),
    ("ask", "answer"),
    ("break", "fix"),
    ("cry", "laugh"),
    ("fail", "pass"),
    ("love", "hate"),
    ("lock", "unlock"),
    ("rise", "fall"),
    ("float", "sink"),
    ("trust", "doubt"),
    ("save", "spend"),
    ("more", "less"),
    ("all", "none"),
    ("many", "few"),
    ("on", "off"),
    ("male", "female"),
    ("boy", "girl"),
    ("man", "woman"),
    ("king", "queen"),
    ("sun", "moon"),
    ("life", "death"),
    ("truth", "lie"),
    ("peace", "war"),
    ("smile", "frown"),
    ("entry", "exit"),
    ("enable", "disable"),
    ("create", "delete"),
    ("join", "leave"),
    ("mix", "split"),
    ("grow", "shrink"),
    ("permit", "ban"),
    ("always", "never"),
    ("profit", "loss"),
    ("credit", "debit"),
    ("import", "export"),
    ("online", "offline"),
    ("login", "logout"),
    ("major", "minor"),
    ("plus", "minus"),
    ("smart", "dumb"),
    ("wise", "fool"),
    ("proud", "humble"),
    ("loose", "tight"),
    ("hungry", "full"),
    ("tall", "short"),
    ("fat", "thin"),
    ("messy", "clean"),
    ("rough", "smooth"),
    ("warm", "cool"),
    ("free", "busy"),
    ("noisy", "silent"),
    ("solid", "liquid"),
    ("gas", "solid"),
    ("city", "rural"),
    ("land", "water"),
    ("fire", "water"),
    ("heaven", "hell"),
    ("spring", "autumn"),
    ("summer", "winter"),
    ("morning", "night"),
    ("inside", "outside"),
    ("above", "below"),
    ("accept", "reject"),
    ("allow", "deny"),
    ("attack", "defend"),
    ("borrow", "lend"),
    ("catch", "throw"),
    ("enter", "exit"),
    ("forget", "remember"),
    ("raise", "lower"),
    ("teach", "learn"),
    ("tie", "untie"),
    ("visible", "hidden"),
    ("victory", "defeat"),
    ("friend", "enemy"),
    ("hero", "villain"),
    ("leader", "follower"),
    ("parent", "child"),
    ("doctor", "patient"),
    ("driver", "passenger"),
    ("owner", "tenant"),
    ("admin", "member"),
    ("public", "secret"),
    ("manual", "auto"),
    ("analog", "digital"),
    ("original", "copy"),
    ("empty", "filled"),
    ("normal", "odd"),
    ("quick", "slow"),
    ("bright", "dim"),
    ("thin", "thick"),
    ("wide", "narrow"),
    ("deep", "shallow"),
    ("tiny", "huge"),
    ("huge", "tiny"),
    ("closed", "open"),
    ("floor", "roof"),
    ("floor", "ceil"),
    ("question", "answer"),
    ("input", "output"),
    ("seller", "buyer"),
    ("gold", "silver")
]

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
game_banned = load_data(GAME_BAN_FILE, {})
connect_leaderboard = load_data(CONNECT_LB_FILE, {})
chatbot_status = {}
connect_games = {}

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
    if user.id not in users:
        users.append(user.id)
        save_data(USERS_FILE, users)
    if chat.type not in ["group", "supergroup"]:
        return
    if chat.id not in groups:
        groups.append(chat.id)
        save_data(GROUPS_FILE, groups)
    cid = str(chat.id)
    active_members.setdefault(cid, [])
    active_members[cid] = [m for m in active_members[cid] if m["id"] != user.id]
    active_members[cid].append({"id": user.id, "name": get_name(user)})
    save_data(ACTIVE_FILE, active_members)

def get_random_member(chat_id, exclude_id=None):
    members = active_members.get(str(chat_id), [])
    if exclude_id:
        members = [m for m in members if m["id"] != exclude_id]
    return random.choice(members) if members else None

async def is_admin_or_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        return True
    if update.effective_chat.type not in ["group", "supergroup"]:
        return False
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return member.status in ["administrator", "creator"]
    except:
        return False

async def is_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(FORCE_CHANNEL, update.effective_user.id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ!", url=SUPPORT_LINK),
            InlineKeyboardButton("ᴏᴡɴᴇʀ!", url=f"tg://user?id={OWNER_ID}")
        ],
        [InlineKeyboardButton("✅ ᴠᴇʀɪꜰʏ", callback_data="verify_join")]
    ])
    caption = """💕 Hieeeeee

ɪ'ᴍ ᴀᴅᴀ ✨
ɪ ʜᴀᴠᴇ ᴀ ʟᴏᴛ ᴏꜰ ꜰᴇᴀᴛᴜʀᴇꜱ ɪɴ ᴛʜɪꜱ ʙᴏᴛ ꜱᴏ
ᴜꜱᴇ /help ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴍʏ ꜰᴇᴀᴛᴜʀᴇꜱ ....!

ꜰɪʀꜱᴛ ᴊᴏɪɴ ꜱᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ ᴛʜᴇɴ ᴠᴇʀɪꜰʏ ✅"""
    await update.message.reply_photo(photo=START_PHOTO, caption=caption, reply_markup=keyboard)

async def verify_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_joined(update, context):
        await query.message.reply_text("✅ ᴠᴇʀɪꜰɪᴇᴅ!\n\nɴᴏᴡ ᴜꜱᴇ /help ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴍʏ ꜰᴇᴀᴛᴜʀᴇꜱ ✨")
    else:
        await query.message.reply_text("❌ ᴘᴇʜʟᴇ ꜱᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ ᴊᴏɪɴ ᴋᴀʀᴏ.\n\n@jp_network")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴄʜᴀᴛʙᴏᴛ", callback_data="help_chatbot"), InlineKeyboardButton("ꜰᴜɴ", callback_data="help_fun")],
        [InlineKeyboardButton("ʀᴇᴘʟʏ ꜰᴜɴ", callback_data="help_replyfun"), InlineKeyboardButton("ᴄᴏɴɴᴇᴄᴛᴡɪɴ", callback_data="help_game")],
        [InlineKeyboardButton("ɢʀᴏᴜᴘ ʜᴇʟᴘ", callback_data="help_group"), InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ!", url=SUPPORT_LINK)]
    ])
    caption = """Cʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ. Iғ ʏᴏᴜ'ʀᴇ ғᴀᴄɪɴɢ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ ʏᴏᴜ ᴄᴀɴ ᴀsᴋ ɪɴ sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ.

Aʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ: /"""
    await update.message.reply_photo(photo=HELP_PHOTO, caption=caption, reply_markup=keyboard)

async def help_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texts = {
        "help_chatbot": """🤖 ᴄʜᴀᴛʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs

/start
/help
/chatbot on
/chatbot off
/stats
/broadcast message
/tagall message""",
        "help_fun": """💕 ꜰᴜɴ ᴄᴏᴍᴍᴀɴᴅs

/couples
/crush
/brain
/love""",
        "help_replyfun": """🎭 ʀᴇᴘʟʏ ꜰᴜɴ ᴄᴏᴍᴍᴀɴᴅs

/slap
/kiss
/hug
/pat
/bite
/punch
/kill
/dance
/cry

Kisi user ke message ko reply karke command use karo.""",
        "help_game": """🔗 ᴏᴘᴘᴏꜱɪᴛᴇ ᴄʜᴀɪɴ ɢᴀᴍᴇ

/startconnectwin
/join
/startchaingame
/chaingamehelp
/endconnectwin
/cleaderboard
/Baningame reply
/Unbaningame reply

Minimum 2 players
/startchaingame se start
Opposite word likhna hai
Correct +1 | Run out -1
Time 45 sec se start, minimum 10 sec
Admin/Owner /endconnectwin se game end kar sakte hai""",
        "help_group": """🛡 ɢʀᴏᴜᴘ ʜᴇʟᴘ ᴄᴏᴍᴍᴀɴᴅs

/ban reply
/unban reply
/mute reply
/unmute reply

Bot ko admin banana zaroori hai."""
    }
    await query.message.reply_text(texts.get(query.data, "❌ No help found."))

async def chaingamehelp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🔗 ᴏᴘᴘᴏꜱɪᴛᴇ ᴄʜᴀɪɴ ɢᴀᴍᴇ ʜᴇʟᴘ

/startconnectwin - game room banao
/join - game me join karo
/startchaingame - admin/owner game start
/endconnectwin - admin/owner game end
/cleaderboard - group leaderboard

🎮 ɢᴀᴍᴇ ᴋᴀɪꜱᴇ ᴋʜᴇʟɴᴀ ʜᴀɪ?

1. /startconnectwin bhejo.
2. Players /join bhej kar game me aayenge.
3. Minimum 2 players chahiye.
4. Admin/Owner /startchaingame dega.
5. Bot random player ko mention karega.
6. Bot ek word dega.

Example:
Word: Gold

Answer:
silver

7. Jiska turn hai sirf wahi answer dega.
8. Correct answer = +1 point.
9. 45 sec me answer nahi diya toh run out, -1 point aur game se bahar.
10. Har round me time 2 sec kam hoga: 45, 43, 41, 39 ... minimum 10.
11. Time 10 sec se niche nahi jayega.
12. Last me highest score / last player winner banega.

⚠️ Note:
Answer spelling bilkul correct honi chahiye."""
    await update.message.reply_text(text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text(f"👥 Users: {len(users)}\n📢 Groups: {len(groups)}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("Usage: /broadcast message")
        return
    sent_users = sent_groups = 0
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
    await update.message.reply_text(f"✅ Broadcast Sent\nUsers: {sent_users}\nGroups: {sent_groups}")

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
            await update.message.reply_text("💕 ᴛʜᴀɴᴋꜱ ꜰᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ!\n\nᴜꜱᴇ /help ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴍʏ ꜰᴇᴀᴛᴜʀᴇꜱ ✨")
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
    if not await is_admin_or_owner(update, context):
        await update.message.reply_text("❌ Sirf admin /tagall use kar sakta hai.")
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
            await context.bot.send_message(chat.id, text, parse_mode=ParseMode.HTML)
            text = ""
    if text:
        await context.bot.send_message(chat.id, text, parse_mode=ParseMode.HTML)

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
        await context.bot.send_photo(chat_id, random.choice(COUPLE_PHOTOS), caption=caption, parse_mode=ParseMode.HTML)
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
        f"💘 {mention_user(user)}'s Sᴇᴄʀᴇᴛ Cʀᴜꜱʜ Iꜱ - {mention_member(crush_user)}\n\nCrush level: {percent}% ❤️",
        parse_mode=ParseMode.HTML
    )

async def brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    iq = random.randint(1, 100)
    await update.message.reply_text(f"🧠 IQ Lᴇᴠᴇʟ Oꜰ {mention_user(update.effective_user)} Iꜱ {iq}% 😎", parse_mode=ParseMode.HTML)

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
        await context.bot.send_animation(update.effective_chat.id, GIFS[action], caption=caption, parse_mode=ParseMode.HTML)
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

def is_game_banned(chat_id, user_id):
    return str(user_id) in game_banned.get(str(chat_id), [])

def add_game_ban(chat_id, user_id):
    cid, uid = str(chat_id), str(user_id)
    game_banned.setdefault(cid, [])
    if uid not in game_banned[cid]:
        game_banned[cid].append(uid)
    save_data(GAME_BAN_FILE, game_banned)

def remove_game_ban(chat_id, user_id):
    cid, uid = str(chat_id), str(user_id)
    if cid in game_banned and uid in game_banned[cid]:
        game_banned[cid].remove(uid)
    save_data(GAME_BAN_FILE, game_banned)

def add_connect_point(chat_id, user, points=1):
    cid, uid = str(chat_id), str(user.id)
    connect_leaderboard.setdefault(cid, {})
    connect_leaderboard[cid].setdefault(uid, {"name": get_name(user), "points": 0, "wins": 0})
    connect_leaderboard[cid][uid]["name"] = get_name(user)
    connect_leaderboard[cid][uid]["points"] += points
    connect_leaderboard[cid][uid]["wins"] += 1
    save_data(CONNECT_LB_FILE, connect_leaderboard)

def make_blank_word(word):
    word = word.lower()
    if len(word) <= 3:
        return word[0] + "_" * (len(word) - 1)
    return word[:2] + "_" * (len(word) - 2)

def format_chain(chain):
    visible = chain[:-1]
    answer = chain[-1]
    blank = make_blank_word(answer)
    return " 🔗 ".join([w.title() for w in visible]) + f" 🔗 <b>{blank.title()}</b>"

async def connectwin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    chat, user = update.effective_chat, update.effective_user

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ ConnectWin sirf group me chalega.")
        return

    if is_game_banned(chat.id, user.id):
        await update.message.reply_text("❌ Tum ConnectWin game se banned ho.")
        return

    if chat.id in connect_games:
        await update.message.reply_text("⚠️ Game room already bana hua hai. Players /join kare, phir /startchaingame do.")
        return

    connect_games[chat.id] = {
        "joining": True,
        "active": False,
        "players": {},
        "score": {},
        "current_player": None,
        "current_word": None,
        "current_answer": None,
        "round": 0,
        "time_limit": 45,
        "answered": False,
        "used_words": [],
        "round_task": None
    }

    await update.message.reply_text(
        "🔗 ᴏᴘᴘᴏꜱɪᴛᴇ ᴄʜᴀɪɴ ɢᴀᴍᴇ ʀᴏᴏᴍ ᴄʀᴇᴀᴛᴇᴅ!\n\n"
        "Khelne ke liye /join bhejo.\n"
        "Minimum players: 2\n\n"
        "Admin/Owner game start karne ke liye /startchaingame de."
    )


async def startchaingame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    chat = update.effective_chat

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Ye command sirf group me chalega.")
        return

    if not await is_admin_or_owner(update, context):
        await update.message.reply_text("❌ Sirf owner/admin game start kar sakta hai.")
        return

    game = connect_games.get(chat.id)

    if not game:
        await update.message.reply_text("❌ Abhi game room nahi bana. Pehle /startconnectwin do.")
        return

    if game.get("active"):
        await update.message.reply_text("⚠️ Game already started hai.")
        return

    if len(game["players"]) < 2:
        await update.message.reply_text("❌ Minimum 2 players chahiye. Players ko /join karne bolo.")
        return

    game["joining"] = False
    game["active"] = True

    await update.message.reply_text(
        f"✅ Game started!\nPlayers: {len(game['players'])}\n\n"
        "Rule: Bot random player choose karega. Us player ko word ka opposite likhna hai.\n"
        "Correct = +1 point | Run out = -1 point\n"
        "Time 45 sec se start hoga, har round 2 sec kam hoga, minimum 10 sec."
    )

    await send_next_opposite_round(chat.id, context)


async def join_connect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_active(update)
    chat, user = update.effective_chat, update.effective_user

    if chat.type not in ["group", "supergroup"]:
        return

    if is_game_banned(chat.id, user.id):
        await update.message.reply_text("❌ Tum ConnectWin game se banned ho.")
        return

    game = connect_games.get(chat.id)

    if not game or not game.get("joining"):
        await update.message.reply_text("❌ Abhi koi join session nahi chal raha.")
        return

    game["players"][user.id] = get_name(user)
    game["score"].setdefault(user.id, 0)

    await update.message.reply_text(
        f"✅ {mention_user(user)} joined game!\nAdmin/Owner ab /startchaingame de sakta hai.",
        parse_mode=ParseMode.HTML
    )


def make_answer_hint(answer):
    answer = answer.lower().strip()
    if len(answer) <= 2:
        return answer
    return answer[:2].title() + " " + " ".join(["_"] * (len(answer) - 2))


async def send_next_opposite_round(chat_id, context: ContextTypes.DEFAULT_TYPE):
    game = connect_games.get(chat_id)
    if not game or not game.get("active"):
        return

    players = list(game["players"].keys())
    if len(players) < 1:
        connect_games.pop(chat_id, None)
        await context.bot.send_message(chat_id, "❌ Game end. Players nahi bache.")
        return

    game["round"] += 1
    game["time_limit"] = max(10, 45 - ((game["round"] - 1) * 2))
    game["answered"] = False

    player_id = random.choice(players)
    game["current_player"] = player_id

    available = [p for p in OPPOSITE_PAIRS if p[0] not in game["used_words"]]
    if not available:
        game["used_words"] = []
        available = OPPOSITE_PAIRS[:]

    word, answer = random.choice(available)
    game["current_word"] = word.lower()
    game["current_answer"] = answer.lower()
    game["used_words"].append(word)

    try:
        member = await context.bot.get_chat_member(chat_id, player_id)
        mention = mention_user(member.user)
    except:
        mention = html.escape(game["players"].get(player_id, "Player"))

    await context.bot.send_message(
        chat_id,
        f"🎯 Turn: {mention}\n"
        f"⏰ Time: <b>{game['time_limit']} sec</b>\n\n"
        f"Word: <b>{html.escape(word.title())}</b>\n"
        f"Hint: <b>{html.escape(make_answer_hint(answer))}</b>\n\n"
        f"Iska opposite English me likho!",
        parse_mode=ParseMode.HTML
    )

    task = context.application.create_task(round_timeout(chat_id, player_id, game["round"], context))
    game["round_task"] = task


async def round_timeout(chat_id, player_id, round_no, context: ContextTypes.DEFAULT_TYPE):
    game = connect_games.get(chat_id)
    if not game:
        return

    await asyncio.sleep(game.get("time_limit", 20))

    game = connect_games.get(chat_id)
    if not game or not game.get("active"):
        return

    if game.get("round") != round_no:
        return

    if game.get("answered"):
        return

    name = game["players"].get(player_id, "Player")
    game["score"][player_id] = game["score"].get(player_id, 0) - 1

    # Run out player game se bahar
    game["players"].pop(player_id, None)

    await context.bot.send_message(
        chat_id,
        f"❌ <b>{html.escape(name)}</b> run out!\n-1 Point\nGame se bahar ho gaya.",
        parse_mode=ParseMode.HTML
    )

    if len(game["players"]) <= 1:
        await finish_opposite_game(chat_id, context)
    else:
        await send_next_opposite_round(chat_id, context)


async def finish_opposite_game(chat_id, context: ContextTypes.DEFAULT_TYPE):
    game = connect_games.get(chat_id)
    if not game:
        return

    scores = game.get("score", {})

    # Last remaining player ko winner bonus
    if game.get("players"):
        winner_id = list(game["players"].keys())[0]
        scores[winner_id] = scores.get(winner_id, 0) + 5
    else:
        winner_id = max(scores, key=scores.get) if scores else None

    if winner_id:
        try:
            member = await context.bot.get_chat_member(chat_id, winner_id)
            winner_name = get_name(member.user)
            add_connect_point(chat_id, member.user, scores.get(winner_id, 0))
        except:
            winner_name = game.get("players", {}).get(winner_id, "Winner")
    else:
        winner_name = "No Winner"

    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    text = "🏆 <b>Opposite Chain Game Finished</b>\n\n"
    text += f"🥇 Winner: <b>{html.escape(winner_name)}</b>\n\n"
    text += "📊 Final Scores:\n"

    for uid, score in top:
        name = game["players"].get(uid) or game.get("score_names", {}).get(uid) or str(uid)
        if uid in game.get("players", {}):
            name = game["players"][uid]
        else:
            name = name if not str(name).isdigit() else "Player"
        text += f"• {html.escape(str(name))} - {score}\n"

    connect_games.pop(chat_id, None)

    await context.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)


async def endconnectwin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ Ye command sirf group me chalega.")
        return

    if not await is_admin_or_owner(update, context):
        await update.message.reply_text("❌ Sirf owner/admin game end kar sakta hai.")
        return

    if chat.id not in connect_games:
        await update.message.reply_text("❌ Abhi koi ConnectWin game nahi chal raha.")
        return

    game = connect_games.pop(chat.id, None)
    task = game.get("round_task") if game else None
    if task:
        task.cancel()

    await update.message.reply_text("✅ Game end kar diya gaya.")


async def connect_guess_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, user = update.effective_chat, update.effective_user

    if not chat or chat.type not in ["group", "supergroup"]:
        return False

    game = connect_games.get(chat.id)

    if not game or not game.get("active"):
        return False

    # Sirf jis player ka turn hai wahi answer de sakta hai
    if user.id != game.get("current_player"):
        return False

    if is_game_banned(chat.id, user.id):
        return True

    guess = (update.message.text or "").strip().lower()
    answer = game.get("current_answer")

    if guess == answer:
        game["answered"] = True
        game["score"][user.id] = game["score"].get(user.id, 0) + 1

        task = game.get("round_task")
        if task:
            task.cancel()

        await update.message.reply_text(
            f"✅ Correct {mention_user(user)}!\n"
            f"{html.escape(game['current_word'].title())} ➜ <b>{html.escape(answer.title())}</b>\n"
            f"+1 Point",
            parse_mode=ParseMode.HTML
        )

        await asyncio.sleep(1)
        await send_next_opposite_round(chat.id, context)
        return True

    return False

async def cleaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    cid = str(chat.id)
    data = connect_leaderboard.get(cid, {})
    if not data:
        await update.message.reply_text("❌ Abhi is group me leaderboard empty hai.")
        return
    top = sorted(data.items(), key=lambda x: x[1].get("points", 0), reverse=True)[:10]
    text = "🏆 <b>ConnectWin Group Leaderboard</b>\n\n"
    for i, (_, info) in enumerate(top, 1):
        text += f"{i}. {html.escape(info.get('name','User'))} - {info.get('points',0)} pts | Wins: {info.get('wins',0)}\n"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def baningame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply karke /Baningame do.")
        return
    target = update.message.reply_to_message.from_user
    add_game_ban(update.effective_chat.id, target.id)
    await update.message.reply_text(f"✅ {mention_user(target)} game se banned.", parse_mode=ParseMode.HTML)

async def unbaningame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply karke /Unbaningame do.")
        return
    target = update.message.reply_to_message.from_user
    remove_game_ban(update.effective_chat.id, target.id)
    await update.message.reply_text(f"✅ {mention_user(target)} game se unbanned.", parse_mode=ParseMode.HTML)

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_owner(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply karke /ban do.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, target.id)
        await update.message.reply_text(f"✅ {mention_user(target)} banned.", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Ban failed: {e}")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_owner(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply karke /unban do.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.unban_chat_member(update.effective_chat.id, target.id)
        await update.message.reply_text(f"✅ {mention_user(target)} unbanned.", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Unban failed: {e}")

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_owner(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply karke /mute do.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text(f"✅ {mention_user(target)} muted.", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Mute failed: {e}")

async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_owner(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply karke /unmute do.")
        return
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await update.message.reply_text(f"✅ {mention_user(target)} unmuted.", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Unmute failed: {e}")

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

    # ConnectWin active ho to joined players ke normal guesses check honge
    if await connect_guess_handler(update, context):
        return

    chat_id = update.effective_chat.id

    if update.effective_chat.type in ["group", "supergroup"]:
        if chatbot_status.get(chat_id, True) is False:
            return

        # Group me bot sirf tab reply karega jab user bot ke message ko reply kare
        if not update.message.reply_to_message:
            return

        replied_user = update.message.reply_to_message.from_user
        if not replied_user or replied_user.id != context.bot.id:
            return

    if not client:
        return

    user_text = update.message.text

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are Ada. Sabse friendly tareeke se baat karo. Hindi me baat karo lekin English alphabets me. Short aur natural replies do. User jaise baat kare waise reply do. Human friend ki tarah behave karo."
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
app.add_handler(CommandHandler("chaingamehelp", chaingamehelp))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("chatbot", chatbot))
app.add_handler(CommandHandler(["tagall", "Tagall"], tagall))

app.add_handler(CommandHandler("startconnectwin", connectwin))
app.add_handler(CommandHandler("startchaingame", startchaingame))
app.add_handler(CommandHandler("endconnectwin", endconnectwin))
app.add_handler(CommandHandler("join", join_connect))
app.add_handler(CommandHandler("cleaderboard", cleaderboard))
app.add_handler(CommandHandler(["Baningame", "baningame"], baningame))
app.add_handler(CommandHandler(["Unbaningame", "unbaningame"], unbaningame))

app.add_handler(CommandHandler(["ban", "Ban"], ban_user))
app.add_handler(CommandHandler(["unban", "Unban"], unban_user))
app.add_handler(CommandHandler(["mute", "Mute"], mute_user))
app.add_handler(CommandHandler(["unmute", "Unmute"], unmute_user))

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

app.add_handler(CallbackQueryHandler(verify_join, pattern="verify_join"))
app.add_handler(CallbackQueryHandler(help_buttons, pattern="help_"))

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.Sticker.ALL, sticker_reply))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

print("Ada Bot Started...")
app.run_polling()
