"""
run.py -- Entry point untuk menjalankan bot
Usage: python run.py
"""
import asyncio
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from bot.main import MyBot
from bot.config import config


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

    bot = MyBot()
    async with bot:
        await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
