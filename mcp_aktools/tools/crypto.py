import json
import time
from typing import Any, Callable, cast

import pandas as pd
import requests
from fastmcp import Context
from pydantic import Field

from ..server import mcp
from ..shared.constants import BINANCE_BASE_URL, OKX_BASE_URL, USER_AGENT
from ..shared.indicators import add_technical_indicators


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Best-effort numeric parsing for exchange APIs.

    Some OKX endpoints may return empty strings for numeric fields.
    """

    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    """Best-effort int parsing for exchange APIs."""

    if value in (None, ""):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@mcp.tool(
    title="获取加密货币历史价格",
    description="获取OKX加密货币的历史K线数据，包括价格、交易量和技术指标",
)
def okx_prices(
    instId: str = Field("BTC-USDT", description="产品ID，格式: BTC-USDT"),
    bar: str = Field(
        "1H",
        description="K线时间粒度，仅支持: [1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/2D/3D/1W/1M/3M] 除分钟为小写m外,其余均为大写",
    ),
    limit: int = Field(100, description="返回数量(int)，最大300，最小建议30", strict=False),
):
    if not bar.endswith("m"):
        bar = bar.upper()
    res = requests.get(
        f"{OKX_BASE_URL}/api/v5/market/candles",
        params={
            "instId": instId,
            "bar": bar,
            "limit": max(300, limit + 62),
        },
        timeout=20,
    )
    data = res.json() or {}
    dfs = pd.DataFrame(data.get("data", []))
    if dfs.empty:
        return pd.DataFrame()
    dfs.columns = ["时间", "开盘", "最高", "最低", "收盘", "成交量", "成交额", "成交额USDT", "K线已完结"]
    dfs.sort_values("时间", inplace=True)
    dfs["时间"] = pd.to_numeric(dfs["时间"], errors="coerce")
    dfs["时间"] = pd.to_datetime(dfs["时间"], errors="coerce", unit="ms")
    dfs["开盘"] = pd.to_numeric(dfs["开盘"], errors="coerce")
    dfs["最高"] = pd.to_numeric(dfs["最高"], errors="coerce")
    dfs["最低"] = pd.to_numeric(dfs["最低"], errors="coerce")
    dfs["收盘"] = pd.to_numeric(dfs["收盘"], errors="coerce")
    dfs["成交量"] = pd.to_numeric(dfs["成交量"], errors="coerce")
    dfs["成交额"] = pd.to_numeric(dfs["成交额"], errors="coerce")
    add_technical_indicators(dfs, dfs["收盘"], dfs["最低"], dfs["最高"])
    columns = [
        "时间",
        "开盘",
        "收盘",
        "最高",
        "最低",
        "成交量",
        "成交额",
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
    all_lines = dfs.to_csv(columns=columns, index=False, float_format="%.2f").strip().split("\n")
    return "\n".join([all_lines[0], *all_lines[-limit:]])


@mcp.tool(
    title="获取加密货币杠杆多空比",
    description="获取OKX加密货币借入计价货币与借入交易货币的累计数额比值",
)
def okx_loan_ratios(
    symbol: str = Field("BTC", description="币种，格式: BTC 或 ETH"),
    period: str = Field("1h", description="时间粒度，仅支持: [5m/1H/1D] 注意大小写，仅分钟为小写m"),
):
    res = requests.get(
        f"{OKX_BASE_URL}/api/v5/rubik/stat/margin/loan-ratio",
        params={
            "ccy": symbol,
            "period": period,
        },
        timeout=20,
    )
    data = res.json() or {}
    dfs = pd.DataFrame(data.get("data", []))
    if dfs.empty:
        return pd.DataFrame()
    dfs.columns = ["时间", "多空比"]
    dfs["时间"] = pd.to_numeric(dfs["时间"], errors="coerce")
    dfs["时间"] = pd.to_datetime(dfs["时间"], errors="coerce", unit="ms")
    dfs["多空比"] = pd.to_numeric(dfs["多空比"], errors="coerce")
    return dfs.to_csv(index=False, float_format="%.2f").strip()


@mcp.tool(
    title="获取加密货币主动买卖情况",
    description="获取OKX加密货币主动买入和卖出的交易量",
)
def okx_taker_volume(
    symbol: str = Field("BTC", description="币种，格式: BTC 或 ETH"),
    period: str = Field("1h", description="时间粒度，仅支持: [5m/1H/1D] 注意大小写，仅分钟为小写m"),
    instType: str = Field("SPOT", description="产品类型 SPOT:现货 CONTRACTS:衍生品"),
):
    res = requests.get(
        f"{OKX_BASE_URL}/api/v5/rubik/stat/taker-volume",
        params={
            "ccy": symbol,
            "period": period,
            "instType": instType,
        },
        timeout=20,
    )
    data = res.json() or {}
    dfs = pd.DataFrame(data.get("data", []))
    if dfs.empty:
        return pd.DataFrame()
    dfs.columns = ["时间", "卖出量", "买入量"]
    dfs["时间"] = pd.to_numeric(dfs["时间"], errors="coerce")
    dfs["时间"] = pd.to_datetime(dfs["时间"], errors="coerce", unit="ms")
    dfs["卖出量"] = pd.to_numeric(dfs["卖出量"], errors="coerce")
    dfs["买入量"] = pd.to_numeric(dfs["买入量"], errors="coerce")
    return dfs.to_csv(index=False, float_format="%.2f").strip()


@mcp.tool(
    title="获取加密货币分析报告",
    description="获取币安对加密货币的AI分析报告，此工具对分析加密货币非常有用，推荐使用",
)
def binance_ai_report(
    symbol: str = Field("BTC", description="加密货币币种，格式: BTC 或 ETH"),
):
    res = requests.post(
        f"{BINANCE_BASE_URL}/bapi/bigdata/v3/friendly/bigdata/search/ai-report/report",
        json={
            "lang": "zh-CN",
            "token": symbol,
            "symbol": f"{symbol}USDT",
            "product": "web-spot",
            "timestamp": int(time.time() * 1000),
            "translateToken": None,
        },
        headers={
            "User-Agent": USER_AGENT,
            "Referer": f"https://www.binance.com/zh-CN/trade/{symbol}_USDT?type=spot",
            "lang": "zh-CN",
        },
        timeout=20,
    )
    try:
        resp = res.json() or {}
    except Exception:
        try:
            resp = json.loads(res.text.strip()) or {}
        except Exception:
            return res.text
    data = resp.get("data") or {}
    report = data.get("report") or {}
    translated = report.get("translated") or report.get("original") or {}
    modules = translated.get("modules") or []
    txts = []
    for module in modules:
        if tit := module.get("overview"):
            txts.append(tit)
        for point in module.get("points", []):
            txts.append(point.get("content", ""))
    return "\n".join(txts)


@mcp.tool(
    title="加密货币综合诊断",
    description="复合技能：一键获取加密货币技术面、情绪面和AI报告的综合诊断数据",
)
async def crypto_composite_diagnostic(
    symbol: str = Field("BTC", description="币种，格式: BTC 或 ETH"),
    ctx: Context | None = None,
):
    if ctx:
        await ctx.report_progress(0, 100, "开始加密货币诊断...")

    inst_id = f"{symbol}-USDT"
    okx_prices_fn = cast(Callable[..., str], okx_prices)
    okx_loan_fn = cast(Callable[..., str], okx_loan_ratios)
    okx_taker_fn = cast(Callable[..., str], okx_taker_volume)
    binance_fn = cast(Callable[..., str], binance_ai_report)

    if ctx:
        await ctx.report_progress(25, 100, "获取价格数据...")
    price_data = okx_prices_fn(instId=inst_id, bar="4H", limit=10)

    if ctx:
        await ctx.report_progress(50, 100, "获取杠杆多空比...")
    loan_data = okx_loan_fn(symbol=symbol, period="1H")

    if ctx:
        await ctx.report_progress(75, 100, "获取主动买卖量...")
    taker_data = okx_taker_fn(symbol=symbol, period="1H", instType="SPOT")
    ai_report = binance_fn(symbol=symbol)

    if ctx:
        await ctx.report_progress(100, 100, "诊断完成")

    return (
        f"--- 加密货币综合诊断: {symbol} ---\n\n"
        f"[近期价格 4H]\n{price_data}\n\n"
        f"[杠杆多空比]\n{loan_data}\n\n"
        f"[主动买卖量]\n{taker_data}\n\n"
        f"[币安AI报告]\n{ai_report}"
    )


@mcp.tool(
    title="加密货币走势图",
    description="生成加密货币的 ASCII 走势图，用于直观展示趋势",
)
def draw_crypto_chart(
    symbol: str = Field("BTC", description="币种，格式: BTC 或 ETH"),
    bar: str = Field("1D", description="K线周期: 1H/4H/1D"),
):
    inst_id = f"{symbol}-USDT"
    okx_prices_fn = cast(Callable[..., str], okx_prices)
    data = okx_prices_fn(instId=inst_id, bar=bar, limit=20)
    if not data or isinstance(data, pd.DataFrame):
        return "数据不足，无法绘图"

    lines = data.strip().split("\n")[1:]
    if not lines:
        return "数据不足，无法绘图"

    prices = []
    for line in lines:
        parts = line.split(",")
        if len(parts) >= 3:
            try:
                prices.append(float(parts[2]))
            except ValueError:
                continue

    if len(prices) < 3:
        return "数据不足，无法绘图"

    min_p, max_p = min(prices), max(prices)
    rng = max_p - min_p or 1
    height = 5
    chart = []

    for h in range(height, -1, -1):
        row = []
        threshold = min_p + (h / height) * rng
        for p in prices:
            row.append("█" if p >= threshold else " ")
        chart.append("".join(row))

    return (
        f"\n{symbol} 最近 {len(prices)} 根 {bar} K线走势:\n"
        + "\n".join(chart)
        + f"\n最低: {min_p:.2f}  最高: {max_p:.2f}"
    )


@mcp.tool(
    title="加密货币策略回测",
    description="基于加密货币历史价格与技术指标进行简单策略回测（SMA/RSI/MACD）",
)
def backtest_crypto_strategy(
    symbol: str = Field("BTC", description="币种，格式: BTC 或 ETH"),
    strategy: str = Field("SMA", description="策略类型: SMA/RSI/MACD"),
    bar: str = Field("4H", description="K线周期: 1H/4H/1D"),
    limit: int = Field(200, description="回测K线数量", strict=False),
):
    from io import StringIO

    inst_id = f"{symbol}-USDT"
    okx_prices_fn = cast(Callable[..., str], okx_prices)
    data = okx_prices_fn(instId=inst_id, bar=bar, limit=limit)

    if not data or not isinstance(data, str):
        return f"未找到可回测数据: {symbol}"

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
        short_window, long_window = 5, 20
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
    win_rate = (active > 0).mean() if len(active) > 0 else None

    start_time = str(dfs["时间"].iloc[0]) if "时间" in dfs.columns else "-"
    end_time = str(dfs["时间"].iloc[-1]) if "时间" in dfs.columns else "-"
    win_text = f"{win_rate:.2%}" if win_rate is not None else "N/A"

    return (
        f"--- 加密货币策略回测: {symbol} ---\n"
        f"策略: {strategy_desc}\n"
        f"周期: {bar} (样本 {len(dfs)} 根K线)\n"
        f"区间: {start_time} ~ {end_time}\n"
        f"累计收益: {cumulative_return:.2%}\n"
        f"最大回撤: {max_drawdown:.2%}\n"
        f"胜率: {win_text}"
    )


@mcp.tool(
    title="获取资金费率",
    description="获取OKX永续合约的资金费率，正费率表示多头付费给空头，负费率反之",
)
def okx_funding_rate(
    symbol: str = Field("BTC", description="币种，格式: BTC 或 ETH"),
):
    inst_id = f"{symbol}-USDT-SWAP"
    res = requests.get(
        f"{OKX_BASE_URL}/api/v5/public/funding-rate",
        params={"instId": inst_id},
        timeout=20,
    )
    data = res.json() or {}
    items = data.get("data", [])
    if not items:
        return f"未找到 {symbol} 的资金费率数据"

    item = items[0]
    current_rate = _safe_float(item.get("fundingRate")) * 100
    next_rate = _safe_float(item.get("nextFundingRate")) * 100
    funding_ts = _safe_int(item.get("fundingTime"))
    funding_time = pd.to_datetime(funding_ts, unit="ms") if funding_ts else "N/A"

    sentiment = "多头拥挤" if current_rate > 0.05 else "空头占优" if current_rate < -0.05 else "中性"

    return (
        f"--- {symbol} 资金费率 ---\n"
        f"当前费率: {current_rate:.4f}%\n"
        f"预测费率: {next_rate:.4f}%\n"
        f"结算时间: {funding_time}\n"
        f"市场情绪: {sentiment}"
    )


@mcp.tool(
    title="获取合约持仓量",
    description="获取OKX永续合约的持仓量数据，用于判断市场资金流向",
)
def okx_open_interest(
    symbol: str = Field("BTC", description="币种，格式: BTC 或 ETH"),
):
    inst_id = f"{symbol}-USDT-SWAP"
    res = requests.get(
        f"{OKX_BASE_URL}/api/v5/public/open-interest",
        params={"instId": inst_id},
        timeout=20,
    )
    data = res.json() or {}
    items = data.get("data", [])
    if not items:
        return f"未找到 {symbol} 的持仓量数据"

    item = items[0]
    oi = float(item.get("oi", 0))
    oi_ccy = float(item.get("oiCcy", 0))
    ts = pd.to_datetime(int(item.get("ts", 0)), unit="ms")

    return f"--- {symbol} 合约持仓量 ---\n持仓量(张): {oi:,.0f}\n持仓量(币): {oi_ccy:,.2f} {symbol}\n更新时间: {ts}"


@mcp.tool(
    title="获取恐惧贪婪指数",
    description="获取加密货币市场恐惧贪婪指数(0-100)，0为极度恐惧，100为极度贪婪",
)
def fear_greed_index():
    res = requests.get(
        "https://api.alternative.me/fng/",
        params={"limit": 7},
        timeout=20,
    )
    data = res.json() or {}
    items = data.get("data", [])
    if not items:
        return "未能获取恐惧贪婪指数"

    current = items[0]
    value = int(current.get("value", 0))
    classification = current.get("value_classification", "")
    ts = pd.to_datetime(int(current.get("timestamp", 0)), unit="s")

    lines = [
        "--- 加密货币恐惧贪婪指数 ---",
        f"当前指数: {value} ({classification})",
        f"更新时间: {ts}",
        "",
        "近7日趋势:",
    ]
    for item in items:
        v = item.get("value", "")
        c = item.get("value_classification", "")
        lines.append(f"  {v} - {c}")

    return "\n".join(lines)
