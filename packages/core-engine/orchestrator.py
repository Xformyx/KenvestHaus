"""Core Engine 오케스트레이터.

차트/수급 Agent의 시그널을 받아, Decision Agent에 전달하여 최종 매매 결정을 내리고,
Execution Agent에게 주문 명령을 전달하는 메인 파이프라인입니다.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

import pandas as pd

from packages.shared.types import (
    GoldenZoneSignal,
    SignalType,
    StrategyConfig,
    StrategyType,
    UserSettings,
)

from .chart_agent import (
    StrategyResult,
    detect_bollinger_breakout,
    detect_bollinger_reversal,
    detect_five_min_gc,
    detect_golden_zone,
    detect_high_breakout,
    detect_ma_golden_cross,
    detect_rsi_oversold,
    detect_strength_and_volume,
    detect_turtle_breakout,
    detect_volume_surge_pullback,
)
from .decision_agent import (
    FourPointFilter,
    MarketRegimeDetector,
    compute_bayesian_confidence,
    compute_position_size,
)

logger = logging.getLogger(__name__)


# StrategyType → 감지 함수 매핑
_DETECTOR_MAP = {
    StrategyType.MA_GOLDEN_CROSS: lambda df, ctx: detect_ma_golden_cross(df),
    StrategyType.BOLLINGER_BREAKOUT: lambda df, ctx: detect_bollinger_breakout(df),
    StrategyType.HIGH_BREAKOUT: lambda df, ctx: detect_high_breakout(df),
    StrategyType.BOLLINGER_REVERSAL: lambda df, ctx: detect_bollinger_reversal(df),
    StrategyType.RSI_OVERSOLD: lambda df, ctx: detect_rsi_oversold(df),
    StrategyType.VOLUME_SURGE_PULLBACK: lambda df, ctx: detect_volume_surge_pullback(df),
    StrategyType.TURTLE_TRADING: lambda df, ctx: detect_turtle_breakout(df),
    StrategyType.GOLDEN_ZONE: lambda df, ctx: detect_golden_zone(
        ctx.get("change_pct", 0.0)
    ),
    StrategyType.FIVE_MIN_GC: lambda df, ctx: detect_five_min_gc(ctx.get("df_5min", df)),
    StrategyType.STRENGTH_AND_VOLUME: lambda df, ctx: detect_strength_and_volume(
        ctx.get("strength", 0),
        ctx.get("current_volume", 0),
        ctx.get("avg_volume", 1),
    ),
}


class CoreOrchestrator:
    """단일 종목에 대한 분석 → 결정 → (옵션) 실행 파이프라인."""

    def __init__(self, user_settings: UserSettings):
        self.user_settings = user_settings
        self.market_regime_detector = MarketRegimeDetector()
        self.four_point_filter = FourPointFilter()

    def analyze(
        self,
        stock_code: str,
        stock_name: str,
        daily_df: pd.DataFrame,
        context: Optional[dict] = None,
    ) -> dict:
        """단일 종목 분석.

        Returns:
            dict: {
                'stock_code', 'stock_name',
                'signals': list[StrategyResult],
                'bayesian': BayesianConfidence | None,
                'filter_score': FilterScore | None,
                'recommendation': 'BUY' | 'HOLD' | 'SKIP'
            }
        """
        ctx = context or {}

        # 1) 활성화된 전략만 감지 실행
        enabled = {
            cfg.strategy_type: cfg
            for cfg in self.user_settings.enabled_strategies
            if cfg.enabled
        }
        signals: list[StrategyResult] = []
        for st, cfg in enabled.items():
            detector = _DETECTOR_MAP.get(st)
            if not detector:
                continue
            try:
                result = detector(daily_df, ctx)
                if result.triggered:
                    signals.append(result)
            except Exception as e:
                logger.warning("Strategy %s failed for %s: %s", st, stock_code, e)

        if not signals:
            return {
                "stock_code": stock_code,
                "stock_name": stock_name,
                "signals": [],
                "bayesian": None,
                "filter_score": None,
                "recommendation": "SKIP",
                "reason": "활성화된 전략 중 발화된 시그널 없음",
            }

        # 2) 베이지안 신뢰도 (학습 데이터 기반, 여기서는 기본값 예시)
        wins = ctx.get("historical_wins", 0)
        total = ctx.get("historical_total", 0)
        bayesian = compute_bayesian_confidence(wins, total) if total > 0 else None

        # 3) 4중 필터 점수
        trend_score = float(sum(s.score for s in signals if s.strategy_type in {
            StrategyType.MA_GOLDEN_CROSS,
            StrategyType.HIGH_BREAKOUT,
            StrategyType.TURTLE_TRADING,
            StrategyType.BOLLINGER_BREAKOUT,
        }) / max(1, len(signals)))
        momentum_score = float(sum(s.score for s in signals if s.strategy_type in {
            StrategyType.GOLDEN_ZONE,
            StrategyType.FIVE_MIN_GC,
            StrategyType.RSI_OVERSOLD,
        }) / max(1, len(signals)))
        flow_score = float(ctx.get("flow_score", 50.0))
        volatility_score = float(ctx.get("volatility_score", 50.0))

        filter_score = self.four_point_filter.evaluate(
            min(trend_score, 100),
            min(momentum_score, 100),
            min(flow_score, 100),
            min(volatility_score, 100),
        )

        # 4) 최종 추천
        if filter_score.label in ("STRONG_BUY", "BUY"):
            recommendation = "BUY"
        elif filter_score.label == "NEUTRAL":
            recommendation = "HOLD"
        else:
            recommendation = "SKIP"

        return {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "signals": signals,
            "bayesian": bayesian,
            "filter_score": filter_score,
            "recommendation": recommendation,
        }
