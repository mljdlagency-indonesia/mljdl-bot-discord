"""
services/sheets_service.py -- Google Sheets reader via gspread + service account
"""
import json
import gspread
from google.oauth2.service_account import Credentials
from bot.config import config


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

_client: gspread.Client | None = None


def _get_client() -> gspread.Client:
    """Lazy-init gspread client."""
    global _client
    if _client is None:
        # Support both file path dan JSON string langsung di env
        raw = config.GOOGLE_SERVICE_ACCOUNT_JSON
        try:
            creds_dict = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            # Kalau bukan JSON string, treat sebagai file path
            with open(raw) as f:
                creds_dict = json.load(f)

        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        _client = gspread.authorize(creds)
    return _client


def _get_sheet() -> gspread.Worksheet:
    client = _get_client()
    spreadsheet = client.open_by_key(config.SPREADSHEET_ID)
    return spreadsheet.worksheet(config.SHEET_NAME)


def get_last_row() -> dict:
    """
    Ambil row terakhir dari sheet.
    Returns dict dengan header sebagai key.
    """
    sheet = _get_sheet()
    headers = sheet.row_values(1)
    all_values = sheet.get_all_values()

    if len(all_values) < 2:
        return {}

    last_row = all_values[-1]
    # Zip header ke values, handle kalau kolom lebih sedikit dari header
    return {
        headers[i]: last_row[i] if i < len(last_row) else ""
        for i in range(len(headers))
    }


def get_all_rows(limit: int = 10) -> list[dict]:
    """Ambil N row terakhir sebagai list of dicts."""
    sheet = _get_sheet()
    records = sheet.get_all_records()
    return records[-limit:] if len(records) > limit else records


def search_by_column(column: str, value: str) -> list[dict]:
    """Cari rows dimana nilai kolom tertentu match (case-insensitive)."""
    sheet = _get_sheet()
    records = sheet.get_all_records()
    return [
        row for row in records
        if str(row.get(column, "")).lower() == value.lower()
    ]
