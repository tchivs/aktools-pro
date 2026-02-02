"""Tests for MCP resources."""

import asyncio
from typing import Any

from mcp_aktools.server import mcp


def require_template(key: str) -> Any:
    template = mcp._resource_manager._templates.get(key)
    assert template is not None, f"{key} template not registered"
    return template


def require_resource(key: str) -> Any:
    resource = mcp._resource_manager._resources.get(key)
    assert resource is not None, f"{key} resource not registered"
    return resource


def read_template(template: Any, arguments: dict[str, Any]) -> str:
    return str(asyncio.run(template.read(arguments)))


def read_resource(resource: Any) -> str:
    return str(asyncio.run(resource.read()))


def test_stock_dynamic_analysis_template():
    """Test that stock dynamic analysis resource returns correct content."""
    template = require_template("stock://{symbol}/analysis")

    # Call the underlying function with a test symbol
    result = read_template(template, {"symbol": "600519"})

    # Verify symbol is interpolated
    assert "600519" in result
    assert "专属分析建议" in result

    # Verify recommended tools are mentioned
    assert "market_prices" in result
    assert "stock_news" in result
    assert "draw_ascii_chart" in result
    assert "stock_indicators_a" in result

    # Verify analysis structure
    assert "推荐工具链" in result
    assert "关键指标关注" in result
    assert "分析流程" in result

    # Verify technical indicators mentioned
    assert "MACD" in result
    assert "RSI" in result
    assert "布林带" in result


def test_sector_flow_guide_template():
    """Test that sector flow guide resource returns correct content."""
    template = require_template("market://{sector}/flow")

    # Call the underlying function with a test sector
    result = read_template(template, {"sector": "半导体"})

    # Verify sector is interpolated
    assert "半导体" in result
    assert "板块资金流向分析" in result

    # Verify recommended tools are mentioned
    assert "stock_sector_fund_flow_rank" in result
    assert "stock_zt_pool_em" in result
    assert "northbound_funds" in result

    # Verify analysis structure
    assert "推荐工具" in result
    assert "分析要点" in result
    assert "操作建议" in result

    # Verify key concepts mentioned
    assert "主力净流入" in result
    assert "北向资金" in result
    assert "涨停股" in result


def test_tech_analysis_resource():
    """Test that technical analysis resource returns correct content."""
    resource = require_resource("skill://trading/logic/technical-analysis")

    # Call the underlying function
    result = read_resource(resource)

    # Verify technical indicators are explained
    assert "MACD" in result
    assert "RSI" in result
    assert "BOLL" in result
    assert "KDJ" in result

    # Verify it's a SOP guide
    assert "技术指标解读 SOP" in result


def test_risk_management_resource():
    """Test that risk management resource returns correct content."""
    resource = require_resource("skill://trading/strategy/risk-management")

    # Call the underlying function
    result = read_resource(resource)

    # Verify risk management principles
    assert "风险管理原则" in result
    assert "止损" in result
    assert "仓位" in result
    assert "波动率" in result


def test_crypto_analysis_resource():
    """Test that crypto analysis resource returns correct content."""
    resource = require_resource("skill://crypto/logic/analysis-sop")

    # Call the underlying function
    result = read_resource(resource)

    # Verify crypto-specific analysis
    assert "加密货币分析 SOP" in result
    assert "多空比" in result
    assert "资金费率" in result
    assert "主动买卖" in result

    # Verify risk warnings
    assert "风险提示" in result
    assert "止损" in result


def test_precious_metals_analysis_resource():
    """Test that precious metals analysis resource returns correct content."""
    resource = require_resource("skill://trading/logic/precious-metals-analysis")

    # Call the underlying function
    result = read_resource(resource)

    # Verify precious metals analysis structure
    assert "贵金属分析 SOP" in result
    assert "价格趋势判断" in result
    assert "资金流向判断" in result
    assert "期现基差解读" in result
    assert "避险情绪指标" in result
    assert "金银比价" in result

    # Verify key concepts
    assert "上海金交所" in result
    assert "伦敦金" in result
    assert "ETF持仓" in result
    assert "COMEX库存" in result


def test_stock_dynamic_analysis_different_symbols():
    """Test stock analysis with different symbols."""
    template = require_template("stock://{symbol}/analysis")

    symbols = ["000001", "600000", "AAPL"]
    for symbol in symbols:
        result = read_template(template, {"symbol": symbol})
        assert symbol in result
        assert len(result) > 100  # Should have substantial content


def test_stock_dynamic_analysis_edge_cases():
    """Test stock analysis with edge cases."""
    template = require_template("stock://{symbol}/analysis")

    # Empty string
    result = read_template(template, {"symbol": ""})
    assert isinstance(result, str)
    assert len(result) > 50

    # Special characters
    result = read_template(template, {"symbol": "600519.SH"})
    assert isinstance(result, str)
    assert "600519.SH" in result


def test_sector_flow_guide_different_sectors():
    """Test sector flow guide with different sectors."""
    template = require_template("market://{sector}/flow")

    sectors = ["电子", "医药", "新能源"]
    for sector in sectors:
        result = read_template(template, {"sector": sector})
        assert sector in result
        assert len(result) > 100


def test_sector_flow_guide_edge_cases():
    """Test sector flow guide with edge cases."""
    template = require_template("market://{sector}/flow")

    # Empty string
    result = read_template(template, {"sector": ""})
    assert isinstance(result, str)
    assert len(result) > 50

    # Special characters
    result = read_template(template, {"sector": "半导体/芯片"})
    assert isinstance(result, str)
    assert "半导体/芯片" in result
