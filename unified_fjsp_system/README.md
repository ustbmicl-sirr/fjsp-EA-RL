# 🏭 Unified FJSP System

统一的柔性作业车间调度问题(FJSP)求解与可视化系统。

## 🚀 快速启动

### 使用启动脚本 (推荐)
```bash
# Linux/Mac
./scripts/start_system.sh

# Windows
scripts\start_system.bat

# Python (跨平台)
python scripts/start_system.py
```

### 手动启动
```bash
# 安装依赖
pip install -r requirements.txt

# 启动Web应用
streamlit run web/streamlit_app.py
```

## 📁 目录结构

```
unified_fjsp_system/
├── 🚀 scripts/          # 启动脚本
├── 📚 docs/             # 文档
├── 🧪 tests/            # 测试
├── 🧠 algorithms/       # 算法层
├── 📊 core/             # 数据层
├── 🎨 visualization/    # 可视化层
├── 🌐 web/              # Web层
└── 💡 examples/         # 示例
```

## 🎯 核心功能

### 多算法集成
- **进化算法**: NSGA-II, BWO, 差分进化
- **强化学习**: DQN, PPO, A3C
- **约束编程**: OR-Tools, CP-SAT
- **混合算法**: 多阶段优化

### 实时可视化
- **析取图**: 交互式问题结构展示
- **甘特图**: 调度方案可视化
- **收敛分析**: 算法性能监控
- **多目标优化**: 帕累托前沿分析

## 📚 文档

- [快速开始](docs/QUICK_START.md) - 安装和基础使用
- [部署指南](docs/DEPLOYMENT_GUIDE.md) - 生产环境部署
- [测试指南](docs/DISJUNCTIVE_GRAPH_TEST_GUIDE.md) - 功能测试

## 🧪 测试

```bash
# 运行所有测试
python tests/test_system.py

# 测试析取图功能
python tests/test_disjunctive_graph.py

# 最小化测试
python tests/test_minimal.py
```

## 💡 示例

```bash
# 基础使用示例
python examples/basic_usage.py

# 多目标优化演示
python examples/multi_objective_demo.py
```

---

**版本**: v1.0.0
**技术栈**: Python, Streamlit, Flask, Plotly
