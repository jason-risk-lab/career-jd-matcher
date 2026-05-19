# 분석 보고서 docx 생성 가이드 (Section 1~6 통합) — v1.2+

5단계 분석의 채팅 마크다운 결과를 **별도 docx 파일 1개**로 생성한다. 이력서·자소서가 "제출용"이라면, 이 보고서는 **본인용 의사결정·면접 준비 자료**다.

## 목차

- [1. 파일명](#파일명)
- [2. 보고서 구조 (목차 순서)](#보고서-구조-목차-순서)
- [3. 콘텐츠 포함 원칙](#콘텐츠-포함-원칙)
- [4. docx 생성 코드 패턴 (요약)](#docx-생성-코드-패턴-요약)
- [5. 작업 순서 (실행 시)](#작업-순서-실행-시)
- [6. 출력 시 주의](#출력-시-주의)
- [7. 한 줄 진행 알림](#한-줄-진행-알림)

## 파일명

`지원분석보고서_[회사명]_[직무명].docx`

`/mnt/user-data/outputs/`에 저장 후 `present_files`로 다른 두 docx와 함께 제시.

## 보고서 구조 (목차 순서)

분석 보고서는 다음 7개 섹션으로 구성. 채팅 마크다운의 Section 1~6 + 표지 1페이지.

```
[표지]
- 회사명, 직무명, 분석 일자
- 종합 점수 (예: 71.8 / 100)
- 지원 권장도 (🟢 강력 지원 / 🟡 신중 검토 / 🔴 재고 권장)
- 한 줄 결론

[목차]

1. 회사 분석 (BCG 컨설턴트 관점)
2. JD 매칭 대시보드
3. 경력기술서 변경 전후 비교
4. 자기소개서 변경 전후 비교 + 적용된 직무 정체성
5. 멀티 페르소나 평가 결과 (9 페르소나 + Stage 0 Fact-Checker)
6. 종합 판단 및 권고 (의사결정 매트릭스)
7. 면접 예상 질문 Top 5 + 답변 키 포인트
```

## 콘텐츠 포함 원칙

채팅 마크다운에 출력된 내용을 **그대로 docx로 옮긴다**. 재생성·요약하지 않는다. 그래야:
- 토큰·시간 추가 부담이 최소화됨
- 채팅과 docx 내용이 일치해 사용자가 혼란 없음

다만 docx에서는 다음만 추가 처리:

| 처리 | 이유 |
|------|------|
| 표지 1페이지 | docx 첫인상 + 한눈에 결론 |
| 목차 자동 생성 | 본인 복습용 네비게이션 |
| Section별 페이지 브레이크 | 인쇄·PDF 변환 시 가독성 |
| 헤더/푸터 | 회사명·페이지 번호 |
| 표 서식 (음영·테두리) | docx-js 표 표준 적용 |

## docx 생성 코드 패턴 (요약)

상세 구문은 `/mnt/skills/public/docx/SKILL.md` 참조. 본 보고서 작성 시 핵심 패턴:

### 1) 페이지 설정 (한국 사용자 → A4 권장)

```javascript
sections: [{
  properties: {
    page: {
      size: {
        width: 11906,   // A4 width in DXA
        height: 16838   // A4 height in DXA
      },
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
    }
  },
  children: [/* content */]
}]
```

### 2) 표지 페이지

```javascript
// 표지 후 페이지 브레이크
new Paragraph({
  heading: HeadingLevel.TITLE,
  alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: "[회사명] [직무명] 지원 패키지 분석", bold: true, size: 40 })]
}),
new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 480 },
  children: [
    new TextRun({ text: `종합 점수: 71.8 / 100`, size: 32, bold: true }),
    new TextRun({ break: 1 }),
    new TextRun({ text: `🟢 강력 지원`, size: 28 }),
    new TextRun({ break: 1 }),
    new TextRun({ text: `분석 일자: 2026-05-15`, size: 20 })
  ]
}),
new Paragraph({ children: [new PageBreak()] })
```

### 3) 목차 (TableOfContents)

```javascript
new Paragraph({
  heading: HeadingLevel.HEADING_1,
  children: [new TextRun({ text: "목차", bold: true })]
}),
new TableOfContents("Table of Contents", {
  hyperlink: true,
  headingStyleRange: "1-2"  // H1·H2까지 포함
})
```

### 4) 매트릭스·페르소나·매칭 표 (한국어 헤더)

```javascript
// 4-1) 표 너비 (A4 - 2" 여백 = 11906 - 2880 = 9026 DXA)
const tableWidth = 9026;

// 4-2) 의사결정 매트릭스 표 예시 (5열)
new Table({
  width: { size: tableWidth, type: WidthType.DXA },
  columnWidths: [2000, 1500, 1500, 1500, 2526],
  rows: [
    // 헤더 행
    new TableRow({
      tableHeader: true,
      children: ["축", "가중치", "점수", "기여 점수", "평가 근거"].map(text =>
        new TableCell({
          borders,
          width: { size: /* 각 열 너비 */, type: WidthType.DXA },
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR },  // 헤더 음영
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({
            children: [new TextRun({ text, bold: true })]
          })]
        })
      )
    }),
    // 데이터 행들...
  ]
})
```

### 5) 페이지 브레이크 (Section 사이)

각 Section 1~7 사이에 `new Paragraph({ children: [new PageBreak()] })` 삽입. 인쇄·PDF 변환 시 섹션 구분 명확.

### 6) 헤더·푸터

```javascript
headers: {
  default: new Header({
    children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: "[회사명] 지원 분석 보고서 v1.3", size: 18, color: "808080" })]
    })]
  })
},
footers: {
  default: new Footer({
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({ text: "Page ", size: 18 }),
        new TextRun({ children: [PageNumber.CURRENT], size: 18 }),
        new TextRun({ text: " / ", size: 18 }),
        new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18 })
      ]
    })]
  })
}
```

## 작업 순서 (실행 시)

1. `/mnt/skills/public/docx/SKILL.md` `view`로 최신 구문 재확인
2. 채팅에 출력된 Section 1~6 마크다운 텍스트를 메모리에 보유
3. docx-js로 생성 스크립트 작성 (`/home/claude/build_report.js`)
4. `node /home/claude/build_report.js` 실행 → `/mnt/user-data/outputs/지원분석보고서_[회사명]_[직무명].docx` 생성
5. `python /mnt/skills/public/docx/scripts/office/validate.py` 로 검증
6. 세 docx 파일을 `present_files`로 한 번에 제시

## 출력 시 주의

- **이력서·자소서 docx 생성 직후, 같은 호출 흐름에서 분석 보고서 docx도 생성한다.** 별도 사용자 요청 기다리지 않음 (v1.2 핵심 변경: 항상 3개 파일).
- 분석 보고서 docx에는 **사용자 원본 이력서/자소서 전문은 포함하지 않는다** (이미 별도 파일로 존재). Section 3·4는 변경 전후 **비교표만** 포함.
- 회사 분석 인용 URL은 docx 본문 각주가 아닌 표 내 짧은 표기로 처리 (예: "출처: DART 2025 사업보고서").
- 보고서 docx 분량은 보통 8~15페이지. 너무 길면 Section 5의 회차별 표를 "최종 회차만 + 회차별 점수 추이 한 줄"로 압축.

## 한 줄 진행 알림

분석 보고서 생성 단계에 진입 시:

> "분석 보고서 docx 생성 중... (회사 분석 + 매트릭스 + 면접 질문 포함, 약 1분)"

생성 완료 후:

> "3개 docx 파일 모두 준비 완료. 이력서·자소서·분석보고서를 함께 첨부합니다."
