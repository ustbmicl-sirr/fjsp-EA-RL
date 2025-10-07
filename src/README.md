# 🔬 FJSP研究框架

## 📋 框架概述

这是轻量级的FJSP研究框架，专门用于算法原型开发和学术研究。

### 🎯 设计目标
- **轻量级**: 最小依赖，快速启动
- **研究导向**: 专注算法开发和实验
- **模块化**: 清晰的功能分离
- **可扩展**: 易于添加新算法和特征

## 🏗️ 框架结构

```
src/fjsp/
├── 📊 data/                    # 数据处理模块
│   ├── __init__.py
│   └── instances.py           # FJSP实例数据结构
├── 🔍 features/               # 特征工程模块  
│   ├── __init__.py
│   └── extractors.py          # 实例特征提取器
├── 🎯 recommend/              # 策略推荐模块
│   ├── __init__.py
│   └── strategies.py          # 初始化策略推荐
├── 🧬 optimizers/             # 优化算法模块
│   ├── __init__.py
│   ├── bwo.py                 # BWO算法实现
│   └── pymoo_nsga2.py         # NSGA-II集成
├── 📈 metrics/                # 性能指标模块
│   ├── __init__.py
│   └── indicators.py          # 多目标性能指标
├── 🧪 experiments/            # 实验框架模块
│   ├── __init__.py
│   └── run_experiment.py      # 实验运行器
└── 🎨 vis/                    # 可视化模块
    ├── __init__.py
    └── plots.py               # 基础图表功能
```

## 🚀 快速开始

### 基本使用
```python
from src.fjsp.data.instances import parse_fjsplib
from src.fjsp.features.extractors import BasicFeatureExtractor
from src.fjsp.optimizers.pymoo_nsga2 import NSGAIIOptimizer

# 加载实例
instance = parse_fjsplib("path/to/instance.fjs")

# 提取特征
extractor = BasicFeatureExtractor()
features = extractor.extract(instance)

# 运行优化
optimizer = NSGAIIOptimizer()
result = optimizer.run(instance)
```

### 实验示例
```bash
# 运行NSGA-II示例
cd examples
python run_nsga2_example.py
```

## 🔬 与unified_fjsp_system的区别

| 特性 | src/fjsp | unified_fjsp_system |
|------|----------|---------------------|
| **定位** | 研究框架 | 生产系统 |
| **复杂度** | 轻量级 | 完整功能 |
| **界面** | 命令行 | Web界面 |
| **算法** | 原型实现 | 多算法集成 |
| **可视化** | 基础图表 | 交互式可视化 |
| **部署** | 本地开发 | 前后端分离 |

## 🎯 使用场景

### 1. 算法开发
- 新算法原型实现
- 算法参数调优
- 性能基准测试

### 2. 学术研究
- 论文实验代码
- 算法对比研究
- 特征工程探索

### 3. 教学用途
- 算法原理演示
- 编程练习框架
- 概念验证代码

## 📚 核心模块说明

### data模块
- `Instance`: FJSP实例数据结构
- `Operation`: 工序定义
- `parse_fjsplib()`: 标准格式解析

### features模块
- `BasicFeatureExtractor`: 基础实例特征
- `GraphFeatureExtractor`: 析取图特征
- 支持自定义特征提取器

### recommend模块
- `SimilarityRecommender`: 相似度推荐
- `ParetoRecommender`: 帕累托前沿推荐
- `ThompsonSamplingRecommender`: 强化学习推荐

### optimizers模块
- `BWOOptimizer`: 改进BWO算法
- `NSGAIIOptimizer`: NSGA-II集成
- 统一的优化器接口

### metrics模块
- `makespan()`: 完工时间计算
- `convergence_metrics()`: 收敛性指标
- `stability_metrics()`: 稳定性指标

## 🔧 扩展开发

### 添加新算法
```python
from src.fjsp.optimizers.base import BaseOptimizer

class CustomOptimizer(BaseOptimizer):
    def run(self, instance, **kwargs):
        # 算法实现
        return result
```

### 添加新特征
```python
from src.fjsp.features.base import BaseExtractor

class CustomExtractor(BaseExtractor):
    def extract(self, instance):
        # 特征提取逻辑
        return features
```

## 📖 相关文档

- [完整系统文档](../documentation/README.md)
- [软件设计规范](../documentation/design/FJSP_SOFTWARE_DESIGN_SPECIFICATION.md)
- [使用指南](../documentation/guides/SYSTEM_SUMMARY_AND_USAGE.md)

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 发起Pull Request

---

**框架版本**: v1.0.0  
**维护团队**: FJSP研究组  
**最后更新**: 2025年10月7日
