"""贵金属数据工具模块"""

from typing import Callable, cast

import akshare as ak
import pandas as pd
from fastmcp import Context
from pydantic import Field

from mcp_aktools.server import mcp
from mcp_aktools.shared.indicators import add_technical_indicators
from mcp_aktools.shared.utils import ak_cache

# 上海金交所品种映射
SGE_SYMBOLS = {
    "Au99.99": "黄金9999",
    "Au99.95": "黄金9995",
    "Au(T+D)": "黄金T+D",
    "Ag99.99": "白银9999",
    "Ag(T+D)": "白银T+D",
}

# 国际品种映射
INTL_SYMBOLS = {
    "XAU": "伦敦金",
    "XAG": "伦敦银",
    "GC": "COMEX黄金",
    "SI": "COMEX白银",
}


@mcp.tool(
    title="获取上海金交所现货价格",
    description="获取上海黄金交易所现货历史价格数据，包括黄金、白银等品种的价格走势和技术指标",
)
def pm_spot_prices(
    symbol: str = Field(
        "Au99.99",
        description="品种代码，支持: Au99.99(黄金9999), Au99.95(黄金9995), Au(T+D)(黄金T+D), Ag99.99(白银9999), Ag(T+D)(白银T+D)",
    ),
    limit: int = Field(30, description="返回数量(int)，建议30-252", strict=False),
):
    """获取上海金交所现货历史价格"""
    df = ak_cache(ak.spot_hist_sge, symbol=symbol)
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.tail(limit + 62)
    df.sort_values("日期", inplace=True)
    df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
    df["开盘价"] = pd.to_numeric(df["开盘价"], errors="coerce")
    df["最高价"] = pd.to_numeric(df["最高价"], errors="coerce")
    df["最低价"] = pd.to_numeric(df["最低价"], errors="coerce")
    df["收盘价"] = pd.to_numeric(df["收盘价"], errors="coerce")
    df["成交量"] = pd.to_numeric(df["成交量"], errors="coerce")

    add_technical_indicators(df, df["收盘价"], df["最低价"], df["最高价"])

    columns = [
        "日期",
        "开盘价",
        "收盘价",
        "最高价",
        "最低价",
        "成交量",
        "MACD",
        "DIF",
        "DEA",
        "KDJ.K",
        "KDJ.D",
        "KDJ.J",
        "RSI",
        "BOLL.U",
        "BOLL.M",
        "BOLL.L",
    ]
    all_lines = df.to_csv(columns=columns, index=False, float_format="%.2f").strip().split("\n")
    return "\n".join([all_lines[0], *all_lines[-limit:]])


@mcp.tool(
    title="获取国际贵金属价格",
    description="获取国际贵金属实时价格，包括伦敦金、伦敦银、COMEX黄金、COMEX白银等",
)
def pm_international_prices(
    symbol: str = Field("XAU", description="品种代码，支持: XAU(伦敦金), XAG(伦敦银), GC(COMEX黄金), SI(COMEX白银)"),
):
    """获取国际贵金属实时价格"""
    df = ak_cache(ak.futures_foreign_commodity_realtime, symbol=symbol, ttl=300)
    if df is None or df.empty:
        return pd.DataFrame()

    return df.to_csv(index=False, float_format="%.2f")


@mcp.tool(
    title="获取贵金属ETF持仓变化",
    description="获取全球黄金或白银ETF持仓量变化数据，用于判断机构资金流向",
)
def pm_etf_holdings(
    metal: str = Field("gold", description="金属类型，支持: gold(黄金), silver(白银)"),
    limit: int = Field(30, description="返回数量(int)，建议30-90", strict=False),
):
    """获取贵金属ETF持仓变化"""
    if metal.lower() == "gold":
        df = ak_cache(ak.macro_cons_gold)
    elif metal.lower() == "silver":
        df = ak_cache(ak.macro_cons_silver)
    else:
        return "不支持的金属类型，仅支持: gold, silver"

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.tail(limit)
    return df.to_csv(index=False, float_format="%.2f")


@mcp.tool(
    title="获取COMEX库存数据",
    description="获取COMEX交易所黄金或白银库存数据，用于判断供需关系",
)
def pm_comex_inventory(
    metal: str = Field("黄金", description="金属类型，支持: 黄金, 白银"),
    limit: int = Field(30, description="返回数量(int)，建议30-90", strict=False),
):
    """获取COMEX库存数据"""
    df = ak_cache(ak.futures_comex_inventory, symbol=metal)
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.tail(limit)
    return df.to_csv(index=False, float_format="%.2f")


@mcp.tool(
    title="获取贵金属期现基差",
    description="获取贵金属期货与现货价格的基差数据，用于判断市场预期和套利机会",
)
def pm_basis(
    metal: str = Field("黄金", description="金属类型，支持: 黄金, 白银"),
):
    """获取贵金属期现基差"""
    df = ak_cache(ak.futures_spot_price, vars_list=[metal])
    if df is None or df.empty:
        return pd.DataFrame()

    return df.to_csv(index=False, float_format="%.2f")


@mcp.tool(
    title="获取上海金银基准价",
    description="获取上海黄金交易所发布的黄金或白银基准价格，这是国内贵金属定价的重要参考",
)
def pm_benchmark_price(
    metal: str = Field("gold", description="金属类型，支持: gold(黄金), silver(白银)"),
    limit: int = Field(30, description="返回数量(int)，建议30-90", strict=False),
):
    """获取上海金银基准价"""
    if metal.lower() == "gold":
        df = ak_cache(ak.spot_golden_benchmark_sge)
    elif metal.lower() == "silver":
        df = ak_cache(ak.spot_silver_benchmark_sge)
    else:
        return "不支持的金属类型，仅支持: gold, silver"

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.tail(limit)
    return df.to_csv(index=False, float_format="%.2f")


@mcp.tool(
    title="贵金属综合诊断",
    description="复合技能：一键获取贵金属的价格走势、ETF持仓、COMEX库存、期现基差等综合诊断数据",
)
async def pm_composite_diagnostic(
    metal: str = Field("gold", description="金属类型，支持: gold(黄金), silver(白银)"),
    ctx: Context | None = None,
):
    """贵金属综合诊断"""
    if ctx:
        await ctx.report_progress(0, 100, "开始贵金属综合诊断...")

    # 确定品种代码
    if metal.lower() == "gold":
        sge_symbol = "Au99.99"
        intl_symbol = "XAU"
        metal_cn = "黄金"
    elif metal.lower() == "silver":
        sge_symbol = "Ag99.99"
        intl_symbol = "XAG"
        metal_cn = "白银"
    else:
        return "不支持的金属类型，仅支持: gold, silver"

    # 调用各个工具函数
    pm_spot_fn = cast(Callable[..., str], pm_spot_prices)
    pm_intl_fn = cast(Callable[..., str], pm_international_prices)
    pm_etf_fn = cast(Callable[..., str], pm_etf_holdings)
    pm_comex_fn = cast(Callable[..., str], pm_comex_inventory)
    pm_basis_fn = cast(Callable[..., str], pm_basis)
    pm_benchmark_fn = cast(Callable[..., str], pm_benchmark_price)

    if ctx:
        await ctx.report_progress(15, 100, "获取现货价格...")
    spot_data = pm_spot_fn(symbol=sge_symbol, limit=10)

    if ctx:
        await ctx.report_progress(30, 100, "获取国际价格...")
    intl_data = pm_intl_fn(symbol=intl_symbol)

    if ctx:
        await ctx.report_progress(45, 100, "获取ETF持仓...")
    etf_data = pm_etf_fn(metal=metal, limit=10)

    if ctx:
        await ctx.report_progress(60, 100, "获取COMEX库存...")
    comex_data = pm_comex_fn(metal=metal_cn, limit=10)

    if ctx:
        await ctx.report_progress(75, 100, "获取期现基差...")
    basis_data = pm_basis_fn(metal=metal_cn)

    if ctx:
        await ctx.report_progress(90, 100, "获取基准价格...")
    benchmark_data = pm_benchmark_fn(metal=metal, limit=10)

    if ctx:
        await ctx.report_progress(100, 100, "诊断完成")

    return (
        f"--- 贵金属综合诊断: {metal_cn} ---\n\n"
        f"[上海金交所现货价格]\n{spot_data}\n\n"
        f"[国际市场价格]\n{intl_data}\n\n"
        f"[ETF持仓变化]\n{etf_data}\n\n"
        f"[COMEX库存]\n{comex_data}\n\n"
        f"[期现基差]\n{basis_data}\n\n"
        f"[上海基准价]\n{benchmark_data}"
    )
