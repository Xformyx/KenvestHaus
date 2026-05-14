"""매매 시그널 및 알림 타입 정의.

사용자 텔레그램 메시지 9가지 유형을 기반으로 설계되었습니다.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SignalType(str, Enum):
    """텔레그램 알림 메시지 유형."""

    DAILY_MAGAZINE = "daily_magazine"  # 1. 일일 매거진
    GOLDEN_ZONE = "golden_zone"  # 2. 단타 골든존
    PORTFOLIO_MGMT = "portfolio_mgmt"  # 3. 포트폴리오 관리
    LIMIT_UP_IMMINENT = "limit_up_imminent"  # 4. 상한가 임박
    LUNCH_CHECKIN = "lunch_checkin"  # 5. 점심시간 중간점검
    REALTIME_ABNORMAL = "realtime_abnormal"  # 6. 실시간 이상신호
    SMART_MONEY_SCAN = "smart_money_scan"  # 7. 수급 알림 스캔
    AFTER_HOURS_STRATEGY = "after_hours_strategy"  # 8. 마감후 내일 전략
    DAILY_CLOSING = "daily_closing"  # 9. 장마감 종합정리


class MarketRegime(str, Enum):
    """시장 체제 인식."""

    GOOD_MARKET = "good_market"  # 좋은 장
    VOLATILE = "volatile"  # 변동성 장
    BEARISH = "bearish"  # 약세 장
    SIDEWAYS = "sideways"  # 횡보 장


class TradingSignal(BaseModel):
    """모든 매매 시그널의 기본 클래스."""

    signal_type: SignalType
    timestamp: datetime = Field(default_factory=datetime.now)
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    market_regime: Optional[MarketRegime] = None


class GoldenZoneSignal(TradingSignal):
    """단타 골든존 진입 시그널 (메시지 유형 2)."""

    signal_type: SignalType = SignalType.GOLDEN_ZONE
    current_price: int
    change_pct: float = Field(..., description="당일 상승률 (예: 9.30)")
    strength: int = Field(..., description="체결강도 (예: 162)")
    trading_value_billion: float = Field(..., description="거래대금 억원 단위")
    bayesian_confidence: float = Field(..., description="베이지안 신뢰도 (0-100)")
    empirical_win_rate: Optional[float] = Field(None, description="실측 승률 (0-100)")
    learning_samples: int = Field(..., description="학습 표본 수")
    filter_score: int = Field(..., description="4중 필터 점수 (0-100)")
    filter_label: str = Field(..., description="STRONG_BUY, BUY, NEUTRAL, AVOID")
    buy_price_low: int
    buy_price_high: int
    take_profit_price: int
    stop_loss_price: int
    risk_reward_ratio: float


class PortfolioSignal(TradingSignal):
    """포트폴리오 관리 시그널 (메시지 유형 3)."""

    signal_type: SignalType = SignalType.PORTFOLIO_MGMT
    entry_price: int
    current_price: int
    pnl_pct: float
    hold_minutes: int
    obi: float = Field(..., description="Order Book Imbalance")
    strength: int
    high_pnl_pct: float = Field(..., description="고점 손익률")
    recommendation: str


class LimitUpImminentSignal(TradingSignal):
    """상한가 임박 시그널 (메시지 유형 4)."""

    signal_type: SignalType = SignalType.LIMIT_UP_IMMINENT
    current_price: int
    change_pct: float
    strength: int
    trading_value_billion: float
    bayesian_confidence: float


class AbnormalSignal(TradingSignal):
    """실시간 이상 신호 (메시지 유형 6)."""

    signal_type: SignalType = SignalType.REALTIME_ABNORMAL
    anomaly_type: str = Field(..., description="예: 거래량 이상 급증")
    multiplier: float = Field(..., description="평균 대비 배수")
    sigma: float = Field(..., description="표준편차 단위")


class SmartMoneyEntry(BaseModel):
    """수급 알림 스캔의 개별 종목 항목."""

    rank: int
    stock_code: str
    stock_name: str
    smart_money_flow_billion: float = Field(..., description="스마트머니 순매수 (억)")
    retail_flow_billion: float = Field(..., description="개인 순매수 (억)")
    foreigner_change: Optional[str] = None  # "sell -> buy", "buy -> sell"
    institution_change: Optional[str] = None


class SmartMoneySignal(TradingSignal):
    """수급 알림 스캔 결과 (메시지 유형 7)."""

    signal_type: SignalType = SignalType.SMART_MONEY_SCAN
    entries: list[SmartMoneyEntry]


class ThemeRanking(BaseModel):
    """강세 테마 정보."""

    theme_name: str
    avg_change_pct: float
    leader_stock: str


class DailyClosingReport(TradingSignal):
    """장마감 종합정리 (메시지 유형 9)."""

    signal_type: SignalType = SignalType.DAILY_CLOSING
    top_themes: list[ThemeRanking]
    limit_up_stocks: list[str]
    tomorrow_top_picks: list[dict]
    ai_learning_result: dict


class NextDayStrategy(TradingSignal):
    """마감 후 내일 전략 (메시지 유형 8)."""

    signal_type: SignalType = SignalType.AFTER_HOURS_STRATEGY
    risk_score: int = Field(..., description="종합 위험도 0-100")
    market_outlook: str
    us_to_kr_coupling: dict = Field(..., description="美 자금 흐름 -> 韓 수혜 테마")
    long_term_candidates: list[dict]
    action_plan: list[str]
