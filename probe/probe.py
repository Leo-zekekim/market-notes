import json, urllib.request, urllib.parse, datetime
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
out=[]
def tryit(label,url,data=None,headers=None,enc="utf-8"):
    h=dict(UA); h.update(headers or {})
    try:
        req=urllib.request.Request(url,data=data,headers=h)
        with urllib.request.urlopen(req,timeout=20) as r:
            b=r.read(); out.append(f"## {label}\nstatus {r.status} len {len(b)}\n{b[:600].decode(enc,'replace')}\n")
    except Exception as e:
        out.append(f"## {label}\nERROR {e}\n")
d=(datetime.datetime.utcnow()+datetime.timedelta(hours=9)).strftime("%Y%m%d")
form=urllib.parse.urlencode({"bld":"dbms/MDC/STAT/standard/MDCSTAT01501","locale":"ko_KR","mktId":"STK","trdDd":"20261027","share":"1","money":"1","csvxls_isNo":"false"}).encode()
tryit("krx",'https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd',form,{"Referer":"https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020101","Content-Type":"application/x-www-form-urlencoded; charset=UTF-8","X-Requested-With":"XMLHttpRequest"})
tryit("naver_sise_quant","https://finance.naver.com/sise/sise_quant.naver?sosok=0",enc="euc-kr")
for p in ["quantTop","amountTop","priceTop","up","marketValue"]:
    tryit("naver_m_"+p,f"https://m.stock.naver.com/api/stocks/{p}/KOSPI?page=1&pageSize=3")
tryit("naver_m_domestic_amount","https://m.stock.naver.com/api/stocks/tradingValue/KOSPI?page=1&pageSize=3")
open("probe/out.txt","w",encoding="utf-8").write("\n".join(out))
