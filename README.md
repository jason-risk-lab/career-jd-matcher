# career-jd-matcher

A Claude skill that handles the full mid-career job application package in one shot — company analysis (with Bull/Bear debate), JD-resume matching, resume refinement, cover letter refinement, and multi-persona evaluation with isolated sub-agent parallel dispatch and tiered fact-checking.

경력직 이직 지원 패키지 전 과정(회사 분석 → JD 매칭 평가 → 경력기술서 정교화 → 직무 정체성 확인 → 자기소개서 정교화 → 9 페르소나 병렬 평가/리라이팅)을 한 번의 호출로 처리하는 Claude 스킬입니다.

> **현재 버전: v1.5** — 격리 sub-agent 병렬 페르소나 dispatch, 등급별(tiered) Fact-Checker, 한국어 AI 작문 디텍션, 회사 분석 Bull vs Bear 토론, cross-talk 라운드, 결정적 docx 생성 스크립트, 회귀 검증 하네스가 새로 들어갔습니다. 변경 이력은 아래 [버전 이력](#버전-이력) 참조.

## 무엇을 하는 스킬인가

채용공고와 본인의 경력기술서·자기소개서를 입력하면 다음을 자동으로 수행합니다.

1. **회사 분석 (BCG 컨설턴트 관점 + Bull/Bear)** — 매출/영업이익률/현금흐름 시계열, Porter's 5 Forces, BCG Matrix, 국내·글로벌 시장 전망, 학자·이론 인용 (Michael Porter, Christensen, Damodaran 등). 웹검색은 `3 재무 + 3 시장·뉴스 + 2 평판 + 2 경쟁사·JD 부서` 타입 쿼터로 10회 강제. 본문 작성 후 **Bull vs Bear 1라운드 토론**으로 단일 관점 편향 보정 (v1.5).
2. **JD 매칭 평가** — Must-have / Nice-to-have / Soft signals로 요건 분해, 0~3점 스코어링, 종합 매칭률 산출.
3. **경력기술서 정교화** — JD 키워드 미러링, 정량화, STAR 구조 압축. **거짓 사실 추가 절대 금지** 원칙 엄수.
4. **직무 정체성 확인 (Step 4-0)** — 자소서 톤의 기준이 될 본인의 직무 정체성을 1회 명시적으로 확인. 메모리·기존 자료의 자동 반영을 막아 사용자 통제권을 보장.
5. **자기소개서 정교화** — 회사 고유 정보 반영, 1,000자 이내 압축, 4-0에서 확정된 직무 정체성 일관 노출.
6. **멀티 페르소나 평가 (9명, 최대 3회차, v1.5 병렬 + cross-talk)** — 다음 9명이 각각 평가/검증합니다:
   - **Stage 0 (사실 검증)**: FACT-CHECKER — **격리 sub-agent**에서 3등급(Hard / Soft / Ambiguous) 판정 (v1.5). Hard FAIL 시 즉시 원상 복구 + 사이클 중단.
   - **Stage 1 (5-Color Harness)**: BLACK · RED · SILVER · BLUE · GOLD — 보편적 완성도 10점 만점. BLACK은 **한국어 AI 작문 표지 검출(11번째 항목)** 포함 (v1.5).
   - **Stage 2 (채용 라인업)**: 헤드헌터 · 현업 매니저 · HR — 실전 통과 가능성 10점 만점.
   - Stage 1·2 페르소나 8명을 **격리 sub-agent에 병렬 dispatch** (v1.5). 1라운드 후 **cross-talk 라운드** 선택적 적용 (핵심 비판자 코멘트 공유 후 재채점).
7. **의사결정 매트릭스 (Section 6)** — Growth 30% / Safety 30% / Meaning 25% / Fit 15% 가중평균 100점 산출. Bull/Bear 결과가 Growth·Safety 채점 근거로 인용됨.

## 산출물

채팅 마크다운 보고서 1개 + docx 파일 3개

- **채팅 내 마크다운 보고서** — 회사 분석(Bull/Bear 포함), JD 매칭 대시보드, 변경 전후 비교표, 9 페르소나 평가표(병렬 + cross-talk), 의사결정 매트릭스 모두 포함
- **`경력기술서_[회사명]_[직무명]_정교화.docx`** — 제출용
- **`자기소개서_[회사명]_[직무명]_정교화.docx`** — 제출용
- **`지원분석보고서_[회사명]_[직무명].docx`** — 면접 준비·의사결정 트래커 보관용

**docx 생성 방식 (v1.5)**: Claude가 마크다운을 작성한 뒤 `scripts/build_docx.py manifest.json`을 호출해 결정적으로 docx 3개를 만듭니다. v1.5 이전의 docx-js 즉석 생성은 fallback으로만 유지.

## 핵심 원칙

- **거짓 사실 절대 금지** — 점수를 올리기 위해서도, 매칭률을 높이기 위해서도, 없는 경험/자격증/수치를 추가하지 않습니다. 갭은 갭으로 두고 학습 의지·확장성으로 다룹니다. v1.5의 **격리 Fact-Checker sub-agent**가 Hard/Soft/Ambiguous 3등급으로 자동 검증하며, Hard FAIL 시 사이클을 즉시 중단합니다.
- **BCG 컨설턴트 톤** — 단순 회사 소개가 아니라 재무 수치·산업 구조·시장 전망에 기반한 분석. 본문 작성 후 Bull vs Bear 토론으로 단일 관점 편향을 보정.
- **사용자 페르소나 존중** — 메모리/기존 자료에 드러난 직무 정체성을 임의로 바꾸지 않습니다. **Step 4-0**에서 1회 명시적으로 확인.
- **정량 기반 의사결정** — Section 6의 지원 권장도는 인상이 아니라 4축 가중평균 100점 매트릭스로 산출. Bull/Bear 토론 결과가 채점 근거로 인용됨.
- **결정적 산출** — docx 3개는 Python 스크립트로 생성해 실행할 때마다 동일한 결과를 보장합니다.

## 설치 방법

### Claude.ai 사용자

1. 이 레포지토리에서 `career-jd-matcher.skill` 파일을 다운로드합니다.
2. Claude.ai 설정 → Capabilities → Skills로 이동합니다.
3. "Upload skill" 또는 "Add skill"을 선택하고 `.skill` 파일을 업로드합니다.

(Claude.ai의 스킬 업로드 UI는 시기에 따라 위치·이름이 다를 수 있습니다. 현재 UI에서 보이지 않으면 https://support.claude.com 에서 "skill" 검색.)

### Claude Code 사용자

레포지토리를 클론한 뒤 스킬 폴더를 `~/.claude/skills/` 아래에 둡니다.

```bash
git clone https://github.com/jason-risk-lab/career-jd-matcher.git ~/.claude/skills/career-jd-matcher
```

`scripts/build_docx.py`를 사용하려면 `python-docx` 패키지가 필요합니다.

```bash
pip install python-docx
```

## 사용법

스킬이 설치된 Claude 세션에서, 다음과 같이 요청합니다.

```
이 회사 분석하고 내 경력에 맞춰 지원서 정교화해줘.

채용공고: [URL 또는 본문]
회사명: [회사명]
경력기술서: [텍스트 또는 첨부]
자기소개서: [텍스트 또는 첨부]
```

스킬이 자동으로 5단계 + Step 4-0 정체성 확인을 순차 실행합니다. 웹검색 10회 + 페르소나 평가 사이클(병렬 dispatch)로 몇 분 소요됩니다. 중간에 직무 정체성 1줄 응답을 한 번 요청합니다.

## 트리거 조건

다음 문구가 등장하면 스킬이 자동으로 작동합니다.

- "이 회사 분석해줘"
- "이 JD에 내 경력 맞춰줘"
- "이직 지원 도와줘"
- "자소서 다듬어줘"
- "매칭도 봐줘"
- 채용공고 + 회사명 + 경력 자료가 동시에 등장하는 경우 (명시적 키워드 없이도)

다음 경우엔 작동하지 않습니다.

- 단순 회사 정보 조회
- 채용공고나 경력 자료 없이 일반론적 이직 조언
- 면접 예상 질문만 따로 요청 → **별도 `mock-interview` 스킬 사용**
- 모의면접 → **별도 `mock-interview` 스킬 사용**
- 연봉 협상 문의

## 폴더 구조

```
career-jd-matcher/
├── SKILL.md                              # 메인 워크플로우 + 트리거
├── references/
│   ├── company-analysis.md                # Step 1: 회사 리서치 (BCG/Porter + Bull/Bear)
│   ├── jd-matching-rubric.md              # Step 2: JD ↔ 경력 매칭 스코어링
│   ├── resume-refinement.md               # Step 3: 경력기술서 정교화
│   ├── cover-letter-refinement.md         # Step 4: 자소서 정교화 (1,000자)
│   ├── persona-evaluation.md              # Step 5: 9 페르소나 평가 사이클
│   ├── parallel-persona-design.md         # v1.5: 격리 sub-agent 병렬 + cross-talk
│   ├── fact-checker.md                    # v1.5: 등급별 Fact-Checker 게이트
│   ├── korean-ai-detection.md             # v1.5: 한국어 AI 작문 표지 검출
│   ├── decision-matrix.md                 # Section 6: 의사결정 매트릭스
│   ├── analysis-report.md                 # 분석 보고서 docx 생성 가이드
│   └── user-profile.example.md            # 사용자 페르소나 템플릿 (선택적)
├── scripts/
│   └── build_docx.py                      # v1.5: 결정적 docx 변환 스크립트
└── evaluations/
    ├── README.md                          # v1.5: 회귀 검증 하네스 가이드
    ├── run_eval.py                        # 회귀 테스트 러너
    └── fixtures/                          # 사용자 케이스 픽스처 (gitignored)
```

## 버전 이력

### v1.5 (현재)
- **격리 sub-agent 병렬 페르소나 dispatch** — Stage 1·2 페르소나 8명을 동시 실행해 시간 단축 + 컨텍스트 격리.
- **등급별(tiered) Fact-Checker** — Hard / Soft / Ambiguous 3등급 판정. Hard FAIL 시 사이클 즉시 중단.
- **한국어 AI 작문 디텍션** — BLACK 페르소나에 11번째 평가 항목 추가.
- **회사 분석 Bull vs Bear 토론** — Section 1.8.5 신규. 본문 작성 후 단일 관점 편향 보정.
- **Cross-talk 라운드** — 1라운드 후 핵심 비판자 코멘트 공유 후 재채점 (선택적).
- **결정적 docx 생성** — `scripts/build_docx.py manifest.json` 호출로 docx 3개를 결정적으로 생성.
- **회귀 검증 하네스 골격** — `evaluations/` 폴더 신규.

### v1.3
- 프론트매터에 `when_to_use`·`allowed-tools` 명시
- references 전체에 TOC
- `user-profile.md` 외부화 (사용자별 컨텍스트 분리)
- 회사 분석 검색을 `3 재무 + 3 시장·뉴스 + 2 평판 + 2 경쟁사·JD 부서` 타입 쿼터 강제

### v1.2
- **분석 보고서 docx 신규** — 최종 산출물이 2개 → 3개로 확장.
- `references/analysis-report.md` 추가.

### v1.1
- **Step 4-0 정체성 확인 게이트** — 자소서 톤 결정 전 직무 정체성을 1회 명시적으로 확인.
- **Stage 0 FACT-CHECKER 페르소나** — 페르소나 8 → 9명.
- **Section 6 의사결정 매트릭스** — 지원 권장도를 4축 100점 가중평균으로 산출.

### v1.0
- 초기 릴리스 — 5단계 워크플로우, 8 페르소나 평가, docx 산출물 2개.

## 관련 스킬

- **`mock-interview`** — 본 스킬의 산출물(특히 분석 보고서 docx의 면접 예상 질문)을 입력으로 모의면접 시뮬레이션 (5개 모드: 인성·PT·기술·토론·AI면접). 별도 호출 필요.

## 라이선스

본 스킬은 개인 사용 및 공유를 목적으로 작성되었습니다. 필요에 따라 라이선스를 자유롭게 추가하세요 (MIT, Apache 2.0 등).

## 만든 이

**[jason-risk-lab](https://github.com/jason-risk-lab)** — 내부감사·윤리경영 도메인 기반 Risk Solution Partner
