"""Fundamental MCP Server - 기업/테마 분석 MCP 서버.

DART 전자공시, 재무제표, 업종/테마 정보를 MCP 도구로 노출합니다.
LLM이 이 도구들을 호출하여 종목의 펀더멘털 가치를 종합 평가할 수 있습니다.

실행: python -m packages.mcp-servers.fundamental-mcp.src.server
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

server: Server = Server("fundamental-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_financial_ratios",
            description=(
                "종목의 주요 재무비율(PER, PBR, ROE, 부채비율, 유보율)을 조회합니다. "
                "가치 투자 및 재무 건전성 필터링에 사용됩니다."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {"type": "string", "description": "6자리 종목코드"},
                },
                "required": ["stock_code"],
            },
        ),
        Tool(
            name="get_quarterly_results",
            description="최근 4분기 매출액 및 영업이익 추이를 조회합니다. 성장주 발굴에 사용됩니다.",
            inputSchema={
                "type": "object",
                "properties": {"stock_code": {"type": "string"}},
                "required": ["stock_code"],
            },
        ),
        Tool(
            name="get_dart_disclosures",
            description=(
                "DART 전자공시 시스템에서 최근 공시 목록을 조회합니다. "
                "M&A, 수주, 자사주 매입 등 호재성 공시 분석에 사용됩니다."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {"type": "string"},
                    "days": {"type": "integer", "default": 30},
                },
                "required": ["stock_code"],
            },
        ),
        Tool(
            name="get_strong_themes_today",
            description="당일 강세 테마 TOP N과 주도주를 조회합니다.",
            inputSchema={
                "type": "object",
                "properties": {"top_n": {"type": "integer", "default": 5}},
                "required": [],
            },
        ),
        Tool(
            name="screen_value_stocks",
            description=(
                "가치 투자 스크리닝 - PER, PBR, ROE 기준으로 저평가 우량 종목을 추출합니다."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "max_per": {"type": "number", "default": 10.0},
                    "max_pbr": {"type": "number", "default": 1.0},
                    "min_roe": {"type": "number", "default": 10.0},
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    # TODO: 실제 구현 시 DART OpenAPI 및 FnGuide 데이터를 활용
    placeholder = {
        "status": "not_implemented",
        "tool": name,
        "arguments": arguments,
        "note": "이 도구는 DART API 키 설정 후 구현됩니다. docs/4_final_system_design.md 참조.",
    }
    return [TextContent(type="text", text=json.dumps(placeholder, ensure_ascii=False, indent=2))]


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
