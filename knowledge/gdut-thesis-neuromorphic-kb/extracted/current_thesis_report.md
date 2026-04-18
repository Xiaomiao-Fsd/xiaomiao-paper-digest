# Extracted from current_thesis_report.docx

-21907566675

本科毕业设计（论文）

基于时空非单调相关可塑性的神经形态突触器件仿真验证

学 院 集成电路学院

专 业 微电子科学与工程

年级班别 2022级（1）班

学 号 3122009664

学生姓名 黎展睿

任课教师 陈雅怡

2026年 4月

摘要

随着人工智能与物联网技术的快速发展，传统冯·诺依曼架构逐渐暴露出存储墙和高功耗等问题，难以同时满足高并行、低延迟和低能耗的信息处理需求。神经形态计算通过在硬件层面融合存储与计算、模拟生物神经系统的事件驱动和并行处理机制，被认为是突破上述瓶颈的重要方向。作为神经形态系统的重要基础单元，能够实现可塑性调控的突触器件因此成为当前研究热点。

现有研究大多集中于时间相关可塑性，而对空间相关可塑性的探索仍较有限；已有空间可塑性研究通常局限于微米尺度，并多表现为随距离增加而单调衰减的响应规律。与此同时，空间可塑性的物理机制尚缺乏充分解释，尤其是在突触输入物理位置如何调控器件权重更新方面，仍缺少系统性的建模与验证。针对这些不足，本文以多侧栅树突突触晶体管为对象，尝试在更大空间尺度上研究时空耦合下的非单调相关可塑性，并从器件、模型和应用三个层面建立相互印证的分析框架。

在模型与方法方面，本文结合COMSOL和Silvaco TCAD开展联合仿真。在本研究中，展示了一种晶体管结构的人工树突（TSAD），在厘米尺度上实现了空间非单调突触效能。观察到的兴奋性突触后电流（EPSC）随距离呈非单调趋势，超越了传统单调离子扩散的限制。结合多物理场模拟与复阻抗分析，本文揭示这一现象来源于离子迁移效率与亚饱和离子环境中有限离子可用性之间的动力学竞争。结合仿真与实测，利用这些内在动力学，实现了一种TSAD-RC，对28类复杂时间信号的识别准确率达到100%，阐明了宏观尺度非单调时空整合的物理本质。

关键词：时空非单调可塑性、突触晶体管、多侧栅树突结构、离子动力学分析、器件仿真、算法训练

Abstract

With the rapid advancement of artificial intelligence and the Internet of Things, the traditional von Neumann architecture has increasingly revealed shortcomings such as the memory wall and high-power consumption, making it difficult to simultaneously satisfy the demands of highly parallel, low-latency, and energy-efficient information processing. Neuromorphic computing, which integrates storage and computation at the hardware level and emulates the event-driven and parallel-processing mechanisms of biological neural systems, is widely regarded as a promising route to overcoming these bottlenecks. Accordingly, synaptic devices capable of plasticity modulation have become a major focus of current research as fundamental building blocks of neuromorphic systems.

Existing research has largely concentrated on temporal plasticity, whereas spatial plasticity has received relatively limited attention. Reported studies of spatial plasticity are typically restricted to the micrometer scale and generally show a monotonic decay in response with increasing distance. Meanwhile, the physical mechanisms underlying spatial plasticity remain insufficiently understood. In particular, systematic modeling and validation are still lacking with respect to how the physical locations of synaptic inputs regulate device weight updates. To address these issues, this paper investigates spatiotemporally coupled non-monotonic correlated plasticity over a larger spatial scale using a multi-side-gate dendritic synaptic transistor as the research platform, and establishes a mutually corroborative analytical framework spanning device, model, and application.

For modeling and methodology, joint simulations were carried out using COMSOL and Silvaco TCAD. In this work, a transistor-structured artificial dendrite (TSAD) is demonstrated to achieve spatially non-monotonic synaptic efficacy at the centimeter scale. The observed excitatory postsynaptic current (EPSC) exhibits a non-monotonic dependence on distance, surpassing the limitation of conventional monotonic ion diffusion. Combined multiphysics simulations and complex impedance analysis reveal that this phenomenon arises from the dynamic competition between ion migration efficiency and the limited availability of ions in a subsaturated ionic environment. By integrating simulation and experimental results and leveraging these intrinsic dynamics, a TSAD-RC is realized, achieving 100% recognition accuracy for 28 classes of complex temporal signals and thereby elucidating the physical basis of macroscale non-monotonic spatiotemporal integration.

Keywords: spatiotemporal non-monotonic correlated plasticity; synaptic transistor; multi-side-gate dendritic structure; ion dynamics analysis; device simulation; algorithm training

目录

TOC \t "标题 2,1,标题 3,2,标题 4,1,标题,3" 1绪论 PAGEREF _Toc227327547 \h 1

1.1研究背景与意义 PAGEREF _Toc227327548 \h 1

1.1.1冯·诺依曼架构瓶颈与神经形态计算的发展需求 PAGEREF _Toc227327549 \h 1

1.1.2突触晶体管在神经形态系统中的作用与研究价值 PAGEREF _Toc227327550 \h 1

1.1.3时空相关可塑性研究的理论意义与应用意义 PAGEREF _Toc227327551 \h 1

1.2国内外研究现状 PAGEREF _Toc227327552 \h 2

1.2.1突触晶体管及侧栅/多栅结构的研究进展 PAGEREF _Toc227327553 \h 2

1.2.2栅距对 EPSC、PPF 等突触行为影响的研究进展 PAGEREF _Toc227327554 \h 3

1.2.3时空信息整合与储备池计算相关研究进展 PAGEREF _Toc227327555 \h 4

1.2.4现有研究的局限性与本文研究切入点 PAGEREF _Toc227327556 \h 5

1.3本文研究内容与创新点 PAGEREF _Toc227327557 \h 5

1.4论文结构与安排 PAGEREF _Toc227327558 \h 6

2器件结构与时空可塑性评价标准 PAGEREF _Toc227327559 \h 7

2.1侧栅/多栅突触晶体管结构与工作机理 PAGEREF _Toc227327560 \h 7

2.1.1器件结构设计与电极布局 PAGEREF _Toc227327561 \h 7

2.1.2工作机理与时空信号调控 PAGEREF _Toc227327562 \h 9

2.2EPSC、PPF、SNDP等指标定义与提取方法 PAGEREF _Toc227327563 \h 11

2.2.1典型突触行为表征指标 PAGEREF _Toc227327564 \h 11

2.2.2时空相关可塑性评价方法 PAGEREF _Toc227327565 \h 11

2.2.3指标提取与计算方法 PAGEREF _Toc227327566 \h 12

2.3“可重构源漏栅”结构的建模假设与等效描述 PAGEREF _Toc227327567 \h 12

2.3.1建模假设与边界条件 PAGEREF _Toc227327568 \h 12

2.3.2等效结构描述与参数映射 PAGEREF _Toc227327569 \h 12

3COMSOL离子动力学仿真与非单调机理分析 PAGEREF _Toc227327570 \h 14

3.1器件模型、边界条件与参数设置 PAGEREF _Toc227327571 \h 14

3.1.1控制方程与求解区域 PAGEREF _Toc227327572 \h 14

3.1.2边界条件与参数设定 PAGEREF _Toc227327573 \h 14

3.2不同侧栅间距下离子浓度/电势分布 PAGEREF _Toc227327574 \h 14

3.2.1离子浓度分布特征 PAGEREF _Toc227327575 \h 14

3.2.2电势分布与沟道耦合 PAGEREF _Toc227327576 \h 14

3.3非单调离子迁移效率序列的形成条件与敏感性分析 PAGEREF _Toc227327577 \h 14

3.3.1非单调形成条件分析 PAGEREF _Toc227327578 \h 14

3.3.2关键参数敏感性分析 PAGEREF _Toc227327579 \h 14

4Silvaco TCAD电学仿真与突触行为复现 PAGEREF _Toc227327580 \h 15

4.1漂移-扩散模型与材料参数 PAGEREF _Toc227327581 \h 15

4.1.1物理模型与求解方法 PAGEREF _Toc227327582 \h 15

4.1.2材料参数与器件设定 PAGEREF _Toc227327583 \h 15

4.2转移/输出特性与等效栅调制 PAGEREF _Toc227327584 \h 15

4.2.1转移与输出特性分析 PAGEREF _Toc227327585 \h 15

4.2.2等效栅调制效应 PAGEREF _Toc227327586 \h 15

4.3脉冲响应：EPSC衰减、STP→LTP、PPF随Δt变化及其空间非单调性 PAGEREF _Toc227327587 \h 15

4.3.1EPSC衰减特性 PAGEREF _Toc227327588 \h 15

4.3.2STP向LTP演化行为 PAGEREF _Toc227327589 \h 15

4.3.3PPF随Δt变化及空间非单调性 PAGEREF _Toc227327590 \h 15

4.4仿真结果与机理讨论 PAGEREF _Toc227327591 \h 15

4.4.1仿真结果对照分析 PAGEREF _Toc227327592 \h 15

4.4.2非单调机理讨论 PAGEREF _Toc227327593 \h 16

5器件制备与实验验证 PAGEREF _Toc227327594 \h 17

5.1工艺流程与关键步骤电学测试平台与测试方法 PAGEREF _Toc227327595 \h 17

5.1.1器件制备流程 PAGEREF _Toc227327596 \h 17

5.1.2关键工艺步骤与控制要点 PAGEREF _Toc227327597 \h 17

5.2实验结果、统计分析与模型回标 PAGEREF _Toc227327598 \h 17

5.2.1测试平台与仪器配置 PAGEREF _Toc227327599 \h 17

5.2.2测试流程与数据采集方法 PAGEREF _Toc227327600 \h 17

5.3面向储备池计算的时空编码验证 PAGEREF _Toc227327601 \h 17

5.3.1基本电学与突触响应结果 PAGEREF _Toc227327602 \h 17

5.3.2统计分析与模型回标 PAGEREF _Toc227327603 \h 17

5.4面向储备池计算的时空编码验证 PAGEREF _Toc227327604 \h 17

5.4.1输入编码与任务构建 PAGEREF _Toc227327605 \h 17

5.4.2识别结果与性能分析 PAGEREF _Toc227327606 \h 17

6结论与展望 PAGEREF _Toc227327607 \h 18

参考文献 PAGEREF _Toc227327608 \h 19

致谢 PAGEREF _Toc227327609 \h 21

绪论

研究背景与意义

冯·诺依曼架构瓶颈与神经形态计算的发展需求

随着人工智能和物联网技术的快速发展，图像识别、模式分类和时序信号处理等任务对计算系统的并行性、实时性和能效提出了更高要求。传统冯·诺依曼架构中存储单元与计算单元相互分离，数据需要在二者之间频繁搬运，容易引发“存储墙”问题，并带来延迟增加、效率下降和能耗上升等限制，难以适应神经网络规模持续扩大和信息处理复杂度不断提升的需求。尤其在高并行、事件驱动的智能任务中，传统架构的适配性不足愈发明显，已难以充分满足新型智能硬件对高效感知、计算与存储协同的要求。为突破这一瓶颈，研究者借鉴生物神经系统中神经元与突触协同工作的机制，提出了神经形态计算。该范式强调在硬件层面实现存储与计算融合，具备并行处理、事件驱动和自适应学习等特点，被认为是实现高效智能信息处理的重要路径，也为新型类脑器件与系统结构研究提供了明确方向。

突触晶体管在神经形态系统中的作用与研究价值

在神经形态系统中，突触负责信息传递、权值调节以及学习记忆，是实现类脑计算的关键单元。因此，能够模拟突触行为的器件是神经形态硬件实现的重要基础。突触晶体管兼具晶体管的电学调控特性与突触功能模拟能力，可通过栅极调控和脉冲刺激实现沟道电导连续变化，进而表征兴奋性突触后电流、成对脉冲易化以及短时、长时可塑性等典型行为。与传统器件相比，突触晶体管在结构设计、参数调控和多端输入响应方面更具灵活性，既可承担类突触权值存储与更新功能，也有助于实现多输入信息整合和神经网络硬件映射。特别是在多侧栅结构中，其对多路信号的协同调制能力更为突出，因此成为连接器件特性、突触行为与系统应用的重要载体，在神经形态器件研究中具有突出的理论与工程价值，也为后续开展复杂时空调制研究提供了器件基础。

时空相关可塑性研究的理论意义与应用意义

生物神经系统对信息的处理具有明显的时间相关性与空间相关性，突触可塑性不仅取决于刺激强度，还与输入的先后顺序、位置分布及多输入协同作用密切相关。因此，从时空相关角度研究突触可塑性，有助于更真实地揭示神经信息编码与学习机制，并为类脑模型构建提供依据。对突触晶体管而言，时空相关可塑性研究能够反映器件在复杂刺激条件下的动态响应和多输入整合能力，并进一步评估其在特征提取、非线性映射和动态状态表征中的应用潜力。这些特征直接关系到系统对时空信息的利用效率，对于图像识别、模式分类、时序信号处理以及储备池计算等任务具有重要意义，也为后续开展多侧栅结构器件的时空非单调调制行为的研究、机制分析与仿真验证奠定了基础。与此同时，该研究也有助于推动器件层特性向系统级功能实现的有效转化。

国内外研究现状

突触晶体管及侧栅/多栅结构的研究进展

从早期单晶体管硅突触到后续电解质栅控有机晶体管，相关研究已证明这一路线能够稳定模拟数据存储与突触可塑性调节过程[1-2]。随着晶体管型人工突触研究的系统展开，已有综述普遍认为三端结构在读写分离、权值线性调控和低功耗集成方面较两端忆阻器更具优势，因此成为神经形态器件的重要分支[3-4]。

图1.1 一种CNT突触晶体管示意图[5]

图1.1展示了Kim等报道的以碳纳米管作为沟道层，氢掺杂聚乙二醇单甲醚（PEG） 作为栅介质层的突触晶体管。这种无机半导体突触晶体管具有良好的稳定性和较高的载流子迁移率。在此基础上，侧栅/多栅结构进一步把多个面内输入端引入同一沟道区域，使器件能够表征来自不同空间位置的刺激并模拟树突式输入整合，这一点已在多栅有机神经元晶体管和离子凝胶侧栅石墨烯突触晶体管中得到验证[6]。

图1.2 一种带有离子凝胶门控的有机突触晶体管的示意图

图1.2展示了一种多栅器件的结构[7]，其中两个平面内的前突触输入同时施加在栅极G0和另一个栅极Gx（x=1~6）。这种晶体管的时空树突状与相关输入的整合可以通过两个栅极的空间相对位置发生不同的响应变化。同时近年的二维铁电晶体管和器件综述研究又表明，晶体管型人工突触正由单纯行为演示转向高精度、多功能和更强结构可设计性的方向发展，但其核心仍在于如何把器件结构优势转化为更有效的时空信息处理能力[8-9]。

栅距对 EPSC、PPF 等突触行为影响的研究进展

在多栅或侧栅突触晶体管研究中，栅极与沟道之间的空间距离已被证明会显著影响兴奋性突触后电流（EPSC）峰值、衰减过程和成对脉冲易化（PPF）等短时动态行为，因此栅极间距实际上是耦合电场分布与离子迁移过程的关键结构参数[10-11]。在图1.2展示的有机突触晶体管中，不同面内栅—沟道距离会造成明显不同的EPSC与PPF响应，说明空间位置本身已经参与突触权重的动态编码。同时，在侧向离子栅控石墨烯突触晶体管中观察到器件响应可由成对脉冲易化逐步转向成对脉冲抑制，表明有效栅控长度变化不仅会改变响应强度，还可能改变器件对脉冲序列的过滤方式[11]。

图1.3 多栅极器件的一种计算应用方式

多栅树突结构可以通过不同空间输入形成差异化时空整合响应，结构尺度与输入位置共同决定了器件的加和、逻辑和突触行为表达。如图1.3所示[12]，多栅树突晶体管在异突触调制机制下可将不同输入端的刺激映射为可区分的输出状态，并进一步实现 OR、AND、NOR 和 NAND 等逻辑功能，表明多栅结构不仅能够表达突触行为，还具备面向信息处理的功能扩展能力。然而，现有文献整体上仍更重视功能演示而非参数规律归纳，对于栅极间距、局域电容、离子扩散和瞬态权重更新之间的定量对应关系，相关综述和研究总结仍显不足[3,9]。

时空信息整合与储备池计算相关研究进展

随着多侧栅和树突式结构的发展，突触晶体管的研究目标已由单一突触功能模拟扩展到时空信息整合、序列判别和类脑计算任务映射[10]。除电信号外，侧栅石墨烯突触晶体管还可以引入光刺激辅助记忆与联想学习，这说明多端晶体管平台具备把多模态输入纳入时空编码的潜力[7]。进一步地，多端离子调控晶体管已被用于构建具有宽时间动态范围的硬件储备池，表明器件内生的短时记忆和非线性可以直接承担时序特征展开的功能[13]。

图1.4 （a）通过单栅极实现五位二进制数值识别 （b）四组平行实验的识别结果波动范围

将晶体管结构人工树突、可交换源漏栅结构和厘米级空间扩展结合起来，如图1.4所示的神经网络识别结果[14]，多栅突触晶体管可以实现面向时空相关任务的器件验证，说明人工树突器件在复杂输入处理方面具有进一步拓展的可能。总体而言，现有这类研究更多聚焦于时空整合能力展示、联想记忆或储备池任务验证，为多栅器件的应用探索提供了基础，但对时空耦合条件下突触响应规律本身的讨论仍相对有限[8,15]。

现有研究的局限性与本文研究切入点

总体来看，现有突触晶体管研究在单独时间维度的可塑性模拟方面已较为成熟，围绕短时/长时可塑性、突触权值调节及典型时间响应行为的器件实现与性能表征已经较为充分[1-2]。相比之下，面向时空信号处理的研究虽然已借助多栅、侧栅和树突式结构展示出多输入整合与序列处理能力，但现有多栅器件报道中的可塑性响应大多仍表现为随空间位置、栅距或刺激条件变化而单调增强或单调衰减，对非单调时空可塑性器件的系统研究仍明显不足[4,15]。这意味着相关领域在能够直接反映复杂时空耦合特征的非单调响应器件方面仍存在一定空缺[11-14]。因此，本文的切入点将重点放在多侧栅树突突触晶体管的时空信号处理能力上，着重通过仿真数据确定器件在不同栅距和时间关联条件下的非单调时空可塑性规律，再结合器件制备与实验测试结果对仿真结论进行佐证，从而突出本器件以非单调时空可塑性为核心特征的研究重点。

本文研究内容与创新点

针对现有研究在时空耦合可塑性研究方面，当前关于突触晶体管时空相关可塑性的研究虽已取得一定进展，但对于非单调时空响应的规律认识、机理解释及实验佐证仍有待进一步完善。基于此，本文选取多侧栅树突突触晶体管作为研究对象，重点围绕器件电学特性、离子动力学行为和实验验证三个层面开展研究，以期对其非单调时空可塑性进行较为系统的分析。

基于上述研究目标，本文的研究内容主要包括以下三个方面：

离子动力学机理分析。基于COMSOL构建离子迁移、电势分布与等效电容耦合模型，重点考察不同栅距和时间关联条件下器件时空响应的变化规律，并解释非单调时空可塑性的形成机制；

器件电学特性仿真与突触行为表征。基于Silvaco TCAD建立多侧栅树突突触晶体管的电学模型，围绕兴奋性突触后电流、成对脉冲易化等典型突触行为，分析不同结构参数与刺激条件下的响应特征；

器件制备与实验验证。完成器件制备并在探针台上开展电学测试，对仿真结果进行实验佐证与参数对照，进一步验证器件在时空信息处理中的实现基础。

本文的创新点主要是将研究重点由常见的单调时空响应推进到厘米尺度下的非单调时空相关可塑性，并围绕空间位置参与突触权重调控这一问题构建多侧栅树突器件结构与表征体系；同时从电学响应和离子输运两条路径建立联合分析框架，对非单调响应的来源给出较为完整的机理解释，揭示其与离子迁移效率及有限离子可用性之间的动力学竞争密切相关；而后通过器件制备和探针台测试对模型分析进行实验验证，并以时序识别等任务作为辅助说明，体现该器件在类脑时空信息处理中的应用潜力。

论文结构与安排

为清晰展示本文的研究思路与整体安排，全文结构安排如下：第一章为绪论，主要介绍研究背景与意义、国内外研究现状、本文研究内容与创新点以及论文结构安排。第二章围绕多侧栅树突突触晶体管的器件结构与时空可塑性评价标准展开，重点介绍器件结构与工作机理、典型突触行为评价指标以及“可重构源漏栅”结构的建模假设与等效描述。第三章基于COMSOL开展离子动力学仿真与非单调机理分析，研究不同侧栅间距条件下离子浓度、电势分布及离子迁移效率的变化规律。第四章基于Silvaco TCAD 开展电学仿真，复现器件的转移/输出特性及典型突触行为，并结合仿真结果讨论器件的非单调时空响应特征。第五章围绕器件制备与实验验证展开，介绍工艺流程、测试平台与方法，并对实验结果进行统计分析和模型回标，同时结合时空编码任务对器件的应用潜力进行补充验证。第六章对全文工作进行总结，并对后续研究方向做出展望。

器件结构与时空可塑性评价标准

为便于后续 COMSOL 离子动力学仿真、Silvaco TCAD 电学建模以及实验结果之间的对应分析，本章以当前器件样品方案为基础，对多侧栅树突突触晶体管的器件结构、基本工作机理和时空可塑性评价标准进行说明，并进一步给出与仿真相匹配的等效建模假设。

SG1

SG2

SG4

SG3

…

∆t

SG1

SG2

SG4

SG3

…

∆t

图2.1 多栅突触晶体管的概念图，原理为一个生物树突接收多空间信号。

为更直观说明本研究器件的仿生设计思路，图2.1 给出了其所模拟的树突式输入整合形态示意。与生物神经元中树突对不同空间位置突触输入进行接收与整合的过程类似，多侧栅树突突触晶体管通过在同一平面工作区引入多个侧栅输入端，实现了对空间分布刺激的映射与调控。基于这一仿生对应关系，下面进一步对器件的具体结构、电极布局及其工作机理展开分析。

侧栅/多栅突触晶体管结构与工作机理

本文所研究的器件属于平面多侧栅突触晶体管，通过在同一沟道周围设置多个具有不同距离位置的输入栅，实现对空间传输距离的硬件映射。与传统单栅结构不同，该器件并非仅利用单一栅端调制沟道电导，而是利用多个侧栅在横向空间上的位置差异，使相同脉冲在不同输入端激发出不同的突触后响应。

器件结构设计与电极布局

图2.2 突触晶体管器件的横截面示意图

结合当前样品方案，如图2.2横截面所示，由下往上，器件采用依次层叠的 SiO2 衬底、ITZO 有源层和明胶离子胶栅介质层结构，并在介质层两侧设置一对 Au 源漏电极，4对侧栅电极，电极之间间隔相等均匀排布，栅介质层与电极对之间紧密贴合、无间隙。该设置可有效避免电场畸变，降低接触电阻，抑制漏电流，从而提升突触晶体管的电学稳定性与可靠性。实际器件结构各层材料尺寸由下表2.1给出：

表2.1 突触晶体管的结构参数

器件结构

结构材料

结构大小（mm）

结构厚度（mm）

衬底

SiO2

5.5*6.5

1.2

有源层

ITZO

5.5*6.5

20e-6

电极层

Au

0.55*0.55

0.1

栅介质层

明胶离子胶

3.4*4.4

1

器件平面内设置一对源漏极输入输出端，再添加4 对侧栅输入端，每一级侧栅与读出端之间的中心距按毫米量级逐级增加，由此构成具有传输距离差异的树突式输入阵列。在实际测试中，可以任选其中一对电极作为源漏，其余8个任取一个作为栅极进行测试。

图2.3 器件结构预览

基于上述尺寸，图2.3展示了该突触晶体管的3d模型示意图。其中浅蓝色为SiO2衬底，蓝色为ITZO有源层，黄色为Au电极，灰色则是明胶离子胶的栅介质层。需要注意的是，明胶离子胶是在器件制备完成后，另外制备出胶体原料通过裁切的方式覆盖到电极有效工作区上，所以实际上栅介质是一层覆盖在金电极和ITZO有源层工作区间的一层软体结构。该结构一方面保证了氧化物沟道具有稳定的晶体管读出能力，另一方面又借助离子介质赋予器件可观的时序调控能力，为研究距离反馈型突触响应提供了结构支撑。

在后续的COMSOL和Silvaco仿真中，仿真器件结构数据都会使用该3d模型的尺寸数据，以保证器件仿真结果的一致性。

工作机理与时空信号调控

在器件仿真与实验测试过程中，通常将底部一对电极作为源漏读出端，并在其间施加较小的读取偏压；上方多个侧向电极则根据测试需求选作单栅或双栅输入端，并施加脉冲刺激。在源漏两端施加较小的读取偏压（如0.3V），在侧栅端施加3V左右的脉冲刺激。受脉冲电场驱动，明胶离子胶中的可迁移离子会在横向界面重新分布，并在 ITZO 沟道表面形成电荷调制层，从而改变沟道载流子输运状态，表现为突触后电流响应。

Ionic-gate dielectric layer

ITZO

D

G

S

Polymer skeleton

Drive away

V

V

Proton

Electron

Ionic-gate dielectric layer

ITZO

D

G

S

Polymer skeleton

Drive away

V

V

Proton

Electron

图2.4 器件沟道离子迁移示意图

如图2.4所示，当侧栅端施加脉冲电压后，明胶离子胶中的可迁移离子在横向电场驱动下沿器件表面发生重新分布，并逐渐向沟道附近迁移聚集。由于离子凝胶与 ITZO 有源层之间存在界面耦合作用，离子在沟道邻近区域的富集会改变沟道表面的局部电势环境，进而调制沟道载流子浓度与输运行为，使漏源电流产生瞬态变化，表现为典型的兴奋性突触后电流（EPSC）响应：

ΔIEPSC=Ipeak-I0 （2.1）

式（2.1）即为EPSC的定义式，其中Ipeak为脉冲作用后的峰值电流，I0为脉冲施加前的初始电流。脉冲撤去后，原先聚集的离子将逐步回扩散，沟道调制作用减弱，器件电导随之恢复，因此该器件能够呈现明显的短时记忆和历史依赖特征。

与传统单栅结构不同，多侧栅树突突触晶体管的关键特征在于：不同输入端对应不同的空间位置，因而其与沟道读出区域之间存在不同的传输距离与耦合路径。当相同幅值和宽度的脉冲施加于不同侧栅时，离子迁移路径长度、界面调制效率以及局部离子参与程度均会发生变化，从而使沟道输出呈现出与输入位置相关的差异化瞬态响应。换言之，空间位置不再只是几何排布参数，而是直接参与器件权重调控与信号表达的重要因素。

此外，在多输入条件下，器件的响应不仅取决于单个脉冲本身，还同时受到输入顺序、时间间隔和空间位置组合的共同影响。近距离输入通常具有更强的界面耦合能力，而较远位置的输入则可能表现出不同的迁移延迟和调制效率。由此，器件在时域和空域两个维度上均可形成差异化响应特征，并为后续开展时空耦合可塑性分析提供物理基础。也正是基于这种“空间位置—离子迁移—沟道调制—瞬态输出”的链式关系，多侧栅结构得以模拟生物树突对分布式输入信号的接收与整合过程，从而体现出神经形态器件在复杂时空信息处理方面的应用潜力。

EPSC、PPF、SNDP等指标定义与提取方法

为对器件的时空响应能力进行定量分析，需要建立统一的突触行为表征指标和数据提取方法。考虑到本研究既关注单脉冲和双脉冲下的瞬态响应，也关注多脉冲训练和时空耦合条件下的权重演化，因此本节从典型突触行为、时空相关评价以及指标提取三个方面进行说明。

典型突触行为表征指标

EPSC 用于描述前突触脉冲作用后沟道电流的瞬态增强过程，通常以峰值电流、响应延迟、衰减时间和积分面积等量进行表征。PPF 用于反映相邻两次脉冲在短时间间隔内对第二次响应的促进作用，其指标一般定义见式（2.2）：

PPF=A2A1×100 （2.2）

其中 A1 和 A2 分别表示第一、第二个脉冲对应的 EPSC 峰值。当脉冲训练次数增加或刺激频率提升时，器件还可能表现出由短时可塑性向长时可塑性过渡的行为，可分别用 STP 和 LTP 描述。此外，针对多脉冲与频率调制过程，本文采用 SNDP 表征脉冲数目及脉冲频率变化对突触权重更新的影响：

SNDP(n)=In-I1I1 （2.3）

式（2.3）描述的是脉冲数增加时权重更新的量化方式，其中In为第n个脉冲后的响应，反应了在不同脉冲数量下SNDP的强度。

时空相关可塑性评价方法

本研究关注的时空相关可塑性不仅取决于脉冲宽度、间隔时间、频率和幅值等时间维度参数，还与侧栅位置、栅距以及输入顺序等空间维度参数密切相关。因此，在评价方法上，需要同时考察“同一位置下随时间参数变化的响应规律”和“同一时间条件下随空间位置变化的响应规律”，并进一步构建 Δt-d 等耦合变量下的二维比较。对于本文重点讨论的非单调时空可塑性，可通过比较不同栅距对应响应峰值、权重变化率或归一化输出随距离变化的趋势来判断：

EPSCnorm=EPSCiEPSCmax （2.4）

式（2.4）通过直接比较不同栅极的EPSC来判断当前响应的强度；当响应随距离不再单调衰减，而是在特定区间出现峰值、拐点或峰谷转换时，可认为器件具备非单调时空相关特征。

指标提取与计算方法

在具体数据处理过程中，本文统一在固定漏源偏压下记录沟道瞬态电流曲线，并从中提取峰值电流、稳态电流、恢复时间和积分面积等基本量。对于 PPF 等双脉冲指标，以相邻两次脉冲对应的峰值电流直接计算比值，并结合双指数衰减形式对其随 Δt 的变化进行拟合；对于 STP/LTP、SNDP 等多脉冲行为，则通过比较训练前后电流变化量、峰值增益及归一化权重演化趋势进行表征。为便于后续比较不同侧栅、不同结构参数及不同模型结果，部分指标还需进行归一化处理，以减小绝对电流量级差异带来的影响。

“可重构源漏栅”结构的建模假设与等效描述

虽然器件的物理结构已经较为明确，但在后续多物理场仿真和 TCAD 电学仿真中，仍需要将实际版图抽象为可计算的等效结构。特别是对于多侧栅输入、多距离比较以及不同测试工况切换，仅依靠工艺层面的描述还不足以支撑模型建立，因此有必要在本节中给出统一的建模假设与参数映射关系。

建模假设与边界条件

后续模型以 SiO2 / ITZO / 明胶离子胶 / Au 电极这一实际器件结构为基础，并对其进行适度理想化处理。具体而言，默认衬底仅起机械支撑作用，不参与导电；ITZO 有源层在工作区域内厚度均匀、材料参数均一；Au 源漏电极和侧栅电极视为理想欧姆接触；明胶离子胶在有效覆盖区域内连续分布，初始离子浓度均匀。考虑到实验测试中关注的是不同侧栅位置引起的输出差异，模型将主要保留侧栅—沟道距离、介质厚度、界面电势和离子分布等关键变量，而对非主导因素作适当简化。

等效结构描述与参数映射

尽管器件在实验上具有固定的源漏与侧栅布局，但从建模角度仍可将其统一抽象为“读出端—多输入端”的平面侧向耦合结构：源漏电极承担沟道电流读取功能，各侧栅电极作为不同空间位置的前突触输入端。这样处理后，不同侧栅工况之间的差异便可归结为输入端与读出端相对位置不同所导致的界面电势、离子迁移效率和等效调控强度差异。对于 COMSOL 仿真，侧栅位置主要映射为离子浓度演化、电势分布和等效电容差异；对于 TCAD 仿真，则可进一步转化为等效表面电荷、界面势垒变化或局域载流子调制强度，从而建立由空间结构到电学输出的统一参数链。

COMSOL离子动力学仿真与非单调机理分析

控制方程、求解区域与参数设置

为分析多侧栅树突突触晶体管在不同侧栅间距条件下的离子迁移行为及其对沟道调制的影响，本文基于 COMSOL Multiphysics 建立离子传输—静电场耦合模型。考虑到器件工作过程中未引入明显的法拉第反应，本文采用以 Nernst–Planck 方程和 Poisson 方程为核心的 PNP 描述框架，对明胶离子胶中的离子迁移、扩散及其与局部电势之间的耦合关系进行数值求解。

其中，式（3.1）用于描述离子在浓度梯度和电场共同作用下的迁移通量平衡，式（3.2）用于建立空间电荷与电势分布之间的对应关系，式（3.3）则用于对沟道耦合区域内的净离子积累量进行积分表征。三者共同构成后续分析不同栅距条件下离子浓度分布、电势耦合强度以及非单调迁移效率序列的理论基础。

控制方程与求解区域

在 COMSOL 模型中，离子凝胶中的离子迁移过程主要由扩散和电迁移共同决定。忽略体均相反应后，单一离子组分 i 的通量守恒关系可写为：

∇·[-D_i∇c_i-(z_iD_iF/RT)c_i∇φ]=0 （3.1）

式（3.1）对应准稳态 Nernst–Planck 形式，其中 D_i、c_i 和 z_i 分别表示第 i 种离子的扩散系数、浓度和化合价，F 为法拉第常数，R 为气体常数，T 为绝对温度，φ 为电势。该式反映了离子在“浓度梯度驱动的扩散”与“电场驱动的迁移”共同作用下达到的局部通量平衡状态。

-∇·(ε_0ε_r∇φ)=F∑_i z_ic_i （3.2）

式（3.2）为 Poisson 方程，其中 ε_0 为真空介电常数，ε_r 为介质相对介电常数，右端 F∑_i z_ic_i 表示由正、负离子重新分布形成的空间电荷密度。该式用于描述离子积累如何改变局部电势分布，并进一步影响沟道附近的等效栅控能力。

为进一步比较不同侧栅位置下沟道耦合区域的有效离子积累强弱，本文引入净离子电荷积分量作为定量指标，其表达式为：

Q_net=∭_Ω(z^+c^+-z^-c^-)dV （3.3）

式（3.3）中，Ω 表示与沟道调控最相关的离子积分区域，Q_net 用于表征该区域内的净离子积累程度。对于本文研究的多侧栅结构，不同侧栅对应的 Q_net 大小可直接用于比较各输入位置的界面调控强度，并为解释 EPSC 随距离呈现非单调变化提供中间物理量支撑。

求解区域主要包括明胶离子胶层、ITZO 有源层邻近区域以及与其接触的金属电极边界。其中，明胶离子胶区域承担离子迁移与浓度演化的主要求解任务；有源层邻近区域主要用于表征界面电势变化对沟道调制的影响。通过上述控制方程与求解区域设置，可较为完整地描述多侧栅输入条件下器件内部离子运动、电势耦合及净离子积累量变化的基本物理过程。

边界条件与参数设定

在边界条件设置方面，本文将与输入信号对应的侧栅电极施加脉冲电压激励，读出端保持与实验测试一致的低偏压条件，其余未参与当前工况的电极根据具体仿真需求设置为参考边界或绝缘边界。对于离子凝胶区域，初始时刻假定可迁移离子均匀分布，以保证不同栅距条件下仿真结果具有可比性；对器件外边界则采用无通量或电绝缘近似，以避免外部边界对有效工作区内离子迁移行为产生额外干扰。

在参数选取方面，模型中的几何尺寸参考第二章图 2.2 和表 2.1 所给出的器件结构参数，包括衬底尺寸、有源层厚度、离子凝胶厚度、电极尺寸以及不同侧栅与读出端之间的相对距离。材料参数方面，明胶离子胶的离子扩散系数、相对介电常数以及初始离子浓度取自相关文献报道范围，并结合前期仿真结果的变化趋势进行适当校准；ITZO 有源层与金属电极则采用 COMSOL 中对应的材料参数设置或基于实验条件进行等效化处理。

在时间域求解过程中，本文重点关注脉冲加载期间及撤去后的短时动态演化过程，因此求解时间范围覆盖脉冲施加、离子迁移、界面富集以及回扩散恢复等关键阶段。通过统一的边界条件和参数设置，可使不同侧栅位置与不同距离工况下得到的离子浓度分布、电势分布和 Q_net 结果具有直接可比性，并为后续讨论非单调离子迁移效率序列的形成条件提供基础。

不同侧栅间距下离子浓度/电势分布

离子浓度分布特征

电势分布与沟道耦合

非单调离子迁移效率序列的形成条件与敏感性分析

非单调形成条件分析

关键参数敏感性分析

Silvaco TCAD电学仿真与突触行为复现

漂移-扩散模型与材料参数

物理模型与求解方法

材料参数与器件设定

∇⋅[-Di∇ci-ziDiFRTci∇ϕ]⏟flux=0 ( steady state)=0(no homogeneous reaction) (1)

-∇⋅(ε0εr∇ϕ)=F∑izici⏟space charge (2)

Qnet=Ω(z+c+-z-c-)V (3)

转移/输出特性与等效栅调制

转移与输出特性分析

等效栅调制效应

脉冲响应：EPSC衰减、STP→LTP、PPF随Δt变化及其空间非单调性

EPSC衰减特性

STP向LTP演化行为

PPF随Δt变化及空间非单调性

仿真结果与机理讨论

仿真结果对照分析

非单调机理讨论

器件制备与实验验证

工艺流程与关键步骤电学测试平台与测试方法

器件制备流程

关键工艺步骤与控制要点

实验结果、统计分析与模型回标

测试平台与仪器配置

测试流程与数据采集方法

面向储备池计算的时空编码验证

基本电学与突触响应结果

统计分析与模型回标

面向储备池计算的时空编码验证

输入编码与任务构建

识别结果与性能分析

结论与展望

参考文献

[1] DIORIO C, HASLER P, MINCH B A, MEAD C A. A single-transistor silicon synapse[J]. IEEE Transactions on Electron Devices, 1996, 43(11): 1972-1980.

[2] KONG L A, SUN J, QIAN C, et al. Long-term synaptic plasticity simulated in ionic liquid/polymer hybrid electrolyte gated organic transistors[J]. Organic Electronics, 2017, 47: 126-132.

[3] DAI S, ZHAO Y, WANG Y, et al. Recent Advances in Transistor-Based Artificial Synapses[J]. Advanced Functional Materials, 2019, 29: 1903700.

[4] WAN Q, ZHU L. 神经形态晶体管研究进展[J]. 微纳电子与智能制造, 2019.

[5] KIM K, CHEN C L, TRUONG Q, et al. A carbon nano tube synapse with dynamic logic and learning[J]. Ad vanced Materials, 2013, 25(12): 1693-1698.

[6] LIU S, HE X, SU J, et al. A Light-Stimulus Flexible Synaptic Transistor Based on Ion-Gel Side-Gated Graphene for Neuromorphic Computing[J]. Advanced Photonics Research, 2022, 3: 2200174.

[7] QIAN C, KONG L A, YANG J, et al. Multi-Gate Organic Neuron Transistors for Spatiotemporal Information Processing[J]. Applied Physics Letters, 2017, 110: 083302.

[8] WANG Z, ZHOU X, LIU X, et al. Van der Waals ferroelectric transistors: the all-round artificial synapses for high-precision neuromorphic computing[J]. Chip, 2023, 2: 100044.

[9] 朱赛克, 赵毅. 面向神经形态系统的突触器件及芯片综述与展望[J]. 功能材料与器件学报, 2024.

[10] HE Y, NIE S, LIU R, et al. Spatiotemporal Information Processing Emulated by Multiterminal Neuro-Transistor Networks[J]. Advanced Materials, 2019, 31: 1900903.

[11] HE X, WANG K, WEI D, et al. Lateral ionic-gated graphene synaptic transistor with transition from paired-pulse facilitation to depression for filtering and image recognition[J]. Carbon, 2024, 226: 119161.

[12] HUANG Y J, WANG W S, HUANG X, et al. Oxide dendrite transistors gated with polyvinyl alcohol/chitosan hybrid electrolyte for spatiotemporal integration[J]. Journal of Alloys and Compounds, 2025, 1010: 177938.

[13] LIU K, LI J, LI F, et al. A multi-terminal ion-controlled transistor with multifunctionality and wide temporal dynamics for reservoir computing[J]. Nano Research, 2024, 17(5): 4444-4453.

[14] NI Y, ZHANG Y, LIN J, et al. Transistor-Structured Artificial Dendrites for Spatiotemporally Correlated Reservoir Computing[J]. IEEE Electron Device Letters, 2025, 46(10): 1881-1884.

[15] SUN B, GUO T, ZHOU G, et al. Synaptic devices based neuromorphic computing applications in artificial intelligence[J]. Materials Today Physics, 2021, 18: 100393.

致谢
