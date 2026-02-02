"""Shared output schemas for tools."""

from __future__ import annotations

import csv
from io import StringIO

PRICE_COLUMNS = [
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "currency",
    "source",
]

INDICATOR_COLUMNS = [
    "macd",
    "dif",
    "dea",
    "kdj_k",
    "kdj_d",
    "kdj_j",
    "rsi",
    "boll_u",
    "boll_m",
    "boll_l",
]

RATE_COLUMNS = [
    "date",
    "rate",
    "currency",
    "source",
]

ERROR_COLUMNS = [
    "error",
    "source",
    "fallback",
]


def format_error_csv(error: str, source: str, fallback: str | None = None) -> str:
    """Return a CSV string with error contract."""

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(ERROR_COLUMNS)
    writer.writerow([error, source, fallback or ""])
    return output.getvalue().strip()
