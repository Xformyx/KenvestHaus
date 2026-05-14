"""포지션 사이징 (Position Sizing).

베이지안 신뢰도와 손익비를 활용한 동적 포지션 결정.
Kelly Criterion의 보수적 변형(Fractional Kelly)을 적용합니다.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PositionPlan:
    """포지션 계획."""

    quantity: int
    price: int
    notional: int  # 매수 금액 (원)
    fraction_of_capital: float  # 전체 자금 대비 비율
    rationale: str


def compute_position_size(
    available_capital: int,
    price: int,
    win_prob: float,  # 0~1
    take_profit_pct: float,  # 예: 4.0
    stop_loss_pct: float,  # 예: -2.0 (음수)
    max_position_pct: float = 10.0,
    kelly_fraction: float = 0.25,  # Quarter Kelly (보수적)
    is_short_term: bool = True,
    short_term_ratio: float = 0.3,
    mid_term_ratio: float = 0.7,
) -> PositionPlan:
    """Kelly Criterion 기반 포지션 사이징.

    Kelly f* = (b*p - q) / b
        p: 승률, q: 패율(1-p), b: 손익비 (TP/|SL|)

    실전에서는 Full Kelly가 과도하게 공격적이므로 Quarter Kelly(1/4) 정도를 권장합니다.

    Args:
        available_capital: 사용 가능 자금 (원)
        price: 현재가
        win_prob: 베이지안 승률 (0~1)
        take_profit_pct: 목표 익절 (%)
        stop_loss_pct: 손절 (%, 음수)
        max_position_pct: 종목당 최대 비중 (%)
        kelly_fraction: Kelly 분율 (0.25 = Quarter Kelly)
        is_short_term: True면 단기 풀, False면 중기 풀에서 자금 차감
        short_term_ratio: 사용자 설정 단기 비중
        mid_term_ratio: 사용자 설정 중기 비중

    Returns:
        PositionPlan
    """
    # 1) 단기/중기별 가용 자금 계산
    pool_ratio = short_term_ratio if is_short_term else mid_term_ratio
    pool_capital = available_capital * pool_ratio

    # 2) Kelly fraction 계산
    p = win_prob
    q = 1 - p
    b = take_profit_pct / abs(stop_loss_pct)
    if b <= 0:
        kelly_f = 0.0
    else:
        kelly_f = (b * p - q) / b
    kelly_f = max(0.0, min(kelly_f, 1.0))  # 0~1로 클리핑

    # 3) 보수적 Kelly 적용
    target_fraction = kelly_f * kelly_fraction

    # 4) 종목당 최대 비중 제한
    max_fraction = max_position_pct / 100
    target_fraction = min(target_fraction, max_fraction)

    # 5) 실제 매수 금액 및 수량
    notional = int(pool_capital * target_fraction)
    quantity = notional // price if price > 0 else 0
    actual_notional = quantity * price

    rationale = (
        f"Kelly f*={kelly_f:.3f}, applied={target_fraction:.3f} "
        f"(win_prob={p:.2f}, R/R={b:.2f})"
    )

    return PositionPlan(
        quantity=quantity,
        price=price,
        notional=actual_notional,
        fraction_of_capital=actual_notional / available_capital
        if available_capital > 0
        else 0.0,
        rationale=rationale,
    )
