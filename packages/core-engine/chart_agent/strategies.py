"""매매 전략 감지 함수 모음.

각 전략은 OHLCV DataFrame과 (선택적으로) 추가 컨텍스트를 받아
StrategyResult 를 반환하는 순수 함수입니다.

설계 문서 docs/4_final_system_design.md 의 매매 전략 목록을 그대로 구현했습니다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

from packages.shared.types import StrategyType

from .indicators import bollinger_bands, ema, rsi, sma


@dataclass
class StrategyResult:
    """전략 감지 결과."""

    strategy_type: StrategyType
    triggered: bool
    score: float = 0.0  # 0~100 점수, 높을수록 신호 강함
    reason: str = ""
    metadata: dict = field(default_factory=dict)


# === 추세 추종 / 돌파 전략 ===


def detect_ma_golden_cross(
    df: pd.DataFrame, short: int = 5, long: int = 20
) -> StrategyResult:
    """이동평균선 골든크로스 (단기 이평선이 장기 이평선 상향 돌파)."""
    if len(df) < long + 2:
        return StrategyResult(StrategyType.MA_GOLDEN_CROSS, False, reason="데이터 부족")

    short_ma = sma(df["close"], short)
    long_ma = sma(df["close"], long)

    prev_diff = short_ma.iloc[-2] - long_ma.iloc[-2]
    curr_diff = short_ma.iloc[-1] - long_ma.iloc[-1]
    crossed = prev_diff <= 0 < curr_diff

    return StrategyResult(
        strategy_type=StrategyType.MA_GOLDEN_CROSS,
        triggered=bool(crossed),
        score=70.0 if crossed else 0.0,
        reason=f"{short}일선이 {long}일선 상향 돌파" if crossed else "교차 없음",
        metadata={
            "short_ma": float(short_ma.iloc[-1]),
            "long_ma": float(long_ma.iloc[-1]),
        },
    )


def detect_bollinger_breakout(
    df: pd.DataFrame, period: int = 20, num_std: float = 2.0
) -> StrategyResult:
    """볼린저 밴드 상단 돌파 (밴드 폭 수축 후 거래량 동반 상단 돌파)."""
    if len(df) < period + 2:
        return StrategyResult(StrategyType.BOLLINGER_BREAKOUT, False)

    bb = bollinger_bands(df["close"], period, num_std)
    prev_width = bb["width"].iloc[-2]
    avg_width = bb["width"].iloc[-period:].mean()
    is_squeeze = prev_width < avg_width * 0.7

    breakout = df["close"].iloc[-1] > bb["upper"].iloc[-1]
    prev_below = df["close"].iloc[-2] <= bb["upper"].iloc[-2]
    volume_surge = df["volume"].iloc[-1] > df["volume"].iloc[-21:-1].mean() * 1.5

    triggered = bool(is_squeeze and breakout and prev_below and volume_surge)
    return StrategyResult(
        strategy_type=StrategyType.BOLLINGER_BREAKOUT,
        triggered=triggered,
        score=80.0 if triggered else 0.0,
        reason="밴드 수축 후 거래량 동반 상단 돌파" if triggered else "조건 미충족",
        metadata={
            "upper": float(bb["upper"].iloc[-1]),
            "width": float(prev_width),
        },
    )


def detect_high_breakout(df: pd.DataFrame, lookback: int = 52 * 5) -> StrategyResult:
    """52주 신고가 또는 매물대 돌파."""
    if len(df) < lookback + 2:
        return StrategyResult(StrategyType.HIGH_BREAKOUT, False)

    prior_high = df["high"].iloc[-(lookback + 1) : -1].max()
    current = df["close"].iloc[-1]
    volume_surge = df["volume"].iloc[-1] > df["volume"].iloc[-21:-1].mean() * 1.5

    triggered = bool(current > prior_high and volume_surge)
    return StrategyResult(
        strategy_type=StrategyType.HIGH_BREAKOUT,
        triggered=triggered,
        score=85.0 if triggered else 0.0,
        reason="52주 신고가 거래량 동반 돌파" if triggered else "고점 미돌파",
        metadata={"prior_high": float(prior_high), "current": float(current)},
    )


# === 역추세 / 눌림목 전략 ===


def detect_bollinger_reversal(
    df: pd.DataFrame, period: int = 20, num_std: float = 2.0
) -> StrategyResult:
    """볼린저 밴드 하단 이탈 후 재진입."""
    if len(df) < period + 2:
        return StrategyResult(StrategyType.BOLLINGER_REVERSAL, False)

    bb = bollinger_bands(df["close"], period, num_std)
    prev_below_lower = df["close"].iloc[-2] < bb["lower"].iloc[-2]
    curr_above_lower = df["close"].iloc[-1] > bb["lower"].iloc[-1]
    triggered = bool(prev_below_lower and curr_above_lower)

    return StrategyResult(
        strategy_type=StrategyType.BOLLINGER_REVERSAL,
        triggered=triggered,
        score=65.0 if triggered else 0.0,
        reason="하단 이탈 후 재진입 (단기 반등 기대)" if triggered else "조건 미충족",
    )


def detect_rsi_oversold(df: pd.DataFrame, period: int = 14) -> StrategyResult:
    """RSI 과매도 반등."""
    if len(df) < period + 2:
        return StrategyResult(StrategyType.RSI_OVERSOLD, False)

    r = rsi(df["close"], period)
    prev = r.iloc[-2]
    curr = r.iloc[-1]
    triggered = bool(prev < 30 and curr > prev)

    return StrategyResult(
        strategy_type=StrategyType.RSI_OVERSOLD,
        triggered=triggered,
        score=60.0 if triggered else 0.0,
        reason=f"RSI 과매도 반등 ({prev:.1f} → {curr:.1f})" if triggered else "조건 미충족",
        metadata={"rsi": float(curr)},
    )


def detect_volume_surge_pullback(df: pd.DataFrame) -> StrategyResult:
    """거래량 급증 후 눌림목 (장대양봉 후 10일선 지지)."""
    if len(df) < 22:
        return StrategyResult(StrategyType.VOLUME_SURGE_PULLBACK, False)

    # 최근 5일 내 거래량 급증(평균 5배+) 장대양봉 존재 확인
    recent = df.iloc[-6:-1]
    avg_volume = df["volume"].iloc[-25:-6].mean()
    surge_mask = (recent["volume"] > avg_volume * 5) & (
        (recent["close"] - recent["open"]) / recent["open"] > 0.05
    )
    if not surge_mask.any():
        return StrategyResult(
            StrategyType.VOLUME_SURGE_PULLBACK, False, reason="장대양봉 없음"
        )

    # 현재가가 10일선 부근에서 지지받는지 확인
    ma10 = sma(df["close"], 10).iloc[-1]
    current = df["close"].iloc[-1]
    near_ma10 = abs(current - ma10) / ma10 < 0.03

    triggered = bool(near_ma10)
    return StrategyResult(
        strategy_type=StrategyType.VOLUME_SURGE_PULLBACK,
        triggered=triggered,
        score=75.0 if triggered else 0.0,
        reason="장대양봉 후 10일선 지지" if triggered else "지지선 미도달",
    )


# === 단타 전용 (텔레그램 데이터 기반) ===


def detect_golden_zone(change_pct: float) -> StrategyResult:
    """단타 골든존 - 당일 등락률 +5% ~ +13% 구간."""
    triggered = 5.0 <= change_pct <= 13.0
    return StrategyResult(
        strategy_type=StrategyType.GOLDEN_ZONE,
        triggered=triggered,
        score=70.0 if triggered else 0.0,
        reason=f"등락률 {change_pct:.2f}% (골든존 5~13%)",
    )


def detect_five_min_gc(df_5min: pd.DataFrame, short: int = 5, long: int = 20) -> StrategyResult:
    """5분봉 골든크로스."""
    return StrategyResult(
        strategy_type=StrategyType.FIVE_MIN_GC,
        **_cross_check(df_5min, short, long, StrategyType.FIVE_MIN_GC),
    )


def _cross_check(
    df: pd.DataFrame, short: int, long: int, st: StrategyType
) -> dict:
    if len(df) < long + 2:
        return {"triggered": False, "score": 0.0, "reason": "데이터 부족"}
    sma_s = sma(df["close"], short)
    sma_l = sma(df["close"], long)
    prev = sma_s.iloc[-2] - sma_l.iloc[-2]
    curr = sma_s.iloc[-1] - sma_l.iloc[-1]
    triggered = bool(prev <= 0 < curr)
    return {
        "triggered": triggered,
        "score": 60.0 if triggered else 0.0,
        "reason": "5분봉 GC 발생" if triggered else "교차 없음",
    }


def detect_strength_and_volume(
    strength: float,
    current_volume: float,
    avg_volume: float,
    strength_threshold: float = 100,
    volume_multiplier: float = 3.0,
) -> StrategyResult:
    """체결강도 100 이상 + 거래량 평균의 3배 이상."""
    strong = strength >= strength_threshold
    high_vol = current_volume >= avg_volume * volume_multiplier
    triggered = bool(strong and high_vol)
    return StrategyResult(
        strategy_type=StrategyType.STRENGTH_AND_VOLUME,
        triggered=triggered,
        score=75.0 if triggered else 0.0,
        reason=(
            f"체결강도 {strength:.0f} + 거래량 {current_volume / avg_volume:.1f}배"
            if triggered
            else "조건 미충족"
        ),
        metadata={"strength": strength, "volume_ratio": current_volume / max(avg_volume, 1)},
    )


# === 중장기 (거북이 매매) ===


def detect_turtle_breakout(df: pd.DataFrame, breakout_period: int = 20) -> StrategyResult:
    """거북이 매매 - N일 신고가 돌파."""
    if len(df) < breakout_period + 2:
        return StrategyResult(StrategyType.TURTLE_TRADING, False)

    prior_high = df["high"].iloc[-(breakout_period + 1) : -1].max()
    current = df["close"].iloc[-1]
    triggered = bool(current > prior_high)
    return StrategyResult(
        strategy_type=StrategyType.TURTLE_TRADING,
        triggered=triggered,
        score=80.0 if triggered else 0.0,
        reason=f"{breakout_period}일 신고가 돌파" if triggered else "고점 미돌파",
        metadata={"prior_high": float(prior_high), "current": float(current)},
    )
