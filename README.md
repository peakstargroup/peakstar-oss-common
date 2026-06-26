# peakstar-oss-common

Peakstar 開源工具組（[DataReady](https://github.com/peakstargroup/dataready-checker)、TrustLens、MCPGuard）的共用底座：一套品牌一致的報告產生器與隱私優先的遙測模組。

`Python 3.11+` ｜ `MIT License` ｜ `0 dependencies`（純標準庫）

## 它提供什麼

- **共用報告外觀**：把工具算好的結果（`ReportDoc`）渲染成自包含 HTML（內嵌 CSS、可離線開、可列印成 PDF）、結構化 JSON、與終端摘要。套 Peakstar 品牌色、不使用 em-dash。
- **燈號邏輯**：`light_for(score, green_min, yellow_min)`，門檻可由各工具覆寫（例如安全工具採較嚴門檻）。
- **隱私優先的遙測**：預設關閉、僅 opt-in、只記匿名事件計數，永不外送任何內容。

## 設計原則

common 對任何工具的領域邏輯一無所知。各工具自行算分、決定維度與 findings、把所有「已在地化」的字串塞進 `ReportDoc`，再交給 `render` 畫。這樣同一套報告外觀就能服務三個工具。

```python
from peakstar_oss_common import render
from peakstar_oss_common.model import Cta, Dimension, Finding, ReportDoc, Stat

doc = ReportDoc(
    tool="dataready", version="1.0.0", lang="zh",
    title="資料準備度健檢報告", subtitle="...",
    total_score=72.0, light_word="黃燈", score_caption="資料準備度總分",
    dimensions=[Dimension("extractability", "可讀取性", "...", 88.0)],
    dimensions_heading="六大維度",
    findings=[Finding("high", "...")], findings_heading="重點發現",
    no_findings_text="未發現重大紅旗。",
    means_heading="這代表什麼", means_stat=Stat("10%", "預期失敗率"),
    cta=Cta("下一步", "...", "了解更多", "https://www.peakstargroup.com/?ref=dataready"),
    disclaimer="...", about="Peakstar ...",
)
html = render.to_html(doc)
```

## 散佈方式：vendoring

為維持各工具「本身零相依」的品牌主張，工具不以 PyPI 相依此套件，而是把它**複製進自己的 package**（見各工具的 `_vendor/`）。本倉庫為單一真相來源；更新後同步到各工具。

## 開發與測試

```bash
py -m unittest discover -s tests -t .
```

## 授權

MIT License。見 [LICENSE](LICENSE)。
