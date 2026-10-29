#!/usr/bin/env python3
"""Generate The Promised Atlas three-page policy brief."""
import json
import math
from pathlib import Path

from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs/the-promised-atlas-research-brief.pdf"
summary = json.loads((ROOT / "outputs/analysis_summary.json").read_text(encoding="utf-8"))

W, H = A4
M = 42
NIGHT = HexColor("#102934")
INK = HexColor("#152129")
MUTED = HexColor("#5D696E")
PAPER = HexColor("#F3F0E8")
WHITE = HexColor("#FFFDF7")
YELLOW = HexColor("#EDC65D")
GREEN = HexColor("#237A5A")
TEAL = HexColor("#1B7682")
AMBER = HexColor("#B77D22")
BLUEGRAY = HexColor("#647789")
RED = HexColor("#C8553D")
LINE = HexColor("#CDD1CA")


def first_existing(*candidates):
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return str(path)
    raise FileNotFoundError(f"No CJK font found in: {candidates}")


regular_font = first_existing(
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
)
bold_font = first_existing(
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Bold.otf",
)
pdfmetrics.registerFont(TTFont("Heiti", regular_font))
pdfmetrics.registerFont(TTFont("HeitiMed", bold_font))


def set_font(c, size, bold=False, color=INK):
    c.setFont("HeitiMed" if bold else "Heiti", size)
    c.setFillColor(color)


def wrap(text, max_width, size, bold=False):
    font = "HeitiMed" if bold else "Heiti"
    lines, line = [], ""
    for char in text:
        candidate = line + char
        if line and pdfmetrics.stringWidth(candidate, font, size) > max_width:
            lines.append(line)
            line = char
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def paragraph(c, text, x, y, width, size=9.3, leading=15, color=MUTED, bold=False, max_lines=None):
    lines = wrap(text, width, size, bold)
    if max_lines:
        lines = lines[:max_lines]
    set_font(c, size, bold, color)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def footer(c, page):
    c.setStrokeColor(LINE)
    c.line(M, 27, W - M, 27)
    set_font(c, 7.2, False, MUTED)
    c.drawString(M, 15, "The Promised Atlas / 签约之后 · 数据截止 2025-12-31 · 状态审定 2026-10-29")
    c.drawRightString(W - M, 15, f"{page} / 3")


def metric(c, x, y, value, label, color=YELLOW):
    set_font(c, 27, True, color)
    c.drawString(x, y, value)
    set_font(c, 7.6, False, Color(0.77, 0.84, 0.82))
    c.drawString(x, y - 17, label)


c = canvas.Canvas(str(OUT), pagesize=A4)
c.setTitle("The Promised Atlas：南阳招商项目兑现地图")
c.setAuthor("The Promised Atlas")

# Page 1: question, scale, and research design.
c.setFillColor(NIGHT)
c.rect(0, 0, W, H, fill=1, stroke=0)
c.setStrokeColor(Color(0.93, 0.78, 0.36, alpha=0.38))
c.setLineWidth(0.7)
for radius in (150, 195, 240):
    c.circle(W - 48, H - 260, radius, fill=0, stroke=1)
set_font(c, 8.5, True, YELLOW)
c.drawString(M, H - 58, "THE PROMISED ATLAS / 签约之后")
set_font(c, 31, True, WHITE)
c.drawString(M, H - 112, "签约之后，项目去了哪里？")
y = paragraph(
    c,
    "我把政府公开宣布的招商项目逐个列出来，几年后再查一遍。不是统计掌声，而是统计还能被公众核对的厂房、施工和投产记录。",
    M, H - 148, 465, 12.5, 20, Color(0.82, 0.87, 0.85), False
)
c.setStrokeColor(Color(1, 1, 1, alpha=0.18))
c.line(M, y - 12, W - M, y - 12)
metric(c, M, y - 58, "426", "不重复主要报道宣布的项目名额")
metric(c, M + 127, y - 58, "62", "同篇报道明确点名的项目")
metric(c, M + 254, y - 58, "80", "逐项追踪项目")
metric(c, M + 381, y - 58, "14", "留下强物理里程碑")

c.setFillColor(WHITE)
c.roundRect(M, 98, W - 2 * M, 310, 2, fill=1, stroke=0)
set_font(c, 9, True, TEAL)
c.drawString(M + 20, 378, "研究设计")
set_font(c, 18, True, INK)
c.drawString(M + 20, 346, "三层结构，避免让14个案例承担整座城市的结论")
layers = [
    ("01", "事件透明度", "24篇官方事件报道；21篇不重复主要事件。统计报道宣布多少项目名额，以及同篇报道真正公开了多少名称。"),
    ("02", "80项明确项目", "南阳各县区2019-2022年公开点名项目。统一检索投产、施工、审批和后续推进记录。"),
    ("03", "淅川14项深审", "同一官方队列逐项核查。用更严格的项目级物理证据检验广域结果是否只是检索深度造成。"),
]
top = 303
for idx, (num, title, body) in enumerate(layers):
    yy = top - idx * 78
    set_font(c, 10, True, RED)
    c.drawString(M + 20, yy, num)
    set_font(c, 12, True, INK)
    c.drawString(M + 58, yy, title)
    paragraph(c, body, M + 58, yy - 19, W - 2 * M - 88, 8.8, 13.5, MUTED)
c.setFillColor(YELLOW)
c.rect(0, 48, W, 28, fill=1, stroke=0)
set_font(c, 9.4, True, INK)
c.drawString(M, 57, "一句话：一场签约会结束以后，承诺去了哪里，等待它的人付出了什么代价？")
footer(c, 1)
c.showPage()

# Page 2: findings and model.
c.setFillColor(PAPER)
c.rect(0, 0, W, H, fill=1, stroke=0)
set_font(c, 8.5, True, TEAL)
c.drawString(M, H - 48, "RESULTS")
set_font(c, 20.5, True, INK)
c.drawString(M, H - 87, "项目先在报道里消失，然后才可能在土地上消失。")

cards = [
    ("14.6%", "同篇报道点名率", "62 / 426 个项目名额"),
    ("17.5%", "强物理里程碑率", "14 / 80 项；95% CI 10.7%-27.3%"),
    ("72.5%", "未定位项目专属里程碑", "58 / 80 项"),
]
card_w = (W - 2 * M - 20) / 3
for i, (value, label, note) in enumerate(cards):
    x = M + i * (card_w + 10)
    c.setFillColor(WHITE)
    c.rect(x, H - 216, card_w, 94, fill=1, stroke=0)
    set_font(c, 21, True, RED)
    c.drawString(x + 12, H - 155, value)
    set_font(c, 9.2, True, INK)
    c.drawString(x + 12, H - 178, label)
    set_font(c, 7.4, False, MUTED)
    c.drawString(x + 12, H - 196, note)

set_font(c, 11.5, True, INK)
c.drawString(M, H - 252, "80项项目的最强公开后续证据")
counts = [
    ("建成 / 试产", 5, GREEN),
    ("物理建设进度", 9, TEAL),
    ("仅手续进度", 3, AMBER),
    ("仅后续提及", 5, BLUEGRAY),
    ("未定位项目专属里程碑", 58, RED),
]
bar_x, bar_y, bar_w, bar_h = M, H - 288, W - 2 * M, 22
offset = 0
for label, count, color in counts:
    width = bar_w * count / 80
    c.setFillColor(color)
    c.rect(bar_x + offset, bar_y, width, bar_h, fill=1, stroke=0)
    offset += width
legend_y = bar_y - 23
lx = M
for label, count, color in counts:
    c.setFillColor(color)
    c.circle(lx + 4, legend_y + 3, 3, fill=1, stroke=0)
    set_font(c, 7.2, False, MUTED)
    c.drawString(lx + 11, legend_y, f"{label} {count}")
    lx += 96 if label != "未定位项目专属里程碑" else 135

set_font(c, 14, True, INK)
c.drawString(M, H - 365, "名企和大场面没有预测兑现")
paragraph(
    c,
    "在核查方法一致的66项广域队列中，带有上市公司、央企或全国品牌信号的项目，强物理里程碑率为18.2%；其他或未披露企业为16.4%。逻辑回归同时放入企业名气信号和活动公布项目规模，两者的95%置信区间都跨过1。",
    M, H - 389, W - 2 * M, 9.4, 15, MUTED
)

model_rows = summary["surface_signals"]["model"]
plot_x, plot_w = M + 220, W - M - (M + 220)
plot_top = H - 480
set_font(c, 8.2, True, INK)
c.drawString(M, plot_top + 9, "表面信号")
c.drawRightString(W - M, plot_top + 9, "优势比 OR [95% CI]")
for i, row in enumerate(model_rows):
    yy = plot_top - 52 * i
    set_font(c, 8.5, False, INK)
    label = "知名企业信号" if row["term"] == "recognizable_company" else "活动规模（log项目数，每1 SD）"
    c.drawString(M, yy - 9, label)
    min_log, max_log = math.log(0.12), math.log(8.2)
    pos = lambda value: plot_x + plot_w * (math.log(value) - min_log) / (max_log - min_log)
    c.setStrokeColor(LINE)
    c.line(plot_x, yy, plot_x + plot_w, yy)
    c.setStrokeColor(INK)
    c.line(pos(1), yy - 11, pos(1), yy + 11)
    c.setStrokeColor(BLUEGRAY)
    c.setLineWidth(2)
    c.line(max(plot_x, pos(row["ci95_low"])), yy, min(plot_x + plot_w, pos(row["ci95_high"])), yy)
    c.setFillColor(RED)
    c.circle(pos(row["odds_ratio"]), yy, 4, fill=1, stroke=0)
    set_font(c, 7.8, True, INK)
    c.drawRightString(W - M, yy - 9, f"{row['odds_ratio']:.2f} [{row['ci95_low']:.2f}, {row['ci95_high']:.2f}]")
set_font(c, 7, False, MUTED)
c.drawString(plot_x, plot_top - 76, "0.12")
c.drawCentredString(pos(1), plot_top - 76, "1")
c.drawRightString(plot_x + plot_w, plot_top - 76, "8.2")

c.setFillColor(WHITE)
c.rect(M, 76, W - 2 * M, 142, fill=1, stroke=0)
set_font(c, 10.5, True, TEAL)
c.drawString(M + 16, 194, "结论边界写清楚，结论本身写直接")
paragraph(c, "我们得出的结果是：在这组南阳公开项目中，知名企业信号和更大规模的签约活动都没有显示出更高的物理兑现率。项目金额只有11/66项可比，因此没有强行拟合金额模型。", M + 16, 170, W - 2 * M - 32, 9.3, 15, INK)
paragraph(c, "“未定位后续里程碑”不等于证明项目不存在；它准确记录了居民、记者或招商部门之外的人能否从公开记录继续追踪这一承诺。", M + 16, 116, W - 2 * M - 32, 8.4, 13.5, MUTED)
footer(c, 2)
c.showPage()

# Page 3: due diligence protocol.
c.setFillColor(WHITE)
c.rect(0, 0, W, H, fill=1, stroke=0)
set_font(c, 8.5, True, TEAL)
c.drawString(M, H - 48, "IF I RAN THE INVESTMENT OFFICE")
set_font(c, 20.5, True, INK)
c.drawString(M, H - 87, "把成功单位从“签了多少”改成“兑现到哪一步”。")
paragraph(c, "签约不是结案，而是审计链的第一行。每个项目在签约前形成一张公开尽调卡，签约后按同一组物理里程碑更新。", M, H - 116, W - 2 * M, 10.2, 16, MUTED)

checks = [
    ("1", "土地", "宗地号、权利人、规划用途、可交付时间、红线图。没有明确地块的项目，不计为已落地。"),
    ("2", "审批路径", "环评、能评、安全、规划和施工许可分别由谁负责；列出最晚完成日和前置条件。"),
    ("3", "本地经营主体", "项目公司注册、实缴资本、母公司担保、资金来源和关键设备采购。名企名称不能替代资金证明。"),
    ("4", "物理里程碑", "开工、基础、钢结构、设备进场、试产、验收、用电与纳税。每一步都要有日期、证据和下一节点。"),
]
start_y = H - 182
row_h = 87
for i, (num, title, body) in enumerate(checks):
    y0 = start_y - i * row_h
    c.setFillColor(PAPER if i % 2 == 0 else HexColor("#ECE8DE"))
    c.rect(M, y0 - 62, W - 2 * M, 72, fill=1, stroke=0)
    set_font(c, 20, True, RED)
    c.drawString(M + 14, y0 - 22, num)
    set_font(c, 12.5, True, INK)
    c.drawString(M + 54, y0 - 10, title)
    paragraph(c, body, M + 54, y0 - 30, W - 2 * M - 70, 8.7, 14, MUTED)

box_y = 183
c.setFillColor(NIGHT)
c.rect(M, box_y, W - 2 * M, 150, fill=1, stroke=0)
set_font(c, 10.5, True, YELLOW)
c.drawString(M + 16, box_y + 126, "触发加强尽调的信号")
warnings = [
    "大额标题金额，但没有宗地、项目公司或资金来源。",
    "只在大型集中签约中出现，后续报道仍只有“推进、协调、观摩”。",
    "同一项目反复签约，名称、投资额或主体发生变化，却没有解释。",
    "知名母公司站台，但本地实体、担保责任和退出机制不清。",
]
for i, warning in enumerate(warnings):
    yy = box_y + 98 - i * 22
    c.setFillColor(RED)
    c.circle(M + 20, yy + 3, 2.8, fill=1, stroke=0)
    set_font(c, 8.6, False, WHITE)
    c.drawString(M + 31, yy, warning)

set_font(c, 11.5, True, INK)
c.drawString(M, 150, "政策动作：用里程碑分批释放土地、补贴和荣誉")
paragraph(c, "土地优惠、财政奖励和宣传口径与真实节点挂钩；设置履约保证金和自动回收条款；公开项目下一节点、责任人和逾期原因。这样做不是降低招商速度，而是把失信成本从居民和财政转回签约双方。", M, 128, W - 2 * M, 9.2, 15, MUTED)
set_font(c, 9, True, RED)
c.drawString(M, 67, "人文落点")
paragraph(c, "消失的不是一座抽象工厂。它可能是一块被预留的土地、一笔被许诺的就业、一套围绕项目安排的人生计划。", M + 58, 67, W - 2 * M - 58, 9.2, 15, INK)
footer(c, 3)
c.save()
print(OUT)
