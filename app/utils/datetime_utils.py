"""Datetime manipulation and ISO-8601 formatting utilities."""

from datetime import datetime, timezone
from typing import Optional


def get_utc_now() -> datetime:
    """Returns the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def get_utc_now_iso() -> str:
    """Returns ISO-8601 formatted string of current UTC timestamp."""
    return get_utc_now().isoformat()


def parse_iso_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parses an ISO format string into a datetime object."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def format_date_str(dt: datetime) -> str:
    """Formats a datetime object to YYYY-MM-DD date string."""
    return dt.strftime("%Y-%m-%d")
