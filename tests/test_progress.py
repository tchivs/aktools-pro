"""Tests for progress reporting in async tools."""

import pytest
from unittest import mock

from mcp_aktools.tools import analysis, crypto, precious_metals, stocks


search_fn = stocks.search.fn
composite_stock_diagnostic_fn = analysis.composite_stock_diagnostic.fn
crypto_composite_diagnostic_fn = crypto.crypto_composite_diagnostic.fn
pm_composite_diagnostic_fn = precious_metals.pm_composite_diagnostic.fn


@pytest.mark.asyncio
async def test_search_reports_progress():
    mock_ctx = mock.AsyncMock()

    with mock.patch("mcp_aktools.tools.stocks.ak_search", return_value=None):
        result = await search_fn(keyword="test", market="sh", ctx=mock_ctx)

    assert mock_ctx.report_progress.call_count >= 2
    assert result == "Not Found for test"


@pytest.mark.asyncio
async def test_search_reports_progress_when_found():
    mock_ctx = mock.AsyncMock()
    mock_info = mock.Mock()
    mock_info.to_string.return_value = "code    000001\nname    平安银行"

    with mock.patch("mcp_aktools.tools.stocks.ak_search", return_value=mock_info):
        result = await search_fn(keyword="平安", market="sh", ctx=mock_ctx)

    assert mock_ctx.report_progress.call_count >= 2
    assert isinstance(result, str)
    assert "交易市场" in result


@pytest.mark.asyncio
async def test_composite_stock_diagnostic_reports_progress():
    mock_ctx = mock.AsyncMock()

    with (
        mock.patch.object(analysis.market_prices, "fn", return_value="price_data"),
        mock.patch.object(analysis.stock_info, "fn", return_value="info_data"),
        mock.patch.object(analysis.stock_news, "fn", return_value="news_data"),
    ):
        result = await composite_stock_diagnostic_fn(symbol="000001", market="sh", ctx=mock_ctx)

    assert mock_ctx.report_progress.call_count >= 5
    assert "综合诊断报告" in result


@pytest.mark.asyncio
async def test_crypto_composite_diagnostic_reports_progress():
    mock_ctx = mock.AsyncMock()

    with (
        mock.patch.object(crypto.crypto_prices, "fn", return_value="price_data"),
        mock.patch.object(crypto.crypto_sentiment_metrics, "fn", return_value="sentiment_data"),
        mock.patch.object(crypto.binance_ai_report, "fn", return_value="ai_report"),
    ):
        result = await crypto_composite_diagnostic_fn(symbol="BTC", ctx=mock_ctx)

    assert mock_ctx.report_progress.call_count >= 4
    assert "加密货币综合诊断" in result


@pytest.mark.asyncio
async def test_pm_composite_diagnostic_reports_progress():
    mock_ctx = mock.AsyncMock()

    with (
        mock.patch.object(precious_metals.pm_spot_prices, "fn", return_value="spot_data"),
        mock.patch.object(precious_metals.pm_international_prices, "fn", return_value="intl_data"),
        mock.patch.object(precious_metals.pm_etf_holdings, "fn", return_value="etf_data"),
        mock.patch.object(precious_metals.pm_comex_inventory, "fn", return_value="comex_data"),
        mock.patch.object(precious_metals.pm_basis, "fn", return_value="basis_data"),
        mock.patch.object(precious_metals.pm_benchmark_price, "fn", return_value="benchmark_data"),
    ):
        result = await pm_composite_diagnostic_fn(metal="gold", ctx=mock_ctx)

    assert mock_ctx.report_progress.call_count >= 7
    assert "贵金属综合诊断" in result
