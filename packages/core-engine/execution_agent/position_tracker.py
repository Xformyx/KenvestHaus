"""포지션 추적기.

진입 가격, 익절/손절/시간 한계(Triple-Barrier)를 추적하고,
조건 도달 시 자동 청산 시그널을 발생시킵니다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class Position:
    """단일 포지션."""

    stock_code: str
    stock_name: str
    entry_price: int
    quantity: int
    entry_time: datetime
    take_profit_pct: float  # 익절 목표 (%)
    stop_loss_pct: float  # 손절 (%, 음수)
    time_limit_minutes: int  # 시간 한계 (분)
    signal_id: Optional[int] = None
    high_water_mark: Optional[int] = None  # 트레일링 스탑용 최고가
    trailing_stop_pct: Optional[float] = None  # 예: -3.0 (고점 대비 -3%)

    @property
    def take_profit_price(self) -> int:
        return int(self.entry_price * (1 + self.take_profit_pct / 100))

    @property
    def stop_loss_price(self) -> int:
        return int(self.entry_price * (1 + self.stop_loss_pct / 100))

    @property
    def time_limit_at(self) -> datetime:
        return self.entry_time + timedelta(minutes=self.time_limit_minutes)

    def pnl_pct(self, current_price: int) -> float:
        return (current_price - self.entry_price) / self.entry_price * 100

    def check_exit_condition(
        self, current_price: int, now: datetime, strength: Optional[float] = None
    ) -> Optional[str]:
        """청산 조건 도달 여부 확인.

        Returns:
            None | 'TP' (익절) | 'SL' (손절) | 'TIME' (시간 한계) |
            'TRAILING' (트레일링 스탑) | 'STRENGTH' (체결강도 약화)
        """
        # 1) 익절 도달
        if current_price >= self.take_profit_price:
            return "TP"

        # 2) 손절 도달
        if current_price <= self.stop_loss_price:
            return "SL"

        # 3) 시간 한계 도달
        if now >= self.time_limit_at:
            return "TIME"

        # 4) 트레일링 스탑
        if self.trailing_stop_pct is not None:
            self.high_water_mark = max(self.high_water_mark or current_price, current_price)
            drop_pct = (current_price - self.high_water_mark) / self.high_water_mark * 100
            if drop_pct <= self.trailing_stop_pct:
                return "TRAILING"

        # 5) 체결강도 약화 (사용자 텔레그램 메시지의 "체결강도 105 이하" 조건)
        if strength is not None and strength < 100:
            return "STRENGTH"

        return None


class PositionTracker:
    """전체 포지션 관리."""

    def __init__(self):
        self._positions: dict[str, Position] = {}

    def open(self, position: Position) -> None:
        if position.stock_code in self._positions:
            raise ValueError(f"이미 보유 중인 종목: {position.stock_code}")
        self._positions[position.stock_code] = position

    def close(self, stock_code: str) -> Position:
        return self._positions.pop(stock_code)

    def get(self, stock_code: str) -> Optional[Position]:
        return self._positions.get(stock_code)

    def all(self) -> list[Position]:
        return list(self._positions.values())

    def __len__(self) -> int:
        return len(self._positions)
