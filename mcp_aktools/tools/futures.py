"""期货数据工具模块"""

import akshare as ak
import pandas as pd
from pydantic import Field

from mcp_aktools.server import mcp
from mcp_aktools.shared.normalize import normalize_price_df
from mcp_aktools.shared.schema import format_error_csv
from mcp_aktools.shared.utils import ak_cache

# 主要期货品种映射
FUTURES_SYMBOLS = {
    "螺纹钢": "RB",
    "铁矿石": "I",
    "原油": "SC",
    "沪铜": "CU",
    "沪金": "AU",
    "沪银": "AG",
    "焦炭": "J",
    "焦煤": "JM",
    "动力煤": "ZC",
    "玉米": "C",
    "豆粕": "M",
    "豆油": "Y",
    "棕榈油": "P",
    "白糖": "SR",
    "棉花": "CF",
    "PTA": "TA",
    "甲醇": "MA",
    "玻璃": "FG",
}


@mcp.tool(
    title="获取期货价格",
    description="获取国内期货主力合约的历史价格数据，包括开高低收、成交量等技术指标",
)
def futures_prices(
    symbol: str = Field(
        "螺纹钢",
        description="期货品种，支持: 螺纹钢(RB), 铁矿石(I), 原油(SC), 沪铜(CU), 沪金(AU), 沪银(AG), 焦炭(J), 焦煤(JM), 动力煤(ZC), 玉米(C), 豆粕(M), 豆油(Y), 棕榈油(P), 白糖(SR), 棉花(CF), PTA(TA), 甲醇(MA), 玻璃(FG)",
    ),
    limit: int = Field(30, description="返回数量(int)，建议30-252", strict=False),
):
    """获取期货价格"""
    # 转换品种名称为代码
    symbol_code = FUTURES_SYMBOLS.get(symbol, symbol)

    # 使用 akshare 的期货主力合约数据接口
    df = ak_cache(ak.futures_main_sina, symbol=symbol_code)
    if df is None or df.empty:
        return normalize_price_df(
            None,
            {},
            source="akshare",
            currency="CNY",
            limit=limit,
        )

    # 取最近的数据
    df = df.tail(limit).copy()

    # 确保日期列存在并格式化
    if "日期" in df.columns:
        df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
    elif "时间" in df.columns:
        df["日期"] = pd.to_datetime(df["时间"], errors="coerce")
        df = df.drop(columns=["时间"])

    date_col = "日期" if "日期" in df.columns else "时间" if "时间" in df.columns else "日期"
    open_col = "开盘价" if "开盘价" in df.columns else "开盘"
    high_col = "最高价" if "最高价" in df.columns else "最高"
    low_col = "最低价" if "最低价" in df.columns else "最低"
    close_col = "收盘价" if "收盘价" in df.columns else "收盘"

    return normalize_price_df(
        df,
        {
            "date": date_col,
            "open": open_col,
            "high": high_col,
            "low": low_col,
            "close": close_col,
            "volume": "成交量",
        },
        source="akshare",
        currency="CNY",
        limit=limit,
        float_format="%.2f",
    )


@mcp.tool(
    title="获取期货库存",
    description="获取国内期货品种的仓单库存数据，用于判断供需关系和价格走势",
)
def futures_inventory(
    symbol: str = Field(
        "螺纹钢",
        description="期货品种，支持: 螺纹钢(RB), 铁矿石(I), 原油(SC), 沪铜(CU), 沪金(AU), 沪银(AG), 焦炭(J), 焦煤(JM), 动力煤(ZC), 玉米(C), 豆粕(M), 豆油(Y), 棕榈油(P), 白糖(SR), 棉花(CF), PTA(TA), 甲醇(MA), 玻璃(FG)",
    ),
):
    """获取期货库存"""
    # 转换品种名称为代码
    symbol_code = FUTURES_SYMBOLS.get(symbol, symbol)

    # 使用 akshare 的期货库存数据接口
    df = ak_cache(ak.futures_inventory_em, symbol=symbol_code)
    if df is None or df.empty:
        return format_error_csv("empty data", "akshare", fallback=symbol)

    # 确保日期列存在并格式化
    if "日期" in df.columns:
        df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
    elif "时间" in df.columns:
        df["日期"] = pd.to_datetime(df["时间"], errors="coerce")
        df = df.drop(columns=["时间"])

    return df.to_csv(index=False, float_format="%.2f")


@mcp.tool(
    title="获取期现价差",
    description="获取期货与现货价格的基差数据，用于判断市场预期和套利机会",
)
def futures_basis(
    symbol: str = Field(
        "螺纹钢",
        description="期货品种，支持: 螺纹钢(RB), 铁矿石(I), 原油(SC), 沪铜(CU), 沪金(AU), 沪银(AG), 焦炭(J), 焦煤(JM), 动力煤(ZC), 玉米(C), 豆粕(M), 豆油(Y), 棕榈油(P), 白糖(SR), 棉花(CF), PTA(TA), 甲醇(MA), 玻璃(FG)",
    ),
):
    """获取期现价差"""
    # 转换品种名称为代码
    symbol_code = FUTURES_SYMBOLS.get(symbol, symbol)

    # 使用 akshare 的期现价差数据接口
    df = ak_cache(ak.futures_spot_price, symbol=symbol_code)
    if df is None or df.empty:
        return format_error_csv("empty data", "akshare", fallback=symbol)

    # 确保日期列存在并格式化
    if "日期" in df.columns:
        df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
    elif "时间" in df.columns:
        df["日期"] = pd.to_datetime(df["时间"], errors="coerce")
        df = df.drop(columns=["时间"])

    return df.to_csv(index=False, float_format="%.2f")


@mcp.tool(
    title="获取期货持仓排名",
    description="获取期货主力合约的机构持仓排名数据，用于判断主力资金动向",
)
def futures_positions(
    symbol: str = Field(
        "螺纹钢",
        description="期货品种，支持: 螺纹钢(RB), 铁矿石(I), 原油(SC), 沪铜(CU), 沪金(AU), 沪银(AG), 焦炭(J), 焦煤(JM), 动力煤(ZC), 玉米(C), 豆粕(M), 豆油(Y), 棕榈油(P), 白糖(SR), 棉花(CF), PTA(TA), 甲醇(MA), 玻璃(FG)",
    ),
):
    """获取期货持仓排名"""
    # 转换品种名称为代码
    symbol_code = FUTURES_SYMBOLS.get(symbol, symbol)

    # 使用 akshare 的期货持仓排名数据接口
    df = ak_cache(ak.futures_hold_pos_sina, symbol=symbol_code)
    if df is None or df.empty:
        return format_error_csv("empty data", "akshare", fallback=symbol)

    return df.to_csv(index=False, float_format="%.2f")
