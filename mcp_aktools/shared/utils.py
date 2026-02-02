import asyncio
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial

import akshare as ak
import pandas as pd

from ..cache import CacheKey
from .constants import PORTFOLIO_FILE

_LOGGER = logging.getLogger(__name__)

# Thread pool for running blocking akshare calls
_executor = ThreadPoolExecutor(max_workers=8)


def ak_cache(fun, *args, **kwargs) -> pd.DataFrame | None:
    key = kwargs.pop("key", None)
    if not key:
        key = f"{fun.__name__}-{args}-{kwargs}"
    ttl1 = kwargs.pop("ttl", 86400)
    ttl2 = kwargs.pop("ttl2", None)
    cache = CacheKey.init(key, ttl1, ttl2)
    all_df = cache.get()
    if all_df is None:
        try:
            _LOGGER.info("Request akshare: %s", [key, args, kwargs])
            all_df = fun(*args, **kwargs)
            cache.set(all_df)
        except Exception as exc:
            _LOGGER.exception(str(exc))
    return all_df


async def ak_cache_async(fun, *args, **kwargs) -> pd.DataFrame | None:
    """Async version of ak_cache that runs blocking calls in thread pool."""
    key = kwargs.pop("key", None)
    if not key:
        key = f"{fun.__name__}-{args}-{kwargs}"
    ttl1 = kwargs.pop("ttl", 86400)
    ttl2 = kwargs.pop("ttl2", None)
    cache = CacheKey.init(key, ttl1, ttl2)
    all_df = cache.get()
    if all_df is None:
        try:
            _LOGGER.info("Request akshare async: %s", [key, args, kwargs])
            loop = asyncio.get_event_loop()
            all_df = await loop.run_in_executor(_executor, partial(fun, *args, **kwargs))
            cache.set(all_df)
        except Exception as exc:
            _LOGGER.exception(str(exc))
    return all_df


def recent_trade_date():
    now = datetime.now().date()
    dfs = ak_cache(ak.tool_trade_date_hist_sina, ttl=43200)
    if dfs is None:
        return now
    dfs.sort_values("trade_date", ascending=False, inplace=True)
    for d in dfs["trade_date"]:
        if d <= now:
            return d
    return now


def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        os.makedirs(os.path.dirname(PORTFOLIO_FILE), exist_ok=True)
        return {}
    with open(PORTFOLIO_FILE, "r") as f:
        return json.load(f)


def save_portfolio(data):
    os.makedirs(os.path.dirname(PORTFOLIO_FILE), exist_ok=True)
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(data, f, indent=2)


def ak_search(symbol: str | None = None, keyword: str | None = None, market: str | None = None):
    markets = [
        ["sh", ak.stock_info_a_code_name, "code", "name"],
        ["sh", ak.stock_info_sh_name_code, "证券代码", "证券简称"],
        ["sz", ak.stock_info_sz_name_code, "A股代码", "A股简称"],
        ["hk", ak.stock_hk_spot, "代码", "中文名称"],
        ["hk", ak.stock_hk_spot_em, "代码", "名称"],
        ["us", ak.get_us_stock_name, "symbol", "cname"],
        ["us", ak.get_us_stock_name, "symbol", "name"],
        ["sh", ak.fund_etf_spot_ths, "基金代码", "基金名称"],
        ["sz", ak.fund_etf_spot_ths, "基金代码", "基金名称"],
        ["sh", ak.fund_info_index_em, "基金代码", "基金名称"],
        ["sz", ak.fund_info_index_em, "基金代码", "基金名称"],
        ["sh", ak.fund_etf_spot_em, "代码", "名称"],
        ["sz", ak.fund_etf_spot_em, "代码", "名称"],
    ]
    for m in markets:
        if market and market != m[0]:
            continue
        all_df = ak_cache(m[1], ttl=86400, ttl2=86400 * 7)
        if all_df is None or all_df.empty:
            continue
        for _, v in all_df.iterrows():
            code, name = str(v[m[2]]).upper(), str(v[m[3]]).upper()
            if symbol and symbol.upper() == code:
                return v
            if keyword and keyword.upper() in [code, name]:
                return v
        if keyword:
            for _, v in all_df.iterrows():
                name = str(v[m[3]])
                if len(keyword) >= 4 and keyword in name:
                    return v
                if name.startswith(keyword):
                    return v
    return None


async def ak_search_async(symbol: str | None = None, keyword: str | None = None, market: str | None = None):
    """Async version with parallel data fetching for faster search."""
    markets = [
        ["sh", ak.stock_info_a_code_name, "code", "name"],
        ["sh", ak.stock_info_sh_name_code, "证券代码", "证券简称"],
        ["sz", ak.stock_info_sz_name_code, "A股代码", "A股简称"],
        ["hk", ak.stock_hk_spot, "代码", "中文名称"],
        ["hk", ak.stock_hk_spot_em, "代码", "名称"],
        ["us", ak.get_us_stock_name, "symbol", "cname"],
        ["us", ak.get_us_stock_name, "symbol", "name"],
        ["sh", ak.fund_etf_spot_ths, "基金代码", "基金名称"],
        ["sz", ak.fund_etf_spot_ths, "基金代码", "基金名称"],
        ["sh", ak.fund_info_index_em, "基金代码", "基金名称"],
        ["sz", ak.fund_info_index_em, "基金代码", "基金名称"],
        ["sh", ak.fund_etf_spot_em, "代码", "名称"],
        ["sz", ak.fund_etf_spot_em, "代码", "名称"],
    ]

    filtered_markets = [m for m in markets if not market or market == m[0]]
    if not filtered_markets:
        return None

    tasks = [ak_cache_async(m[1], ttl=86400, ttl2=86400 * 7) for m in filtered_markets]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for m, all_df in zip(filtered_markets, results):
        if isinstance(all_df, Exception) or all_df is None or all_df.empty:
            continue
        for _, v in all_df.iterrows():
            code, name = str(v[m[2]]).upper(), str(v[m[3]]).upper()
            if symbol and symbol.upper() == code:
                return v
            if keyword and keyword.upper() in [code, name]:
                return v
        if keyword:
            for _, v in all_df.iterrows():
                name = str(v[m[3]])
                if len(keyword) >= 4 and keyword in name:
                    return v
                if name.startswith(keyword):
                    return v
    return None
