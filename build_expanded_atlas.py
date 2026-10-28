#!/usr/bin/env python3
"""Build the Nanyang signing-event census and 80-project named cohort."""
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent

EVENTS = [
    ("E01", "2019-10-29", "南阳市", "张仲景医药文化节经贸洽谈暨项目签约会", "https://www.nanyang.gov.cn/2019/10-30/306759.html", 65, 3, 385.9, "primary_event", "grouped_in_person"),
    ("E02", "2020-07-24", "南阳市", "驻郑州务工创业招商引智项目签约", "https://www.nanyang.gov.cn/2020/07-27/307871.html", 2, 2, 20.4, "primary_event", "grouped_in_person"),
    ("E03", "2020-05-09", "卧龙区", "养老健康产业合作项目签约", "https://www.nanyang.gov.cn/2020/05-12/306455.html", 1, 1, "", "primary_event", "single_project"),
    ("E04", "2021-04-28", "镇平县", "玉雕文化节集中签约", "https://www.nanyang.gov.cn/2021/04-29/308002.html", 25, 0, 67.7, "primary_event", "grouped_in_person"),
    ("E05", "2022-01-24", "南阳市", "一月份项目签约和建设推进日", "https://www.nanyang.gov.cn/2022/01-27/294779.html", 103, 0, 1016.2, "primary_event", "grouped_video"),
    ("E06", "2022-03-28", "南阳市", "三月份项目签约和建设推进日", "https://www.nanyang.gov.cn/2022/03-29/25208.html", 117, 2, 1228, "primary_event", "grouped_video"),
    ("E07", "2022-03-28", "卧龙区", "卧龙区三月份在线视频签约", "https://www.nanyang.gov.cn/2022/03-30/269931.html", 11, 11, 59.26, "subset_detail", "grouped_video"),
    ("E08", "2022-04-28", "宛城区", "月季花会宛城区经贸合作签约", "https://www.nanyang.gov.cn/2022/05-05/271959.html", 20, 0, 180, "primary_event", "grouped_in_person"),
    ("E09", "2022-04-28", "西峡县", "月季花会西峡县经贸合作签约", "https://www.nanyang.gov.cn/2022/05-05/287057.html", 6, 6, 71.35, "primary_event", "grouped_in_person"),
    ("E10", "2022-04-28", "镇平县", "月季花会镇平县经贸合作签约", "https://www.nanyang.gov.cn/2022/05-07/298681.html", 17, 0, 95.9, "primary_event", "grouped_in_person"),
    ("E11", "2022-05-10", "桐柏县", "招商引资项目签约", "https://www.nanyang.gov.cn/2022/05-17/281604.html", 3, 3, 119.4, "primary_event", "grouped_in_person"),
    ("E12", "2022-05-17", "卧龙区", "卧龙区重大项目签约", "https://www.nanyang.gov.cn/2022/05-20/269961.html", 2, 2, 59, "primary_event", "grouped_in_person"),
    ("E13", "2022-06-02", "桐柏县", "招商引资项目集中签约", "https://www.nanyang.gov.cn/2022/06-06/281610.html", 4, 4, "", "primary_event", "grouped_in_person"),
    ("E14", "2022-06-10", "南阳市", "重点文旅项目招商推介暨签约", "https://www.nanyang.gov.cn/2022/06-14/234236.html", 12, 8, 46, "primary_event", "grouped_in_person"),
    ("E15", "2022-06-20", "南召县", "重大项目签约落户", "https://www.nanyang.gov.cn/2022/06-23/284956.html", 4, 4, 90, "primary_event", "grouped_report"),
    ("E16", "2022-06-30", "卧龙区", "卧龙区六月份在线视频签约", "https://www.nanyang.gov.cn/2022/07-01/269988.html", 21, 3, 59, "primary_event", "grouped_video"),
    ("E17", "2022-07-06", "内乡县", "中原畜牧业交易博览会项目签约", "https://www.nanyang.gov.cn/2022/07-08/289387.html", 7, 7, 50, "primary_event", "grouped_in_person"),
    ("E18", "2022-08-05", "卧龙区", "生态环保静脉产业园项目签约", "https://www.nanyang.gov.cn/2022/08-11/234613.html", 1, 1, 7, "primary_event", "single_project"),
    ("E19", "2022-08-26", "卧龙区", "卧龙区八月份项目签约", "https://www.nanyang.gov.cn/2022/08-29/270028.html", 13, 13, 134.93, "primary_event", "grouped_video"),
    ("E20", "2022-08-26", "高新区", "仲源艾草健康产业园签约", "https://www.nanyang.gov.cn/2022/08-30/206274.html", 1, 1, 10, "primary_event", "grouped_video"),
    ("E21", "2022-09-28", "西峡县", "国家级中医药新经济产业园签约", "https://www.nanyang.gov.cn/2022/10-08/287143.html", 1, 1, "", "primary_event", "single_project"),
    ("E22", "2022-12-09", "内乡县", "十万头肉牛产业项目签约", "https://www.nanyang.gov.cn/2022/12-13/289469.html", 1, 1, "", "primary_event", "single_project"),
    ("E23", "2022-06-15", "淅川县", "十四项重点签约项目集中观摩队列", "https://www.xichuan.gov.cn/2022/06-15/1283248.html", 14, 14, "", "deep_audit_cohort", "grouped_inspection"),
    ("E24", "2022-01-17", "方城县", "奇瑞商用车区域总部经济项目签约", "http://www.nanyang.gov.cn/2022/01-24/279472.html", 1, 1, "", "possible_subset_detail", "single_project"),
]

COORDS = {
    "南阳市": (32.9908, 112.5283), "卧龙区": (32.9868, 112.5230),
    "宛城区": (32.9945, 112.5395), "高新区": (33.0350, 112.5400),
    "西峡县": (33.3056, 111.4725), "镇平县": (33.0334, 112.2347),
    "桐柏县": (32.3792, 113.4288), "方城县": (33.2544, 113.0127),
    "南召县": (33.4899, 112.4292), "内乡县": (33.0447, 111.8493),
}

# Project name, company, county, industry, event, exact amount (CNY 100m), signal.
PROJECTS = [
    ("宛城区新奥燃气能源利用项目", "新奥燃气", "宛城区", "能源", "E01", "", "national_company"),
    ("卧龙区牧原农牧装备研发生产项目", "牧原集团", "卧龙区", "农牧装备", "E01", "", "listed_company"),
    ("高新区河南远近人工智能大数据项目", "河南远近", "高新区", "数字产业", "E01", "", "regional_company"),
    ("南阳市人力资源产业园区建设项目", "", "南阳市", "产业服务", "E02", 20, "undisclosed"),
    ("新型鼻炎治疗仪生产项目", "", "南阳市", "医疗器械", "E02", 0.4, "undisclosed"),
    ("南阳市养老中心项目", "光大养老健康产业有限公司", "卧龙区", "养老服务", "E03", "", "national_company"),
    ("奇瑞商用车区域总部经济项目", "奇瑞商用车（安徽）有限公司", "方城县", "汽车产业", "E24", "", "national_company"),
    ("宛城区中德产业园一期项目", "", "宛城区", "产业园", "E06", "", "undisclosed"),
    ("西峡县特钢连铸连轧绿色生产线建设项目", "", "西峡县", "钢铁/绿色制造", "E06", "", "undisclosed"),
    ("年产1.5亿件高端光学新材料生产项目", "", "卧龙区", "光学新材料", "E07", "", "undisclosed"),
    ("标准化五星级农贸市场项目", "", "卧龙区", "商贸", "E07", "", "undisclosed"),
    ("南阳青桔产业项目", "青桔", "卧龙区", "绿色出行", "E07", "", "national_brand"),
    ("年产6000套全自动艾灸床生产线建设项目", "", "卧龙区", "艾草健康设备", "E07", "", "undisclosed"),
    ("年产30套大型筑路设备生产线项目", "", "卧龙区", "装备制造", "E07", "", "undisclosed"),
    ("高品质肉牛养殖繁育及有机农产品种植一体化项目", "", "卧龙区", "现代农业", "E07", "", "undisclosed"),
    ("年产4000吨包装及印刷品建设项目", "", "卧龙区", "包装印刷", "E07", "", "undisclosed"),
    ("伊品万家年产20000吨清真食品建设项目", "伊品万家", "卧龙区", "食品加工", "E07", "", "regional_company"),
    ("年产100万件无烟艾制品加工项目", "", "卧龙区", "艾草制品", "E07", "", "undisclosed"),
    ("南阳市木本油料及农产品加工基地产业园区项目", "", "卧龙区", "农产品加工", "E07", "", "undisclosed"),
    ("河南艾益健产业园建设项目", "河南艾益健", "卧龙区", "艾草健康", "E07", "", "regional_company"),
    ("年产200万只高端出口汽车零部件智能化项目", "", "西峡县", "汽车零部件", "E09", "", "undisclosed"),
    ("仁创新型精密铸造材料生产线建设项目", "仁创", "西峡县", "铸造材料", "E09", "", "regional_company"),
    ("中药智能化提取生产线建设项目", "", "西峡县", "中医药", "E09", "", "undisclosed"),
    ("年产3万支环保用陶瓷纤维滤管生产线建设项目", "", "西峡县", "环保材料", "E09", "", "undisclosed"),
    ("电力设备配件生产项目", "", "西峡县", "电力装备", "E09", "", "undisclosed"),
    ("鑫立矿业蒲塘金矿项目", "鑫立矿业", "西峡县", "矿业", "E09", "", "regional_company"),
    ("桐柏县熙开地创新药物工业园项目", "熙开地", "桐柏县", "生物医药", "E11", "", "regional_company"),
    ("桐柏县年产30万吨集装吨袋生产项目", "", "桐柏县", "包装材料", "E11", "", "undisclosed"),
    ("桐柏县年产30万吨工业纯碱及小苏打项目", "", "桐柏县", "化工", "E11", "", "undisclosed"),
    ("超电10GWh超级快充动力电池生产线建设项目", "江苏超电/中如建工", "卧龙区", "动力电池", "E12", 56, "national_company"),
    ("共享电单车组装生产与投放运营项目", "宁波小遛共享信息科技有限公司", "卧龙区", "绿色出行", "E12", 3, "national_brand"),
    ("桐柏县5G新型智慧城市建设合作项目", "", "桐柏县", "数字城市", "E13", "", "undisclosed"),
    ("桐柏县交通建设发展投资有限公司项目", "", "桐柏县", "交通投资", "E13", "", "local_platform"),
    ("中电投新农创乡村振兴合作项目", "中电投新农创", "桐柏县", "乡村振兴", "E13", "", "national_company"),
    ("桐柏县与华润数科合作项目", "华润数科", "桐柏县", "数字产业", "E13", "", "central_state_company"),
    ("东方雨虹南阳绿色建材生产基地项目", "东方雨虹", "南召县", "新型建材", "E15", 30, "listed_company"),
    ("康辉石业项目", "康辉石业", "南召县", "石材", "E15", 20, "regional_company"),
    ("青山建材项目", "青山建材", "南召县", "新型建材", "E15", 20, "regional_company"),
    ("超赢现代中药及白酒产业园", "超赢", "南召县", "中医药/食品", "E15", 20, "regional_company"),
    ("年产500万平方米新材料智能制造建设项目", "", "卧龙区", "新材料", "E16", "", "undisclosed"),
    ("南阳艾的仁年产1000吨艾草精油养生化妆品项目", "南阳艾的仁", "卧龙区", "艾草健康", "E16", "", "regional_company"),
    ("年产10万平方米智能门窗生产建设项目", "", "卧龙区", "智能家居", "E16", "", "undisclosed"),
    ("1万吨不锈钢管材管件项目", "", "内乡县", "金属加工", "E17", "", "undisclosed"),
    ("年产2000吨塑料包装产品项目", "", "内乡县", "包装材料", "E17", "", "undisclosed"),
    ("5G智慧路灯生产项目", "", "内乡县", "智慧城市装备", "E17", "", "undisclosed"),
    ("农牧智能化物联网软硬件产品研发生产项目", "", "内乡县", "农牧科技", "E17", "", "undisclosed"),
    ("农牧智能饲喂研发生产基地项目", "", "内乡县", "农牧装备", "E17", "", "undisclosed"),
    ("农牧装备加工生产基地项目", "", "内乡县", "农牧装备", "E17", "", "undisclosed"),
    ("特种线缆生产项目", "", "内乡县", "电工材料", "E17", "", "undisclosed"),
    ("南阳市生态环保静脉产业园污泥固废资源化利用项目", "河南宗源环保科技有限公司", "卧龙区", "环保", "E18", 7, "regional_company"),
    ("高端智能装备制造建设项目", "", "卧龙区", "高端装备", "E19", 35, "undisclosed"),
    ("年产2000台套智能环保矿山机械设备研发生产建设项目", "", "卧龙区", "矿山装备", "E19", "", "undisclosed"),
    ("乔官庄中州村城中村改造项目A区B区", "", "卧龙区", "城市更新", "E19", "", "undisclosed"),
    ("年产3000件套智能艾制品设备及家具制造项目", "", "卧龙区", "艾草设备/家具", "E19", "", "undisclosed"),
    ("南阳产投预制菜产业园建设项目", "南阳产投", "卧龙区", "食品加工", "E19", "", "local_platform"),
    ("年产1000台套工程检测智能机器人制造项目", "", "卧龙区", "机器人", "E19", "", "undisclosed"),
    ("年产500万套新型环保包装材料项目", "", "卧龙区", "包装材料", "E19", "", "undisclosed"),
    ("年产300万平方米装配式建筑建设项目", "", "卧龙区", "装配式建筑", "E19", "", "undisclosed"),
    ("年产50万套特种光学镜片生产研发项目", "", "卧龙区", "光学", "E19", "", "undisclosed"),
    ("年加工5000吨红薯淀粉制品项目", "", "卧龙区", "食品加工", "E19", "", "undisclosed"),
    ("商英医疗年产20000套智能艾灸机器人项目", "商英医疗", "卧龙区", "医疗机器人", "E19", "", "regional_company"),
    ("御草堂药业年产3000吨中药饮片建设项目", "御草堂药业", "卧龙区", "中医药", "E19", "", "regional_company"),
    ("年产2万套智能门窗家居生产线", "", "卧龙区", "智能家居", "E19", "", "undisclosed"),
    ("仲源艾草健康产业园精深加工基地项目", "仲源", "高新区", "艾草健康", "E20", 10, "regional_company"),
    ("国家级中医药新经济产业园项目", "深圳正威有限公司", "西峡县", "中医药产业园", "E21", "", "national_company"),
    ("10万头肉牛产业项目", "河南坤汇牧业集团", "内乡县", "现代农业/食品", "E22", "", "regional_company"),
]


def quantified(name):
    return "yes" if any(token in name for token in ("年产", "万吨", "万件", "万套", "平方米", "GWh", "10万头", "台套", "生产线")) else "no"


event_by_id = {row[0]: row for row in EVENTS}
event_fields = ["event_id", "event_date", "county", "event_title", "source_url", "announced_project_slots", "named_physical_projects_in_article", "announced_investment_cny_100m", "counting_role", "event_mode"]
with (ROOT / "data/events.csv").open("w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file, lineterminator="\n")
    writer.writerow(event_fields)
    writer.writerows(EVENTS)

project_fields = ["project_id", "project_name", "company_name", "county", "sign_date", "industry", "announced_investment_cny_100m", "event_id", "event_mode", "event_announced_project_slots", "leader_present", "company_signal", "quantified_project_name", "source_sign", "followup_status", "followup_date", "source_followup", "source_followup_secondary", "followup_reason", "evidence_grade", "reviewed_on", "source_environment", "environment_check", "source_registry", "registry_check", "imagery_context", "lat", "lon", "geometry_precision", "cohort_role"]
rows = []
for index, project in enumerate(PROJECTS, 1):
    name, company, county, industry, event_id, amount, signal = project
    event = event_by_id[event_id]
    lat, lon = COORDS[county]
    rows.append({
        "project_id": f"N{index:03d}", "project_name": name, "company_name": company,
        "county": county, "sign_date": event[1], "industry": industry,
        "announced_investment_cny_100m": amount, "event_id": event_id,
        "event_mode": event[9], "event_announced_project_slots": event[5],
        "leader_present": "yes", "company_signal": signal,
        "quantified_project_name": quantified(name), "source_sign": event[4],
        "followup_status": "search_pending", "followup_date": "", "source_followup": "",
        "source_followup_secondary": "", "followup_reason": "", "evidence_grade": "",
        "reviewed_on": "", "source_environment": "", "environment_check": "not_systematically_verified",
        "source_registry": "", "registry_check": "not_systematically_verified",
        "imagery_context": "esri_wayback_local_distinct_project_pair",
        "lat": lat, "lon": lon,
        "geometry_precision": "indicative_county_centroid", "cohort_role": "nanyang_named_project",
    })

# Append the 14-row Xichuan deep audit without altering its evidence decisions.
with (ROOT / "data/projects.csv").open(encoding="utf-8", newline="") as file:
    xichuan = [row for row in csv.DictReader(file) if row["cohort_role"] == "primary_2022_cohort"]
for row in xichuan:
    event = event_by_id["E23"]
    status = {"built": "built", "partially_built": "physical_progress", "unverified": "no_physical_milestone_located"}[row["status"]]
    rows.append({
        "project_id": "X" + row["project_id"][1:], "project_name": row["project_name"],
        "company_name": row["company_name"], "county": "淅川县", "sign_date": event[1],
        "industry": row["industry"], "announced_investment_cny_100m": row["investment_cny_100m"],
        "event_id": "E23", "event_mode": event[9], "event_announced_project_slots": event[5],
        "leader_present": row["leader_present_at_signing"], "company_signal": row["company_signal"],
        "quantified_project_name": quantified(row["project_name"]), "source_sign": row["source_sign"],
        "followup_status": status, "followup_date": "", "source_followup": row["source_followup"],
        "source_followup_secondary": "", "followup_reason": row["status_reason"],
        "evidence_grade": "A" if status != "no_physical_milestone_located" else "D",
        "reviewed_on": "2026-10-29", "source_environment": row["source_environment"],
        "environment_check": row["environment_check"], "source_registry": row["source_registry"],
        "registry_check": row["registry_check"],
        "imagery_context": "esri_wayback_local_distinct_project_pair",
        "lat": row["lat"], "lon": row["lon"],
        "geometry_precision": row["geometry_precision"], "cohort_role": "xichuan_deep_audit",
    })

with (ROOT / "data/nanyang_projects.csv").open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=project_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

print(ROOT / "data/events.csv", len(EVENTS))
print(ROOT / "data/nanyang_projects.csv", len(rows))
