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
1. `stock_prices(symbol="{symbol}", limit=30)` - 获取近期走势
2. `stock_news(symbol="{symbol}", limit=5)` - 获取相关新闻
3. `draw_ascii_chart(symbol="{symbol}")` - 可视化趋势
4. `stock_indicators_a(symbol="{symbol}")` - 财务指标

## 关键指标关注
- MACD 金叉/死叉信号
- RSI 超买(>70)/超卖(<30)
- 布林带突破
- 成交量异常放大

## 分析流程
1. 先用 stock_prices 获取技术面数据
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
