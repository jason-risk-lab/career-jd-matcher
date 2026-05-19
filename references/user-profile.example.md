# User Profile (예시) — v1.3 신규

이 파일은 사용자별 컨텍스트를 스킬에 주입하기 위한 **템플릿**이다.

**사용법**: 이 `.example.md` 파일을 `user-profile.md`로 복사하고, 본인 정보로 채운 뒤, 스킬 호출 시 첨부하거나 메모리·CLAUDE.md에 등록한다. **`user-profile.md`는 `.gitignore`에 등록되어 커밋되지 않는다** (개인정보 보호).

```
cp references/user-profile.example.md references/user-profile.md
# 그 다음 user-profile.md를 직접 편집
```

스킬은 schema만 정의하고 실제 데이터는 사용자가 주입한다. 이 분리 덕분에 스킬 자체는 누구나 fork·공유 가능한 일반 도구가 된다.

## 목차

- [1. 직무 정체성](#1-직무-정체성-cover-letter-refinement에서-사용)
- [2. 산업 선호도](#2-산업-선호도-company-analysis에서-사용)
- [3. 거버넌스·리스크 민감도](#3-거버넌스리스크-민감도-company-analysis에서-사용)
- [4. 사전 필터 조건](#4-사전-필터-조건-분석에서-제외)
- [5. 핵심 정량 근거](#5-핵심-정량-근거-resume-cover-letter에서-사용)
- [6. 회피 키워드·이력 가이드](#6-회피-키워드이력-가이드선택)

---

## 1. 직무 정체성 (cover-letter-refinement에서 사용)

자소서 톤·키워드의 일관성을 위해 본인이 어떤 직무 정체성/슬로건을 가지고 있는지 1~3줄로 정의한다. **Step 4-0에서 1회 확인하므로**, 여기 적힌 값이 자동 반영되지 않고 매번 사용자에게 확인 후 사용된다.

```yaml
identity:
  primary: "Risk Solution Partner"           # 핵심 1줄 슬로건
  description: "처벌보다 신뢰 기반의 감사 — 데이터와 사람을 연결하는 컴플라이언스"
  supporting:
    - "글로벌 멘토 지향 — 단기 성과를 넘어선 장기 영향력"
    - "데이터 + 사람 — Python·SQL 등 데이터 역량을 사람·문화와 연결"
```

자소서 정교화 시:
- 첫 문단·중간·결론에 자연스럽게 반복 노출
- 한 군데서만 외치고 사라지지 않도록 분포 확인

## 2. 산업 선호도 (company-analysis에서 사용)

특정 산업에 대한 본인의 호불호·익숙도를 기록. **회사 분석 시 가중치 조정에는 사용하지 않고**, Section 6 Meaning 축 채점 시 참고 자료로만 활용.

```yaml
industries:
  preferred:                                  # 선호 — 의사결정 시 가점 인자로 노출
    - "식품"
    - "유통"
    - "프랜차이즈"
  comfortable:                                # 익숙 — 표준 분석
    - "IT"
    - "플랫폼"
    - "제약"
  caution:                                    # 신중 — 매칭 사유를 더 꼼꼼히 검토
    - "그 외 산업"
```

## 3. 거버넌스·리스크 민감도 (company-analysis에서 사용)

본인이 과거 경험에서 트라우마/학습 포인트를 가진 리스크 영역을 명시. Step 1.6 지배구조·1.7 평판 시그널 분석 시 추가 주의 신호로 작동.

```yaml
risk_sensitivity:
  high:                                       # 강하게 체크 — 발견 시 보고서에 굵게 표시
    - "오너 리스크 / 대주주 갈등"
    - "감사 기능 독립성 (직전 1년 내 CAE·CCO·감사책임자 교체)"
    - "내부고발자 보복 이력"
  medium:                                     # 표준 체크
    - "재무 건전성 (부채비율, 자본잠식)"
    - "잡플래닛·블라인드 일관 부정 패턴"
  notes:
    - "본인이 SPC·인스파이어 등에서 거버넌스 충돌로 어려움을 겪은 이력이 있다면 여기 한 줄 적어 두기. 분석 보고서 작성 시 어조 조정에 반영."
```

## 4. 사전 필터 조건 (분석에서 제외)

스킬 호출 전에 사용자가 이미 사전 필터링한 조건. 분석 단계에서는 다루지 않는다.

```yaml
prefiltered:
  - commute_distance      # 통근 거리는 본인이 사전에 잘랐다고 가정
  - salary_floor          # 연봉 하한도 사전 필터
  - work_arrangement      # 출근/원격 조건도 사전 필터
```

이 항목들이 보고서 본문에서 다시 다뤄지면 토큰 낭비이므로 제외한다.

## 5. 핵심 정량 근거 (resume·cover letter에서 사용)

본인 경력의 정량 성과 중 가장 임팩트 있는 것 3~5개. **거짓 사실 금지 원칙상 이 수치는 원본 경력기술서와 1:1 매칭되어야 한다.** Stage 0 Fact-Checker가 이 값을 게이트로 사용.

```yaml
key_metrics:
  - metric: "감사 80건+ / 5년"
    source: "경력기술서 SPC 정도경영실 섹션"
    use_for: ["헤드라인", "강점 Top 3", "자소서 2번 문항"]
  - metric: "제보 400건 처리, 96% 해결률"
    source: "경력기술서 K-Whistle 핫라인 항목"
    use_for: ["강점", "면접 답변 키"]
  - metric: "100시나리오 상시감사 시스템 단독 설계"
    source: "경력기술서 Python·SQL 항목"
    use_for: ["데이터 역량 강조 시"]
```

## 6. 회피 키워드·이력 가이드 (선택)

본인 이력 중 노출을 최소화하고 싶거나, 면접에서 미리 답을 준비해 두고 싶은 항목. **숨기지 않고 다루는 방향**으로만 사용 (거짓 사실 금지 원칙 동일).

```yaml
sensitive_topics:
  - topic: "짧은 재직기간 (3개월)"
    framing: "통근 안전(200km) + 자녀·건강 사유 + 다음 회사 선택 기준 재정립"
    use_for: ["면접 예상 질문 Top 5 - 이전 직장 사유형"]
  - topic: "FCPA 실무 무경험"
    framing: "국내 부패방지법 운영 경험을 토대로 글로벌 기준 확장 학습 중"
    use_for: ["자소서 갭 처리", "면접 갭 검증형 답변"]
```

## 7. 메모리·CLAUDE.md와의 관계

- **메모리 (Claude memory)**: 시간 경과로 누적되는 일반적 사용자 정보. **여기서는 직무 정체성을 자동 반영하지 않는다.** user-profile.md가 single source of truth.
- **CLAUDE.md**: 프로젝트별 룰. 본 스킬과 무관.
- **본 user-profile.md**: 이직 지원 워크플로우 전용. 회사·직무에 따라 미세조정.

## 변경 이력

- v1.3 (2026-05): 신규. 기존 `company-analysis.md`·`cover-letter-refinement.md`·`resume-refinement.md`에 흩어져 있던 사용자별 컨텍스트를 한 파일로 통합.
