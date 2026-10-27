# 리포트 업데이트 가이드

매 거래일 두 번 이 저장소의 리포트를 갱신한다. 이 문서는 예약 작업이 따르는 기준이다.

## 공통 규칙
- 날짜는 한국 시간(Asia/Seoul) 기준 오늘 날짜를 쓴다. 파일: `reports/YYYY-MM-DD.json`
- 오늘이 한국거래소(KRX) 휴장일(주말·공휴일·연말 휴장)이면 아무것도 만들지 않고 종료한다.
- 수치는 반드시 웹 검색/조회로 확인한 값만 넣는다. 확인하지 못한 항목은 필드를 비우거나 생략한다. 추정값을 넣지 않는다.
- 문장은 모두 직접 요약해서 쓴다. 기사 문장을 그대로 옮기지 않는다.
- 숫자 필드는 숫자 타입(문자열 아님)으로 쓴다. 등락(change)과 등락률(pct)은 하락이면 음수.
- `reports/index.json`의 `reports` 배열에 오늘 날짜가 없으면 추가한다(중복 금지).
- `updatedAt`에는 "HH:MM" 형식의 한국 시간을 넣는다.
- JSON이 올바른지 확인한 뒤 커밋하고 `main`에 push한다.

## 주요 지표 (`macro`)
국고채 3년·10년, 기준금리, 원/달러, 미 국채 2년·10년, 연방기금금리, 달러지수(광의), WTI, 브렌트유, VIX, 비트코인은
GitHub Actions(`scripts/fetch_macro.py`)가 한국은행 ECOS·FRED·CoinGecko에서 자동으로 받아 `data/macro.json`에 저장하고,
사이트가 이 값을 우선 표시한다. 리포트 작업에서는 아래 두 항목만 `macro` 배열에 넣는다.

| name | group | unit |
|---|---|---|
| 금 | 원자재 | $ |
| 달러인덱스 | 환율 | (unit 생략) |

- 각 항목: `{name, group, value, unit, change, pct, note}` — `change`는 전일 대비 절대 변화, `pct`는 등락률 %, `note`는 기준 시점(예: "10/26 뉴욕")
- 확인하지 못한 항목은 배열에서 뺀다. 추정값을 넣지 않는다.

## 1) 장 시작 전 (오전, `status: "premarket"`)
새 파일을 만든다(이미 있으면 덮어쓰지 말고 아래 필드만 갱신).
- `date`, `status: "premarket"`, `updatedAt`
- `summary`: 밤사이 미국·글로벌 시장과 오늘 한국장 분위기를 2~3문장으로
- `indices`: 직전 미국 마감 S&P500, 나스닥, 다우존스 (`region: "US"`)
- `fx`: 원/달러 환율 최신값과 전일 대비 변동
- `global`: 직전 마감 기준 닛케이 225, 상해종합, 홍콩항셍, 독일 DAX, 영국 FTSE
- `usNotes`: 미국 증시 주요 동향 3~5개
- `preview`: 오늘 한국장에서 볼 포인트 3~5개 (실적 발표, 경제지표 발표, 이벤트 일정 등)
- `news`: 주요 경제 뉴스 3~6개 `{title, source, summary, url}` (title은 직접 쓴 짧은 제목 가능, url은 실제 기사 주소)
- `sources`: 참고한 매체 이름

## 2) 장 마감 후 (오후, `status: "closed"`)
오늘 파일을 읽어서 기존 내용(미국 지수, 글로벌, preview, news)은 유지하고 아래를 추가·갱신한다. 파일이 없으면 새로 만든다.
- `status: "closed"`, `updatedAt`
- `summary`: 오늘 한국장 총평 2~3문장으로 교체
- `indices`: 코스피, 코스닥, 코스피200을 맨 앞에 추가 (`region: "KR"`, 특이사항은 `note`), 미국 지수는 그대로 둔다
- `fx`: 오늘 원/달러 종가로 갱신
- `flows.kospi`: 외국인, 기관, 개인, 프로그램 순매수(억원) `{investor, amount}`
- `flows.kosdaqNote`: 코스닥 수급 한 줄 요약
- `stocks.kospi`, `stocks.kosdaq`: 거래대금 상위 5종목 `{name, code, price, pct}`
- `insights`: 시사점 및 특이사항 4~7개
- `news`: 장중에 나온 중요한 뉴스가 있으면 추가 (총 8개 이내)
- `sources`: 갱신

## 데이터 예시
`reports/2026-10-26.json` 참고.
