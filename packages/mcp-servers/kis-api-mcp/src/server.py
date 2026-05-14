"""한국투자증권 MCP 서버.

MCP(Model Context Protocol) 표준 인터페이스로 한국투자증권 API를 노출합니다.
Cursor, Claude Desktop 등 MCP Host에서 이 서버를 등록하여 사용할 수 있습니다.

실행:
    python -m packages.mcp-servers.kis-api-mcp.src.server
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .client import KISClient

logger = logging.getLogger(__name__)

server: Server = Server("kis-api-mcp")
_client: KISClient | None = None


def _get_client() -> KISClient:
    global _client
    if _client is None:
        _client = KISClient()
    return _client


@server.list_tools()
async def list_tools() -> list[Tool]:
    """이 MCP 서버가 제공하는 도구 목록."""
    return [
        Tool(
            name="kis_get_current_price",
            description="한국투자증권 API로 종목의 현재가, 등락률, 거래량을 조회합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "6자리 종목코드 (예: 005380 현대차)",
                    }
                },
                "required": ["stock_code"],
            },
        ),
        Tool(
            name="kis_get_order_book",
            description="10단계 호가창 정보를 조회합니다. OBI 계산에 사용됩니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {"type": "string"},
                },
                "required": ["stock_code"],
            },
        ),
        Tool(
            name="kis_get_ohlcv",
            description="일봉/주봉/월봉 OHLCV 데이터를 조회합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {"type": "string"},
                    "period": {
                        "type": "string",
                        "enum": ["D", "W", "M"],
                        "default": "D",
                    },
                    "count": {"type": "integer", "default": 100},
                },
                "required": ["stock_code"],
            },
        ),
        Tool(
            name="kis_get_balance",
            description="계좌 주식 잔고와 평가 손익을 조회합니다.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="kis_place_order",
            description=(
                "현금 주식 주문을 실행합니다. "
                "주의: enable_auto_trading=True 인 경우에만 실전 주문이 가능합니다."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {"type": "string"},
                    "quantity": {"type": "integer"},
                    "price": {"type": "integer"},
                    "side": {"type": "string", "enum": ["buy", "sell"]},
                    "order_type": {
                        "type": "string",
                        "enum": ["limit", "market"],
                        "default": "limit",
                    },
                },
                "required": ["stock_code", "quantity", "price", "side"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """MCP 도구 호출 핸들러."""
    client = _get_client()
    try:
        if name == "kis_get_current_price":
            result = await client.get_current_price(arguments["stock_code"])
        elif name == "kis_get_order_book":
            result = await client.get_order_book(arguments["stock_code"])
        elif name == "kis_get_ohlcv":
            result = await client.get_ohlcv(
                arguments["stock_code"],
                arguments.get("period", "D"),
                arguments.get("count", 100),
            )
        elif name == "kis_get_balance":
            result = await client.get_balance()
        elif name == "kis_place_order":
            result = await client.place_order(
                arguments["stock_code"],
                arguments["quantity"],
                arguments["price"],
                arguments["side"],
                arguments.get("order_type", "limit"),
            )
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        import json

        return [
            TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2),
            )
        ]
    except Exception as e:
        logger.exception("Tool %s failed", name)
        return [TextContent(type="text", text=f"Error: {e}")]


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
