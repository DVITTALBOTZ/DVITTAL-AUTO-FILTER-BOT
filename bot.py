import asyncio
import glob
import importlib
import logging
import logging.config
import sys
import time
from datetime import date, datetime
from pathlib import Path

import pytz
from aiohttp import web
from PIL import Image
from pyrogram import Client, __version__, filters, idle
from pyrogram.errors import FloodWait, MessageDeleteForbidden
from pyrogram.raw.all import layer

from database.ia_filterdb import Media, Media2
from database.users_chats_db import db
from dreamxbotz.Bot import dreamxbotz
from dreamxbotz.Bot.clients import initialize_clients
from dreamxbotz.util.keepalive import ping_server
from info import *  # includes AUTO_DELETE_HOURS now
from plugins import check_expired_premium, keep_alive, web_server
from Script import script
from utils import temp

# --- Image & Logging setup ---
Image.MAX_IMAGE_PIXELS = 500_000_000
logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("pymongo").setLevel(logging.WARNING)

botStartTime = time.time()
PLUGIN_PATH = Path("plugins")


# --- Helper: Load all plugins safely ---
def load_plugins():
    for plugin_path in PLUGIN_PATH.glob("*.py"):
        plugin_name = plugin_path.stem
        import_path = f"plugins.{plugin_name}"
        try:
            if import_path in sys.modules:
                importlib.reload(sys.modules[import_path])
            else:
                spec = importlib.util.spec_from_file_location(import_path, plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                sys.modules[import_path] = module
            print(f"✅ Loaded plugin: {plugin_name}")
        except Exception as e:
            logging.error(f"❌ Failed to load plugin {plugin_name}: {e}", exc_info=True)


# --- Auto Delete Handler ---
@dreamxbotz.on_message(filters.private & ~filters.service & ~filters.bot)
async def auto_delete_pm(client, message):
    """Automatically delete USER PM messages after configured hours."""
    # Skip messages from the bot itself
    if message.from_user and message.from_user.is_self:
        return

    delay = int(AUTO_DELETE_HOURS) * 60 * 60  # Convert hours to seconds

    try:
        await asyncio.sleep(delay)
        await message.delete()
        logging.info(
            f"🗑️ Auto-deleted PM from {message.from_user.id} after {AUTO_DELETE_HOURS}h"
        )
    except MessageDeleteForbidden:
        logging.warning(f"⚠️ Cannot delete message {message.id} (forbidden)")
    except Exception as e:
        logging.error(f"❌ Error auto-deleting message {message.id}: {e}")


# --- Main Startup ---
async def dreamxbotz_start():
    print("\n🚀 Initializing DreamxBotz...")
    await dreamxbotz.start()

    bot_info = await dreamxbotz.get_me()
    dreamxbotz.username = bot_info.username

    await initialize_clients()
    load_plugins()

    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # Load banned users & chats
    temp.BANNED_USERS, temp.BANNED_CHATS = await db.get_banned()

    # Ensure database indexes
    await Media.ensure_indexes()
    if MULTIPLE_DB:
        await Media2.ensure_indexes()
        print("💾 Multi-DB mode enabled.")
    else:
        print("💾 Single-DB mode enabled.")

    me = bot_info
    temp.ME, temp.U_NAME, temp.B_NAME, temp.B_LINK = (
        me.id,
        me.username,
        me.first_name,
        me.mention,
    )
    dreamxbotz.username = f"@{me.username}"

    dreamxbotz.loop.create_task(check_expired_premium(dreamxbotz))

    logging.info(
        f"{me.first_name} running with Pyrogram v{__version__} (Layer {layer})."
    )
    logging.info(LOG_STR)
    logging.info(script.LOGO)

    tz = pytz.timezone("Asia/Kolkata")
    today = date.today()
    now = datetime.now(tz)
    current_time = now.strftime("%H:%M:%S %p")

    await dreamxbotz.send_message(
        chat_id=LOG_CHANNEL,
        text=script.RESTART_TXT.format(temp.B_LINK, today, current_time),
    )

    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, "0.0.0.0", PORT).start()

    dreamxbotz.loop.create_task(keep_alive())
    await idle()


# --- Safe entry point ---
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(dreamxbotz_start())
            break
        except FloodWait as e:
            print(f"⚠️ FloodWait! Sleeping for {e.value} seconds.")
            loop.run_until_complete(asyncio.sleep(e.value))
        except KeyboardInterrupt:
            logging.info("🛑 Bot stopped by user. Exiting...")
            break
        except Exception as e:
            logging.error(f"Unexpected Error: {e}", exc_info=True)
            time.sleep(5)
