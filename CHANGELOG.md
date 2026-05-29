# 변경 이력 (Changelog)

career-jd-matcher 스킬의 버전별 변경 기록. `SKILL.md` 본문은 "지금 무엇을 어떻게 실행하라"만 담고, 변경 내역은 이 파일에서 단일하게 관리한다.

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
