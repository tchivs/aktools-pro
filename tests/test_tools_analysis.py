"""Tests for analysis module tools."""

import pytest
import pandas as pd
from unittest import mock

from mcp_aktools.tools import analysis as analysis_module

composite_diag_fn = analysis_module.composite_stock_diagnostic.fn
draw_chart_fn = analysis_module.draw_ascii_chart.fn
backtest_fn = analysis_module.backtest_strategy.fn
trading_suggest_fn = analysis_module.trading_suggest.fn


class TestCompositeStockDiagnostic:
    """Test the composite_stock_diagnostic tool."""

    @pytest.mark.asyncio
    async def test_returns_composite_report(self):
        """Test that function returns a composite diagnostic report."""
        mock_prices = "date,open,high,low,close\n2024-01-01,10.0,11.5,9.5,11.0"
        mock_info = "股票信息\n名称: 平安银行\n代码: 000001"
        mock_news = "日期,标题\n2024-01-01,Test news"

        with mock.patch.object(analysis_module.market_prices, "fn", return_value=mock_prices):
            with mock.patch.object(analysis_module.stock_info, "fn", return_value=mock_info):
                with mock.patch.object(analysis_module.stock_news, "fn", return_value=mock_news):
                    result = await composite_diag_fn(symbol="000001", market="sh")

                    assert isinstance(result, str)
                    assert "综合诊断报告" in result
                    assert "近期价格" in result
                    assert "基本面" in result
                    assert "核心新闻" in result


class TestDrawAsciiChart:
    """Test the draw_ascii_chart tool."""

    def test_returns_chart(self):
        """Test that function returns an ASCII chart."""
        mock_prices = "date,open,high,low,close\n" + "\n".join(
            [
                "2024-01-01,10.0,11.0,9.5,10.5",
                "2024-01-02,10.5,11.5,10.0,11.0",
                "2024-01-03,11.0,11.2,10.5,10.8",
            ]
        )

        with mock.patch.object(analysis_module.market_prices, "fn", return_value=mock_prices):
            result = draw_chart_fn(symbol="000001", market="sh")

            assert isinstance(result, str)
            assert "走势图" in result
            assert "最低" in result
            assert "最高" in result

    def test_handles_empty_data(self):
        """Test that function handles empty price data."""
        with mock.patch.object(analysis_module.market_prices, "fn", return_value=""):
            result = draw_chart_fn(symbol="000001", market="sh")

            assert isinstance(result, str)


class TestBacktestStrategy:
    """Test the backtest_strategy tool."""

    def test_sma_strategy_returns_report(self):
        """Test SMA strategy backtest."""
        dates = pd.date_range("2024-01-01", periods=30)
        mock_prices = "date,open,high,low,close\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1},{10.5 + i * 0.1}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch.object(analysis_module.market_prices, "fn", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="SMA", days=30)

            assert isinstance(result, str)
            assert "策略回测" in result
            assert "SMA" in result
            assert "累计收益" in result

    def test_rsi_strategy_returns_report(self):
        """Test RSI strategy backtest."""
        dates = pd.date_range("2024-01-01", periods=30)
        mock_prices = "date,open,high,low,close,rsi\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1},{10.5 + i * 0.1},{30 + i}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch.object(analysis_module.market_prices, "fn", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="RSI", days=30)

            assert isinstance(result, str)
            assert "RSI" in result

    def test_macd_strategy_returns_report(self):
        """Test MACD strategy backtest."""
        dates = pd.date_range("2024-01-01", periods=30)
        mock_prices = "date,open,high,low,close,dif,dea\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1},{10.5 + i * 0.1},{0.1 + i * 0.01},{0.05 + i * 0.01}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch.object(analysis_module.market_prices, "fn", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="MACD", days=30)

            assert isinstance(result, str)
            assert "MACD" in result

    def test_invalid_strategy(self):
        """Test backtest with invalid strategy."""
        dates = pd.date_range("2024-01-01", periods=30)
        mock_prices = "date,open,high,low,close\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1},{10.5 + i * 0.1}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch.object(analysis_module.market_prices, "fn", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="INVALID", days=30)

            assert isinstance(result, str)
            assert "不支持" in result

    def test_not_found_symbol(self):
        """Test backtest when symbol not found."""
        with mock.patch.object(
            analysis_module.market_prices, "fn", return_value="error,source,fallback\nempty data,akshare,"
        ):
            result = backtest_fn(symbol="NONEXISTENT", market="sh", strategy="SMA", days=30)

            assert isinstance(result, str)
            assert "未找到" in result

    def test_boll_strategy_returns_report(self):
        """Test BOLL strategy backtest."""
        dates = pd.date_range("2024-01-01", periods=30)
        mock_prices = "date,open,high,low,close,boll_u,boll_l\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1},{10.5 + i * 0.1},{12 + i * 0.1},{9 + i * 0.1}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch.object(analysis_module.market_prices, "fn", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="BOLL", days=30)

            assert isinstance(result, str)
            assert "BOLL" in result
            assert "累计收益" in result

    def test_ma_cross_strategy_returns_report(self):
        """Test MA_CROSS strategy backtest."""
        dates = pd.date_range("2024-01-01", periods=40)
        mock_prices = "date,open,high,low,close\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1},{10.5 + i * 0.1}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch.object(analysis_module.market_prices, "fn", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="MA_CROSS", days=40)

            assert isinstance(result, str)
            assert "MA_CROSS" in result
            assert "累计收益" in result

    def test_kdj_strategy_returns_report(self):
        """Test KDJ strategy backtest."""
        dates = pd.date_range("2024-01-01", periods=30)
        mock_prices = "date,open,high,low,close,kdj_k,kdj_d\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1},{10.5 + i * 0.1},{50 + i},{45 + i}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch.object(analysis_module.market_prices, "fn", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="KDJ", days=30)

            assert isinstance(result, str)
            assert "KDJ" in result
            assert "累计收益" in result

    def test_rsi_missing_indicator(self):
        """Test RSI strategy when RSI column is missing."""
        dates = pd.date_range("2024-01-01", periods=30)
        mock_prices = "date,open,high,low,close\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1},{10.5 + i * 0.1}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch.object(analysis_module.market_prices, "fn", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="RSI", days=30)

            assert "缺少 RSI" in result

    def test_macd_missing_indicator(self):
        """Test MACD strategy when DIF/DEA columns are missing."""
        dates = pd.date_range("2024-01-01", periods=30)
        mock_prices = "date,open,high,low,close\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1},{10.5 + i * 0.1}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch.object(analysis_module.market_prices, "fn", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="MACD", days=30)

            assert "缺少 MACD" in result

    def test_boll_missing_indicator(self):
        """Test BOLL strategy when BOLL columns are missing."""
        dates = pd.date_range("2024-01-01", periods=30)
        mock_prices = "date,open,high,low,close\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1},{10.5 + i * 0.1}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch.object(analysis_module.market_prices, "fn", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="BOLL", days=30)

            assert "缺少 BOLL" in result

    def test_kdj_missing_indicator(self):
        """Test KDJ strategy when KDJ columns are missing."""
        dates = pd.date_range("2024-01-01", periods=30)
        mock_prices = "date,open,high,low,close\n" + "\n".join(
            [
                f"{d.strftime('%Y-%m-%d')},{10 + i * 0.1},{11 + i * 0.1},{9.5 + i * 0.1},{10.5 + i * 0.1}"
                for i, d in enumerate(dates)
            ]
        )

        with mock.patch.object(analysis_module.market_prices, "fn", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="KDJ", days=30)

            assert "缺少 KDJ" in result

    def test_parse_failure(self):
        """Test backtest when price data cannot be parsed."""
        with mock.patch.object(analysis_module.market_prices, "fn", return_value="invalid,csv,data"):
            result = backtest_fn(symbol="000001", market="sh", strategy="SMA", days=30)

            assert "数据不足" in result or "解析失败" in result

    def test_empty_dataframe(self):
        """Test backtest with empty data after header."""
        mock_prices = "date,open,high,low,close\n"

        with mock.patch.object(analysis_module.market_prices, "fn", return_value=mock_prices):
            result = backtest_fn(symbol="000001", market="sh", strategy="SMA", days=30)

            assert "数据不足" in result


class TestCacheTools:
    """Test cache management tools."""

    def test_cache_status_empty(self):
        """Test cache_status when cache is empty."""
        from mcp_aktools.tools.analysis import cache_status
        from mcp_aktools.cache import CacheKey

        original_all = CacheKey.ALL.copy()
        CacheKey.ALL.clear()

        try:
            result = cache_status.fn()
            assert "缓存为空" in result
        finally:
            CacheKey.ALL.update(original_all)

    def test_cache_status_with_entries(self):
        """Test cache_status with cached entries."""
        from mcp_aktools.tools.analysis import cache_status
        from mcp_aktools.cache import CacheKey

        original_all = CacheKey.ALL.copy()
        CacheKey.ALL.clear()
        CacheKey.ALL["test_key_1"] = mock.Mock()
        CacheKey.ALL["test_key_2"] = mock.Mock()

        try:
            result = cache_status.fn()
            assert "缓存条目数: 2" in result
            assert "test_key_1" in result
        finally:
            CacheKey.ALL.clear()
            CacheKey.ALL.update(original_all)

    def test_cache_clear_all(self):
        """Test cache_clear clears all entries."""
        from mcp_aktools.tools.analysis import cache_clear
        from mcp_aktools.cache import CacheKey

        original_all = CacheKey.ALL.copy()
        mock_cache = mock.Mock()
        CacheKey.ALL.clear()
        CacheKey.ALL["test_key"] = mock_cache

        try:
            result = cache_clear.fn(key="")
            assert "已清理所有缓存" in result
            mock_cache.delete.assert_called_once()
        finally:
            CacheKey.ALL.clear()
            CacheKey.ALL.update(original_all)

    def test_cache_clear_specific_key(self):
        """Test cache_clear clears specific key."""
        from mcp_aktools.tools.analysis import cache_clear
        from mcp_aktools.cache import CacheKey

        original_all = CacheKey.ALL.copy()
        mock_cache = mock.Mock()
        CacheKey.ALL.clear()
        CacheKey.ALL["specific_key"] = mock_cache

        try:
            result = cache_clear.fn(key="specific_key")
            assert "已清理缓存: specific_key" in result
            mock_cache.delete.assert_called_once()
        finally:
            CacheKey.ALL.clear()
            CacheKey.ALL.update(original_all)

    def test_cache_clear_nonexistent_key(self):
        """Test cache_clear with nonexistent key."""
        from mcp_aktools.tools.analysis import cache_clear
        from mcp_aktools.cache import CacheKey

        original_all = CacheKey.ALL.copy()
        CacheKey.ALL.clear()

        try:
            result = cache_clear.fn(key="nonexistent")
            assert "未找到缓存键" in result
        finally:
            CacheKey.ALL.update(original_all)


class TestTradingSuggest:
    """Test the trading_suggest tool."""

    def test_returns_dict(self):
        """Test that function returns a dictionary with trade suggestion."""
        result = trading_suggest_fn(
            symbol="000001",
            action="buy",
            score=85,
            reason="技术指标显示买入信号",
        )

        assert isinstance(result, dict)
        assert result["symbol"] == "000001"
        assert result["action"] == "buy"
        assert result["score"] == 85
        assert "买入信号" in result["reason"]

    def test_returns_sell_suggestion(self):
        """Test sell suggestion."""
        result = trading_suggest_fn(
            symbol="000002",
            action="sell",
            score=70,
            reason="达到目标价位",
        )

        assert result["action"] == "sell"
        assert result["score"] == 70


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
