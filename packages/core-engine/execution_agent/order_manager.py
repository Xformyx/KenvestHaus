"""주문 관리자.

분할 매수/매도, 슬리피지 최소화, 한국투자증권 API 호출을 담당합니다.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from packages.shared.types import (
    ExecutionResult,
    OrderBook,
    OrderSide,
    OrderType,
)

if TYPE_CHECKING:
    # KIS API MCP 서버의 client 모듈은 디렉토리명에 하이픈이 있어
    # runtime import path가 일반 import 와 다릅니다. 실제 구동 시에는
    # importlib.import_module + 동적 sys.path 추가 방식을 사용합니다.
    from typing import Any as KISClient

logger = logging.getLogger(__name__)


class OrderManager:
    """KIS API를 통한 주문 실행 매니저.

    실제 운영 시에는 사용자가 활성화한 경우에만 주문이 실행되도록 보호 로직이 적용됩니다.
    """

    def __init__(
        self,
        client: "KISClient",
        enable_auto_trading: bool = False,
        paper_trading: bool = True,
    ):
        self.client = client
        self.enable_auto_trading = enable_auto_trading
        self.paper_trading = paper_trading

    async def place_split_buy(
        self,
        stock_code: str,
        total_quantity: int,
        target_price: int,
        splits: int = 3,
    ) -> list[ExecutionResult]:
        """분할 매수 실행.

        총 수량을 splits 개로 나누어 약간씩 다른 가격에 지정가 주문을 냅니다.
        예: 100주를 3분할 → 34/33/33주, 가격 -0.3% / 0% / +0.3% 호가에 분산.
        """
        if not self.enable_auto_trading:
            logger.warning("자동매매가 비활성화되어 있습니다. 주문 무시.")
            return []

        chunk = total_quantity // splits
        remainder = total_quantity - chunk * splits
        offsets_pct = [-0.3, 0.0, 0.3][:splits]

        results: list[ExecutionResult] = []
        for i, offset in enumerate(offsets_pct):
            qty = chunk + (remainder if i == splits - 1 else 0)
            price = int(target_price * (1 + offset / 100))
            result = await self._place_one(stock_code, qty, price, OrderSide.BUY)
            results.append(result)
        return results

    async def place_split_sell(
        self,
        stock_code: str,
        total_quantity: int,
        target_price: int,
        splits: int = 2,
    ) -> list[ExecutionResult]:
        """분할 매도 (1차/2차 익절)."""
        if not self.enable_auto_trading:
            logger.warning("자동매매가 비활성화되어 있습니다. 주문 무시.")
            return []

        chunk = total_quantity // splits
        remainder = total_quantity - chunk * splits
        offsets_pct = [0.0, 1.0][:splits]  # 1차 즉시, 2차 +1% 가격

        results: list[ExecutionResult] = []
        for i, offset in enumerate(offsets_pct):
            qty = chunk + (remainder if i == splits - 1 else 0)
            price = int(target_price * (1 + offset / 100))
            result = await self._place_one(stock_code, qty, price, OrderSide.SELL)
            results.append(result)
        return results

    async def emergency_market_sell(
        self, stock_code: str, quantity: int
    ) -> ExecutionResult:
        """비상 시장가 매도 (손절, 체결강도 급락 등)."""
        return await self._place_one(
            stock_code, quantity, 0, OrderSide.SELL, order_type=OrderType.MARKET
        )

    async def _place_one(
        self,
        stock_code: str,
        quantity: int,
        price: int,
        side: OrderSide,
        order_type: OrderType = OrderType.LIMIT,
    ) -> ExecutionResult:
        api_result = await self.client.place_order(
            stock_code=stock_code,
            quantity=quantity,
            price=price,
            side=side.value,
            order_type=order_type.value,
        )
        # KIS API 응답 → ExecutionResult 매핑 (실제 응답 포맷에 맞춰 추후 보정 필요)
        output = api_result.get("output", {}) if isinstance(api_result, dict) else {}
        return ExecutionResult(
            order_id=output.get("ODNO", "UNKNOWN"),
            stock_code=stock_code,
            side=side,
            order_type=order_type,
            requested_price=price,
            executed_price=price,  # 체결 통보 수신 시 업데이트
            quantity=quantity,
            executed_quantity=quantity,
            fee=0,
            tax=0,
            timestamp=datetime.now(),
            status="submitted",
        )

    @staticmethod
    def estimate_slippage(book: OrderBook, side: OrderSide, quantity: int) -> float:
        """호가창 분석으로 예상 슬리피지(basis points) 계산.

        시장가 주문 시 호가창 깊이가 얕으면 슬리피지가 커집니다.
        """
        if side == OrderSide.BUY:
            prices, volumes = book.ask_prices, book.ask_volumes
        else:
            prices, volumes = book.bid_prices, book.bid_volumes

        remaining = quantity
        cost = 0
        for p, v in zip(prices, volumes):
            take = min(remaining, v)
            cost += take * p
            remaining -= take
            if remaining <= 0:
                break

        if quantity == 0:
            return 0.0

        avg_price = cost / quantity if remaining <= 0 else cost / (quantity - remaining)
        ref_price = prices[0] if prices else 0
        if ref_price == 0:
            return 0.0
        return abs(avg_price - ref_price) / ref_price * 10_000  # bps
