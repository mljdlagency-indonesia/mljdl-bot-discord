"""
run.py -- Entry point untuk menjalankan bot
Usage: python run.py
"""
import asyncio
import logging
import os
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import aiohttp

from bot.main import MyBot
from bot.config import config

log = logging.getLogger("bot")


class HealthHandler(BaseHTTPRequestHandler):
    """Minimal HTTP server agar HF Spaces detect app running."""
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        pass  # suppress access logs


def start_health_server():
    port = int(os.getenv("PORT", 7860))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


async def main() -> None:
    # Start health check server in background (for HF Spaces)
    threading.Thread(target=start_health_server, daemon=True).start()

    # Force Google DNS via custom resolver (HF Spaces DNS fix)
    resolver = aiohttp.resolver.AsyncResolver(nameservers=["8.8.8.8", "8.8.4.4"])
    connector = aiohttp.TCPConnector(resolver=resolver)

    bot = MyBot()
    bot.http.connector = connector

    # Retry connection up to 5 times (HF Spaces network might not be ready)
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            async with bot:
                await bot.start(config.DISCORD_TOKEN)
        except Exception as e:
            if attempt < max_retries:
                wait = attempt * 5
                log.warning(f"Connection failed (attempt {attempt}/{max_retries}): {e}")
                log.warning(f"Retrying in {wait}s...")
                await asyncio.sleep(wait)
            else:
                log.error(f"Failed after {max_retries} attempts: {e}")
                raise


if __name__ == "__main__":
    asyncio.run(main())
