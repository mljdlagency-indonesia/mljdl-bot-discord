"""
config.py -- Central config loader from .env
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")


class Config:
    DISCORD_TOKEN: str = os.environ["DISCORD_TOKEN"]

    # Google Sheets
    GOOGLE_SERVICE_ACCOUNT_JSON: str = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
    SPREADSHEET_ID: str = os.environ["SPREADSHEET_ID"]
    SHEET_NAME: str = os.getenv("SHEET_NAME", "Sheet1")

    # GitHub
    GITHUB_TOKEN: str = os.environ["GITHUB_TOKEN"]
    GITHUB_REPO: str = os.environ["GITHUB_REPO"]
    GITHUB_POLL_INTERVAL: int = int(os.getenv("GITHUB_POLL_INTERVAL", 300))
    GITHUB_NOTIF_CHANNEL_ID: int = int(os.environ["GITHUB_NOTIF_CHANNEL_ID"])

    # Bot prefix
    COMMAND_PREFIX: str = os.getenv("COMMAND_PREFIX", "!")


config = Config()
