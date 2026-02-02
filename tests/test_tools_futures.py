"""Tests for futures module tools."""

import pytest
import pandas as pd
from unittest import mock

from mcp_aktools.tools import futures as futures_module

futures_prices_fn = futures_module.futures_prices.fn
futures_inventory_fn = futures_module.futures_inventory.fn
futures_basis_fn = futures_module.futures_basis.fn
futures_positions_fn = futures_module.futures_positions.fn


class TestFuturesPrices:
    """Test the futures_prices tool."""

    def test_returns_csv(self):
        """Test that function returns futures price data."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2025-01-01", "2025-01-02", "2025-01-03"],
                "开盘价": [4000.0, 4010.0, 4020.0],
                "收盘价": [4010.0, 4020.0, 4030.0],
                "最高价": [4020.0, 4030.0, 4040.0],
                "最低价": [3990.0, 4000.0, 4010.0],
                "成交量": [100000, 110000, 120000],
            }
        )

        with mock.patch("mcp_aktools.tools.futures.ak_cache", return_value=mock_df):
            result = futures_prices_fn(symbol="螺纹钢", limit=30)

            assert isinstance(result, str)
            assert "date" in result

    def test_handles_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        mock_df = pd.DataFrame()

        with mock.patch("mcp_aktools.tools.futures.ak_cache", return_value=mock_df):
            result = futures_prices_fn(symbol="螺纹钢", limit=30)

            assert isinstance(result, str)
            assert "error" in result

    def test_handles_time_column(self):
        """Test handling when DataFrame has '时间' instead of '日期'."""
        mock_df = pd.DataFrame(
            {
                "时间": ["2025-01-01 10:00", "2025-01-02 10:00"],
                "开盘价": [4000.0, 4010.0],
                "收盘价": [4010.0, 4020.0],
            }
        )

        with mock.patch("mcp_aktools.tools.futures.ak_cache", return_value=mock_df):
            result = futures_prices_fn(symbol="螺纹钢", limit=30)

            assert isinstance(result, str)
            assert "date" in result


class TestFuturesInventory:
    """Test the futures_inventory tool."""

    def test_returns_csv(self):
        """Test that function returns inventory data."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2025-01-01", "2025-01-02", "2025-01-03"],
                "库存": [500000, 510000, 520000],
                "增减": [10000, 10000, 10000],
            }
        )

        with mock.patch("mcp_aktools.tools.futures.ak_cache", return_value=mock_df):
            result = futures_inventory_fn(symbol="螺纹钢")

            assert isinstance(result, str)
            assert "日期" in result or "库存" in result

    def test_handles_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        mock_df = pd.DataFrame()

        with mock.patch("mcp_aktools.tools.futures.ak_cache", return_value=mock_df):
            result = futures_inventory_fn(symbol="螺纹钢")

            assert isinstance(result, pd.DataFrame)


class TestFuturesBasis:
    """Test the futures_basis tool."""

    def test_returns_csv(self):
        """Test that function returns basis data."""
        mock_df = pd.DataFrame(
            {
                "日期": ["2025-01-01", "2025-01-02", "2025-01-03"],
                "期货价格": [4000.0, 4010.0, 4020.0],
                "现货价格": [3950.0, 3960.0, 3970.0],
                "基差": [50.0, 50.0, 50.0],
            }
        )

        with mock.patch("mcp_aktools.tools.futures.ak_cache", return_value=mock_df):
            result = futures_basis_fn(symbol="螺纹钢")

            assert isinstance(result, str)
            assert "日期" in result or "基差" in result

    def test_handles_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        mock_df = pd.DataFrame()

        with mock.patch("mcp_aktools.tools.futures.ak_cache", return_value=mock_df):
            result = futures_basis_fn(symbol="螺纹钢")

            assert isinstance(result, pd.DataFrame)


class TestFuturesPositions:
    """Test the futures_positions tool."""

    def test_returns_csv(self):
        """Test that function returns position ranking data."""
        mock_df = pd.DataFrame(
            {
                "会员简称": ["机构A", "机构B", "机构C"],
                "持买仓量": [10000, 9000, 8000],
                "持卖仓量": [8000, 9000, 10000],
                "净持仓": [2000, 0, -2000],
            }
        )

        with mock.patch("mcp_aktools.tools.futures.ak_cache", return_value=mock_df):
            result = futures_positions_fn(symbol="螺纹钢")

            assert isinstance(result, str)
            assert "会员简称" in result or "持买仓量" in result

    def test_handles_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        mock_df = pd.DataFrame()

        with mock.patch("mcp_aktools.tools.futures.ak_cache", return_value=mock_df):
            result = futures_positions_fn(symbol="螺纹钢")

            assert isinstance(result, pd.DataFrame)
