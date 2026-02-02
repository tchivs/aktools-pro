import argparse
import os
from typing import Literal, cast

# 导入 main 需要用到的中间件
from starlette.middleware.cors import CORSMiddleware

# 触发装饰器注册
from . import prompts, resources
from .server import mcp
from .tools import analysis, crypto, forex, market, portfolio, precious_metals, stocks

__all__ = [
    "analysis",
    "crypto",
    "forex",
    "market",
    "mcp",
    "portfolio",
    "precious_metals",
    "prompts",
    "resources",
    "stocks",
]


def _run_inspect():
    """列出所有注册的工具、resources 和 prompts."""
    # Show instructions first if available
    if mcp.instructions:
        print("=== Server Instructions ===")
        print(mcp.instructions)
        print("\n")

    print("=== Registered Tools ===")
    for name, tool in sorted(mcp._tool_manager._tools.items()):
        mcp_tool = tool.to_mcp_tool()
        print(f"\n{name}:")
        print(f"  title: {mcp_tool.title}")
        print(f"  description: {mcp_tool.description}")

    print("\n\n=== Registered Resources ===")
    for uri, resource in sorted(mcp._resource_manager._resources.items()):
        print(f"\n{uri}:")
        print(f"  name: {resource.name}")
        print(f"  description: {resource.description}")
        print(f"  mime_type: {resource.mime_type}")

    print("\n\n=== Registered Prompts ===")
    for name, prompt in sorted(mcp._prompt_manager._prompts.items()):
        mcp_prompt = prompt.to_mcp_prompt()
        print(f"\n{name}:")
        print(f"  description: {mcp_prompt.description}")


def main():
    port = int(os.getenv("PORT", 0)) or 80
    parser = argparse.ArgumentParser(description="AkTools MCP Server")
    subparsers = parser.add_subparsers(dest="command")

    # inspect 子命令
    subparsers.add_parser("inspect", help="List all registered tools, resources and prompts")

    # 运行服务器参数 (作为默认行为)
    parser.add_argument("--http", action="store_true", help="Use streamable HTTP mode instead of stdio")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=port, help=f"Port to listen on (default: {port})")

    args = parser.parse_args()

    if args.command == "inspect":
        _run_inspect()
        return

    mode = os.getenv("TRANSPORT") or ("http" if args.http else None)
    if mode in ["http", "sse", "streamable-http"]:
        transport = cast(Literal["http", "sse", "streamable-http"], mode)
        app = mcp.http_app(transport=transport)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["mcp-session-id", "mcp-protocol-version"],
            max_age=86400,
        )
        mcp.run(transport=transport, host=args.host, port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
