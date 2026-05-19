# Evaluation Harness — v1.5 신규

career-jd-matcher 스킬의 회귀(regression) 검출용 테스트 세트. 스킬을 수정한 뒤 "이전과 같이 작동하는가"를 자동 검증.

## 왜 필요한가

Phase 2·3 작업은 워크플로우 깊이를 건드린다. 한 항목을 고치면 다른 항목이 망가질 수 있다.

손으로 테스트하려면:
1. 매번 JD·이력서 한 쌍 준비
2. 스킬 호출
3. 산출물 점검 (3개 docx + 마크다운 보고서)
4. 이전 산출물과 수동 비교

수정 한 번에 30~60분. **수정 10번이면 5~10시간이 회귀 검증에만 사용된다.**

Evaluation Harness는 이걸 자동화한다.

## 구조

```
evaluations/
├── README.md                       (이 파일)
├── run_eval.py                     (러너 스크립트, 사용자 환경에서 실행)
└── fixtures/
    ├── README.md                   (픽스처 가이드)
    ├── case-01-clear-fit/
    │   ├── jd.md                   (채용공고 본문)
    │   ├── resume.md               (이력서 원본)
    │   ├── cover_letter.md         (자소서 초안)
    │   ├── user_profile.md         (사용자 컨텍스트)
    │   └── expected.yaml           (기대 거동 명세)
    ├── case-02-gap-heavy/
    │   └── ... (필수 갭이 많은 케이스)
    └── case-03-edge-truncated-jd/
        └── ... (정보 부족 JD 케이스)
```

## 픽스처 필수 케이스 3가지

| ID | 시나리오 | 검증 포인트 |
|----|---------|------------|
| **case-01-clear-fit** | JD ↔ 이력서 매칭률 80%+, 명확한 강점 | Decision Matrix 70+ 산출, Stage 0 Pass, 리라이팅 1회 내 종료 |
| **case-02-gap-heavy** | Must-have 중 2~3개 갭 존재 | 갭이 0점으로 정확히 표시되는가, 자소서에서 학습 의지로 다루는가, 거짓 추가 없는가 |
| **case-03-edge-truncated-jd** | JD 본문 3문장만, 회사 정보 적음 | "공개 정보 제한적" 명시되는가, 추정 표시(*)되는가, 매칭률을 추측하지 않는가 |

추가 권장 케이스 (Phase 3-10에서 사용자가 채워 넣을 슬롯):
- case-04: 정량 수치 부풀리기 시도 (Fact-Checker 검증)
- case-05: 한국어 AI 작문 표지 다수 (BLACK 페르소나 검증)
- case-06: 짧은 재직기간 처리 (sensitive_topics 검증)

## expected.yaml 스키마

각 픽스처의 기대 거동을 선언적으로 정의:

```yaml
case_id: case-01-clear-fit

# 1. Step 1 회사 분석
company_analysis:
  search_calls_typed:
    financials: 3
    market_news: 3
    reputation: 2
    competitor_jd_dept: 2
  frameworks_applied: ["Porter 5 Forces", "BCG Matrix"]
  scholar_citations_min: 1

# 2. Step 2 JD 매칭
jd_matching:
  must_have_count_min: 5
  match_rate_range: [75, 90]
  strengths_count: 3
  gaps_count: 3

# 3. Step 5 페르소나 평가
persona_evaluation:
  iterations_max: 3
  stage_0_fact_checker:
    hard_claims_pass: true
    fabrication_count: 0
  final_average_min: 8.5

# 4. Step 6 의사결정 매트릭스
decision_matrix:
  total_score_range: [65, 85]
  recommendation: "🟢 강력 지원"
  axis_scores:
    growth: [6.0, 9.0]
    safety: [5.0, 8.0]
    meaning: [7.0, 10.0]
    fit: [7.0, 9.5]

# 5. 산출물
outputs:
  docx_files_count: 3
  filenames:
    - "경력기술서_*_정교화.docx"
    - "자기소개서_*_정교화.docx"
    - "지원분석보고서_*.docx"
  markdown_sections_present: ["1.", "2.", "3.", "4.", "5.", "6."]

# 6. 금지 거동
must_not:
  - "거짓 정량 수치 추가"
  - "원본에 없는 자격증 추가"
  - "팀 성과를 단독 성과로 표시"
  - "한국어 AI 작문 표지 5건 초과"
```

## 실행 방법

```bash
cd evaluations/
python run_eval.py --case case-01-clear-fit
# 또는 전체 케이스
python run_eval.py --all
```

`run_eval.py`는 다음을 수행:
1. 픽스처를 읽어 스킬 호출 (실제 Claude 세션 또는 mock)
2. 산출물 회수
3. `expected.yaml` 기준 검증
4. Pass/Fail 표 출력 + diff 보고서

## 사용자 셋업 가이드

본 v1.5 패치는 **fixtures/는 비어있다.** 사용자가 본인 케이스 1~3개를 직접 채워야 한다.

권장 셋업 절차:
1. 기존에 career-jd-matcher를 실행해 본 케이스 중 가장 만족스러웠던 것을 case-01로 복사
2. 갭이 많아 어려웠던 케이스를 case-02
3. 정보가 부족했던 케이스를 case-03
4. expected.yaml에 그때의 실제 산출물 값을 기준선으로 박는다

이후 스킬을 수정할 때마다:
```bash
python run_eval.py --all
```
실행해서 회귀가 없는지 확인.

## 참고

기존 OSS 평가 하네스 사례:
- [openevals](https://github.com/langchain-ai/openevals) — LLM 평가 표준화
- [promptfoo](https://github.com/promptfoo/promptfoo) — 프롬프트 회귀 테스트
- [LangSmith eval datasets](https://docs.langchain.com/langsmith/evaluation)

본 harness는 단순 dict 비교 + regex 매칭 수준. 더 깊은 평가는 위 OSS 도구로 연계 가능.
