import asyncio
import glob
import importlib.util
import sys
from datetime import date, datetime
from pathlib import Path

import pytz
from aiohttp import web
from PIL import Image
from pyrogram import __version__, idle
from pyrogram.errors import FloodWait
from pyrogram.raw.all import layer

from database.ia_filterdb import Media, Media2
from database.users_chats_db import db
from dreamxbotz.Bot import dreamxbotz
from dreamxbotz.Bot.clients import initialize_clients
from dreamxbotz.util.keepalive import ping_server
from info import *
from plugins import check_expired_premium, keep_alive, web_server
from Script import script
from utils import temp

# PIL image size limit
Image.MAX_IMAGE_PIXELS = 500_000_000

# Logging configuration
import logging
import logging.config

logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)
logging.getLogger("pymongo").setLevel(logging.WARNING)

PLUGIN_PATH = "plugins/*.py"
plugin_files = glob.glob(PLUGIN_PATH)


async def load_plugins():
    """Dynamically import all plugins from the plugins folder."""
    for filepath in plugin_files:
        path = Path(filepath)
        plugin_name = path.stem
        import_path = f"plugins.{plugin_name}"
        spec = importlib.util.spec_from_file_location(import_path, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[import_path] = module
        print(f"DreamxBotz Imported => {plugin_name}")


async def safe_start_bot():
    """Wrapper to start bot with FloodWait handling."""
    while True:
        try:
            await start_bot()
            break
        except FloodWait as e:
            logging.warning(f"FloodWait! Sleeping asynchronously for {e.value} seconds...")
            await asyncio.sleep(e.value)
        except KeyboardInterrupt:
            logging.info("Service stopped. Bye 👋")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}", exc_info=True)
            await asyncio.sleep(5)  # brief delay before retry


async def start_bot():
    """Main startup routine for DreamxBotz."""
    print("\n\nInitializing DreamxBotz...")
    await dreamxbotz.start()

    # Get bot info
    me = await dreamxbotz.get_me()
    dreamxbotz.username = f"@{me.username}"
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    temp.B_LINK = me.mention

    # Initialize additional clients
    await initialize_clients()

    # Load plugins
    await load_plugins()

    # Ping server if on Heroku
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # Load banned users and chats
    banned_users, banned_chats = await db.get_banned()
    temp.BANNED_USERS = banned_users
    temp.BANNED_CHATS = banned_chats

    # Ensure database indexes
    await Media.ensure_indexes()
    if MULTIPLE_DB:
        await Media2.ensure_indexes()
        print("Multiple Database Mode On. Files will be saved in second DB if the first DB is full.")
    else:
        print("Single DB Mode On! Files will be saved in first database.")

    # Start premium expiry checker
    asyncio.create_task(check_expired_premium(dreamxbotz))

    # Logging startup
    logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    logging.info(LOG_STR)
    logging.info(script.LOGO)

    # Send startup message
    tz = pytz.timezone("Asia/Kolkata")
    today = date.today()
    now = datetime.now(tz)
    current_time = now.strftime("%H:%M:%S %p")
    await dreamxbotz.send_message(
        chat_id=LOG_CHANNEL,
        text=script.RESTART_TXT.format(temp.B_LINK, today, current_time)
    )

    # Start web server
    app_runner = web.AppRunner(await web_server())
    await app_runner.setup()
    site = web.TCPSite(app_runner, "0.0.0.0", PORT)
    await site.start()

    # Start keep-alive task
    asyncio.create_task(keep_alive())

    # Keep the bot running
    await idle()


if __name__ == "__main__":
    asyncio.run(safe_start_bot())
