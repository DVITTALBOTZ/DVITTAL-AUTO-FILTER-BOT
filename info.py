import os
import re
from os import environ, getenv

from Script import script

# Utility functions
id_pattern = re.compile(r"^-?\d+$")  # corrected regex for IDs


def is_enabled(value, default):
    if isinstance(value, bool):
        return value
    value = str(value).lower()
    if value in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default


# ============================
# Bot Information Configuration
# ============================
SESSION = environ.get("SESSION", "dreamxbotz_search")
API_ID = int(environ.get("API_ID", "2468192"))
API_HASH = environ.get("API_HASH", "4906b3f8f198ec0e24edb2c197677678")
BOT_TOKEN = environ.get("BOT_TOKEN", "")

# ============================
# Bot Settings Configuration
# ============================
CACHE_TIME = int(environ.get("CACHE_TIME", 300))
USE_CAPTION_FILTER = is_enabled(environ.get("USE_CAPTION_FILTER", False), False)
INDEX_CAPTION = is_enabled(environ.get("SAVE_CAPTION", False), False)

PICS = environ.get("PICS", "https://envs.sh/t3L.jpg").split()
NOR_IMG = environ.get("NOR_IMG", "https://graph.org/file/e20b5fdaf217252964202.jpg")
MELCOW_PHOTO = environ.get("MELCOW_PHOTO", "https://envs.sh/t3L.jpg")
SPELL_IMG = environ.get("SPELL_IMG", "https://envs.sh/P9Q.jpg")
SUBSCRIPTION = environ.get(
    "SUBSCRIPTION", "https://graph.org/file/242b7f1b52743938d81f1.jpg"
)
FSUB_PICS = environ.get("FSUB_PICS", "https://envs.sh/bBD.jpg").split()

# ============================
# Admin, Channels & Users Configuration
# ============================
ADMINS = [
    int(admin) if id_pattern.match(admin) else admin
    for admin in environ.get("ADMINS", "2098589219").split()
]
CHANNELS = [
    int(ch) if id_pattern.match(ch) else ch
    for ch in environ.get("CHANNELS", "-100").split()
]

LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "-1001693006436"))
BIN_CHANNEL = int(environ.get("BIN_CHANNEL", "-1001693006436"))
PREMIUM_LOGS = int(environ.get("PREMIUM_LOGS", "-1001693006436"))
DELETE_CHANNELS = [
    int(dch) if id_pattern.match(dch) else dch
    for dch in environ.get("DELETE_CHANNELS", "-1001693006436").split()
]
support_chat_id = environ.get("SUPPORT_CHAT_ID", "-1001734119324")
reqst_channel = environ.get("REQST_CHANNEL_ID", "-1002485372743")
SUPPORT_CHAT = environ.get("SUPPORT_CHAT", "https://t.me/+TpM5uDvYamswZGM9")

auth_req_channels = environ.get("AUTH_REQ_CHANNELS", "-1001882874297")
auth_channels = environ.get("AUTH_CHANNELS", "-1002055023335")

# ============================
# Payment Configuration
# ============================
QR_CODE = environ.get("QR_CODE", "https://envs.sh/t3L.jpg")
OWNER_UPI_ID = environ.get("OWNER_UPI_ID", "@Nikhil5757h")

STAR_PREMIUM_PLANS = {
    10: "7day",
    20: "15day",
    40: "1month",
    55: "45day",
    75: "60day",
}

# ============================
# MongoDB Configuration
# ============================
DATABASE_URI = environ.get("DATABASE_URI", "")
DATABASE_NAME = environ.get("DATABASE_NAME", "Rashmika1")
COLLECTION_NAME = environ.get("COLLECTION_NAME", "Rashmika1")
MULTIPLE_DB = is_enabled(environ.get("MULTIPLE_DB", "True"), True)
DATABASE_URI2 = environ.get("DATABASE_URI2", "")

# ============================
# Movie Notification & Update Settings
# ============================
MOVIE_UPDATE_NOTIFICATION = is_enabled(
    environ.get("MOVIE_UPDATE_NOTIFICATION", False), False
)
MOVIE_UPDATE_CHANNEL = int(environ.get("MOVIE_UPDATE_CHANNEL", "-100"))
DREAMXBOTZ_IMAGE_FETCH = is_enabled(environ.get("DREAMXBOTZ_IMAGE_FETCH", False), False)
LINK_PREVIEW = is_enabled(environ.get("LINK_PREVIEW", False), False)
ABOVE_PREVIEW = is_enabled(environ.get("ABOVE_PREVIEW", False), False)
TMDB_API_KEY = environ.get("TMDB_API_KEY", "")
TMDB_POSTER = is_enabled(environ.get("TMDB_POSTER", False), False)
LANDSCAPE_POSTER = is_enabled(environ.get("LANDSCAPE_POSTER", False), False)

# ============================
# Verification Settings
# ============================
IS_VERIFY = is_enabled(environ.get("IS_VERIFY", False), False)
LOG_VR_CHANNEL = int(environ.get("LOG_VR_CHANNEL", "-1001693006436"))
LOG_API_CHANNEL = int(environ.get("LOG_API_CHANNEL", "-1001693006436"))
VERIFY_IMG = environ.get(
    "VERIFY_IMG", "https://telegra.ph/file/9ecc5d6e4df5b83424896.jpg"
)

TUTORIAL = environ.get("TUTORIAL", "https://t.me/how_to_opan_linkz/6")
TUTORIAL_2 = environ.get("TUTORIAL_2", "https://t.me/how_to_opan_linkz/6")
TUTORIAL_3 = environ.get("TUTORIAL_3", "https://t.me/how_to_opan_linkz/6")

SHORTENER_API = environ.get("SHORTENER_API", "ab42d0b5656f5c774f800dacb6739342b6f094aa")
SHORTENER_WEBSITE = environ.get("SHORTENER_WEBSITE", "vplink.in")
SHORTENER_API2 = environ.get(
    "SHORTENER_API2", "ab42d0b5656f5c774f800dacb6739342b6f094aa"
)
SHORTENER_WEBSITE2 = environ.get("SHORTENER_WEBSITE2", "vplink.in")
SHORTENER_API3 = environ.get(
    "SHORTENER_API3", "ab42d0b5656f5c774f800dacb6739342b6f094aa"
)
SHORTENER_WEBSITE3 = environ.get("SHORTENER_WEBSITE3", "vplink.in")

TWO_VERIFY_GAP = int(environ.get("TWO_VERIFY_GAP", "1200"))
THREE_VERIFY_GAP = int(environ.get("THREE_VERIFY_GAP", "54000"))

# ============================
# Channel & Group Links Configuration
# ============================
GRP_LNK = environ.get("GRP_LNK", "https://t.me/Sandalwood_Kannada_Group")
OWNER_LNK = environ.get("OWNER_LNK", "https://t.me/NIKHIL5757H")
UPDATE_CHNL_LNK = environ.get("UPDATE_CHNL_LNK", "https://t.me/KR_PICTURE")

# ============================
# User Configuration
# ============================
auth_users = [
    int(user) if id_pattern.match(user) else user
    for user in environ.get("AUTH_USERS", "2098589219").split()
]
AUTH_USERS = (auth_users + ADMINS) if auth_users else ADMINS
PREMIUM_USER = [
    int(user) if id_pattern.match(user) else user
    for user in environ.get("PREMIUM_USER", "").split()
]

# ============================
# Miscellaneous Configuration
# ============================
MAX_B_TN = int(environ.get("MAX_B_TN", "8"))
PORT = int(environ.get("PORT", "8080"))
MSG_ALRT = environ.get("MSG_ALRT", "Tᴇᴀᴍ: @KR_Picture ❤️")
DELETE_TIME = int(environ.get("DELETE_TIME", "1800"))
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", getattr(script, "CAPTION", ""))
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", getattr(script, "IMDB_TEMPLATE_TXT", ""))
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get("INDEX_REQ_CHANNEL", LOG_CHANNEL))
NO_RESULTS_MSG = is_enabled(environ.get("NO_RESULTS_MSG", False), False)
MAX_BTN = is_enabled(environ.get("MAX_BTN", "True"), True)
P_TTI_SHOW_OFF = is_enabled(environ.get("P_TTI_SHOW_OFF", "True"), True)
IMDB = is_enabled(environ.get("IMDB", "False"), False)
AUTO_FFILTER = is_enabled(environ.get("AUTO_FFILTER", "True"), True)
AUTO_DELETE = is_enabled(environ.get("AUTO_DELETE", "True"), True)
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "False"), False)
MELCOW_NEW_USERS = is_enabled(environ.get("MELCOW_NEW_USERS", "False"), False)
PROTECT_CONTENT = is_enabled(environ.get("PROTECT_CONTENT", "False"), False)
PM_SEARCH = is_enabled(environ.get("PM_SEARCH", False), False)
EMOJI_MODE = is_enabled(environ.get("EMOJI_MODE", False), False)
BUTTON_MODE = is_enabled(environ.get("BUTTON_MODE", "False"), False)
STREAM_MODE = is_enabled(environ.get("STREAM_MODE", False), False)
PREMIUM_STREAM_MODE = is_enabled(environ.get("PREMIUM_STREAM_MODE", False), False)

# ============================
# Bot Configuration
# ============================

AUTH_REQ_CHANNELS = [
    int(ch) for ch in auth_req_channels.split() if ch and id_pattern.match(ch)
]
AUTH_CHANNELS = [int(ch) for ch in auth_channels.split() if ch and id_pattern.match(ch)]
REQST_CHANNEL = (
    int(reqst_channel) if reqst_channel and id_pattern.match(reqst_channel) else None
)
SUPPORT_CHAT_ID = (
    int(support_chat_id)
    if support_chat_id and id_pattern.match(support_chat_id)
    else None
)
LANGUAGES = {
    "ᴍᴀʟᴀʏᴀʟᴀᴍ": "mal",
    "ᴛᴀᴍɪʟ": "tam",
    "ᴇɴɢʟɪsʜ": "eng",
    "ʜɪɴᴅɪ": "hin",
    "ᴛᴇʟᴜɢᴜ": "tel",
    "ᴋᴀɴɴᴀᴅᴀ": "kan",
    "ɢᴜᴊᴀʀᴀᴛɪ": "guj",
    "ᴍᴀʀᴀᴛʜɪ": "mar",
    "ᴘᴜɴᴊᴀʙɪ": "pun",
}
QUALITIES = ["360P", "480P", "720P", "1080P", "1440P", "2160P", "4K"]

SEASON_COUNT = 12
SEASONS = [f"S{str(i).zfill(2)}" for i in range(1, SEASON_COUNT + 1)]

BAD_WORDS = {
    "PrivateMovieZ",
    "toonworld4all",
    "themoviesboss",
    "1tamilmv",
    "tamilblasters",
    "1tamilblasters",
    "skymovieshd",
    "extraflix",
    "hdm2",
    "moviesmod",
    "hdhub4u",
    "mkvcinemas",
    "primefix",
    "join",
    "www",
    "villa",
    "tg",
    "original",
}

# ============================
# Server & Web Configuration
# ============================
NO_PORT = is_enabled(environ.get("NO_PORT", False), False)
APP_NAME = environ.get("APP_NAME", None)
ON_HEROKU = "DYNO" in environ

BIND_ADDRESS = environ.get("WEB_SERVER_BIND_ADDRESS", "0.0.0.0")
if environ.get("FQDN"):
    FQDN = environ.get("FQDN")
elif ON_HEROKU and APP_NAME:
    FQDN = f"{APP_NAME}.herokuapp.com"
else:
    FQDN = "localhost"  # safer fallback than 0.0.0.0

HAS_SSL = is_enabled(environ.get("HAS_SSL", True), True)
PORT = int(environ.get("PORT", "8080"))

if HAS_SSL:
    URL = f"https://{FQDN}/"
else:
    URL = f"http://{FQDN}/"

SLEEP_THRESHOLD = int(environ.get("SLEEP_THRESHOLD", "60"))
WORKERS = int(environ.get("WORKERS", "4"))
SESSION_NAME = environ.get("SESSION_NAME", "dreamXBotz")
MULTI_CLIENT = False
name = environ.get("name", "DREAMXBOTZ")
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))

# ============================
# Reactions Configuration
# ============================
REACTIONS = [
    "🤝",
    "😇",
    "🤗",
    "😍",
    "👍",
    "🎅",
    "😐",
    "🥰",
    "🤩",
    "😱",
    "🤣",
    "😘",
    "👏",
    "😛",
    "😈",
    "🎉",
    "⚡️",
    "🫡",
    "🤓",
    "😎",
    "🏆",
    "🔥",
    "🤭",
    "🌚",
    "🆒",
    "👻",
    "😁",
]

# ============================
# Commands Bot
# ============================
Bot_cmds = {
    "start": "Sᴛᴀʀᴛ Mᴇ Bᴀʙʏ",
    "stats": "Gᴇᴛ Bᴏᴛ Sᴛᴀᴛs",
    "alive": " Cʜᴇᴄᴋ Bᴏᴛ Aʟɪᴠᴇ ᴏʀ Nᴏᴛ ",
    "settings": "ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɢs",
    "id": "ɢᴇᴛ ɪᴅ ᴛᴇʟᴇɢʀᴀᴍ ",
    "info": "Gᴇᴛ Usᴇʀ ɪɴғᴏ ",
    "del_msg": "ʀᴇᴍᴏᴠᴇ ғɪʟᴇ ɴᴀᴍᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ɴᴏтɪғɪᴄᴀᴛɪᴏɴ...",
    "movie_update": "ᴏɴ ᴏғғ ᴀᴄᴄᴏʀᴅɪɴɢ ʏᴏᴜʀ ɴᴇᴇᴅᴇᴅ...",
    "pm_search": "ᴘᴍ sᴇᴀʀᴄʜ ᴏɴ ᴏғғ ᴀᴄᴄᴏʀᴅɪɴɢ ʏᴏᴜʀ ɴᴇᴇᴅᴇᴅ...",
    "trendlist": "Gᴇᴛ Tᴏᴘ Tʀᴀɴᴅɪɴɢ Sᴇᴀʀᴄʜ Lɪsᴛ",
    "broadcast": "ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ.",
    "grp_broadcast": "ʙʀᴏᴀᴅᴄᴀsᴛ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɢʀᴏᴜᴘs",
    "send": "ꜱᴇɴᴅ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴀ ᴘᴀʀᴛɪᴄᴜʟᴀʀ ᴜꜱᴇʀ.",
    "add_premium": "ᴀᴅᴅ ᴀɴʏ ᴜꜱᴇʀ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ.",
    "remove_premium": "ʀᴇᴍᴏᴠᴇ ᴀɴʏ ᴜꜱᴇʀ ꜰʀᴏᴍ ᴘʀᴇᴍɪᴜᴍ.",
    "premium_users": "ɢᴇᴛ ʟɪꜱᴛ ᴏꜰ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ.",
    "restart": "ʀᴇꜱᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ.",
    "group_cmd": "ɢʀᴏᴜᴘ ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ",
    "admin_cmd": "ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs ʟɪsᴛ.",
    "reset_group": "Group Setting Default",
    "trial_reset": "User Trial Reset",
}

# ============================
# Logs Configuration
# ============================
LOG_STR = "Current Customized Configurations are:-\n"
LOG_STR += (
    "IMDB Results are enabled, Bot will be showing imdb details for your queries.\n"
    if IMDB
    else "IMDB Results are disabled.\n"
)
LOG_STR += (
    "P_TTI_SHOW_OFF found, Users will be redirected to send /start to Bot PM instead of sending file directly.\n"
    if P_TTI_SHOW_OFF
    else "P_TTI_SHOW_OFF is disabled, files will be sent in PM instead of starting the bot.\n"
)
LOG_STR += (
    "BUTTON_MODE is found, filename and file size will be shown in a single button instead of two separate buttons.\n"
    if BUTTON_MODE
    else "BUTTON_MODE is disabled, filename and file size will be shown as different buttons.\n"
)
LOG_STR += (
    f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be sent along with this customized caption.\n"
    if CUSTOM_FILE_CAPTION
    else "No CUSTOM_FILE_CAPTION Found, Default captions of file will be used.\n"
)
LOG_STR += (
    "Long IMDB storyline enabled.\n"
    if LONG_IMDB_DESCRIPTION
    else "LONG_IMDB_DESCRIPTION is disabled, Plot will be shorter.\n"
)
LOG_STR += (
    "Spell Check Mode is enabled, bot will be suggesting related movies if movie name is misspelled.\n"
    if SPELL_CHECK_REPLY
    else "Spell Check Mode is disabled.\n"
)
