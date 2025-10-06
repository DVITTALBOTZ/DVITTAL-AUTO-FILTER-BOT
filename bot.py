import asyncio, glob, importlib, sys, time
from datetime import date, datetime
from pathlib import Path

import pytz
from aiohttp import web
from PIL import Image
from pyrogram import __version__, idle, Client, filters
from pyrogram.errors import FloodWait
from pyrogram.raw.all import layer
from pyrogram.types import Message

from database.ia_filterdb import Media, Media2
from database.users_chats_db import db
from dreamxbotz.Bot import dreamxbotz
from dreamxbotz.Bot.clients import initialize_clients
from dreamxbotz.util.keepalive import ping_server
from info import *
from plugins import check_expired_premium, keep_alive, web_server
from Script import script
from utils import temp

import logging, logging.config

Image.MAX_IMAGE_PIXELS = 500_000_000
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
FAILED_PLUGINS = {}
PLUGIN_STATUS = {}
AUTO_DELETE_DELAY = 4*60*60  # 4 hours

# ---------------- Plugin Loader ---------------- #
async def load_plugins():
    global LOADED_PLUGINS
    for path in files:
        plugin_name = Path(path).stem.replace(".py","")
        if plugin_name in LOADED_PLUGINS: continue
        await import_plugin(path, plugin_name)

async def import_plugin(path, plugin_name):
    import_path = f"plugins.{plugin_name}"
    try:
        spec = importlib.util.spec_from_file_location(import_path, Path(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[import_path] = module
        LOADED_PLUGINS.add(plugin_name)
        PLUGIN_STATUS[plugin_name] = "Loaded ✅"
        FAILED_PLUGINS.pop(plugin_name,None)
        print(f"✅ Plugin loaded => {plugin_name}")
        if dreamxbotz.is_connected:
            await dreamxbotz.send_message(LOG_CHANNEL,f"✅ **Plugin loaded:** `{plugin_name}`")
    except Exception as e:
        PLUGIN_STATUS[plugin_name] = f"Failed ❌: {e}"
        FAILED_PLUGINS[plugin_name] = path
        print(f"⚠ Failed to load plugin {plugin_name}: {e}")
        if dreamxbotz.is_connected:
            await dreamxbotz.send_message(LOG_CHANNEL,f"⚠ **Plugin failed:** `{plugin_name}`\n`{e}`")

# ---------------- Dashboard ---------------- #
async def send_plugin_dashboard():
    if not dreamxbotz.is_connected: return
    msg = "**📋 Plugin Status Dashboard:**\n\n"
    for plugin,status in PLUGIN_STATUS.items(): msg+=f"{plugin}: {status}\n"
    await dreamxbotz.send_message(LOG_CHANNEL,msg)

# ---------------- Retry Failed Plugins ---------------- #
async def retry_failed_plugins(interval:int=300):
    while True:
        if FAILED_PLUGINS:
            for plugin_name,path in list(FAILED_PLUGINS.items()):
                print(f"🔁 Retrying plugin: {plugin_name}")
                await import_plugin(path, plugin_name)
        await asyncio.sleep(interval)

# ---------------- Auto-Delete PM ---------------- #
@dreamxbotz.on_message(filters.private & ~filters.service)
async def auto_delete_pm(client:Client,message:Message):
    try: asyncio.create_task(schedule_delete(message))
    except: pass

async def schedule_delete(message:Message):
    await asyncio.sleep(AUTO_DELETE_DELAY)
    try: await message.delete()
    except: pass

# ---------------- Telegram Commands ---------------- #
@dreamxbotz.on_message(filters.command("plugins") & filters.user(OWNER_ID))
async def show_plugins_auto(client:Client,message:Message):
    try:
        if not PLUGIN_STATUS: text="No plugins loaded yet."
        else:
            text="**📋 Plugin Status Dashboard:**\n\n"
            for plugin,status in PLUGIN_STATUS.items(): text+=f"{plugin}: {status}\n"
        await message.reply_text(text)
    except Exception as e: await message.reply_text(f"⚠ Error: {e}")

@dreamxbotz.on_message(filters.command("reload") & filters.user(OWNER_ID))
async def reload_plugin_command(client:Client,message:Message):
    try:
        if len(message.command)<2: await message.reply_text("⚠ Usage: /reload <plugin_name>"); return
        plugin_name = message.command[1].strip()
        plugin_path = f"plugins/{plugin_name}.py"
        if not Path(plugin_path).exists(): await message.reply_text(f"❌ Plugin `{plugin_name}` does not exist."); return
        await import_plugin(plugin_path, plugin_name)
        await message.reply_text(f"🔄 Plugin `{plugin_name}` reloaded successfully!")
    except Exception as e:
        await message.reply_text(f"⚠ Failed to reload plugin `{plugin_name}`:\n{e}")

# ---------------- Bot Startup ---------------- #
async def dreamxbotz_start():
    print("\n\nInitializing DreamxBotz")
    if not dreamxbotz.is_connected: await dreamxbotz.start()
    bot_info = await dreamxbotz.get_me()
    dreamxbotz.username = bot_info.username
    await initialize_clients()
    await load_plugins()
    await send_plugin_dashboard()
    if ON_HEROKU: asyncio.create_task(ping_server())
    b_users,b_chats = await db.get_banned()
    temp.BANNED_USERS=b_users; temp.BANNED_CHATS=b_chats
    await Media.ensure_indexes()
    if MULTIPLE_DB: await Media2.ensure_indexes(); print("Multiple Database Mode On.")
    else: print("Single DB Mode On !")
    me = await dreamxbotz.get_me()
    temp.ME=me.id; temp.U_NAME=me.username; temp.B_NAME=me.first_name; temp.B_LINK=me.mention
    dreamxbotz.username = "@"+me.username
    dreamxbotz.loop.create_task(check_expired_premium(dreamxbotz))
    logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    logging.info(LOG_STR); logging.info(script.LOGO)
    tz=pytz.timezone("Asia/Kolkata"); today=date.today(); now=datetime.now(tz)
    current_time=now.strftime("%H:%M:%S %p")
    await dreamxbotz.send_message(LOG_CHANNEL, script.RESTART_TXT.format(temp.B_LINK,today,current_time))
    # Web server
    app=web.AppRunner(await web_server()); await app.setup(); await web.TCPSite(app,"0.0.0.0",PORT).start()
    dreamxbotz.loop.create_task(keep_alive())
    dreamxbotz.loop.create_task(retry_failed_plugins(300))
    await idle()

# ---------------- Safe Startup ---------------- #
async def safe_start():
    while True:
        try: await dreamxbotz_start(); break
        except FloodWait as e: logging.warning(f"FloodWait! Sleeping for {e.value} seconds..."); await asyncio.sleep(e.value)
        except KeyboardInterrupt:
            logging.info("Service Stopped Bye 👋")
            if dreamxbotz.is_connected: await dreamxbotz.stop(); break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            if dreamxbotz.is_connected: await dreamxbotz.stop()
            logging.info("Restarting in 5 seconds..."); await asyncio.sleep(5)

if __name__=="__main__":
    try: asyncio.run(safe_start())
    except Exception as e: logging.critical(f"Fatal startup error: {e}")
