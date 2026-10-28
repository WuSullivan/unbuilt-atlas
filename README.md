# 签约之后 / Unbuilt Atlas

> 我把政府公开宣布的招商项目逐个列出来，几年后再查一遍，看有多少留下了公众可以核对的建设证据。

**在线地图：** https://wusullivan.github.io/unbuilt-atlas/  
**公开仓库：** https://github.com/WuSullivan/unbuilt-atlas

一场招商签约会结束以后，承诺去了哪里，等待它的人付出了什么代价？

## 结论

研究覆盖河南南阳2019至2022年的公开招商项目，追踪截止2025年12月31日。

- 21篇不重复的主要签约报道宣布了426个项目名额，只有62个在同一篇报道中被明确点名，点名率为14.6%。
- 数据集逐项追踪80个明确点名项目。5项有建成或试产记录，9项有开工、主体建成或明确投产调度，强物理里程碑率为14/80，即17.5%。
- 58/80项在既定公开检索中没有定位到项目专属后续里程碑。
- 淅川14项深度核查队列中，1项建成、2项部分建成，建成或部分建成率为3/14，即21.4%。
- 在核查方法一致的66项广域队列中，知名企业信号和活动公布规模都没有显示出更高的物理兑现率。逻辑回归优势比分别为1.21和1.16，95%置信区间都跨过1。

这不是把“没查到”改写成“没建成”。项目状态记录的是公众能否沿着公开记录继续追踪一项承诺。

## 打开成品

- [交互地图](site/index.html)
- [80项项目数据](data/nanyang_projects.csv)
- [24个事件表](data/events.csv)
- [400条证据阶段账本](data/evidence_ledger.csv)
- [497条搜索候选记录](data/followup_search_results.csv)
- [去重来源表](data/source_register.csv)
- [80项本地不同卫星影像配对元数据](data/wayback_pairs.json)
- [来源链接健康审计](outputs/source_health.csv)
- [三页政策简报](outputs/unbuilt-atlas-research-brief.pdf)
- [申请叙事与延伸路线](outputs/application-story.md)
- [完整数据归档](outputs/unbuilt-atlas-dataset.zip)
- [可直接发布的完整项目归档](outputs/unbuilt-atlas-publication.zip)
- [字段字典](data/field_dictionary.md)
- [方法与纳入规则](data/method.md)
- [人工判断日志](data/decision_log.md)

## 研究结构

1. **事件透明度层**：统计主要官方报道宣布多少项目名额，以及报道本身公开多少项目名称。
2. **80项项目层**：追踪南阳市、县区公开点名项目的投产、施工、审批和后续提及。
3. **淅川深审层**：对同一14项官方队列使用更严格的项目级证据规则，检查广域结果是否只是搜索深度不足造成。

## 状态规则

- built：明确投产、试产、验收或投入运营。
- physical_progress：明确开工、主体建成、车间或设备进度，或官方文件显示进入投产调度阶段。
- administrative_only：规划、备案、注册或审批推进，没有物理建设证据。
- later_mention_only：签约后再次出现，但没有新增物理或行政节点。
- no_later_trace_located：广域队列在预设公开检索中没有定位到项目专属后续记录。
- no_physical_milestone_located：淅川深审没有定位到项目专属物理里程碑。

## 复现

使用工作区自带的Python环境或安装 pandas、numpy、statsmodels、reportlab。

    python3 build_expanded_atlas.py
    python3 search_followups.py
    python3 curate_followups.py
    python3 analysis.py
    python3 build_wayback_pairs.py
    python3 build_evidence_ledger.py
    python3 build_site_data.py
    python3 build_brief_pdf.py
    python3 audit_sources.py
    python3 build_publication.py
    ./verify.sh

search_followups.py只生成候选记录，不自动判定项目状态。人工审定集中在curate_followups.py，因此每一个非默认状态都有可审查的来源、日期、理由和证据等级。

audit_sources.py并发检查引用链接是否仍可访问，输出source_health.csv。链接临时受限或失效不会自动改变项目状态；证据判断与网络健康是两条独立审计链。

## 影像说明

地图为每项项目分别查询Esri Wayback的本地历史版本，并对同一中心瓦片做SHA-256去重，确保两张图实际调用的是不同影像文件。80组中，62组实际采集日期跨过签约日；16组没有定位到签约后的采集影像；另2组有签约后影像，但左图采集日期缺失。页面逐项标出日期、来源和分辨率，不把Wayback版本发布日期冒充拍摄日期。广域坐标是县区中心，淅川坐标是园区或乡镇指示点，不是宗地红线；影像不参与项目状态判定。

## 发布

仓库根目录的index.html会跳转到地图。GitHub Pages可直接从主分支根目录发布；.nojekyll确保CSV、PDF和静态资源按原路径提供。Zenodo发布所需的CITATION.cff已准备好，可在GitHub首次正式版本发布后连接Zenodo生成DOI。

