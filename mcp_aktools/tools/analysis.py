from io import StringIO
from typing import Callable, cast

import pandas as pd
from fastmcp import Context
from pydantic import Field

from ..server import mcp
from ..shared.fields import field_market, field_symbol
from .stocks import stock_info, stock_news, stock_prices


@mcp.tool(
    title="个股综合诊断",
    description="复合技能：一键获取技术面、基本面和消息面的综合诊断数据",
)
async def composite_stock_diagnostic(
    symbol: str = field_symbol,
    market: str = field_market,
    ctx: Context | None = None,
):
    if ctx:
        await ctx.report_progress(0, 100, "开始综合诊断...")

    # 内部组合调用
    stock_prices_fn = cast(Callable[..., str], stock_prices)
    stock_info_fn = cast(Callable[..., str], stock_info)
    stock_news_fn = cast(Callable[..., str], stock_news)

    if ctx:
        await ctx.report_progress(20, 100, "获取历史价格...")
    price_data = stock_prices_fn(symbol, market, limit=5)

    if ctx:
        await ctx.report_progress(40, 100, "获取基本面信息...")
    fundamental = stock_info_fn(symbol, market)

    if ctx:
        await ctx.report_progress(60, 100, "获取新闻动态...")
    news = stock_news_fn(symbol, limit=3)

    if ctx:
        await ctx.report_progress(80, 100, "汇总分析结果...")

    result = (
        f"--- 综合诊断报告: {symbol} ---\n\n[近期价格]\n{price_data}\n\n[基本面]\n{fundamental}\n\n[核心新闻]\n{news}"
    )

    if ctx:
        await ctx.report_progress(100, 100, "诊断完成")

    return result


@mcp.tool(
    title="生成走势字符图",
    description="根据提供的价格列表生成一个简单的 ASCII 走势图，用于直观展示趋势",
)
def draw_ascii_chart(symbol: str = field_symbol, market: str = field_market):
    stock_prices_fn = cast(Callable[..., str], stock_prices)
    data = stock_prices_fn(symbol, market, limit=20)
    lines = data.strip().split("\n")[1:]  # 跳过表头
    prices = [float(l.split(",")[2]) for l in lines]  # 取收盘价

    if not prices:
        return "数据不足，无法绘图"

    min_p, max_p = min(prices), max(prices)
    rng = max_p - min_p or 1
    height = 5
    chart = []

    for h in range(height, -1, -1):
        row = []
        threshold = min_p + (h / height) * rng
        for p in prices:
            if p >= threshold:
                row.append("📈" if h == height else "█")
            else:
                row.append("  ")
        chart.append("".join(row))

    return f"\n{symbol} 最近 20 日走势图:\n" + "\n".join(chart) + f"\n最低: {min_p:.2f}  最高: {max_p:.2f}"


@mcp.tool(
    title="策略回测",
    description="基于历史价格与技术指标进行简单策略回测（SMA/RSI/MACD）",
)
def backtest_strategy(
    symbol: str = field_symbol,
    market: str = field_market,
    strategy: str = Field("SMA", description="策略类型: SMA/RSI/MACD"),
    days: int = Field(252, description="回测天数"),
):
    stock_prices_fn = cast(Callable[..., str], stock_prices)
    data = stock_prices_fn(symbol=symbol, market=market, limit=days)
    if not data or data.startswith("Not Found"):
        return f"未找到可回测数据: {symbol}.{market}"

    try:
        dfs = pd.read_csv(StringIO(data))
    except Exception:
        return "价格数据解析失败"

    if dfs is None or dfs.empty or "收盘" not in dfs.columns:
        return "数据不足，无法回测"

    close = pd.to_numeric(dfs["收盘"], errors="coerce")
    dfs = dfs.assign(收盘=close).dropna(subset=["收盘"])
    if dfs.empty:
        return "数据不足，无法回测"

    strategy_key = (strategy or "").strip().upper()
    if strategy_key == "SMA":
        short_window = 5
        long_window = 20
        dfs["ma_short"] = dfs["收盘"].rolling(short_window).mean()
        dfs["ma_long"] = dfs["收盘"].rolling(long_window).mean()
        signal = pd.Series((dfs["ma_short"] > dfs["ma_long"]).astype(int), index=dfs.index)
        strategy_desc = f"SMA{short_window}/{long_window}"
    elif strategy_key == "RSI":
        if "RSI" not in dfs.columns:
            return "数据缺少 RSI 指标，无法回测"
        rsi = pd.Series(pd.to_numeric(dfs["RSI"], errors="coerce"), index=dfs.index)
        positions = []
        position = 0
        for value in rsi.to_list():
            if pd.isna(value):
                positions.append(position)
                continue
            if value < 30:
                position = 1
            elif value > 70:
                position = 0
            positions.append(position)
        signal = pd.Series(positions, index=dfs.index)
        strategy_desc = "RSI(30/70)"
    elif strategy_key == "MACD":
        if "DIF" not in dfs.columns or "DEA" not in dfs.columns:
            return "数据缺少 MACD 指标，无法回测"
        dif = pd.Series(pd.to_numeric(dfs["DIF"], errors="coerce"), index=dfs.index)
        dea = pd.Series(pd.to_numeric(dfs["DEA"], errors="coerce"), index=dfs.index)
        signal = pd.Series((dif > dea).astype(int), index=dfs.index)
        strategy_desc = "MACD(DIF/DEA)"
    else:
        return f"不支持的策略类型: {strategy}"

    returns = dfs["收盘"].pct_change().fillna(0)
    position = signal.shift(1).fillna(0)
    strat_returns = returns.mul(position)
    equity = (1 + strat_returns).cumprod()
    cumulative_return = equity.iloc[-1] - 1
    drawdown = equity / equity.cummax() - 1
    max_drawdown = drawdown.min()

    active = strat_returns[strat_returns != 0]
    win_rate = (active > 0).mean() if not active.empty else None

    start_date = str(dfs["日期"].iloc[0]) if "日期" in dfs.columns else "-"
    end_date = str(dfs["日期"].iloc[-1]) if "日期" in dfs.columns else "-"
    win_text = f"{win_rate:.2%}" if win_rate is not None else "N/A"
    return (
        f"--- 策略回测: {symbol} ({market}) ---\n"
        f"策略: {strategy_desc}\n"
        f"区间: {start_date} ~ {end_date} (样本 {len(dfs)} 日)\n"
        f"累计收益: {cumulative_return:.2%}\n"
        f"最大回撤: {max_drawdown:.2%}\n"
        f"胜率: {win_text}"
    )


@mcp.tool(
    title="给出投资建议",
    description="基于AI对其他工具提供的数据分析结果给出具体投资建议",
)
def trading_suggest(
    symbol: str = Field(description="股票代码或加密币种"),
    action: str = Field(description="推荐操作: buy/sell/hold"),
    score: int = Field(description="置信度，范围: 0-100"),
    reason: str = Field(description="推荐理由"),
):
    return {
        "symbol": symbol,
        "action": action,
        "score": score,
        "reason": reason,
    }
