import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fm.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
plt.rcParams.update({"font.family": "WenQuanYi Zen Hei", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.spines.left": False, "axes.edgecolor": "#8a8984", "pdf.fonttype": 42})
INK, INK2, MUTED, SURF = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb"
fig, ax = plt.subplots(figsize=(6, 7.5)); fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
names = ["曼彻斯特\n11/8 07:00", "上海\n11/8 15:00"]; vals = [59.3, 9]
ax.bar(names, vals, width=0.55, color=["#d03b3b", "#2a78d6"], zorder=2)
ax.text(0, 59.3 + 1.5, "59.3 μg/m³\nUS AQI 154 不健康", ha="center", va="bottom", fontsize=13, color=INK)
ax.text(1, 21, "9 μg/m³\nUS AQI 50 优", ha="center", va="bottom", fontsize=13, color=INK)
ax.axhline(15, color=INK2, lw=1.2, ls="--", zorder=1)
ax.text(0.5, 15.8, "WHO 24小时指导值 15", ha="center", va="bottom", fontsize=10, color=INK2)
ax.set_ylim(0, 72); ax.set_yticks([]); ax.tick_params(axis="x", labelsize=13, length=0)
fig.suptitle("曼彻斯特今早不只是雾：PM2.5 是上海的 6.6 倍", x=0.05, ha="left", fontsize=15, color=INK, y=0.97)
fig.text(0.05, 0.895, "PM2.5 是 WHO 24 小时指导值的 4 倍\n这个浓度 ≈ 北京 2017 年全年平均（57.9 μg/m³）", fontsize=11.5, color=INK2, va="top")
fig.text(0.05, 0.02, "数据：WAQI/aqicn 监测站读数（截图）；北京年均值来自中国国控站数据计算。\n瞬时读数与年均值仅作量级参考。", fontsize=8.5, color=MUTED)
fig.tight_layout(rect=(0, 0.07, 1, 0.8))
fig.savefig("out/deliver/fig4_曼彻斯特vs上海.pdf", facecolor=SURF); fig.savefig("out/曼彻斯特vs上海_PM25.png", dpi=200, facecolor=SURF)
