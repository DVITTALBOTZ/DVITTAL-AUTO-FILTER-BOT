import asyncio
import glob
import importlib
import logging
import logging.config
import sys
import threading
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
from info import *  # OWNER_LNK, LOG_CHANNEL, PORT, MULTIPLE_DB, ON_HEROKU, LOG_STR
from plugins import check_expired_premium, keep_alive, web_server
from Script import script
from utils import temp

Image.MAX_IMAGE_PIXELS = 500_000_000

logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("pymongo").setLevel(logging.WARNING)

botStartTime = time.time()
ppath = "plugins/*.py"
files = glob.glob(ppath)
LOADED_PLUGINS = set()
PLUGINS_FOLDER = Path("plugins")
MAIN_LOOP = None


# ---------------- Plugin Loader ---------------- #
async def load_plugins():
    global LOADED_PLUGINS
    for path in files:
        patt = Path(path)
        plugin_name = patt.stem
        if plugin_name in LOADED_PLUGINS:
            continue
        try:
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_name}", patt
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[f"plugins.{plugin_name}"] = module
            LOADED_PLUGINS.add(plugin_name)
            logging.info(f"✅ DreamxBotz Imported => {plugin_name}")
        except Exception as e:
            logging.error(f"⚠ Failed to import {plugin_name}: {e}")


# ---------------- Plugin Hot Reload ---------------- #
class PluginReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py") and MAIN_LOOP:
            asyncio.run_coroutine_threadsafe(reload_plugin(event.src_path), MAIN_LOOP)

    def on_created(self, event):
        if event.src_path.endswith(".py") and MAIN_LOOP:
            asyncio.run_coroutine_threadsafe(reload_plugin(event.src_path), MAIN_LOOP)


async def reload_plugin(path):
    try:
        patt = Path(path)
        plugin_name = patt.stem
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
        logging.info(f"🔁 Plugin reloaded => {plugin_name}")
    except Exception as e:
        logging.error(f"⚠ Failed to reload plugin {plugin_name}: {e}")


def start_plugin_watcher():
    event_handler = PluginReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, str(PLUGINS_FOLDER), recursive=False)
    observer.daemon = True
    observer.start()
    return observer


# ---------------- Auto Delete PM ---------------- #
@dreamxbotz.on_message(filters.private & ~filters.service)
async def auto_delete_pm(_, message):
    try:
        if message.from_user and str(message.from_user.id) == str(OWNER_LNK):
            return
        await asyncio.sleep(4 * 60 * 60)  # 4 hours
        try:
            await message.delete()
        except Exception:
            pass
    except Exception as e:
        logging.debug(f"Auto-delete error: {e}")


# ---------------- Owner Commands ---------------- #
@dreamxbotz.on_message(filters.command("plugins") & filters.user(OWNER_LNK))
async def list_plugins(_, message):
    loaded = "\n".join(f"• {p}" for p in sorted(LOADED_PLUGINS)) or "No plugins loaded."
    await message.reply_text(f"✅ **Loaded Plugins:**\n{loaded}")


@dreamxbotz.on_message(
    filters.command(["reload", "reload_plugin"]) & filters.user(OWNER_LNK)
)
async def reload_plugins_cmd(_, message):
    args = message.text.split(maxsplit=1)
    target = args[1].strip() if len(args) > 1 else None

    if not target:
        await message.reply_text("♻ Reloading all plugins...")
        for p in list(LOADED_PLUGINS):
            path = Path(f"plugins/{p}.py")
            if path.exists():
                try:
                    await reload_plugin(str(path))
                except Exception as e:
                    await message.reply_text(f"⚠ Failed to reload {p}: {e}")
        await message.reply_text("✅ All plugins reloaded.")
        return

    plugin_name = target.replace(".py", "")
    path = Path(f"plugins/{plugin_name}.py")
    if not path.exists():
        await message.reply_text(f"⚠ Plugin not found: {plugin_name}")
        return
    try:
        await reload_plugin(str(path))
        await message.reply_text(f"🔁 Reloaded plugin: {plugin_name}")
    except Exception as e:
        await message.reply_text(f"⚠ Failed to reload {plugin_name}: {e}")


# ---------------- Bot Startup ---------------- #
async def dreamxbotz_start():
    global MAIN_LOOP
    logging.info("\n🚀 Initializing DreamxBotz...")
    MAIN_LOOP = asyncio.get_running_loop()

    if not dreamxbotz.is_connected:
        await dreamxbotz.start()

    me = await dreamxbotz.get_me()
    dreamxbotz.username = "@" + me.username
    temp.ME, temp.U_NAME, temp.B_NAME, temp.B_LINK = (
        me.id,
        me.username,
        me.first_name,
        me.mention,
    )

    await initialize_clients()
    await load_plugins()

    if ON_HEROKU:
        asyncio.create_task(ping_server())

    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS, temp.BANNED_CHATS = b_users, b_chats

    await Media.ensure_indexes()
    if MULTIPLE_DB:
        await Media2.ensure_indexes()
        logging.info("🗄 Multiple Database Mode On.")
    else:
        logging.info("🗄 Single DB Mode On.")

    dreamxbotz.loop.create_task(check_expired_premium(dreamxbotz))
    logging.info(
        f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on @{me.username}."
    )
    logging.info(LOG_STR)
    logging.info(script.LOGO)

    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)
    today, current_time = date.today(), now.strftime("%I:%M:%S %p")

    try:
        await dreamxbotz.send_message(
            LOG_CHANNEL, script.RESTART_TXT.format(temp.B_LINK, today, current_time)
        )
    except Exception as e:
        logging.warning(f"Failed to send restart message: {e}")

    try:
        app = web.AppRunner(await web_server())
        await app.setup()
        site = web.TCPSite(app, "0.0.0.0", PORT)
        await site.start()
        logging.info(f"🌐 Web server started on port {PORT}")
    except Exception as e:
        logging.error(f"⚠ Web server startup failed: {e}")

    dreamxbotz.loop.create_task(keep_alive())
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
