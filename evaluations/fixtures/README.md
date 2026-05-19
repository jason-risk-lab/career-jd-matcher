# Evaluation Fixtures

본인의 케이스로 채워야 작동한다. v1.5 패치에는 슬롯만 제공.

## 권장 케이스 3개

| ID | 시나리오 |
|----|---------|
| `case-01-clear-fit` | JD ↔ 이력서 매칭률 80%+, 명확한 강점 |
| `case-02-gap-heavy` | Must-have 중 2~3개 갭 존재 |
| `case-03-edge-truncated-jd` | JD 본문 짧고 회사 정보 부족 |

## 각 케이스 폴더 구조

```
fixtures/case-01-clear-fit/
├── jd.md                     # 채용공고 본문 (또는 URL을 첫 줄에 메모)
├── resume.md                 # 본인 이력서 원본 (마크다운)
├── cover_letter.md           # 본인 자소서 초안 (없으면 빈 파일)
├── user_profile.md           # 사용자 컨텍스트 (예시: ../../references/user-profile.example.md 참조)
├── expected.yaml             # 기대 거동 명세 (아래 스키마)
└── outputs/                  # 스킬 실행 후 산출물 수동 저장 위치
    ├── report.md             # 채팅 마크다운 보고서 (사용자가 채팅에서 복사)
    ├── 경력기술서_*.docx
    ├── 자기소개서_*.docx
    └── 지원분석보고서_*.docx
```

## expected.yaml 스키마

`../../README.md`의 "expected.yaml 스키마" 섹션 참조. 핵심 필드:

```yaml
case_id: case-01-clear-fit

company_analysis:
  search_calls_typed: { financials: 3, market_news: 3, reputation: 2, competitor_jd_dept: 2 }
  frameworks_applied: ["Porter 5 Forces", "BCG Matrix"]
  scholar_citations_min: 1

jd_matching:
  must_have_count_min: 5
  match_rate_range: [75, 90]

persona_evaluation:
  iterations_max: 3
  stage_0_fact_checker: { hard_claims_pass: true, fabrication_count: 0 }
  final_average_min: 8.5

decision_matrix:
  total_score_range: [65, 85]
  recommendation: "🟢 강력 지원"

outputs:
  docx_files_count: 3
  filenames:
    - "경력기술서_*_정교화.docx"
    - "자기소개서_*_정교화.docx"
    - "지원분석보고서_*.docx"
  markdown_sections_present: ["1.", "2.", "3.", "4.", "5.", "6."]

must_not:
  - "거짓 정량 수치 추가"
  - "원본에 없는 자격증 추가"
  - "한국어 AI 작문 표지 5건 초과"
```

## 셋업 절차

1. **최초 1회**: 기존에 만족스럽게 작동했던 케이스 1개로 case-01 폴더 채우기
2. JD·이력서·자소서 마크다운 파일 저장
3. 그때의 산출물(docx + 채팅 보고서)을 `outputs/`에 저장
4. 채팅 보고서에서 실제 산출 수치를 `expected.yaml`에 박아 기준선 확정
5. 스킬 수정 후 같은 입력으로 다시 실행 → `outputs/`에 덮어쓰기 → `python ../../run_eval.py --case case-01-clear-fit`

## 보안 주의

- `resume.md`·`cover_letter.md`·`user_profile.md`에는 개인정보가 들어간다. **fixtures/ 폴더 전체를 .gitignore에 등록 권장**.
- 또는 익명화된 더미 케이스를 별도로 만들어 공유용 fixtures 운영.

```gitignore
# 개인정보 포함 가능
evaluations/fixtures/case-*/
```

## 빈 시작 (예시)

```bash
mkdir -p fixtures/case-01-clear-fit/outputs
touch fixtures/case-01-clear-fit/{jd,resume,cover_letter,user_profile}.md
cp fixtures/_template_expected.yaml fixtures/case-01-clear-fit/expected.yaml  # 또는 위 스키마 복붙
```
