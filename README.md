# 📈 AkTools Pro MCP Server

<p align="left">
    <a href="https://github.com/tchivs/mcp-aktools/releases"><img src="https://img.shields.io/github/v/release/tchivs/mcp-aktools?color=blue&label=version" alt="Version"></a>
    <a href="https://github.com/tchivs/mcp-aktools/blob/main/LICENSE"><img src="https://img.shields.io/github/license/tchivs/mcp-aktools?color=orange" alt="License"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python"></a>
    <a href="https://github.com/jlowin/fastmcp"><img src="https://img.shields.io/badge/Powered%20by-FastMCP-blue" alt="FastMCP"></a>
    <a href="https://github.com/tchivs/mcp-aktools/stargazers"><img src="https://img.shields.io/github/stars/tchivs/mcp-aktools" alt="GitHub stars"></a>
    <a href="https://github.com/tchivs/mcp-aktools/network/members"><img src="https://img.shields.io/github/forks/tchivs/mcp-aktools" alt="GitHub forks"></a>
</p>

<!-- mcp-name: io.github.tchivs/aktools-pro -->
基于 [akshare](https://github.com/akfamily/akshare) 的增强型 MCP (Model Context Protocol) 服务器，为 AI Agent 提供专业的金融数据查询、深度分析及实战交易技能。

## 🌟 核心亮点

- 🧠 **不仅是工具，更是技能**: 支持 MCP Prompts 和 Resources，内置金融分析 SOP。
- 💹 **全市场覆盖**: A股、港股、美股、加密货币数据一站式获取。
- 📊 **可视化增强**: 支持 ASCII 字符走势图，让 AI 的分析更直观。
- 🛡️ **双层缓存**: 内存 + 磁盘双层缓存机制，极致响应速度，保护数据源。
- 💼 **实战模拟**: 内置模拟持仓管理，支持 AI 自动跟踪盈亏。
- 🧪 **策略回测**: 内置极简回测引擎，支持验证均线、RSI、MACD 等交易策略。

---

## 💎 AkTools Pro vs 原版区别 (Why Pro?)

本项目 fork 自 [aahl/mcp-aktools](https://github.com/aahl/mcp-aktools)，并在其基础上进行了深度的工程化重构与功能增强。主要区别如下：

| 维度 | AkTools (原版) | AkTools Pro (本版本) |
| :--- | :--- | :--- |
| **项目架构** | 单文件 (`__init__.py` > 900行) | **标准模块化包结构**，易于扩展和维护 |
| **回测能力** | ❌ 无 | ✅ **内置 Backtesting 引擎**，支持 SMA/RSI/MACD 策略验证 |
| **实战功能** | ❌ 无 | ✅ **模拟盘持仓管理** (`portfolio_add/view`)，实时跟踪胜率 |
| **视觉增强** | ❌ 仅限纯文本/CSV | ✅ **ASCII 字符趋势图** (`draw_ascii_chart`)，分析更直观 |
| **市场雷达** | ❌ 基础行情抓取 | ✅ **实时异动监控** (火箭发射/封板等) 与 **北向资金** 追踪 |
| **Agent 支持** | 基础 Tool 调用 | ✅ **全功能技能引擎**：内置 Prompts、Resources 与 `AGENTS.md` SOP |
| **工程质量** | 基础实现 | ✅ **严格类型提示**、Ruff 规范检查与自动缓存机制 |

---

## 🚀 快速开始 (aktools-pro)

### 方式 1: 自动安装 (推荐)

在你的 AI 终端中根据客户端类型执行：

#### **OpenCode (Sisyphus)**
直接运行交互式命令：
```bash
opencode mcp add
```
按照提示进行操作：
1. **Location**: 选择 `Global`
2. **Name**: 输入 `aktools-pro`
3. **Type**: 选择 `Local`
4. **Command**: 输入 `uvx aktools-pro`

#### **Claude Code / OpenAI Codex**
```bash
# Claude Code
claude mcp add aktools-pro -- uvx aktools-pro

# OpenAI Codex (或其他支持 CLI 安装的客户端)
codex mcp add aktools-pro -- uvx aktools-pro
```

#### **Cursor / VS Code / Cherry Studio**
- **Cursor**: 手动在 `mcpServers` 配置中添加以下 JSON，或 [点击一键安装](https://cursor.com/zh/install-mcp?name=aktools-pro&config=eyJjb21tYW5kIjoiaXZ4IiwiYXJncyI6WyJha3Rvb2xzLXBybyJdfQ==)
- **VS Code**: [![Install MCP Server](https://img.shields.io/badge/VS_Code-+?label=Add+MCP+Server&color=0098FF)](https://insiders.vscode.dev/redirect?url=vscode:mcp/install%3F%7B%22name%22%3A%22aktools-pro%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22aktools-pro%22%5D%7D)
- **Cherry Studio**: [![Install MCP Server](https://img.shields.io/badge/Cherry_Studio-+?label=Add+MCP+Server&color=FF5F5F)](https://gitee.com/link?target=cherrystudio%3A%2F%2Fmcp%2Finstall%3Fservers%3DeyJtY3BTZXJ2ZXJzIjp7ImFrdG9vbHMtcHJvIjp7ImNvbW1hbmQiOiJ1dngiLCJhcmdzIjpbImFrdG9vbHMtcHJvIl19fX0%3D)

```json
"aktools-pro": {
  "command": "uvx",
  "args": ["aktools-pro"]
}
```

### 方式 2: Docker
```bash
mkdir /opt/aktools-pro
cd /opt/aktools-pro
wget https://raw.githubusercontent.com/tchivs/mcp-aktools/main/docker-compose.yml
docker-compose up -d
```

### ⚙️ 环境变量配置 (Optional)
无论通过 `uvx` 还是 `Docker` 安装，均支持以下环境变量：

| 变量名 | 说明 | 默认值 / 示例 |
| :--- | :--- | :--- |
| `OKX_BASE_URL` | OKX 代理地址 (避开网络限制) | `https://okx.com` |
| `BINANCE_BASE_URL` | 币安代理地址 | `https://www.binance.com` |
| `NEWSNOW_BASE_URL` | 财经资讯接口地址 | `https://newsnow.busiyi.world` |
| `NEWSNOW_CHANNELS` | 资讯频道 (逗号分隔) | `wallstreetcn-quick,cls-telegraph,jin10` |
| `PORT` | HTTP 模式下的监听端口 | `80` |
| `TRANSPORT` | MCP 传输协议类型 | `stdio` (可选 `http`, `sse`) |

### 方式 3: Smithery (即将支持)
> 敬请期待专属 AkTools Pro 的 Smithery 快速集成。

---

## 🧠 高级技能 (Advanced Skills)

本项目为 OpenCode / Claude Code 注入了深度金融分析技能：

### 1. 提示词工作流 (Prompts)
- `analyze-stock`: 触发资深分析师人格，对个股进行技术面+基本面+消息面的全方位诊断。
- `market-pulse`: 研判大盘脉搏，分析涨停家数与板块资金流向。
- `analyze-crypto`: 触发加密货币分析师人格，对币种进行技术面+情绪面的深度分析。
- `crypto-pulse`: 研判币圈脉搏，分析恐惧贪婪指数、资金费率与持仓量。
- `analyze-precious-metal`: 触发贵金属分析师人格，对黄金/白银进行全方位诊断。
- `precious-metal-pulse`: 研判贵金属市场脉搏，分析ETF持仓与库存变化。

### 2. 知识库资源 (Resources)
- `skill://trading/logic/technical-analysis`: 内置 MACD、RSI、布林带等指标的专业解读标准。
- `skill://trading/strategy/risk-management`: 内置仓位管理与止损风险控制准则。
- `skill://crypto/logic/analysis-sop`: 内置加密货币分析 SOP（多空比、资金费率、RSI 阈值解读）。
- `skill://trading/logic/precious-metals-analysis`: 内置贵金属分析SOP（内外盘价差、ETF持仓、期现基差解读）。

### 3. 复合工具 (Composite Tools)
- `composite_stock_diagnostic`: 一键获取聚合后的诊断报告。
- `draw_ascii_chart`: 在聊天框中直接生成价格趋势字符图。
- `market_anomaly_scan`: 实时扫描“火箭发射”、“大笔买入”等市场异动。
- `backtest_strategy`: 基于历史数据验证交易策略（SMA/RSI/MACD）。
- `sector_valuation` / `sector_rotation`: 研判行业估值水平与资金轮动方向。
- `northbound_funds`: 跟踪北向资金（聪明钱）的每日流入流出。
- `institutional_holding_summary`: 汇总个股的机构持仓深度信息。

---

## 🛠️ 常用工具列表

<details>
<summary><strong>📈 股票 & 市场</strong></summary>

- `search`: 关键词查找代码
- `stock_info`: 基本信息
- `stock_prices`: 历史价格 (含技术指标)
- `stock_indicators_a/hk/us`: 财务关键指标
- `stock_zt_pool_em`: 涨停股池
- `stock_lhb_ggtj_sina`: 龙虎榜统计

</details>

<details>
<summary><strong>₿ 加密货币</strong></summary>

- `okx_prices`: K线数据 (含技术指标)
- `okx_loan_ratios`: 杠杆多空比
- `okx_taker_volume`: 主动买卖量
- `okx_funding_rate`: 永续合约资金费率
- `okx_open_interest`: 合约持仓量
- `fear_greed_index`: 市场恐惧贪婪指数
- `binance_ai_report`: 币安 AI 深度报告
- `crypto_composite_diagnostic`: 一键综合诊断
- `draw_crypto_chart`: ASCII 走势图
- `backtest_crypto_strategy`: 策略回测

</details>

<details>
<summary><strong>🥇 贵金属</strong></summary>

- `pm_spot_prices`: 上海金交所现货价格
- `pm_international_prices`: 国际贵金属价格 (伦敦金/银, COMEX)
- `pm_etf_holdings`: ETF持仓变化 (SPDR GLD, iShares SLV)
- `pm_comex_inventory`: COMEX库存数据
- `pm_basis`: 期现基差
- `pm_benchmark_price`: 上海金/银基准价
- `pm_composite_diagnostic`: 贵金属综合诊断

</details>

<details>
<summary><strong>💼 模拟实战</strong></summary>

- `portfolio_add`: 加入模拟持仓
- `portfolio_view`: 查看实时盈亏
- `trading_suggest`: AI 投资建议

</details>

---

## 👨‍💻 开发与贡献

本项目遵循 `AGENTS.md` 中的 **OpenCode / Sisyphus** 开发规范。

```bash
# 同步环境
uv sync

# 本地运行 (stdio)
uv run aktools-pro

# 检查技能注册情况
uv run aktools-pro inspect
```

---

<p align="center">
    Built with ❤️ for the Quantitative Trading Community
</p>
