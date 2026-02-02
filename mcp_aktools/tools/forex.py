"""外汇数据工具模块"""

import akshare as ak
import pandas as pd
from pydantic import Field

from mcp_aktools.server import mcp
from mcp_aktools.shared.normalize import normalize_rate_df
from mcp_aktools.shared.utils import ak_cache

# 主要货币对映射
FX_PAIRS = {
    "USDCNY": "美元/人民币",
    "EURUSD": "欧元/美元",
    "USDJPY": "美元/日元",
    "GBPUSD": "英镑/美元",
    "AUDUSD": "澳元/美元",
    "USDCAD": "美元/加元",
    "USDCHF": "美元/瑞郎",
    "NZDUSD": "纽元/美元",
}


@mcp.tool(
    title="获取外汇汇率",
    description="获取主要货币对的实时汇率报价，输出标准化字段",
)
def fx_rates(
    symbol: str = Field(
        "USDCNY",
        description="货币对代码，支持: USDCNY(美元/人民币), EURUSD(欧元/美元), USDJPY(美元/日元), GBPUSD(英镑/美元), AUDUSD(澳元/美元), USDCAD(美元/加元), USDCHF(美元/瑞郎), NZDUSD(纽元/美元)",
    ),
):
    """获取实时外汇汇率"""
    raw = ak_cache(ak.fx_spot_quote, ttl=300)
    if not isinstance(raw, pd.DataFrame):
        return normalize_rate_df(None, {}, source="akshare", currency=symbol.upper(), limit=1)
    df = raw.copy()

    data = df.copy()
    if symbol and symbol.upper() in FX_PAIRS:
        pair_name = FX_PAIRS[symbol.upper()]
        if "货币对" in data.columns:
            mask = data["货币对"].str.contains(symbol, case=False, na=False)
            data = data.loc[mask]
            if isinstance(data, pd.Series):
                data = data.to_frame().T
        elif "名称" in data.columns:
            mask = data["名称"].str.contains(pair_name, case=False, na=False)
            data = data.loc[mask]
            if isinstance(data, pd.Series):
                data = data.to_frame().T

    rate_column = None
    for candidate in ["最新价", "现汇卖出价", "现汇买入价", "汇率"]:
        if candidate in data.columns:
            rate_column = candidate
            break

    if rate_column is None:
        return normalize_rate_df(None, {}, source="akshare", currency=symbol.upper(), limit=1)

    data = data.copy()
    data["rate"] = data[rate_column]
    if "时间" in data.columns:
        data["date"] = data["时间"]
    elif "日期" in data.columns:
        data["date"] = data["日期"]

    return normalize_rate_df(
        data,
        {"date": "date", "rate": "rate"},
        source="akshare",
        currency=symbol.upper() if symbol else "FX",
        limit=len(data),
        float_format="%.4f",
    )


@mcp.tool(
    title="获取外汇历史汇率",
    description="获取指定货币对的历史汇率数据，用于分析汇率走势和波动",
)
def fx_history(
    symbol: str = Field(
        "USDCNY",
        description="货币对代码，支持: USDCNY(美元/人民币), EURUSD(欧元/美元), USDJPY(美元/日元), GBPUSD(英镑/美元), AUDUSD(澳元/美元), USDCAD(美元/加元), USDCHF(美元/瑞郎), NZDUSD(纽元/美元)",
    ),
    limit: int = Field(30, description="返回数量(int)，建议30-252", strict=False),
):
    """获取外汇历史汇率"""
    # 使用 akshare 的外汇历史数据接口
    raw = ak_cache(ak.fx_pair_quote, symbol=symbol.upper())
    if not isinstance(raw, pd.DataFrame):
        return normalize_rate_df(None, {}, source="akshare", currency=symbol.upper(), limit=limit)
    df = raw.copy()

    df = df.tail(limit).copy()
    date_col = "日期" if "日期" in df.columns else "时间" if "时间" in df.columns else None
    rate_col = None
    for candidate in ["收盘价", "最新价", "收盘"]:
        if candidate in df.columns:
            rate_col = candidate
            break
    if date_col is None or rate_col is None:
        return normalize_rate_df(None, {}, source="akshare", currency=symbol.upper(), limit=limit)

    df = df.copy()
    df["rate"] = df[rate_col]

    return normalize_rate_df(
        df,
        {"date": date_col, "rate": "rate"},
        source="akshare",
        currency=symbol.upper(),
        limit=limit,
        float_format="%.4f",
    )
