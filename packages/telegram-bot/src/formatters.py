"""텔레그램 메시지 포매터.

사용자가 제공한 9가지 메시지 유형(pasted_content.txt)을 그대로 재현하는 포매터입니다.
실제 텔레그램 메시지 양식과 100% 일치하도록 설계되었습니다.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional


def format_golden_zone(
    stock_name: str,
    stock_code: str,
    current_price: int,
    change_pct: float,
    strength: float,
    trading_value_billion: float,
    bayesian_pct: float,
    empirical_pct: float,
    samples: int,
    bayesian_label: str,
    market_regime: str,
    filter_score: int,
    filter_label: str,
    buy_low: int,
    buy_high: int,
    take_profit: int,
    stop_loss: int,
    risk_reward: float,
    total_learning: int,
    avg_win_rate: float,
    avg_return: float,
    now: Optional[datetime] = None,
) -> str:
    """단타 골든존 메시지 (유형 2)."""
    now = now or datetime.now()
    regime_emoji = "🌊" if market_regime == "변동성 장" else "✅"
    bayes_emoji = "🟢" if bayesian_pct >= 70 else "🟡" if bayesian_pct >= 50 else "🔴"

    if filter_label == "STRONG_BUY":
        filter_emoji = "🚀"
    elif filter_label == "BUY":
        filter_emoji = "📈"
    elif filter_label == "NEUTRAL":
        filter_emoji = "⚖️"
    else:
        filter_emoji = "⚠️"

    return f"""💎 단타 골든존 🔴
━━━━━━━━━━━━━━━━

📌 {stock_name} ({stock_code})
💰 현재가: {current_price:,}원 ({change_pct:+.2f}%)
⚡ 체결강도: {strength:.0f}
💵 거래대금: {trading_value_billion:.0f}억원

🤖 AI 신뢰도: {bayes_emoji} 베이지안 {bayesian_pct:.0f}% (실측 {empirical_pct:.0f}% · {samples}건 학습 · {bayesian_label})
⚠️ 시장체제: {regime_emoji} {market_regime}
🔬 4중 필터: {filter_emoji} {filter_score}점 ({filter_label})

🎯 매매 가이드
  └ 매수: {buy_low:,}~{buy_high:,}원 (현재가 ±0.5%)
  └ 익절: {take_profit:,}원 ({(take_profit/current_price-1)*100:+.1f}%)
  └ 손절: {stop_loss:,}원 ({(stop_loss/current_price-1)*100:+.1f}%)
  └ 손익비: 1:{risk_reward:.1f}

⏰ 매수 타이밍
  └ 5분봉 GC 확인 후 진입 (지금 또는 다음 봉)
  └ 거래량 평소 3배+ 유지 시 적정
⏱ 매도 타이밍
  └ 익절 1차: +2.0% (절반 매도)
  └ 익절 2차: +4.0% (전량 청산)
  └ 손절: -2.0% 또는 5분봉 DC

📊 전체 학습 (누적 {total_learning}회)
  └ 🔴 평균 승률 {avg_win_rate:.0f}% · 수익률 {avg_return:.2f}%

💡 대응 전략
  └ 분할매수 적정 — 5분봉 GC 확인 후 진입

✓ 골든존(5~13%) 단타 진입 적정 구간
✓ 지지선 이탈 시 즉시 손절, 욕심 금물

🕒 {now.strftime('%H:%M:%S')} · 즉시 알림
📐 기본값 적용 (학습 데이터 누적 중)
🤖 자동 추적 시작 — 청산 조건 발동 시 알림 발송
   └ 체결강도 105 이하 / 익절 / 손절 / 시간 한계 / 추세 전환
📚 Lopez de Prado (2018) Triple-Barrier
⚠ 참고용 — 매수 결정은 본인 책임"""


def format_portfolio_mgmt(
    stock_name: str,
    stock_code: str,
    signal: str,
    entry_price: int,
    current_price: int,
    pnl_pct: float,
    hold_minutes: int,
    obi: float,
    strength: float,
    high_pnl_pct: float,
    bayesian_pct: float,
    samples: int,
    market_regime: str,
    recommendation: str,
    now: Optional[datetime] = None,
) -> str:
    """포트폴리오 관리 메시지 (유형 3)."""
    now = now or datetime.now()
    pnl_emoji = "🟢" if pnl_pct > 5 else "🟡" if pnl_pct > 0 else "🔴"
    obi_emoji = "🟢" if obi > 0.3 else "⚪" if obi > -0.3 else "🔴"
    obi_label = "매수우위" if obi > 0.3 else "균형" if obi > -0.3 else "매도우위"

    return f"""⏰ 포트폴리오 관리 — 시간 한계 임박 (재평가 필요)
━━━━━━━━━━━━━━━━

📌 {stock_name} ({stock_code})
   신호: ✨ {signal}

📥 진입: {entry_price:,}원
📤 현재: {current_price:,}원
💰 손익: {pnl_emoji} {pnl_pct:+.2f}% (보유 {hold_minutes}분)

📊 현황
  └ OBI: {obi:.2f} ({obi_emoji} {obi_label})
  └ 체결강도: {strength:.0f}
  └ 고점 손익: {high_pnl_pct:+.2f}%

💡 권장: {recommendation}

🤖 AI 컨텍스트
  └ 🤖 베이지안 {bayesian_pct:.0f}% ({samples}건) 🟡
  └ ⚠️ 🌊 {market_regime}

🕒 {now.strftime('%H:%M:%S')} · 포트폴리오 자동 관리
⚠ 참고용 — 매매 결정은 본인 책임"""


def format_limit_up_imminent(
    stock_name: str,
    stock_code: str,
    current_price: int,
    change_pct: float,
    strength: float,
    trading_value_billion: float,
    bayesian_pct: float,
    empirical_pct: float,
    samples: int,
    bayesian_label: str,
    market_regime: str,
    filter_score: int,
    filter_label: str,
    buy_low: int,
    buy_high: int,
    take_profit: int,
    stop_loss: int,
    total_learning: int,
    avg_win_rate: float,
    avg_return: float,
    now: Optional[datetime] = None,
) -> str:
    """상한가 임박 메시지 (유형 4)."""
    now = now or datetime.now()
    return f"""🚀 상한가 임박 🔴
━━━━━━━━━━━━━━━━

📌 {stock_name} ({stock_code})
💰 현재가: {current_price:,}원 ({change_pct:+.2f}%)
⚡ 체결강도: {strength:.0f}
💵 거래대금: {trading_value_billion:.0f}억원

🤖 AI 신뢰도: 🔴 베이지안 {bayesian_pct:.0f}% (실측 {empirical_pct:.0f}% · {samples}건 학습 · {bayesian_label})
⚠️ 시장체제: 🌊 {market_regime}
🔬 4중 필터: 🚀 {filter_score}점 ({filter_label})

🎯 매매 가이드
  └ 매수: {buy_low:,}~{buy_high:,}원 (현재가 ±0.5%)
  └ 익절: {take_profit:,}원 ({(take_profit/current_price-1)*100:+.1f}%)
  └ 손절: {stop_loss:,}원 ({(stop_loss/current_price-1)*100:+.1f}%)
  └ 손익비: 1:1.0

⏰ 매수 타이밍
  └ ⚠ 추격매수 자제 (이미 상한가 근접)
  └ 익일 갭상 베팅: 종가 무렵 5% 이내 분할
⏱ 매도 타이밍
  └ 익일 시초가 +1~3% 익절 권장
  └ 갭하락 시 손절 -2%

📊 전체 학습 (누적 {total_learning}회)
  └ 🔴 평균 승률 {avg_win_rate:.0f}% · 수익률 {avg_return:.2f}%

💡 대응 전략
  └ 추격매수 자제, 익일 갭상 베팅 검토

⚠ 상한가 부근 — 추격 자제, 갭상 베팅 검토
⚠ 연속 상한가 전력 확인 (네이버 차트)

🕒 {now.strftime('%H:%M:%S')} · 즉시 알림
📐 기본값 적용 (학습 데이터 누적 중)
🤖 자동 추적 시작 — 청산 조건 발동 시 알림 발송
   └ 체결강도 100 이하 / 익절 / 손절 / 시간 한계 / 추세 전환
📚 Lopez de Prado (2018) Triple-Barrier
⚠ 참고용 — 매수 결정은 본인 책임"""


def format_realtime_abnormal(
    stock_name: str,
    stock_code: str,
    anomaly_type: str,
    multiplier: float,
    sigma: float,
    now: Optional[datetime] = None,
) -> str:
    """실시간 이상신호 메시지 (유형 6)."""
    now = now or datetime.now()
    return f"""🚨🚨🚨 실시간 이상 신호

📊 {stock_name} ({stock_code})

🔥 {anomaly_type}: 평균 대비 {multiplier:.1f}배 (σ={sigma:.1f})

⏰ {now.strftime('%H:%M:%S')}"""


def format_smart_money_scan(
    market_regime: str,
    entries: list[dict],
    now: Optional[datetime] = None,
) -> str:
    """수급 알림 스캔 메시지 (유형 7)."""
    now = now or datetime.now()
    ranks = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    lines = [
        "🔔 수급 알림 스캔 결과",
        f"⏰ {now.strftime('%Y-%m-%d %H:%M')}",
        "",
        f"🚨 {len(entries)}개 종목에서 수급 신호 감지",
        "",
        f"  ⚠️ 🌊 {market_regime}",
        "",
    ]
    for i, e in enumerate(entries):
        rank = ranks[i] if i < len(ranks) else f"{i+1}."
        flow = e["smart_money_flow_billion"]
        flow_emoji = "💎 💎" if flow > 0 else "☠️ ☠️"
        lines.append(f"{rank} {e['stock_name']} ({e['stock_code']})")
        lines.append(
            f"   {flow_emoji} 스마트머니 {flow:+.0f}억 / 개인 {e['retail_flow_billion']:+.0f}억"
        )
        if e.get("foreigner_change"):
            f_emoji = "🟢" if "buy" in e["foreigner_change"].split("→")[-1] else "🔴"
            lines.append(f"   🌍 {f_emoji} 외국인 {e['foreigner_change']}")
        if e.get("institution_change"):
            i_emoji = "🟢" if "buy" in e["institution_change"].split("→")[-1] else "🔴"
            lines.append(f"   🏦 {i_emoji} 금융투자 {e['institution_change']}")
        lines.append("")
    return "\n".join(lines)


def format_lunch_checkin(
    active_count: int,
    long_term_pick: dict,
    theme_pick: dict,
    now: Optional[datetime] = None,
) -> str:
    """점심시간 중간점검 (유형 5)."""
    now = now or datetime.now()
    return f"""단타 {active_count}건 청산 알림 대기
  2️⃣ 중장기 진입: {long_term_pick['name']} (신뢰 {long_term_pick['confidence']}%) 분할 매수 시작
  3️⃣ 강세 테마: {theme_pick['theme']} 주도주 {theme_pick['leader']} 단타 진입 검토

🕒 {now.strftime('%Y-%m-%d %H:%M')}
📚 통합: Wolpert(1992) Stacked Gen · Markowitz(1952) Portfolio
⚠ 참고용 — 매매 결정은 본인 책임"""


def format_daily_closing(
    top_themes: list[dict],
    limit_up_stocks: list[str],
    tomorrow_top_picks: list[dict],
    ai_learning_result: dict,
    now: Optional[datetime] = None,
) -> str:
    """장마감 종합정리 (유형 9)."""
    now = now or datetime.now()
    weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][
        now.weekday()
    ]
    lines = [
        "🌆 장마감 종합정리",
        f"📅 {now.strftime('%Y-%m-%d')} {weekday} · ⏰ {now.strftime('%H:%M')}",
        "━━━━━━━━━━━━━━━━━━",
        "",
        f"🔥 오늘 돈 쏠린 테마 TOP{len(top_themes)}",
        "",
    ]
    for t in top_themes:
        lines.append(f"[{t['theme_name']}] ▲{t['avg_change_pct']:.2f}%")
        lines.append(f"  └ {t['theme_name']} 섹터 강세")
        lines.append(f"  └ 주도주: {t['leader_stock']}")
        lines.append("")

    lines.append(f"💎 오늘 상한가 ({len(limit_up_stocks)}개)")
    for s in limit_up_stocks[:8]:
        lines.append(f"  • {s}")
    if len(limit_up_stocks) > 8:
        lines.append(f"  ... 외 {len(limit_up_stocks) - 8}개")
    lines.append("")

    lines.append(f"🎯 내일 상승여력 TOP{len(tomorrow_top_picks)} (판단 근거)")
    lines.append("")
    for i, p in enumerate(tomorrow_top_picks, 1):
        lines.append(f"{i}위 {p['name']} · {p['score']}점")
        lines.append(f"  └ 오늘 {p['today_change']:+.2f}% · 종가 {p['close_price']:,}원")
        lines.append(f"  └ 신호: {p['signals']}")
        lines.append("")

    lines.append("")
    lines.append("🧠 오늘 AI 학습 결과")
    lines.append(
        f"  └ ⚠️ 청산 {ai_learning_result['exits']}건 / "
        f"승률 {ai_learning_result['win_rate']}% / "
        f"평균 {ai_learning_result['avg_return']:.2f}%"
    )
    lines.append(f"  └ ⚠️ 🌊 {ai_learning_result.get('regime', '변동성 장')}")
    lines.append("  └ 💡 자세한 분석은 15:35 v7 일일 요약 참고")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("⚠️ 본 정보는 투자 참고용 — 매매 결정의 책임은 본인에게 있습니다.")

    return "\n".join(lines)
