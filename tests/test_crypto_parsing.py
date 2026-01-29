import unittest
from unittest import mock


class TestCryptoParsing(unittest.TestCase):
    def test_safe_float_handles_empty(self) -> None:
        from mcp_aktools.tools.crypto import _safe_float

        self.assertEqual(_safe_float(""), 0.0)
        self.assertEqual(_safe_float(None), 0.0)
        self.assertEqual(_safe_float("0"), 0.0)
        self.assertAlmostEqual(_safe_float("0.001"), 0.001)

    def test_safe_int_handles_empty(self) -> None:
        from mcp_aktools.tools.crypto import _safe_int

        self.assertEqual(_safe_int(""), 0)
        self.assertEqual(_safe_int(None), 0)
        self.assertEqual(_safe_int("0"), 0)
        self.assertEqual(_safe_int("1700000000000"), 1700000000000)

    def test_okx_funding_rate_tolerates_empty_fields(self) -> None:
        # Avoid network; OKX occasionally returns empty strings for numeric fields.
        from mcp_aktools.tools import crypto

        class _Resp:
            def json(self):
                return {
                    "data": [
                        {
                            "fundingRate": "",
                            "nextFundingRate": "",
                            "fundingTime": "",
                        }
                    ]
                }

        with mock.patch.object(crypto.requests, "get", return_value=_Resp()):
            out = crypto.okx_funding_rate.fn("BTC")
        self.assertIn("BTC", out)
        self.assertIn("当前费率", out)
        self.assertIn("预测费率", out)


if __name__ == "__main__":
    unittest.main()
