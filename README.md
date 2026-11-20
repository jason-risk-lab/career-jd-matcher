# career-jd-matcher

A Claude skill for mid-career job applications. Given a job posting and your resume, it summarizes the company and role on one screen (including Blind/JobPlanet score comparison and a requirements match table). If you want, it then rewrites only the first page of your resume and your cover letter for the posting and has them reviewed from five hiring perspectives. You make the final edits.

경력직 이직 지원을 돕는 Claude 스킬입니다. 채용공고와 경력기술서를 받아 **회사·직무를 화면 한 장으로 요약**하고, 원하면 **경력기술서 1장과 자기소개서만** 공고에 맞춰 고친 뒤 평가합니다. 최종 수정은 본인이 합니다.

> **현재 버전: v3.0** — 목적 중심 재설계. 지원/보류 판정과 합격 가능성 예측을 없애고 판단 재료만 줍니다. 고치는 범위를 1장과 자기소개서로 좁히고, 그 둘은 다섯 관점(5-Color)으로 제대로 평가합니다. 전체 변경 이력은 [`CHANGELOG.md`](CHANGELOG.md) 참조. 이전 버전은 [`archive/v2.0` 브랜치](https://github.com/jason-risk-lab/career-jd-matcher/tree/archive/v2.0), [`v1.8` 태그](https://github.com/jason-risk-lab/career-jd-matcher/tree/v1.8)에 있습니다.

## 왜 이렇게 만들었나

- **이직할 만한 회사인지는 주관이 큰 판단**이라 스킬이 결론을 내리지 않습니다. 좋은 점, 걸리는 점, 확인할 것만 정리합니다.
- **매칭이 서류 결과를 예측하지 못합니다.** 다 맞아도 떨어지고, 덜 맞아도 붙습니다. 그래서 매칭표는 참고용으로만 보여 줍니다.
- **읽는 사람은 1장과 자기소개서를 몇 초 훑고** 나머지를 봅니다. 그래서 힘을 그 둘에만 씁니다.
- **2장 이후 경력 상세는 본인의 실제 경력을 본인의 말로 쓴 부분**이라 건드리지 않습니다.

## 무엇을 하는가

**1단계. 회사·직무 한 장 요약 (화면)**
- 회사 5줄 요약: 사업, 규모·재무, 최근 이슈, 채용 배경, 들어갈 조직
- 블라인드·잡플래닛 점수를 지원 회사와 기준 회사(예: 예전 직장)로 나란히 비교
- 이직 판단 재료: 좋은 점 / 걸리는 점 / 확인할 것
- 경험과의 관계: 겹치는 업무 / 넓힐 수 있는 업무
- 매칭표: 필수·주요 업무별 충족 / 부분 / 갭 (영어는 필수면 "갭(필수)", 우대면 "우대 갭"으로 표시만)
- 끝에 "서류까지 볼까요?"를 묻고 멈춥니다.

**2단계. 경력기술서 1장과 자기소개서 수정** — 고친 글 전체를 만듭니다. 원본 1장의 틀과 분량을 지키고, 전 직장 사건은 알아볼 수 없게 유형으로만 씁니다.

**3단계. 평가 (최대 2회)** — 하위 에이전트 한 명이 다섯 관점으로 봅니다: 채용 담당자(BLACK), 함께 일할 팀장(SILVER), 그 위 임원(GOLD), 문장 에디터(BLUE), 사실 대조자(RED). 평균 90 이상, 85 미만 없음, 사실 지적 0건이면 통과. 미달이면 처음 보는 검토자로 한 번 더 보고 끝냅니다.

## 산출물

| 무엇 | 내용 |
|------|------|
| 화면 | 회사·직무 한 장 요약 |
| `수정안_[회사]_[직무].docx` | 1장 수정본, 자기소개서 수정본(글 전체, 바꾼 이유 3줄씩), 평가 점수, 2장 이후 참고 목록 |
| `확인된_사실.md` | 스킬이 물어본 사실을 모은 파일. 다음 공고에서 같이 주면 같은 질문을 다시 받지 않습니다 |

원본 파일은 고치지 않습니다. "원본 파일에 직접 반영해 줘"라고 할 때만 원본의 1장과 자기소개서 쪽을 고칩니다.

## 핵심 원칙: 사실 규칙

- 사실의 출처는 셋뿐입니다: 원본 문서, 대화에서 본인이 직접 말한 것, `확인된_사실.md`.
- 숫자 부풀리기, 역할 격상(지원 → 주도), 팀 성과를 개인 성과로, 예정을 완료로, 범위 수식어 이동, 따로 적힌 도구와 성과 잇기 등을 금지합니다.
- 회사 정보도 같습니다. 못 찾은 것은 "확인 안 됨"으로 쓰고, 리뷰 점수는 추측하지 않습니다.

## 내 기준 설정

`SKILL.md` 위쪽의 **"내 기준"** 블록에 직무 정체성, 가려는 방향, 강하게 보는 위험, 익숙한 산업, 리뷰 점수 기준 회사, 보지 않는 것을 적으세요. 개인 정보이니 공개 저장소에 올릴 때는 예시로 되돌리세요.

## 준비할 파일

| 필수 | 있으면 |
|------|--------|
| 채용공고문(파일, 캡처, URL) | `확인된_사실.md` |
| 경력기술서 원본(PPT·Word, 마지막 장이 자기소개서여도 됨) | 영문 이력서(공고가 영문 제출을 요구할 때) |

## 설치 방법

### Claude.ai 사용자

1. 이 저장소에서 `career-jd-matcher.skill` 파일을 다운로드합니다.
2. Claude.ai 설정 → Capabilities → Skills로 이동합니다.
3. "Upload skill"을 선택하고 `.skill` 파일을 업로드합니다.

(스킬 업로드 UI는 시기에 따라 위치·이름이 다를 수 있습니다. 보이지 않으면 https://support.claude.com 에서 "skill" 검색.)

### Claude Code 사용자

```bash
git clone https://github.com/jason-risk-lab/career-jd-matcher.git ~/.claude/skills/career-jd-matcher
```

## 사용법

```
이 공고 봐줘.

채용공고: [URL 또는 첨부]
경력기술서: [첨부]
```

면접 준비, 모의면접, 연봉 협상, 공고 없는 일반 이직 상담에는 쓰지 않습니다.

## 폴더 구조

```
career-jd-matcher/
├── SKILL.md                 # 전체 워크플로우
├── CHANGELOG.md             # 버전별 변경 이력
└── career-jd-matcher.skill  # Claude.ai 업로드용 패키지
```

## 관련 스킬

- **`interview-qa-prep`** — 면접 전날 읽는 회사 브리프.
- **`mock-interview`** — 모의면접 시뮬레이션.

## 라이선스

본 스킬은 개인 사용 및 공유를 목적으로 작성되었습니다. 필요에 따라 라이선스를 자유롭게 추가하세요 (MIT, Apache 2.0 등).

## 만든 이

**[jason-risk-lab](https://github.com/jason-risk-lab)** — 내부감사·윤리경영 도메인 기반 Risk Solution Partner
