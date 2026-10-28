# 字段字典

## events.csv

| 字段 | 含义 |
|---|---|
| event_id | 稳定事件编号。 |
| event_date | 签约或报道所述活动日期。 |
| county | 活动所属市或县区。 |
| event_title | 官方报道中的活动简称。 |
| source_url | 事件来源链接。 |
| announced_project_slots | 报道宣布的项目数量。它是报道层项目名额，不保证已经完成跨报道去重。 |
| named_physical_projects_in_article | 同一篇报道里明确写出名称的物理项目数。 |
| announced_investment_cny_100m | 报道公布的总投资额，单位亿元；空白表示没有可比数字。 |
| counting_role | primary_event进入事件分母；subset_detail和possible_subset_detail不重复计数；deep_audit_cohort只用于深审。 |
| event_mode | single_project、grouped_in_person、grouped_video、grouped_report或grouped_inspection。 |

## nanyang_projects.csv

| 字段 | 含义 |
|---|---|
| project_id | 稳定项目编号。N为广域队列，X为淅川深审。 |
| project_name | 去重后的项目名称。 |
| company_name | 报道披露的企业或发起方。 |
| county | 项目所属县区。 |
| sign_date | 项目签约或进入队列的日期。 |
| industry | 便于描述分析的行业分组。 |
| announced_investment_cny_100m | 项目级公开投资额，单位亿元。 |
| event_id | 对应events.csv。 |
| event_mode | 对应事件的活动形式。 |
| event_announced_project_slots | 该活动报道宣布的项目名额。 |
| leader_present | 报道是否披露领导出席。 |
| company_signal | 企业表面信号类别，如listed_company、national_company、regional_company或undisclosed。 |
| quantified_project_name | 项目名称是否含产能、数量或规模词。 |
| source_sign | 纳入项目的主要来源。 |
| followup_status | 人工审定的最强后续状态。 |
| followup_date | 主要后续证据日期。 |
| source_followup | 主要后续证据链接。 |
| source_followup_secondary | 交叉核对来源。 |
| followup_reason | 状态判定的简短证据链。 |
| evidence_grade | A、B、C或D级。 |
| reviewed_on | 人工审定日期。 |
| source_environment | 已捕获的项目级环评、规划或许可来源。 |
| environment_check | 环境/规划证据核查状态。 |
| source_registry | 已捕获的本地注册或企业来源。 |
| registry_check | 注册证据核查状态。 |
| imagery_context | 项目详情双图的Wayback本地不同影像配对说明；具体版本、采集日期和瓦片哈希见wayback_pairs.json。 |
| lat, lon | 指示坐标。 |
| geometry_precision | 坐标精度；indicative_county_centroid等都不是宗地。 |
| cohort_role | nanyang_named_project或xichuan_deep_audit。 |

## evidence_ledger.csv

每个项目有五条记录：inclusion、post_signing_followup、environment、local_registry、imagery。finding记录该阶段发现，certainty记录证据强度，audit_note说明空白是否属于真正的负面结果。

## wayback_pairs.json

每个项目包含`before`和`after`两张本地影像；同一指示坐标、同一缩放级别的中心瓦片文件哈希不同。`release_date`是Wayback版本发布日期；`capture_date`是Esri元数据返回的影像采集日，二者不能互换。`provider`、`source`、`resolution_m`和`accuracy_m`来自影像元数据。`tile_sha256`记录中心瓦片文件哈希；两个哈希不同是进入前端配对的必要条件。`comparison_type`若为`latest_distinct_image_no_verified_post_sign_capture`，表示该点没有定位到签约后采集影像，不能把右图称作签约后影像；`post_sign_capture_before_capture_unknown`表示右图有签约后采集日期，但左图采集日期缺失。坐标精度仍由主项目表中的`geometry_precision`决定。

## followup_search_results.csv

这是候选账本，不是结论表。relevance_score和milestone_guess仅用于排序。项目状态以nanyang_projects.csv和curate_followups.py为准。

