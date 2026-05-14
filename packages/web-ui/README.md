# web-ui — KenventHaus Web Dashboard

Next.js + TypeScript + TailwindCSS 기반의 통합 대시보드입니다.

## 주요 페이지 및 기능

| 페이지 | 기능 |
| :--- | :--- |
| `/dashboard` | 보유 종목 통합 조회 (한국투자증권 + 토스증권), 실시간 수익률 |
| `/signals` | Agent들이 발생시킨 매매 시그널 리스트 (필터/정렬 가능) |
| `/recommendations` | 종목 추천 (단기/중기 모두 노출, 비중 설정과 무관) |
| `/settings` | 단기/중기 비중 조절 (자동매매 시에만 적용), 매매 기법 Check/Uncheck |
| `/backtest` | 백테스팅 결과 리포트 (CAGR, MDD, 승률, 시그널별 성과) |
| `/portfolio` | 포지션 관리 (Triple-Barrier 진행 상황 시각화) |
| `/magazine` | 데일리 트레이더스 매거진 아카이브 |

## 초기화 방법

추후 Cursor에서 다음 명령으로 Next.js 프로젝트를 초기화할 예정입니다.

```bash
cd packages/web-ui
pnpm create next-app@latest . --typescript --tailwind --eslint --app --src-dir
```

## 백엔드 연동

- 실시간 시세: WebSocket (한국투자증권 실시간 API)
- 매매 시그널/포지션: PostgreSQL → FastAPI 백엔드 → REST
- 시계열 차트: InfluxDB → Recharts/Lightweight Charts
- MCP 호출: 백엔드 프록시를 통해 매거진 자동 생성 등 LLM 분석 트리거

## 설계 원칙

설계 문서 `docs/4_final_system_design.md` 의 Web UI Dashboard 절을 따릅니다. 모든 매매 기법은 사용자가 활성화/비활성화할 수 있어야 하며, 각 기법 옆에 툴팁으로 간단한 설명이 표시되어야 합니다.
