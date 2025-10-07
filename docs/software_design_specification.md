# 统一FJSP求解与可视化系统 - 软件概要设计文档

## 1. 项目概述

### 1.1 项目背景
柔性作业车间调度问题（Flexible Job Shop Scheduling Problem, FJSP）是制造业中的核心优化问题。当前存在多个优秀的开源解决方案，但缺乏统一的集成平台。本项目旨在融合多种算法和可视化技术，构建一个统一的FJSP求解与可视化系统。

### 1.2 设计目标
- **算法融合**: 集成进化算法、强化学习、约束编程等多种求解方法
- **库整合**: 统一JobShopLib、Schlably、Graph-JSP-Env等优秀开源库
- **析取图支持**: 完整的析取图构建、操作和可视化
- **可视化丰富**: 提供甘特图、析取图、性能比较等多种可视化
- **易用性**: 提供Web界面和命令行工具，降低使用门槛

### 1.3 技术路线
遵循"特征+策略推荐+改进元启发式+多目标评估"的研究路线，构建可扩展的框架架构。

## 2. 系统架构设计

### 2.1 总体架构
系统采用分层架构模式，包含四个主要层次：

```
┌─────────────────────────────────────────┐
│           🌐 接口层 (Interface)          │
├─────────────────────────────────────────┤
│          📈 可视化层 (Visualization)     │
├─────────────────────────────────────────┤
│           🧠 算法层 (Algorithm)          │
├─────────────────────────────────────────┤
│            📊 核心层 (Core)              │
└─────────────────────────────────────────┘
```

### 2.2 架构层次说明

#### 2.2.1 核心层 (Core Layer)
- **数据适配器 (DataAdapter)**: 统一不同库的数据格式
- **实例生成器 (InstanceGenerator)**: 生成随机和基准FJSP实例
- **析取图构建器**: 构建和操作析取图结构

#### 2.2.2 算法层 (Algorithm Layer)
- **统一求解器管理器**: 管理和调度多种算法
- **进化算法求解器**: 遗传算法、差分进化等
- **强化学习求解器**: 基于Graph-JSP-Env的RL算法
- **约束编程求解器**: OR-Tools CP-SAT等精确算法

#### 2.2.3 可视化层 (Visualization Layer)
- **甘特图可视化**: 交互式调度方案展示
- **析取图可视化**: 问题结构和求解过程展示
- **性能分析图表**: 算法收敛性和性能比较
- **综合仪表板**: 多维度结果展示

#### 2.2.4 接口层 (Interface Layer)
- **Web应用**: Streamlit构建的交互式界面
- **REST API**: Flask提供的编程接口
- **命令行工具**: 批处理和自动化支持

## 3. 核心模块设计

### 3.1 数据适配模块 (core/data_adapter.py)

#### 3.1.1 统一数据结构
```python
@dataclass
class UnifiedOperation:
    job_id: int
    operation_id: int
    machines: List[int]
    processing_times: List[float]
    setup_time: float = 0.0
    due_date: Optional[float] = None
    release_time: float = 0.0

@dataclass
class UnifiedFJSPInstance:
    name: str
    num_jobs: int
    num_machines: int
    operations: List[UnifiedOperation]
    metadata: Dict[str, Any] = None
```

#### 3.1.2 格式转换功能
- JobShopLib ↔ 统一格式
- Graph-JSP-Env ↔ 统一格式
- Schlably ↔ 统一格式
- 析取图构建和操作

#### 3.1.3 实例生成功能
- 随机实例生成（可配置作业数、机器数、柔性度）
- 基准实例加载（支持标准测试集）
- 自定义实例解析（多种文件格式）

### 3.2 算法模块 (algorithms/unified_solver.py)

#### 3.2.1 求解器基类
```python
class BaseSolver(ABC):
    def __init__(self, name: str)
    def add_callback(self, callback: Callable)
    def solve(self, instance: UnifiedFJSPInstance, **kwargs) -> SolutionResult
```

#### 3.2.2 进化算法求解器
- **编码方案**: 基于操作序列的排列编码
- **选择策略**: 锦标赛选择、轮盘赌选择
- **交叉算子**: 顺序交叉(OX)、部分映射交叉(PMX)
- **变异算子**: 交换变异、插入变异
- **适应度函数**: 最小化makespan、多目标优化

#### 3.2.3 强化学习求解器
- **环境集成**: Graph-JSP-Env析取图环境
- **状态表示**: 图节点特征和全局状态
- **动作空间**: 操作选择和机器分配
- **奖励设计**: 基于makespan改进的奖励函数
- **算法支持**: DQN、PPO、A3C等

#### 3.2.4 约束编程求解器
- **求解器**: OR-Tools CP-SAT
- **约束建模**: 工序顺序、机器容量、时间窗口
- **目标函数**: 最小化makespan、总完工时间等
- **求解策略**: 分支定界、启发式搜索

### 3.3 可视化模块 (visualization/unified_visualizer.py)

#### 3.3.1 甘特图可视化
- **交互式甘特图**: Plotly实现，支持缩放、悬停
- **多算法对比**: 并排显示不同算法的调度方案
- **时间轴分析**: 机器利用率、作业完成时间
- **导出功能**: HTML、PNG、PDF格式

#### 3.3.2 析取图可视化
- **图结构展示**: 节点和边的可视化
- **布局算法**: 弹簧布局、分层布局、圆形布局
- **交互功能**: 节点选择、边高亮、路径追踪
- **动态展示**: 求解过程的动画演示

#### 3.3.3 性能分析图表
- **收敛曲线**: 算法迭代过程的适应度变化
- **性能对比**: 多算法的makespan、计算时间比较
- **统计分析**: 箱线图、散点图、热力图
- **实时监控**: 求解过程的实时进度显示

### 3.4 Web界面模块 (web/streamlit_app.py)

#### 3.4.1 页面结构
- **问题配置页**: 实例生成、参数设置
- **算法选择页**: 算法配置、参数调优
- **求解监控页**: 实时进度、中间结果
- **结果分析页**: 可视化展示、性能比较

#### 3.4.2 交互功能
- **参数调节**: 滑块、输入框、下拉菜单
- **实时更新**: 自动刷新、进度条显示
- **结果导出**: 图表下载、数据导出
- **会话管理**: 状态保存、历史记录

## 4. 数据流设计

### 4.1 数据流向
```
实例输入 → 数据适配 → 算法求解 → 结果处理 → 可视化展示
    ↓         ↓         ↓         ↓         ↓
  文件/生成  格式转换   并行计算   结果汇总   图表生成
```

### 4.2 关键数据结构

#### 4.2.1 求解结果
```python
@dataclass
class SolutionResult:
    schedule: Dict[str, Any]
    makespan: float
    objectives: Dict[str, float]
    algorithm: str
    computation_time: float
    iterations: int
    convergence_history: List[float]
    metadata: Dict[str, Any]
```

#### 4.2.2 析取图结构
- **节点类型**: 源点、汇点、操作节点
- **边类型**: 合取边（作业顺序）、析取边（机器冲突）
- **属性信息**: 处理时间、机器分配、优先级

## 5. 接口设计

### 5.1 核心API接口

#### 5.1.1 实例管理接口
```python
# 生成随机实例
instance = InstanceGenerator.generate_random_fjsp(num_jobs, num_machines, max_ops)

# 加载基准实例
instance = InstanceGenerator.load_benchmark("ft06")

# 解析文件实例
instance = InstanceGenerator.parse_file("instance.fjs")
```

#### 5.1.2 求解接口
```python
# 单算法求解
solver = manager.get_solver('evolutionary')
result = solver.solve(instance, **params)

# 并行多算法求解
results = manager.solve_parallel(instance, algorithms=['ea', 'rl'])
```

#### 5.1.3 可视化接口
```python
# 甘特图
fig = visualizer.plot_gantt_chart(instance, result)

# 析取图
fig = visualizer.plot_disjunctive_graph(instance)

# 性能比较
fig = visualizer.plot_algorithm_comparison(results)
```

### 5.2 Web API接口

#### 5.2.1 RESTful API设计
```
POST /api/instances          # 创建实例
GET  /api/instances/{id}     # 获取实例
POST /api/solve              # 求解问题
GET  /api/results/{id}       # 获取结果
GET  /api/visualize/{type}   # 生成可视化
```

#### 5.2.2 WebSocket接口
```
/ws/solve/{session_id}       # 实时求解进度
/ws/monitor/{session_id}     # 实时监控数据
```

## 6. 技术选型

### 6.1 开发语言和框架
- **主语言**: Python 3.8+
- **Web框架**: Streamlit (前端), Flask (API)
- **数值计算**: NumPy, SciPy
- **数据处理**: Pandas
- **图计算**: NetworkX
- **可视化**: Plotly, Matplotlib

### 6.2 外部依赖库
- **JobShopLib**: 作业车间调度库
- **Graph-JSP-Env**: 强化学习环境
- **OR-Tools**: 约束编程求解器
- **Gymnasium**: 强化学习标准接口
- **Stable-Baselines3**: 强化学习算法

### 6.3 开发工具
- **版本控制**: Git
- **包管理**: pip, conda
- **测试框架**: pytest
- **代码质量**: black, flake8, mypy
- **文档生成**: Sphinx

## 7. 部署架构

### 7.1 本地部署
```
用户机器
├── Python环境
├── 依赖包安装
├── 源码部署
└── Web服务启动
```

### 7.2 容器化部署
```
Docker容器
├── Python运行时
├── 系统依赖
├── 应用代码
└── 服务配置
```

### 7.3 云端部署
```
云平台
├── 容器服务
├── 负载均衡
├── 数据存储
└── 监控日志
```

## 8. 性能设计

### 8.1 算法性能
- **并行计算**: 多算法并行执行
- **内存优化**: 大规模实例的内存管理
- **计算加速**: GPU加速（可选）
- **缓存机制**: 中间结果缓存

### 8.2 系统性能
- **响应时间**: Web界面 < 2秒响应
- **并发支持**: 支持多用户同时使用
- **资源管理**: CPU和内存使用监控
- **扩展性**: 水平扩展支持

## 9. 质量保证

### 9.1 测试策略
- **单元测试**: 核心模块功能测试
- **集成测试**: 模块间接口测试
- **系统测试**: 端到端功能测试
- **性能测试**: 算法性能基准测试

### 9.2 代码质量
- **代码规范**: PEP8标准
- **类型检查**: mypy静态检查
- **代码覆盖**: 测试覆盖率 > 80%
- **文档完整**: API文档和用户手册

## 10. 扩展性设计

### 10.1 算法扩展
- **插件机制**: 新算法的插件式集成
- **配置化**: 算法参数的配置文件管理
- **标准接口**: 统一的求解器接口规范

### 10.2 功能扩展
- **新问题类型**: 支持其他调度问题
- **新可视化**: 扩展可视化类型
- **新接口**: 支持更多编程语言接口

### 10.3 集成扩展
- **外部系统**: 与MES、ERP系统集成
- **数据源**: 支持多种数据源接入
- **输出格式**: 支持多种结果输出格式

## 11. 风险分析与应对

### 11.1 技术风险
- **依赖库兼容性**: 定期更新依赖，维护兼容性矩阵
- **性能瓶颈**: 性能监控和优化，算法并行化
- **内存溢出**: 大实例分块处理，内存使用监控

### 11.2 项目风险
- **开发进度**: 敏捷开发，迭代交付
- **质量控制**: 自动化测试，代码审查
- **用户接受度**: 用户反馈收集，界面优化

## 12. 开发计划

### 12.1 开发阶段
1. **第一阶段**: 核心数据适配和基础算法（4周）
2. **第二阶段**: 可视化模块和Web界面（3周）
3. **第三阶段**: 算法集成和性能优化（3周）
4. **第四阶段**: 测试完善和文档编写（2周）

### 12.2 里程碑
- **M1**: 核心模块完成，基础功能可用
- **M2**: Web界面完成，用户可操作
- **M3**: 算法集成完成，性能达标
- **M4**: 系统测试完成，正式发布

## 13. 维护计划

### 13.1 版本管理
- **主版本**: 重大功能更新
- **次版本**: 新功能添加
- **修订版本**: 错误修复和小改进

### 13.2 支持计划
- **技术支持**: 用户问题解答和技术指导
- **功能更新**: 根据用户需求持续改进
- **安全维护**: 安全漏洞修复和防护

---

**文档版本**: v1.0
**创建日期**: 2024年10月
**最后更新**: 2024年10月
**维护团队**: FJSP系统开发团队
**审核状态**: 待审核
