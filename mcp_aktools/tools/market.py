import os
from datetime import datetime, timedelta

import akshare as ak
import pandas as pd
import requests
from pydantic import Field

from ..server import mcp
from ..shared.constants import USER_AGENT
from ..shared.utils import ak_cache, recent_trade_date


@mcp.tool(
    title="获取当前时间及A股交易日信息",
    description="获取当前系统时间及A股交易日信息，建议在调用其他需要日期参数的工具前使用该工具",
)
def get_current_time():
    now = datetime.now()
    week = "日一二三四五六日"[now.isoweekday()]
    texts = [f"当前时间: {now.isoformat()}, 星期{week}"]
    dfs = ak_cache(ak.tool_trade_date_hist_sina, ttl=43200)
    if dfs is not None:
        start = now.date() - timedelta(days=5)
        ended = now.date() + timedelta(days=5)
        dates = [d.strftime("%Y-%m-%d") for d in dfs["trade_date"] if start <= d <= ended]
        texts.append(f", 最近交易日有: {','.join(dates)}")
    return "".join(texts)


@mcp.tool(
    title="A股涨停股池",
    description="获取中国A股市场(上证、深证)的所有涨停股票",
)
def stock_zt_pool_em(
    date: str = Field("", description="交易日日期(可选)，默认为最近的交易日，格式: 20251231"),
    limit: int = Field(50, description="返回数量(int,30-100)", strict=False),
):
    if not date:
        date = recent_trade_date().strftime("%Y%m%d")
    dfs = ak_cache(ak.stock_zt_pool_em, date=date, ttl=1200)
    if dfs is None:
        return "获取涨停股池数据失败"
    if dfs.empty:
        return "获取涨停股池数据失败"
    cnt = len(dfs)
    try:
        dfs.drop(columns=["序号", "流通市值", "总市值"], inplace=True)
    except Exception:
        pass
    dfs.sort_values("成交额", ascending=False, inplace=True)
    dfs = dfs.head(int(limit))
    desc = f"共{cnt}只涨停股\n"
    return desc + dfs.to_csv(index=False, float_format="%.2f").strip()


@mcp.tool(
    title="A股强势股池",
    description="获取中国A股市场(上证、深证)的强势股池数据",
)
def stock_zt_pool_strong_em(
    date: str = Field("", description="交易日日期(可选)，默认为最近的交易日，格式: 20251231"),
    limit: int = Field(50, description="返回数量(int,30-100)", strict=False),
):
    if not date:
        date = recent_trade_date().strftime("%Y%m%d")
    dfs = ak_cache(ak.stock_zt_pool_strong_em, date=date, ttl=1200)
    if dfs is None:
        return "获取强势股池数据失败"
    if dfs.empty:
        return "获取强势股池数据失败"
    try:
        dfs.drop(columns=["序号", "流通市值", "总市值"], inplace=True)
    except Exception:
        pass
    dfs.sort_values("成交额", ascending=False, inplace=True)
    dfs = dfs.head(int(limit))
    return dfs.to_csv(index=False, float_format="%.2f").strip()


@mcp.tool(
    title="A股龙虎榜统计",
    description="获取中国A股市场(上证、深证)的龙虎榜个股上榜统计数据",
)
def stock_lhb_ggtj_sina(
    days: str = Field("5", description="统计最近天数，仅支持: [5/10/30/60]"),
    limit: int = Field(50, description="返回数量(int,30-100)", strict=False),
):
    dfs = ak_cache(ak.stock_lhb_ggtj_sina, symbol=days, ttl=3600)
    if dfs is None:
        return "获取龙虎榜统计数据失败"
    if dfs.empty:
        return "获取龙虎榜统计数据失败"
    dfs = dfs.head(int(limit))
    return dfs.to_csv(index=False, float_format="%.2f").strip()


@mcp.tool(
    title="A股板块资金流",
    description="获取中国A股市场(上证、深证)的行业资金流向数据",
)
def stock_sector_fund_flow_rank(
    days: str = Field("今日", description="天数，仅支持: {'今日','5日','10日'}，如果需要获取今日数据，请确保是交易日"),
    cate: str = Field("行业资金流", description="仅支持: {'行业资金流','概念资金流','地域资金流'}"),
):
    dfs = ak_cache(ak.stock_sector_fund_flow_rank, indicator=days, sector_type=cate, ttl=1200)
    if dfs is None:
        return "获取数据失败"
    try:
        dfs.sort_values("今日涨跌幅", ascending=False, inplace=True)
        dfs.drop(columns=["序号"], inplace=True)
    except Exception:
        pass
    try:
        dfs = pd.concat([dfs.head(20), dfs.tail(20)])
        return dfs.to_csv(index=False, float_format="%.2f").strip()
    except Exception as exc:
        return str(exc)


@mcp.tool(
    title="北向资金近况",
    description="获取北向资金近 10 个交易日数据",
)
def northbound_funds():
    dfs = ak_cache(ak.stock_hsgt_hist_em, symbol="北向资金", ttl=3600)
    if dfs is None or dfs.empty:
        return "获取北向资金数据失败"
    try:
        dfs = dfs.tail(10)
    except Exception:
        pass
    return dfs.to_csv(index=False, float_format="%.2f").strip()


@mcp.tool(
    title="行业估值水平",
    description="获取申万一级行业估值(P/E、P/B)概览",
)
def sector_valuation():
    dfs = ak_cache(ak.sw_index_first_info, ttl=43200)
    if dfs is None or dfs.empty:
        return "获取行业估值数据失败"
    if "市盈率" in dfs.columns:
        dfs["市盈率"] = pd.to_numeric(dfs["市盈率"], errors="coerce")
    if "市净率" in dfs.columns:
        dfs["市净率"] = pd.to_numeric(dfs["市净率"], errors="coerce")
    try:
        if "市盈率" in dfs.columns:
            dfs.sort_values("市盈率", inplace=True)
        if "序号" in dfs.columns:
            dfs.drop(columns=["序号"], inplace=True)
    except Exception:
        pass
    return dfs.head(50).to_csv(index=False, float_format="%.2f").strip()


@mcp.tool(
    title="行业轮动",
    description="基于行业资金流与涨跌幅识别短期强势行业",
)
def sector_rotation():
    dfs = ak_cache(ak.stock_sector_fund_flow_rank, indicator="今日", sector_type="行业资金流", ttl=1200)
    if dfs is None or dfs.empty:
        return "获取行业轮动数据失败"
    try:
        if "今日涨跌幅" in dfs.columns:
            dfs["今日涨跌幅"] = pd.to_numeric(dfs["今日涨跌幅"], errors="coerce")
            dfs.sort_values("今日涨跌幅", ascending=False, inplace=True)
        elif "净流入" in dfs.columns:
            dfs["净流入"] = pd.to_numeric(dfs["净流入"], errors="coerce")
            dfs.sort_values("净流入", ascending=False, inplace=True)
        if "序号" in dfs.columns:
            dfs.drop(columns=["序号"], inplace=True)
    except Exception:
        pass
    return dfs.head(15).to_csv(index=False, float_format="%.2f").strip()


@mcp.tool(
    title="全球财经快讯",
    description="获取最新的全球财经快讯",
)
def stock_news_global():
    news = []
    try:
        dfs = ak_cache(ak.stock_info_global_sina, ttl=300, key="stock_info_global_sina")
        if dfs is not None and not dfs.empty:
            csv = dfs.to_csv(index=False, float_format="%.2f").strip()
            csv = csv.replace(datetime.now().strftime("%Y-%m-%d "), "")
            news.extend(csv.split("\n"))
    except Exception:
        pass
    news.extend(newsnow_news())
    return "\n".join(news)


def newsnow_news(channels=None):
    base = os.getenv("NEWSNOW_BASE_URL")
    if not base:
        return []
    if not channels:
        channels = os.getenv("NEWSNOW_CHANNELS") or "wallstreetcn-quick,cls-telegraph,jin10"
    if isinstance(channels, str):
        channels = channels.split(",")
    all_news = []
    try:
        res = requests.post(
            f"{base}/api/s/entire",
            json={"sources": channels},
            headers={
                "User-Agent": USER_AGENT,
                "Referer": base,
            },
            timeout=60,
        )
        lst = res.json() or []
        for item in lst:
            for v in item.get("items", [])[0:15]:
                title = v.get("title", "")
                extra = v.get("extra") or {}
                hover = extra.get("hover") or title
                info = extra.get("info") or ""
                all_news.append(f"{hover} {info}".strip().replace("\n", " "))
    except Exception:
        pass
    return all_news


@mcp.tool(
    title="全市场异动扫描",
    description="扫描 A 股市场实时的异动信号，如火箭发射、大笔买入、快速反弹等",
)
def market_anomaly_scan(
    symbol: str = Field(
        "火箭发射",
        description="异动类型，可选: 火箭发射, 快速反弹, 加速下跌, 高台跳水, 大笔买入, 大笔卖出, 封涨停板, 打开涨停板",
    ),
):
    try:
        dfs = ak_cache(ak.stock_changes_em, symbol=symbol, ttl=30, key=f"stock_changes_em-{symbol}")
        if dfs is None or dfs.empty:
            return f"当前没有检测到 [{symbol}] 类型的异动信号"
        dfs = dfs.head(20)
        dfs.rename(
            columns={
                "时间": "异动时间",
                "代码": "股票代码",
                "名称": "股票名称",
                "板块": "所属板块",
                "相关信息": "异动详情",
            },
            inplace=True,
        )
        return f"--- 实时异动扫描报告 [{symbol}] ---\n" + dfs.to_csv(index=False)
    except Exception as e:
        return f"异动扫描失败: {str(e)}"
