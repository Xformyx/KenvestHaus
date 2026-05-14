# KenvestHaus

주식 종목 추천 및 자동매매 시스템. 하이브리드 아키텍처(MCP + 마이크로서비스)와 모노레포 구조로 구성됩니다.

## 핵심 컨셉

KenvestHaus는 단기(단타)부터 중기(스윙) 투자까지 모두 지원하는 AI 기반 트레이딩 어시스턴트입니다. 차트/수급 분석, 베이지안 신뢰도 산출, Lopez de Prado의 Triple-Barrier 청산 로직, 글로벌 매크로 동조화 분석 등 다양한 계량 금융 기법을 종합하여 매매 시그널을 생성하고, 사용자의 한국투자증권 계좌를 통해 실제 자동매매를 실행합니다.

## 시스템 구성

| 패키지 | 역할 |
| :--- | :--- |
| `packages/shared` | 공통 타입 정의, DB 스키마, 환경 설정 |
| `packages/core-engine` | 실시간 매매 코어 (차트/수급/의사결정/자동매매 Agent) |
| `packages/mcp-servers/kis-api-mcp` | 한국투자증권 OpenAPI MCP 서버 |
| `packages/mcp-servers/fundamental-mcp` | 기업/테마 분석 MCP 서버 |
| `packages/mcp-servers/news-sentiment-mcp` | 뉴스 크롤링 및 감성 분석 MCP 서버 |
| `packages/mcp-servers/magazine-mcp` | 데일리 트레이더스 매거진 자동 생성 MCP 서버 |
| `packages/mcp-servers/macro-mcp` | 글로벌 매크로 및 동조화 분석 MCP 서버 |
| `packages/telegram-bot` | 9가지 유형의 매매 시그널 알림 발송 봇 |
| `packages/web-ui` | Next.js 기반 통합 대시보드 |

## 설계 문서

이 프로젝트의 모든 설계 결정은 `docs/` 디렉토리에 상세히 기록되어 있습니다.

1. `docs/1_architecture_draft.md` — 초기 시스템 아키텍처 초안
2. `docs/2_agent_design.md` — Agent별 세부 설계 및 매매 전략 목록
3. `docs/3_data_pipeline_dl_design.md` — 데이터 파이프라인 및 딥러닝 학습 구조
4. `docs/4_final_system_design.md` — 텔레그램 데이터 분석을 반영한 최종 설계
5. `docs/5_cursor_dev_strategy.md` — Cursor IDE 기반 개발 전략

## 개발 환경 설정

### 의존성 설치

```bash
# Python 3.11+
pip install -r packages/shared/requirements.txt
pip install -r packages/core-engine/requirements.txt
pip install -r packages/mcp-servers/requirements.txt
pip install -r packages/telegram-bot/requirements.txt
```

### 환경 변수

프로젝트 루트에 `.env` 파일을 생성하고 다음 값을 설정합니다.

```env
# 한국투자증권 OpenAPI
KIS_APP_KEY=
KIS_APP_SECRET=
KIS_ACCOUNT_NO=12345678-01
KIS_IS_PAPER=true

# DART 전자공시
DART_API_KEY=

# 데이터베이스
POSTGRES_URL=postgresql+asyncpg://kenvest:kenvest@localhost:5432/kenvesthaus
INFLUX_URL=http://localhost:8086

# 텔레그램
TELEGRAM_BOT_TOKEN=
TELEGRAM_ADMIN_CHAT_ID=

# LLM (선택)
OPENAI_API_KEY=
```

### 테스트 실행

```bash
python -m pytest packages/core-engine/tests/ -v
```

## Cursor IDE 사용 가이드

이 프로젝트는 Cursor AI Pair Programming 환경에 최적화되어 있습니다.

`.cursorrules` 파일에 프로젝트 아키텍처 원칙과 코딩 규칙이 정의되어 있어 Cursor AI가 일관된 코드를 생성합니다. 또한 `.cursor/mcp.json` 에 KenvestHaus MCP 서버들이 등록되어 있어, Cursor 채팅에서 직접 시세 조회, 매거진 생성 등의 도구를 호출할 수 있습니다.

## 개발 단계 (Roadmap)

| Phase | 내용 | 상태 |
| :--- | :--- | :--- |
| 1 | 모노레포 구조, 공통 타입, 설계 문서화 | 진행 |
| 2 | KIS API MCP 서버 + Core Engine 기본 골격 | 진행 |
| 3 | 분석 MCP 서버 (fundamental, news, macro) 실데이터 연동 | 예정 |
| 4 | 텔레그램 봇 9가지 메시지 포매터 완성 | 진행 |
| 5 | Web UI Next.js 구현 | 예정 |
| 6 | 백테스팅 엔진 및 딥러닝 학습 파이프라인 | 예정 |
| 7 | 모의투자 검증 | 예정 |
| 8 | 실전 자동매매 활성화 | 예정 |

## 주의 사항

본 시스템이 생성하는 모든 매매 시그널은 투자 참고용이며, 매매 결정의 책임은 전적으로 사용자에게 있습니다. 실전 자동매매는 충분한 백테스팅과 모의투자 검증을 거친 후에만 활성화하는 것을 강력히 권장합니다.
