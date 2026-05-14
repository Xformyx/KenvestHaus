"""Execution Agent - 자동매매 실행 Agent.

의사결정 Agent로부터 명령을 받아 한국투자증권 API로 실제 주문을 실행합니다.
Triple-Barrier 방식으로 포지션을 관리하며, 분할 매수/매도 및 슬리피지 최소화를 담당합니다.
"""

from .order_manager import OrderManager
from .position_tracker import Position, PositionTracker

__all__ = ["OrderManager", "Position", "PositionTracker"]
