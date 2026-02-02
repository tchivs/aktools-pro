"""Tests for market module tools."""

import pytest
import pandas as pd
import os
from datetime import datetime, date
from unittest import mock

# Import the module and access functions via .fn attribute
from mcp_aktools.tools import market as market_module

# Get actual functions from FunctionTool objects
get_current_time_fn = market_module.get_current_time.fn
zt_pool_fn = market_module.stock_zt_pool_em.fn
zt_strong_fn = market_module.stock_zt_pool_strong_em.fn
lhb_fn = market_module.stock_lhb_ggtj_sina.fn
sector_flow_fn = market_module.stock_sector_fund_flow_rank.fn
northbound_fn = market_module.northbound_funds.fn
sector_val_fn = market_module.sector_valuation.fn
sector_rot_fn = market_module.sector_rotation.fn
news_global_fn = market_module.stock_news_global.fn
anomaly_scan_fn = market_module.market_anomaly_scan.fn


class TestGetCurrentTime:
    """Test the get_current_time tool."""

    def test_returns_string_with_time(self):
        """Test that function returns current time info."""
        result = get_current_time_fn()

        assert isinstance(result, str)
        assert "当前时间" in result

    def test_returns_weekday(self):
        """Test that result contains weekday info."""
        result = get_current_time_fn()

        # Should contain one of the weekdays
        weekdays = ["星期", "周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        assert any(day in result for day in weekdays)


class TestStockZtPoolEm:
    """Test the stock_zt_pool_em tool (limit up stocks)."""

    def test_returns_csv_with_count(self):
        """Test that function returns limit up stocks data."""
        mock_df = pd.DataFrame(
            {
                "代码": ["000001", "000002"],
                "名称": ["股票A", "股票B"],
                "成交额": [1000000, 2000000],
            }
        )

        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=mock_df):
            with mock.patch("mcp_aktools.tools.market.recent_trade_date", return_value=date.today()):
                result = zt_pool_fn(date="20240101", limit=10)

                assert isinstance(result, str)
                assert "涨停" in result or "代码" in result or "股票" in result or "共" in result

    def test_empty_result(self):
        """Test when no data available."""
        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=None):
            with mock.patch("mcp_aktools.tools.market.recent_trade_date", return_value=date.today()):
                result = zt_pool_fn()

                assert "失败" in result or "获取" in result

    def test_defaults_date_when_empty(self):
        mock_df = pd.DataFrame({"代码": ["000001"], "名称": ["股票A"], "成交额": [1000000]})
        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=mock_df):
            with mock.patch("mcp_aktools.tools.market.recent_trade_date", return_value=date.today()):
                result = zt_pool_fn(date="", limit=10)
        assert isinstance(result, str)
        assert "共" in result

    def test_empty_dataframe_returns_failure(self):
        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=pd.DataFrame()):
            with mock.patch("mcp_aktools.tools.market.recent_trade_date", return_value=date.today()):
                result = zt_pool_fn(date="", limit=10)
        assert "失败" in result


class TestStockZtPoolStrongEm:
    """Test the stock_zt_pool_strong_em tool (strong stocks)."""

    def test_returns_csv(self):
        """Test that function returns strong stocks data."""
        mock_df = pd.DataFrame(
            {
                "代码": ["000001"],
                "名称": ["股票A"],
                "成交额": [1000000],
            }
        )

        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=mock_df):
            with mock.patch("mcp_aktools.tools.market.recent_trade_date", return_value=date.today()):
                result = zt_strong_fn(date="20240101", limit=50)

                assert isinstance(result, str)

    def test_empty_dataframe_returns_failure(self):
        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=pd.DataFrame()):
            with mock.patch("mcp_aktools.tools.market.recent_trade_date", return_value=date.today()):
                result = zt_strong_fn(date="", limit=50)
        assert "失败" in result


class TestStockLhbGgtjSina:
    """Test the stock_lhb_ggtj_sina tool (dragon tiger list)."""

    def test_returns_csv(self):
        """Test that function returns dragon tiger list statistics."""
        mock_df = pd.DataFrame(
            {
                "代码": ["000001"],
                "名称": ["股票A"],
                "上榜次数": [5],
            }
        )

        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=mock_df):
            result = lhb_fn(days="5", limit=50)

            assert isinstance(result, str)

    def test_returns_failure_on_none(self):
        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=None):
            result = lhb_fn(days="5", limit=50)
        assert "失败" in result

    def test_returns_failure_on_empty(self):
        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=pd.DataFrame()):
            result = lhb_fn(days="5", limit=50)
        assert "失败" in result


class TestStockSectorFundFlowRank:
    """Test the stock_sector_fund_flow_rank tool."""

    def test_returns_csv(self):
        """Test that function returns sector fund flow data."""
        mock_df = pd.DataFrame(
            {
                "名称": ["银行", "科技"],
                "今日涨跌幅": [2.5, -1.5],
                "净流入": [1000000, -500000],
            }
        )

        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=mock_df):
            result = sector_flow_fn(days="今日", cate="行业资金流")

            assert isinstance(result, str)

    def test_returns_failure_on_none(self):
        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=None):
            result = sector_flow_fn(days="今日", cate="行业资金流")
        assert "失败" in result

    def test_concat_exception_returns_message(self):
        mock_df = pd.DataFrame({"名称": ["银行"], "今日涨跌幅": [2.5], "净流入": [1000000]})
        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=mock_df):
            with mock.patch("mcp_aktools.tools.market.pd.concat", side_effect=Exception("boom")):
                result = sector_flow_fn(days="今日", cate="行业资金流")
        assert "boom" in result


class TestNorthboundFunds:
    """Test the northbound_funds tool."""

    def test_returns_csv(self):
        """Test that function returns northbound funds data."""
        mock_df = pd.DataFrame(
            {
                "日期": pd.date_range("2024-01-01", periods=15),
                "净流入": [1000000] * 15,
            }
        )

        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=mock_df):
            result = northbound_fn()

            assert isinstance(result, str)

    def test_returns_failure_on_none(self):
        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=None):
            result = northbound_fn()
        assert "失败" in result

    def test_returns_failure_on_empty(self):
        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=pd.DataFrame()):
            result = northbound_fn()
        assert "失败" in result


class TestSectorValuation:
    """Test the sector_valuation tool."""

    def test_returns_csv(self):
        """Test that function returns sector valuation data."""
        mock_df = pd.DataFrame(
            {
                "行业": ["银行", "科技"],
                "市盈率": [10.5, 25.0],
                "市净率": [1.2, 3.5],
            }
        )

        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=mock_df):
            result = sector_val_fn()

            assert isinstance(result, str)

    def test_returns_failure_on_empty(self):
        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=None):
            result = sector_val_fn()
        assert "失败" in result


class TestSectorRotation:
    """Test the sector_rotation tool."""

    def test_returns_csv(self):
        """Test that function returns sector rotation data."""
        mock_df = pd.DataFrame(
            {
                "名称": ["银行", "科技"],
                "今日涨跌幅": [2.5, -1.5],
            }
        )

        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=mock_df):
            result = sector_rot_fn()

            assert isinstance(result, str)

    def test_returns_failure_on_empty(self):
        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=pd.DataFrame()):
            result = sector_rot_fn()
        assert "失败" in result


class TestStockNewsGlobal:
    """Test the stock_news_global tool."""

    def test_returns_string(self):
        """Test that function returns global news."""
        mock_df = pd.DataFrame(
            {
                "时间": ["2024-01-01 10:00"],
                "内容": ["Test news"],
            }
        )

        with mock.patch("mcp_aktools.tools.market.ak.stock_info_global_sina", return_value=mock_df):
            result = news_global_fn()

            assert isinstance(result, str)

    def test_newsnow_env_fetch(self):
        mock_response = mock.Mock()
        mock_response.json.return_value = [
            {"items": [{"title": "t1", "extra": {"hover": "h1", "info": "i1"}}]},
        ]
        with mock.patch.dict(os.environ, {"NEWSNOW_BASE_URL": "http://newstest"}, clear=False):
            with mock.patch("mcp_aktools.tools.market.requests.post", return_value=mock_response):
                items = market_module.newsnow_news(channels=["a"])
        assert isinstance(items, list)
        assert len(items) >= 1


class TestMarketAnomalyScan:
    """Test the market_anomaly_scan tool."""

    def test_returns_report(self):
        """Test that function returns anomaly scan report."""
        mock_df = pd.DataFrame(
            {
                "时间": ["10:00"],
                "代码": ["000001"],
                "名称": ["股票A"],
                "板块": ["银行"],
                "相关信息": ["快速上涨"],
            }
        )

        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=mock_df):
            result = anomaly_scan_fn(symbol="火箭发射")

            assert isinstance(result, str)
            assert "异动扫描" in result

    def test_returns_no_signal_message(self):
        with mock.patch("mcp_aktools.tools.market.ak_cache", return_value=pd.DataFrame()):
            result = anomaly_scan_fn(symbol="火箭发射")
        assert "没有检测到" in result

    def test_handles_exception(self):
        """Test that function handles exceptions gracefully."""
        with mock.patch("mcp_aktools.tools.market.ak_cache", side_effect=Exception("API Error")):
            result = anomaly_scan_fn()

            assert isinstance(result, str)
            assert "失败" in result or "错误" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
