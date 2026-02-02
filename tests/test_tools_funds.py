"""Tests for funds module tools."""

import pytest
import pandas as pd
from unittest import mock
from io import StringIO

# Import the module and access functions via .fn attribute
from mcp_aktools.tools import funds as funds_module

# Get actual functions from FunctionTool objects
fund_info_fn = funds_module.fund_info.fn
fund_nav_fn = funds_module.fund_nav.fn
fund_holdings_fn = funds_module.fund_holdings.fn
fund_ranking_fn = funds_module.fund_ranking.fn


class TestFundInfo:
    """Test the fund_info tool."""

    def test_fund_info_returns_csv(self):
        """Test that fund_info returns CSV format."""
        mock_df = pd.DataFrame(
            {
                "基金代码": ["000001"],
                "基金名称": ["华夏成长"],
                "基金类型": ["混合型"],
                "基金规模": ["100.00"],
            }
        )

        with mock.patch("mcp_aktools.tools.funds.ak_cache", return_value=mock_df):
            result = fund_info_fn(code="000001")

            assert isinstance(result, str)
            assert "基金代码" in result
            assert "000001" in result

    def test_fund_info_empty_result(self):
        """Test fund_info with empty result."""
        with mock.patch("mcp_aktools.tools.funds.ak_cache", return_value=pd.DataFrame()):
            result = fund_info_fn(code="000001")

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestFundNav:
    """Test the fund_nav tool."""

    def test_fund_nav_returns_csv(self):
        """Test that fund_nav returns CSV format."""
        mock_df = pd.DataFrame(
            {
                "净值日期": ["2024-01-01", "2024-01-02"],
                "单位净值": [1.5000, 1.5100],
                "累计净值": [2.0000, 2.0100],
                "日增长率": [0.50, 0.67],
            }
        )

        with mock.patch("mcp_aktools.tools.funds.ak_cache", return_value=mock_df):
            result = fund_nav_fn(code="000001", limit=30)

            assert isinstance(result, str)
            assert "净值日期" in result
            assert "单位净值" in result

    def test_fund_nav_limit(self):
        """Test fund_nav respects limit parameter."""
        mock_df = pd.DataFrame(
            {
                "净值日期": pd.date_range("2024-01-01", periods=100),
                "单位净值": [1.5 + i * 0.01 for i in range(100)],
            }
        )

        with mock.patch("mcp_aktools.tools.funds.ak_cache", return_value=mock_df):
            result = fund_nav_fn(code="000001", limit=10)

            csv_df = pd.read_csv(StringIO(result))
            assert len(csv_df) == 10


class TestFundHoldings:
    """Test the fund_holdings tool."""

    def test_fund_holdings_returns_csv(self):
        """Test that fund_holdings returns CSV format."""
        mock_df = pd.DataFrame(
            {
                "股票代码": ["600519", "000858"],
                "股票名称": ["贵州茅台", "五粮液"],
                "持仓比例": [8.50, 6.30],
            }
        )

        with mock.patch("mcp_aktools.tools.funds.ak_cache", return_value=mock_df):
            result = fund_holdings_fn(code="000001")

            assert isinstance(result, str)
            assert "股票代码" in result
            assert "持仓比例" in result


class TestFundRanking:
    """Test the fund_ranking tool."""

    def test_fund_ranking_returns_csv(self):
        """Test that fund_ranking returns CSV format."""
        mock_df = pd.DataFrame(
            {
                "基金代码": ["000001", "000002"],
                "基金名称": ["华夏成长", "华夏大盘"],
                "日增长率": [1.50, 1.20],
                "近1周": [3.50, 2.80],
            }
        )

        with mock.patch("mcp_aktools.tools.funds.ak_cache", return_value=mock_df):
            result = fund_ranking_fn(type="全部")

            assert isinstance(result, str)
            assert "基金代码" in result
            assert "日增长率" in result

    def test_fund_ranking_limits_results(self):
        """Test fund_ranking limits to 100 results."""
        mock_df = pd.DataFrame(
            {
                "基金代码": [f"{i:06d}" for i in range(200)],
                "基金名称": [f"基金{i}" for i in range(200)],
            }
        )

        with mock.patch("mcp_aktools.tools.funds.ak_cache", return_value=mock_df):
            result = fund_ranking_fn(type="全部")

            csv_df = pd.read_csv(StringIO(result))
            assert len(csv_df) <= 100
