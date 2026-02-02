from .server import mcp


@mcp.resource("skill://trading/logic/technical-analysis")
def resource_tech_analysis():
    """提供技术指标解读技能"""
    return """
    技术指标解读 SOP:
    - MACD: DIF > DEA 且 MACD 柱变长为多头强势；死叉则需警惕。
    - RSI: > 70 为超买，< 30 为超卖。
    - BOLL: 价格触及上轨且缩口表示压力，触及下轨且缩口表示支撑。
    - KDJ: J 线拐头通常是短期转折信号。
    """


@mcp.resource("skill://trading/strategy/risk-management")
def resource_risk_management():
    """提供风险管理技能"""
    return """
    风险管理原则:
    - 单笔交易止损不应超过总资金的 2%。
    - 建议在波动率（ATR）较高时缩小仓位。
    - 严禁在市场关闭前 15 分钟进行无计划的追涨。
    """


@mcp.resource("skill://crypto/logic/analysis-sop")
def resource_crypto_analysis():
    """提供加密货币分析SOP"""
    return """
    加密货币分析 SOP:
    - 多空比: > 1.5 表示多头情绪过热需警惕回调; < 0.7 表示空头占优可能超卖。
    - 主动买卖: 买入量持续 > 卖出量为资金流入信号; 反之为流出。
    - MACD: 4H级别金叉配合放量为短期做多信号; 死叉需减仓。
    - RSI: 加密货币波动大，建议用 80/20 作为超买超卖阈值。
    - 资金费率: 正费率过高(>0.1%)表示多头拥挤; 负费率表示空头占优。
    - 风险提示: 加密货币24小时交易，注意设置止损，避免爆仓。
    """


@mcp.resource("skill://trading/logic/precious-metals-analysis")
def resource_pm_analysis():
    """提供贵金属分析SOP"""
    return """
    贵金属分析 SOP:

    1. 价格趋势判断:
       - 上海金交所现货价格为国内定价基准
       - 伦敦金(XAU)为国际定价基准
       - 内外盘溢价 > 2% 表示国内需求强劲
    - 内外盘折价 > 2% 表示国内抛压较大

    2. 资金流向判断:
       - ETF持仓连续增加 → 机构看多，趋势延续
       - ETF持仓连续减少 → 机构看空，注意风险
       - COMEX库存下降 → 实物需求强劲，利多
    - COMEX库存上升 → 实物需求疲软，利空

    3. 期现基差解读:
       - 正基差(期货>现货) → 市场预期上涨(Contango)
       - 负基差(期货<现货) → 现货紧缺或预期下跌(Backwardation)
    - 基差扩大 → 套利空间增加

    4. 避险情绪指标:
       - 美元指数走弱 → 利多黄金
       - 实际利率下降 → 利多黄金
       - 地缘风险上升 → 利多黄金
    - VIX恐慌指数上升 → 利多黄金
    5. 金银比价:
       - 金银比 > 80 → 白银相对低估，可关注白银
       - 金银比 < 60 → 白银相对高估，可关注黄金
    """


@mcp.resource("stock://{symbol}/analysis")
def stock_dynamic_analysis(symbol: str) -> str:
    """动态生成某只股票的专属分析指南"""
    return f"""
# {symbol} 专属分析建议

## 推荐工具链
1. `market_prices(symbol="{symbol}", limit=30)` - 获取近期走势
2. `stock_news(symbol="{symbol}", limit=5)` - 获取相关新闻
3. `draw_ascii_chart(symbol="{symbol}")` - 可视化趋势
4. `stock_indicators_a(symbol="{symbol}")` - 财务指标

## 关键指标关注
- MACD 金叉/死叉信号
- RSI 超买(>70)/超卖(<30)
- 布林带突破
- 成交量异常放大

## 分析流程
1. 先用 market_prices 获取技术面数据
2. 用 stock_indicators 获取基本面数据
3. 用 stock_news 获取消息面
4. 综合三者给出判断
"""


@mcp.resource("market://{sector}/flow")
def sector_flow_guide(sector: str) -> str:
    """板块资金流向分析指南"""
    return f"""
# {sector} 板块资金流向分析

## 推荐工具
1. `stock_sector_fund_flow_rank(cate="行业资金流")` - 获取行业资金流向
2. `stock_zt_pool_em()` - 查看板块涨停股
3. `northbound_funds()` - 北向资金动向

## 分析要点
- 主力净流入 > 0 表示资金看好
- 连续3日净流入为强势信号
- 结合北向资金判断外资态度
- 涨停股数量反映板块热度

## 操作建议
1. 先用 stock_sector_fund_flow_rank 查看整体资金流向
2. 用 stock_zt_pool_em 找出板块龙头
3. 用 northbound_funds 确认外资态度
4. 综合判断板块强弱
"""


@mcp.resource("crypto://{symbol}/analysis")
def crypto_dynamic_analysis(symbol: str) -> str:
    """动态生成某个加密货币的专属分析指南"""
    return f"""
# {symbol} 加密货币分析指南

## 推荐工具链
1. `crypto_prices(symbol="{symbol}-USDT", period="4H", limit=30)` - 获取K线数据
2. `crypto_sentiment_metrics(symbol="{symbol}")` - 情绪指标
4. `okx_funding_rate(symbol="{symbol}")` - 资金费率
5. `okx_open_interest(symbol="{symbol}")` - 合约持仓量
6. `binance_ai_report(symbol="{symbol}")` - AI研报
6. `draw_crypto_chart(symbol="{symbol}")` - 可视化走势
7. `crypto_composite_diagnostic(symbol="{symbol}")` - 综合诊断

## 关键指标关注
- 多空比 > 1.5 表示多头过热，需警惕回调
- 多空比 < 0.7 表示空头占优，可能超卖
- 资金费率 > 0.1% 表示多头拥挤
- 资金费率 < -0.1% 表示空头占优
- 持仓量持续增加配合价格上涨为强势信号

## 分析流程
1. 先用 crypto_composite_diagnostic 获取全面数据
2. 用 binance_ai_report 获取AI深度分析
3. 用 fear_greed_index 判断市场情绪
4. 综合给出操作建议
"""


@mcp.resource("pm://{metal}/analysis")
def pm_dynamic_analysis(metal: str) -> str:
    """动态生成贵金属分析指南"""
    metal_name = "黄金" if metal.lower() in ("gold", "au") else "白银"
    symbol = "Au99.99" if metal.lower() in ("gold", "au") else "Ag99.99"
    return f"""
# {metal_name} 分析指南

## 推荐工具链
1. `pm_spot_prices(symbol="{symbol}", limit=30)` - 国内现货价格
2. `pm_international_prices(symbol="XAU")` - 国际价格
3. `pm_etf_holdings(metal="{metal}")` - ETF持仓变化
4. `pm_comex_inventory(metal="{metal_name}")` - COMEX库存
5. `pm_basis(metal="{metal_name}")` - 期现基差
6. `pm_benchmark_price(metal="{metal}")` - 基准价格
7. `pm_composite_diagnostic(metal="{metal}")` - 综合诊断

## 关键指标关注
- ETF持仓连续增加 → 机构看多
- ETF持仓连续减少 → 机构看空
- COMEX库存下降 → 实物需求强劲
- 正基差(期货>现货) → 市场预期上涨
- 负基差(期货<现货) → 现货紧缺

## 分析流程
1. 先用 pm_composite_diagnostic 获取全面数据
2. 关注内外盘价差判断套利空间
3. 结合ETF持仓和库存判断资金流向
4. 综合给出操作建议
"""


@mcp.resource("fund://{code}/analysis")
def fund_dynamic_analysis(code: str) -> str:
    """动态生成基金分析指南"""
    return f"""
# 基金 {code} 分析指南

## 推荐工具链
1. `fund_info(code="{code}")` - 基金基本信息
2. `fund_nav(code="{code}", limit=30)` - 净值走势
3. `fund_holdings(code="{code}")` - 重仓股明细
4. `fund_ranking(type="全部")` - 同类排名

## 关键指标关注
- 近1年收益率与同类排名
- 最大回撤与波动率
- 基金规模变化(规模过大可能影响操作灵活性)
- 基金经理任职年限和历史业绩
- 重仓股集中度

## 分析流程
1. 先用 fund_info 了解基金基本情况
2. 用 fund_nav 分析历史业绩表现
3. 用 fund_holdings 查看持仓风格
4. 用 fund_ranking 对比同类基金
5. 综合给出投资建议
"""
