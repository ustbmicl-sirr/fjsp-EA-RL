# 🏭 Unified FJSP System

一个融合多种算法和可视化技术的柔性作业车间调度问题（FJSP）求解与可视化系统。

## 🎯 系统特点

### 📚 集成的库
- **JobShopLib**: 约束编程、调度规则、元启发式算法
- **Schlably**: 深度强化学习框架  
- **Graph-JSP-Env**: 基于图的强化学习环境

### 🧠 算法支持
- **进化算法**: 遗传算法、差分进化等
- **强化学习**: DQN、PPO、A3C等
- **约束编程**: OR-Tools CP-SAT求解器
- **元启发式**: 模拟退火、禁忌搜索等

### 📊 可视化功能
- 交互式甘特图
- 析取图表示
- 实时收敛监控
- 算法性能比较
- 综合仪表板

## 🚀 快速开始

### 安装依赖

```bash
# 基础依赖
pip install numpy pandas matplotlib plotly streamlit networkx

# 可选：完整依赖
pip install -r requirements.txt

# 可选：特定库
pip install job-shop-lib graph-jsp-env ortools
```

### 运行Web应用

```bash
# 启动Streamlit应用
cd unified_fjsp_system
streamlit run web/streamlit_app.py
```

### 基本使用

```python
from core.data_adapter import InstanceGenerator, DataAdapter
from algorithms.unified_solver import UnifiedSolverManager
from visualization.unified_visualizer import UnifiedVisualizer

# 1. 生成FJSP实例
instance = InstanceGenerator.generate_random_fjsp(
    num_jobs=3, 
    num_machines=3, 
    max_operations_per_job=3,
    flexibility=0.5
)

# 2. 创建求解器管理器
solver_manager = UnifiedSolverManager()

# 3. 并行求解
results = solver_manager.solve_parallel(
    instance, 
    algorithms=['evolutionary', 'reinforcement']
)

# 4. 可视化结果
visualizer = UnifiedVisualizer()
for alg, result in results.items():
    fig = visualizer.plot_gantt_chart(instance, result)
    fig.show()
```

## 📁 项目结构

```
unified_fjsp_system/
├── core/
│   ├── __init__.py
│   └── data_adapter.py          # 统一数据适配器
├── algorithms/
│   ├── __init__.py
│   └── unified_solver.py        # 统一求解器接口
├── visualization/
│   ├── __init__.py
│   └── unified_visualizer.py    # 统一可视化模块
├── web/
│   ├── __init__.py
│   ├── streamlit_app.py         # Streamlit前端
│   └── flask_api.py             # Flask后端API
├── examples/
│   ├── basic_usage.py           # 基础使用示例
│   ├── algorithm_comparison.py  # 算法比较示例
│   └── custom_instance.py       # 自定义实例示例
├── tests/
│   ├── test_data_adapter.py
│   ├── test_solvers.py
│   └── test_visualizer.py
├── requirements.txt
└── README.md
```

## 🔧 核心组件

### 1. 数据适配器 (DataAdapter)

统一不同库的数据格式，支持：
- JobShopLib ↔ 统一格式
- Graph-JSP-Env ↔ 统一格式  
- Schlably ↔ 统一格式
- 析取图构建

```python
# 格式转换示例
from core.data_adapter import DataAdapter

# 转换为JobShopLib格式
jsl_instance = DataAdapter.to_jobshoplib(unified_instance)

# 构建析取图
graph = DataAdapter.build_disjunctive_graph(unified_instance)
```

### 2. 统一求解器 (UnifiedSolverManager)

集成多种求解算法：

```python
from algorithms.unified_solver import UnifiedSolverManager

manager = UnifiedSolverManager()

# 单个算法求解
result = manager.get_solver('evolutionary').solve(instance)

# 并行多算法求解
results = manager.solve_parallel(instance, ['evolutionary', 'reinforcement'])
```

### 3. 可视化器 (UnifiedVisualizer)

提供多种可视化方式：

```python
from visualization.unified_visualizer import UnifiedVisualizer

visualizer = UnifiedVisualizer()

# 甘特图
gantt_fig = visualizer.plot_gantt_chart(instance, solution)

# 析取图
graph_fig = visualizer.plot_disjunctive_graph(instance)

# 算法比较
comparison_fig = visualizer.plot_algorithm_comparison(results)

# 综合仪表板
dashboard_fig = visualizer.create_dashboard(instance, results)
```

## 🌐 Web界面功能

### Streamlit应用特性
- 📊 实例配置和生成
- 🔧 算法参数调整
- 🚀 并行求解执行
- 📈 实时进度监控
- 📋 结果对比分析
- 🎨 交互式可视化

### 主要页面
1. **问题配置**: 生成随机实例、加载基准实例、上传文件
2. **算法设置**: 选择算法、调整参数
3. **求解监控**: 实时显示求解进度
4. **结果分析**: 甘特图、析取图、性能比较

## 🧪 算法详解

### 进化算法
- **编码**: 基于操作序列的排列编码
- **选择**: 锦标赛选择
- **交叉**: 顺序交叉(OX)
- **变异**: 交换变异
- **适应度**: 最小化makespan

### 强化学习
- **环境**: 基于Graph-JSP-Env的析取图环境
- **状态**: 图节点特征和全局状态
- **动作**: 选择下一个要调度的操作
- **奖励**: 基于makespan改进的奖励函数

### 约束编程
- **求解器**: OR-Tools CP-SAT
- **约束**: 工序顺序、机器容量、时间窗口
- **目标**: 最小化makespan

## 📈 性能监控

系统提供实时监控功能：

```python
# 添加监控回调
def monitor_callback(data):
    if 'generation' in data:
        print(f"Generation {data['generation']}: Best = {data['best_fitness']}")
    elif 'step' in data:
        print(f"RL Step {data['step']}: Reward = {data['reward']}")

solver_manager.add_global_callback(monitor_callback)
```

## 🔬 扩展开发

### 添加新算法

```python
from algorithms.unified_solver import BaseSolver

class CustomSolver(BaseSolver):
    def __init__(self):
        super().__init__("CustomAlgorithm")
    
    def solve(self, instance, **kwargs):
        # 实现自定义算法
        return SolutionResult(...)

# 注册到管理器
manager.solvers['custom'] = CustomSolver()
```

### 添加新可视化

```python
def plot_custom_view(self, instance, solution):
    # 实现自定义可视化
    fig = go.Figure()
    # ... 绘图逻辑
    return fig

# 添加到可视化器
UnifiedVisualizer.plot_custom_view = plot_custom_view
```

## 🧪 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_data_adapter.py -v

# 生成覆盖率报告
pytest --cov=unified_fjsp_system tests/
```

## 📝 示例

查看 `examples/` 目录获取更多使用示例：

- `basic_usage.py`: 基础功能演示
- `algorithm_comparison.py`: 多算法性能比较
- `custom_instance.py`: 自定义实例创建
- `real_time_monitoring.py`: 实时监控示例

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下开源项目的贡献：
- [JobShopLib](https://github.com/Pabloo22/job_shop_lib)
- [Schlably](https://github.com/tmdt-buw/schlably)  
- [Graph-JSP-Env](https://github.com/Alexander-Nasuta/graph-jsp-env)
- [OR-Tools](https://developers.google.com/optimization)
- [Plotly](https://plotly.com/)
- [Streamlit](https://streamlit.io/)

## 📞 联系

如有问题或建议，请通过以下方式联系：
- 创建 Issue
- 发送邮件
- 参与讨论

---

**让FJSP求解变得简单而强大！** 🚀
