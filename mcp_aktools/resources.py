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
