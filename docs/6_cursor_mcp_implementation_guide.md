# Cursor IDE를 활용한 MCP 서버 및 Web UI 구현 가이드

이 문서는 사용자가 Cursor IDE 환경에서 `KenvestHaus` 프로젝트의 남은 `TODO` 항목들(MCP 서버 데이터 소스 연동 및 Web UI 구축)을 AI에게 효과적으로 지시하여 완성할 수 있도록 돕는 가이드입니다.

## 1. MCP 서버 구현 가이드

각 MCP 서버는 현재 스켈레톤(껍데기)만 구현되어 있으며, 실제 데이터를 가져오는 로직이 필요합니다. Cursor 채팅창(Cmd+L 또는 Ctrl+L)에서 아래 프롬프트 예시를 복사하여 AI에게 지시하십시오.

### 1.1 `fundamental-mcp` (기업/테마 분석)

이 서버는 DART(전자공시)와 네이버 금융/FnGuide 등에서 재무 데이터를 가져와야 합니다.

**권장 데이터 소스:**
*   DART OpenAPI (OpenDART) - 공시 및 재무제표
*   `FinanceDataReader` 또는 네이버 금융 크롤링 - 테마 및 기본 재무 비율

**Cursor 프롬프트 예시:**
> "현재 `packages/mcp-servers/fundamental-mcp/src/server.py` 에 있는 `TODO`를 구현해줘.
> 1. DART OpenAPI (OpenDART)를 사용해서 `get_dart_disclosures` 도구를 구현해. `Settings`에서 `dart_api_key`를 읽어오도록 해.
> 2. `FinanceDataReader` 라이브러리를 사용해서 `get_financial_ratios` 와 `get_quarterly_results` 도구를 구현해줘. 네이버 금융 데이터를 스크래핑해도 좋아.
> 3. 비동기(`httpx` 또는 `aiohttp`)로 구현해서 블로킹이 발생하지 않게 해줘."

### 1.2 `news-sentiment-mcp` (뉴스 및 감성 분석)

이 서버는 뉴스를 수집하고 텍스트의 긍정/부정/중립을 판단해야 합니다.

**권장 데이터 소스:**
*   네이버 금융 종목 뉴스 크롤링 (`BeautifulSoup4`)
*   감성 분석: `transformers` (Hugging Face의 KoBERT 등) 또는 LLM API(OpenAI) 직접 호출

**Cursor 프롬프트 예시:**
> "`packages/mcp-servers/news-sentiment-mcp/src/server.py` 의 `TODO`를 구현할 거야.
> 1. `BeautifulSoup4`와 `httpx`를 사용해서 네이버 금융의 특정 종목 최신 뉴스를 가져오는 `crawl_stock_news` 도구를 만들어줘.
> 2. `analyze_sentiment` 도구는 OpenAI API (gpt-4.1-mini)를 사용해서 뉴스 텍스트를 입력받아 'positive', 'negative', 'neutral' 중 하나로 분류하고, 0~100점 사이의 긍정 점수를 반환하도록 구현해. `packages/shared/config/settings.py` 의 `openai_api_key`를 사용해.
> 3. 코드를 작성한 뒤 `requirements.txt` 도 업데이트해줘."

### 1.3 `macro-mcp` (글로벌 매크로)

이 서버는 미국 증시 데이터를 가져와야 합니다.

**권장 데이터 소스:**
*   `yfinance` (Yahoo Finance API)

**Cursor 프롬프트 예시:**
> "`packages/mcp-servers/macro-mcp/src/server.py` 를 완성해줘.
> 1. `yfinance` 라이브러리를 사용해서 `get_us_market_close` (다우, S&P500, 나스닥 지수) 와 `get_us_etf_movers` (SOXX, NVDA 등) 도구를 구현해.
> 2. 장 마감 후 종가와 전일 대비 등락률(%)을 정확히 계산해서 반환하도록 해.
> 3. `get_usd_krw_rate` 도구도 `yfinance` 의 `KRW=X` 심볼을 이용해 구현해줘. 비동기로 동작하게 래핑해줘."

### 1.4 `magazine-mcp` (데일리 매거진)

이 서버는 다른 MCP 도구들의 결과를 종합하여 최종 리포트를 만듭니다. 이 서버 자체는 외부 API 통신보다는 데이터 취합 및 포매팅에 집중합니다.

**Cursor 프롬프트 예시:**
> "`packages/mcp-servers/magazine-mcp/src/server.py` 의 매거진 생성 로직을 고도화할 거야.
> 지금은 정적인 텍스트만 반환하는데, 이 도구가 호출될 때 인자로 다른 데이터들(미국 증시 결과, 핫이슈 뉴스, 추천 종목 리스트 등)을 JSON 형태로 입력받도록 `inputSchema`를 수정해줘. 그리고 그 데이터를 파싱해서 `packages/telegram-bot/src/formatters.py` 에 있는 포맷처럼 깔끔한 마크다운 리포트를 생성하는 파이썬 코드를 작성해줘."

---

## 2. Web UI (Next.js) 초기화 및 구현 가이드

대시보드 역할을 할 Web UI 프로젝트를 설정하고 초기 컴포넌트를 구성합니다.

### 2.1 프로젝트 초기화

터미널을 열고 다음 명령어를 실행하여 Next.js 프로젝트를 초기화합니다. (기존 `README.md`는 덮어쓰거나 합칩니다.)

```bash
cd packages/web-ui
# 기존 README.md 백업
mv README.md README_docs.md
# Next.js 앱 생성 (기본 설정 모두 Yes 선택 권장: TypeScript, ESLint, Tailwind, App Router)
pnpm create next-app@latest .
```

### 2.2 Cursor 프롬프트 예시 (Web UI)

초기화가 끝난 후, Cursor 채팅창에서 다음 프롬프트를 사용하여 대시보드의 뼈대를 만듭니다.

**Cursor 프롬프트 예시:**
> "방금 `packages/web-ui` 에 Next.js (App Router) + Tailwind CSS 프로젝트를 초기화했어.
> `docs/4_final_system_design.md` 와 `packages/web-ui/README_docs.md` 에 명시된 요구사항을 바탕으로 메인 대시보드 레이아웃을 만들어줘.
> 
> 1. 좌측에 사이드바(Sidebar)를 만들고 다음 메뉴를 넣어: Dashboard, Signals, Recommendations, Backtest, Settings.
> 2. `app/page.tsx` (Dashboard) 에는 현재 보유 종목의 손익률을 보여주는 요약 카드 3개와, 최근 발생한 매매 시그널 목록을 보여주는 테이블 컴포넌트를 더미 데이터로 만들어줘.
> 3. `lucide-react` 아이콘을 사용해서 UI를 깔끔하게 꾸며줘."

**설정(Settings) 페이지 구현 프롬프트:**
> "`packages/web-ui/app/settings/page.tsx` 를 만들어줘.
> 이 페이지에서는 사용자가 매매 전략을 켜고 끌 수 있어야 해. `packages/shared/types/strategy.py` 에 정의된 `StrategyType` enum 값들(예: VALUE_INVESTING, MA_GOLDEN_CROSS, GOLDEN_ZONE 등)을 가져와서 각각 토글 스위치(Toggle Switch) 형태의 UI로 만들어줘.
> 단기/중기 투자 비중을 조절하는 슬라이더(Slider) 컴포넌트도 추가해줘."

---

## 3. 요약: Cursor 100% 활용 팁

1.  **컨텍스트 제공:** 프롬프트를 작성할 때 항상 관련된 파일 경로(`packages/shared/types/signals.py` 등)나 문서(`docs/2_agent_design.md`)를 언급하세요. Cursor AI가 해당 파일을 읽고 정확한 코드를 작성합니다.
2.  **점진적 구현:** 한 번에 모든 것을 해달라고 하지 말고, 하나의 MCP 서버(예: `macro-mcp`)를 먼저 완성하고 테스트한 뒤 다음 서버로 넘어가는 것이 오류를 줄이는 방법입니다.
3.  **MCP 직접 테스트:** 구현이 완료된 MCP 서버는 터미널에서 실행(`python -m packages.mcp-servers.macro-mcp.src.server`)해둔 상태로, Cursor 채팅창의 `Tools` 메뉴에서 해당 서버를 연결하여 직접 "오늘 다우지수 어때?"라고 물어보며 테스트할 수 있습니다.
