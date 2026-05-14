"""Magazine MCP Server - 데일리 트레이더스 매거진 자동 생성.

사용자 텔레그램 데이터의 매거진 PDF와 동일한 형태의 일일 시장 리포트를 LLM이 자동 작성합니다.
다른 MCP 서버들(macro, fundamental, news-sentiment, kis-api)의 도구를 호출하여 데이터를 수집하고
구조화된 매거진을 생성합니다.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

logger = logging.getLogger(__name__)

server: Server = Server("magazine-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="generate_daily_magazine",
            description=(
                "데일리 트레이더스 매거진을 자동 생성합니다. "
                "글로벌 마켓, 美 자금 흐름, 강세 테마, 신의 한수 TOP3, "
                "중장기 추천, 속보 뉴스, 내일 시장 전망(시나리오)을 포함합니다."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "publish_date": {
                        "type": "string",
                        "description": "YYYY-MM-DD 형식. 기본값은 오늘",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["markdown", "pdf"],
                        "default": "markdown",
                    },
                },
            },
        ),
        Tool(
            name="generate_after_hours_strategy",
            description=(
                "마감 후 내일 전략 알림을 생성합니다. "
                "성격 모드, 종합 위험도, 활성 단타 추적, 중장기 진입 후보, 액션 플랜을 포함합니다."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="generate_closing_summary",
            description="장마감 종합정리 (TOP 테마, 상한가, 내일 상승여력 TOP3, AI 학습 결과)를 생성합니다.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="generate_lunch_checkin",
            description="점심시간 중간 점검 메시지를 생성합니다.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "generate_daily_magazine":
        publish_date = arguments.get("publish_date", datetime.now().strftime("%Y-%m-%d"))
        # 실제 구현 시: macro-mcp, news-sentiment-mcp, fundamental-mcp 도구를 LLM이 조합 호출
        sample = _sample_magazine_skeleton(publish_date)
        return [TextContent(type="text", text=sample)]

    placeholder = {
        "status": "not_implemented",
        "tool": name,
        "arguments": arguments,
        "note": "다른 MCP 서버 + LLM Host와 함께 동작합니다.",
    }
    return [TextContent(type="text", text=json.dumps(placeholder, ensure_ascii=False, indent=2))]


def _sample_magazine_skeleton(publish_date: str) -> str:
    """매거진의 마크다운 스켈레톤."""
    return f"""# 데일리 트레이더스 매거진
## {publish_date}

### 오늘의 헤드라인
- (자동 생성 예정)

### 글로벌 마켓
| 항목 | 값 | 변동 | 해석 |
| :--- | :--- | :--- | :--- |
| 다우 | - | - | - |
| S&P 500 | - | - | - |
| 나스닥 | - | - | - |

### 美 자금 흐름 → 韓 수혜 테마
(macro-mcp 결과로 채워질 예정)

### 신의 한수 TOP 3 / 중장기 투자 추천
(fundamental-mcp 결과로 채워질 예정)

### 속보 뉴스 (호재/악재)
(news-sentiment-mcp 결과로 채워질 예정)

### 내일 시장 예측 시나리오
| 시나리오 | 확률 | 예상 범위 | 트리거 / 대응 |
| :--- | :--- | :--- | :--- |
| 상승 | - | - | - |
| 보합 | - | - | - |
| 하락 | - | - | - |

---
*이 매거진은 KenventHaus magazine-mcp가 자동 생성한 초안입니다.*
"""


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
