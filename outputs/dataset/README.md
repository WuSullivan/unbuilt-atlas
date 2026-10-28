# 数据说明

## 范围

- 地区：河南省南阳市及其县区，以淅川县为深度核查队列。
- 签约窗口：2019-01-01至2022-12-31。
- 后续截止：2025-12-31。
- 事件单位：一篇官方签约或项目队列报道。
- 项目单位：一个在公开来源中明确点名、可以建立身份的项目。

events.csv含24条事件记录。其中21条primary_event进入426个项目名额的分母；subset_detail、possible_subset_detail和deep_audit_cohort用于补充项目名称或深审，不重复计入事件名额分母。

nanyang_projects.csv含80项：66项南阳广域追踪项目和14项淅川深度核查项目。

## 证据等级

- A：项目名称匹配明确，并有投产、开工、主体建成、车间或设备等直接物理节点。
- B：项目名称匹配明确，官方文件显示进入投产调度或相近实施阶段，但缺少完整投产记录。
- C：只有规划、备案、注册、再次签约或后续提及。
- D：按预设检索没有定位到项目专属后续里程碑。

## 负面结果的写法

no_later_trace_located和no_physical_milestone_located都不是“项目不存在”。它们记录的是：在既定时间、查询式和公开来源范围内，没有定位到满足状态规则的项目专属证据。

## 影像

地图为80项项目分别配对Esri World Imagery Wayback的两个不同本地历史影像瓦片版本。配对根据实际采集日期、签约日期和2025-12-31截止线选择；中心瓦片经过SHA-256差异核验。Wayback发布版本日期与影像采集日期分开记录。坐标为县区、园区或乡镇指示点，不能用于宗地判断，也不参与状态编码。

## 文件关系

- events.csv：报道事件层。
- nanyang_projects.csv：项目主表。
- followup_search_results.csv：自动检索产生的497条候选，不代表事实判定。
- evidence_ledger.csv：80项乘5个证据阶段，共400条审计记录。
- source_register.csv：项目主表中的50个去重来源。
- wayback_pairs.json：80项各自的两个Wayback版本、采集元数据、指示点精度和中心瓦片SHA-256。
- ../outputs/source_health.csv：来源链接的独立可访问性检查，不参与状态自动编码。
- projects.csv：最初16行淅川pilot，保留用于复现深审队列来源。

