from __future__ import annotations

import re
from datetime import date
from typing import Optional


def parse_price_to_int(price_text: str | None) -> Optional[int]:
    if not price_text:
        return None
    digits = re.sub(r"\D", "", price_text)
    return int(digits) if digits else None


def parse_release_date(value: str | None) -> Optional[date]:
    if not value:
        return None
    # supports YYYY or YYYY-MM or YYYY/MM or YYYY.MM
    m = re.match(r"^(\d{4})(?:[-/.](\d{1,2}))?$", value.strip())
    if not m:
        return None
    year = int(m.group(1))
    month = int(m.group(2)) if m.group(2) else 1
    try:
        return date(year, month, 1)
    except ValueError:
        return None
