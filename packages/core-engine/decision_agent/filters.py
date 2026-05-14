"""4중 필터 (Four-Point Filter).

텔레그램 메시지에 등장하는 "🔬 4중 필터: ⚖️ 43점 (NEUTRAL)" 형태의
종합 점수를 산출합니다. 4가지 축을 평가하여 가중 평균합니다.

축 구성:
1. 추세 (Trend): 이동평균선 정배열 여부
2. 모멘텀 (Momentum): RSI, MACD, 등락률
3. 수급 (Flow): 체결강도, 외국인/기관 순매수
4. 변동성 (Volatility): 볼린저 밴드 폭, 일중 변동성
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FilterLabel = Literal["STRONG_BUY", "BUY", "NEUTRAL", "AVOID"]


@dataclass
class FilterScore:
    """필터 점수 결과."""

    total: float  # 0~100 종합 점수
    trend: float
    momentum: float
    flow: float
    volatility: float
    label: FilterLabel

    def emoji(self) -> str:
        if self.label == "STRONG_BUY":
            return "🚀"
        elif self.label == "BUY":
            return "📈"
        elif self.label == "NEUTRAL":
            return "⚖️"
        else:
            return "⚠️"


class FourPointFilter:
    """4중 필터 평가기.

    각 축의 점수는 0-100 범위이며, 가중치를 적용해 합산합니다.
    """

    def __init__(
        self,
        weights: tuple[float, float, float, float] = (0.25, 0.25, 0.30, 0.20),
    ):
        if abs(sum(weights) - 1.0) > 1e-6:
            raise ValueError("가중치 합은 1.0 이어야 합니다.")
        self.w_trend, self.w_momentum, self.w_flow, self.w_volatility = weights

    def evaluate(
        self,
        trend_score: float,
        momentum_score: float,
        flow_score: float,
        volatility_score: float,
    ) -> FilterScore:
        """4개 축의 점수를 종합합니다.

        각 입력은 0-100 범위여야 합니다.
        """
        total = (
            self.w_trend * trend_score
            + self.w_momentum * momentum_score
            + self.w_flow * flow_score
            + self.w_volatility * volatility_score
        )

        if total >= 75:
            label: FilterLabel = "STRONG_BUY"
        elif total >= 55:
            label = "BUY"
        elif total >= 40:
            label = "NEUTRAL"
        else:
            label = "AVOID"

        return FilterScore(
            total=total,
            trend=trend_score,
            momentum=momentum_score,
            flow=flow_score,
            volatility=volatility_score,
            label=label,
        )
