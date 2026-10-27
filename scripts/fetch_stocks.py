"""네이버 증권 모바일 API에서 코스피·코스닥 거래대금 상위 종목(ETF·ETN 제외)을 받아
data/top_stocks.json에 날짜별로 저장한다. 키 불필요."""
import json
import os
import sys
import urllib.request

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "top_stocks.json")
TOP_N = 5          # 저장 개수 (화면에는 3개 표시)
KEEP_DAYS = 250    # 보관할 날짜 수
UA = {"User-Agent": "Mozilla/5.0 (market-notes)"}


def num(s):
    try:
        return float(str(s).replace(",", ""))
    except ValueError:
        return None


def fetch(market):
    url = f"https://m.stock.naver.com/api/stocks/priceTop/{market}?page=1&pageSize=40"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        data = json.load(r)
    rows, date = [], None
    for s in data.get("stocks", []):
        if s.get("stockEndType") != "stock":
            continue
        date = date or (s.get("localTradedAt") or "")[:10]
        rows.append({
            "name": s.get("stockName"),
            "code": s.get("itemCode"),
            "price": num(s.get("closePrice")),
            "pct": num(s.get("fluctuationsRatio")),
            "tradingValue": num(s.get("accumulatedTradingValue")),  # 백만원
        })
        if len(rows) >= TOP_N:
            break
    if not rows or not date:
        raise RuntimeError(f"{market}: 종목 데이터가 없습니다")
    return date, rows


def main():
    try:
        with open(OUT, encoding="utf-8") as f:
            store = json.load(f)
    except (OSError, ValueError):
        store = {}
    ok = 0
    for market, key in (("KOSPI", "kospi"), ("KOSDAQ", "kosdaq")):
        try:
            date, rows = fetch(market)
            store.setdefault(date, {})[key] = rows
            ok += 1
            print(f"OK   {market} {date}: " + ", ".join(r["name"] for r in rows[:3]))
        except Exception as e:
            print(f"FAIL {market}: {e}", file=sys.stderr)
    store = dict(sorted(store.items())[-KEEP_DAYS:])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, separators=(",", ":"))
    if ok == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
