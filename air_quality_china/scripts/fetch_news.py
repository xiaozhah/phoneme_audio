"""Count haze/smog headlines per day in two complete daily news indexes.
  cns : 中国新闻网 滚动新闻 https://www.chinanews.com.cn/scroll-news/YYYY/MMDD/news.shtml
  nyt : New York Times sitemap https://www.nytimes.com/sitemap/YYYY/MM/DD/
Writes out/news_daily_<src>.csv (date,total,hits) and out/news_hits_<src>.csv
(date,url,title) for audit. Resumable."""
import csv, os, re, sys, datetime as dt, concurrent.futures as cf, requests, time

SRC = sys.argv[1]
OUTDIR = sys.argv[2]
START, END = dt.date(2010, 1, 1), dt.date(2026, 11, 7)
CA = "/root/.ccr/ca-bundle.crt"
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (research script; haze news counting)"

# Chinese: 雾霾 / 灰霾 / 霾 (exclude metaphorical 阴霾) / PM2.5
CN_RE = re.compile(r"雾霾|灰霾|(?<!阴)霾|PM2\.5|PM2．5", re.I)
EN_POLL = re.compile(r"smog|haze|hazy|pollut|air quality|airpocalypse|pm ?2\.5|bad air|toxic air|dirty air|clean air|blue sk|purifier|breath", re.I)
EN_CHINA = re.compile(r"china|chinese|beijing|shanghai|wuhan|guangzhou|harbin|hebei|tianjin", re.I)

def url_for(d):
    if SRC == "cns":
        return f"https://www.chinanews.com.cn/scroll-news/{d:%Y}/{d:%m%d}/news.shtml"
    return f"https://www.nytimes.com/sitemap/{d:%Y}/{d:%m}/{d:%d}/"

def parse(d, b):
    if SRC == "cns":
        try:
            t = b.decode("utf-8")
        except UnicodeDecodeError:
            t = b.decode("gb18030", "replace")
        links = re.findall(r'<a href="([^"]*/20\d\d/\d\d-\d\d/[^"]+)"[^>]*>([^<]+)</a>', t)
        items = {}
        for u, title in links:
            u = re.sub(r"^https?:", "", u)
            items.setdefault(u.split("/", 3)[-1] if u.startswith("//") else u, title.strip())
        hits = [(u, ti) for u, ti in items.items() if CN_RE.search(ti)]
    else:
        t = b.decode("utf-8", "replace")
        links = re.findall(r'<a href="(https://www\.nytimes\.com/(?:19|20)[^"]+)"[^>]*>([^<]+)</a>', t)
        items = dict(links)
        hits = [(u, ti) for u, ti in items.items()
                if EN_POLL.search(ti) and (EN_CHINA.search(ti) or EN_CHINA.search(u.rsplit("/", 1)[-1]))]
    return len(items), hits

def fetch(d):
    for attempt in range(5):
        try:
            r = s.get(url_for(d), timeout=60, verify=CA)
            if r.status_code == 404:
                return d, 0, [], "404"
            if r.status_code in (429, 503):
                time.sleep(5 * (attempt + 1)); continue
            r.raise_for_status()
            n, hits = parse(d, r.content)
            return d, n, hits, "ok"
        except Exception as e:
            err = repr(e); time.sleep(2 * (attempt + 1))
    return d, None, [], err

daily_p = f"{OUTDIR}/news_daily_{SRC}.csv"; hits_p = f"{OUTDIR}/news_hits_{SRC}.csv"
done = set()
if os.path.exists(daily_p):
    with open(daily_p, encoding="utf-8") as f:
        done = {r["date"] for r in csv.DictReader(f)}
days = [START + dt.timedelta(i) for i in range((END - START).days + 1)]
todo = [d for d in days if d.isoformat() not in done]
print(SRC, "todo", len(todo), flush=True)
newd, newh = not os.path.exists(daily_p), not os.path.exists(hits_p)
with open(daily_p, "a", encoding="utf-8", newline="") as fd, open(hits_p, "a", encoding="utf-8", newline="") as fh:
    wd, wh = csv.writer(fd), csv.writer(fh)
    if newd: wd.writerow(["date", "total", "hits"])
    if newh: wh.writerow(["date", "url", "title"])
    with cf.ThreadPoolExecutor(10) as ex:
        for k, (d, n, hits, st) in enumerate(ex.map(fetch, todo)):
            if n is None:
                print("FAIL", d, st, flush=True); continue
            wd.writerow([d.isoformat(), n, len(hits)])
            for u, ti in hits: wh.writerow([d.isoformat(), u, ti])
            if k % 250 == 0:
                fd.flush(); fh.flush(); print(k, d, n, len(hits), flush=True)
print("done", flush=True)
