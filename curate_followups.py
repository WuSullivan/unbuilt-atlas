#!/usr/bin/env python3
"""Apply human-reviewed follow-up decisions to the 80-project cohort.

Search results remain a candidate ledger. This file is the auditable decision
layer: every non-default status has a dated source and a short matching reason.
"""
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data/nanyang_projects.csv"
REVIEWED_ON = "2026-10-29"


# status, date, primary URL, secondary URL, grade, reason
DECISIONS = {
    "N002": ("later_mention_only", "2024-08-09", "https://hnjs.henan.gov.cn/2024/08-09/3033866.html", "", "C", "省住建部门清单再次出现‘卧龙牧原农牧装备研发生产项目’，但该记录是配套保租房信息，不足以证明签约项目已投产。"),
    "N004": ("administrative_only", "2025-03-04", "https://rensheju.nanyang.gov.cn/2025/03-04/944522.html", "", "C", "市人社规划继续提出建设综合性人力资源产业园，属于规划层后续，未形成项目专属物理里程碑。"),
    "N007": ("physical_progress", "2023-08-11", "https://m.sohu.com/a/710937378_121123800/", "https://www.fangcheng.gov.cn/2024/11-15/801999.html", "A", "后续报道明确称奇瑞商用车项目一期于2023年7月开工；方城县政府2024年报道再次将其列为已落地项目。"),
    "N009": ("built", "2023-01-31", "https://m.henan.gov.cn/2023/01-31/2681311.html", "", "A", "河南省政府转载的南阳投产报道将特钢连铸连轧绿色生产线列入集中投产项目。"),
    "N010": ("built", "2023-11-21", "https://oss.nanyang.gov.cn/wcm.files/upload/CMSnygx/202311/202311211101010.pdf", "", "A", "《南阳市光电产业振兴三年行动计划》项目清单称一期生产线已建成投产，可年产1.5亿件压型光学材料产品。"),
    "N011": ("administrative_only", "2022-08-14", "http://m.163.com/dy/article/HEO296EH0550BXTE.html", "", "C", "后续记录称有关部门协助办理项目公司注册和备案；这是行政推进，不是建设或投产证据。"),
    "N012": ("later_mention_only", "2022-09-29", "https://toutiao.com/group/7148645485812040207/", "", "C", "同名南阳青桔产业化生产项目在半年后再次签约；重复签约本身不构成物理建设里程碑。"),
    "N017": ("physical_progress", "2022-04-06", "https://m.sohu.com/a/535817390_120326960/", "https://wap.01ny.cn/html/news/2023/05/19/show-370662.html", "A", "项目被列入卧龙区第四期‘三个一批’集中开工，2023年后续报道又出现企业展厅和经营运转信息。"),
    "N020": ("physical_progress", "2022-04-15", "https://toutiao.com/group/7086621262742782467/", "https://4g.dahe.cn/city/202304041214894", "A", "河南艾益健产业园被列入集中开工项目；2023年公开报道出现对产业园的现场调研。"),
    "N021": ("built", "2024-04-11", "http://c.m.163.com/news/a/IVH52T1U0552ADWT.html", "https://toutiao.com/group/7347496670827823657/", "A", "公开报道明确称年产200万只高端出口汽车零部件智能化项目一期已建成投产。"),
    "N024": ("physical_progress", "2022-08-17", "https://toutiao.com/group/7132763198117773854/", "", "A", "河南日报报道该陶瓷纤维滤管生产线建设接近尾声，并描述设备安装进度。"),
    "N030": ("later_mention_only", "2023-03-03", "https://www.wolong.gov.cn/2023/03-03/911625.html", "", "C", "卧龙区政府工作报告称56亿元江苏超电项目‘落地实施’，但未给出厂房、设备、开工或投产等项目专属物理节点。"),
    "N036": ("built", "2024-03-08", "https://www.nanzhao.gov.cn/2024/06-17/805847.html", "", "A", "南召县政府工作报告称东方雨虹一期从开工到试产仅用67天。"),
    "N037": ("physical_progress", "2024-07-26", "https://toutiao.com/group/7395803481875038731/", "", "A", "河南日报报道中能建康辉绿色建材项目举行开工活动。"),
    "N038": ("later_mention_only", "2024-03-07", "https://www.nanzhao.gov.cn/2024/03-07/806195.html", "", "C", "南召县年度安排继续提出推进青山绿色建材产业园，未找到项目专属已开工或已投产节点。"),
    "N039": ("later_mention_only", "2022-10-12", "https://toutiao.com/group/7153477018905281058/", "", "C", "项目在后续招商报道中再次被列为已签约项目，未出现新的建设节点。"),
    "N051": ("physical_progress", "2023-03-03", "https://www.wolong.gov.cn/2023/03-03/911625.html", "", "B", "卧龙区政府工作报告把高端智能装备列入‘抓投产’并要求尽早达产，说明已进入投产调度阶段，但未找到完整投产记录。"),
    "N053": ("administrative_only", "2024-08-29", "https://nygtzy.nanyang.gov.cn/2024/08-29/611259.html", "", "C", "南阳市自然资源和规划局发布乔官庄中州村改造项目建设工程设计方案公示，属于规划审批进度。"),
    "N055": ("physical_progress", "2025-05-16", "https://www.wolong.gov.cn/2025/05-16/1040024.html", "", "A", "卧龙区政府发布的计划报告明确写明南阳产投预制菜产业园一期主体工程建成，标准化厂房预定率达到70%。"),
}


with DATA.open(encoding="utf-8", newline="") as file:
    rows = list(csv.DictReader(file))
    fields = list(rows[0])

for row in rows:
    if row["cohort_role"] != "nanyang_named_project":
        continue
    decision = DECISIONS.get(row["project_id"])
    if decision:
        status, date, source, secondary, grade, reason = decision
    else:
        status, date, source, secondary, grade = "no_later_trace_located", "", "", "", "D"
        reason = "截至2025-12-31，在预设的项目全称、企业名和县区双查询公开检索中，未定位到项目专属的投产、施工、审批或后续推进记录。"
    row.update({
        "followup_status": status,
        "followup_date": date,
        "source_followup": source,
        "source_followup_secondary": secondary,
        "followup_reason": reason,
        "evidence_grade": grade,
        "reviewed_on": REVIEWED_ON,
    })

with DATA.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

counts = {}
for row in rows:
    counts[row["followup_status"]] = counts.get(row["followup_status"], 0) + 1
print(DATA, len(rows))
print(counts)
