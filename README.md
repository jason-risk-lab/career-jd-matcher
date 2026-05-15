# career-jd-matcher

A Claude skill that handles the full mid-career job application package in one shot — company analysis, JD-resume matching, resume refinement, cover letter refinement, and multi-persona evaluation with source-of-truth fact-checking.

경력직 이직 지원 패키지 전 과정(회사 분석 → JD 매칭 평가 → 경력기술서 정교화 → 직무 정체성 확인 → 자기소개서 정교화 → 멀티 페르소나 평가/리라이팅)을 한 번의 호출로 처리하는 Claude 스킬입니다.

> **현재 버전: v1.2** — v1.0 대비 정체성 확인 게이트, Fact-Checker 페르소나, 의사결정 매트릭스, 분석 보고서 docx 자동 생성이 추가되었습니다. 변경 이력은 아래 [버전 이력](#버전-이력) 참조.

## 무엇을 하는 스킬인가

채용공고와 본인의 경력기술서·자기소개서를 입력하면 다음을 자동으로 수행합니다.

1. **회사 분석 (BCG 컨설턴트 관점)** — 매출/영업이익률/현금흐름 시계열, Porter's 5 Forces, BCG Matrix, 국내·글로벌 시장 전망, 학자·이론 인용 (Michael Porter, Christensen, Damodaran 등). 웹검색 10회 기본.
2. **JD 매칭 평가** — Must-have / Nice-to-have / Soft signals로 요건 분해, 0~3점 스코어링, 종합 매칭률 산출.
3. **경력기술서 정교화** — JD 키워드 미러링, 정량화, STAR 구조 압축. **거짓 사실 추가 절대 금지** 원칙 엄수.
4. **직무 정체성 확인 (Step 4-0, v1.1+)** — 자소서 톤의 기준이 될 본인의 직무 정체성을 1회 명시적으로 확인. 메모리·기존 자료의 자동 반영을 막아 사용자 통제권을 보장.
5. **자기소개서 정교화** — 회사 고유 정보 반영, 1,000자 이내 압축, 4-0에서 확정된 직무 정체성 일관 노출.
6. **멀티 페르소나 평가 (9명, 최대 3회차)** — 다음 9명이 각각 평가/검증합니다:
   - **Stage 0 (사실 검증, v1.1+)**: FACT-CHECKER — 매 리라이팅 직후 원본 1:1 대조 (Pass/Fail 게이트). Fail 시 해당 문장 원상 복구.
   - **Stage 1 (5-Color Harness)**: BLACK · RED · SILVER · BLUE · GOLD — 보편적 완성도 10점 만점.
   - **Stage 2 (채용 라인업)**: 헤드헌터 · 현업 매니저 · HR — 실전 통과 가능성 10점 만점.
   - 9점 미만 항목은 리라이팅 후 재평가. 최대 3회 반복.
7. **의사결정 매트릭스 (Section 6, v1.1+)** — Growth 30% / Safety 30% / Meaning 25% / Fit 15% 가중평균 100점 산출. 70+ 강력 지원 / 50~69 신중 검토 / 50 미만 재고 권장.

## 산출물

채팅 마크다운 보고서 1개 + docx 파일 3개 (v1.2부터 분석 보고서 추가)

- **채팅 내 마크다운 보고서** — 회사 분석, JD 매칭 대시보드, 변경 전후 비교표, 9 페르소나 평가표, 의사결정 매트릭스 모두 포함
- **`경력기술서_[회사명]_[직무명]_정교화.docx`** — 제출용
- **`자기소개서_[회사명]_[직무명]_정교화.docx`** — 제출용
- **`지원분석보고서_[회사명]_[직무명].docx`** ← v1.2 신규 — 면접 준비·의사결정 트래커 보관용 (채팅 마크다운 Section 1~6 + 면접 예상 질문 Top 5 통합)

## 핵심 원칙

- **거짓 사실 절대 금지** — 점수를 올리기 위해서도, 매칭률을 높이기 위해서도, 없는 경험/자격증/수치를 추가하지 않습니다. 갭은 갭으로 두고 학습 의지·확장성으로 다룹니다. v1.1부터 **Stage 0 FACT-CHECKER**가 매 리라이팅 직후 원본 대조 Pass/Fail로 자동 검증.
- **BCG 컨설턴트 톤** — 단순 회사 소개가 아니라 재무 수치·산업 구조·시장 전망에 기반한 분석.
- **사용자 페르소나 존중** — 메모리/기존 자료에 드러난 직무 정체성을 임의로 바꾸지 않습니다. v1.1부터 **Step 4-0**에서 1회 명시적으로 확인.
- **정량 기반 의사결정** — Section 6의 지원 권장도는 인상이 아니라 4축 가중평균 100점 매트릭스로 산출.

## 설치 방법

### Claude.ai 사용자

1. 이 레포지토리에서 `career-jd-matcher.skill` 파일을 다운로드합니다.
2. Claude.ai 설정 → Capabilities → Skills로 이동합니다.
3. "Upload skill" 또는 "Add skill"을 선택하고 `.skill` 파일을 업로드합니다.

(Claude.ai의 스킬 업로드 UI는 시기에 따라 위치·이름이 다를 수 있습니다. 현재 UI에서 보이지 않으면 https://support.claude.com 에서 "skill" 검색.)

### 개발자 / Claude Code 사용자

레포지토리를 클론한 뒤 스킬 폴더를 적절한 위치에 두면 됩니다.

```bash
git clone https://github.com/jason-risk-lab/career-jd-matcher.git
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

스킬이 자동으로 5단계 + Step 4-0 정체성 확인을 순차 실행합니다. 웹검색 10회 + 페르소나 평가 사이클로 몇 분 소요됩니다. 중간에 직무 정체성 1줄 응답을 한 번 요청합니다.

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
- 면접 예상 질문만 따로 요청
- 연봉 협상 문의

## 폴더 구조

```
career-jd-matcher/
├── SKILL.md                           # 메인 워크플로우 + 트리거
└── references/
    ├── company-analysis.md             # Step 1: 회사 리서치 (BCG/Porter)
    ├── jd-matching-rubric.md           # Step 2: JD ↔ 경력 매칭 스코어링
    ├── resume-refinement.md            # Step 3: 경력기술서 정교화
    ├── cover-letter-refinement.md      # Step 4: 자소서 정교화 (1,000자)
    ├── persona-evaluation.md           # Step 5: 9 페르소나 평가 사이클 (Stage 0 + 1 + 2)
    ├── decision-matrix.md              # Section 6: 의사결정 매트릭스 (v1.1+)
    └── analysis-report.md              # 분석 보고서 docx 생성 가이드 (v1.2+)
```

## 버전 이력

### v1.2 (현재)
- **분석 보고서 docx 신규** — 채팅 마크다운 Section 1~6 + 면접 예상 질문 Top 5를 통합한 별도 docx 파일을 항상 생성. 최종 산출물이 2개 → **3개**로 확장.
- `references/analysis-report.md` 추가.

### v1.1
- **Step 4-0 정체성 확인 게이트** — 자소서 톤 결정 전 직무 정체성을 1회 명시적으로 확인.
- **Stage 0 FACT-CHECKER 페르소나** — 리라이팅 사이클 종료 시 원본 대조 Pass/Fail 게이트. 페르소나 8 → **9명**.
- **Section 6 의사결정 매트릭스** — 지원 권장도를 Growth/Safety/Meaning/Fit 4축 100점 가중평균으로 산출.
- `references/decision-matrix.md` 추가.

### v1.0
- 초기 릴리스 — 5단계 워크플로우, 8 페르소나 평가, docx 산출물 2개.

## 라이선스

본 스킬은 개인 사용 및 공유를 목적으로 작성되었습니다. 필요에 따라 라이선스를 자유롭게 추가하세요 (MIT, Apache 2.0 등).

## 만든 이

이한성 (Hanseong Lee) — 내부감사/윤리경영 전문가, Risk Solution Partner
