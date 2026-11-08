"""Download quotsoft.net mirror of CNEMC city-level hourly data and reduce to
daily PM2.5 means for target cities + all-city national mean.
Output: out/cnemc_daily.csv (date, city, pm25_mean, n_hours) ; resumable."""
import csv, io, os, sys, datetime as dt, concurrent.futures as cf, requests, statistics

OUT = sys.argv[1]
START = dt.date(2014, 5, 13)
END = dt.date(2026, 11, 7)
CITIES = ["北京", "上海", "武汉", "广州"]
CA = "/root/.ccr/ca-bundle.crt"
s = requests.Session()

done = set()
if os.path.exists(OUT):
    with open(OUT, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            done.add(r["date"])

def fetch(d):
    url = f"https://quotsoft.net/air/data/china_cities_{d:%Y%m%d}.csv"
    for attempt in range(4):
        try:
            r = s.get(url, timeout=60, verify=CA)
            if r.status_code == 404:
                return d, None, "404"
            r.raise_for_status()
            break
        except Exception as e:
            err = str(e)
    else:
        return d, None, err
    rows = list(csv.reader(io.StringIO(r.content.decode("utf-8-sig", "replace"))))
    head = rows[0]
    hourly = {}  # city -> list of hourly pm25
    for row in rows[1:]:
        if len(row) < 4 or row[2] != "PM2.5":
            continue
        for i in range(3, min(len(row), len(head))):
            v = row[i].strip()
            if v:
                try:
                    x = float(v)
                except ValueError:
                    continue
                if 0 < x < 2000:
                    hourly.setdefault(head[i].strip(), []).append(x)
    res = []
    daily = {c: statistics.fmean(v) for c, v in hourly.items() if len(v) >= 18}
    for c in CITIES:
        if c in daily:
            res.append((c, daily[c], len(hourly[c])))
    if daily:
        res.append(("全国城市均值", statistics.fmean(daily.values()), len(daily)))
    return d, res, "ok"

days = [START + dt.timedelta(n) for n in range((END - START).days + 1)]
todo = [d for d in days if d.isoformat() not in done]
print("todo", len(todo), flush=True)
new = not os.path.exists(OUT)
with open(OUT, "a", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    if new:
        w.writerow(["date", "city", "pm25", "n"])
    with cf.ThreadPoolExecutor(12) as ex:
        for k, (d, res, status) in enumerate(ex.map(fetch, todo)):
            if res:
                for c, v, n in res:
                    w.writerow([d.isoformat(), c, f"{v:.2f}", n])
            elif status != "404":
                print("FAIL", d, status, flush=True)
            if k % 200 == 0:
                f.flush(); print(k, d, status, flush=True)
print("done")
