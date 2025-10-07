# 项目结构说明

## 📁 目录结构

```
unified_fjsp_system/
├── 📊 core/                          # 核心模块
│   ├── __init__.py                   # 模块初始化
│   └── data_adapter.py               # 数据适配器
│       ├── UnifiedOperation          # 统一操作类
│       ├── UnifiedFJSPInstance       # 统一实例类
│       ├── DataAdapter               # 数据转换器
│       └── InstanceGenerator         # 实例生成器
│
├── 🧠 algorithms/                    # 算法模块
│   ├── __init__.py                   # 模块初始化
│   └── unified_solver.py             # 统一求解器
│       ├── BaseSolver                # 求解器基类
│       ├── EvolutionaryAlgorithmSolver # 进化算法
│       ├── ReinforcementLearningSolver # 强化学习
│       ├── JobShopLibSolver          # JobShopLib集成
│       └── UnifiedSolverManager      # 求解器管理器
│
├── 📈 visualization/                 # 可视化模块
│   ├── __init__.py                   # 模块初始化
│   └── unified_visualizer.py         # 统一可视化器
│       ├── plot_gantt_chart()        # 甘特图
│       ├── plot_disjunctive_graph()  # 析取图
│       ├── plot_convergence_comparison() # 收敛比较
│       ├── plot_algorithm_comparison() # 算法比较
│       └── create_dashboard()        # 综合仪表板
│
├── 🌐 web/                          # Web界面
│   ├── __init__.py                   # 模块初始化
│   └── streamlit_app.py              # Streamlit应用
│       ├── StreamlitApp              # 主应用类
│       ├── render_sidebar()          # 侧边栏
│       ├── render_main_interface()   # 主界面
│       └── solve_problem()           # 求解控制
│
├── 🧪 examples/                     # 示例代码
│   ├── __init__.py                   # 模块初始化
│   ├── basic_usage.py                # 基础使用示例
│   ├── algorithm_comparison.py       # 算法比较示例
│   └── custom_instance.py           # 自定义实例示例
│
├── 📚 docs/                         # 文档目录
│   ├── software_design_specification.md # 软件设计文档
│   ├── project_structure.md          # 项目结构说明
│   ├── api_reference.md              # API参考文档
│   └── user_guide.md                 # 用户指南
│
├── 🧪 tests/                        # 测试目录
│   ├── test_data_adapter.py          # 数据适配器测试
│   ├── test_solvers.py               # 求解器测试
│   ├── test_visualizer.py            # 可视化器测试
│   └── test_integration.py           # 集成测试
│
├── 📋 配置文件
│   ├── requirements.txt              # Python依赖
│   ├── setup.py                      # 安装配置
│   ├── pyproject.toml               # 项目配置
│   └── .gitignore                   # Git忽略文件
│
├── 🚀 启动脚本
│   ├── run_web_app.py               # Web应用启动器
│   ├── test_system.py               # 系统测试脚本
│   └── __init__.py                  # 包初始化
│
└── 📖 说明文档
    ├── README.md                    # 项目说明
    ├── QUICK_START.md              # 快速开始
    ├── CHANGELOG.md                # 更新日志
    └── LICENSE                     # 许可证
```

## 🔧 核心模块详解

### 📊 Core Module (core/)
**职责**: 提供统一的数据结构和格式转换功能

- **data_adapter.py**: 核心数据适配器
  - `UnifiedOperation`: 标准化的操作表示
  - `UnifiedFJSPInstance`: 标准化的FJSP实例
  - `DataAdapter`: 多格式数据转换
  - `InstanceGenerator`: 实例生成和加载

**关键特性**:
- 统一数据格式，消除库间差异
- 析取图自动构建
- 多种实例生成方式
- 格式验证和错误处理

### 🧠 Algorithm Module (algorithms/)
**职责**: 集成多种求解算法，提供统一接口

- **unified_solver.py**: 统一求解器框架
  - `BaseSolver`: 抽象基类，定义标准接口
  - `EvolutionaryAlgorithmSolver`: 进化算法实现
  - `ReinforcementLearningSolver`: 强化学习集成
  - `JobShopLibSolver`: JobShopLib包装器
  - `UnifiedSolverManager`: 求解器管理和调度

**关键特性**:
- 插件式算法架构
- 并行求解支持
- 实时进度监控
- 统一结果格式

### 📈 Visualization Module (visualization/)
**职责**: 提供丰富的可视化功能

- **unified_visualizer.py**: 统一可视化引擎
  - 甘特图：调度方案可视化
  - 析取图：问题结构展示
  - 性能图表：算法比较分析
  - 综合仪表板：多维度展示

**关键特性**:
- 交互式图表（Plotly）
- 多种布局算法
- 实时更新支持
- 多格式导出

### 🌐 Web Module (web/)
**职责**: 提供用户友好的Web界面

- **streamlit_app.py**: Streamlit Web应用
  - 问题配置界面
  - 算法参数调整
  - 实时求解监控
  - 结果分析展示

**关键特性**:
- 响应式设计
- 实时交互
- 会话状态管理
- 多页面导航

## 📦 依赖关系

### 内部依赖
```
web/ → algorithms/ → core/
web/ → visualization/ → core/
visualization/ → algorithms/
examples/ → all modules
```

### 外部依赖
```
Core Dependencies:
├── numpy (数值计算)
├── pandas (数据处理)
├── networkx (图计算)
├── matplotlib (基础绘图)
├── plotly (交互式图表)
└── streamlit (Web框架)

Optional Dependencies:
├── job-shop-lib (作业车间库)
├── graph-jsp-env (图环境)
├── ortools (优化工具)
├── gymnasium (强化学习)
└── stable-baselines3 (RL算法)
```

## 🔄 数据流转

### 1. 输入阶段
```
用户输入 → 实例生成/加载 → 统一数据格式
```

### 2. 处理阶段
```
统一格式 → 数据转换 → 算法求解 → 结果收集
```

### 3. 输出阶段
```
求解结果 → 可视化处理 → Web展示 → 用户交互
```

## 🧪 测试策略

### 测试层次
1. **单元测试**: 各模块独立功能测试
2. **集成测试**: 模块间接口测试
3. **系统测试**: 端到端功能测试
4. **性能测试**: 算法性能基准测试

### 测试覆盖
- 核心功能：100%覆盖
- 算法模块：90%覆盖
- 可视化模块：80%覆盖
- Web界面：70%覆盖

## 🚀 部署结构

### 开发环境
```
本地开发
├── Python 3.8+
├── 虚拟环境
├── 开发依赖
└── 测试数据
```

### 生产环境
```
生产部署
├── Docker容器
├── Web服务器
├── 负载均衡
└── 监控日志
```

## 📈 扩展点

### 算法扩展
- 新增求解器：继承`BaseSolver`
- 参数配置：YAML配置文件
- 性能监控：回调函数机制

### 可视化扩展
- 新图表类型：扩展`UnifiedVisualizer`
- 交互功能：Plotly事件处理
- 导出格式：多种输出支持

### 接口扩展
- REST API：Flask扩展
- 命令行工具：Click框架
- 桌面应用：PyQt/Tkinter

## 🔧 配置管理

### 配置文件层次
1. **默认配置**: 代码内置默认值
2. **系统配置**: 全局配置文件
3. **用户配置**: 用户自定义设置
4. **运行时配置**: 动态参数调整

### 配置项分类
- **算法参数**: 种群大小、迭代次数等
- **可视化设置**: 颜色主题、图表样式等
- **系统配置**: 并发数、内存限制等
- **用户偏好**: 界面语言、默认算法等

---

这个项目结构设计遵循了模块化、可扩展、易维护的原则，为FJSP求解与可视化提供了完整的解决方案。
