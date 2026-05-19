# 페르소나 9명 병렬 sub-agent 설계 (Phase 3-6) — v1.5 신규

기존 v1.4 이하에서 9 페르소나는 메인 컨텍스트에서 직렬로 채점되었다. v1.5부터 페르소나별 격리 sub-agent로 디스패치하여 **병렬 실행**한다.

## 목차

- [1. 왜 병렬화하는가](#왜-병렬화하는가)
- [2. 디스패치 패턴](#디스패치-패턴)
- [3. 페르소나별 sub-agent 스펙](#페르소나별-sub-agent-스펙)
- [4. 결과 집계 (orchestrator)](#결과-집계-orchestrator)
- [5. 토론 라운드 (cross-talk, Phase 2-5)](#토론-라운드-cross-talk-phase-2-5)
- [6. 회차 관리](#회차-관리)
- [7. 폴백: 병렬 미지원 환경](#폴백-병렬-미지원-환경)

## 왜 병렬화하는가

| 기존 (직렬) | v1.5 (병렬) |
|------------|-------------|
| 9명 순차 채점 → 평균 2~3분 | 9명 동시 채점 → 평균 30~60초 |
| 메인 컨텍스트에 9명 평가 + 코멘트 누적 → 비대 | 결과 JSON만 회수, 메인 컨텍스트 가벼움 |
| 후행 페르소나가 앞 페르소나 코멘트를 본 영향 | 페르소나 간 컨텍스트 누출 차단 |
| 9명 모두 같은 톤 위험 | 독립 컨텍스트 = 다양성 확보 |

## 디스패치 패턴

### A. 권장: Claude Code `context: fork` + `Task` 병렬

```
[Step 5 시작]
    ↓
[메인 agent] 8개 Task 호출을 한 메시지에 동시 발행:
    - Task(persona: black)
    - Task(persona: red)
    - Task(persona: silver)
    - Task(persona: blue)
    - Task(persona: gold)
    - Task(persona: headhunter)
    - Task(persona: manager)
    - Task(persona: hr)
    ↓ (모두 완료 대기)
[결과 집계] 8개 JSON 결과 회수
    ↓
[Fact-Checker는 별도 dispatch — references/fact-checker.md 참조]
```

Stage 0 Fact-Checker는 **다른 페르소나와 독립적으로** 호출 (격리 강도 더 강함, `references/fact-checker.md` 참조).

### B. 폴백: 단일 sub-agent에 페르소나 8명을 한 번에 위임

병렬 디스패치를 지원하지 않는 환경에서는 1개 sub-agent에 8 페르소나 룰북을 모두 주고 8개 JSON을 반환받는다. 컨텍스트 격리는 약하지만 메인 컨텍스트 분리 효과는 유지.

## 페르소나별 sub-agent 스펙

각 페르소나는 동일한 sub-agent 스키마로 호출된다:

### 입력

```json
{
  "persona_id": "red" | "silver" | "blue" | "gold" | "black" | "headhunter" | "manager" | "hr",
  "iteration": 1,
  "document_type": "resume" | "cover_letter",
  "document_content": "[전문]",
  "jd_summary": "[JD 핵심 요약, 3~5줄]",
  "user_identity": "[Step 4-0에서 확정된 직무 정체성]",
  "rules_path": "references/persona-evaluation.md#stage-1-5-color-harness-5-페르소나" 
}
```

### 출력 (JSON)

```json
{
  "persona_id": "red",
  "iteration": 1,
  "document_type": "cover_letter",
  "scores": {
    "criterion_1": 8,
    "criterion_2": 7,
    "criterion_3": 9,
    "criterion_4": 6,
    "criterion_5": 8,
    "criterion_6": 9,
    "criterion_7": 7,
    "criterion_8": 8,
    "criterion_9": 8,
    "criterion_10": 7
  },
  "average": 7.7,
  "strengths": ["정량 근거 1~2개 명시", "갭 솔직 인정"],
  "improvements": ["인과 관계 명확화 필요 (criterion 3)", "정량 수치 1개 더 (criterion 2)"]
}
```

각 페르소나의 10개 criteria 정의는 `references/persona-evaluation.md` 본문에서 그대로 사용. sub-agent는 **본인 페르소나의 룰만 본다.**

## 결과 집계 (orchestrator)

메인 agent는 8개 결과 회수 후 집계:

```python
# 의사 코드
results = wait_all(8 tasks)

stage1_personas = ["black", "red", "silver", "blue", "gold"]
stage2_personas = ["headhunter", "manager", "hr"]

stage1_avg = mean(results[p]["average"] for p in stage1_personas)
stage2_avg = mean(results[p]["average"] for p in stage2_personas)

# 리라이팅 필요 항목 식별
rewrite_targets = []
for p in stage1_personas + stage2_personas:
    if results[p]["average"] < 9.0:
        rewrite_targets.extend(results[p]["improvements"])
    for ci, score in results[p]["scores"].items():
        if score <= 7:
            rewrite_targets.append(f"{p}/{ci}: {results[p]['improvements']}")
```

## 토론 라운드 (cross-talk, Phase 2-5)

1라운드 채점 결과를 페르소나 간에 **선택적으로 공유**한 뒤, 핵심 결함을 잡았다고 판단되는 페르소나의 코멘트를 다른 페르소나에게 보여주고 재채점.

### 절차

1. **1라운드 (격리 채점)**: 위의 병렬 디스패치 그대로
2. **결함 검출**: 8 페르소나 중 단일 항목 5점 이하를 매긴 페르소나를 "핵심 비판자"로 식별 (보통 1~2명)
3. **cross-talk 디스패치**: 나머지 페르소나에게 핵심 비판자의 코멘트만 추가 컨텍스트로 주고 재채점 요청
   ```
   Task(persona: silver, additional_context="RED 페르소나가 다음을 지적했습니다: '인과 관계 불명확.' 이를 본 뒤 본인 채점을 재검토해 주세요.")
   ```
4. **2라운드 점수 회수**: 점수가 ±1점 이상 변동된 페르소나만 추적
5. **임계 충족 시 토론 종료**: 모든 페르소나 평균 9.0 이상 또는 단일 항목 7점 이하 없음

### 토론 라운드 적용 조건

- **항상 적용하지 않는다.** 1라운드에서 모든 페르소나 평균 9.0 이상이면 토론 라운드 스킵.
- **최대 1회**: cross-talk는 1회만. 무한 반복 방지.
- **토큰 부담**: 1라운드 8개 + 토론 라운드 5~8개 = 총 13~16 sub-agent 호출. 회차당 시간·비용 ~50% 증가.

## 회차 관리

기존 v1.4 이하: 평균 9.0 미만이면 리라이팅 → 재평가 (최대 3회차)

v1.5 변경:
- 회차 = 1라운드 + 토론 라운드 + 리라이팅
- 최대 회차 수 그대로 3회. 단 회차당 sub-agent 호출이 늘었으니 토큰·시간 모니터링 필요.

## 폴백: 병렬 미지원 환경

`context: fork` 또는 동시 Task가 불가능하면:
1. 직렬 호출로 8 페르소나를 순차 디스패치 (컨텍스트 격리만 유지)
2. 또는 단일 sub-agent에 8 페르소나를 한 번에 위임 (디스패치 패턴 B)

둘 다 v1.4의 메인 컨텍스트 직렬보다는 격리 강도가 높다. 사용자 환경이 병렬 디스패치를 지원하는지 메인 SKILL.md 진입 시 1줄 안내:

> "(병렬 페르소나 디스패치 시도 — 미지원 환경이면 직렬로 자동 폴백)"

## 변경 이력 통합

`SKILL.md` (v1.5) Step 5에서 본 파일을 참조로 명시. `persona-evaluation.md` (v1.5)는 페르소나별 룰북 역할을 유지하고, 디스패치/집계 방식은 본 파일이 단일 소스.
