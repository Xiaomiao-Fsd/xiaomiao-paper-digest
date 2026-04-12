# Extracted from current_thesis_report.docx

本科毕业设计（论文）

基于时空非单调相关可塑性的神经形态突触器件仿真验证

学    院       集成电路学院

专    业     微电子科学与工程

年级班别      2022级（1）班

学    号        3122009664

学生姓名          黎展睿

任课教师          陈雅怡

2026年 4月

摘要

随着人工智能与物联网技术的快速发展，传统冯·诺依曼架构逐渐暴露出存储墙和高功耗等问题，难以同时满足高并行、低延迟和低能耗的信息处理需求。神经形态计算通过在硬件层面融合存储与计算、模拟生物神经系统的事件驱动和并行处理机制，被认为是突破上述瓶颈的重要方向。作为神经形态系统的重要基础单元，能够实现可塑性调控的突触器件因此成为当前研究热点。

现有研究大多集中于时间相关可塑性，而对空间相关可塑性的探索仍较有限；已有空间可塑性研究通常局限于微米尺度，并多表现为随距离增加而单调衰减的响应规律。与此同时，空间可塑性的物理机制尚缺乏充分解释，尤其是在突触输入物理位置如何调控器件权重更新方面，仍缺少系统性的建模与验证。针对这些不足，本文以多侧栅树突突触晶体管为对象，尝试在更大空间尺度上研究时空耦合下的非单调相关可塑性，并从器件、模型和应用三个层面建立相互印证的分析框架。

在模型与方法方面，本文结合COMSOL和Silvaco TCAD开展联合仿真。在本研究中，我们展示了一种晶体管结构的人工树突（TSAD），在厘米尺度上实现了空间非单调突触效能。观察到的兴奋性突触后电流（EPSC）随距离呈非单调趋势，超越了传统单调离子扩散的限制。结合多物理场模拟与复阻抗分析，我们揭示这一现象来源于离子迁移效率与亚饱和离子环境中有限离子可用性之间的动力学竞争。结合仿真与实测，利用这些内在动力学，我们实现了一种TSAD-RC，对28类复杂时间信号的识别准确率达到100%，阐明了宏观尺度非单调时空整合的物理本质。

关键词：时空非单调可塑性、突触晶体管、多侧栅树突结构、离子动力学分析、器件仿真、算法训练

Abstract

With the rapid advancement of artificial intelligence and the Internet of Things, the traditional von Neumann architecture has increasingly revealed shortcomings such as the memory wall and high-power consumption, making it difficult to simultaneously satisfy the demands of highly parallel, low-latency, and energy-efficient information processing. Neuromorphic computing, which integrates storage and computation at the hardware level and emulates the event-driven and parallel-processing mechanisms of biological neural systems, is widely regarded as a promising route to overcoming these bottlenecks. Accordingly, synaptic devices capable of plasticity modulation have become a major focus of current research as fundamental building blocks of neuromorphic systems.

Existing research has largely concentrated on temporal plasticity, whereas spatial plasticity has received relatively limited attention. Reported studies of spatial plasticity are typically restricted to the micrometer scale and generally show a monotonic decay in response with increasing distance. Meanwhile, the physical mechanisms underlying spatial plasticity remain insufficiently understood. In particular, systematic modeling and validation are still lacking with respect to how the physical locations of synaptic inputs regulate device weight updates. To address these issues, this paper investigates spatiotemporally coupled non-monotonic correlated plasticity over a larger spatial scale using a multi-side-gate dendritic synaptic transistor as the research platform, and establishes a mutually corroborative analytical framework spanning device, model, and application.

For modeling and methodology, joint simulations were carried out using COMSOL and Silvaco TCAD. In this work, a transistor-structured artificial dendrite (TSAD) is demonstrated to achieve spatially non-monotonic synaptic efficacy at the centimeter scale. The observed excitatory postsynaptic current (EPSC) exhibits a non-monotonic dependence on distance, surpassing the limitation of conventional monotonic ion diffusion. Combined multiphysics simulations and complex impedance analysis reveal that this phenomenon arises from the dynamic competition between ion migration efficiency and the limited availability of ions in a subsaturated ionic environment. By integrating simulation and experimental results and leveraging these intrinsic dynamics, a TSAD-RC is realized, achieving 100% recognition accuracy for 28 classes of complex temporal signals and thereby elucidating the physical basis of macroscale non-monotonic spatiotemporal integration.

Keywords: spatiotemporal non-monotonic correlated plasticity; synaptic transistor; multi-side-gate dendritic structure; ion dynamics analysis; device simulation; algorithm training

目录

1绪论1

1.1研究背景与意义1

1.1.1冯·诺依曼架构瓶颈与神经形态计算的发展需求1

1.1.2突触晶体管在神经形态系统中的作用与研究价值1

1.1.3时空相关可塑性研究的理论意义与应用意义2

1.2国内外研究现状3

1.2.1我是小标题3

1.3本文研究内容与创新点3

1.4论文结构与安排3

参考文献4

致谢5

绪论

研究背景与意义

冯·诺依曼架构瓶颈与神经形态计算的发展需求

随着人工智能和物联网技术的快速发展，图像识别、模式分类和时序信号处理等任务对计算系统的并行性、实时性和能效提出了更高要求。传统冯·诺依曼架构中存储单元与计算单元相互分离，数据需要在二者之间频繁搬运，容易引发“存储墙”问题，并带来延迟增加、效率下降和能耗上升等限制，难以适应神经网络规模持续扩大和信息处理复杂度不断提升的需求。尤其在高并行、事件驱动的智能任务中，传统架构的适配性不足愈发明显，已难以充分满足新型智能硬件对高效感知、计算与存储协同的要求。为突破这一瓶颈，研究者借鉴生物神经系统中神经元与突触协同工作的机制，提出了神经形态计算。该范式强调在硬件层面实现存储与计算融合，具备并行处理、事件驱动和自适应学习等特点，被认为是实现高效智能信息处理的重要路径，也为新型类脑器件与系统结构研究提供了明确方向。

突触晶体管在神经形态系统中的作用与研究价值

在神经形态系统中，突触负责信息传递、权值调节以及学习记忆，是实现类脑计算的关键单元。因此，能够模拟突触行为的器件是神经形态硬件实现的重要基础。突触晶体管兼具晶体管的电学调控特性与突触功能模拟能力，可通过栅极调控和脉冲刺激实现沟道电导连续变化，进而表征兴奋性突触后电流、成对脉冲易化以及短时、长时可塑性等典型行为。与传统器件相比，突触晶体管在结构设计、参数调控和多端输入响应方面更具灵活性，既可承担类突触权值存储与更新功能，也有助于实现多输入信息整合和神经网络硬件映射。特别是在多侧栅结构中，其对多路信号的协同调制能力更为突出，因此成为连接器件特性、突触行为与系统应用的重要载体，在神经形态器件研究中具有突出的理论与工程价值，也为后续开展复杂时空调制研究提供了器件基础。

时空相关可塑性研究的理论意义与应用意义

生物神经系统对信息的处理具有明显的时间相关性与空间相关性，突触可塑性不仅取决于刺激强度，还与输入的先后顺序、位置分布及多输入协同作用密切相关。因此，从时空相关角度研究突触可塑性，有助于更真实地揭示神经信息编码与学习机制，并为类脑模型构建提供依据。对突触晶体管而言，时空相关可塑性研究能够反映器件在复杂刺激条件下的动态响应和多输入整合能力，并进一步评估其在特征提取、非线性映射和动态状态表征中的应用潜力。这些特征直接关系到系统对时空信息的利用效率，对于图像识别、模式分类、时序信号处理以及储备池计算等任务具有重要意义，也为后续开展多侧栅结构器件的时空非单调调制行为的研究、机制分析与仿真验证奠定了基础。与此同时，该研究也有助于推动器件层特性向系统级功能实现的有效转化。

国内外研究现状

测试测试

我是小标题

本文研究内容与创新点

论文结构与安排

参考文献

致谢
