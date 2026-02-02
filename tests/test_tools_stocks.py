"""Tests for stocks module tools."""

import pytest
import pandas as pd
from unittest import mock

from mcp_aktools.tools import stocks as stocks_module


search_fn = stocks_module.search.fn
stock_info_fn = stocks_module.stock_info.fn
stock_news_fn = stocks_module.stock_news.fn
inst_holding_fn = stocks_module.institutional_holding_summary.fn
market_prices_fn = stocks_module.market_prices.fn
indicators_a_fn = stocks_module.stock_indicators_a.fn
indicators_hk_fn = stocks_module.stock_indicators_hk.fn
indicators_us_fn = stocks_module.stock_indicators_us.fn


class TestSearch:
    @pytest.mark.asyncio
    async def test_search_returns_string(self):
        mock_result = pd.Series({"code": "000001", "name": "平安银行"})
        with mock.patch("mcp_aktools.tools.stocks.ak_search", return_value=mock_result):
            result = await search_fn(keyword="平安", market="sh")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_search_not_found(self):
        with mock.patch("mcp_aktools.tools.stocks.ak_search", return_value=None):
            result = await search_fn(keyword="NONEXISTENT", market="sh")
        assert "Not Found" in result


class TestStockInfo:
    def test_stock_info_returns_string(self):
        mock_df = pd.DataFrame({"item": ["名称", "代码"], "value": ["平安银行", "000001"]})
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = stock_info_fn(symbol="000001", market="sh")
        assert isinstance(result, str)

    def test_stock_info_not_found(self):
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=None):
            with mock.patch("mcp_aktools.tools.stocks.ak_search", return_value=None):
                result = stock_info_fn(symbol="NONEXISTENT", market="sh")
        assert "Not Found" in result

    def test_stock_info_fallback_to_search_when_cache_none(self):
        mock_info = pd.Series({"code": "000001", "name": "平安银行"})
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=None):
            with mock.patch("mcp_aktools.tools.stocks.ak_search", return_value=mock_info):
                result = stock_info_fn(symbol="000001", market="sh")
        assert isinstance(result, str)

    def test_stock_info_fallback_to_search_when_cache_empty(self):
        mock_df = pd.DataFrame({"item": [], "value": []})
        mock_info = pd.Series({"code": "000001", "name": "平安银行"})
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            with mock.patch("mcp_aktools.tools.stocks.ak_search", return_value=mock_info):
                result = stock_info_fn(symbol="000001", market="sh")
        assert isinstance(result, str)


class TestStockNews:
    def test_stock_news_returns_csv(self):
        mock_df = pd.DataFrame({"发布时间": ["2024-01-01 10:00", "2024-01-02 11:00"], "标题": ["News 1", "News 2"]})
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = stock_news_fn(symbol="000001", limit=2)
        assert isinstance(result, str)

    def test_stock_news_empty_none(self):
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=None):
            result = stock_news_fn(symbol="000001")
        assert "未获取到" in result

    def test_stock_news_empty_dataframe(self):
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=pd.DataFrame()):
            result = stock_news_fn(symbol="000001")
        assert "未获取到" in result

    def test_stock_news_sorts_by_time_column(self):
        mock_df = pd.DataFrame({"时间": ["2024-01-01 10:00", "2024-01-02 11:00"], "标题": ["A", "B"]})
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = stock_news_fn(symbol="000001", limit=1)
        assert isinstance(result, str)

    def test_stock_news_sort_exception_is_ignored(self):
        mock_df = pd.DataFrame({"发布时间": ["2024-01-01 10:00"], "标题": ["News 1"]})
        with mock.patch.object(mock_df, "sort_values", side_effect=Exception("boom")):
            with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
                result = stock_news_fn(symbol="000001", limit=1)
        assert isinstance(result, str)


class TestInstitutionalHolding:
    def test_holding_summary_returns_csv(self):
        mock_df = pd.DataFrame({"报告期": ["2024Q1", "2024Q2"], "机构数": [100, 150], "持股比例": [5.5, 6.0]})
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = inst_holding_fn(symbol="000001")
        assert isinstance(result, str)

    def test_holding_summary_empty(self):
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=None):
            result = inst_holding_fn(symbol="000001")
        assert "未获取到" in result

    def test_holding_summary_drops_seq_column(self):
        mock_df = pd.DataFrame({"序号": [1, 2], "报告期": ["2024Q1", "2024Q2"], "机构数": [100, 150]})
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = inst_holding_fn(symbol="000001")
        assert "序号" not in result.split("\n")[0]

    def test_holding_summary_drop_exception_is_ignored(self):
        mock_df = pd.DataFrame({"报告期": ["2024Q1"], "序号": [1], "机构数": [100]})
        with mock.patch.object(mock_df, "drop", side_effect=Exception("boom")):
            with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
                result = inst_holding_fn(symbol="000001")
        assert isinstance(result, str)


class TestMarketPrices:
    def test_market_prices_returns_csv_with_indicators(self):
        mock_df = pd.DataFrame(
            {
                "日期": pd.date_range("2024-01-01", periods=10),
                "开盘": [10.0] * 10,
                "收盘": [10.5] * 10,
                "最高": [11.0] * 10,
                "最低": [9.5] * 10,
                "成交量": [1000000] * 10,
                "换手率": [1.5] * 10,
            }
        )
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = market_prices_fn(symbol="000001", market="sh", limit=5)
        assert isinstance(result, str)
        assert "date" in result

    def test_market_prices_not_found(self):
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=None):
            result = market_prices_fn(symbol="NONEXISTENT", market="sh", limit=30)
        assert "error" in result

    def test_market_prices_weekly(self):
        mock_df = pd.DataFrame(
            {
                "日期": pd.date_range("2024-01-01", periods=10),
                "开盘": [10.0] * 10,
                "收盘": [10.5] * 10,
                "最高": [11.0] * 10,
                "最低": [9.5] * 10,
                "成交量": [1000000] * 10,
                "换手率": [1.5] * 10,
            }
        )
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = market_prices_fn(symbol="000001", market="sh", period="weekly", limit=5)
        assert isinstance(result, str)
        assert "date" in result


class TestStockIndicators:
    def test_stock_indicators_a_returns_csv(self):
        mock_df = pd.DataFrame({"报告期": ["2024Q1"], "每股收益": [2.5], "净利润": [100000000]})
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = indicators_a_fn(symbol="000001")
        assert isinstance(result, str)

    def test_stock_indicators_hk_returns_csv(self):
        mock_df = pd.DataFrame({"报告期": ["2024Q1"], "市盈率": [10.5]})
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = indicators_hk_fn(symbol="00700")
        assert isinstance(result, str)

    def test_stock_indicators_us_returns_csv(self):
        mock_df = pd.DataFrame({"报告期": ["2024Q1"], "市盈率": [25.0]})
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=mock_df):
            result = indicators_us_fn(symbol="AAPL")
        assert isinstance(result, str)

    def test_stock_indicators_a_empty(self):
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=None):
            result = indicators_a_fn(symbol="000001")
        assert "未获取到" in result

    def test_stock_indicators_hk_empty(self):
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=pd.DataFrame()):
            result = indicators_hk_fn(symbol="00700")
        assert "未获取到" in result

    def test_stock_indicators_us_empty(self):
        with mock.patch("mcp_aktools.tools.stocks.ak_cache", return_value=pd.DataFrame()):
            result = indicators_us_fn(symbol="AAPL")
        assert "未获取到" in result


class TestStockHelpers:
    def test_stock_us_daily_empty(self):
        with mock.patch("mcp_aktools.tools.stocks.ak.stock_us_daily", return_value=pd.DataFrame()):
            assert stocks_module.stock_us_daily(symbol="AAPL") is None

    def test_stock_us_daily_transforms(self):
        raw = pd.DataFrame(
            {
                "date": ["2025-01-01", "2025-01-02"],
                "open": [1.0, 2.0],
                "close": [1.1, 2.1],
                "high": [1.2, 2.2],
                "low": [0.9, 1.9],
                "volume": [100, 200],
            }
        )
        with mock.patch("mcp_aktools.tools.stocks.ak.stock_us_daily", return_value=raw):
            df = stocks_module.stock_us_daily(symbol="AAPL", start_date="2025-01-01")
        assert df is not None
        assert "日期" in df.columns
        assert "换手率" in df.columns

    def test_fund_etf_hist_sina_empty(self):
        with mock.patch("mcp_aktools.tools.stocks.ak.fund_etf_hist_sina", return_value=pd.DataFrame()):
            assert stocks_module.fund_etf_hist_sina(symbol="510300", market="sh") is None

    def test_fund_etf_hist_sina_transforms(self):
        raw = pd.DataFrame(
            {
                "date": ["2025-01-01", "2025-01-02"],
                "open": [1.0, 2.0],
                "close": [1.1, 2.1],
                "high": [1.2, 2.2],
                "low": [0.9, 1.9],
                "volume": [100, 200],
            }
        )
        with mock.patch("mcp_aktools.tools.stocks.ak.fund_etf_hist_sina", return_value=raw):
            df = stocks_module.fund_etf_hist_sina(symbol="510300", market="sh", start_date="2025-01-01")
        assert df is not None
        assert "日期" in df.columns
        assert "换手率" in df.columns
