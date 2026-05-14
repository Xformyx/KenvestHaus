"""시장 체제 인식 (Market Regime Detection).

KOSPI 지수의 변동성, 추세, 외국인 수급 등을 종합하여
현재 시장이 어떤 국면인지를 판단합니다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from packages.shared.types import MarketRegime


@dataclass
class RegimeAnalysis:
    """시장 체제 분석 결과."""

    regime: MarketRegime
    confidence: float  # 0~100
    vix_estimate: float
    trend_score: float
    notes: str


class MarketRegimeDetector:
    """시장 체제 분류기.

    간단한 규칙 기반 분류이며, 추후 HMM(Hidden Markov Model) 또는
    딥러닝 분류기로 교체할 수 있도록 인터페이스를 유지합니다.
    """

    def __init__(
        self,
        volatility_window: int = 20,
        trend_window: int = 60,
        high_vol_threshold: float = 0.020,  # 일간 변동성 2%+ → 변동성 장
        low_vol_threshold: float = 0.010,
    ):
        self.volatility_window = volatility_window
        self.trend_window = trend_window
        self.high_vol_threshold = high_vol_threshold
        self.low_vol_threshold = low_vol_threshold

    def detect(
        self, index_ohlcv: pd.DataFrame, foreign_flow: Optional[pd.Series] = None
    ) -> RegimeAnalysis:
        """시장 체제를 분류합니다.

        Args:
            index_ohlcv: KOSPI/KOSDAQ 지수의 OHLCV DataFrame
            foreign_flow: (선택) 외국인 순매수 시계열

        Returns:
            RegimeAnalysis
        """
        if len(index_ohlcv) < self.trend_window:
            return RegimeAnalysis(
                regime=MarketRegime.SIDEWAYS,
                confidence=0.0,
                vix_estimate=0.0,
                trend_score=0.0,
                notes="데이터 부족",
            )

        returns = index_ohlcv["close"].pct_change().dropna()
        recent_vol = float(returns.iloc[-self.volatility_window :].std())
        vix_estimate = recent_vol * np.sqrt(252) * 100  # 연환산 변동성

        # 추세 점수: 60일 종가 대비 현재 종가 변화율
        trend_score = float(
            (index_ohlcv["close"].iloc[-1] - index_ohlcv["close"].iloc[-self.trend_window])
            / index_ohlcv["close"].iloc[-self.trend_window]
            * 100
        )

        if recent_vol > self.high_vol_threshold:
            regime = MarketRegime.VOLATILE
            notes = "변동성 확대 - 손절 라인 엄격히 적용"
        elif trend_score < -5.0:
            regime = MarketRegime.BEARISH
            notes = "약세 추세 - 신규 진입 자제, 현금 비중 확대"
        elif trend_score > 3.0 and recent_vol < self.low_vol_threshold:
            regime = MarketRegime.GOOD_MARKET
            notes = "안정적 상승장 - 적극 매수"
        else:
            regime = MarketRegime.SIDEWAYS
            notes = "횡보장 - 단타 위주, 종가 베팅 자제"

        # 외국인 수급으로 보정
        if foreign_flow is not None and len(foreign_flow) >= 5:
            recent_foreign = float(foreign_flow.iloc[-5:].sum())
            if recent_foreign < -2_000_000_000_000:  # -2조 이상 이탈
                regime = MarketRegime.BEARISH
                notes += " | 외국인 대량 이탈"

        return RegimeAnalysis(
            regime=regime,
            confidence=70.0,
            vix_estimate=vix_estimate,
            trend_score=trend_score,
            notes=notes,
        )
