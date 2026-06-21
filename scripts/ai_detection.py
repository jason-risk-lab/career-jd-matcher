#!/usr/bin/env python3
"""한국어 AI 작문 표지 결정적 카운터 (Tier 2 / v1.7 신규).

references/korean-ai-detection.md의 6개 카테고리(A~F) 규칙을 결정적으로
카운트하여 BLACK 페르소나 항목 (11) "AI 작문 표지 없음" 점수의 근거를 만든다.

목적: BLACK 페르소나가 임계치를 "눈으로 세는" 비결정성을 제거. 같은 입력 →
항상 같은 카운트·감점·점수. 단, 본 스크립트는 **보조 도구**다. 자동 리라이팅하지
않으며, 최종 판단·예외(정체성 선언, PT/보고서 문맥)는 BLACK 페르소나가 내린다.

사용:
    python ai_detection.py path/to/cover_letter.txt
    python ai_detection.py path/to/cover_letter.md --json
    cat cover_letter.txt | python ai_detection.py -

출력(기본): 사람이 읽는 요약 + 카테고리별 표.
출력(--json): 기계가 읽는 JSON (BLACK sub-agent 입력용).

임계치 출처: references/korean-ai-detection.md. 카테고리별로 임계치 초과 시
감점하며, 6개 합산 감점 ≤ 2점이면 통과(BLACK 항목 11 기준).
"""

import argparse
import json
import re
import sys
from pathlib import Path


# --- 카테고리별 검출 패턴 (korean-ai-detection.md와 동기화) ---

PATTERNS_A = [  # 회피형 종결어미 — 1000자당 3건 초과 시 -1
    r"할 수 있도록", r"에 기여하고자", r"을 도모하여", r"를 도모하여",
    r"을 통해 성장하고자", r"의 일익을 담당하고자", r"에 보탬이 되고자",
    r"을 추구하고자", r"를 추구하고자",
]
PATTERNS_B = [  # 추상 성취어 — 전체 5건 초과 시 -1
    r"다양한 경험", r"폭넓은 역량", r"탁월한 성과", r"체계적인 접근",
    r"전문성을 바탕으로", r"통찰력 있는", r"차별화된 시각",
]
PATTERNS_C = [  # 균형 강박(양시론) — 2회 이상 시 -1
    r"한편으로는", r"장점이 있는 반면", r"의 한계도 있어", r"\b다만\b", r"\b반면\b",
]
PATTERNS_D = [  # 과도한 접속어 — 문단당 1건 초과 시 -1, 전체 5건 초과 시 -2
    r"따라서", r"뿐만 아니라", r"또한", r"더불어", r"이러한 점에서", r"이를 통해",
]
PATTERNS_E = [  # 구조 강박 — 본문 1회 이상 시 -2 (강한 감점)
    r"첫째", r"둘째", r"셋째", r"\d+\s*가지 관점", r"\d+\s*가지 측면", r"\d+\s*단계",
]
# F 미사여구 헤더 — 첫 비어있지 않은 줄이 따옴표로 시작하면 -1
HEADER_QUOTE_RE = re.compile(r'^\s*["「『].*["」』]\s*$')


def count_patterns(text, patterns):
    """패턴 목록의 총 발생 횟수와 패턴별 내역을 반환."""
    total = 0
    detail = {}
    for p in patterns:
        n = len(re.findall(p, text))
        if n:
            detail[p] = n
        total += n
    return total, detail


def split_paragraphs(text):
    """빈 줄 기준으로 문단 분리."""
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


def analyze(text):
    """전체 텍스트를 분석해 카테고리별 카운트·감점·종합 점수를 산출."""
    char_count = len(re.sub(r"\s", "", text))
    paragraphs = split_paragraphs(text)
    results = {}

    # A. 회피형 종결어미: 1000자당 3건 초과
    a_total, a_detail = count_patterns(text, PATTERNS_A)
    a_rate = (a_total / char_count * 1000) if char_count else 0
    a_deduct = 1 if a_rate > 3 else 0
    results["A_evasive_endings"] = {
        "count": a_total, "per_1000_chars": round(a_rate, 2),
        "threshold": "1000자당 3건 초과", "deduction": a_deduct, "detail": a_detail,
    }

    # B. 추상 성취어: 전체 5건 초과
    b_total, b_detail = count_patterns(text, PATTERNS_B)
    b_deduct = 1 if b_total > 5 else 0
    results["B_abstract_achievement"] = {
        "count": b_total, "threshold": "전체 5건 초과",
        "deduction": b_deduct, "detail": b_detail,
    }

    # C. 균형 강박: 2회 이상
    c_total, c_detail = count_patterns(text, PATTERNS_C)
    c_deduct = 1 if c_total >= 2 else 0
    results["C_forced_balance"] = {
        "count": c_total, "threshold": "2회 이상",
        "deduction": c_deduct, "detail": c_detail,
    }

    # D. 과도한 접속어: 문단당 1건 초과(-1) 또는 전체 5건 초과(-2), 큰 값 적용
    d_total, d_detail = count_patterns(text, PATTERNS_D)
    d_max_per_para = 0
    for para in paragraphs:
        n, _ = count_patterns(para, PATTERNS_D)
        d_max_per_para = max(d_max_per_para, n)
    d_deduct = 2 if d_total > 5 else (1 if d_max_per_para > 1 else 0)
    results["D_excess_connectives"] = {
        "count": d_total, "max_per_paragraph": d_max_per_para,
        "threshold": "문단당 1건 초과(-1) / 전체 5건 초과(-2)",
        "deduction": d_deduct, "detail": d_detail,
    }

    # E. 구조 강박: 본문 1회 이상 → -2 (PT/보고서/JD 요구 문항은 예외 가능)
    e_total, e_detail = count_patterns(text, PATTERNS_E)
    e_deduct = 2 if e_total >= 1 else 0
    results["E_structural_compulsion"] = {
        "count": e_total, "threshold": "본문 1회 이상(강한 감점)",
        "deduction": e_deduct, "detail": e_detail,
        "note": "PT 발표안·분석 보고서·'N가지 강점을 적어주세요' 문항은 예외. 문맥은 BLACK이 판단.",
    }

    # F. 미사여구 헤더: 첫 비어있지 않은 줄이 따옴표로 시작
    first_line = next((ln for ln in text.splitlines() if ln.strip()), "")
    f_hit = bool(HEADER_QUOTE_RE.match(first_line))
    f_deduct = 1 if f_hit else 0
    results["F_decorative_header"] = {
        "count": 1 if f_hit else 0, "threshold": "1건 시 감점",
        "deduction": f_deduct, "first_line": first_line.strip()[:60],
    }

    total_deduction = sum(v["deduction"] for v in results.values())
    score = max(0, 10 - total_deduction)
    passed = total_deduction <= 2

    return {
        "char_count": char_count,
        "paragraph_count": len(paragraphs),
        "categories": results,
        "total_deduction": total_deduction,
        "suggested_black_item11_score": score,
        "pass": passed,
        "pass_threshold": "합산 감점 ≤ 2점",
        "advisory": "보조 카운트일 뿐 자동 리라이팅 금지. 정체성 선언·문맥 예외는 BLACK이 최종 판단.",
    }


def format_human(result):
    """사람이 읽는 요약 출력."""
    lines = []
    lines.append(f"글자 수(공백 제외): {result['char_count']} / 문단: {result['paragraph_count']}")
    lines.append("")
    lines.append(f"{'카테고리':<28}{'카운트':>8}{'감점':>6}")
    lines.append("-" * 44)
    labels = {
        "A_evasive_endings": "A 회피형 종결어미",
        "B_abstract_achievement": "B 추상 성취어",
        "C_forced_balance": "C 균형 강박",
        "D_excess_connectives": "D 과도한 접속어",
        "E_structural_compulsion": "E 구조 강박",
        "F_decorative_header": "F 미사여구 헤더",
    }
    for key, label in labels.items():
        c = result["categories"][key]
        lines.append(f"{label:<26}{c['count']:>8}{c['deduction']:>6}")
    lines.append("-" * 44)
    lines.append(f"{'합산 감점':<26}{'':>8}{result['total_deduction']:>6}")
    lines.append("")
    verdict = "PASS ✅" if result["pass"] else "FAIL ❌"
    lines.append(f"BLACK 항목(11) 제안 점수: {result['suggested_black_item11_score']}/10  →  {verdict} (기준: 합산 감점 ≤ 2)")
    lines.append(f"※ {result['advisory']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="한국어 AI 작문 표지 결정적 카운터 (korean-ai-detection.md 동기화)")
    parser.add_argument("input", help="자소서 텍스트 파일 경로. '-' 이면 stdin.")
    parser.add_argument("--json", action="store_true", help="JSON 출력 (BLACK sub-agent 입력용)")
    args = parser.parse_args()

    # Windows 콘솔(cp949)에서도 이모지·한글을 안전하게 출력.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    if args.input == "-":
        text = sys.stdin.read()
    else:
        text = Path(args.input).read_text(encoding="utf-8")

    result = analyze(text)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_human(result))
    # 통과 시 0, 임계 초과 시 1 (CI/회귀 연동용)
    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
