from datetime import datetime
from io import StringIO

import pandas as pd
from pydantic import Field

from ..server import mcp
from ..shared.fields import field_market
from ..shared.utils import load_portfolio, save_portfolio
from .stocks import market_prices


@mcp.tool(
    title="添加持仓记录",
    description="在模拟盘中添加一笔持仓记录，用于后续跟踪盈亏",
)
def portfolio_add(
    symbol: str = Field(description="股票或币种代码"),
    price: float = Field(description="买入价格"),
    volume: float = Field(description="买入数量"),
    market: str = field_market,
):
    p = load_portfolio()
    p[f"{symbol}.{market}"] = {
        "symbol": symbol,
        "price": price,
        "volume": volume,
        "market": market,
        "time": datetime.now().isoformat(),
    }
    save_portfolio(p)
    return f"成功添加持仓: {symbol}, 价格: {price}"


@mcp.tool(
    title="查看模拟盘盈亏",
    description="计算当前所有模拟持仓的实时盈亏情况",
)
def portfolio_view():
    p = load_portfolio()
    if not p:
        return "当前模拟盘为空"
    results = []
    for k, v in p.items():
        try:
            prices = market_prices.fn(v["symbol"], v["market"], limit=1)
            df = pd.read_csv(StringIO(prices))
            current_price = float(df["close"].iloc[-1])
            profit = (current_price - v["price"]) * v["volume"]
            ratio = (current_price / v["price"] - 1) * 100
            results.append(
                f"{k}: 成本 {v['price']:.2f} -> 现价 {current_price:.2f} | 盈亏 {profit:+.2f} ({ratio:+.2f}%)"
            )
        except Exception:
            results.append(f"{k}: 成本 {v['price']:.2f} (无法获取实时现价)")
    return "\n".join(results)


@mcp.tool(
    title="持仓盈亏图表",
    description="生成持仓盈亏的 ASCII 柱状图，直观展示各持仓盈亏情况",
)
def portfolio_chart():
    p = load_portfolio()
    if not p:
        return "当前模拟盘为空，无法生成图表"

    holdings = []
    for k, v in p.items():
        try:
            prices = market_prices.fn(v["symbol"], v["market"], limit=1)
            df = pd.read_csv(StringIO(prices))
            current_price = float(df["close"].iloc[-1])
            ratio = (current_price / v["price"] - 1) * 100
            holdings.append({"name": k, "ratio": ratio})
        except Exception:
            holdings.append({"name": k, "ratio": 0.0})

    if not holdings:
        return "无有效持仓数据"

    max_ratio = max(abs(h["ratio"]) for h in holdings) or 1
    bar_width = 20

    lines = ["--- 持仓盈亏图表 ---", ""]
    for h in holdings:
        ratio = h["ratio"]
        bar_len = int(abs(ratio) / max_ratio * bar_width)
        if ratio >= 0:
            bar = "█" * bar_len
            line = f"{h['name']:>15} | {bar:<{bar_width}} | +{ratio:.2f}%"
        else:
            bar = "█" * bar_len
            line = f"{h['name']:>15} | {' ' * (bar_width - bar_len)}{bar} | {ratio:.2f}%"
        lines.append(line)

    lines.append("")
    lines.append(f"最大波动: ±{max_ratio:.2f}%")
    return "\n".join(lines)
