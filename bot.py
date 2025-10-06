import asyncio
import glob
import importlib
import sys
import time
from datetime import date, datetime
from pathlib import Path

import pytz
from aiohttp import web
from PIL import Image
from pyrogram import __version__, filters, idle
from pyrogram.errors import FloodWait
from pyrogram.raw.all import layer
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from database.ia_filterdb import Media, Media2
from database.users_chats_db import db
from dreamxbotz.Bot import dreamxbotz
from dreamxbotz.Bot.clients import initialize_clients
from dreamxbotz.util.keepalive import ping_server
from info import *  # OWNER_LNK should be here
from plugins import check_expired_premium, keep_alive, web_server
from Script import script
from utils import temp

Image.MAX_IMAGE_PIXELS = 500_000_000

import logging
import logging.config

logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)
logging.getLogger("pymongo").setLevel(logging.WARNING)

botStartTime = time.time()
ppath = "plugins/*.py"
files = glob.glob(ppath)
LOADED_PLUGINS = set()
PLUGINS_FOLDER = Path("plugins")


# ---------------- Plugin Loader ---------------- #
async def load_plugins():
    global LOADED_PLUGINS
    for path in files:
        patt = Path(path)
        plugin_name = patt.stem.replace(".py", "")
        if plugin_name in LOADED_PLUGINS:
            continue
        plugins_dir = Path(f"plugins/{plugin_name}.py")
        import_path = f"plugins.{plugin_name}"
        spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[import_path] = module
        LOADED_PLUGINS.add(plugin_name)
        print(f"✅ DreamxBotz Imported => {plugin_name}")


# ---------------- Plugin Hot-Reload ---------------- #
class PluginReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            asyncio.create_task(reload_plugin(event.src_path))

    def on_created(self, event):
        if event.src_path.endswith(".py"):
            asyncio.create_task(reload_plugin(event.src_path))


async def reload_plugin(path):
    try:
        patt = Path(path)
        plugin_name = patt.stem.replace(".py", "")
        import_path = f"plugins.{plugin_name}"

        if import_path in sys.modules:
            del sys.modules[import_path]
            if plugin_name in LOADED_PLUGINS:
                LOADED_PLUGINS.remove(plugin_name)

        spec = importlib.util.spec_from_file_location(import_path, Path(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[import_path] = module
        LOADED_PLUGINS.add(plugin_name)
        print(f"🔁 Plugin reloaded => {plugin_name}")
    except Exception as e:
        print(f"⚠ Failed to reload plugin {plugin_name}: {e}")


def start_plugin_watcher():
    event_handler = PluginReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, str(PLUGINS_FOLDER), recursive=False)
    observer.start()
    return observer


# ---------------- Auto Delete Private Messages ---------------- #
@dreamxbotz.on_message(filters.private & ~filters.service)
async def auto_delete_pm(_, message):
    try:
        # Ignore owner messages
        if message.from_user and str(message.from_user.id) == str(OWNER_LNK):
            return

        delete_after = 4 * 60 * 60  # 4 hours
        await asyncio.sleep(delete_after)
        await message.delete()
    except Exception as e:
        print(f"Auto-delete error: {e}")


# ---------------- Owner Command to Reload Plugins ---------------- #
@dreamxbotz.on_message(filters.command("plugins") & filters.user(OWNER_LNK))
async def list_plugins(_, message):
    loaded = "\n".join(f"• {p}" for p in sorted(LOADED_PLUGINS)) or "No plugins loaded."
    await message.reply_text(f"✅ **Loaded Plugins:**\n{loaded}")


# ---------------- Bot Startup ---------------- #
async def dreamxbotz_start():
    print("\n🚀 Initializing DreamxBotz...")

    if not dreamxbotz.is_connected:
        await dreamxbotz.start()

    bot_info = await dreamxbotz.get_me()
    dreamxbotz.username = bot_info.username
    await initialize_clients()
    await load_plugins()

    if ON_HEROKU:
        asyncio.create_task(ping_server())

    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats

    await Media.ensure_indexes()
    if MULTIPLE_DB:
        await Media2.ensure_indexes()
        print("🗄 Multiple Database Mode On.")
    else:
        print("🗄 Single DB Mode On.")

    me = await dreamxbotz.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    temp.B_LINK = me.mention
    dreamxbotz.username = "@" + me.username

    dreamxbotz.loop.create_task(check_expired_premium(dreamxbotz))
    logging.info(
        f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}."
    )
    logging.info(LOG_STR)
    logging.info(script.LOGO)

    tz = pytz.timezone("Asia/Kolkata")
    today = date.today()
    now = datetime.now(tz)
    current_time = now.strftime("%I:%M:%S %p")

    await dreamxbotz.send_message(
        chat_id=LOG_CHANNEL,
        text=script.RESTART_TXT.format(temp.B_LINK, today, current_time),
    )

    # Start web server
    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, "0.0.0.0", PORT).start()

    # Keep-alive
    dreamxbotz.loop.create_task(keep_alive())

    # Plugin watcher
    observer = start_plugin_watcher()
    dreamxbotz.loop.create_task(asyncio.to_thread(observer.join))

    await idle()


# ---------------- Safe Startup ---------------- #
async def safe_start():
    while True:
        try:
            await dreamxbotz_start()
            break
        except FloodWait as e:
            logging.warning(f"⏳ FloodWait! Sleeping for {e.value} seconds...")
            await asyncio.sleep(e.value)
        except KeyboardInterrupt:
            logging.info("🛑 Service Stopped Bye 👋")
            if dreamxbotz.is_connected:
                await dreamxbotz.stop()
            break
        except Exception as e:
            logging.error(f"⚠ Unexpected error: {e}")
            if dreamxbotz.is_connected:
                await dreamxbotz.stop()
            logging.info("♻ Restarting DreamxBotz in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(safe_start())
    except Exception as e:
        logging.critical(f"💥 Fatal startup error: {e}")
