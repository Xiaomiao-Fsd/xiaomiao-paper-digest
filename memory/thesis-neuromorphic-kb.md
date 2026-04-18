# Thesis neuromorphic KB

建立时间：2026-04-12

## 目的

为用户的广东工业大学本科毕业论文建立一个本地可检索记忆库，避免几天后继续写作时遗忘当前论文版本、开题报告结构和参考文献分工。

## 固定入口

- KB 根目录：`/home/XiaomiaoClaw/.openclaw/workspace/knowledge/gdut-thesis-neuromorphic-kb/`
- KB 索引：`/home/XiaomiaoClaw/.openclaw/workspace/knowledge/gdut-thesis-neuromorphic-kb/INDEX.md`
- 当前论文副本：`/home/XiaomiaoClaw/.openclaw/workspace/knowledge/gdut-thesis-neuromorphic-kb/sources/current_thesis_report.docx`
- 开题报告副本：`/home/XiaomiaoClaw/.openclaw/workspace/knowledge/gdut-thesis-neuromorphic-kb/sources/opening_report.docx`
- 当前论文提取版：`/home/XiaomiaoClaw/.openclaw/workspace/knowledge/gdut-thesis-neuromorphic-kb/extracted/current_thesis_report.md`
- 开题报告提取版：`/home/XiaomiaoClaw/.openclaw/workspace/knowledge/gdut-thesis-neuromorphic-kb/extracted/opening_report.md`
- 文献总库：`/home/XiaomiaoClaw/.openclaw/workspace/literature/neuromorphic-paperlib-2026-04-10/`
- 文献索引：`/home/XiaomiaoClaw/.openclaw/workspace/literature/neuromorphic-paperlib-2026-04-10/INDEX.md`

## 已确认的第一章结构

- 1.1.1 冯·诺依曼架构瓶颈与神经形态计算的发展需求
- 1.1.2 突触晶体管在神经形态系统中的作用与研究价值
- 1.1.3 时空相关可塑性研究的理论意义与应用意义
- 1.2.1 突触晶体管及侧栅/多栅结构的研究进展
- 1.2.2 栅距对 EPSC、PPF 等突触行为影响的研究进展
- 1.2.3 时空信息整合与储备池计算相关研究进展
- 1.2.4 当前研究存在的问题与不足

## 用户当前要求

- 续写时以当前论文文档 1.1 的语言风格和结构为准。
- 条理与章节拆分参考开题报告。
- 之前整理好的 PDF 文献合集继续作为主要参考来源。
- 当用户再次提到 1.2.1 / 1.2.2 / 1.2.3 时，优先先看 KB 索引和参考文献映射再动笔。
- 2026-04-18 已恢复并同步较新的主稿版本；当前 KB 的 `sources/current_thesis_report.docx` 已不再是 4 月 12 日那份旧副本，而是包含完整第 1 章、已写第 2 章和新起草的第 3.1 节的方法稿。

## 最新工作断点（2026-04-18）

- 恢复出的较新工作底稿来源：`/home/XiaomiaoClaw/.openclaw/workspace/tmp/Report_chapter2_patent_calibrated_1776166139.docx`
- 新生成的续写稿：`/home/XiaomiaoClaw/.openclaw/workspace/tmp/Report_chapter3_1_comsol_draft_1776489312.docx`
- 用户基于此前版本补写并回传了：`/home/XiaomiaoClaw/.openclaw/qqbot/downloads/Report_1776488081235.docx`
- 已进一步整理增强版：`/home/XiaomiaoClaw/.openclaw/workspace/tmp/Report_3_1_formula_enriched_1776492244.docx`
- 已写入内容：第 3 章中 `控制方程、求解区域与参数设置` 相关段落；显式补入了 3 条与 COMSOL 相关的公式（准稳态 Nernst–Planck 通量平衡、Poisson 方程、净离子电荷积分式），并补足变量定义与物理作用说明
- 用户额外确认的写作约束：第 3.1 节不要讨论 N 型 / P 型分类，因为这里按 TFT 器件主线来写，重点应放在离子迁移、电势耦合、边界条件与仿真模型，而不是器件极性分类。
- 下一优先续写目标：第 3 章 `不同侧栅间距下离子浓度/电势分布`，再往后是 `非单调离子迁移效率序列的形成条件与敏感性分析`

## 文献映射简记

- 1.2.1：Multi-gate organic neuron transistors、side-gated graphene、ionic liquid/polymer electrolyte gated transistors、A Single-Transistor Silicon Synapse
- 1.2.2：Multi-gate organic neuron transistors、Lateral ionic-gated graphene synaptic transistor
- 1.2.3：Oxide dendrite transistors、Artificial Dendrites for Reservoir Computing、multi-terminal ion-controlled transistor
