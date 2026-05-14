"""베이지안 신뢰도 계산.

사용자 텔레그램 메시지에 등장하는 "🤖 베이지안 38% (실측 46% · 26건 학습)" 형태의
신뢰도를 산출합니다. Beta 분포를 사전(prior)으로 사용하는 표준 베이지안 방식입니다.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass
class BayesianConfidence:
    """베이지안 신뢰도 결과."""

    bayesian_pct: float  # 베이지안 사후 평균 (0-100)
    empirical_pct: float  # 단순 실측 승률 (0-100)
    samples: int  # 학습 표본 수
    label: str  # 탐색 | 학습 중 | 확실 | 매우 확실
    std_pct: float  # 사후 분포의 표준편차

    def emoji(self) -> str:
        """텔레그램 표시용 이모지."""
        if self.bayesian_pct >= 70:
            return "🟢"
        elif self.bayesian_pct >= 50:
            return "🟡"
        else:
            return "🔴"


def compute_bayesian_confidence(
    wins: int,
    total: int,
    prior_alpha: float = 2.0,
    prior_beta: float = 2.0,
) -> BayesianConfidence:
    """Beta(prior_alpha, prior_beta) 사전 분포 기반 사후 평균 계산.

    표본이 적을 때는 사전에 가까운 보수적 값을, 표본이 많아질수록 실측에 가까운 값을 반환합니다.

    Args:
        wins: 승리 횟수
        total: 총 시도 횟수
        prior_alpha: Beta 사전 분포의 alpha (기본 2.0 = 약한 사전)
        prior_beta: Beta 사전 분포의 beta

    Returns:
        BayesianConfidence
    """
    if total < 0 or wins < 0 or wins > total:
        raise ValueError("invalid wins/total")

    # Posterior: Beta(alpha + wins, beta + losses)
    posterior_alpha = prior_alpha + wins
    posterior_beta = prior_beta + (total - wins)
    mean = posterior_alpha / (posterior_alpha + posterior_beta)
    var = (posterior_alpha * posterior_beta) / (
        (posterior_alpha + posterior_beta) ** 2
        * (posterior_alpha + posterior_beta + 1)
    )
    std = sqrt(var)

    empirical = (wins / total * 100) if total > 0 else 0.0

    # 표본 수에 따른 라벨링
    if total < 10:
        label = "탐색"
    elif total < 30:
        label = "학습 중"
    elif total < 100:
        label = "확실"
    else:
        label = "매우 확실"

    return BayesianConfidence(
        bayesian_pct=mean * 100,
        empirical_pct=empirical,
        samples=total,
        label=label,
        std_pct=std * 100,
    )
