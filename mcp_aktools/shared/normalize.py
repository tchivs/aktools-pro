"""Normalization helpers for tool outputs."""

from __future__ import annotations

import pandas as pd

from .schema import INDICATOR_COLUMNS, PRICE_COLUMNS, RATE_COLUMNS, format_error_csv


def _ensure_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col not in df.columns:
            df[col] = None
    return df


def normalize_price_df(
    df: pd.DataFrame | None,
    column_map: dict[str, str],
    source: str,
    currency: str,
    limit: int,
    float_format: str = "%.2f",
    date_unit: str | None = None,
    indicator_map: dict[str, str] | None = None,
) -> str:
    if df is None or df.empty:
        return format_error_csv("empty data", source)

    data = df.copy()

    for canonical, original in column_map.items():
        if original in data.columns:
            data.rename(columns={original: canonical}, inplace=True)

    date_col = "date"
    if date_col in data.columns:
        if date_unit:
            data[date_col] = pd.to_datetime(data[date_col], errors="coerce", unit=date_unit)
        else:
            data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
        data.sort_values(date_col, inplace=True)

    for numeric_col in ["open", "high", "low", "close", "volume", "amount"]:
        if numeric_col in data.columns:
            data[numeric_col] = pd.to_numeric(data[numeric_col], errors="coerce")

    if indicator_map:
        for canonical, original in indicator_map.items():
            if original in data.columns:
                data.rename(columns={original: canonical}, inplace=True)
        for indicator in INDICATOR_COLUMNS:
            if indicator in data.columns:
                data[indicator] = pd.to_numeric(data[indicator], errors="coerce")

    data = _ensure_columns(data, PRICE_COLUMNS)
    data["currency"] = currency
    data["source"] = source

    tail = data.tail(limit)
    columns = PRICE_COLUMNS + [col for col in INDICATOR_COLUMNS if col in tail.columns]
    return tail.to_csv(columns=columns, index=False, float_format=float_format).strip()


def normalize_rate_df(
    df: object | None,
    column_map: dict[str, str],
    source: str,
    currency: str,
    limit: int,
    float_format: str = "%.4f",
    date_unit: str | None = None,
) -> str:
    if df is None:
        return format_error_csv("empty data", source)

    data = pd.DataFrame(df)
    if data.empty:
        return format_error_csv("empty data", source)
    for canonical, original in column_map.items():
        if original in data.columns:
            data.rename(columns={original: canonical}, inplace=True)

    if "date" in data.columns:
        if date_unit:
            data["date"] = pd.to_datetime(data["date"], errors="coerce", unit=date_unit)
        else:
            data["date"] = pd.to_datetime(data["date"], errors="coerce")
        data.sort_values("date", inplace=True)

    if "rate" in data.columns:
        data["rate"] = pd.to_numeric(data["rate"], errors="coerce")

    data = _ensure_columns(data, RATE_COLUMNS)
    data["currency"] = currency
    data["source"] = source

    tail = data.tail(limit)
    return tail.to_csv(columns=RATE_COLUMNS, index=False, float_format=float_format).strip()
