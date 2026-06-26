"""共用報告渲染器測試（stdlib unittest，零相依）。"""

import json
import tempfile
import unittest
from pathlib import Path

from peakstar_oss_common import brand, render
from peakstar_oss_common.model import Cta, Dimension, Finding, ReportDoc, Stat


def _doc(**over):
    base = dict(
        tool="exampletool",
        version="1.2.3",
        lang="zh",
        title="範例健檢報告",
        subtitle="一句副標",
        total_score=72.0,
        light_word="黃燈",
        score_caption="總分",
        dimensions=[
            Dimension("a", "維度甲", "說明甲", 90.0),
            Dimension("b", "維度乙", "說明乙", 40.0),
        ],
        dimensions_heading="維度",
        findings=[Finding("high", "這是一條高風險發現"), Finding("low", "這是一條低風險發現")],
        findings_heading="重點發現",
        no_findings_text="未發現重大紅旗。",
        means_heading="這代表什麼",
        cta=Cta("下一步", "建議文案", "了解更多", "https://www.peakstargroup.com/?ref=exampletool"),
        disclaimer="本報告僅供參考，不構成保證。",
        about="Peakstar 一行簡介。",
        meta=[("標的", "/some/path"), ("時間", "2026-06-26 10:00:00")],
        means_stat=Stat("10%", "預期失敗率"),
        means_rows=[("工作量級", "中")],
    )
    base.update(over)
    return ReportDoc(**base)


class TestLight(unittest.TestCase):
    def test_default_thresholds(self):
        self.assertEqual(brand.light_for(85), "green")
        self.assertEqual(brand.light_for(60), "yellow")
        self.assertEqual(brand.light_for(20), "red")

    def test_override_thresholds(self):
        # 安全工具採較嚴門檻：85 / 60
        self.assertEqual(brand.light_for(82, green_min=85, yellow_min=60), "yellow")
        self.assertEqual(brand.light_for(55, green_min=85, yellow_min=60), "red")


class TestHtml(unittest.TestCase):
    def setUp(self):
        self.html = render.to_html(_doc())

    def test_no_em_dash(self):
        self.assertNotIn("—", self.html)   # em-dash
        self.assertNotIn("--", self.html)

    def test_has_core_pieces(self):
        self.assertIn("範例健檢報告", self.html)
        self.assertIn("72", self.html)
        self.assertIn("維度甲", self.html)
        self.assertIn("這是一條高風險發現", self.html)
        self.assertIn("https://www.peakstargroup.com/?ref=exampletool", self.html)

    def test_brand_color_present(self):
        self.assertIn("#0D1F3C", self.html)

    def test_no_findings_fallback(self):
        html = render.to_html(_doc(findings=[]))
        self.assertIn("未發現重大紅旗。", html)

    def test_means_optional(self):
        html = render.to_html(_doc(means_stat=None, means_rows=[]))
        self.assertNotIn('class="means"', html)


class TestJson(unittest.TestCase):
    def test_structure(self):
        data = json.loads(render.to_json(_doc()))
        self.assertEqual(data["tool"], "exampletool")
        self.assertEqual(data["light"], "yellow")
        self.assertEqual(len(data["dimensions"]), 2)
        self.assertEqual(data["consult_url"], "https://www.peakstargroup.com/?ref=exampletool")
        self.assertEqual(data["means"]["stat"]["value"], "10%")


class TestTerminalAndWrite(unittest.TestCase):
    def test_terminal_summary(self):
        out = render.terminal_summary(_doc())
        self.assertIn("黃燈", out)
        self.assertIn("維度甲", out)

    def test_write_reports(self):
        with tempfile.TemporaryDirectory() as d:
            written = render.write_reports(_doc(), Path(d), ["html", "json"])
            self.assertEqual(len(written), 2)
            self.assertTrue((Path(d) / "report.html").exists())
            self.assertTrue((Path(d) / "report.json").exists())


if __name__ == "__main__":
    unittest.main()
