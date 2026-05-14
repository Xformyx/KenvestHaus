# kis-api-mcp — 한국투자증권 OpenAPI MCP 서버

한국투자증권 OpenAPI를 Model Context Protocol(MCP) 표준으로 노출하는 서버입니다. Cursor IDE, Claude Desktop, Manus 등 MCP를 지원하는 모든 AI Host에서 직접 호출하여 시세 조회, 잔고 확인, 주문 실행이 가능합니다.

## 제공 도구 (Tools)

| Tool 이름 | 설명 |
| :--- | :--- |
| `kis_get_current_price` | 종목의 현재가, 등락률, 거래량 조회 |
| `kis_get_order_book` | 10단계 호가창 조회 (OBI 계산용) |
| `kis_get_ohlcv` | 일봉/주봉/월봉 OHLCV 데이터 조회 |
| `kis_get_balance` | 계좌 잔고와 평가 손익 조회 |
| `kis_place_order` | 현금 주식 주문 실행 (지정가/시장가) |

## 환경 변수 설정

프로젝트 루트의 `.env` 파일에 다음 값을 설정합니다.

```env
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCOUNT_NO=12345678-01
KIS_IS_PAPER=true  # 모의투자(true), 실전(false)
KIS_BASE_URL=https://openapivts.koreainvestment.com:29443
```

실전 투자 URL은 `https://openapi.koreainvestment.com:9443` 입니다.

## 실행 방법

```bash
cd /path/to/KenventHaus
pip install -r packages/mcp-servers/kis-api-mcp/requirements.txt
python -m packages.mcp-servers.kis-api-mcp.src.server
```

## Cursor 연동

프로젝트 루트의 `.cursor/mcp.json`에 이미 등록되어 있습니다. Cursor를 재시작하면 채팅창에서 다음과 같이 호출할 수 있습니다.

> "삼성전자 현재가 알려줘"

> "내 계좌 잔고 보여줘"

## 주의 사항

`kis_place_order`는 실제 주문을 발생시키는 도구입니다. 운영 환경에서는 반드시 `enable_auto_trading=True` 설정과 사용자의 명시적 승인 절차를 거친 후에만 호출되어야 합니다. 본 MCP 서버 단독으로는 인증된 상위 시스템(core-engine의 execution_agent)을 통해서만 호출하는 것을 권장합니다.
