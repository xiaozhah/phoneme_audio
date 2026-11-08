"""Build monthly PM2.5 / US AQI table (2010-01..2026-10) and charts.
Sources
  US State Dept consulate monitors (hourly, via UCI 'PM2.5 Data of Five Chinese Cities', 2010-2015)
  CNEMC national monitoring network city means (hourly, quotsoft.net mirror, 2014-05-13..)
  News: 中国新闻网 scroll index + NYT sitemap headline counts.
"""
import sys, os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

W = sys.argv[1]               # scratch root
OUT = sys.argv[2]             # deliverable dir
os.makedirs(OUT, exist_ok=True)
fm.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
plt.rcParams.update({"font.family": "WenQuanYi Zen Hei", "axes.unicode_minus": False,
                     "font.size": 10.5, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#8a8984", "axes.labelcolor": "#52514e",
                     "xtick.color": "#52514e", "ytick.color": "#52514e"})
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#fcfcfb"

LOCS = ["全国城市均值", "北京", "上海", "武汉", "广州"]
LABEL = {"全国城市均值": "全国(所有城市均值)", "北京": "北京", "上海": "上海", "武汉": "武汉", "广州": "广州"}
COLOR = {"全国城市均值": "#52514e", "北京": "#2a78d6", "上海": "#eb6834", "武汉": "#1baf7a", "广州": "#6250d6"}
LAST_FULL_MONTH = pd.Period("2026-10", "M")

# ---------- US AQI (EPA PM2.5 breakpoints, revised 2024-02) ----------
BP = [(0.0, 9.0, 0, 50), (9.1, 35.4, 51, 100), (35.5, 55.4, 101, 150), (55.5, 125.4, 151, 200),
      (125.5, 225.4, 201, 300), (225.5, 325.4, 301, 500)]
CAT = ["优 Good", "中等 Moderate", "对敏感人群不健康", "不健康 Unhealthy", "非常不健康", "危险 Hazardous"]
def aqi(c):
    if pd.isna(c): return np.nan
    c = np.floor(c * 10) / 10
    for lo, hi, ilo, ihi in BP:
        if c <= hi:
            return round((ihi - ilo) / (hi - lo) * (max(c, lo) - lo) + ilo)
    return 500
def aqi_cat(a):
    if pd.isna(a): return ""
    for (lo, hi, ilo, ihi), name in zip(BP, CAT):
        if a <= ihi: return name
    return CAT[-1]

# ---------- daily series ----------
def us_post_daily():
    m = {"Beijing": "北京", "Shanghai": "上海", "Guangzhou": "广州"}
    out = []
    for en, zh in m.items():
        df = pd.read_csv(f"{W}/dl/uci/FiveCitiePMData/{en}PM20100101_20151231.csv")
        df["date"] = pd.to_datetime(df[["year", "month", "day"]])
        g = df.groupby("date")["PM_US Post"].agg(["mean", "count"])
        g = g[g["count"] >= 18]
        out.append(pd.DataFrame({"date": g.index, "city": zh, "pm25": g["mean"].values}))
    return pd.concat(out)

us = us_post_daily(); us["src"] = "美国使领馆监测点"
cn = pd.read_csv(f"{W}/out/cnemc_daily.csv", parse_dates=["date"]); cn["src"] = "中国国控站城市均值"
cn = cn.drop_duplicates(["date", "city"])

def monthly(d):
    d = d.assign(month=d["date"].dt.to_period("M"))
    g = d.groupby(["city", "month"])["pm25"].agg(["mean", "count"]).reset_index()
    g["days_in_month"] = g["month"].dt.days_in_month
    return g[g["count"] >= 15]  # >= 15 valid days per month

mu, mc = monthly(us), monthly(cn)
# overlap check (2014-05..2015-12): consulate single site vs city-wide network mean
ov = mu.merge(mc, on=["city", "month"], suffixes=("_us", "_cn"))
ov = ov[(ov.month >= pd.Period("2014-06", "M")) & (ov.month <= pd.Period("2015-12", "M"))]
ovs = ov.groupby("city").apply(lambda x: pd.Series({
    "月份数": len(x), "使领馆均值": x.mean_us.mean(), "国控站均值": x.mean_cn.mean(),
    "相关系数r": np.corrcoef(x.mean_us, x.mean_cn)[0, 1]})).round(2)
print(ovs)

# splice: CNEMC from 2014-06 (first full month), US consulate before
mu["source"] = "美国使领馆监测点(单站)"; mc["source"] = "中国国控站(全市平均)"
spl = pd.concat([mu[mu.month < pd.Period("2014-06", "M")], mc[mc.month >= pd.Period("2014-06", "M")]])
spl = spl[spl.month <= LAST_FULL_MONTH]
months = pd.period_range("2010-01", LAST_FULL_MONTH, freq="M")
rows = []
for loc in LOCS:
    s = spl[spl.city == loc].set_index("month")
    for mth in months:
        if mth in s.index:
            r = s.loc[mth]; v = float(r["mean"]); a = aqi(v)
            rows.append([loc, mth.year, mth.month, round(v, 1), a, aqi_cat(a), r["source"], int(r["count"])])
        else:
            rows.append([loc, mth.year, mth.month, np.nan, np.nan, "", "无公开逐时数据", 0])
tab = pd.DataFrame(rows, columns=["地点", "年", "月", "PM2.5(μg/m³)", "US AQI", "AQI等级", "数据来源", "有效天数"])

# annual means (from monthly means; require >= 10 months)
ann = tab.dropna(subset=["PM2.5(μg/m³)"]).groupby(["地点", "年"]).agg(
    pm=("PM2.5(μg/m³)", "mean"), n=("月", "count")).reset_index()
ann = ann[ann.n >= 10].copy(); ann["aqi"] = ann.pm.apply(aqi)
ann_w = ann.pivot(index="年", columns="地点", values="pm").reindex(columns=LOCS).round(1)
print(ann_w)

# ---------- news ----------
def news(src):
    d = pd.read_csv(f"{W}/out/news_daily_{src}.csv", parse_dates=["date"]).drop_duplicates("date")
    d = d[d.total > 0]
    d["year"] = d.date.dt.year
    h = pd.read_csv(f"{W}/out/news_hits_{src}.csv", parse_dates=["date"])
    h["t"] = h.title.str.replace(r"\(\d+\)|（\d+）|\(图\)|\(组图\)|\s", "", regex=True)
    h = h[~h.title.str.contains("烟霾", na=False)].drop_duplicates(["date", "t"])
    if src == "nyt":
        txt = h.title + " " + h.url.str.rsplit("/", n=1).str[-1].str.replace("-", " ")
        air = txt.str.contains(r"smog|haze|hazy|air ?pollut|air quality|airpocalypse|pm ?2\.5|polluted air|bad air|toxic air|dirty air|clean air|blue sk|purifier", case=False, regex=True)
        gen = txt.str.contains(r"pollut", case=False) & ~txt.str.contains(r"water|river|soil|lake|sea\b|ocean|plastic|waste|cadmium|spill|chemical|noise|light pollution", case=False, regex=True)
        h = h[air | gen]
        h.to_csv(f"{OUT}/nyt_haze_headlines.csv", index=False, encoding="utf-8-sig")
    else:
        h.to_csv(f"{OUT}/cns_haze_headlines.csv", index=False, encoding="utf-8-sig")
    d = d.drop(columns="hits").merge(h.groupby("date").size().rename("hits"), on="date", how="left").fillna({"hits": 0})
    y = d.groupby("year").agg(days=("date", "count"), total=("total", "sum"), hits=("hits", "sum"))
    y["per10k"] = y.hits / y.total * 1e4
    d["m"] = d.date.dt.to_period("M")
    m = d.groupby("m").agg(days=("date", "count"), total=("total", "sum"), hits=("hits", "sum"))
    m["share"] = m.hits / m.total * 1e4
    m["est"] = m.hits * m.index.days_in_month / m.days      # scale for missing archive days
    ok = m[m.days >= 10]
    y["months_ok"] = ok.groupby(ok.index.year).size().reindex(y.index).fillna(0).astype(int)
    y["monthly_mean_per10k"] = ok.groupby(ok.index.year).share.mean().reindex(y.index)
    y["est_full_year_hits"] = m.groupby(m.index.year).est.sum().reindex(y.index).round()
    y["reliable"] = y.months_ok >= 9
    m.to_csv(f"{OUT}/news_monthly_{src}.csv", encoding="utf-8-sig")
    return d, y
cnsd, cnsy = news("cns"); nytd, nyty = news("nyt")
print(cnsy); print(nyty)
# 2026 only to 11-07 -> fine for share; for NYT counts, annualise for ranking note only
peak_cns = int(cnsy[cnsy.reliable].per10k.idxmax()); peak_nyt = int(nyty.hits.idxmax())
assert peak_cns == int(cnsy[cnsy.reliable].monthly_mean_per10k.idxmax()) == int(cnsy[cnsy.reliable].est_full_year_hits.idxmax()), "metrics disagree"
print("peak cns", peak_cns, "peak nyt", peak_nyt)
PEAK = peak_cns

# ---------- save tables ----------
with pd.ExcelWriter(f"{OUT}/china_pm25_monthly_2010_2026.xlsx") as xw:
    tab.to_excel(xw, sheet_name="逐月数据(长表)", index=False)
    for loc in LOCS:
        t = tab[tab["地点"] == loc]
        p = t.pivot(index="年", columns="月", values="PM2.5(μg/m³)"); p.columns = [f"{c}月" for c in p.columns]
        q = t.pivot(index="年", columns="月", values="US AQI"); q.columns = [f"{c}月" for c in q.columns]
        p.to_excel(xw, sheet_name=f"{loc[:4]}_PM2.5")
        q.to_excel(xw, sheet_name=f"{loc[:4]}_USAQI")
    a = ann.copy(); a.columns = ["地点", "年", "年均PM2.5", "有效月数", "年均对应US AQI"]
    a.round(1).to_excel(xw, sheet_name="年均值", index=False)
    ovs.to_excel(xw, sheet_name="两数据源重叠期对比")
    nn = pd.concat({"中国新闻网": cnsy, "纽约时报": nyty}, axis=1)
    nn.round(2).to_excel(xw, sheet_name="雾霾新闻年度统计")
tab.to_csv(f"{OUT}/china_pm25_monthly_2010_2026.csv", index=False, encoding="utf-8-sig")
nn.round(2).to_csv(f"{OUT}/haze_news_by_year.csv", encoding="utf-8-sig")

# ---------- charts ----------
def aqi_bands(ax, ymax, labels=True):
    for (lo, hi, ilo, ihi), name in zip(BP, CAT):
        if lo > ymax: break
        ax.axhline(hi, color=GRID, lw=0.8, zorder=0)
        if labels and (min(hi, ymax) - lo) >= ymax * 0.09:
            ax.text(1.005, (lo + min(hi, ymax)) / 2, f"AQI {ilo}–{ihi}\n{name}", transform=ax.get_yaxis_transform(),
                    va="center", ha="left", fontsize=8, color=MUTED)

def peak_band(ax, y=PEAK, label=None):
    ax.axvspan(y, y + 1, color="#d03b3b", alpha=0.09, lw=0, zorder=0)
    if label:
        ax.text(y + 0.5, 1.0, label, transform=ax.get_xaxis_transform(), ha="center",
                va="bottom", fontsize=9.5, color="#a02020", fontweight="bold")

x_lim = (2009.9, 2027.1)
def year_axis(ax):
    ax.set_xlim(*x_lim)
    ax.set_xticks([y + 0.5 for y in range(2010, 2027)]); ax.set_xticklabels(range(2010, 2027))
    ax.set_xticks(range(2010, 2028), minor=True); ax.tick_params(axis="x", which="major", length=0)
    ax.grid(axis="x", which="minor", color=GRID, lw=0.6)

# Figure 1: overview — annual mean + news
fig, axes = plt.subplots(3, 1, figsize=(13, 13.5), gridspec_kw={"height_ratios": [2.3, 1, 1]}, sharex=True)
fig.patch.set_facecolor(SURF)
ax = axes[0]
for loc in LOCS:
    a = ann[ann["地点"] == loc]
    xs = a["年"] + 0.5
    ax.plot(xs, a.pm, color=COLOR[loc], lw=2.2 if loc != "全国城市均值" else 2.6,
            ls="-" if loc != "全国城市均值" else (0, (5, 2)), marker="o", ms=6, mec=SURF, mew=1.5, label=LABEL[loc], zorder=3)
# label the peak values
for loc in ["北京"]:
    a = ann[ann["地点"] == loc].set_index("年")
    for y in a.index[:6]:
        ax.annotate(f"{a.loc[y,'pm']:.0f}", (y + 0.5, a.loc[y, "pm"]), xytext=(0, 9),
                    textcoords="offset points", ha="center", fontsize=8.5, color=INK2)
ax.set_ylim(0, 115); aqi_bands(ax, 115)
ax.set_ylabel("年均 PM2.5 浓度 (μg/m³)")
ax.axvline(2014 + 5 / 12, color=MUTED, lw=1, ls=":")
ax.text(2014 + 5 / 12, 4, "← 美国使领馆单站数据 | 中国国控站全市均值 →", fontsize=8.5, color=MUTED, ha="center", va="bottom",
        bbox=dict(fc=SURF, ec="none", pad=1))
ax.legend(loc="upper right", bbox_to_anchor=(0.995, 0.93), frameon=False, ncol=1, fontsize=9.5)
peak_band(ax, label=f"雾霾新闻报道最多的年份：{PEAK}")
ax.set_title("北京 · 上海 · 武汉 · 广州 · 全国  年均 PM2.5 与 US AQI 等级（2010–2026）", loc="left", fontsize=14, color=INK, pad=24)
year_axis(ax)

ax = axes[1]
xs = cnsy.index + 0.5
cols = ["#d03b3b" if y == PEAK else ("#2a78d6" if cnsy.loc[y, "reliable"] else "#b9b8b2") for y in cnsy.index]
ax.bar(xs, cnsy.per10k, width=0.7, color=cols, zorder=2)
for xv, (y, r) in zip(xs, cnsy.iterrows()):
    ax.text(xv, r.per10k, f"{r.per10k:.1f}" if r.reliable else f"{r.per10k:.1f}\n存档不足", ha="center", va="bottom", fontsize=8.5, color=INK2)
ax.set_ylabel("每万条标题中\n含“雾霾/霾/PM2.5”")
ax.set_title(f"中国新闻网（中新社）全部滚动新闻标题中雾霾相关标题占比   峰值 {peak_cns} 年：每万条 {cnsy.loc[peak_cns,'per10k']:.1f} 条（按存档缺失补齐约 {int(cnsy.loc[peak_cns,'est_full_year_hits'])} 条）",
             loc="left", fontsize=11, color=INK)
peak_band(ax); ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)

ax = axes[2]
xs = nyty.index + 0.5
cols = ["#d03b3b" if y == peak_nyt else "#eb6834" for y in nyty.index]
ax.bar(xs, nyty.hits, width=0.7, color=cols, zorder=2)
for xv, (y, r) in zip(xs, nyty.iterrows()):
    ax.text(xv, r.hits, f"{int(r.hits)}", ha="center", va="bottom", fontsize=8.5, color=INK2)
ax.set_ylabel("篇数")
ax.set_title(f"《纽约时报》标题同时提及“雾霾/空气污染”与“中国/北京等”的文章数   最多 {peak_nyt} 年 {int(nyty.hits.max())} 篇，{PEAK} 年 {int(nyty.loc[PEAK,'hits'])} 篇（样本小，作国际视角参考）",
             loc="left", fontsize=11, color=INK)
peak_band(ax, peak_nyt); ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
for a_ in axes: year_axis(a_)
fig.text(0.01, 0.005,
         "数据：PM2.5 2010-01–2014-05 为美国驻华使领馆监测点逐时数据（UCI 机器学习库整理；上海/广州自2011年末起；武汉与全国在2014-05前无公开逐时数据），"
         "2014-06 起为中国环境监测总站国控站城市均值（quotsoft.net 镜像）。\nUS AQI 按美国EPA 2024年PM2.5分级换算（对月/年均浓度换算，仅表示等级位置）。"
         "2026年为1–10月。新闻：逐日抓取中国新闻网滚动新闻页与《纽约时报》站点地图全部标题后按关键词计数；2026年截至11月7日。",
         fontsize=8, color=MUTED, va="bottom")
fig.tight_layout(rect=(0, 0.035, 0.93, 1))
fig.savefig(f"{OUT}/fig1_年均PM25与雾霾新闻.png", dpi=170, facecolor=SURF)

# Figure 2: monthly small multiples
fig, axes = plt.subplots(5, 1, figsize=(13, 15), sharex=True)
fig.patch.set_facecolor(SURF)
for ax, loc in zip(axes, LOCS):
    t = tab[tab["地点"] == loc].copy()
    t["d"] = t["年"] + (t["月"] - 0.5) / 12
    us_part = t[t["数据来源"].str.startswith("美国")]; cn_part = t[t["数据来源"].str.startswith("中国")]
    ymax = 260 if loc == "北京" else 150
    aqi_bands(ax, ymax)
    peak_band(ax)
    ax.text(PEAK + 0.5, ymax * 0.97, f"雾霾新闻\n最多：{PEAK}", ha="center", va="top", fontsize=8.5, color="#a02020")
    ax.plot(us_part.d, us_part["PM2.5(μg/m³)"], color=COLOR[loc] if loc != "全国城市均值" else INK2, lw=1.6, ls=(0, (3, 1.5)))
    ax.plot(cn_part.d, cn_part["PM2.5(μg/m³)"], color=COLOR[loc] if loc != "全国城市均值" else INK2, lw=1.6)
    # annual mean step
    a = ann[ann["地点"] == loc]
    for _, r in a.iterrows():
        ax.hlines(r.pm, r["年"], r["年"] + 1, color=INK, lw=1.2, alpha=0.6)
    mx = t.loc[t["PM2.5(μg/m³)"].idxmax()]
    ax.annotate(f"最高月 {int(mx['年'])}-{int(mx['月']):02d}: {mx['PM2.5(μg/m³)']:.0f} μg/m³ (AQI {int(mx['US AQI'])})",
                (mx.d, mx["PM2.5(μg/m³)"]), xytext=(14, 4), textcoords="offset points", fontsize=8.5, color=INK2, va="bottom",
                bbox=dict(fc=SURF, ec="none", pad=1, alpha=0.85))
    ax.set_ylim(0, ymax)
    ax.set_title(f"{LABEL[loc]}　逐月 PM2.5（μg/m³）", loc="left", fontsize=11.5, color=INK)
    if loc in ("武汉", "全国城市均值"):
        ax.text(2012.2, ymax * 0.5, "2014年5月前无公开逐时监测数据", ha="center", fontsize=9, color=MUTED)
for a_ in axes: year_axis(a_)
fig.text(0.01, 0.004, "虚线=美国使领馆单站；实线=中国国控站全市均值；黑色短横=当年年均值；右侧为对应 US AQI 等级。红色底=雾霾新闻报道最多的年份（中国新闻网标题占比）。",
         fontsize=8.5, color=MUTED)
fig.tight_layout(rect=(0, 0.015, 0.92, 1))
fig.savefig(f"{OUT}/fig2_逐月PM25.png", dpi=150, facecolor=SURF)

# Figure 3: heatmap year x month, US AQI
from matplotlib.colors import BoundaryNorm, ListedColormap
aqi_colors = ["#00e400", "#ffff00", "#ff7e00", "#ff0000", "#8f3f97", "#7e0023"]  # official EPA AQI colors
cmap = ListedColormap(aqi_colors); norm = BoundaryNorm([0, 50.5, 100.5, 150.5, 200.5, 300.5, 500], 6)
fig, axes = plt.subplots(1, 5, figsize=(17, 7.5), sharey=True)
fig.patch.set_facecolor(SURF)
years = list(range(2010, 2027))
for ax, loc in zip(axes, LOCS):
    t = tab[tab["地点"] == loc]
    M = t.pivot(index="年", columns="月", values="US AQI").reindex(index=years, columns=range(1, 13))
    P = t.pivot(index="年", columns="月", values="PM2.5(μg/m³)").reindex(index=years, columns=range(1, 13))
    ax.imshow(np.ma.masked_invalid(M.values.astype(float)), cmap=cmap, norm=norm, aspect="auto")
    for i in range(len(years)):
        for j in range(12):
            v = M.values[i, j]
            if not pd.isna(v):
                ax.text(j, i, f"{int(v)}", ha="center", va="center", fontsize=6.5,
                        color="white" if v > 150 else "#222")
    ax.set_xticks(range(12)); ax.set_xticklabels([f"{m}" for m in range(1, 13)], fontsize=8)
    ax.set_yticks(range(len(years))); ax.set_yticklabels(years, fontsize=8.5)
    ax.set_title(LABEL[loc], fontsize=11.5, color=INK)
    ax.set_xlabel("月份")
    if M.iloc[:4].isna().all().all():
        ax.text(5.5, 1.5, "2014年5月前\n无公开逐时数据", ha="center", va="center", fontsize=9, color=MUTED)
    i = years.index(PEAK)
    ax.add_patch(plt.Rectangle((-0.5, i - 0.5), 12, 1, fill=False, ec="#0b0b0b", lw=2))
    for s in ax.spines.values(): s.set_visible(False)
axes[0].text(-2.6, years.index(PEAK), "新闻最多→", ha="right", va="center", fontsize=9, color="#a02020", fontweight="bold")
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in aqi_colors]
fig.legend(handles, [f"{a}–{b}  {n}" for (_, _, a, b), n in zip(BP, CAT)], loc="lower center", ncol=6, frameon=False, fontsize=9)
fig.suptitle(f"逐月 US AQI 热力图（格内数字=月均PM2.5换算的US AQI；黑框={PEAK}年，雾霾新闻报道最多）", x=0.01, ha="left", fontsize=13, color=INK)
fig.tight_layout(rect=(0.02, 0.05, 1, 0.96))
fig.savefig(f"{OUT}/fig3_逐月USAQI热力图.png", dpi=160, facecolor=SURF)
print("saved")
