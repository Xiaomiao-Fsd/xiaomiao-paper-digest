# 2026-04-13 参考文献合集筛选（撰写与参考文献_1776057019982.zip）

来源压缩包：`/home/XiaomiaoClaw/.openclaw/qqbot/downloads/撰写与参考文献_1776057019982.zip`

## 实际内容

- 实际解压到 **16 篇 PDF**（并非 30 篇完整论文）
- `20-30/` 目录为空

## 本次筛选采用的“贴合设计意图”标准

仅优先保留能直接服务当前毕业设计主线的文献：

1. **多侧栅 / 多栅 / 树突式 / 多端输入的突触晶体管**
2. 明确涉及 **EPSC、PPF、STP/LTP、SNDP/SFDP** 等突触行为
3. 能支撑 **栅距 / 空间位置 / 距离变化** 对器件响应的影响
4. 能支撑 **时空信息整合 / 空间相关可塑性 / 非单调或复杂动态行为**
5. 最好还能与后文的 **COMSOL / TCAD 机理分析** 以及 **字母识别 / 储备池计算验证** 接上

结论：这批文献里真正“强贴合”的并不多，应当严格筛选，宁缺毋滥。

## 一、强烈建议纳入正文（核心文献）

### 1) Multi-Gate Organic Neuron Transistors for Spatiotemporal Information Processing
- 贴合度：**极高**
- 关键词：multi-gate、OECT、distance between in-plane gate and channel、EPSC、PPF、dendritic integration
- 入选理由：
  - 直接命中“**多栅 / 侧栅突触晶体管**”主线
  - 明确讨论 **EPSC、PPF** 等典型突触行为
  - 明确出现 **栅-沟道距离 / 空间位置** 对响应的影响
  - 可同时支撑 `1.2.1`、`1.2.2`、`1.2.3`
- 建议定位：**本包中最关键的一篇之一**

### 2) Spatiotemporal Information Processing Emulated by Multiterminal Neuro-Transistor Networks
- 贴合度：**很高**
- 关键词：multiterminal、multiple in-plane gates、EDL、EPSC、PPF、spatiotemporal input sequences
- 入选理由：
  - 属于 **多端/多栅神经晶体管**，和“树突式多输入整合”方向高度一致
  - 文中明确给出不同 gate-to-channel distance，并讨论 **EPSC / PPF / 时空序列判别**
  - 非常适合支撑“多输入时空处理能力”这条线
- 局限：
  - 更偏 **时空序列处理 / 神经晶体管网络**，对“栅距规律”不如 Qian 2017 那么直接
- 建议定位：可作为 `1.2.1` 与 `1.2.3` 的强支撑，也能部分辅助 `1.2.2`

### 3) Oxide dendrite transistors gated with polyvinyl alcohol/chitosan hybrid electrolyte for spatiotemporal integration
- 贴合度：**很高**
- 关键词：oxide dendrite transistor、multi-gate、spatiotemporal integration、logic operation
- 入选理由：
  - 直接命中“**树突 / 多栅 / 时空整合**”主线
  - 适合体现树突式结构如何处理多输入时空信号
  - 与后文器件结构和时空相关功能验证具有较强连续性
- 局限：
  - 更强调时空整合与功能展示，对“栅距—EPSC/PPF 定量关系”不是最强证据
- 建议定位：重点放在 `1.2.1`、`1.2.3`

### 4) Transistor-Structured Artificial Dendrites for Spatiotemporally Correlated Reservoir Computing
- 贴合度：**很高**
- 关键词：artificial dendrites、source/drain and gate interchangeability、centimeter-scale gate-channel distance、reservoir computing
- 入选理由：
  - 与开题报告中的“**可重构源/漏/栅 + 树突结构 + 时空相关 + 应用验证**”特别接近
  - 明确出现 **厘米级 gate-channel distance** 与人工树突结构
  - 非常适合作为 `1.2.3 时空整合与储备池计算` 的代表文献
- 局限：
  - 对基础突触指标和栅距规律的展开不一定是最核心
- 建议定位：`1.2.3` 的核心文献之一，也可在 `1.2.1` 末尾过渡引用

## 二、可作为背景补充，但不建议当主支撑文献

### 5) Recent Advances in Transistor-Based Artificial Synapses
- 贴合度：**中等偏高（综述价值高）**
- 作用：
  - 适合在“国内外研究现状”开头作为 **晶体管型人工突触总体综述**
  - 可帮助铺垫材料体系、工作机理与总体发展路线
- 不足：
  - 综述太宽，不足以直接支撑你的“多侧栅 + 栅距 + 时空相关”这一具体设计意图
- 建议：**只做综述型引文，不做核心论据**

### 6) All-Solid-State Synaptic Transistor with Ultralow Conductance for Neuromorphic Computing
- 贴合度：**中等**
- 作用：
  - 说明三端突触晶体管可以实现 STP/LTP、近线性权重更新和识别应用
  - 可在背景段说明“突触晶体管不仅可模拟突触行为，也可服务识别任务”
- 不足：
  - 缺少 **多侧栅 / 树突 / 栅距 / 空间相关** 这些你真正需要的内容
- 建议：**最多一笔带过，不要放成主文献**

## 三、不建议纳入当前主线正文（避免“擦边入选”）

### A. 偏忆阻器 / 阵列 / 泛神经形态综述
- Memristive crossbar arrays for brain-inspired computing
- Synaptic devices based neuromorphic computing applications in artificial intelligence

原因：范围太大，且重心偏 **忆阻器 / 阵列 / 泛神经形态器件**，不适合支撑当前“多侧栅树突突触晶体管”主线。

### B. 偏生物理论 / 计算神经科学，而非器件论文
- When Less Is More: Non-monotonic Spike Sequence Processing in Neurons
- A triplet spike-timing-dependent plasticity model generalizes the BCM rule to higher-order spatiotemporal correlations
- Parallel synapses with transmission nonlinearities enhance neuronal classification capacity

原因：这些文献可作为“理论启发”，但不适合放进当前器件综述正文作为核心依据，除非后续单独写生物启发理论背景。

### C. 偏非本课题主线的器件方向
- Artificial non-monotonic neurons based on nonvolatile anti-ambipolar transistors
- High-Precision Multibit Opto-Electronic Synapses Based on ReS2/h-BN/Graphene Heterostructure
- High-temperature optoelectronic synaptic devices based on 4H-SiC
- Carbon nanotube-based bio-inspired neuron systems via cascaded TFT-driven LEDs and optoelectronic synaptic transistors

原因：
- 虽然其中部分涉及“非单调”或“突触器件”，但核心重心偏 **非单调神经元 / 光电突触 / 异质结构 / 生物启发系统级集成**
- 与你的“**多侧栅树突突触晶体管 + 空间距离效应 + 时空相关可塑性 + 仿真闭环**”主线距离仍然偏大
- 若硬塞进正文，会稀释论证重心

## 四、对第一章各小节的直接帮助

### 对 1.2.1（突触晶体管及侧栅/多栅结构研究进展）
优先使用：
1. Multi-Gate Organic Neuron Transistors for Spatiotemporal Information Processing
2. Spatiotemporal Information Processing Emulated by Multiterminal Neuro-Transistor Networks
3. Oxide dendrite transistors gated with polyvinyl alcohol/chitosan hybrid electrolyte for spatiotemporal integration

### 对 1.2.2（栅距对 EPSC、PPF 等突触行为影响的研究进展）
优先使用：
1. Multi-Gate Organic Neuron Transistors for Spatiotemporal Information Processing
2. Spatiotemporal Information Processing Emulated by Multiterminal Neuro-Transistor Networks（辅助）

备注：
- 这批文献里，真正能**直接且有力**支撑“栅距/空间距离对 EPSC、PPF 的影响”的，仍然是 **Qian 2017** 最强。
- 也就是说，这份合集虽然能补强你的“多栅/时空处理”部分，但对 `1.2.2` 的专门证据仍然**不算充足**。

### 对 1.2.3（时空整合与储备池计算相关研究进展）
优先使用：
1. Transistor-Structured Artificial Dendrites for Spatiotemporally Correlated Reservoir Computing
2. Oxide dendrite transistors gated with polyvinyl alcohol/chitosan hybrid electrolyte for spatiotemporal integration
3. Spatiotemporal Information Processing Emulated by Multiterminal Neuro-Transistor Networks
4. Multi-Gate Organic Neuron Transistors for Spatiotemporal Information Processing

## 五、总判断

如果严格按“不要擦边就放进去”的标准，这包文献里：

- **强烈建议真正重点用：4 篇**
- **可做背景补充：2 篇**
- **其余不建议塞进当前主线正文**

其中最值得抓住的组合是：
- `Qian 2017`（多栅 + 栅距 + EPSC/PPF）
- `He 2019`（多端神经晶体管 + 时空序列处理）
- `Huang 2025`（氧化物树突晶体管 + 时空整合）
- `Ni 2025`（人工树突 + 厘米级距离 + 储备池计算）

## 六、后续建议

1. 写 `1.2.1` 时：以 **Qian 2017 + He 2019 + Huang 2025** 为主线
2. 写 `1.2.2` 时：以 **Qian 2017** 为核心证据，He 2019 仅作辅助
3. 写 `1.2.3` 时：以 **Ni 2025 + Huang 2025 + He 2019** 为主线
4. 若要把 `1.2.2` 写得更硬，仍建议后续**定向补充“距离/栅距影响 EPSC/PPF”更直接的论文**
