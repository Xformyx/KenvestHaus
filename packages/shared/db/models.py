"""SQLAlchemy ORM 모델 정의 (PostgreSQL).

시계열 데이터(OHLCV, 호가)는 InfluxDB에 저장하고,
메타데이터/시그널/체결/백테스트 결과 등은 PostgreSQL에 저장합니다.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """ORM Base 클래스."""


class StockMaster(Base):
    """종목 마스터 테이블."""

    __tablename__ = "stock_master"

    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    market: Mapped[str] = mapped_column(String(10), nullable=False)  # KOSPI/KOSDAQ
    sector: Mapped[Optional[str]] = mapped_column(String(50))
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    listed_shares: Mapped[Optional[int]] = mapped_column(BigInteger)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SignalLog(Base):
    """매매 시그널 발생 로그.

    텔레그램으로 발송된 모든 시그널이 기록되며,
    이후 백테스팅 및 딥러닝 학습 데이터로 활용됩니다.
    """

    __tablename__ = "signal_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    signal_type: Mapped[str] = mapped_column(String(50), index=True)
    stock_code: Mapped[Optional[str]] = mapped_column(String(10), index=True)
    strategy_type: Mapped[Optional[str]] = mapped_column(String(50))
    bayesian_confidence: Mapped[Optional[float]] = mapped_column(Float)
    filter_score: Mapped[Optional[int]] = mapped_column(Integer)
    market_regime: Mapped[Optional[str]] = mapped_column(String(20))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    # 사후 평가 필드 (학습 데이터용)
    realized_pnl_pct: Mapped[Optional[float]] = mapped_column(Float)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    close_reason: Mapped[Optional[str]] = mapped_column(String(30))  # TP, SL, TIME, MANUAL


class TradeLog(Base):
    """실제 체결 기록."""

    __tablename__ = "trade_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(50), index=True)
    stock_code: Mapped[str] = mapped_column(String(10), index=True)
    side: Mapped[str] = mapped_column(String(10))  # buy / sell
    order_type: Mapped[str] = mapped_column(String(20))
    requested_price: Mapped[int] = mapped_column(Integer)
    executed_price: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    executed_quantity: Mapped[int] = mapped_column(Integer)
    fee: Mapped[int] = mapped_column(Integer, default=0)
    tax: Mapped[int] = mapped_column(Integer, default=0)
    slippage_bps: Mapped[float] = mapped_column(Float, default=0.0)
    signal_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    status: Mapped[str] = mapped_column(String(20), default="filled")
    is_paper: Mapped[bool] = mapped_column(Boolean, default=True)


class BacktestResult(Base):
    """백테스팅 결과 저장."""

    __tablename__ = "backtest_result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200))
    strategy_type: Mapped[str] = mapped_column(String(50))
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime] = mapped_column(DateTime)
    initial_capital: Mapped[int] = mapped_column(BigInteger)
    final_capital: Mapped[int] = mapped_column(BigInteger)
    total_return_pct: Mapped[float] = mapped_column(Float)
    cagr_pct: Mapped[float] = mapped_column(Float)
    mdd_pct: Mapped[float] = mapped_column(Float)
    sharpe_ratio: Mapped[float] = mapped_column(Float)
    win_rate_pct: Mapped[float] = mapped_column(Float)
    total_trades: Mapped[int] = mapped_column(Integer)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    detailed_report: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserSettingsRow(Base):
    """사용자 설정 저장."""

    __tablename__ = "user_settings"

    user_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    short_term_ratio: Mapped[float] = mapped_column(Float, default=0.3)
    mid_term_ratio: Mapped[float] = mapped_column(Float, default=0.7)
    total_capital: Mapped[int] = mapped_column(BigInteger, default=10_000_000)
    max_position_per_stock_pct: Mapped[float] = mapped_column(Float, default=10.0)
    hard_stop_loss_pct: Mapped[float] = mapped_column(Float, default=-3.0)
    trailing_stop_pct: Mapped[float] = mapped_column(Float, default=-3.0)
    enabled_strategies: Mapped[dict] = mapped_column(JSON, default=dict)
    enable_auto_trading: Mapped[bool] = mapped_column(Boolean, default=False)
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(String(50))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
