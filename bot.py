import sys
import glob
import importlib
import time
import asyncio
import logging
import pytz
from pathlib import Path
from datetime import date, datetime
from asyncio import sleep

import aiohttp
from aiohttp import web
from PIL import Image
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
from pyrogram.errors import FloodWait

from database.users_chats_db import db
from database.ia_filterdb import Media, Media2
from info import LOG_CHANNEL, URL, *
from utils import temp
from Script import script
from plugins import web_server, check_expired_premium, keep_alive
from dreamxbotz.Bot import dreamxbotz
from dreamxbotz.util.keepalive import ping_server
from dreamxbotz.Bot.clients import initialize_clients
from .route import routes

Image.MAX_IMAGE_PIXELS = 500_000_000
logging.config.dictConfig(logging.getLogger().manager.loggerDict)

logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)
logging.getLogger("pymongo").setLevel(logging.WARNING)


botStartTime = time.time()
ppath = "plugins/*.py"
files = glob.glob(ppath)

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

async def check_expired_premium(client):
    while 1:
        data = await db.get_expired(datetime.now())
        for user in data:
            user_id = user["id"]
            await db.remove_premium_access(user_id)
            try:
                user = await client.get_users(user_id)
                await client.send_message(
                    chat_id=user_id,
                    text=f"<b>ʜᴇʏ {user.mention},\n\n𝑌𝑜𝑢𝑟 𝑃𝑟𝑒𝑚𝑖𝑢𝑚 𝐴𝑐𝑐𝑒𝑠𝑠 𝐻𝑎𝑠 𝐸𝑥𝑝𝑖𝑟𝑒𝑑 𝑇ℎ𝑎𝑛𝑘 𝑌𝑜𝑢 𝐹𝑜𝑟 𝑈𝑠𝑖𝑛𝑔 𝑂𝑢𝑟 𝑆𝑒𝑟𝑣𝑖𝑐𝑒 😊. 𝐼𝑓 𝑌𝑜𝑢 𝑊𝑎𝑛𝑡 𝑇𝑜 𝑇𝑎𝑘𝑒 𝑃𝑟𝑒𝑚𝑖𝑢𝑚 𝐴𝑔𝑎𝑖𝑛, 𝑇ℎ𝑒𝑛 𝐶𝑙𝑖𝑐𝑘 𝑂𝑛 𝑇ℎ𝑒 /plan 𝐹𝑜𝑟 𝑇ℎ𝑒 𝐷𝑒𝑡𝑎𝑖𝑙𝑠 𝑂𝐹 𝑇ℎ𝑒 𝑃𝑙𝑎𝑛𝑠..\n\n\n<blockquote>आपका 𝑷𝒓𝒆𝒎𝒊𝒖𝒎 𝑨𝒄𝒄𝒆𝒔𝒔 समाप्त हो गया है हमारी सेवा का उपयोग करने के लिए धन्यवाद 😊। यदि आप फिर से 𝑷𝒓𝒆𝒎𝒊𝒖𝒎 लेना चाहते हैं, तो योजनाओं के विवरण के लिए /plan पर 𝑪𝒍𝒊𝒄𝒌 करें।</blockquote></b>"
                )
                await client.send_message(LOG_CHANNEL, text=f"<b>#Premium_Expire\n\nUser name: {user.mention}\nUser id: <code>{user_id}</code>")
            except Exception as e:
                print(e)
            await sleep(0.5)
        await sleep(1)

async def keep_alive():
    """Keep bot alive by sending periodic pings."""
    async with aiohttp.ClientSession() as session:
        while True:
            await asyncio.sleep(298)
            try:
                async with session.get(URL) as resp:
                    if resp.status != 200:
                        logging.warning(f"⚠️ Ping Error! Status: {resp.status}")
            except Exception as e:
                logging.error(f"❌ Ping Failed: {e}")

async def dreamxbotz_start():
    print('\n\nInitalizing DreamxBotz')
    await dreamxbotz.start()
    bot_info = await dreamxbotz.get_me()
    dreamxbotz.username = bot_info.username
    await initialize_clients()
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("DreamxBotz Imported => " + plugin_name)
    if ON_HEROKU:
        asyncio.create_task(ping_server()) 
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    await Media.ensure_indexes()
    if MULTIPLE_DB:
        await Media2.ensure_indexes()
        print("Multiple Database Mode On. Now Files Will Be Save In Second DB If First DB Is Full")
    else:
        print("Single DB Mode On ! Files Will Be Save In First Database")
    me = await dreamxbotz.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    temp.B_LINK = me.mention
    dreamxbotz.username = '@' + me.username
    dreamxbotz.loop.create_task(check_expired_premium(dreamxbotz))
    logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    logging.info(LOG_STR)
    logging.info(script.LOGO)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    await dreamxbotz.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(temp.B_LINK, today, time))
    for admin_id in ADMINS:
        try:
            await dreamxbotz.send_message(chat_id=int(admin_id), text=f"🤖 {temp.B_NAME} Restarted Successfully ✅")
        except Exception as e:
            logging.warning(f"Couldn't send restart message to admin {admin_id}: {e}")
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    dreamxbotz.loop.create_task(keep_alive())
    await idle()
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(dreamxbotz_start())
            break  
        except FloodWait as e:
            print(f"FloodWait! Sleeping for {e.value} seconds.")
            time.sleep(e.value) 
        except KeyboardInterrupt:
            logging.info('Service Stopped Bye 👋')
            break
