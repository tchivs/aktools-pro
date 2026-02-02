"""Tests for precious_metals module tools."""

import pytest
import pandas as pd
from unittest import mock

# Import the module and access functions via .fn attribute
from mcp_aktools.tools import precious_metals as pm_module

# Get actual functions from FunctionTool objects
pm_spot_prices_fn = pm_module.pm_spot_prices.fn
pm_international_prices_fn = pm_module.pm_international_prices.fn
pm_etf_holdings_fn = pm_module.pm_etf_holdings.fn
pm_comex_inventory_fn = pm_module.pm_comex_inventory.fn
pm_basis_fn = pm_module.pm_basis.fn
pm_benchmark_price_fn = pm_module.pm_benchmark_price.fn
pm_composite_diagnostic_fn = pm_module.pm_composite_diagnostic.fn


class TestPmSpotPrices:
    """Test the pm_spot_prices tool."""

    def test_returns_csv_with_indicators(self):
        """Test that function returns spot price data with technical indicators."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2025-01-01", "2025-01-02", "2025-01-03"],
                "开盘价": [500.0, 501.0, 502.0],
                "收盘价": [501.0, 502.0, 503.0],
                "最高价": [502.0, 503.0, 504.0],
                "最低价": [499.0, 500.0, 501.0],
                "成交量": [1000, 1100, 1200],
            }
        )

        with mock.patch("mcp_aktools.tools.precious_metals.ak_cache", return_value=mock_df):
            result = pm_spot_prices_fn(symbol="Au99.99", limit=10)

            assert isinstance(result, str)
            assert "date" in result

    def test_handles_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        mock_df = pd.DataFrame()

        with mock.patch("mcp_aktools.tools.precious_metals.ak_cache", return_value=mock_df):
            result = pm_spot_prices_fn(symbol="Au99.99", limit=10)

            assert isinstance(result, str)
            assert "error" in result

    def test_handles_english_column_names(self):
        """Test handling of English column names from newer akshare API."""
        mock_df = pd.DataFrame(
            {
                "date": ["2025-01-01", "2025-01-02", "2025-01-03"],
                "open": [500.0, 501.0, 502.0],
                "close": [501.0, 502.0, 503.0],
                "high": [502.0, 503.0, 504.0],
                "low": [499.0, 500.0, 501.0],
            }
        )

        with mock.patch("mcp_aktools.tools.precious_metals.ak_cache", return_value=mock_df):
            result = pm_spot_prices_fn(symbol="Au99.99", limit=10)

            assert isinstance(result, str)
            assert "date" in result
            assert "open" in result
            assert "close" in result


class TestPmInternationalPrices:
    """Test the pm_international_prices tool."""

    def test_returns_csv(self):
        """Test that function returns international price data."""
        mock_df = pd.DataFrame(
            {
                "时间": ["2025-01-01 10:00", "2025-01-01 11:00"],
                "价格": [2000.0, 2005.0],
                "涨跌幅": [0.5, 0.25],
            }
        )

        with mock.patch("mcp_aktools.tools.precious_metals.ak_cache", return_value=mock_df):
            result = pm_international_prices_fn(symbol="XAU")

            assert isinstance(result, str)
            assert "时间" in result or "价格" in result


class TestPmEtfHoldings:
    """Test the pm_etf_holdings tool."""

    def test_returns_csv(self):
        """Test that function returns ETF holdings data."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2025-01-01", "2025-01-02"],
                "持仓量": [1000.0, 1010.0],
                "变化": [10.0, 10.0],
            }
        )

        with mock.patch("mcp_aktools.tools.precious_metals.ak_cache", return_value=mock_df):
            result = pm_etf_holdings_fn(metal="gold", limit=10)

            assert isinstance(result, str)
            assert "日期" in result or "持仓" in result


class TestPmComexInventory:
    """Test the pm_comex_inventory tool."""

    def test_returns_csv(self):
        """Test that function returns COMEX inventory data."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2025-01-01", "2025-01-02"],
                "库存": [5000.0, 4990.0],
                "变化": [-10.0, -10.0],
            }
        )

        with mock.patch("mcp_aktools.tools.precious_metals.ak_cache", return_value=mock_df):
            result = pm_comex_inventory_fn(metal="gold", limit=10)

            assert isinstance(result, str)
            assert "日期" in result or "库存" in result


class TestPmBasis:
    """Test the pm_basis tool."""

    def test_returns_csv(self):
        """Test that function returns basis data."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2025-01-01", "2025-01-02"],
                "现货价": [500.0, 501.0],
                "期货价": [505.0, 506.0],
                "基差": [5.0, 5.0],
            }
        )

        with mock.patch("mcp_aktools.tools.precious_metals.ak_cache", return_value=mock_df):
            result = pm_basis_fn(metal="gold")

            assert isinstance(result, str)
            assert "日期" in result or "基差" in result or "现货" in result


class TestPmBenchmarkPrice:
    """Test the pm_benchmark_price tool."""

    def test_returns_csv(self):
        """Test that function returns benchmark price data."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2025-01-01", "2025-01-02"],
                "基准价": [500.0, 501.0],
            }
        )

        with mock.patch("mcp_aktools.tools.precious_metals.ak_cache", return_value=mock_df):
            result = pm_benchmark_price_fn(metal="gold", limit=10)

            assert isinstance(result, str)
            assert "日期" in result or "基准" in result


class TestPmCompositeDiagnostic:
    """Test the pm_composite_diagnostic tool."""

    @pytest.mark.asyncio
    async def test_returns_composite_report(self):
        """Test that function returns a composite diagnostic report."""
        mock_spot = "日期,开盘价,收盘价\n2025-01-01,500.0,501.0"
        mock_intl = "时间,最新价\n2025-01-01,2000.0"
        mock_etf = "日期,黄金-持仓量\n2025-01-01,1000.0"
        mock_comex = "日期,库存\n2025-01-01,5000.0"
        mock_basis = "日期,现货价格,期货价格\n2025-01-01,500.0,505.0"
        mock_benchmark = "日期,开盘价\n2025-01-01,500.0"

        with mock.patch("mcp_aktools.tools.precious_metals.pm_spot_prices", return_value=mock_spot):
            with mock.patch("mcp_aktools.tools.precious_metals.pm_international_prices", return_value=mock_intl):
                with mock.patch("mcp_aktools.tools.precious_metals.pm_etf_holdings", return_value=mock_etf):
                    with mock.patch("mcp_aktools.tools.precious_metals.pm_comex_inventory", return_value=mock_comex):
                        with mock.patch("mcp_aktools.tools.precious_metals.pm_basis", return_value=mock_basis):
                            with mock.patch(
                                "mcp_aktools.tools.precious_metals.pm_benchmark_price", return_value=mock_benchmark
                            ):
                                result = await pm_composite_diagnostic_fn(metal="gold")

                                assert isinstance(result, str)
                                assert "贵金属综合诊断" in result
                                assert "上海金交所现货价格" in result
                                assert "国际市场价格" in result
                                assert "ETF持仓变化" in result
                                assert "COMEX库存" in result
                                assert "期现基差" in result
                                assert "上海基准价" in result

    @pytest.mark.asyncio
    async def test_handles_partial_data(self):
        """Test handling when some data sources fail."""
        mock_spot = "日期,开盘价,收盘价\n2025-01-01,500.0,501.0"
        mock_empty = ""

        with mock.patch("mcp_aktools.tools.precious_metals.pm_spot_prices", return_value=mock_spot):
            with mock.patch("mcp_aktools.tools.precious_metals.pm_international_prices", return_value=mock_empty):
                with mock.patch("mcp_aktools.tools.precious_metals.pm_etf_holdings", return_value=mock_spot):
                    with mock.patch("mcp_aktools.tools.precious_metals.pm_comex_inventory", return_value=mock_empty):
                        with mock.patch("mcp_aktools.tools.precious_metals.pm_basis", return_value=mock_spot):
                            with mock.patch(
                                "mcp_aktools.tools.precious_metals.pm_benchmark_price", return_value=mock_spot
                            ):
                                result = await pm_composite_diagnostic_fn(metal="gold")

                                assert isinstance(result, str)
                                assert "贵金属综合诊断" in result
