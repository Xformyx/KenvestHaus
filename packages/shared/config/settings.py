"""환경 변수 기반 설정 관리.

`.env` 파일에서 API 키와 DB 접속 정보 등을 읽어옵니다.
프로덕션에서는 환경 변수로 주입하는 것을 권장합니다.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """전체 시스템 설정."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # === 일반 ===
    app_env: str = Field("development", description="development | staging | production")
    log_level: str = Field("INFO")

    # === 한국투자증권 OpenAPI ===
    kis_app_key: Optional[str] = Field(None, description="한국투자증권 APP KEY")
    kis_app_secret: Optional[str] = Field(None, description="한국투자증권 APP SECRET")
    kis_account_no: Optional[str] = Field(None, description="계좌번호 (예: 12345678-01)")
    kis_is_paper: bool = Field(True, description="모의투자 여부 (True=모의, False=실전)")
    kis_base_url: str = Field(
        "https://openapivts.koreainvestment.com:29443",
        description="모의투자 URL. 실전: https://openapi.koreainvestment.com:9443",
    )

    # === DART OpenAPI ===
    dart_api_key: Optional[str] = Field(None, description="DART 전자공시 API Key")

    # === LLM (OpenAI 호환) ===
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"
    default_llm_model: str = "gpt-4.1-mini"

    # === 데이터베이스 ===
    postgres_url: str = Field(
        "postgresql+asyncpg://kenvent:kenvent@localhost:5432/kenventhaus",
        description="PostgreSQL 메타데이터 DB",
    )
    influx_url: str = Field("http://localhost:8086", description="InfluxDB URL")
    influx_token: Optional[str] = None
    influx_org: str = "kenventhaus"
    influx_bucket: str = "market_data"
    redis_url: str = "redis://localhost:6379/0"

    # === 텔레그램 ===
    telegram_bot_token: Optional[str] = None
    telegram_admin_chat_id: Optional[str] = None

    # === 토스증권 (조회용 - 스크래핑) ===
    toss_username: Optional[str] = None
    toss_password: Optional[str] = None

    # === 매매 시스템 파라미터 ===
    market_open_time: str = "09:00"
    market_close_time: str = "15:30"
    after_hours_report_time: str = "17:00"


@lru_cache()
def get_settings() -> Settings:
    """싱글톤 패턴으로 Settings 인스턴스 반환."""
    return Settings()
