# 参考库说明

本目录包含三个 FJSP 开源库的源码，仅供参考学习。

---

## 📁 目录结构

```
reference_libs/
├── job_shop_lib/              # JobShopLib 源码（参考）
├── schlably/                  # Schlably 源码（参考）
├── graph-jsp-env/             # Graph-JSP-Env 源码（参考）
├── test_current_project.sh    # 测试脚本
└── README.md                  # 本文件
```

---

## 📚 三个参考库简介

### 1. JobShopLib
- **类型**: Python 包（`pip install job-shop-lib`）
- **功能**: OR-Tools 求解器、调度规则、模拟退火、可视化
- **文档**: https://job-shop-lib.readthedocs.io/

### 2. Schlably
- **类型**: Python 框架（本地源码）
- **功能**: 深度强化学习（PPO/DQN）、YAML 配置、实验追踪
- **文档**: https://schlably.readthedocs.io/

### 3. Graph-JSP-Env
- **类型**: Python 包（`pip install graph-jsp-env`）
- **功能**: Gymnasium 环境、析取图、实时渲染
- **文档**: https://graph-jsp-env.readthedocs.io/

---

## ⚠️ 当前状态说明

### 您的项目与这些库的关系

| 库 | 您的代码 | 实际调用 | 说明 |
|----|---------|---------|------|
| JobShopLib | ✅ 有集成代码 | ❌ 未安装库 | 代码在 `unified_solver.py`，但库未安装 |
| Graph-JSP-Env | ✅ 有集成代码 | ❌ 未安装库 | 代码在 `data_adapter.py`，但库未安装 |
| Schlably | ⚠️ 仅格式转换 | ❌ 未集成 | 只有数据格式转换函数 |

**核心要点**：
- ✅ 您的项目**写好了调用代码**（在 `unified_fjsp_system/` 中）
- ❌ 这些库**没有安装**，所以不会真正调用
- ⚠️ 程序有容错处理，不会崩溃，只是这些功能不可用
- 🔌 **安装后立即可用**，无需改代码

---

## 🧪 测试脚本

### `test_current_project.sh` - 测试您的项目

**用途**: 测试您的项目代码能否成功集成这些库

```bash
./test_current_project.sh
```

**自动执行**：
1. 创建 conda 环境（Python 3.10）
2. 安装依赖（job-shop-lib、graph-jsp-env 等）
3. 测试您的集成代码
4. 生成测试报告

**测试内容**：
- ✅ DataAdapter 格式转换
- ✅ JobShopLibSolver 能否调用
- ✅ UnifiedVisualizer 功能
- ✅ 遗传算法求解器
- ✅ Web 界面模块

**报告位置**: `/tmp/fjsp_test_report.md`

---

## 💡 使用建议

### 如果您想使用这些库的功能

运行测试脚本：
```bash
./test_current_project.sh
```

脚本会自动安装并测试集成。

### 如果不需要这些库

您的项目可以独立运行：
- ✅ 遗传算法求解器（您自己实现的）
- ✅ 可视化（Plotly + Matplotlib）
- ✅ Web 界面（Streamlit + Flask）
- ✅ 数据生成和管理

这些功能完全不依赖参考库。

---

## 🎯 您的项目优势

相比这三个参考库，您的项目独有：

1. 🏆 **Streamlit + Flask Web 界面** - 参考库都没有
2. 🏆 **REST API** - 参考库都没有
3. 🏆 **统一数据适配器** - 可以转换三个库的格式
4. 🏆 **并行求解** - 多算法同时运行

**参考库只是可选的增强**，不是必需的。

---

## 📖 参考库代码位置

如果您想学习参考库的实现：

### JobShopLib 核心代码
- 求解器：`job_shop_lib/job_shop_lib/constraint_programming/`
- 调度规则：`job_shop_lib/job_shop_lib/dispatching/`
- 可视化：`job_shop_lib/job_shop_lib/visualization/`

### Schlably 核心代码
- RL 算法：`schlably/src/agents/reinforcement_learning/`
- 启发式：`schlably/src/agents/heuristic/`
- 环境：`schlably/src/environments/`

### Graph-JSP-Env 核心代码
- 环境：`graph-jsp-env/src/graph_jsp_env/disjunctive_graph_jsp_env.py`
- 可视化：`graph-jsp-env/src/graph_jsp_env/disjunctive_graph_jsp_visualizer.py`

---

**仅供参考学习，不影响您的项目正常使用。**
