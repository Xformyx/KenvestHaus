"""Macro MCP Server - 글로벌 매크로 및 한국 시장 동조화 분석.

미국 증시 마감 정보 (다우, S&P 500, 나스닥, SOXX, NVDA 등) 와
한국 시장 수혜 테마 매핑(Coupling) 을 제공합니다.
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

server: Server = Server("macro-mcp")


# 미국 ETF/종목 → 한국 수혜 테마/종목 매핑 (텔레그램 매거진 데이터 기반)
US_TO_KR_THEME_MAP = {
    "SOXX": {"theme": "반도체", "leaders": ["삼성전자", "SK하이닉스", "원익QnC"]},
    "SMH": {"theme": "반도체", "leaders": ["삼성전자", "SK하이닉스"]},
    "NVDA": {"theme": "반도체/HBM", "leaders": ["삼성전자", "SK하이닉스", "한미반도체"]},
    "MU": {"theme": "메모리", "leaders": ["SK하이닉스", "삼성전자"]},
    "TSLA": {
        "theme": "2차전지/전기차",
        "leaders": ["LG에너지솔루션", "삼성SDI", "포스코퓨처엠", "에코프로비엠"],
    },
    "URA": {"theme": "원전/우라늄", "leaders": ["두산에너빌리티", "한전기술"]},
    "TSM": {"theme": "파운드리", "leaders": ["삼성전자", "DB하이텍"]},
    "PAVE": {"theme": "인프라/전력", "leaders": ["현대건설", "LS"]},
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_us_market_close",
            description="전일 미국 증시(다우, S&P 500, 나스닥) 종가 및 등락률을 조회합니다.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_us_etf_movers",
            description=(
                "관심 미국 ETF/종목(SOXX, SMH, NVDA, TSLA, URA 등)의 마감 등락률을 조회합니다."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "tickers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["SOXX", "SMH", "NVDA", "TSLA", "URA"],
                    }
                },
            },
        ),
        Tool(
            name="predict_korea_coupling",
            description=(
                "미국 시장 강세 종목에 동조하여 상승이 예상되는 한국 수혜 테마와 종목을 예측합니다. "
                "글로벌 공급망 분석 기반."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "us_movers": {
                        "type": "object",
                        "description": "{ticker: change_pct} 형태의 미국 종목 등락률",
                    }
                },
                "required": ["us_movers"],
            },
        ),
        Tool(
            name="get_usd_krw_rate",
            description="USD/KRW 환율과 변동률을 조회합니다.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_us_to_kr_theme_map",
            description="미국 ETF/종목 → 한국 수혜 테마/종목 매핑 테이블을 반환합니다.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "get_us_to_kr_theme_map":
        return [
            TextContent(
                type="text",
                text=json.dumps(US_TO_KR_THEME_MAP, ensure_ascii=False, indent=2),
            )
        ]
    if name == "predict_korea_coupling":
        us_movers: dict = arguments.get("us_movers", {})
        predictions = []
        for ticker, change_pct in us_movers.items():
            if ticker in US_TO_KR_THEME_MAP and change_pct > 1.0:
                info = US_TO_KR_THEME_MAP[ticker]
                predictions.append(
                    {
                        "us_trigger": ticker,
                        "us_change_pct": change_pct,
                        "kr_theme": info["theme"],
                        "kr_leaders": info["leaders"],
                        "expected_direction": "상승",
                    }
                )
        return [
            TextContent(
                type="text", text=json.dumps({"predictions": predictions}, ensure_ascii=False, indent=2)
            )
        ]

    placeholder = {
        "status": "not_implemented",
        "tool": name,
        "arguments": arguments,
        "note": "Yahoo Finance API 등 외부 데이터 소스 연결 후 구현됩니다.",
    }
    return [TextContent(type="text", text=json.dumps(placeholder, ensure_ascii=False, indent=2))]


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
