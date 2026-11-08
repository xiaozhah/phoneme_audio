"""One chart per page, iPhone 19.5:9 aspect, landscape + portrait vector PDFs.
Reads tables produced by build.py."""
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import BoundaryNorm, ListedColormap

D, OUT = sys.argv[1], sys.argv[2]
fm.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
plt.rcParams.update({"font.family": "WenQuanYi Zen Hei", "axes.unicode_minus": False, "pdf.fonttype": 42,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#8a8984",
                     "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e"})
INK, INK2, MUTED, GRID, SURF, RED = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#fcfcfb", "#d03b3b"
LOCS = ["全国城市均值", "北京", "上海", "武汉", "广州"]
LABEL = {"全国城市均值": "全国", "北京": "北京", "上海": "上海", "武汉": "武汉", "广州": "广州"}
COLOR = {"全国城市均值": "#52514e", "北京": "#2a78d6", "上海": "#eb6834", "武汉": "#1baf7a", "广州": "#6250d6"}
BP = [(0.0, 9.0, 0, 50), (9.1, 35.4, 51, 100), (35.5, 55.4, 101, 150), (55.5, 125.4, 151, 200),
      (125.5, 225.4, 201, 300), (225.5, 325.4, 301, 500)]
CAT = ["优", "中等", "对敏感人群不健康", "不健康", "非常不健康", "危险"]
AQI_COLORS = ["#00e400", "#ffff00", "#ff7e00", "#ff0000", "#8f3f97", "#7e0023"]
YEARS = list(range(2010, 2027))
SRC_PM = "数据：2010–2014.5 美国驻华使领馆监测点（UCI整理）；2014.6起 中国环境监测总站国控站城市均值。2026年为1–10月。"

tab = pd.read_csv(f"{D}/china_pm25_monthly_2010_2026.csv")
tab = tab.rename(columns={"PM2.5(μg/m³)": "pm", "US AQI": "aqi"})
ann = tab.dropna(subset=["pm"]).groupby(["地点", "年"]).agg(pm=("pm", "mean"), n=("月", "count")).reset_index()
ann = ann[ann.n >= 10]
news = pd.read_csv(f"{D}/haze_news_by_year.csv", header=[0, 1], index_col=0)
cns, nyt = news["中国新闻网"], news["纽约时报"]
cns.index = cns.index.astype(int); nyt.index = nyt.index.astype(int)
rel = cns.reliable.astype(str) == "True"
PEAK = int(cns[rel].per10k.idxmax())

SIZES = {
    "L": dict(fig=(9.75, 4.5), title=15, sub=11, tick=11, lab=11.5, note=8, ann=10, cell=8, rot=0,
              wt=60, ws=95, wn=150, xt=0.30),
    "P": dict(fig=(4.5, 9.75), title=14, sub=10.5, tick=10, lab=10.5, note=7.5, ann=9, cell=7, rot=90,
              wt=26, ws=31, wn=42, xt=0.50),
}
import textwrap
def wrap(txt, w):
    return "\n".join(textwrap.fill(line, w) if line else "" for line in txt.split("\n"))
def lh(fs, S, n):  # height of n lines in figure fraction
    return n * fs * 1.4 / 72 / S["fig"][1]

class Page:
    pass

def page(o, title, sub=None, note=SRC_PM, legend_rows=0, top_pad=0.0):
    S = SIZES[o]
    fig = plt.figure(figsize=S["fig"]); fig.patch.set_facecolor(SURF)
    x0 = 0.045 if o == "L" else 0.06
    y = 1 - 0.18 / S["fig"][1]
    if isinstance(title, tuple): title = title[0] if o == "L" else title[1]
    title = wrap(title, S["wt"]); nt = title.count("\n") + 1
    fig.text(x0, y, title, fontsize=S["title"], color=INK, va="top", ha="left", linespacing=1.25)
    y -= lh(S["title"], S, nt) + 0.08 / S["fig"][1]
    if sub:
        sub = wrap(sub, S["ws"]); ns = sub.count("\n") + 1
        fig.text(x0, y, sub, fontsize=S["sub"], color=INK2, va="top", ha="left", linespacing=1.35)
        y -= lh(S["sub"], S, ns)
    yb = 0.12 / S["fig"][1]
    if note:
        note = wrap(note, S["wn"]); nn = note.count("\n") + 1
        fig.text(x0, yb, note, fontsize=S["note"], color=MUTED, va="bottom", ha="left", linespacing=1.3)
        yb += lh(S["note"], S, nn)
    fig._legend_y = yb + 0.06 / S["fig"][1]
    yb += legend_rows * lh(S["note"] + 1, S, 1) + (0.08 / S["fig"][1] if legend_rows else 0)
    fig._top = y - (0.30 + top_pad) / S["fig"][1]
    fig._bottom = yb + S["xt"] / S["fig"][1]
    return fig, S

def axes_box(fig, o, left=None, right=None, **kw):
    l = left if left is not None else (0.07 if o == "L" else 0.14)
    r = right if right is not None else (0.86 if o == "L" else 0.80)
    return fig.add_axes([l, fig._bottom, r - l, fig._top - fig._bottom])

def year_axis(ax, S, o, xmin=2010, xmax=2027):
    ax.set_xlim(xmin - 0.1, xmax + 0.1)
    ax.set_xticks([y + 0.5 for y in range(xmin, xmax)])
    ax.set_xticklabels([str(y) for y in range(xmin, xmax)], fontsize=S["tick"] - (1 if o == "L" else 0),
                       rotation=90 if o == "P" else 0)
    ax.set_xticks(range(xmin, xmax + 1), minor=True)
    ax.tick_params(axis="x", which="major", length=0, pad=3); ax.tick_params(axis="x", which="minor", length=4)
    ax.tick_params(axis="y", labelsize=S["tick"])
    ax.grid(axis="x", which="minor", color=GRID, lw=0.6); ax.set_axisbelow(True)

def peak_band(ax, S, label=True, ytext=None):
    ax.axvspan(PEAK, PEAK + 1, color=RED, alpha=0.10, lw=0, zorder=0)
    if label:
        ax.text(PEAK + 0.5, ax.get_ylim()[1], f"雾霾新闻最多 {PEAK}", ha="center", va="bottom",
                fontsize=S["ann"], color="#a02020", zorder=5, clip_on=False)

def aqi_bands(ax, S, ymax, o):
    for (lo, hi, ilo, ihi), name in zip(BP, CAT):
        if lo > ymax: break
        if hi < ymax: ax.axhline(hi, color=GRID, lw=0.9, zorder=0)
        if (min(hi, ymax) - lo) >= ymax * 0.10:
            ax.text(1.015, (lo + min(hi, ymax)) / 2, f"AQI\n{ilo}–{ihi}\n{name}" if o == "P" else f"AQI {ilo}–{ihi}\n{name}",
                    transform=ax.get_yaxis_transform(), va="center", ha="left",
                    fontsize=S["note"] + (0.5 if o == "L" else 0), color=MUTED, linespacing=1.15)

def p_annual(pdf, o):
    fig, S = page(o, ("年均 PM2.5：北京·上海·武汉·广州·全国\n2010–2026（μg/m³，右侧为 US AQI 等级）",
                    "年均 PM2.5（μg/m³）\n北京·上海·武汉·广州·全国\n2010–2026，右侧为 US AQI 等级"))
    ax = axes_box(fig, o)
    for loc in LOCS:
        a = ann[ann["地点"] == loc]
        ax.plot(a["年"] + 0.5, a.pm, color=COLOR[loc], lw=2.2, ls=(0, (4, 1.6)) if loc == "全国城市均值" else "-",
                marker="o", ms=5 if o == "L" else 4, mec=SURF, mew=1.2, label=LABEL[loc], zorder=3)
    b = ann[ann["地点"] == "北京"].set_index("年")
    for y in [2010, 2013]:
        ax.annotate(f"{b.loc[y,'pm']:.0f}", (y + 0.5, b.loc[y, "pm"]), xytext=(0, 7), textcoords="offset points",
                    ha="center", fontsize=S["ann"], color=COLOR["北京"])
    ax.set_ylim(0, 115); aqi_bands(ax, S, 115, o); year_axis(ax, S, o)
    peak_band(ax, S)
    ax.set_ylabel("μg/m³", fontsize=S["lab"])
    ax.legend(loc="upper right", frameon=False, fontsize=S["tick"], bbox_to_anchor=(1.0, 0.9), handlelength=2)
    pdf.savefig(fig, facecolor=SURF); plt.close(fig)

def p_cns(pdf, o):
    fig, S = page(o, (f"雾霾新闻最多的年份：{PEAK}\n中国新闻网全部标题中含“雾霾/霾/PM2.5”的比例",
                    f"雾霾新闻最多的年份：{PEAK}\n中国新闻网全部标题中\n含“雾霾/霾/PM2.5”的比例"),
                  note="数据：逐日抓取中国新闻网滚动新闻全部标题（约497万条）按关键词计数，按每万条标题计。灰色=当年存档天数不足。2026年截至11月7日。")
    ax = axes_box(fig, o, right=0.97 if o == "L" else 0.96)
    x = cns.index + 0.5
    cols = [RED if y == PEAK else ("#2a78d6" if r else "#b9b8b2") for y, r in zip(cns.index, rel)]
    ax.bar(x, cns.per10k, width=0.72, color=cols, zorder=2)
    for xv, v, r in zip(x, cns.per10k, rel):
        ax.text(xv, v + 0.6, f"{v:.0f}" if v >= 10 else f"{v:.1f}", ha="center", va="bottom",
                fontsize=S["ann"] - (1.5 if o == "P" else 0), color=INK2)
    ax.set_ylabel("每万条标题中的条数", fontsize=S["lab"]); ax.set_ylim(0, 55)
    year_axis(ax, S, o); ax.grid(axis="y", color=GRID, lw=0.6)
    pdf.savefig(fig, facecolor=SURF); plt.close(fig)

def p_nyt(pdf, o):
    pk = int(nyt.hits.idxmax())
    fig, S = page(o, ("《纽约时报》中国雾霾报道篇数\n标题同时提到雾霾/空气污染与中国地名",
                    "《纽约时报》中国雾霾报道篇数\n标题同时提到雾霾/空气污染\n与中国地名"),
                  sub=f"最多 {pk} 年 {int(nyt.hits.max())} 篇，{PEAK} 年 {int(nyt.loc[PEAK,'hits'])} 篇（样本小，作国际视角参考）",
                  note="数据：逐日抓取《纽约时报》站点地图全部标题后按关键词计数。2026年截至11月7日。")
    ax = axes_box(fig, o, right=0.97 if o == "L" else 0.96)
    x = nyt.index + 0.5
    ax.bar(x, nyt.hits, width=0.72, color=[RED if y == pk else "#eb6834" for y in nyt.index], zorder=2)
    for xv, v in zip(x, nyt.hits):
        ax.text(xv, v + 0.3, f"{int(v)}", ha="center", va="bottom", fontsize=S["ann"], color=INK2)
    ax.set_ylabel("篇数", fontsize=S["lab"]); ax.set_ylim(0, 26)
    year_axis(ax, S, o); ax.grid(axis="y", color=GRID, lw=0.6); peak_band(ax, S, label=False)
    pdf.savefig(fig, facecolor=SURF); plt.close(fig)

def p_monthly(pdf, o, loc):
    t = tab[tab["地点"] == loc].copy(); t["x"] = t["年"] + (t["月"] - 0.5) / 12
    mx = t.loc[t.pm.idxmax()]
    name = "全国（所有城市均值）" if loc == "全国城市均值" else loc
    fig, S = page(o, (f"{name} 逐月 PM2.5（μg/m³）2010–2026", f"{name}\n逐月 PM2.5（μg/m³）2010–2026"),
                  sub=f"最高月 {int(mx['年'])}年{int(mx['月'])}月：{mx.pm:.0f} μg/m³（US AQI {int(mx.aqi)}）\n"
                      f"虚线=美国使领馆单站；实线=中国国控站全市均值；黑横线=年均值")
    ax = axes_box(fig, o)
    ymax = 260 if loc == "北京" else 150
    c = COLOR[loc]
    us = t[t["数据来源"].astype(str).str.startswith("美国")]; cn = t[t["数据来源"].astype(str).str.startswith("中国")]
    ax.plot(us.x, us.pm, color=c, lw=1.6, ls=(0, (3, 1.4)))
    ax.plot(cn.x, cn.pm, color=c, lw=1.6)
    for _, r in ann[ann["地点"] == loc].iterrows():
        ax.hlines(r.pm, r["年"], r["年"] + 1, color=INK, lw=1.4, alpha=0.65)
    ax.set_ylim(0, ymax); aqi_bands(ax, S, ymax, o); year_axis(ax, S, o); peak_band(ax, S)
    if loc in ("武汉", "全国城市均值"):
        ax.text(2012.2, ymax * 0.45, "2014年5月前\n无公开逐时\n监测数据", ha="center", va="center", fontsize=S["ann"], color=MUTED)
    ax.set_ylabel("μg/m³", fontsize=S["lab"])
    pdf.savefig(fig, facecolor=SURF); plt.close(fig)

def p_heat(pdf, o, loc):
    name = "全国（所有城市均值）" if loc == "全国城市均值" else loc
    fig, S = page(o, (f"{name} 逐月 US AQI 热力图 2010–2026", f"{name}\n逐月 US AQI 热力图 2010–2026"),
                  sub=f"格内数字=月均 PM2.5 换算的 US AQI；黑框={PEAK}年（雾霾新闻最多）",
                  note=SRC_PM + " 颜色为美国EPA官方AQI配色。", legend_rows=1 if o == "L" else 2)
    ax = axes_box(fig, o, left=0.08 if o == "L" else 0.12, right=0.98)
    M = tab[tab["地点"] == loc].pivot(index="月", columns="年", values="aqi").reindex(index=range(1, 13), columns=YEARS)
    cmap = ListedColormap(AQI_COLORS); norm = BoundaryNorm([0, 50.5, 100.5, 150.5, 200.5, 300.5, 500], 6)
    ax.pcolormesh(np.arange(len(YEARS) + 1), np.arange(13) + 0.5, np.ma.masked_invalid(M.values.astype(float)),
                  cmap=cmap, norm=norm, edgecolors=SURF, linewidth=0.8)
    for i, m in enumerate(range(1, 13)):
        for j, y in enumerate(YEARS):
            v = M.loc[m, y]
            if not pd.isna(v):
                ax.text(j + 0.5, m, f"{int(v)}", ha="center", va="center", fontsize=S["cell"],
                        color="white" if v > 150 else "#222")
    ax.set_xlim(0, len(YEARS)); ax.set_ylim(12.5, 0.5)
    ax.set_xticks(np.arange(len(YEARS)) + 0.5)
    ax.set_xticklabels(YEARS, fontsize=S["tick"], rotation=90 if o == "P" else 0)
    if o == "L": ax.set_xticklabels(YEARS, fontsize=S["tick"] - 1.5)
    ax.set_yticks(range(1, 13)); ax.set_yticklabels([f"{m}月" for m in range(1, 13)], fontsize=S["tick"])
    ax.tick_params(length=0)
    for s in ax.spines.values(): s.set_visible(False)
    j = YEARS.index(PEAK)
    ax.add_patch(plt.Rectangle((j, 0.5), 1, 12, fill=False, ec=INK, lw=2.2, zorder=5))
    if M.loc[:, 2010:2013].isna().all().all():
        ax.text(2, 6.5, "2014年5月前\n无公开\n逐时数据", ha="center", va="center", fontsize=S["ann"], color=MUTED)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in AQI_COLORS]
    labels = [f"{a}–{b} {n}" for (_, _, a, b), n in zip(BP, CAT)]
    fig.legend(handles, labels, loc="lower left", bbox_to_anchor=(0.03 if o == "L" else 0.04, fig._legend_y),
               ncol=6 if o == "L" else 3, frameon=False, fontsize=S["note"] + 0.5, handlelength=1.2, columnspacing=1)
    pdf.savefig(fig, facecolor=SURF); plt.close(fig)

def p_manchester(pdf, o):
    fig, S = page(o, "曼彻斯特今早不只是雾：\nPM2.5 是上海的 6.6 倍",
                  sub="PM2.5 是 WHO 24 小时指导值的 4 倍\n这个浓度 ≈ 北京 2017 年全年平均（57.9 μg/m³）",
                  note="数据：WAQI/aqicn 监测站读数（截图），2026年11月8日；北京年均值来自国控站数据计算。瞬时读数与年均值仅作量级参考。")
    fig._bottom -= (0.0 if o == "L" else 0.0)
    ax = axes_box(fig, o, left=0.06, right=0.96 if o == "L" else 0.94)
    names = ["曼彻斯特  11/8 07:00", "上海  11/8 15:00"] if o == "L" else ["曼彻斯特\n11/8 07:00", "上海\n11/8 15:00"]
    ax.bar(names, [59.3, 9], width=0.5, color=[RED, "#2a78d6"], zorder=2)
    ax.text(0, 61, "59.3 μg/m³\nUS AQI 154 不健康", ha="center", va="bottom", fontsize=S["sub"] + 1, color=INK)
    ax.text(1, 20, "9 μg/m³\nUS AQI 50 优", ha="center", va="bottom", fontsize=S["sub"] + 1, color=INK)
    ax.axhline(15, color=INK2, lw=1.2, ls="--", zorder=1)
    ax.text(0.5, 15.8, "WHO 24小时指导值 15", ha="center", va="bottom", fontsize=S["note"] + 1, color=INK2)
    ax.set_ylim(0, 78); ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", labelsize=S["lab"], length=0)
    pdf.savefig(fig, facecolor=SURF); plt.close(fig)

for o, fname in [("L", "横屏版")]:
    with PdfPages(f"{OUT}/中国空气质量2010-2026_{fname}.pdf") as pdf:
        p_annual(pdf, o); p_cns(pdf, o); p_nyt(pdf, o)
        for loc in LOCS: p_monthly(pdf, o, loc)
        for loc in LOCS: p_heat(pdf, o, loc)
        p_manchester(pdf, o)
print("ok", PEAK)
