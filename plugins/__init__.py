import asyncio
import logging
from datetime import datetime

import aiohttp
from aiohttp import web

from database.users_chats_db import db
from info import LOG_CHANNEL, PREMIUM_LOGS, URL
from .route import routes

# -----------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

# -----------------------------------------------------------
# Web Server Setup (for Koyeb health checks)
# -----------------------------------------------------------
async def web_server():
    """Start aiohttp web server for health checks and API routes."""
    app = web.Application(client_max_size=30_000_000)
    app.add_routes(routes)
    return app

# -----------------------------------------------------------
# Premium Expiry Checker
# -----------------------------------------------------------
async def check_expired_premium(client):
    """Periodically check for expired premium users and notify them."""
    while True:
        try:
            expired_users = await db.get_expired(datetime.now())
            if expired_users:
                logging.info(f"Found {len(expired_users)} expired premium users.")
            for user in expired_users:
                user_id = user.get("id")
                if not user_id:
                    continue

                await db.remove_premium_access(user_id)
                try:
                    user_info = await client.get_users(user_id)
                    await client.send_message(
                        chat_id=user_id,
                        text=(
                            f"<b>ʜᴇʏ {user_info.mention},\n\n"
                            "𝑌𝑜𝑢𝑟 𝑃𝑟𝑒𝑚𝑖𝑢𝑚 𝐴𝑐𝑐𝑒𝑠𝑠 𝐻𝑎𝑠 𝐸𝑥𝑝𝑖𝑟𝑒𝑑 💎\n"
                            "𝐓𝐡𝐚𝐧𝐤 𝐘𝐨𝐮 𝐅𝐨𝐫 𝐔𝐬𝐢𝐧𝐠 𝐎𝐮𝐫 𝐒𝐞𝐫𝐯𝐢𝐜𝐞 😊\n\n"
                            "𝐓𝐨 𝐑𝐞𝐧𝐞𝐰 𝐘𝐨𝐮𝐫 𝐏𝐥𝐚𝐧, 𝐂𝐥𝐢𝐜𝐤 /plan 🔁\n\n"
                            "<blockquote>"
                            "आपका Premium Access समाप्त हो गया है। "
                            "फिर से प्रीमियम लेने के लिए /plan पर क्लिक करें।"
                            "</blockquote></b>"
                        ),
                    )

                    await client.send_message(
                        PREMIUM_LOGS,
                        text=(
                            f"<b>#Premium_Expire\n\n"
                            f"👤 User: {user_info.mention}\n"
                            f"🆔 ID: <code>{user_id}</code></b>"
                        ),
                    )

                except Exception as e:
                    logging.error(f"Error notifying user {user_id}: {e}")
                await asyncio.sleep(0.5)

        except Exception as e:
            logging.error(f"Error while checking expired premiums: {e}")

        await asyncio.sleep(60)  # Check every 1 minute

# -----------------------------------------------------------
# Keep Alive Pinger
# -----------------------------------------------------------
async def keep_alive():
    """Send periodic pings to keep the bot alive on Koyeb."""
    if not URL or "localhost" in URL:
        logging.warning("⚠️ Invalid or local URL detected — skipping ping loop.")
        return

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(URL) as resp:
                    if resp.status == 200:
                        logging.info("✅ Ping successful (200 OK).")
                    else:
                        logging.warning(f"⚠️ Ping returned status: {resp.status}")
            except Exception as e:
                logging.error(f"❌ Ping failed: {e}")
            await asyncio.sleep(298)  # Ping every 5 minutes
