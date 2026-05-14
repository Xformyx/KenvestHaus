"""한국투자증권 OpenAPI 클라이언트 래퍼.

OAuth 인증 토큰 발급, 시세 조회, 잔고 조회, 주문 실행을 담당합니다.
모의투자(paper)와 실전(live) URL을 환경 변수로 전환 가능합니다.

API 공식 문서: https://apiportal.koreainvestment.com/
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

import httpx

from packages.shared.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class AccessToken:
    """OAuth 액세스 토큰 정보."""

    token: str
    expires_at: datetime

    @property
    def is_expired(self) -> bool:
        # 안전 마진 60초
        return datetime.now() >= self.expires_at - timedelta(seconds=60)


class KISClient:
    """한국투자증권 OpenAPI 비동기 클라이언트."""

    def __init__(
        self,
        app_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        account_no: Optional[str] = None,
        is_paper: Optional[bool] = None,
        base_url: Optional[str] = None,
    ):
        settings = get_settings()
        self.app_key = app_key or settings.kis_app_key
        self.app_secret = app_secret or settings.kis_app_secret
        self.account_no = account_no or settings.kis_account_no
        self.is_paper = is_paper if is_paper is not None else settings.kis_is_paper
        self.base_url = base_url or settings.kis_base_url

        if not self.app_key or not self.app_secret:
            logger.warning(
                "KIS APP KEY/SECRET이 설정되지 않았습니다. 실제 API 호출은 실패합니다."
            )

        self._token: Optional[AccessToken] = None
        self._token_lock = asyncio.Lock()
        self._http = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

    async def close(self) -> None:
        await self._http.aclose()

    # === 인증 ===

    async def _ensure_token(self) -> str:
        async with self._token_lock:
            if self._token is None or self._token.is_expired:
                await self._issue_token()
            assert self._token is not None
            return self._token.token

    async def _issue_token(self) -> None:
        """OAuth 액세스 토큰 발급."""
        url = "/oauth2/tokenP"
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
        }
        resp = await self._http.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        expires_in = int(data.get("expires_in", 86400))
        self._token = AccessToken(
            token=data["access_token"],
            expires_at=datetime.now() + timedelta(seconds=expires_in),
        )
        logger.info("KIS access token issued (expires in %ss)", expires_in)

    async def _headers(self, tr_id: str) -> dict[str, str]:
        token = await self._ensure_token()
        return {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": self.app_key or "",
            "appsecret": self.app_secret or "",
            "tr_id": tr_id,
            "custtype": "P",  # 개인
        }

    # === 시세 조회 ===

    async def get_current_price(self, stock_code: str) -> dict[str, Any]:
        """주식 현재가 시세 조회.

        Args:
            stock_code: 종목코드 (예: '005380' 현대차)
        """
        tr_id = "FHKST01010100"
        headers = await self._headers(tr_id)
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",  # 주식
            "FID_INPUT_ISCD": stock_code,
        }
        resp = await self._http.get(
            "/uapi/domestic-stock/v1/quotations/inquire-price",
            headers=headers,
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    async def get_order_book(self, stock_code: str) -> dict[str, Any]:
        """호가창 조회 (10단계)."""
        tr_id = "FHKST01010200"
        headers = await self._headers(tr_id)
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
        }
        resp = await self._http.get(
            "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn",
            headers=headers,
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    async def get_ohlcv(
        self, stock_code: str, period: str = "D", count: int = 100
    ) -> dict[str, Any]:
        """OHLCV 캔들 조회.

        Args:
            stock_code: 종목코드
            period: D(일), W(주), M(월)
            count: 조회 개수
        """
        tr_id = "FHKST03010100"
        headers = await self._headers(tr_id)
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_PERIOD_DIV_CODE": period,
            "FID_ORG_ADJ_PRC": "1",  # 수정주가
            "FID_INPUT_DATE_1": "",
            "FID_INPUT_DATE_2": "",
        }
        resp = await self._http.get(
            "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
            headers=headers,
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    # === 계좌/잔고 ===

    async def get_balance(self) -> dict[str, Any]:
        """주식 잔고 조회."""
        tr_id = "VTTC8434R" if self.is_paper else "TTTC8434R"
        headers = await self._headers(tr_id)
        if not self.account_no:
            raise ValueError("KIS 계좌번호가 설정되지 않았습니다.")
        cano, acnt_prdt_cd = self.account_no.split("-")
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }
        resp = await self._http.get(
            "/uapi/domestic-stock/v1/trading/inquire-balance",
            headers=headers,
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    # === 주문 ===

    async def place_order(
        self,
        stock_code: str,
        quantity: int,
        price: int,
        side: str,  # "buy" or "sell"
        order_type: str = "limit",  # limit | market
    ) -> dict[str, Any]:
        """현금 주문 실행 (지정가/시장가).

        실전투자/모의투자 TR_ID는 다릅니다.
        """
        if not self.account_no:
            raise ValueError("KIS 계좌번호가 설정되지 않았습니다.")

        if side == "buy":
            tr_id = "VTTC0802U" if self.is_paper else "TTTC0802U"
        else:
            tr_id = "VTTC0801U" if self.is_paper else "TTTC0801U"

        # 주문 구분: 00 지정가, 01 시장가
        ord_dvsn = "00" if order_type == "limit" else "01"
        ord_price = str(price) if order_type == "limit" else "0"

        headers = await self._headers(tr_id)
        cano, acnt_prdt_cd = self.account_no.split("-")
        payload = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "PDNO": stock_code,
            "ORD_DVSN": ord_dvsn,
            "ORD_QTY": str(quantity),
            "ORD_UNPR": ord_price,
        }
        resp = await self._http.post(
            "/uapi/domestic-stock/v1/trading/order-cash",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()
