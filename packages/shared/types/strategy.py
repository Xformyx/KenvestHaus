"""사용자 매매 전략 설정 타입 정의.

Web UI에서 사용자가 Check/Uncheck로 활성화할 수 있는 매매 전략 목록입니다.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class StrategyType(str, Enum):
    """시스템에 탑재된 매매 전략 목록.

    설계 문서 (docs/2_agent_design.md, docs/4_final_system_design.md) 참조.
    각 전략은 Web UI 설정에서 사용자가 활성화/비활성화 할 수 있습니다.
    """

    # === 기업/펀더멘털 전략 ===
    VALUE_INVESTING = "value_investing"
    """저평가 가치주 발굴 - PER, PBR, ROE 기반 저평가 종목 발굴"""

    GROWTH_INVESTING = "growth_investing"
    """성장주 발굴 - 매출/영업이익 증가율, PEG 기반"""

    SAFETY_FILTER = "safety_filter"
    """재무 건전성 필터링 - 부채비율, 유보율, 적자 여부 (필수 권장)"""

    NLP_SENTIMENT = "nlp_sentiment"
    """공시/뉴스 센티멘털 분석 - NLP 기반 감성 점수"""

    # === 차트 분석: 추세 추종 / 돌파 전략 ===
    MA_GOLDEN_CROSS = "ma_golden_cross"
    """이동평균선 골든크로스 - 단기 이평선이 장기 이평선 상향 돌파"""

    BOLLINGER_BREAKOUT = "bollinger_breakout"
    """볼린저 밴드 상단 돌파 - 밴드 폭 수축 후 거래량 동반 상단 돌파"""

    HIGH_BREAKOUT = "high_breakout"
    """신고가/전고점 돌파 - 52주 신고가 또는 매물대 돌파"""

    # === 차트 분석: 역추세 / 눌림목 전략 ===
    BOLLINGER_REVERSAL = "bollinger_reversal"
    """볼린저 밴드 하단 반등 - 하단 이탈 후 재진입"""

    RSI_OVERSOLD = "rsi_oversold"
    """RSI 과매도 및 다이버전스 - RSI 30 이하 반등 또는 상승 다이버전스"""

    VOLUME_SURGE_PULLBACK = "volume_surge_pullback"
    """거래량 급증 후 눌림목 - 장대양봉 후 거래량 감소 + 지지선 안착"""

    # === 차트 분석: 수급 전략 ===
    INSTITUTIONAL_FOLLOW = "institutional_follow"
    """외국인/기관 양매수 추종 - 스마트머니 매집 추종"""

    # === 단타 전용 전략 (텔레그램 데이터 기반) ===
    GOLDEN_ZONE = "golden_zone"
    """단타 골든존 - 당일 상승률 +5%~+13% 구간 진입"""

    FIVE_MIN_GC = "five_min_gc"
    """5분봉 골든크로스 - 5분봉 기준 이평선 교차"""

    STRENGTH_AND_VOLUME = "strength_and_volume"
    """체결강도 & 거래량 - 체결강도 100 이상 + 거래량 3배 이상"""

    LIMIT_UP_GAP_BET = "limit_up_gap_bet"
    """상한가 갭상 베팅 - 상한가 근접 종목 종가 매수, 익일 시초 매도"""

    # === 중장기 전략 ===
    TURTLE_TRADING = "turtle_trading"
    """거북이 매매 - 20일선 돌파 추세 추종 (1~3개월 보유)"""

    # === 매크로/테마 전략 ===
    GLOBAL_COUPLING = "global_coupling"
    """글로벌 동조화 - 美 강세 테마 → 韓 수혜 종목 시초가 베팅"""


class StrategyConfig(BaseModel):
    """개별 매매 전략의 활성화 및 파라미터 설정."""

    strategy_type: StrategyType
    enabled: bool = True
    weight: float = Field(1.0, description="전략 가중치 (0.0 ~ 2.0)")
    params: dict = Field(default_factory=dict, description="전략별 커스텀 파라미터")


class UserSettings(BaseModel):
    """사용자 설정 (Web UI에서 조정).

    단기/중기 비중은 자동매매 시 자금 배분에만 영향을 미치며,
    종목 발굴 및 시그널 알림은 비중과 무관하게 모두 제공됩니다.
    """

    user_id: str
    short_term_ratio: float = Field(
        0.3, ge=0.0, le=1.0, description="단기 투자 비중 (0.0~1.0)"
    )
    mid_term_ratio: float = Field(
        0.7, ge=0.0, le=1.0, description="중기 투자 비중 (0.0~1.0)"
    )
    total_capital: int = Field(10_000_000, description="총 운용 자금 (원)")
    max_position_per_stock_pct: float = Field(
        10.0, description="종목별 최대 비중 (%)"
    )
    hard_stop_loss_pct: float = Field(-3.0, description="강제 손절 비율 (%)")
    trailing_stop_pct: float = Field(-3.0, description="트레일링 스탑 (%)")

    # 매매 전략 활성화 설정 (체크박스)
    enabled_strategies: list[StrategyConfig] = Field(default_factory=list)

    # 알림 설정
    telegram_chat_id: Optional[str] = None
    enable_auto_trading: bool = False  # 자동매매 활성화 여부 (기본 OFF)

    # 증권사 연동
    kis_account_no: Optional[str] = None  # 한국투자증권 계좌
    toss_username: Optional[str] = None  # 토스증권 (조회용)
