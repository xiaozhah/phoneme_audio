# 中国 · 北京 · 上海 · 武汉 · 广州 逐月 PM2.5 / US AQI（2010–2026）与雾霾新闻年份

## 文件

| 文件 | 内容 |
|---|---|
| `data/china_pm25_monthly_2010_2026.xlsx` | 逐月 PM2.5（μg/m³）与 US AQI，含长表、每地逐年×逐月透视表、年均值、两数据源重叠期对比、雾霾新闻年度统计 |
| `data/china_pm25_monthly_2010_2026.csv` | 同上长表（UTF-8 BOM，可直接用 Excel 打开） |
| `data/haze_news_by_year.csv` | 每年雾霾新闻数量（中国新闻网 / 纽约时报） |
| `data/cns_haze_headlines.csv`, `data/nyt_haze_headlines.csv` | 计入统计的每一条新闻标题与链接（可逐条核查） |
| `figures/fig1_年均PM25与雾霾新闻.png` | 年均 PM2.5 趋势 + 两个新闻量面板，标出新闻最多的年份 |
| `figures/fig2_逐月PM25.png` | 五个地点逐月曲线，右侧标注 US AQI 等级 |
| `figures/fig3_逐月USAQI热力图.png` | 年 × 月 US AQI 热力图（EPA 标准配色） |
| `scripts/` | 全部抓取与计算代码，可完整复现 |

## 数据来源

**PM2.5 浓度**

1. **2010-01 至 2014-05：美国驻华使领馆监测点逐时数据**（北京使馆、上海/广州总领馆；美国国务院 StateAir 项目），
   使用 UCI 机器学习库整理版 *PM2.5 Data of Five Chinese Cities*（2010–2015）。上海自 2011-12、广州自 2011-11 起才有数据。
2. **2014-06 至 2026-10：中国环境监测总站全国城市空气质量实时发布平台**的城市逐时均值，
   来自 quotsoft.net（王晓磊）每日存档 `china_cities_YYYYMMDD.csv`。“全国”是当天所有有数据城市日均值的算术平均
   （2014 年约 190 个城市，2015 年起约 360 个）。
3. **武汉和全国在 2014-05 之前没有可公开下载的逐时 PM2.5 数据**（中国 2013 年才开始在 74 个城市发布 PM2.5，可下载存档从 2014-05-13 开始），
   这些格子留空，没有插补或估算。

**重叠期校验（2014-06 至 2015-12，19 个月）**：使领馆单站与国控站全市均值的月均值相关系数为北京 0.97、上海 0.96、广州 0.80，
均值相差在 3 μg/m³ 以内，所以两段数据可以拼接。

**口径**：日均值要求当天至少 18 个有效小时，月均值要求当月至少 15 个有效日，年均值要求至少 10 个有效月。
2026 年只到 10 月（11 月数据不全，未计入）。
本数据算出的 2025 年全国均值为 29.8 μg/m³，生态环境部公布的是 28 μg/m³。官方值扣除了沙尘天气，城市口径也不同（339 个地级及以上城市），所以官方值偏低 1–2 μg/m³ 属于正常。

**US AQI**：按美国 EPA 2024 年修订的 PM2.5 分级（0–9.0 / 9.1–35.4 / 35.5–55.4 / 55.5–125.4 / 125.5–225.4 / 225.5+）换算。
注意：AQI 的正式定义针对 24 小时均值，这里是把月均（或年均）浓度换算成对应的 AQI，表示这段时间平均处于哪个等级。

**雾霾新闻量（“雾霾最集中/报道最多的年份”）**

逐日抓取两个按日期完整存档的新闻目录，统计每一条标题：

- **中国新闻网（中新社）滚动新闻**，`chinanews.com.cn/scroll-news/YYYY/MMDD/news.shtml`：
  标题含“雾霾 / 灰霾 / 霾 / PM2.5”的计为一条（排除比喻用法“阴霾”，以及多指东南亚火灾的“烟霾”；同日同标题去重）。
  各年存档页数和总发稿量差别很大，所以按 **每万条标题中雾霾相关标题条数** 来比较各年。
- **《纽约时报》站点地图**，`nytimes.com/sitemap/YYYY/MM/DD/`：
  标题或链接同时提到空气污染类词（smog、haze、air pollution、air quality、PM2.5 等）和中国地名（China、Beijing、Shanghai 等）的文章数。

可以复核的文献旁证：He, Zhang & Chen (2020), *Sustainability* 12(1):386，用 Factiva 统计了《中国日报》2000–2018 年的雾霾报道，
峰值也在 2013 年（130 篇）。

## 复现

```bash
mkdir -p work/out work/dl/uci
python3 scripts/fetch_cnemc.py work/out/cnemc_daily.csv  # ~4,560 天，城市日均
python3 scripts/fetch_news.py cns work/out               # 中国新闻网逐日标题
python3 scripts/fetch_news.py nyt work/out               # 纽约时报逐日标题
# UCI 数据：https://archive.ics.uci.edu/dataset/394 下载，用 unar 解压到 work/dl/uci/（得到 FiveCitiePMData/）
python3 scripts/build.py work out
```
