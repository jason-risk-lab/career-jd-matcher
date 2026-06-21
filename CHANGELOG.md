# 변경 이력 (Changelog)

career-jd-matcher 스킬의 버전별 변경 기록. `SKILL.md` 본문은 "지금 무엇을 어떻게 실행하라"만 담고, 변경 내역은 이 파일에서 단일하게 관리한다.

## v1.8 (2026-06)

산출물 품질 개선 — 지원자가 받는 분석·자소서·보고서의 신뢰성·통과율을 직접 끌어올림.

- **회사 분석 grounding 게이트** — Section 1의 모든 정량 주장을 ✅확인/⚠️추정/⛔미확인 3등급으로 표기하고, 미확인 수치는 만들지 않으며 자소서로 넘기지 않는다. 1.9 직전 self-check 3줄 추가. 이력서의 Fact-Checker에 대응하는 "회사 분석의 Fact-Checker". (`references/company-analysis.md`)
- **자소서 첫 문장 기준(원칙 5)** — 각 문항 첫 문장을 정량 사실·회사 구체 맥락·직무 정체성 중 하나로 시작하도록 강제. 명언·일반론·회사 칭송 금지(AI 표지 E·F와 직결). 회사 인용은 ✅확인 사실·방향성 사실로만 한정해 면접 반박 리스크 제거. (`references/cover-letter-refinement.md`)
- **리라이팅 우선순위 규칙** — 페르소나 점수(완성도↑)와 BLACK AI 작문 표지가 충돌할 때 사람 목소리 우선, 바닐라 수렴 시 부분 롤백, `ai_detection.py`로 합산 감점 ≤ 2 유지. (`references/persona-evaluation.md`)
- **분석 보고서 경로·섹션 정합** — `build_docx.py`를 정식 경로로, docx-js를 claude.ai 웹 fallback으로 명확화. 면접 질문을 별도 Section 7이 아닌 6.5로 통일(SKILL.md·decision-matrix.md와 일치). 하드코딩된 버전 표기 제거. (`references/analysis-report.md`)
- **build_docx 바이트 결정성** — docx zip 엔트리 타임스탬프·core.xml 생성/수정 시각을 고정해 **같은 마크다운 → 바이트 동일 docx** 보장(기존 "결정적" 주장을 실측 성립). (`scripts/build_docx.py`)

## v1.7 (2026-06)

Tier 2 — 비용·재현성·사용성 개선 (신규 기능).

- **결정적 AI 작문 디텍션** — `scripts/ai_detection.py` 신규. `korean-ai-detection.md`의 6개 카테고리(A~F)를 결정적으로 카운트해 BLACK 항목 (11) 제안 점수·PASS/FAIL(합산 감점 ≤ 2)을 산출. 같은 입력 → 항상 같은 결과. BLACK 페르소나의 "눈으로 세기" 비결정성 제거. exit code(0/1)로 회귀 연동.
- **실행 모드 (quick/full)** — 비용 큰 스킬에 `quick`(검색 6·평가 1회차+리라이팅 1·cross-talk off)과 `full`(기본, 현행) 모드 도입. 단 거짓 사실 금지·Fact-Checker·Bull/Bear는 모드 무관하게 항상 수행.
- **회사 분석 캐시** — `cache/company_<slug>.md`에 Section 1을 30일 TTL로 저장. 같은 회사 재지원 시 검색 0회 재사용 옵션. 회사 정보만 저장(사용자 자료 분리).
- **`.gitignore` 추가** — user-profile.md·fixtures 케이스·output·cache·docx·bak을 저장소에서 제외(개인정보 보호).

## v1.6.1 (2026-06)

정합성 버그 5건 수정 — 동작 정정, 신규 기능 없음.

- **fact-checker 비작동 "권장 경로" 제거** — 존재하지 않는 `context: fork` frontmatter와 부재 파일 `references/fact-checker.skill`을 권장 경로로 안내하던 부분을 제거. 실동작하는 **격리 Task dispatch(원본·수정안 인라인 전달)** 를 기본 경로로 단일화. (`references/fact-checker.md`, `references/parallel-persona-design.md`, `references/persona-evaluation.md`)
- **회귀 하네스 상시 오탐 제거** — `run_eval.py`의 `check_persona_evaluation`이 "Hard Fail" 컬럼 헤더 때문에 Pass 케이스를 상시 FAIL 처리하던 문제, `check_must_not`이 보고서 본문에 인용된 AI 패턴명을 카운트해 상시 오탐하던 문제를 각각 5.3의 명시 판정/집계 라인 파싱으로 교체.
- **결정성 주장 한정** — SKILL.md 핵심원칙 6을 "분석 본문은 비결정적, md→docx 렌더링만 결정적(재현성)"으로 정정해 과장 제거.
- **JD 매칭 키워드 가중항 정의** — 종합식의 `키워드 0.1` 항이 미정의였던 문제 해결. Soft signals를 0~3으로 채점하는 기준표를 `jd-matching-rubric.md`에 추가.
- **페르소나 수 표기 통일** — "9 페르소나 = Fact-Checker 1 + Stage1 5 + Stage2 3, 병렬 dispatch는 8명" 규약을 명문화해 8/9 드리프트 제거.

## v1.6 (2026-05)

문서 구조 리팩터링 — 동작 변경 없음, 유지보수성·컨텍스트 효율 개선.

- **SKILL.md 슬림화** — 본문에 누적되던 버전 변경 요약 섹션(`v1.5 변경 요약` 표, `v1.3/v1.2/v1.1 변경(유지)`)을 제거하고 이 `CHANGELOG.md`로 분리. 매 호출 시 로딩되는 컨텍스트를 줄임 (점진적 정보 공개 원칙).
- **단일 출처(Single Source of Truth) 정리** — `핵심 원칙`의 `v1.5 추가` 인라인 중복 설명을 제거하고 references 파일을 가리키는 포인터만 유지. SKILL.md ↔ references 불일치 위험 제거.
- **오케스트레이터 페르소나 명시** — 스킬을 실행하는 Claude 본인의 정체성·톤을 `## 페르소나` 블록으로 신규 정의 (기존엔 평가용 9 페르소나만 정의되어 있었음).
- **Boundaries 단일 블록화** — 흩어져 있던 금지 사항(거짓 사실 금지, 트리거 제외, 장황한 설명 회피)을 `## 이 스킬이 하지 않는 것` 한 블록으로 통합.
- **출력물의 버전 하드코딩 제거** — 보고서 템플릿 제목/섹션 라벨에 박혀 있던 `(v1.5)` 표기를 제거해 버전 갱신 시 출력 템플릿을 따라 고칠 필요를 없앰.

## v1.5 (2026-05)

- **격리 sub-agent 병렬 페르소나 dispatch** — Stage 1·2 페르소나 8명을 동시 실행해 시간 단축 + 컨텍스트 격리. (`references/parallel-persona-design.md`)
- **등급별(tiered) Fact-Checker** — Hard / Soft / Ambiguous 3등급 판정. Hard FAIL 시 사이클 즉시 중단. (`references/fact-checker.md`)
- **한국어 AI 작문 디텍션** — BLACK 페르소나에 11번째 평가 항목 추가. (`references/korean-ai-detection.md`)
- **회사 분석 Bull vs Bear 토론** — Section 1.8.5 신규. 본문 작성 후 단일 관점 편향 보정. (`references/company-analysis.md`)
- **Cross-talk 라운드** — 1라운드 후 핵심 비판자 코멘트 공유 후 재채점 (선택적).
- **결정적 docx 생성** — `scripts/build_docx.py manifest.json` 호출로 docx 3개를 결정적으로 생성.
- **회귀 검증 하네스 골격** — `evaluations/` 폴더 신규.

## v1.3 (2026-05)

- 프론트매터에 `when_to_use`·`allowed-tools` 명시
- references 전체에 TOC
- `user-profile.md` 외부화 (사용자별 컨텍스트 분리)
- 회사 분석 검색을 `3 재무 + 3 시장·뉴스 + 2 평판 + 2 경쟁사·JD 부서` 타입 쿼터 강제

## v1.2 (2026-05)

- **분석 보고서 docx 신규** — 최종 산출물이 2개 → 3개로 확장.
- `references/analysis-report.md` 추가.

## v1.1 (2026-05)

- **Step 4-0 정체성 확인 게이트** — 자소서 톤 결정 전 직무 정체성을 1회 명시적으로 확인.
- **Stage 0 FACT-CHECKER 페르소나** — 페르소나 8 → 9명.
- **Section 6 의사결정 매트릭스** — 지원 권장도를 4축 100점 가중평균으로 산출.

## v1.0

- 초기 릴리스 — 5단계 워크플로우, 8 페르소나 평가, docx 산출물 2개.
