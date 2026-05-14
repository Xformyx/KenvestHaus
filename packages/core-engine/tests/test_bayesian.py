"""베이지안 신뢰도 단위 테스트."""

from __future__ import annotations

import sys
from pathlib import Path

_CORE_DIR = Path(__file__).resolve().parents[1]
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from decision_agent.bayesian import compute_bayesian_confidence  # noqa: E402


def test_zero_samples() -> None:
    """표본 0건 시에는 호출이 거부되어야 함."""
    # total=0인 경우는 사전 분포만 사용 → 50%
    result = compute_bayesian_confidence(0, 0)
    assert 40 < result.bayesian_pct < 60
    assert result.empirical_pct == 0.0
    assert result.label == "탐색"


def test_few_samples_conservative() -> None:
    """표본이 적을 때는 사전에 끌려서 보수적 값."""
    # 5승 5패 → 실측 50%, 베이지안도 50% 근처
    result = compute_bayesian_confidence(5, 10)
    assert 40 < result.bayesian_pct < 60


def test_many_samples_converge() -> None:
    """표본이 많아지면 실측에 수렴."""
    # 70승 30패 → 실측 70%, 베이지안도 70% 근처
    result = compute_bayesian_confidence(70, 100)
    assert 65 < result.bayesian_pct < 72
    assert result.empirical_pct == 70.0
    assert result.label == "매우 확실"


def test_label_progression() -> None:
    assert compute_bayesian_confidence(2, 5).label == "탐색"
    assert compute_bayesian_confidence(10, 20).label == "학습 중"
    assert compute_bayesian_confidence(30, 50).label == "확실"
    assert compute_bayesian_confidence(70, 100).label == "매우 확실"
