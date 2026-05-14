# Cursor 기반 개발 환경을 고려한 아키텍처 전략

향후 코드를 Cursor IDE에서 관리하실 계획임을 고려하여, 개발 생산성과 AI 활용도를 극대화할 수 있는 아키텍처 및 프로젝트 구성 전략을 제안드립니다.

## 1. Cursor의 핵심 특성과 시사점

Cursor는 단순한 IDE가 아니라 LLM(Claude, GPT 등)이 코드베이스 전체를 이해하고 함께 개발하는 'AI Pair Programming' 환경입니다. 이러한 특성은 본 프로젝트의 아키텍처 결정에 다음과 같은 영향을 미칩니다.

첫째, Cursor는 **모노레포(Monorepo)** 와 같이 한 곳에 모든 코드가 있는 구조에서 가장 강력하게 동작합니다. AI가 프로젝트 전반의 컨텍스트를 한 번에 파악할 수 있기 때문입니다. 둘째, Cursor 자체가 **MCP Client**를 내장하고 있어, 사용자가 개발하는 MCP Server를 직접 Cursor에 연결하여 코드 작성 중에 테스트하고 활용할 수 있습니다. 셋째, `.cursorrules` 파일을 통해 프로젝트별로 코딩 규칙, 아키텍처 가이드, Agent 역할 정의 등을 AI에게 주입할 수 있어, 일관된 코드 품질을 유지할 수 있습니다.

## 2. 추천 전략: MCP 비중을 높인 하이브리드 + 모노레포

이전에 제안드린 하이브리드 아키텍처를 유지하되, Cursor의 강점을 최대한 활용하기 위해 **MCP 서버의 비중을 좀 더 높이고**, 전체 코드를 **모노레포 구조**로 관리하는 것을 추천합니다.

### 2.1 프로젝트 구조 (Monorepo Layout)

다음과 같은 구조로 GitHub 저장소(`Xformyx/KenventHaus`)를 구성하시면, Cursor가 전체 시스템을 잘 이해하고 개발을 도와줄 수 있습니다.

```
KenventHaus/
├── .cursorrules                    # Cursor AI 행동 규칙 정의
├── .cursor/
│   └── mcp.json                    # Cursor에 연결할 MCP 서버 설정
├── docs/                           # 설계 문서 (이번 설계안 모두 포함)
│   ├── architecture.md
│   ├── agent_design.md
│   └── trading_strategies.md
├── packages/
│   ├── core-engine/                # 실시간 매매 코어 (Python, 전통 방식)
│   │   ├── chart_agent/            # 차트/수급 분석
│   │   ├── decision_agent/         # 딥러닝 의사결정
│   │   └── execution_agent/        # 자동매매 실행
│   ├── mcp-servers/                # MCP 서버들 (분석/리포트 레이어)
│   │   ├── fundamental-mcp/        # 기업/테마 분석
│   │   ├── news-sentiment-mcp/     # 뉴스 센티멘털
│   │   ├── magazine-mcp/           # 데일리 매거진 생성
│   │   ├── macro-mcp/              # 글로벌 매크로
│   │   └── kis-api-mcp/            # 한국투자증권 API 래퍼
│   ├── web-ui/                     # Web Dashboard (Next.js 등)
│   ├── telegram-bot/               # 텔레그램 알림 봇
│   └── shared/                     # 공통 타입, 유틸, DB 스키마
├── data/
│   ├── backtest/                   # 백테스팅 결과
│   └── models/                     # 학습된 딥러닝 모델
├── scripts/                        # 운영 스크립트
├── docker-compose.yml              # 로컬 개발 환경
└── README.md
```

### 2.2 `.cursorrules` 활용 전략

`.cursorrules` 파일에 본 설계 문서의 핵심 내용을 요약하여 작성해두면, Cursor AI가 코드를 작성하거나 수정할 때 항상 이 규칙을 따르게 됩니다. 예를 들어 "차트 분석 Agent의 시그널 생성 함수는 항상 결정론적이어야 하며 LLM 호출을 포함해서는 안 된다", "Triple-Barrier 청산 로직은 Lopez de Prado(2018)의 정의를 따를 것"과 같은 규칙을 명시할 수 있습니다.

### 2.3 Cursor의 MCP Client 활용

`.cursor/mcp.json`에 본 프로젝트의 MCP 서버들을 등록해두면, Cursor 채팅창에서 직접 "어제 코스피 강세 테마 뭐였어?"나 "삼성전자 최근 공시 요약해줘"와 같이 질문할 수 있고, AI가 본인이 만든 MCP 서버를 호출하여 답변해줍니다. 이를 통해 개발 중에 실시간으로 시스템을 검증하고 디버깅할 수 있습니다.

## 3. MCP 비중을 더 높이는 이유

Cursor 환경에서는 MCP를 적극 활용할수록 다음 이점이 커집니다.

| 항목 | 이점 |
| :--- | :--- |
| **개발 속도** | MCP 표준을 따르면 Cursor AI가 도구 사용 패턴을 잘 이해하므로 코드 생성 정확도가 높아짐 |
| **재사용성** | 동일한 MCP 서버를 Cursor, Claude Desktop, Manus 등 여러 환경에서 활용 가능 |
| **테스트 용이성** | MCP는 표준 인터페이스이므로 단위 테스트 작성이 명확함 |
| **점진적 개발** | MCP 서버를 하나씩 추가하면서 시스템을 확장할 수 있어 초기 진입 장벽이 낮음 |

## 4. 단, 실시간 매매 코어는 그대로 유지

자동매매와 같이 ms 단위 성능과 결정론적 동작이 필요한 부분은 여전히 일반 Python 코드(전통 마이크로서비스)로 두는 것이 좋습니다. Cursor는 일반 Python 코드도 매우 잘 다루므로, MCP가 아니어도 개발 생산성에는 문제가 없습니다.

## 5. 권장 개발 순서

Cursor 환경에서의 점진적 개발 순서는 다음과 같이 제안드립니다.

1. **저장소 초기화 및 문서화:** 본 설계 문서들을 `docs/` 에 커밋하고, `.cursorrules` 작성. (Cursor AI에게 프로젝트 컨텍스트 제공)
2. **MCP 서버 1개 우선 개발:** 가장 만들기 쉬운 `kis-api-mcp`(한국투자증권 API 래퍼)부터 개발하여 Cursor에 연결. 채팅으로 "삼성전자 현재가" 같은 질문을 던져 동작 검증.
3. **실시간 코어 엔진 개발:** `core-engine` 디렉토리에 차트/수급 Agent를 일반 Python으로 구현.
4. **분석 MCP 서버 확장:** 뉴스 센티멘털, 매거진 생성 등 MCP 서버를 추가 개발.
5. **Web UI 및 통합:** 마지막으로 대시보드와 텔레그램 봇을 붙여 완성.

## 6. 결론

Cursor에서 관리하실 것이라면, **모노레포 + .cursorrules + MCP 비중 확대** 조합을 강력 추천드립니다. 이 전략은 사용자가 혼자 개발하더라도 Cursor AI가 든든한 페어 프로그래머 역할을 하여 개발 속도와 코드 품질을 모두 끌어올려 줄 것입니다.
