"""E2E Tests for MCP Server Protocol.

These tests verify the MCP server functionality at the protocol level,
testing tool registration, listing, and invocation.
"""

import pytest

# Import to trigger registration
from mcp_aktools.server import mcp
from mcp_aktools.tools import stocks, crypto, market, portfolio, analysis
from mcp_aktools import resources, prompts


class TestMCPServerSetup:
    """Test MCP server basic setup."""

    def test_server_name(self):
        """Test that server has correct name."""
        assert mcp.name == "aktools-pro"

    def test_server_has_version(self):
        """Test that server has version."""
        assert mcp.version is not None


class TestToolRegistration:
    """Test that all tools are properly registered."""

    def test_tools_registered(self):
        """Test that tools are registered."""
        tools = mcp._tool_manager._tools
        assert len(tools) > 0

    def test_stock_tools_registered(self):
        """Test stock-related tools."""
        tools = mcp._tool_manager._tools

        expected_tools = [
            "search",
            "stock_info",
            "market_prices",
            "stock_news",
            "institutional_holding_summary",
            "stock_indicators_a",
            "stock_indicators_hk",
            "stock_indicators_us",
        ]

        for tool in expected_tools:
            assert tool in tools, f"Tool {tool} not registered"

    def test_crypto_tools_registered(self):
        """Test crypto-related tools."""
        tools = mcp._tool_manager._tools

        expected_tools = [
            "crypto_prices",
            "crypto_sentiment_metrics",
            "binance_ai_report",
            "crypto_composite_diagnostic",
            "draw_crypto_chart",
            "backtest_crypto_strategy",
            "okx_funding_rate",
            "okx_open_interest",
            "fear_greed_index",
        ]

        for tool in expected_tools:
            assert tool in tools, f"Tool {tool} not registered"

    def test_market_tools_registered(self):
        """Test market-related tools."""
        tools = mcp._tool_manager._tools

        expected_tools = [
            "get_current_time",
            "stock_zt_pool_em",
            "stock_zt_pool_strong_em",
            "stock_lhb_ggtj_sina",
            "stock_sector_fund_flow_rank",
            "northbound_funds",
            "sector_valuation",
            "sector_rotation",
            "stock_news_global",
            "market_anomaly_scan",
        ]

        for tool in expected_tools:
            assert tool in tools, f"Tool {tool} not registered"

    def test_portfolio_tools_registered(self):
        """Test portfolio-related tools."""
        tools = mcp._tool_manager._tools

        expected_tools = ["portfolio_add", "portfolio_view"]

        for tool in expected_tools:
            assert tool in tools, f"Tool {tool} not registered"

    def test_analysis_tools_registered(self):
        """Test analysis-related tools."""
        tools = mcp._tool_manager._tools

        expected_tools = [
            "composite_stock_diagnostic",
            "draw_ascii_chart",
            "backtest_strategy",
            "trading_suggest",
        ]

        for tool in expected_tools:
            assert tool in tools, f"Tool {tool} not registered"


class TestToolMetadata:
    """Test tool metadata (title, description)."""

    def test_tools_have_title(self):
        """Test that all tools have title."""
        for name, tool in mcp._tool_manager._tools.items():
            mcp_tool = tool.to_mcp_tool()
            assert mcp_tool.title, f"Tool {name} missing title"

    def test_tools_have_description(self):
        """Test that all tools have description."""
        for name, tool in mcp._tool_manager._tools.items():
            mcp_tool = tool.to_mcp_tool()
            assert mcp_tool.description, f"Tool {name} missing description"

    def test_tools_have_input_schema(self):
        """Test that all tools have input schema."""
        for name, tool in mcp._tool_manager._tools.items():
            mcp_tool = tool.to_mcp_tool()
            assert mcp_tool.inputSchema, f"Tool {name} missing inputSchema"
            assert "type" in mcp_tool.inputSchema


class TestToolInvocation:
    """Test tool invocation through MCP protocol."""

    def test_get_current_time_invocation(self):
        """Test invoking get_current_time tool."""
        tool = mcp._tool_manager._tools.get("get_current_time")
        assert tool is not None

        # Call the underlying function
        fn = getattr(tool, "fn", None)
        assert callable(fn)
        result = fn()
        assert isinstance(result, str)
        assert "当前时间" in result

    def test_trading_suggest_invocation(self):
        """Test invoking trading_suggest tool."""
        tool = mcp._tool_manager._tools.get("trading_suggest")
        assert tool is not None

        fn = getattr(tool, "fn", None)
        assert callable(fn)
        result = fn(symbol="000001", action="buy", score=85, reason="Test")
        assert isinstance(result, dict)
        assert result["symbol"] == "000001"
        assert result["action"] == "buy"

    def test_portfolio_add_invocation(self):
        """Test invoking portfolio_add tool."""
        tool = mcp._tool_manager._tools.get("portfolio_add")
        assert tool is not None

        from unittest import mock
        from mcp_aktools.shared import constants

        # Mock the portfolio file
        with mock.patch.object(constants, "PORTFOLIO_FILE", "/tmp/test_portfolio.json"):
            fn = getattr(tool, "fn", None)
            assert callable(fn)
            result = fn(symbol="000001", price=10.5, volume=100, market="sh")
            assert isinstance(result, str)
            assert "成功" in result


class TestResourceRegistration:
    """Test that resources are properly registered."""

    def test_resources_registered(self):
        """Test that resources are registered."""
        resources = mcp._resource_manager._resources
        assert len(resources) > 0

    def test_resource_uris(self):
        """Test that resources have valid URIs."""
        resources = mcp._resource_manager._resources

        expected_uris = [
            "skill://crypto/logic/analysis-sop",
            "skill://trading/logic/technical-analysis",
            "skill://trading/strategy/risk-management",
        ]

        for uri in expected_uris:
            assert uri in resources, f"Resource {uri} not registered"

    def test_resources_have_content(self):
        """Test that resources return content."""
        for uri, resource in mcp._resource_manager._resources.items():
            fn = getattr(resource, "fn", None)
            assert callable(fn), f"Resource {uri} missing callable fn"
            content = fn()
            assert content, f"Resource {uri} has no content"


class TestPromptRegistration:
    """Test that prompts are properly registered."""

    def test_prompts_registered(self):
        """Test that prompts are registered."""
        prompts = mcp._prompt_manager._prompts
        assert len(prompts) > 0

    def test_prompt_names(self):
        """Test that expected prompts exist."""
        prompts = mcp._prompt_manager._prompts

        expected_prompts = [
            "analyze-stock",
            "analyze-crypto",
            "market-pulse",
            "crypto-pulse",
        ]

        for name in expected_prompts:
            assert name in prompts, f"Prompt {name} not registered"

    def test_prompts_have_description(self):
        """Test that all prompts have description."""
        for name, prompt in mcp._prompt_manager._prompts.items():
            mcp_prompt = prompt.to_mcp_prompt()
            assert mcp_prompt.description, f"Prompt {name} missing description"


class TestMCPProtocolCompliance:
    """Test MCP protocol compliance."""

    def test_tools_list_export(self):
        """Test that tools can be exported for tools/list."""
        tools = []
        for name, tool in mcp._tool_manager._tools.items():
            mcp_tool = tool.to_mcp_tool()
            tools.append(mcp_tool)

        assert len(tools) == len(mcp._tool_manager._tools)

        for tool in tools:
            assert tool.name
            assert tool.inputSchema

    def test_resources_list_export(self):
        """Test that resources can be exported for resources/list."""
        resources = []
        for uri, resource in mcp._resource_manager._resources.items():
            resources.append(
                {
                    "uri": uri,
                    "name": resource.name,
                    "description": resource.description,
                }
            )

        assert len(resources) == len(mcp._resource_manager._resources)

    def test_prompts_list_export(self):
        """Test that prompts can be exported for prompts/list."""
        prompts = []
        for name, prompt in mcp._prompt_manager._prompts.items():
            mcp_prompt = prompt.to_mcp_prompt()
            prompts.append(
                {
                    "name": name,
                    "description": mcp_prompt.description,
                }
            )

        assert len(prompts) == len(mcp._prompt_manager._prompts)


class TestIntegrationScenarios:
    """Test common integration scenarios."""

    def test_analyze_stock_workflow_tools_exist(self):
        """Test that tools needed for stock analysis workflow exist."""
        required_tools = [
            "get_current_time",
            "market_anomaly_scan",
            "composite_stock_diagnostic",
            "draw_ascii_chart",
            "trading_suggest",
        ]

        for tool in required_tools:
            assert tool in mcp._tool_manager._tools, f"Workflow tool {tool} missing"

    def test_crypto_analysis_workflow_tools_exist(self):
        """Test that tools needed for crypto analysis workflow exist."""
        required_tools = [
            "crypto_prices",
            "crypto_sentiment_metrics",
            "binance_ai_report",
            "crypto_composite_diagnostic",
            "draw_crypto_chart",
            "fear_greed_index",
        ]

        for tool in required_tools:
            assert tool in mcp._tool_manager._tools, f"Workflow tool {tool} missing"


class TestFunctionToolCallability:
    """Test that FunctionTool.fn is callable for composite tools.

    This prevents regression of the 'FunctionTool object is not callable' bug.
    These tests do NOT use mocks to verify real internal call paths.
    """

    def test_all_tools_have_callable_fn(self):
        """Verify all registered tools have callable .fn attribute."""
        for name, tool in mcp._tool_manager._tools.items():
            assert hasattr(tool, "fn"), f"Tool {name} missing .fn attribute"
            assert callable(getattr(tool, "fn", None)), f"Tool {name}.fn is not callable"

    def test_market_prices_fn_callable(self):
        """Test market_prices.fn is directly callable."""
        tool = mcp._tool_manager._tools.get("market_prices")
        assert tool is not None
        fn = getattr(tool, "fn", None)
        assert callable(fn)
        assert fn.__name__ == "market_prices"

    def test_stock_info_fn_callable(self):
        """Test stock_info.fn is directly callable."""
        tool = mcp._tool_manager._tools.get("stock_info")
        assert tool is not None
        assert callable(getattr(tool, "fn", None))

    def test_stock_news_fn_callable(self):
        """Test stock_news.fn is directly callable."""
        tool = mcp._tool_manager._tools.get("stock_news")
        assert tool is not None
        assert callable(getattr(tool, "fn", None))

    def test_crypto_prices_fn_callable(self):
        """Test crypto_prices.fn is directly callable."""
        tool = mcp._tool_manager._tools.get("crypto_prices")
        assert tool is not None
        assert callable(getattr(tool, "fn", None))

    def test_composite_tools_use_fn_attribute(self):
        """Verify composite tools access dependencies via .fn attribute.

        This is a code inspection test to ensure the fix is in place.
        """
        import inspect

        composite_tool = mcp._tool_manager._tools.get("composite_stock_diagnostic")
        assert composite_tool is not None
        fn = getattr(composite_tool, "fn", None)
        assert callable(fn)
        source = inspect.getsource(fn)

        assert "market_prices.fn" in source, "composite_stock_diagnostic should use market_prices.fn"
        assert "stock_info.fn" in source, "composite_stock_diagnostic should use stock_info.fn"
        assert "stock_news.fn" in source, "composite_stock_diagnostic should use stock_news.fn"
        assert "cast(Callable" not in source, "Should not use cast(Callable...) pattern"

    def test_draw_ascii_chart_uses_fn_attribute(self):
        """Verify draw_ascii_chart uses .fn attribute."""
        import inspect

        tool = mcp._tool_manager._tools.get("draw_ascii_chart")
        assert tool is not None
        fn = getattr(tool, "fn", None)
        assert callable(fn)
        source = inspect.getsource(fn)

        assert "market_prices.fn" in source, "draw_ascii_chart should use market_prices.fn"
        assert "cast(Callable" not in source, "Should not use cast(Callable...) pattern"

    def test_backtest_strategy_uses_fn_attribute(self):
        """Verify backtest_strategy uses .fn attribute."""
        import inspect

        tool = mcp._tool_manager._tools.get("backtest_strategy")
        assert tool is not None
        fn = getattr(tool, "fn", None)
        assert callable(fn)
        source = inspect.getsource(fn)

        assert "market_prices.fn" in source, "backtest_strategy should use market_prices.fn"
        assert "cast(Callable" not in source, "Should not use cast(Callable...) pattern"

    def test_crypto_composite_uses_fn_attribute(self):
        """Verify crypto_composite_diagnostic uses .fn attribute."""
        import inspect

        tool = mcp._tool_manager._tools.get("crypto_composite_diagnostic")
        assert tool is not None
        fn = getattr(tool, "fn", None)
        assert callable(fn)
        source = inspect.getsource(fn)

        assert "crypto_prices.fn" in source, "crypto_composite_diagnostic should use crypto_prices.fn"
        assert "cast(Callable" not in source, "Should not use cast(Callable...) pattern"

    def test_pm_composite_uses_fn_attribute(self):
        """Verify pm_composite_diagnostic uses .fn attribute."""
        import inspect

        tool = mcp._tool_manager._tools.get("pm_composite_diagnostic")
        assert tool is not None
        fn = getattr(tool, "fn", None)
        assert callable(fn)
        source = inspect.getsource(fn)

        assert "pm_spot_prices.fn" in source, "pm_composite_diagnostic should use pm_spot_prices.fn"
        assert "cast(Callable" not in source, "Should not use cast(Callable...) pattern"

    def test_draw_crypto_chart_uses_fn_attribute(self):
        """Verify draw_crypto_chart uses .fn attribute."""
        import inspect

        tool = mcp._tool_manager._tools.get("draw_crypto_chart")
        assert tool is not None
        fn = getattr(tool, "fn", None)
        assert callable(fn)
        source = inspect.getsource(fn)

        assert "crypto_prices.fn" in source, "draw_crypto_chart should use crypto_prices.fn"
        assert "cast(Callable" not in source, "Should not use cast(Callable...) pattern"

    def test_backtest_crypto_uses_fn_attribute(self):
        """Verify backtest_crypto_strategy uses .fn attribute."""
        import inspect

        tool = mcp._tool_manager._tools.get("backtest_crypto_strategy")
        assert tool is not None
        fn = getattr(tool, "fn", None)
        assert callable(fn)
        source = inspect.getsource(fn)

        assert "crypto_prices.fn" in source, "backtest_crypto_strategy should use crypto_prices.fn"
        assert "cast(Callable" not in source, "Should not use cast(Callable...) pattern"

    def test_portfolio_view_uses_fn_attribute(self):
        """Verify portfolio_view uses .fn attribute."""
        import inspect

        tool = mcp._tool_manager._tools.get("portfolio_view")
        assert tool is not None
        fn = getattr(tool, "fn", None)
        assert callable(fn)
        source = inspect.getsource(fn)

        assert "market_prices.fn" in source, "portfolio_view should use market_prices.fn"

    def test_portfolio_chart_uses_fn_attribute(self):
        """Verify portfolio_chart uses .fn attribute."""
        import inspect

        tool = mcp._tool_manager._tools.get("portfolio_chart")
        assert tool is not None
        fn = getattr(tool, "fn", None)
        assert callable(fn)
        source = inspect.getsource(fn)

        assert "market_prices.fn" in source, "portfolio_chart should use market_prices.fn"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
