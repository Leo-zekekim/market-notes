import json, urllib.request
UA={"User-Agent":"Mozilla/5.0"}
out=[]
for mk in ["KOSPI","KOSDAQ"]:
    for p in ["priceTop","quantTop"]:
        try:
            with urllib.request.urlopen(urllib.request.Request(f"https://m.stock.naver.com/api/stocks/{p}/{mk}?page=1&pageSize=8",headers=UA),timeout=20) as r:
                j=json.load(r)
            out.append(f"## {mk} {p} keys={sorted(j['stocks'][0].keys())}")
            for s in j["stocks"]:
                out.append(f"{s.get('stockName')}|{s.get('itemCode')}|{s.get('stockEndType')}|{s.get('closePrice')}|{s.get('fluctuationsRatio')}|vol={s.get('accumulatedTradingVolume')}|val={s.get('accumulatedTradingValue')}|{s.get('localTradedAt','')}")
        except Exception as e:
            out.append(f"## {mk} {p} ERROR {e}")
open("probe/out.txt","w",encoding="utf-8").write("\n".join(out))
