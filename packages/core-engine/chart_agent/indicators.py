"""기술적 지표 계산 라이브러리.

모든 지표는 numpy/pandas 기반으로 결정론적으로 계산됩니다.
순수 함수 형태이므로 단위 테스트 및 백테스팅에 적합합니다.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, period: int) -> pd.Series:
    """단순 이동평균선 (Simple Moving Average)."""
    return series.rolling(window=period, min_periods=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    """지수 이동평균선 (Exponential Moving Average)."""
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """상대강도지수 (Relative Strength Index).

    Wilder의 평활법(EMA 변형)을 사용합니다.
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """MACD (Moving Average Convergence Divergence)."""
    fast_ema = ema(series, fast)
    slow_ema = ema(series, slow)
    macd_line = fast_ema - slow_ema
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return pd.DataFrame(
        {"macd": macd_line, "signal": signal_line, "histogram": histogram}
    )


def bollinger_bands(
    series: pd.Series, period: int = 20, num_std: float = 2.0
) -> pd.DataFrame:
    """볼린저 밴드."""
    middle = sma(series, period)
    std = series.rolling(window=period, min_periods=period).std()
    upper = middle + num_std * std
    lower = middle - num_std * std
    width = (upper - lower) / middle
    return pd.DataFrame(
        {"middle": middle, "upper": upper, "lower": lower, "width": width}
    )


def triple_barrier_labels(
    prices: pd.Series,
    entry_index: int,
    take_profit_pct: float,
    stop_loss_pct: float,
    time_limit: int,
) -> dict:
    """Triple-Barrier Method (Lopez de Prado, 2018).

    포지션 진입 후 익절(TP)/손절(SL)/시간 한계 중 가장 먼저 도달하는 지점을 찾습니다.

    Args:
        prices: 진입 이후의 가격 시계열
        entry_index: 진입 시점 인덱스
        take_profit_pct: 익절 목표 비율 (예: +4.0)
        stop_loss_pct: 손절 비율 (예: -2.0)
        time_limit: 시간 한계 (캔들 개수)

    Returns:
        dict: {label, exit_index, exit_price, pnl_pct, reason}
            label: 1(TP), -1(SL), 0(TIME)
            reason: 'tp' | 'sl' | 'time'
    """
    if entry_index >= len(prices):
        raise IndexError("entry_index out of range")

    entry_price = float(prices.iloc[entry_index])
    tp_price = entry_price * (1 + take_profit_pct / 100)
    sl_price = entry_price * (1 + stop_loss_pct / 100)

    end_index = min(entry_index + time_limit, len(prices) - 1)
    window = prices.iloc[entry_index + 1 : end_index + 1]

    for offset, price in enumerate(window, start=1):
        idx = entry_index + offset
        if price >= tp_price:
            return {
                "label": 1,
                "exit_index": idx,
                "exit_price": float(price),
                "pnl_pct": (price - entry_price) / entry_price * 100,
                "reason": "tp",
            }
        if price <= sl_price:
            return {
                "label": -1,
                "exit_index": idx,
                "exit_price": float(price),
                "pnl_pct": (price - entry_price) / entry_price * 100,
                "reason": "sl",
            }

    final_price = float(prices.iloc[end_index])
    return {
        "label": 0,
        "exit_index": end_index,
        "exit_price": final_price,
        "pnl_pct": (final_price - entry_price) / entry_price * 100,
        "reason": "time",
    }
