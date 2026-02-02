"""Tests for crypto module tools."""

import pytest
import pandas as pd
from unittest import mock

# Import the module and access functions via .fn attribute
from mcp_aktools.tools import crypto as crypto_module

# Get actual functions from FunctionTool objects
_safe_float = crypto_module._safe_float
_safe_int = crypto_module._safe_int
crypto_prices_fn = crypto_module.crypto_prices.fn
crypto_sentiment_fn = crypto_module.crypto_sentiment_metrics.fn
binance_ai_fn = crypto_module.binance_ai_report.fn
crypto_diag_fn = crypto_module.crypto_composite_diagnostic.fn
draw_crypto_chart_fn = crypto_module.draw_crypto_chart.fn
backtest_crypto_fn = crypto_module.backtest_crypto_strategy.fn
okx_funding_fn = crypto_module.okx_funding_rate.fn
okx_oi_fn = crypto_module.okx_open_interest.fn
fgi_fn = crypto_module.fear_greed_index.fn


class TestSafeFloat:
    """Test _safe_float helper function."""

    def test_handles_empty_string(self):
        assert _safe_float("") == 0.0

    def test_handles_none(self):
        assert _safe_float(None) == 0.0

    def test_handles_valid_string(self):
        assert _safe_float("123.45") == 123.45

    def test_handles_valid_number(self):
        assert _safe_float(123.45) == 123.45

    def test_handles_invalid_string(self):
        assert _safe_float("invalid") == 0.0

    def test_custom_default(self):
        assert _safe_float("", default=1.0) == 1.0


class TestSafeInt:
    """Test _safe_int helper function."""

    def test_handles_empty_string(self):
        assert _safe_int("") == 0

    def test_handles_none(self):
        assert _safe_int(None) == 0

    def test_handles_valid_string(self):
        assert _safe_int("123") == 123

    def test_handles_valid_int(self):
        assert _safe_int(123) == 123

    def test_handles_invalid_string(self):
        assert _safe_int("invalid") == 0


class TestCryptoPrices:
    """Test the crypto_prices tool."""

    def test_returns_csv_with_indicators(self):
        """Test that function returns price data with technical indicators."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "data": [
                [
                    "1704067200000",
                    "42000.00",
                    "42500.00",
                    "43000.00",
                    "41500.00",
                    "100.00",
                    "4200000.00",
                    "4200000.00",
                    "1",
                ],
                [
                    "1704153600000",
                    "42500.00",
                    "43000.00",
                    "43500.00",
                    "42000.00",
                    "150.00",
                    "6375000.00",
                    "6375000.00",
                    "1",
                ],
            ]
        }

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = crypto_prices_fn(symbol="BTC-USDT", period="1H", limit=2)

            assert isinstance(result, str)
            assert "date" in result
            assert "close" in result

    def test_empty_response(self):
        """Test handling of empty response."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": []}

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = crypto_prices_fn(symbol="BTC-USDT", period="1H", limit=2)

            assert isinstance(result, str)
            assert "error" in result


class TestCryptoSentimentMetrics:
    """Test the crypto_sentiment_metrics tool."""

    def test_returns_csv(self):
        """Test that function returns sentiment data."""
        loan_response = mock.Mock()
        loan_response.json.return_value = {
            "data": [
                ["1704067200000", "1.5"],
                ["1704153600000", "1.6"],
            ]
        }
        taker_response = mock.Mock()
        taker_response.json.return_value = {
            "data": [
                ["1704067200000", "100.00", "150.00"],
                ["1704153600000", "120.00", "180.00"],
            ]
        }

        with mock.patch(
            "mcp_aktools.tools.crypto.requests.get",
            side_effect=[loan_response, taker_response],
        ):
            result = crypto_sentiment_fn(symbol="BTC", period="1H", inst_type="SPOT")

            assert isinstance(result, str)
            assert "时间" in result
            assert "多空比" in result
            assert "卖出量" in result


class TestBinanceAiReport:
    """Test the binance_ai_report tool."""

    def test_returns_report_text(self):
        """Test that function returns AI report text."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "data": {
                "report": {
                    "translated": {
                        "modules": [
                            {"overview": "BTC Analysis", "points": [{"content": "Point 1"}]},
                        ]
                    }
                }
            }
        }

        with mock.patch("mcp_aktools.tools.crypto.requests.post", return_value=mock_response):
            result = binance_ai_fn(symbol="BTC")

            assert isinstance(result, str)
            assert "BTC" in result or "Point 1" in result or "Analysis" in result

    def test_handles_invalid_json(self):
        """Test handling of invalid JSON response."""
        mock_response = mock.Mock()
        mock_response.json.side_effect = Exception("Invalid JSON")
        mock_response.text = "Some text response"

        with mock.patch("mcp_aktools.tools.crypto.requests.post", return_value=mock_response):
            result = binance_ai_fn(symbol="BTC")

            assert isinstance(result, str)


class TestCryptoCompositeDiagnostic:
    """Test the crypto_composite_diagnostic tool."""

    @pytest.mark.asyncio
    async def test_returns_composite_report(self):
        """Test that function returns a composite diagnostic report."""
        mock_prices = "date,open,high,low,close\n2024-01-01,42000,43000,41500,42500"
        mock_sentiment = "时间,多空比\n2024-01-01,1.5"
        mock_ai = "BTC AI Analysis Report"

        with mock.patch("mcp_aktools.tools.crypto.crypto_prices", return_value=mock_prices):
            with mock.patch("mcp_aktools.tools.crypto.crypto_sentiment_metrics", return_value=mock_sentiment):
                with mock.patch("mcp_aktools.tools.crypto.binance_ai_report", return_value=mock_ai):
                    result = await crypto_diag_fn(symbol="BTC")

                    assert isinstance(result, str)
                    assert "加密货币综合诊断" in result
                    assert "近期价格" in result
                    assert "情绪指标" in result
                    assert "币安AI报告" in result


class TestDrawCryptoChart:
    """Test the draw_crypto_chart tool."""

    def test_returns_ascii_chart(self):
        """Test that function returns an ASCII chart."""
        mock_prices = "date,open,high,low,close\n" + "\n".join(
            [f"2024-01-{i + 1:02d},42000,43000,41500,42500" for i in range(20)]
        )

        with mock.patch.object(crypto_module.crypto_prices, "fn", return_value=mock_prices):
            result = draw_crypto_chart_fn(symbol="BTC", bar="1D")

            assert isinstance(result, str)
            assert "BTC" in result
            assert "最低" in result
            assert "最高" in result

    def test_handles_insufficient_data(self):
        """Test handling of insufficient data."""
        with mock.patch.object(crypto_module.crypto_prices, "fn", return_value=""):
            result = draw_crypto_chart_fn(symbol="BTC", bar="1D")

            assert isinstance(result, str)
            assert "不足" in result or "无法" in result


class TestBacktestCryptoStrategy:
    """Test the backtest_crypto_strategy tool."""

    def test_sma_strategy(self):
        """Test SMA strategy backtest."""
        mock_prices = "date,open,high,low,close\n" + "\n".join(
            [f"2024-01-{i + 1:02d},42000,43000,41500,{42000 + i * 100}" for i in range(30)]
        )

        with mock.patch.object(crypto_module.crypto_prices, "fn", return_value=mock_prices):
            result = backtest_crypto_fn(symbol="BTC", strategy="SMA", bar="4H", limit=30)

            assert isinstance(result, str)
            assert "策略回测" in result
            assert "累计收益" in result
            assert "最大回撤" in result

    def test_returns_not_found_when_crypto_prices_not_string(self):
        """Test backtest when crypto_prices returns non-string."""
        with mock.patch.object(crypto_module.crypto_prices, "fn", return_value=pd.DataFrame()):
            result = backtest_crypto_fn(symbol="BTC", strategy="SMA", bar="4H", limit=30)

            assert isinstance(result, str)
            assert "未找到" in result

    def test_parse_failure(self):
        """Test backtest when price data cannot be parsed."""
        bad_csv = 'date,close\n"unterminated'
        with mock.patch.object(crypto_module.crypto_prices, "fn", return_value=bad_csv):
            result = backtest_crypto_fn(symbol="BTC", strategy="SMA", bar="4H", limit=30)

            assert isinstance(result, str)
            assert "解析失败" in result

    def test_empty_dataframe_after_parsing(self):
        """Test backtest when parsed data is empty."""
        with mock.patch.object(crypto_module.crypto_prices, "fn", return_value="date,open,high,low,close\n"):
            result = backtest_crypto_fn(symbol="BTC", strategy="SMA", bar="4H", limit=30)

            assert isinstance(result, str)
            assert "数据不足" in result

    def test_missing_close_column(self):
        """Test backtest when '收盘' column is missing."""
        mock_prices = "date,open,high,low\n2024-01-01,42000,43000,41500"
        with mock.patch.object(crypto_module.crypto_prices, "fn", return_value=mock_prices):
            result = backtest_crypto_fn(symbol="BTC", strategy="SMA", bar="4H", limit=30)

            assert isinstance(result, str)
            assert "数据不足" in result

    def test_rsi_strategy_missing_rsi_column(self):
        """Test RSI strategy when RSI column is missing."""
        mock_prices = "date,open,high,low,close\n" + "\n".join(
            [f"2024-01-{i + 1:02d},42000,43000,41500,{42000 + i * 10}" for i in range(30)]
        )
        with mock.patch.object(crypto_module.crypto_prices, "fn", return_value=mock_prices):
            result = backtest_crypto_fn(symbol="BTC", strategy="RSI", bar="4H", limit=30)

            assert isinstance(result, str)
            assert "缺少 RSI" in result

    def test_macd_strategy_missing_columns(self):
        """Test MACD strategy when DIF/DEA columns are missing."""
        mock_prices = "date,open,high,low,close\n" + "\n".join(
            [f"2024-01-{i + 1:02d},42000,43000,41500,{42000 + i * 10}" for i in range(30)]
        )
        with mock.patch.object(crypto_module.crypto_prices, "fn", return_value=mock_prices):
            result = backtest_crypto_fn(symbol="BTC", strategy="MACD", bar="4H", limit=30)

            assert isinstance(result, str)
            assert "缺少 MACD" in result

    def test_invalid_strategy(self):
        """Test backtest with invalid strategy."""
        mock_prices = "date,open,high,low,close\n" + "\n".join(
            [f"2024-01-{i + 1:02d},42000,43000,41500,{42000 + i * 10}" for i in range(30)]
        )
        with mock.patch.object(crypto_module.crypto_prices, "fn", return_value=mock_prices):
            result = backtest_crypto_fn(symbol="BTC", strategy="INVALID", bar="4H", limit=30)

            assert isinstance(result, str)
            assert "不支持" in result

    def test_returns_not_found_when_no_data(self):
        """Test backtest returns not-found when crypto_prices is empty."""
        with mock.patch.object(crypto_module.crypto_prices, "fn", return_value=""):
            result = backtest_crypto_fn(symbol="BTC", strategy="SMA", bar="4H", limit=30)
            assert "未找到" in result


class TestOkxFundingRate:
    """Test the okx_funding_rate tool."""

    def test_returns_funding_rate(self):
        """Test that function returns funding rate data."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "fundingRate": "0.0001",
                    "nextFundingRate": "0.0002",
                    "fundingTime": "1704067200000",
                }
            ]
        }

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = okx_funding_fn(symbol="BTC")

            assert isinstance(result, str)
            assert "资金费率" in result
            assert "当前费率" in result

    def test_handles_empty_fields(self):
        """Test handling of empty fields in response."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "fundingRate": "",
                    "nextFundingRate": "",
                    "fundingTime": "",
                }
            ]
        }

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = okx_funding_fn(symbol="BTC")

            assert isinstance(result, str)
            assert "BTC" in result

    def test_handles_no_items(self):
        """Test funding rate when API returns no items."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": []}

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = okx_funding_fn(symbol="BTC")

            assert isinstance(result, str)
            assert "未找到" in result


class TestOkxOpenInterest:
    """Test the okx_open_interest tool."""

    def test_returns_open_interest(self):
        """Test that function returns open interest data."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "oi": "1000000",
                    "oiCcy": "1000.00",
                    "ts": "1704067200000",
                }
            ]
        }

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = okx_oi_fn(symbol="BTC")

            assert isinstance(result, str)
            assert "持仓量" in result

    def test_handles_no_items(self):
        """Test open interest when API returns no items."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": []}

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = okx_oi_fn(symbol="BTC")

            assert isinstance(result, str)
            assert "未找到" in result

    def test_returns_not_found_when_empty(self):
        """Test open interest handles empty data."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": []}

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = okx_oi_fn(symbol="BTC")
            assert "未找到" in result


class TestFearGreedIndex:
    """Test the fear_greed_index tool."""

    def test_returns_index(self):
        """Test that function returns fear & greed index."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "value": "75",
                    "value_classification": "Greed",
                    "timestamp": "1704067200",
                }
            ]
            * 7
        }

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = fgi_fn()

            assert isinstance(result, str)
            assert "恐惧贪婪指数" in result
            assert "75" in result or "Greed" in result

    def test_handles_no_items(self):
        """Test fear_greed_index when API returns no items."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": []}

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = fgi_fn()

            assert isinstance(result, str)
            assert "未能获取" in result

    def test_handles_empty_response(self):
        """Test fear_greed_index handles empty response."""
        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": []}

        with mock.patch("mcp_aktools.tools.crypto.requests.get", return_value=mock_response):
            result = fgi_fn()
            assert "未能获取" in result


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
