# 일일 증시 아카이브

장마감 증시 리포트를 날짜별로 모아 보는 사이트입니다.

## 구조
- `index.html` — 사이트 화면
- `reports/YYYY-MM-DD.json` — 날짜별 리포트 데이터
- `reports/index.json` — 게시된 리포트 날짜 목록 (새 리포트를 추가하면 여기에도 날짜를 넣어야 화면에 나타납니다)

## 리포트 데이터 형식
`reports/2026-10-26.json`을 참고하세요. 주요 필드:
`date`, `summary`, `indices[]`(name, region, close, change, pct, note), `fx`(usdkrw, change),
`flows`(kospi[], kosdaqNote), `stocks`(kospi[], kosdaq[]), `usNotes[]`, `global[]`, `insights[]`,
`news[]`(title, source, summary, url), `sources[]`
