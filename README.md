# 🏭 FJSP统一求解与可视化系统

for changqi，集成多种算法、支持实时可视化的柔性作业车间调度问题(FJSP)研究平台，融合进化算法、强化学习和约束编程方法。
柔性作业车间调度（FJSP），核心是两类决策：
- 任务分配：每道工序选择哪台可加工机器。
- 顺序调度：在所选机器上的加工次序。 

## 🎯 项目结构

### 🔬 研究框架 (`src/fjsp/`)
轻量级的FJSP研究框架，专注于算法原型开发和学术研究：

- 📊 数据处理和实例加载
- 🔍 特征工程和策略推荐  
- 🧬 优化算法实现 (BWO, NSGA-II)
- 📈 性能指标和实验框架
- 🎨 基础可视化功能

### 🏭 统一系统 (`unified_fjsp_system/`)
生产就绪的完整FJSP求解系统：

- 🌐 Web界面 (Streamlit + Flask)
- 🎯 多算法集成和并行求解
- 🎨 交互式可视化 (析取图、甘特图、帕累托前沿)
- 📊 实时监控和性能分析
- 🔧 智能启动和环境管理

### 📚 完整文档 (`documentation/`)
系统化的项目文档：

- 🏗️ [软件设计规范](documentation/design/FJSP_SOFTWARE_DESIGN_SPECIFICATION.md)
- 🎯 [多目标优化扩展指南](documentation/design/MULTI_OBJECTIVE_EXTENSION_GUIDE.md)
- 📖 [系统使用指南](documentation/guides/SYSTEM_SUMMARY_AND_USAGE.md)
- 🔧 [API参考文档](documentation/api/api_reference.md)

## 🚀 快速开始

### 1. 启动统一系统
```bash
cd unified_fjsp_system
./start_system.sh
```

访问Web界面: <http://localhost:8501>

### 2. 使用研究框架
```bash
cd examples
python run_nsga2_example.py
```

### 3. 查看文档
- 📖 [快速使用指南](documentation/guides/SYSTEM_SUMMARY_AND_USAGE.md)
- 🏗️ [完整设计文档](documentation/design/FJSP_SOFTWARE_DESIGN_SPECIFICATION.md)

## 🎯 核心功能

### 多算法集成
- **进化算法**: NSGA-II, NSGA-III, BWO, 差分进化
- **强化学习**: DQN, PPO, A3C, SAC  
- **约束编程**: OR-Tools, Gurobi, CP-SAT
- **混合算法**: 进化+强化学习, 多阶段优化

### 实时可视化
- **析取图**: 交互式问题结构展示
- **甘特图**: 调度方案可视化
- **帕累托前沿**: 多目标优化结果
- **收敛分析**: 算法性能监控

### 多目标优化
- **目标函数**: 完工时间、流程时间、延迟时间、能耗、成本
- **性能指标**: 超体积、收敛性、分布均匀性
- **交互优化**: 用户偏好引导的解选择

## 📊 技术特色

- ✅ **前后端分离**: Streamlit + Flask架构
- ✅ **智能启动**: 自动环境管理和端口处理
- ✅ **容错设计**: 简化模式确保系统可用
- ✅ **中文界面**: 完全本地化用户体验
- ✅ **并行求解**: 多算法同时运行对比
- ✅ **实时监控**: WebSocket进度推送

## 📚 文档导航

| 文档类型 | 链接 | 说明 |
|---------|------|------|
| 🚀 快速开始 | [使用指南](documentation/guides/SYSTEM_SUMMARY_AND_USAGE.md) | 系统功能和使用方法 |
| 🏗️ 系统设计 | [设计规范](documentation/design/FJSP_SOFTWARE_DESIGN_SPECIFICATION.md) | 完整的架构和技术设计 |
| 🎯 多目标优化 | [扩展指南](documentation/design/MULTI_OBJECTIVE_EXTENSION_GUIDE.md) | 帕累托前沿和算法实现 |
| 🔧 API接口 | [API文档](documentation/api/api_reference.md) | 完整的接口参考 |
| 📖 项目结构 | [结构说明](documentation/guides/project_structure.md) | 代码组织和模块介绍 |

## 🔬 研究背景

### 问题定义
柔性作业车间调度（FJSP）涉及两类核心决策：
- **任务分配**: 每道工序选择哪台可加工机器
- **顺序调度**: 在所选机器上的加工次序

### 技术路线
采用"进化算法+强化学习+约束编程"的混合方法：
- **特征工程**: 实例特征、图特征、历史性能指标
- **策略推荐**: 基于相似度、帕累托前沿、强化学习的初始化策略
- **多目标优化**: 完工时间、收敛效率、稳定性等多维度评价

### 应用场景
- 🎓 **学术研究**: 算法对比、性能基准、论文实验
- 🏭 **工业应用**: 生产调度、决策支持、系统集成
- 📚 **教学培训**: 可视化教学、交互学习、案例分析

---

# 项目整体结构                                                                                   │
│   fjsp-EA-RL/                                                                                      │
│   ├── README.md                              # 项目主文档                                          │
│   ├── CLAUDE.md                              # Claude Code使用指南                                 │
│   │                                                                                                │
│   ├── documentation/                         # 📚 文档中心                                         │
│   │   ├── api/                              # API文档                                              │
│   │   │   └── api_reference.md                                                                     │
│   │   ├── design/                           # 设计文档                                             │
│   │   │   ├── FJSP_SOFTWARE_DESIGN_SPECIFICATION.md                                                │
│   │   │   └── MULTI_OBJECTIVE_EXTENSION_GUIDE.md                                                   │
│   │   └── guides/                           # 使用指南                                             │
│   │       ├── SYSTEM_SUMMARY_AND_USAGE.md                                                          │
│   │       ├── project_structure.md                                                                 │
│   │       └── fjsp-resources.md                                                                    │
│   │                                                                                                │
│   ├── src/fjsp/                             # 🔬 研究框架                                          │
│   │   ├── data/                             # 数据加载                                             │
│   │   ├── features/                         # 特征工程                                             │
│   │   ├── optimizers/                       # 优化算法                                             │
│   │   ├── recommend/                        # 策略推荐                                             │
│   │   ├── metrics/                          # 性能指标                                             │
│   │   ├── experiments/                      # 实验框架                                             │
│   │   └── vis/                              # 可视化                                               │
│   │                                                                                                │
│   ├── unified_fjsp_system/                  # 🏭 统一系统                                          │
│   │   ├── algorithms/                       # 求解算法                                             │
│   │   │   └── unified_solver.py                                                                    │
│   │   ├── core/                             # 核心模块                                             │
│   │   │   └── data_adapter.py                                                                      │
│   │   ├── visualization/                    # 可视化                                               │
│   │   │   └── unified_visualizer.py                                                                │
│   │   ├── web/                              # Web界面                                              │
│   │   │   ├── backend/                                                                             │
│   │   │   │   └── flask_api.py                                                                     │
│   │   │   └── streamlit_app.py                                                                     │
│   │   ├── scripts/                          # 启动脚本                                             │
│   │   │   ├── start_system.sh                                                                      │
│   │   │   └── start_system.py                                                                      │
│   │   ├── examples/                         # 示例代码                                             │
│   │   │   ├── basic_usage.py                                                                       │
│   │   │   └── multi_objective_demo.py                                                              │
│   │   ├── tests/                            # 测试文件                                             │
│   │   │   ├── test_system.py                                                                       │
│   │   │   ├── test_minimal.py                                                                      │
│   │   │   └── test_disjunctive_graph.py                                                            │
│   │   ├── docs/                             # 系统文档                                             │
│   │   │   ├── README.md                                                                            │
│   │   │   ├── QUICK_START.md                                                                       │
│   │   │   ├── DEPLOYMENT_GUIDE.md                                                                  │
│   │   │   └── DISJUNCTIVE_GRAPH_TEST_GUIDE.md                                                      │
│   │   ├── README.md                         # 系统主文档                                           │
│   │   ├── ARCHITECTURE_ANALYSIS.md          # 架构分析                                             │
│   │   ├── environment.yml                   # Conda环境配置                                        │
│   │   └── requirements.txt                  # Python依赖                                           │
│   │                                                                                                │
│   ├── reference_libs/                       # 📚 参考库                                            │
│   │   ├── README.md                                                                                │
│   │   ├── test_current_project.sh                                                                  │
│   │   ├── job_shop_lib/                                                                            │
│   │   ├── schlably/                                                                                │
│   │   └── graph-jsp-env/                                                                           │
│   │                                                                                                │
│   ├── examples/                             # 示例代码                                             │
│   │   └── run_nsga2_example.py                                                                     │
│   │                                                                                                │
│   ├── tools/                                # 🔧 工具脚本                                          │
│   │   ├── README.md                                                                                │
│   │   └── performance_benchmark.py                                                                 │
│   │                                                                                                │
│   └── test_results/                         # 🧪 测试结果                                          │
│       ├── README.md                                                                                │
│       ├── html/                                                                                    │
│       └── reports/     
