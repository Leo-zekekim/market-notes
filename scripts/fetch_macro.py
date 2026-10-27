"""ECOS(한국은행)·FRED(미 연준)·CoinGecko에서 주요 지표를 받아 data/macro.json에 저장한다.

- API 키는 환경변수 ECOS_API_KEY, FRED_API_KEY에서 읽는다 (GitHub Secrets).
- 지표마다 따로 받으므로 하나가 실패해도 나머지는 저장된다.
- 실패한 지표는 이전에 저장된 값을 그대로 유지한다.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "macro.json")
DAYS = 400  # 약 1년 + 여유

# key: (표시 이름, 그룹, 단위, 출처, 조회 정보)
SERIES = [
    ("kr3y",   "국고채 3년",   "금리",   "%", "ECOS", {"stat": "817Y002", "cycle": "D", "item": "010200000"}),
    ("kr10y",  "국고채 10년",  "금리",   "%", "ECOS", {"stat": "817Y002", "cycle": "D", "item": "010210000"}),
    ("krbase", "한국 기준금리", "금리",   "%", "ECOS", {"stat": "722Y001", "cycle": "M", "item": "0101000"}),
    ("usdkrw", "원/달러",      "환율",   "원", "ECOS", {"stat": "731Y001", "cycle": "D", "item": "0000001"}),
    ("us2y",   "미 국채 2년",  "금리",   "%", "FRED", {"id": "DGS2"}),
    ("us10y",  "미 국채 10년", "금리",   "%", "FRED", {"id": "DGS10"}),
    ("fedfunds", "미 연방기금금리", "금리", "%", "FRED", {"id": "DFF"}),
    ("dollar", "달러지수(광의)", "환율", "",  "FRED", {"id": "DTWEXBGS"}),
    ("wti",    "WTI",          "원자재", "$", "FRED", {"id": "DCOILWTICO"}),
    ("brent",  "브렌트유",     "원자재", "$", "FRED", {"id": "DCOILBRENTEU"}),
    ("vix",    "VIX",          "변동성", "",  "FRED", {"id": "VIXCLS"}),
    ("btc",    "비트코인",     "코인",   "$", "COINGECKO", {"id": "bitcoin"}),
]


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "market-notes/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def parse_ecos(payload, cycle):
    if "StatisticSearch" not in payload:
        raise RuntimeError(f"ECOS 응답 오류: {json.dumps(payload, ensure_ascii=False)[:200]}")
    pts = []
    for row in payload["StatisticSearch"].get("row", []):
        t, v = row.get("TIME", ""), row.get("DATA_VALUE", "")
        try:
            val = float(v)
        except ValueError:
            continue
        date = f"{t[:4]}-{t[4:6]}-{t[6:8]}" if cycle == "D" else f"{t[:4]}-{t[4:6]}-01"
        pts.append([date, val])
    return pts


def fetch_ecos(cfg, key, start, end):
    cycle = cfg["cycle"]
    s = start.strftime("%Y%m%d") if cycle == "D" else start.strftime("%Y%m")
    e = end.strftime("%Y%m%d") if cycle == "D" else end.strftime("%Y%m")
    url = (f"https://ecos.bok.or.kr/api/StatisticSearch/{urllib.parse.quote(key)}/json/kr/1/1000/"
           f"{cfg['stat']}/{cycle}/{s}/{e}/{cfg['item']}")
    return parse_ecos(get_json(url), cycle)


def parse_fred(payload):
    if "observations" not in payload:
        raise RuntimeError(f"FRED 응답 오류: {str(payload)[:200]}")
    pts = []
    for o in payload["observations"]:
        try:
            pts.append([o["date"], float(o["value"])])
        except (ValueError, KeyError):
            continue  # 휴일 등은 "." 로 온다
    return pts


def fetch_fred(cfg, key, start, end):
    q = urllib.parse.urlencode({"series_id": cfg["id"], "api_key": key, "file_type": "json",
                                "observation_start": start.strftime("%Y-%m-%d"),
                                "observation_end": end.strftime("%Y-%m-%d")})
    return parse_fred(get_json("https://api.stlouisfed.org/fred/series/observations?" + q))


def parse_coingecko(payload):
    by_day = {}
    for ms, price in payload.get("prices", []):
        d = datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        by_day[d] = round(float(price), 2)  # 같은 날은 마지막 값
    if not by_day:
        raise RuntimeError("CoinGecko 응답에 가격이 없습니다")
    return [[d, v] for d, v in sorted(by_day.items())]


def fetch_coingecko(cfg, _key, _start, _end):
    url = f"https://api.coingecko.com/api/v3/coins/{cfg['id']}/market_chart?vs_currency=usd&days=365&interval=daily"
    return parse_coingecko(get_json(url))


FETCHERS = {"ECOS": (fetch_ecos, "ECOS_API_KEY"), "FRED": (fetch_fred, "FRED_API_KEY"),
            "COINGECKO": (fetch_coingecko, None)}


def summarize(points, unit):
    pts = sorted(points)
    last = pts[-1]
    out = {"date": last[0], "value": last[1]}
    if len(pts) >= 2:
        prev = pts[-2][1]
        out["prevDate"] = pts[-2][0]
        out["change"] = round(last[1] - prev, 4)
        if unit != "%" and prev:
            out["pct"] = round((last[1] - prev) / prev * 100, 2)
    return out


def main():
    now = datetime.now(KST)
    start, end = now - timedelta(days=DAYS), now
    try:
        with open(OUT, encoding="utf-8") as f:
            old = json.load(f).get("series", {})
    except (OSError, ValueError):
        old = {}

    series, failed = {}, []
    for key, name, group, unit, source, cfg in SERIES:
        fetch, env = FETCHERS[source]
        api_key = os.environ.get(env, "") if env else ""
        try:
            if env and not api_key:
                raise RuntimeError(f"{env} 가 설정되지 않았습니다")
            pts = fetch(cfg, api_key, start, end)
            if not pts:
                raise RuntimeError("데이터가 비어 있습니다")
            series[key] = {"name": name, "group": group, "unit": unit, "source": source,
                           "latest": summarize(pts, unit), "points": sorted(pts)}
            print(f"OK   {name}: {series[key]['latest']}")
        except Exception as e:  # 지표 하나의 실패가 전체를 멈추지 않게
            failed.append(key)
            print(f"FAIL {name}: {e}", file=sys.stderr)
            if key in old:
                series[key] = old[key]

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    data = {"updatedAt": now.strftime("%Y-%m-%d %H:%M"), "failed": failed,
            "order": [s[0] for s in SERIES], "series": series}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"저장: {len(series)}개 지표, 실패 {len(failed)}개 {failed}")
    if len(failed) == len(SERIES):
        sys.exit(1)


if __name__ == "__main__":
    main()
