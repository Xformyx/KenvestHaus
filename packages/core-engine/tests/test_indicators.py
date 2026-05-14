"""기술적 지표 단위 테스트.

실행: pytest packages/core-engine/tests/
"""

from __future__ import annotations

import sys
from pathlib import Path

# core-engine 디렉토리를 sys.path에 추가 (하이픈 때문에 직접 import 불가)
_CORE_DIR = Path(__file__).resolve().parents[1]
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402

from chart_agent.indicators import (  # noqa: E402
    bollinger_bands,
    rsi,
    sma,
    triple_barrier_labels,
)


@pytest.fixture
def sample_series() -> pd.Series:
    np.random.seed(42)
    return pd.Series(np.cumsum(np.random.randn(100)) + 100)


def test_sma(sample_series: pd.Series) -> None:
    result = sma(sample_series, 5)
    assert len(result) == len(sample_series)
    assert result.iloc[:4].isna().all()
    assert not result.iloc[5:].isna().any()


def test_rsi(sample_series: pd.Series) -> None:
    result = rsi(sample_series, 14)
    valid = result.dropna()
    assert (valid >= 0).all()
    assert (valid <= 100).all()


def test_bollinger_bands(sample_series: pd.Series) -> None:
    bb = bollinger_bands(sample_series, 20, 2.0)
    valid = bb.dropna()
    assert (valid["upper"] >= valid["middle"]).all()
    assert (valid["middle"] >= valid["lower"]).all()


def test_triple_barrier_tp() -> None:
    prices = pd.Series([100, 101, 102, 105, 103, 99])
    result = triple_barrier_labels(prices, 0, 4.0, -3.0, 10)
    assert result["label"] == 1  # TP 도달
    assert result["reason"] == "tp"
    assert result["exit_index"] == 3


def test_triple_barrier_sl() -> None:
    prices = pd.Series([100, 99, 98, 97, 95, 99])
    result = triple_barrier_labels(prices, 0, 4.0, -3.0, 10)
    assert result["label"] == -1
    assert result["reason"] == "sl"


def test_triple_barrier_time() -> None:
    prices = pd.Series([100, 100, 101, 100, 99, 100])
    result = triple_barrier_labels(prices, 0, 10.0, -10.0, 3)
    assert result["label"] == 0
    assert result["reason"] == "time"
