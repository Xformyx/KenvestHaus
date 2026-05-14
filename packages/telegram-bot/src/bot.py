"""KenvestHaus 텔레그램 봇.

매매 시그널을 사용자에게 전달하는 봇입니다. 시그널 발생 시 core-engine 또는
mcp-servers/magazine-mcp 에서 호출하여 메시지를 발송합니다.

실행: python -m packages.telegram-bot.src.bot
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

import httpx

from packages.shared.config import get_settings

logger = logging.getLogger(__name__)


class TelegramBot:
    """간단한 텔레그램 Bot API 래퍼.

    sendMessage 만 사용하므로 별도 라이브러리 없이 httpx로 직접 호출합니다.
    """

    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        settings = get_settings()
        self.token = token or settings.telegram_bot_token
        self.chat_id = chat_id or settings.telegram_admin_chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None
        self._http = httpx.AsyncClient(timeout=10.0)

    async def close(self) -> None:
        await self._http.aclose()

    async def send(self, text: str, chat_id: Optional[str] = None) -> bool:
        """메시지 발송."""
        if not self.base_url:
            logger.warning("TELEGRAM_BOT_TOKEN이 설정되지 않아 메시지를 발송할 수 없습니다.")
            logger.info("Would send: %s", text[:200])
            return False

        target = chat_id or self.chat_id
        if not target:
            logger.warning("chat_id가 지정되지 않았습니다.")
            return False

        try:
            resp = await self._http.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": target,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.exception("텔레그램 발송 실패: %s", e)
            return False


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = TelegramBot()
    await bot.send("✅ KenvestHaus 텔레그램 봇이 정상적으로 시작되었습니다.")
    await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
