from .server import mcp


@mcp.prompt("analyze-stock")
def prompt_analyze_stock(symbol: str):
    """一键触发全方位的个股深度分析技能"""
    return f"""
    你现在是一名资深证券分析师。请针对股票 {symbol} 执行以下深度分析技能：
    1. 获取当前时间确认市场状态。
    2. 使用 `stock_prices` 获取最近 30 天的日线数据，分析 MACD 和布林带走势。
    3. 调用 `stock_indicators` 获取财务摘要，判断基本面。
    4. 检索 `stock_news` 获取最近的新闻动态。
    5. 最后，结合 `skill://trading/logic/technical-analysis` 中的 SOP 给出你的专业评价。
    """


@mcp.prompt("market-pulse")
def prompt_market_pulse():
    """分析当前 A 股大盘整体脉搏"""
    return """
    作为市场观察员，请执行以下技能：
    1. 检查 `stock_zt_pool_em` 看涨停家数和市场高度。
    2. 检查 `stock_sector_fund_flow_rank` 找出今日领涨板块。
    3. 结合龙虎榜 `stock_lhb_ggtj_sina` 分析机构动向。
    请总结当前市场是处于"进攻"、"防守"还是"观望"状态。
    """


@mcp.prompt("analyze-crypto")
def prompt_analyze_crypto(symbol: str):
    """一键触发全方位的加密货币深度分析技能"""
    return f"""
    你现在是一名资深加密货币分析师。请针对币种 {symbol} 执行以下深度分析技能：
    1. 使用 `okx_prices` 获取最近 100 根 4H K线数据，分析 MACD、RSI 和布林带走势。
    2. 调用 `okx_loan_ratios` 获取杠杆多空比，判断市场情绪偏向。
    3. 调用 `okx_taker_volume` 获取主动买卖量，分析资金流向。
    4. 使用 `binance_ai_report` 获取币安 AI 深度报告作为参考。
    5. 最后，结合 `skill://crypto/logic/analysis-sop` 中的 SOP 给出你的专业评价和操作建议。
    """


@mcp.prompt("crypto-pulse")
def prompt_crypto_pulse():
    """分析当前加密货币市场整体脉搏"""
    return """
    作为加密货币市场观察员，请执行以下技能：
    1. 使用 `fear_greed_index` 获取市场恐惧贪婪指数，判断整体情绪。
    2. 使用 `okx_funding_rate` 获取 BTC 和 ETH 的资金费率，判断多空力量。
    3. 使用 `okx_open_interest` 获取 BTC 和 ETH 的持仓量，分析资金规模。
    4. 使用 `okx_prices` 获取 BTC-USDT 的 1D K线，判断大盘趋势。
    5. 调用 `binance_ai_report` 获取 BTC 的 AI 分析报告。
    请总结当前加密货币市场是处于"牛市"、"熊市"还是"震荡"状态，并给出风险提示。
    """


@mcp.prompt("analyze-precious-metal")
def prompt_analyze_precious_metal(metal: str):
    """一键触发贵金属深度分析技能"""
    return f"""
    你现在是一名资深贵金属分析师。请针对 {metal} 执行以下深度分析：
    1. 使用 `pm_spot_prices` 获取近30日现货价格，分析技术走势。
    2. 使用 `pm_international_prices` 获取国际价格，对比内外盘价差。
    3. 使用 `pm_etf_holdings` 获取ETF持仓变化，判断机构动向。
    4. 使用 `pm_comex_inventory` 获取COMEX库存，分析实物需求。
    5. 使用 `pm_basis` 获取期现基差，判断市场预期。
    6. 结合 `skill://trading/logic/precious-metals-analysis` 给出专业评价。
    """


@mcp.prompt("precious-metal-pulse")
def prompt_precious_metal_pulse():
    """分析贵金属市场整体脉搏"""
    return """
    作为贵金属市场观察员，请执行以下技能：
    1. 使用 `pm_international_prices` 获取伦敦金(XAU)和伦敦银(XAG)价格。
    2. 使用 `pm_etf_holdings` 对比黄金和白银ETF持仓变化。
    3. 使用 `pm_comex_inventory` 分析COMEX库存趋势。
    4. 使用 `pm_benchmark_price` 获取上海金/银基准价。
    请总结当前贵金属市场是处于"避险升温"、"回调整理"还是"趋势延续"状态。
    """
