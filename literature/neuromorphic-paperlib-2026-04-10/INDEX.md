# Neuromorphic Paper Library — 2026-04-10

来源压缩包：`/home/XiaomiaoClaw/.openclaw/qqbot/downloads/Paper_1775801330849.zip`

已完成的整理工作：
- 解包原始文献
- 使用 `pdftotext` 将 12 篇 PDF 转为可检索文本
- 完成首轮主题筛选，按“与论文目录的契合度”分组

目录结构：
- `pdfs/`：原始 PDF 副本
- `text/`：可检索文本
- `INDEX.md`：文献索引与首轮评估

---

## A 组：与当前论文高度相关，优先细读

### 1) Multi-gate organic neuron transistors for spatiotemporal information processing
- 相关度：很高
- 关键词：multi-gate、OECT、spatiotemporal information processing、EPSC、PPF、distance between gate and channel
- 价值判断：这篇和你的论文目录贴合度非常高，既能支撑 **1.2.1 突触晶体管及侧栅/多栅结构的研究进展**，也能支撑 **1.2.2 栅距对 EPSC、PPF 等突触行为影响的研究进展**，同时还能自然过渡到 **1.2.3 时空信息整合**。
- 建议用途：核心参考文献之一。

### 2) Oxide dendrite transistors gated with polyvinyl alcohol/chitosan hybrid electrolyte for spatiotemporal integration
- 相关度：很高
- 关键词：oxide dendrite transistor、multi-gate、spatiotemporal integration、logic operation、heterosynaptic mechanism
- 价值判断：适合用于多栅/树突结构、时空整合能力和复杂仿生功能展示，可重点放入 **1.2.1** 与 **1.2.3**。
- 建议用途：核心参考文献之一。

### 3) Transistor-Structured Artificial Dendrites for Spatiotemporally Correlated Reservoir Computing
- 相关度：很高
- 关键词：artificial dendrites、spatiotemporally correlated、reservoir computing、lateral gate expansion
- 价值判断：非常适合支撑 **1.2.3 时空信息整合与储备池计算相关研究进展**，也和你后文的识别验证思路相当接近。
- 建议用途：核心参考文献之一。

### 4) A multi-terminal ion-controlled transistor with multifunctionality and wide temporal dynamics for reservoir computing
- 相关度：高
- 关键词：multi-terminal、ion-controlled transistor、wide temporal dynamics、reservoir computing
- 价值判断：更偏向储备池计算和多端输入动态特性，可作为 **1.2.3** 的强支撑文献。
- 建议用途：优先细读。

### 5) Lateral ionic-gated graphene synaptic transistor with transition from paired-pulse facilitation to depression for filtering and image recognition
- 相关度：高
- 关键词：lateral ionic-gated、graphene synaptic transistor、PPF to PPD、filtering、image recognition
- 价值判断：和 **PPF/突触行为调控** 以及 **识别应用** 都有关，适合放在 **1.2.2**，也可在应用段落顺带引用。
- 建议用途：优先细读。

---

## B 组：可作为背景或补充引用

### 6) A Light-Stimulus Flexible Synaptic Transistor Based on Ion-Gel Side-Gated Graphene for Neuromorphic Computing
- 相关度：中高
- 关键词：side-gated、ion-gel、graphene、light stimulus、synaptic transistor
- 价值判断：对 **侧栅结构** 很有帮助，但重点偏光刺激与柔性器件，和你的主线不是完全重合。
- 建议用途：适合在 **1.2.1** 作为侧栅结构代表性工作之一。

### 7) Long-term synaptic plasticity simulated in ionic liquid/polymer hybrid electrolyte gated organic transistors
- 相关度：中高
- 关键词：long-term synaptic plasticity、ionic liquid/polymer hybrid electrolyte、organic transistors
- 价值判断：适合作为突触可塑性与电解质栅控晶体管的基础背景文献。
- 建议用途：可放入 **1.2.1** 或一般背景综述段。

### 8) A Single-Transistor Silicon Synapse
- 相关度：中
- 关键词：single-transistor、silicon synapse、analog learning
- 价值判断：属于较经典的基础工作，适合在“突触晶体管发展脉络”里当早期代表性文献引用。
- 建议用途：适合背景铺垫，不一定要重点展开。

### 9) Van der Waals ferroelectric transistors: the all-round artificial synapses for high-precision neuromorphic computing
- 相关度：中
- 关键词：ferroelectric transistors、artificial synapses、high-precision neuromorphic computing
- 价值判断：更适合作为“人工突触器件总体发展”的代表性先进工作，用于拓宽综述视野。
- 建议用途：背景补充文献。

### 10) Flexible organic electrochemical transistors for bioelectronics
- 相关度：中
- 关键词：review、OECT、bioelectronics
- 价值判断：这是一篇偏综述型文章，对 OECT 基本机制和应用面有帮助，但与当前论文主线并不完全紧贴。
- 建议用途：了解 OECT 大背景时可用，正文不一定必须引用。

---

## C 组：与当前论文仅部分相关，谨慎使用

### 11) Multiple-gate SOI MOSFETs
- 相关度：较低
- 关键词：multiple-gate、SOI MOSFET
- 价值判断：更偏传统器件结构演进，对“多栅”这个概念有帮助，但不属于神经形态突触器件主线。
- 建议用途：除非需要从器件结构角度补充背景，否则可以不引。

### 12) An artificial nociceptor based on a diffusive memristor
- 相关度：较低
- 关键词：artificial nociceptor、diffusive memristor
- 价值判断：属于仿生感知器件的有趣工作，但与你的“突触晶体管 + 时空相关可塑性 + 储备池计算”主线关联不强。
- 建议用途：通常不建议在当前章节中作为核心引用。

---

## 按目录的初步映射建议

### 1.2.1 突触晶体管及侧栅/多栅结构的研究进展
优先考虑：
- Multi-gate organic neuron transistors for spatiotemporal information processing
- A Light-Stimulus Flexible Synaptic Transistor Based on Ion-Gel Side-Gated Graphene for Neuromorphic Computing
- Long-term synaptic plasticity simulated in ionic liquid/polymer hybrid electrolyte gated organic transistors
- A Single-Transistor Silicon Synapse

### 1.2.2 栅距对 EPSC、PPF 等突触行为影响的研究进展
优先考虑：
- Multi-gate organic neuron transistors for spatiotemporal information processing
- Lateral ionic-gated graphene synaptic transistor with transition from paired-pulse facilitation to depression for filtering and image recognition

说明：当前文献库里与“**栅距/距离效应**”直接高度贴合的文献仍然偏少，后续大概率需要补充更有针对性的论文。

### 1.2.3 时空信息整合与储备池计算相关研究进展
优先考虑：
- Oxide dendrite transistors gated with polyvinyl alcohol/chitosan hybrid electrolyte for spatiotemporal integration
- Transistor-Structured Artificial Dendrites for Spatiotemporally Correlated Reservoir Computing
- A multi-terminal ion-controlled transistor with multifunctionality and wide temporal dynamics for reservoir computing
- Multi-gate organic neuron transistors for spatiotemporal information processing

---

## 当前判断：还可能需要补的文献方向

后续如果要进一步提高“引用的针对性”，建议重点补以下几类论文：

1. **明确研究栅距/侧栅距离对 EPSC、PPF、STP/LTP 影响的论文**
2. **研究空间相关可塑性、且明确讨论距离依赖规律的论文**
3. **涉及非单调空间响应、非单调突触效能或厘米尺度空间调制的论文**
4. **结合 COMSOL / TCAD / 离子动力学分析来解释突触行为的论文**
5. **时空相关器件用于识别任务或储备池计算的代表性论文**

---

## 下一步建议

1. 优先细读 A 组文献，形成更扎实的引用依据。
2. 根据 1.2.1 / 1.2.2 / 1.2.3 三个小节分别筛选可直接嵌入正文的句子与结论。
3. 若发现 **1.2.2（栅距影响）** 的证据仍不够，再定向补文献。
