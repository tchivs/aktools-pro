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
