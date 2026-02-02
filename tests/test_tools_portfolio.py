"""Tests for portfolio module tools."""

import pytest
import json
import tempfile
import os
import uuid
from typing import ClassVar
from datetime import datetime
from pathlib import Path
from unittest import mock

from mcp_aktools.shared import constants
from mcp_aktools.shared import utils as utils_module
from mcp_aktools.cache import CacheKey

from mcp_aktools.tools import portfolio as portfolio_module

portfolio_add_fn = portfolio_module.portfolio_add.fn
portfolio_view_fn = portfolio_module.portfolio_view.fn
portfolio_chart_fn = portfolio_module.portfolio_chart.fn


def get_unique_portfolio_file(base_dir):
    return Path(base_dir) / f"portfolio_{uuid.uuid4().hex}.json"


class TestPortfolioAdd:
    """Test the portfolio_add tool."""

    temp_dir: ClassVar[str] = ""
    temp_portfolio: ClassVar[Path] = Path("")
    orig_file: ClassVar[str] = ""

    def setup_method(self):
        cls = type(self)
        cls.temp_dir = tempfile.mkdtemp()
        cls.temp_portfolio = get_unique_portfolio_file(cls.temp_dir)
        cls.orig_file = utils_module.PORTFOLIO_FILE
        CacheKey.ALL = {}

    def teardown_method(self):
        cls = type(self)
        utils_module.PORTFOLIO_FILE = cls.orig_file
        constants.PORTFOLIO_FILE = cls.orig_file
        if cls.temp_portfolio.exists():
            cls.temp_portfolio.unlink()
        if Path(cls.temp_dir).exists():
            import shutil

            shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_add_portfolio_record(self):
        temp_portfolio = type(self).temp_portfolio
        utils_module.PORTFOLIO_FILE = str(temp_portfolio)
        constants.PORTFOLIO_FILE = str(temp_portfolio)
        result = portfolio_add_fn(symbol="000001", price=10.5, volume=100, market="sh")

        assert isinstance(result, str)
        assert "成功" in result
        assert "000001" in result

    def test_add_multiple_records(self):
        temp_portfolio = type(self).temp_portfolio
        utils_module.PORTFOLIO_FILE = str(temp_portfolio)
        constants.PORTFOLIO_FILE = str(temp_portfolio)

        portfolio_add_fn(symbol="000001", price=10.5, volume=100, market="sh")
        portfolio_add_fn(symbol="000002", price=20.0, volume=200, market="sz")

        with open(temp_portfolio, "r") as f:
            data = json.load(f)

        assert "000001.sh" in data
        assert "000002.sz" in data
        assert data["000001.sh"]["price"] == 10.5
        assert data["000002.sz"]["price"] == 20.0


class TestPortfolioView:
    """Test the portfolio_view tool."""

    temp_dir: ClassVar[str] = ""
    temp_portfolio: ClassVar[Path] = Path("")
    orig_file: ClassVar[str] = ""

    def setup_method(self):
        cls = type(self)
        cls.temp_dir = tempfile.mkdtemp()
        cls.temp_portfolio = get_unique_portfolio_file(cls.temp_dir)
        cls.orig_file = utils_module.PORTFOLIO_FILE
        CacheKey.ALL = {}

    def teardown_method(self):
        cls = type(self)
        utils_module.PORTFOLIO_FILE = cls.orig_file
        constants.PORTFOLIO_FILE = cls.orig_file
        if cls.temp_portfolio.exists():
            cls.temp_portfolio.unlink()
        if Path(cls.temp_dir).exists():
            import shutil

            shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_empty_portfolio(self):
        utils_module.PORTFOLIO_FILE = str(self.temp_portfolio)
        constants.PORTFOLIO_FILE = str(self.temp_portfolio)
        result = portfolio_view_fn()

        assert isinstance(result, str)
        assert "为空" in result

    def test_view_with_holdings(self):
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.0,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            }
        }

        temp_portfolio = type(self).temp_portfolio
        os.makedirs(os.path.dirname(temp_portfolio), exist_ok=True)
        with open(temp_portfolio, "w") as f:
            json.dump(test_data, f)

        mock_prices = "date,open,high,low,close\n2024-01-01,9.5,11.5,9.0,11.0"

        utils_module.PORTFOLIO_FILE = str(temp_portfolio)
        constants.PORTFOLIO_FILE = str(temp_portfolio)
        with mock.patch.object(portfolio_module.market_prices, "fn", return_value=mock_prices):
            result = portfolio_view_fn()

            assert isinstance(result, str)
            assert "000001" in result
            assert "成本" in result
            assert "盈亏" in result

    def test_view_handles_price_fetch_failure(self):
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.0,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            }
        }

        temp_portfolio = type(self).temp_portfolio
        os.makedirs(os.path.dirname(temp_portfolio), exist_ok=True)
        with open(temp_portfolio, "w") as f:
            json.dump(test_data, f)

        def mock_error(*args, **kwargs):
            raise Exception("API Error")

        utils_module.PORTFOLIO_FILE = str(temp_portfolio)
        constants.PORTFOLIO_FILE = str(temp_portfolio)
        with mock.patch.object(portfolio_module.market_prices, "fn", side_effect=mock_error):
            result = portfolio_view_fn()

            assert isinstance(result, str)
            assert "000001" in result
            assert "无法获取" in result


class TestPortfolioChart:
    """Test the portfolio_chart tool."""

    temp_dir: ClassVar[str] = ""
    temp_portfolio: ClassVar[Path] = Path("")
    orig_file: ClassVar[str] = ""

    def setup_method(self):
        cls = type(self)
        cls.temp_dir = tempfile.mkdtemp()
        cls.temp_portfolio = get_unique_portfolio_file(cls.temp_dir)
        cls.orig_file = utils_module.PORTFOLIO_FILE
        CacheKey.ALL = {}

    def teardown_method(self):
        cls = type(self)
        utils_module.PORTFOLIO_FILE = cls.orig_file
        constants.PORTFOLIO_FILE = cls.orig_file
        if cls.temp_portfolio.exists():
            cls.temp_portfolio.unlink()
        if Path(cls.temp_dir).exists():
            import shutil

            shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_empty_portfolio_chart(self):
        temp_portfolio = type(self).temp_portfolio
        utils_module.PORTFOLIO_FILE = str(temp_portfolio)
        constants.PORTFOLIO_FILE = str(temp_portfolio)
        result = portfolio_chart_fn()

        assert "为空" in result

    def test_chart_with_positive_returns(self):
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.0,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            }
        }

        temp_portfolio = type(self).temp_portfolio
        os.makedirs(os.path.dirname(temp_portfolio), exist_ok=True)
        with open(temp_portfolio, "w") as f:
            json.dump(test_data, f)

        mock_prices = "date,open,high,low,close\n2024-01-01,9.5,12.5,9.0,12.0"

        utils_module.PORTFOLIO_FILE = str(temp_portfolio)
        constants.PORTFOLIO_FILE = str(temp_portfolio)
        with mock.patch.object(portfolio_module.market_prices, "fn", return_value=mock_prices):
            result = portfolio_chart_fn()

            assert "持仓盈亏图表" in result
            assert "000001" in result
            assert "+" in result

    def test_chart_with_negative_returns(self):
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.0,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            }
        }

        temp_portfolio = type(self).temp_portfolio
        os.makedirs(os.path.dirname(temp_portfolio), exist_ok=True)
        with open(temp_portfolio, "w") as f:
            json.dump(test_data, f)

        mock_prices = "date,open,high,low,close\n2024-01-01,9.5,10.0,7.5,8.0"

        utils_module.PORTFOLIO_FILE = str(temp_portfolio)
        constants.PORTFOLIO_FILE = str(temp_portfolio)
        with mock.patch.object(portfolio_module.market_prices, "fn", return_value=mock_prices):
            result = portfolio_chart_fn()

            assert "持仓盈亏图表" in result
            assert "-" in result

    def test_chart_handles_price_fetch_failure(self):
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.0,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            }
        }

        temp_portfolio = type(self).temp_portfolio
        os.makedirs(os.path.dirname(temp_portfolio), exist_ok=True)
        with open(temp_portfolio, "w") as f:
            json.dump(test_data, f)

        def mock_error(*args, **kwargs):
            raise Exception("API Error")

        utils_module.PORTFOLIO_FILE = str(temp_portfolio)
        constants.PORTFOLIO_FILE = str(temp_portfolio)
        with mock.patch.object(portfolio_module.market_prices, "fn", side_effect=mock_error):
            result = portfolio_chart_fn()

            assert "持仓盈亏图表" in result
            assert "0.00%" in result

    def test_chart_with_multiple_holdings(self):
        test_data = {
            "000001.sh": {
                "symbol": "000001",
                "price": 10.0,
                "volume": 100,
                "market": "sh",
                "time": datetime.now().isoformat(),
            },
            "000002.sz": {
                "symbol": "000002",
                "price": 20.0,
                "volume": 50,
                "market": "sz",
                "time": datetime.now().isoformat(),
            },
        }

        temp_portfolio = type(self).temp_portfolio
        os.makedirs(os.path.dirname(temp_portfolio), exist_ok=True)
        with open(temp_portfolio, "w") as f:
            json.dump(test_data, f)

        mock_prices = "date,open,high,low,close\n2024-01-01,9.5,11.5,9.0,11.0"

        utils_module.PORTFOLIO_FILE = str(temp_portfolio)
        constants.PORTFOLIO_FILE = str(temp_portfolio)
        with mock.patch.object(portfolio_module.market_prices, "fn", return_value=mock_prices):
            result = portfolio_chart_fn()

            assert "持仓盈亏图表" in result
            assert "000001" in result
            assert "000002" in result
            assert "最大波动" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
