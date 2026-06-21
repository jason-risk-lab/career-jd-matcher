#!/usr/bin/env python3
"""career-jd-matcher 스킬 회귀 검증 러너 (v1.5 신규).

본 스크립트는 스킬을 직접 호출하지 않는다. 사용자가 Claude 세션에서
스킬을 실행한 뒤 산출물(.docx + 마크다운 보고서)을 fixtures/<case>/outputs/에
저장하면, 본 스크립트가 expected.yaml 기준으로 검증한다.

Phase 3-10 v1.5 단계에서는 골격만 제공. 사용자가 본인 케이스로 fixtures를
채운 뒤 사용한다.
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML 필요. 설치: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_expected(case_dir: Path) -> dict:
    expected_path = case_dir / "expected.yaml"
    if not expected_path.exists():
        raise FileNotFoundError(f"expected.yaml 없음: {expected_path}")
    with open(expected_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_outputs(case_dir: Path) -> dict:
    """사용자가 저장한 산출물 회수. 마크다운 보고서 + 3개 docx."""
    outputs_dir = case_dir / "outputs"
    if not outputs_dir.exists():
        raise FileNotFoundError(
            f"산출물 폴더 없음: {outputs_dir}\n"
            f"스킬 실행 후 결과를 {outputs_dir}/에 저장하세요:\n"
            f"  - report.md (채팅 마크다운 보고서 복사)\n"
            f"  - 경력기술서_*.docx\n"
            f"  - 자기소개서_*.docx\n"
            f"  - 지원분석보고서_*.docx"
        )

    report_md = outputs_dir / "report.md"
    if not report_md.exists():
        raise FileNotFoundError(f"report.md 없음: {report_md}")

    docx_files = sorted(outputs_dir.glob("*.docx"))
    return {
        "report_md": report_md.read_text(encoding="utf-8"),
        "docx_files": docx_files,
        "outputs_dir": outputs_dir,
    }


def check_company_analysis(expected: dict, report: str) -> list:
    issues = []
    ca = expected.get("company_analysis", {})

    frameworks = ca.get("frameworks_applied", [])
    for fw in frameworks:
        if fw not in report:
            issues.append(f"회사 분석에 '{fw}' 프레임워크 적용 흔적 없음")

    citation_min = ca.get("scholar_citations_min", 0)
    citation_patterns = ["Porter", "Christensen", "Damodaran", "Henderson",
                         "Hamel", "McGrath", "Moore", "Ries", "COSO", "IIA"]
    found = sum(1 for p in citation_patterns if p in report)
    if found < citation_min:
        issues.append(f"학자 인용 부족: {found}건 < 기준 {citation_min}건")

    return issues


def check_jd_matching(expected: dict, report: str) -> list:
    issues = []
    jm = expected.get("jd_matching", {})

    rng = jm.get("match_rate_range", [0, 100])
    match = re.search(r"종합[\s\S]*?(\d{1,3})\s*%", report)
    if match:
        rate = int(match.group(1))
        if not (rng[0] <= rate <= rng[1]):
            issues.append(f"매칭률 {rate}%가 기대 범위 {rng} 벗어남")
    else:
        issues.append("종합 매칭률을 보고서에서 찾지 못함")

    return issues


def check_persona_evaluation(expected: dict, report: str) -> list:
    issues = []
    pe = expected.get("persona_evaluation", {})

    if pe.get("stage_0_fact_checker", {}).get("hard_claims_pass"):
        # 보고서에는 "Hard Fail" 컬럼 헤더가 상시 등장하므로 전체 텍스트에
        # "fail"이 있는지로 판정하면 안 된다(상시 오탐). 5.3의 최종 판정 라인만 본다.
        m = re.search(r"Fact-Checker\s*최종\s*판정[:\s]*([✅❌⏸]?\s*[A-Za-z_]+)", report)
        if m:
            verdict = m.group(1).upper()
            if "PASS" not in verdict and "✅" not in m.group(1):
                issues.append(
                    f"Stage 0 Fact-Checker 최종 판정이 PASS가 아님 (기대: Pass) — '{m.group(1).strip()}'")
        else:
            issues.append("Fact-Checker 최종 판정 라인(5.3)을 보고서에서 찾지 못함")

    avg_min = pe.get("final_average_min")
    if avg_min:
        match = re.search(r"최종 평균[:\s]*(\d+\.\d+)", report)
        if match:
            avg = float(match.group(1))
            if avg < avg_min:
                issues.append(f"최종 평균 {avg} < 기준 {avg_min}")

    return issues


def check_decision_matrix(expected: dict, report: str) -> list:
    issues = []
    dm = expected.get("decision_matrix", {})

    rng = dm.get("total_score_range", [0, 100])
    match = re.search(r"종합\s*점수[\s\S]*?(\d+\.\d+)\s*/\s*100", report)
    if match:
        score = float(match.group(1))
        if not (rng[0] <= score <= rng[1]):
            issues.append(f"의사결정 매트릭스 점수 {score}이 기대 범위 {rng} 벗어남")
    else:
        issues.append("종합 점수를 보고서에서 찾지 못함")

    recommendation = dm.get("recommendation")
    if recommendation and recommendation not in report:
        issues.append(f"권고 등급 '{recommendation}' 보고서에 없음")

    return issues


def check_outputs(expected: dict, outputs: dict) -> list:
    issues = []
    out_spec = expected.get("outputs", {})

    expected_count = out_spec.get("docx_files_count", 3)
    actual_count = len(outputs["docx_files"])
    if actual_count != expected_count:
        issues.append(f"docx 파일 수 {actual_count} ≠ 기대 {expected_count}")

    patterns = out_spec.get("filenames", [])
    for pat in patterns:
        regex = re.compile(pat.replace("*", ".*"))
        if not any(regex.match(p.name) for p in outputs["docx_files"]):
            issues.append(f"docx 파일명 패턴 매치 없음: {pat}")

    sections = out_spec.get("markdown_sections_present", [])
    for sec in sections:
        if not re.search(rf"^##?\s*{re.escape(sec)}", outputs["report_md"], re.M):
            issues.append(f"마크다운 섹션 '{sec}' 없음")

    return issues


def check_must_not(expected: dict, report: str) -> list:
    issues = []
    forbidden = expected.get("must_not", [])

    # "거짓 사실 추가" 금지 검증: 보고서 전체의 ❌ 개수로 보면 표의 Fail 마커까지
    # 잡혀 상시 오탐이다. 대신 5.3이 명시하는 긍정 확인 문구의 '부재'를 신호로 본다.
    if any("거짓" in k for k in forbidden):
        if not re.search(r"거짓\s*사실\s*추가\s*없음", report):
            issues.append("'거짓 사실 추가 없음' 확인 문구(5.3)가 보고서에 없음")

    # AI 작문 표지: 보고서는 패턴명·Before/After를 본문에 인용하므로 전체 카운트는
    # 무의미하다. 보고서가 스스로 집계해 적는 'BLACK 항목 (11) ... X건'만 신뢰한다.
    if "한국어 AI 작문 표지" in str(forbidden):
        m = re.search(r"AI\s*작문\s*표지[:\s]*(\d+)\s*건", report)
        if m:
            count = int(m.group(1))
            threshold = 2  # korean-ai-detection.md: 합산 감점 ≤ 2점 기준
            if count > threshold:
                issues.append(
                    f"BLACK 항목 (11) AI 작문 표지 {count}건 (기준 {threshold}건 초과)")
        else:
            issues.append("BLACK 항목 (11) AI 작문 표지 집계(5.3)를 보고서에서 찾지 못함")

    return issues


CHECKS = [
    ("회사 분석", check_company_analysis, "report"),
    ("JD 매칭", check_jd_matching, "report"),
    ("페르소나 평가", check_persona_evaluation, "report"),
    ("의사결정 매트릭스", check_decision_matrix, "report"),
    ("산출물", check_outputs, "outputs"),
    ("금지 거동", check_must_not, "report"),
]


def run_case(case_id: str) -> int:
    case_dir = FIXTURES_DIR / case_id
    if not case_dir.exists():
        print(f"ERROR: 케이스 폴더 없음: {case_dir}", file=sys.stderr)
        return 1

    try:
        expected = load_expected(case_dir)
        outputs = load_outputs(case_dir)
    except FileNotFoundError as e:
        print(f"ERROR [{case_id}]: {e}", file=sys.stderr)
        return 1

    print(f"\n=== {case_id} 검증 시작 ===")
    all_issues = []
    for name, check_fn, target in CHECKS:
        if target == "report":
            issues = check_fn(expected, outputs["report_md"])
        else:
            issues = check_fn(expected, outputs)
        status = "✅" if not issues else "❌"
        print(f"  {status} {name}: {len(issues)}건")
        for issue in issues:
            print(f"      - {issue}")
        all_issues.extend(issues)

    print(f"\n결과: {'PASS' if not all_issues else 'FAIL'} ({len(all_issues)}건)")
    return 0 if not all_issues else 1


def main():
    parser = argparse.ArgumentParser(description="career-jd-matcher 회귀 검증")
    parser.add_argument("--case", help="특정 케이스 ID (예: case-01-clear-fit)")
    parser.add_argument("--all", action="store_true", help="fixtures 전체 검증")
    args = parser.parse_args()

    if not args.case and not args.all:
        parser.print_help()
        sys.exit(2)

    if args.all:
        cases = sorted(p.name for p in FIXTURES_DIR.iterdir()
                       if p.is_dir() and p.name.startswith("case-"))
        if not cases:
            print("ERROR: fixtures/case-*/ 없음. README.md 참조하여 케이스 추가.",
                  file=sys.stderr)
            sys.exit(1)
        exit_codes = [run_case(c) for c in cases]
        sys.exit(max(exit_codes))
    else:
        sys.exit(run_case(args.case))


if __name__ == "__main__":
    main()
