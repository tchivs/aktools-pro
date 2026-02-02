from datetime import datetime, timedelta

import akshare as ak
import pandas as pd
from fastmcp import Context
from pydantic import Field

from ..server import mcp
from ..shared.fields import field_market, field_symbol
from ..shared.indicators import add_technical_indicators
from ..shared.normalize import normalize_price_df
from ..shared.utils import ak_cache, ak_search


@mcp.tool(
    title="查找股票代码",
    description="根据股票名称、公司名称等关键词查找股票代码, 不支持加密货币。"
    "该工具比较耗时，当你知道股票代码或用户已指定股票代码时，建议直接通过股票代码使用其他工具",
)
async def search(
    keyword: str = Field(description="搜索关键词，公司名称、股票名称、股票代码、证券简称"),
    market: str = field_market,
    ctx: Context | None = None,
):
    if ctx:
        await ctx.report_progress(0, 100, "正在初始化搜索...")

    if ctx:
        await ctx.report_progress(30, 100, "正在查询市场数据...")

    info = ak_search(None, keyword, market)

    if ctx:
        await ctx.report_progress(70, 100, "正在匹配关键词...")

    if info is not None:
        if ctx:
            await ctx.report_progress(100, 100, "搜索完成")
        suffix = f"交易市场: {market}"
        return "\n".join([info.to_string(), suffix])

    if ctx:
        await ctx.report_progress(100, 100, "未找到结果")
    return f"Not Found for {keyword}"


@mcp.tool(
    title="获取股票信息",
    description="根据股票代码和市场获取股票基本信息, 不支持加密货币",
)
def stock_info(
    symbol: str = field_symbol,
    market: str = field_market,
) -> str:
    markets = [
        ["sh", ak.stock_individual_info_em],
        ["sz", ak.stock_individual_info_em],
        ["hk", ak.stock_hk_security_profile_em],
    ]
    for m in markets:
        if m[0] != market:
            continue
        all_df: pd.DataFrame | None = ak_cache(m[1], symbol=symbol, ttl=43200)
        if all_df is None or all_df.empty:
            continue
        return all_df.to_string()

    info = ak_search(symbol, market)
    if info is not None:
        return info.to_string()
    return f"Not Found for {symbol}.{market}"


@mcp.tool(
    title="个股新闻",
    description="获取指定个股最近新闻动态",
)
def stock_news(
    symbol: str = field_symbol,
    limit: int = Field(10, description="返回数量(int)", strict=False),
):
    dfs = ak_cache(ak.stock_news_em, symbol=symbol, ttl=3600)
    if dfs is None:
        return f"未获取到相关新闻: {symbol}"
    if dfs.empty:
        return f"未获取到相关新闻: {symbol}"
    try:
        if "发布时间" in dfs.columns:
            dfs.sort_values("发布时间", ascending=False, inplace=True)
        elif "时间" in dfs.columns:
            dfs.sort_values("时间", ascending=False, inplace=True)
    except Exception:
        pass
    return dfs.head(int(limit)).to_csv(index=False).strip()


@mcp.tool(
    title="机构持仓汇总",
    description="获取个股最新机构持仓与持股比例等信息",
)
def institutional_holding_summary(symbol: str = field_symbol):
    dfs = ak_cache(ak.stock_institute_hold, symbol=symbol, ttl=43200)
    if dfs is None or dfs.empty:
        return f"未获取到机构持仓数据: {symbol}"
    try:
        if "报告期" in dfs.columns:
            dfs.sort_values("报告期", inplace=True)
        if "序号" in dfs.columns:
            dfs.drop(columns=["序号"], inplace=True)
    except Exception:
        pass
    return dfs.head(20).to_csv(index=False, float_format="%.2f").strip()


@mcp.tool(
    title="获取市场历史价格",
    description="统一获取股票/ETF历史价格及技术指标，输出标准化行情字段",
)
def market_prices(
    symbol: str = field_symbol,
    market: str = field_market,
    period: str = Field("daily", description="周期，如: daily(日线), weekly(周线，不支持美股)"),
    limit: int = Field(30, description="返回数量(int)", strict=False),
    asset: str = Field("equity", description="资产类型: equity/etf"),
) -> str:
    if not isinstance(market, str):
        market = "sh"
    if not isinstance(period, str):
        period = "daily"
    if not isinstance(asset, str):
        asset = "equity"
    if period == "weekly":
        delta = {"weeks": limit + 62}
    else:
        delta = {"days": limit + 62}
    start_date = (datetime.now() - timedelta(**delta)).strftime("%Y%m%d")
    markets = [
        ["sh", ak.stock_zh_a_hist, {}, "equity"],
        ["sz", ak.stock_zh_a_hist, {}, "equity"],
        ["hk", ak.stock_hk_hist, {}, "equity"],
        ["us", stock_us_daily, {}, "equity"],
        ["sh", fund_etf_hist_sina, {"market": "sh"}, "etf"],
        ["sz", fund_etf_hist_sina, {"market": "sz"}, "etf"],
    ]
    for m in markets:
        if m[0] != market:
            continue
        if m[3] != asset:
            continue
        extra = m[2] if isinstance(m[2], dict) else {}
        kws = {"period": period, "start_date": start_date, **extra}
        dfs = ak_cache(m[1], symbol=symbol, ttl=3600, **kws)
        if dfs is None or dfs.empty:
            continue
        add_technical_indicators(dfs, dfs["收盘"], dfs["最低"], dfs["最高"])
        currency_map = {"sh": "CNY", "sz": "CNY", "hk": "HKD", "us": "USD"}
        currency = currency_map.get(market, "CNY")
        return normalize_price_df(
            dfs,
            {
                "date": "日期",
                "open": "开盘",
                "high": "最高",
                "low": "最低",
                "close": "收盘",
                "volume": "成交量",
                "amount": "成交额",
            },
            source="akshare",
            currency=currency,
            limit=limit,
            float_format="%.2f",
            indicator_map={
                "macd": "MACD",
                "dif": "DIF",
                "dea": "DEA",
                "kdj_k": "KDJ.K",
                "kdj_d": "KDJ.D",
                "kdj_j": "KDJ.J",
                "rsi": "RSI",
                "boll_u": "BOLL.U",
                "boll_m": "BOLL.M",
                "boll_l": "BOLL.L",
            },
        )
    return normalize_price_df(
        None,
        {},
        source="akshare",
        currency="",
        limit=limit,
    )


def stock_us_daily(symbol, start_date="2025-01-01", period="daily"):
    dfs = ak.stock_us_daily(symbol=symbol)
    if dfs is None or dfs.empty:
        return None
    dfs.rename(
        columns={
            "date": "日期",
            "open": "开盘",
            "close": "收盘",
            "high": "最高",
            "low": "最低",
            "volume": "成交量",
        },
        inplace=True,
    )
    dfs["换手率"] = None
    dfs.index = pd.to_datetime(dfs["日期"], errors="coerce")
    return dfs[start_date:"2222-01-01"]


def fund_etf_hist_sina(symbol, market="sh", start_date="2025-01-01", period="daily"):
    dfs = ak.fund_etf_hist_sina(symbol=f"{market}{symbol}")
    if dfs is None or dfs.empty:
        return None
    dfs.rename(
        columns={
            "date": "日期",
            "open": "开盘",
            "close": "收盘",
            "high": "最高",
            "low": "最低",
            "volume": "成交量",
        },
        inplace=True,
    )
    dfs["换手率"] = None
    dfs.index = pd.to_datetime(dfs["日期"], errors="coerce")
    return dfs[start_date:"2222-01-01"]


@mcp.tool(
    title="A股关键指标",
    description="获取中国A股市场(上证、深证)的股票财务报告关键指标",
)
def stock_indicators_a(
    symbol: str = field_symbol,
):
    dfs = ak_cache(ak.stock_financial_abstract_ths, symbol=symbol)
    if dfs is None:
        return f"未获取到财务指标: {symbol}"
    if dfs.empty:
        return f"未获取到财务指标: {symbol}"
    keys = dfs.to_csv(index=False, float_format="%.3f").strip().split("\n")
    return "\n".join([keys[0], *keys[-15:]])


@mcp.tool(
    title="港股关键指标",
    description="获取港股市场的股票财务报告关键指标",
)
def stock_indicators_hk(
    symbol: str = field_symbol,
):
    dfs = ak_cache(ak.stock_financial_hk_analysis_indicator_em, symbol=symbol, indicator="报告期")
    if dfs is None:
        return f"未获取到财务指标: {symbol}"
    if dfs.empty:
        return f"未获取到财务指标: {symbol}"
    keys = dfs.to_csv(index=False, float_format="%.3f").strip().split("\n")
    return "\n".join(keys[0:15])


@mcp.tool(
    title="美股关键指标",
    description="获取美股市场的股票财务报告关键指标",
)
def stock_indicators_us(
    symbol: str = field_symbol,
):
    dfs = ak_cache(ak.stock_financial_us_analysis_indicator_em, symbol=symbol, indicator="单季报")
    if dfs is None:
        return f"未获取到财务指标: {symbol}"
    if dfs.empty:
        return f"未获取到财务指标: {symbol}"
    keys = dfs.to_csv(index=False, float_format="%.3f").strip().split("\n")
    return "\n".join(keys[0:15])
