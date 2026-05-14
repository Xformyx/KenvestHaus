"""주식 데이터 관련 타입 정의."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    LIMIT = "limit"  # 지정가
    MARKET = "market"  # 시장가
    CONDITIONAL = "conditional"  # 조건부 지정가


class StockInfo(BaseModel):
    """기본 종목 정보."""

    code: str = Field(..., description="종목 코드, 예: 005380")
    name: str = Field(..., description="종목명, 예: 현대차")
    market: str = Field(..., description="KOSPI | KOSDAQ")
    sector: Optional[str] = None
    industry: Optional[str] = None


class OHLCV(BaseModel):
    """캔들 데이터."""

    timestamp: datetime
    open: int
    high: int
    low: int
    close: int
    volume: int
    trading_value: int = Field(0, description="거래대금")


class OrderBook(BaseModel):
    """호가창 데이터 - 슬리피지 분석 및 OBI 계산용."""

    timestamp: datetime
    stock_code: str
    bid_prices: list[int] = Field(..., description="매수 호가 10단계")
    bid_volumes: list[int]
    ask_prices: list[int] = Field(..., description="매도 호가 10단계")
    ask_volumes: list[int]

    @property
    def obi(self) -> float:
        """Order Book Imbalance (-1 ~ +1, 양수면 매수세 우위)."""
        total_bid = sum(self.bid_volumes)
        total_ask = sum(self.ask_volumes)
        if total_bid + total_ask == 0:
            return 0.0
        return (total_bid - total_ask) / (total_bid + total_ask)


class ExecutionResult(BaseModel):
    """주문 체결 결과."""

    order_id: str
    stock_code: str
    side: OrderSide
    order_type: OrderType
    requested_price: int
    executed_price: int
    quantity: int
    executed_quantity: int
    fee: int
    tax: int
    slippage_bps: float = Field(0, description="슬리피지 (basis points)")
    timestamp: datetime
    status: str = Field("filled", description="filled | partial | rejected | cancelled")
