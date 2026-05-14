"""News & Sentiment MCP Server - 뉴스 크롤링 및 감성 분석.

네이버 금융 뉴스, 종목별 뉴스를 크롤링하고 NLP로 호재/악재를 분류합니다.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

logger = logging.getLogger(__name__)

server: Server = Server("news-sentiment-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="crawl_stock_news",
            description="특정 종목의 최근 뉴스 기사를 네이버 금융에서 크롤링합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {"type": "string"},
                    "limit": {"type": "integer", "default": 20},
                },
                "required": ["stock_code"],
            },
        ),
        Tool(
            name="analyze_sentiment",
            description=(
                "뉴스 텍스트의 감성을 분석하여 호재(positive)/악재(negative)/중립(neutral)으로 분류합니다."
            ),
            inputSchema={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        ),
        Tool(
            name="get_market_sentiment_summary",
            description="당일 전체 시장 뉴스의 호재/악재 비율을 요약합니다.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_global_macro_news",
            description="미국 증시 마감, 환율, 원자재 등 글로벌 매크로 뉴스를 조회합니다.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    # TODO: 실제 구현 시 BeautifulSoup으로 크롤링 + KoBERT/Transformer 모델로 감성 분석
    placeholder = {
        "status": "not_implemented",
        "tool": name,
        "arguments": arguments,
    }
    return [TextContent(type="text", text=json.dumps(placeholder, ensure_ascii=False, indent=2))]


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
