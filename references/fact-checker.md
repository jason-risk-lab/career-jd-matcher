# Fact-Checker 격리 sub-skill (Phase 2-2/2-3) — v1.5 신규

Stage 0 FACT-CHECKER를 `context: fork` 패턴으로 **격리된 sub-agent**에서 실행한다. 동시에 기존 8개 이진 체크리스트를 **등급별(tiered) 게이트**로 재설계.

## 목차

- [1. 왜 격리하는가](#왜-격리하는가)
- [2. 격리 sub-agent 호출 패턴](#격리-sub-agent-호출-패턴)
- [3. 등급별(tiered) 게이트 설계](#등급별tiered-게이트-설계)
- [4. 입출력 스펙](#입출력-스펙)
- [5. 통합 시 메인 스킬 변경점](#통합-시-메인-스킬-변경점)

## 왜 격리하는가

기존 v1.4 이전의 Fact-Checker는 같은 컨텍스트에서 Stage 1·2 페르소나의 평가 직후에 실행되었다. 문제:

1. **편향 누출**: "Stage 1 RED 페르소나가 정량 부족이라 했으니 좀 더 임팩트 있게 표현했다" 같은 흐름이 Fact-Checker에게 의식되어, 미세한 변조를 "허용 가능한 정교화"로 합리화할 위험.
2. **컨텍스트 비대**: 9 페르소나의 평가 코멘트가 누적되어 Fact-Checker가 원본 대조에 집중하기 어려움.
3. **누적 변형**: 3회차로 갈수록 미세한 추정이 누적되어 원본과 미세하게 어긋난 문장이 만들어지는데, 같은 컨텍스트에서는 첫 회차의 "OK"를 다시 본 결과로 착시.

격리 sub-agent는 이 3가지를 구조적으로 차단한다.

## 격리 sub-agent 호출 패턴

### 패턴 1: Claude Code `context: fork` (권장)

`references/fact-checker.skill` 또는 별도 frontmatter 블록을 둬서 sub-skill로 등록:

```yaml
---
name: career-jd-matcher-fact-checker
description: career-jd-matcher 스킬의 Stage 0 Fact-Checker 격리 실행. 원본 이력서/자소서와 수정안만 입력 받아 등급별 검증을 수행. 직접 호출되지 않고 메인 스킬이 dispatch.
disable-model-invocation: true
context: fork
agent: Explore
allowed-tools: Read
---
```

메인 스킬에서 호출:
```
Task(
  subagent_type="career-jd-matcher-fact-checker",
  prompt="원본:\n[원본 텍스트]\n\n수정안:\n[수정안 텍스트]\n\n규칙: references/fact-checker.md"
)
```

### 패턴 2: 일반 Task (대안)

`context: fork` 미지원 환경에서는 `Task` 디스패치만으로도 컨텍스트 격리 가능:

```
Task(
  subagent_type="general-purpose",
  prompt="당신은 Fact-Checker입니다. 원본과 수정안만 보고 등급별 판정만 출력. 다른 페르소나의 평가를 의식하지 않습니다.\n\n[원본 + 수정안 + 룰]"
)
```

격리 sub-agent는 **원본 이력서·자소서·user-profile.md의 key_metrics 외에는 어떤 컨텍스트도 받지 않는다.** 평가자 코멘트·점수·리라이팅 의도 전부 차단.

## 등급별(tiered) 게이트 설계

기존 8개 이진 체크리스트를 3등급으로 재분류:

### 🔴 하드 클레임 (Hard Claims) — 출처 라인 인용 필수

원본 경력기술서/자소서에 **정확히 일치하는 문장 또는 단어**가 있어야 통과. 없으면 즉시 Fail.

| 카테고리 | 예시 | 판정 |
|---------|------|------|
| 정량 수치 | "감사 80건", "96% 해결률", "5년 경력" | 원본에서 동일 수치 발견 → Pass |
| 회사명·기간·직책 | "SPC 정도경영실 2018.04~2023.10", "내부감사 책임자" | 원본 일치 → Pass |
| 자격증·교육 이수 | "CISA", "CIA", "Wharton 수료" | 원본 일치 → Pass (단, "진행 중" → "취득"은 Fail) |
| 프로젝트명·도구명 | "K-Whistle 핫라인", "Python 100시나리오 시스템" | 원본 일치 → Pass |
| 인용 인물·기관 | "○○ 대표 직접 칭찬", "△△ 기관 표창" | 원본 일치 → Pass / 없으면 Fail |

**판정 룰**: 1건 Fail = 해당 문장 즉시 원상 복구 + 사이클 중단.

### 🟡 소프트 클레임 (Soft Claims) — 의미 일치만 검증

원본의 **의미**가 보존되면 통과. 표현·강조·순서 조정 허용.

| 카테고리 | 허용 변환 예시 | 금지 변환 예시 |
|---------|--------------|--------------|
| 키워드 미러링 | "감사 활동" → "리스크 기반 감사" (JD 키워드, 의미 동일) | "감사 보조" → "감사 주도" (역할 격상) |
| 정량 표현 | "80건" → "80건+", "다수" → "20건+" (원본에 근거 있으면) | "80건" → "100건" (없는 수치) |
| STAR 재구조화 | 평문 → 상황/과제/행동/결과 4요소 분해 | 단독으로 한 일과 팀이 한 일 혼합 |
| 순서 재배치 | 시간 순 → JD 우선순위 순 | 사실 자체 변경 없음 |

**판정 룰**: 의미 변형 의심 시 Hard Claim로 강등 처리. 통상 통과.

### ⚪ 모호 클레임 (Ambiguous) — 사용자 확인 요청

판정이 갈리는 경우 자동 통과/실패시키지 않고 사용자에게 한 줄 질의.

**예시**:
- "감사 80건+" → 원본 "80건"에서 "+"가 의미하는 모호함. "80건 이상으로 표기하시겠습니까?"
- "헬스케어 도메인 학습 중" → 원본에 없는 새 도메인 시사. "이 표현을 쓸 의도가 맞는지 확인 부탁드립니다."
- "데이터 기반 의사결정 문화 정착 기여" → 원본에 "정착"이 없는 경우. 약한 표현으로 강등 또는 사용자 확인.

**판정 룰**: 사용자 응답에 따라 Hard/Soft 재분류 후 적용. 무응답 시 보수적으로 Hard로 분류.

## 입출력 스펙

### Sub-agent 입력

```json
{
  "original_resume": "[사용자 원본 이력서 전문]",
  "original_cover_letter": "[사용자 원본 자소서 전문]",
  "user_profile_metrics": "[user-profile.md의 key_metrics 섹션]",
  "refined_resume": "[수정안 이력서 전문]",
  "refined_cover_letter": "[수정안 자소서 전문]",
  "iteration": 1
}
```

### Sub-agent 출력 (JSON)

```json
{
  "iteration": 1,
  "verdict": "PASS" | "FAIL" | "NEEDS_USER_INPUT",
  "hard_claims": [
    {
      "claim": "감사 80건 누적",
      "category": "정량",
      "source_line": "경력기술서 SPC 2022 항목 line 3",
      "status": "PASS"
    },
    {
      "claim": "FCPA 운영 경험",
      "category": "프로젝트",
      "source_line": null,
      "status": "FAIL",
      "action": "해당 문장 원상 복구"
    }
  ],
  "soft_claims": [
    {
      "transformation": "감사 활동 → 리스크 기반 감사",
      "category": "키워드 미러링",
      "status": "PASS"
    }
  ],
  "ambiguous": [
    {
      "claim": "80건+",
      "question": "원본 '80건'에서 '+'를 붙여도 되는지 확인 부탁드립니다",
      "user_response": null
    }
  ],
  "summary": "Hard 1 Fail, Soft 모두 Pass, Ambiguous 1건. 1건 원상 복구 후 사이클 종료 권장."
}
```

## 통합 시 메인 스킬 변경점

`SKILL.md` (v1.5)의 Step 5 평가 사이클 부분에 다음 흐름 명시:

```
[Step 3·4 정교화 산출물]
    ↓
[Fact-Checker sub-agent dispatch] ─── Hard FAIL ──→ 원상 복구 + 사이클 중단
    ↓ Pass or Ambiguous(사용자 확인 후 Pass)
[Stage 1·2 페르소나 평가 (병렬)] (1회차)
    ↓
[리라이팅] (7점 이하 항목)
    ↓
[Fact-Checker sub-agent dispatch] ─── Hard FAIL ──→ 원상 복구
    ↓ Pass
[Stage 1·2 재평가 (병렬)] (2회차)
    ↓
... (3회차까지 반복)
```

`persona-evaluation.md` (v1.5)의 Stage 0 섹션은 본 파일을 참조로 단축하고, 8항목 이진 표는 본 파일의 3등급 표로 대체.

## 거짓 사실 금지 원칙 (변경 없음)

본 sub-skill은 "거짓 사실 절대 금지" 원칙의 **자동 게이트**로서, 사람이 깜빡해도 시스템이 잡는다. 모호 케이스에서는 보수적 판정 (Fail 쪽으로 기운다). 사용자 통제권 보장을 위해 Ambiguous는 사용자 응답을 받는다.
