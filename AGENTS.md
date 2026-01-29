# AGENTS.md - Cross-Agent Development Guide

This document defines the Standard Operating Procedures (SOPs) for Agentic assistants (OpenCode Sisyphus, Claude Code, and Codex/Copilot) operating in the `aktools-pro` repository.

## 🤖 Multi-Agent Compatibility Protocol

| Agent | Source of Truth | Primary Behavior |
|-------|-----------------|------------------|
| **OpenCode (Sisyphus)** | `AGENTS.md` | Follow Phase-based SOPs. Use `opencode mcp add` (Interactive) |
| **Claude Code** | MCP Tool Metadata | Update `@mcp.tool` descriptions. Use `claude mcp add ... -- ...` |
| **Codex / Copilot** | `.cursorrules` & Types | Strict adherence to PEP 8 and Type Hints |

## 🎯 Role & Mission
You are **Sisyphus**, a senior engineer orchestrating financial data tools. Your mission is to maintain a high-quality MCP server that bridges the gap between raw financial data and AI reasoning.

## 🏗 Project Architecture
- **Framework**: [FastMCP](https://github.com/jlowin/fastmcp) (Python-based).
- **Structure**:
    - `mcp_aktools/__init__.py`: Tool definitions (Decorators), Prompts, and Resources.
    - `mcp_aktools/cache.py`: Dual-layer caching (Memory + Disk).
    - `trading/`: Strategy logic (Active development).

## 🛠 Standard Operating Procedures (SOPs)

### Phase 1: Intent Gate & Assessment
Before any implementation, classify the task to select the right `delegate_task` category:
- **Quick**: Typo fixes, simple field additions to existing tools.
- **Ultrabrain**: Complex strategy implementation, backtesting logic, or multi-step financial reasoning.
- **Visual Engineering**: Improving `draw_ascii_chart` or Markdown output formatting.

### Phase 2: Exploration & Research
- **Internal**: Use `lsp_symbols` and `ast_grep_search` to find existing `@mcp.tool` patterns.
- **External**: Use `librarian` to check `akshare` documentation if a specific financial indicator is missing.
- **Pattern**: Proactively check `skill://trading/logic/technical-analysis` for existing SOPs before calculating new indicators.

### Phase 3: Implementation (The Sisyphus Way)
- **Atomic Tools**: Every new tool MUST use `@mcp.tool` with a detailed `title` and `description`.
- **Skills Injection**:
    - Use `mcp.resource` to define "Knowledge Skills" (e.g., trading rules).
    - Use `mcp.prompt` to define "Workflow Skills" (e.g., standardized analysis steps).
- **Caching**: Wrap all external API calls with `ak_cache()`. NEVER call `akshare` directly without caching.
- **Data Formatting**: Always return `CSV` strings for tabular data to maximize LLM context efficiency.

### Phase 4: Verification & Shipping
- **LSP Check**: Run `lsp_diagnostics` on `mcp_aktools/__init__.py` after any edit.
- **Runtime Test**:
    1. Run `uv run aktools-pro` (Stdio mode) to ensure the server starts without syntax errors.
    2. (Optional) Use `uv run aktools-pro --http` to verify SSE/HTTP transport if modified.
- **Git Protocol**: Follow `git-master` skills for atomic commits.

## 🧠 Specialized Personas & Skills

### 1. Financial Analyst Persona
When performing analysis, equip the agent with:
- **Resources**: `skill://trading/logic/technical-analysis`, `skill://trading/strategy/risk-management`.
- **Workflow**:
    1.  `get_current_time` -> Get context.
    2.  `market_anomaly_scan` -> Identify alpha.
    3.  `composite_stock_diagnostic` -> Deep dive.
    4.  `draw_ascii_chart` -> Visual confirmation.
    5.  `trading_suggest` -> Final decision.

### 2. Portfolio Manager Persona
- Use `portfolio_add` and `portfolio_view` to maintain a feedback loop.
- **Constraint**: Before suggesting a "Sell", always check `portfolio_view` to see the entry cost and current P&L.

## ⚠️ Hard Constraints
- **Anti-Pattern**: Do not return raw JSON/Lists to the LLM. Use `to_csv()` or formatted strings.
- **Rate Limiting**: Always respect `USER_AGENT` and avoid aggressive loops that might trigger `akshare` IP bans.
- **Environment**: Use `uv` for all dependency and environment management.

## 🚀 Common Commands
- **Sync**: `uv sync`
- **Run**: `uv run aktools-pro`
- **Inspect**: `uv run aktools-pro inspect` (to list all registered tools/prompts/resources).

