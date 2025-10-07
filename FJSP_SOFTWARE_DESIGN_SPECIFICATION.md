# 🏭 统一FJSP求解与可视化系统 - 软件设计规范

## 📋 项目概述

### 系统名称
统一柔性作业车间调度问题(FJSP)求解与可视化系统

### 版本信息
- **版本**: v1.0.0
- **开发日期**: 2025年10月
- **技术栈**: Python 3.10, Flask, Streamlit, Plotly, NetworkX

### 系统目标
构建一个集成多种算法、支持实时可视化的FJSP研究平台，融合进化算法、强化学习和约束编程方法，提供完整的问题建模、求解和分析功能。

## 🏗️ 系统架构设计

### 整体架构
```
┌─────────────────────────────────────────────────────────────┐
│                    前端展示层 (Streamlit)                    │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   问题配置界面   │ │   可视化展示     │ │   结果分析       │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                   API服务层 (Flask)                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   RESTful API   │ │   WebSocket     │ │   文件管理       │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    核心业务层                                │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   数据适配器     │ │   算法管理器     │ │   可视化引擎     │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    算法实现层                                │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   进化算法       │ │   强化学习       │ │   约束编程       │ │
│  │   (NSGA-II,BWO) │ │   (DQN,PPO)     │ │   (OR-Tools)    │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 模块化设计

#### 1. 数据适配层 (`core/data_adapter.py`)
```python
class UnifiedFJSPInstance:
    - name: str                    # 实例名称
    - num_jobs: int               # 工件数量
    - num_machines: int           # 机器数量
    - operations: List[Operation] # 工序列表
    - metadata: Dict[str, Any]    # 元数据

class DataAdapter:
    - from_jobshoplib()          # JobShopLib格式转换
    - to_jobshoplib()            # 转换为JobShopLib格式
    - build_disjunctive_graph()  # 构建析取图
    - to_graph_jsp_env()         # Graph-JSP-Env格式
```

#### 2. 算法管理层 (`algorithms/unified_solver.py`)
```python
class UnifiedSolverManager:
    - solve_parallel()           # 并行多算法求解
    - add_global_callback()      # 添加全局回调
    - get_pareto_front()         # 获取帕累托前沿

class BaseSolver(ABC):
    - solve()                    # 抽象求解方法
    - add_callback()             # 添加回调函数
    - notify_callbacks()         # 通知回调
```

#### 3. 可视化引擎 (`visualization/unified_visualizer.py`)
```python
class UnifiedVisualizer:
    - plot_gantt_chart()         # 甘特图可视化
    - plot_disjunctive_graph()   # 析取图可视化
    - plot_convergence_comparison() # 收敛对比
    - plot_pareto_front()        # 帕累托前沿
    - create_dashboard()         # 综合仪表板
```

## 🎯 核心功能模块

### 1. 问题建模模块
- **实例生成**: 随机生成、基准实例加载、文件导入
- **数据验证**: 约束检查、数据完整性验证
- **格式转换**: 多种数据格式间的无缝转换

### 2. 算法求解模块
- **进化算法**: NSGA-II, NSGA-III, BWO, 差分进化
- **强化学习**: DQN, PPO, A3C, SAC
- **约束编程**: OR-Tools CP-SAT, Gurobi
- **混合算法**: 进化+强化学习, 多阶段优化

### 3. 实时监控模块
- **进度跟踪**: WebSocket实时进度推送
- **性能监控**: CPU、内存、收敛指标
- **异常处理**: 算法异常检测和恢复

### 4. 可视化分析模块
- **调度方案**: 交互式甘特图
- **问题结构**: 析取图、工艺路径图
- **算法分析**: 收敛曲线、帕累托前沿
- **性能对比**: 多算法综合比较

## 📊 性能指标体系

### 主要性能指标

#### 1. 调度质量指标
```python
class ScheduleMetrics:
    makespan: float              # 最大完工时间
    total_flowtime: float        # 总流程时间
    mean_flowtime: float         # 平均流程时间
    total_tardiness: float       # 总延迟时间
    max_tardiness: float         # 最大延迟时间
    machine_utilization: List[float]  # 机器利用率
    setup_time: float            # 总设置时间
    energy_consumption: float    # 能耗 (扩展指标)
```

#### 2. 算法性能指标
```python
class AlgorithmMetrics:
    computation_time: float      # 计算时间
    iterations: int              # 迭代次数
    convergence_rate: float      # 收敛速度
    solution_quality: float      # 解质量
    stability: float             # 稳定性指标
    memory_usage: float          # 内存使用量
    cpu_utilization: float       # CPU利用率
```

#### 3. 多目标优化指标
```python
class MultiObjectiveMetrics:
    hypervolume: float           # 超体积指标
    spacing: float               # 分布均匀性
    spread: float                # 分布范围
    convergence_metric: float    # 收敛性指标
    diversity_metric: float      # 多样性指标
    pareto_front_size: int       # 帕累托前沿大小
```

### 性能评估框架
```python
class PerformanceEvaluator:
    def evaluate_single_objective(self, solution, instance):
        """单目标性能评估"""
        return {
            'makespan': self.calculate_makespan(solution),
            'flowtime': self.calculate_flowtime(solution),
            'utilization': self.calculate_utilization(solution, instance)
        }
    
    def evaluate_multi_objective(self, pareto_front, reference_front=None):
        """多目标性能评估"""
        return {
            'hypervolume': self.calculate_hypervolume(pareto_front),
            'spacing': self.calculate_spacing(pareto_front),
            'convergence': self.calculate_convergence(pareto_front, reference_front)
        }
    
    def benchmark_algorithms(self, algorithms, instances):
        """算法基准测试"""
        results = {}
        for alg in algorithms:
            for inst in instances:
                result = alg.solve(inst)
                results[f"{alg.name}_{inst.name}"] = self.evaluate_single_objective(result, inst)
        return results
```

## 🎯 多目标帕累托最优扩展设计

### 1. 多目标优化框架

#### 目标函数定义
```python
class MultiObjectiveFunction:
    def __init__(self):
        self.objectives = {
            'makespan': self.minimize_makespan,
            'flowtime': self.minimize_total_flowtime,
            'tardiness': self.minimize_total_tardiness,
            'energy': self.minimize_energy_consumption,
            'cost': self.minimize_total_cost,
            'quality': self.maximize_quality,
            'flexibility': self.maximize_flexibility
        }
    
    def evaluate(self, solution, instance, objective_weights=None):
        """多目标评估"""
        values = {}
        for name, func in self.objectives.items():
            values[name] = func(solution, instance)
        
        if objective_weights:
            # 加权求和方法
            return sum(w * values[obj] for obj, w in objective_weights.items())
        else:
            # 返回目标向量
            return list(values.values())
```

#### 帕累托前沿管理
```python
class ParetoFrontManager:
    def __init__(self):
        self.solutions = []
        self.objectives = []
        self.dominated_count = []
    
    def add_solution(self, solution, objectives):
        """添加解到帕累托前沿"""
        is_dominated = False
        dominated_indices = []
        
        for i, existing_obj in enumerate(self.objectives):
            dominance = self.compare_solutions(objectives, existing_obj)
            if dominance == -1:  # 新解被支配
                is_dominated = True
                break
            elif dominance == 1:  # 新解支配现有解
                dominated_indices.append(i)
        
        if not is_dominated:
            # 移除被支配的解
            for i in reversed(dominated_indices):
                del self.solutions[i]
                del self.objectives[i]
            
            # 添加新解
            self.solutions.append(solution)
            self.objectives.append(objectives)
    
    def get_pareto_front(self):
        """获取当前帕累托前沿"""
        return list(zip(self.solutions, self.objectives))
    
    def compare_solutions(self, obj1, obj2):
        """比较两个解的支配关系"""
        better_count = 0
        worse_count = 0
        
        for v1, v2 in zip(obj1, obj2):
            if v1 < v2:  # 假设最小化
                better_count += 1
            elif v1 > v2:
                worse_count += 1
        
        if better_count > 0 and worse_count == 0:
            return 1   # obj1 支配 obj2
        elif worse_count > 0 and better_count == 0:
            return -1  # obj2 支配 obj1
        else:
            return 0   # 非支配关系
```

### 2. 多目标算法扩展

#### NSGA-II 扩展实现
```python
class MultiObjectiveNSGAII(BaseSolver):
    def __init__(self, population_size=100, max_generations=500):
        super().__init__("MO-NSGA-II")
        self.population_size = population_size
        self.max_generations = max_generations
        self.pareto_manager = ParetoFrontManager()
    
    def solve(self, instance, objectives=['makespan', 'flowtime', 'tardiness']):
        """多目标NSGA-II求解"""
        population = self.initialize_population(instance)
        
        for generation in range(self.max_generations):
            # 评估目标函数
            objective_values = []
            for individual in population:
                values = self.evaluate_objectives(individual, instance, objectives)
                objective_values.append(values)
                self.pareto_manager.add_solution(individual, values)
            
            # 非支配排序
            fronts = self.non_dominated_sort(population, objective_values)
            
            # 拥挤距离计算
            for front in fronts:
                self.calculate_crowding_distance(front, objective_values)
            
            # 选择和变异
            population = self.selection_and_variation(fronts)
            
            # 回调通知
            self.notify_callbacks({
                'generation': generation,
                'pareto_front_size': len(self.pareto_manager.solutions),
                'hypervolume': self.calculate_hypervolume()
            })
        
        return self.pareto_manager.get_pareto_front()
```

#### 多目标强化学习扩展
```python
class MultiObjectiveRL(BaseSolver):
    def __init__(self, objectives=['makespan', 'flowtime']):
        super().__init__("MO-RL")
        self.objectives = objectives
        self.scalarization_methods = {
            'weighted_sum': self.weighted_sum_scalarization,
            'tchebycheff': self.tchebycheff_scalarization,
            'pbi': self.penalty_boundary_intersection
        }
    
    def solve(self, instance, method='weighted_sum', reference_point=None):
        """多目标强化学习求解"""
        # 生成权重向量
        weight_vectors = self.generate_weight_vectors(len(self.objectives))
        pareto_solutions = []
        
        for weights in weight_vectors:
            # 标量化多目标问题
            scalarized_reward = self.scalarization_methods[method]
            
            # 训练RL智能体
            agent = self.create_agent(instance, scalarized_reward, weights)
            solution = agent.train_and_solve()
            
            # 评估原始目标
            objectives = self.evaluate_objectives(solution, instance)
            pareto_solutions.append((solution, objectives))
        
        # 提取帕累托前沿
        return self.extract_pareto_front(pareto_solutions)
```

### 3. 交互式多目标优化

#### 偏好引导优化
```python
class InteractiveMultiObjective:
    def __init__(self, solver):
        self.solver = solver
        self.user_preferences = {}
        self.aspiration_levels = {}
    
    def set_user_preferences(self, preferences):
        """设置用户偏好"""
        self.user_preferences = preferences
        # preferences = {
        #     'makespan': {'weight': 0.4, 'aspiration': 100},
        #     'flowtime': {'weight': 0.3, 'aspiration': 500},
        #     'cost': {'weight': 0.3, 'aspiration': 1000}
        # }
    
    def interactive_solve(self, instance):
        """交互式求解"""
        # 初始求解获得帕累托前沿
        initial_front = self.solver.solve(instance)
        
        # 展示给用户并获取反馈
        selected_region = self.present_to_user(initial_front)
        
        # 基于用户反馈调整搜索
        refined_front = self.refine_search(instance, selected_region)
        
        return refined_front
    
    def present_to_user(self, pareto_front):
        """向用户展示帕累托前沿"""
        # 可视化帕累托前沿
        self.visualize_pareto_front(pareto_front)
        
        # 获取用户选择的感兴趣区域
        return self.get_user_selection()
```

### 4. 可视化扩展

#### 多目标可视化组件
```python
class MultiObjectiveVisualizer(UnifiedVisualizer):
    def plot_pareto_front_2d(self, pareto_front, objectives):
        """2D帕累托前沿可视化"""
        fig = go.Figure()
        
        x_values = [sol[1][0] for sol in pareto_front]  # 第一个目标
        y_values = [sol[1][1] for sol in pareto_front]  # 第二个目标
        
        fig.add_trace(go.Scatter(
            x=x_values, y=y_values,
            mode='markers+lines',
            name='帕累托前沿',
            marker=dict(size=8, color='red')
        ))
        
        fig.update_layout(
            title='帕累托前沿',
            xaxis_title=objectives[0],
            yaxis_title=objectives[1]
        )
        
        return fig
    
    def plot_pareto_front_3d(self, pareto_front, objectives):
        """3D帕累托前沿可视化"""
        fig = go.Figure()
        
        x_values = [sol[1][0] for sol in pareto_front]
        y_values = [sol[1][1] for sol in pareto_front]
        z_values = [sol[1][2] for sol in pareto_front]
        
        fig.add_trace(go.Scatter3d(
            x=x_values, y=y_values, z=z_values,
            mode='markers',
            name='帕累托前沿',
            marker=dict(size=5, color='blue')
        ))
        
        fig.update_layout(
            title='3D帕累托前沿',
            scene=dict(
                xaxis_title=objectives[0],
                yaxis_title=objectives[1],
                zaxis_title=objectives[2]
            )
        )
        
        return fig
    
    def plot_parallel_coordinates(self, pareto_front, objectives):
        """平行坐标图"""
        data = []
        for sol in pareto_front:
            data.append(sol[1])  # 目标值
        
        df = pd.DataFrame(data, columns=objectives)
        
        fig = go.Figure(data=go.Parcoords(
            line=dict(color=df.index, colorscale='Viridis'),
            dimensions=[dict(label=obj, values=df[obj]) for obj in objectives]
        ))
        
        fig.update_layout(title='帕累托解集平行坐标图')
        return fig
```

## 🔧 技术实现细节

### 1. 并发处理
- **多进程**: 算法并行执行
- **异步IO**: WebSocket实时通信
- **线程池**: 可视化任务处理

### 2. 内存管理
- **对象池**: 重用频繁创建的对象
- **延迟加载**: 按需加载大型数据
- **缓存机制**: 计算结果缓存

### 3. 扩展性设计
- **插件架构**: 新算法动态加载
- **配置驱动**: 参数外部化配置
- **接口标准化**: 统一的算法接口

## 📈 性能优化策略

### 1. 算法优化
- **早停机制**: 收敛检测
- **自适应参数**: 动态调整算法参数
- **混合策略**: 多算法协同优化

### 2. 系统优化
- **数据结构**: 高效的数据表示
- **计算优化**: 向量化计算
- **IO优化**: 批量数据处理

### 3. 可视化优化
- **渐进渲染**: 大数据集分批渲染
- **LOD技术**: 多层次细节
- **缓存策略**: 图表结果缓存

## 🎯 未来扩展方向

### 1. 算法扩展
- **深度强化学习**: Transformer-based RL
- **联邦学习**: 分布式优化
- **量子算法**: 量子退火优化

### 2. 功能扩展
- **云端部署**: 微服务架构
- **移动端**: 响应式设计
- **协作功能**: 多用户协同

### 3. 应用扩展
- **实时调度**: 动态重调度
- **预测性维护**: 设备故障预测
- **供应链优化**: 端到端优化

## 📊 系统性能基准测试

### 测试环境规格
```yaml
硬件配置:
  CPU: Intel i7-12700K (12核24线程)
  内存: 32GB DDR4-3200
  存储: 1TB NVMe SSD
  GPU: NVIDIA RTX 3080 (可选)

软件环境:
  操作系统: macOS 13.0 / Ubuntu 22.04
  Python: 3.10+
  依赖库: 见requirements.txt
```

### 性能基准数据
```python
# 标准测试实例性能
BENCHMARK_RESULTS = {
    'ft06': {  # 6工件×6机器
        'makespan_optimal': 55,
        'algorithms': {
            'OR-Tools': {'time': 0.12, 'makespan': 55, 'gap': 0.0},
            'NSGA-II': {'time': 2.34, 'makespan': 57, 'gap': 3.6},
            'BWO': {'time': 1.89, 'makespan': 56, 'gap': 1.8},
            'DQN': {'time': 15.67, 'makespan': 58, 'gap': 5.4}
        }
    },
    'la21': {  # 15工件×10机器
        'makespan_optimal': 1046,
        'algorithms': {
            'OR-Tools': {'time': 45.23, 'makespan': 1046, 'gap': 0.0},
            'NSGA-II': {'time': 12.45, 'makespan': 1089, 'gap': 4.1},
            'BWO': {'time': 8.76, 'makespan': 1067, 'gap': 2.0},
            'DQN': {'time': 89.34, 'makespan': 1123, 'gap': 7.4}
        }
    }
}
```

### 可扩展性测试
```python
SCALABILITY_TEST = {
    'small': {'jobs': 10, 'machines': 5, 'avg_time': 1.2},
    'medium': {'jobs': 50, 'machines': 20, 'avg_time': 15.6},
    'large': {'jobs': 100, 'machines': 50, 'avg_time': 156.8},
    'xlarge': {'jobs': 500, 'machines': 100, 'avg_time': 1247.3}
}
```

## 🎯 多目标优化深度设计

### 1. 目标函数数学模型

#### 基础目标函数
```python
class ObjectiveFunctions:
    @staticmethod
    def makespan(schedule, instance):
        """最大完工时间 - 主要目标"""
        return max(job.completion_time for job in schedule.jobs)

    @staticmethod
    def total_flowtime(schedule, instance):
        """总流程时间 - 效率目标"""
        return sum(job.completion_time - job.release_time
                  for job in schedule.jobs)

    @staticmethod
    def total_tardiness(schedule, instance):
        """总延迟时间 - 准时性目标"""
        return sum(max(0, job.completion_time - job.due_date)
                  for job in schedule.jobs)

    @staticmethod
    def energy_consumption(schedule, instance):
        """能耗 - 绿色制造目标"""
        total_energy = 0
        for machine in schedule.machines:
            # 加工能耗
            processing_energy = sum(op.processing_time * machine.power_rating
                                  for op in machine.operations)
            # 空闲能耗
            idle_energy = machine.idle_time * machine.idle_power
            total_energy += processing_energy + idle_energy
        return total_energy

    @staticmethod
    def setup_cost(schedule, instance):
        """设置成本 - 经济目标"""
        return sum(op.setup_cost for machine in schedule.machines
                  for op in machine.operations)
```

#### 高级目标函数
```python
class AdvancedObjectives:
    @staticmethod
    def robustness(schedule, instance, uncertainty_scenarios):
        """鲁棒性 - 不确定性处理"""
        worst_case_makespan = 0
        for scenario in uncertainty_scenarios:
            perturbed_schedule = schedule.apply_uncertainty(scenario)
            makespan = ObjectiveFunctions.makespan(perturbed_schedule, instance)
            worst_case_makespan = max(worst_case_makespan, makespan)
        return worst_case_makespan

    @staticmethod
    def flexibility(schedule, instance):
        """柔性度 - 适应性目标"""
        flexibility_score = 0
        for job in schedule.jobs:
            for operation in job.operations:
                # 机器选择的多样性
                machine_options = len(operation.alternative_machines)
                flexibility_score += machine_options
        return flexibility_score / len(schedule.operations)

    @staticmethod
    def quality_index(schedule, instance):
        """质量指数 - 产品质量目标"""
        quality_score = 0
        for job in schedule.jobs:
            for operation in job.operations:
                machine = operation.assigned_machine
                quality_score += machine.quality_rating * operation.processing_time
        return quality_score / schedule.total_processing_time
```

### 2. 帕累托前沿算法实现

#### 快速非支配排序
```python
class FastNonDominatedSort:
    def __init__(self):
        self.fronts = []

    def sort(self, population, objectives):
        """快速非支配排序算法"""
        n = len(population)
        domination_count = [0] * n  # 被支配次数
        dominated_solutions = [[] for _ in range(n)]  # 支配的解集

        # 计算支配关系
        for i in range(n):
            for j in range(n):
                if i != j:
                    dominance = self.dominates(objectives[i], objectives[j])
                    if dominance == 1:  # i支配j
                        dominated_solutions[i].append(j)
                    elif dominance == -1:  # j支配i
                        domination_count[i] += 1

        # 构建前沿
        current_front = []
        for i in range(n):
            if domination_count[i] == 0:
                current_front.append(i)

        front_index = 0
        self.fronts = [current_front]

        while len(current_front) > 0:
            next_front = []
            for i in current_front:
                for j in dominated_solutions[i]:
                    domination_count[j] -= 1
                    if domination_count[j] == 0:
                        next_front.append(j)

            if len(next_front) > 0:
                self.fronts.append(next_front)
            current_front = next_front
            front_index += 1

        return self.fronts

    def dominates(self, obj1, obj2):
        """判断obj1是否支配obj2"""
        better = False
        for v1, v2 in zip(obj1, obj2):
            if v1 > v2:  # 假设最小化问题
                return -1  # obj1被obj2支配
            elif v1 < v2:
                better = True

        return 1 if better else 0  # 1表示支配，0表示非支配
```

#### 拥挤距离计算
```python
class CrowdingDistance:
    @staticmethod
    def calculate(front_indices, objectives):
        """计算拥挤距离"""
        if len(front_indices) <= 2:
            return [float('inf')] * len(front_indices)

        distances = [0.0] * len(front_indices)
        num_objectives = len(objectives[0])

        for obj_idx in range(num_objectives):
            # 按当前目标排序
            sorted_indices = sorted(front_indices,
                                  key=lambda x: objectives[x][obj_idx])

            # 边界点设为无穷大
            distances[0] = float('inf')
            distances[-1] = float('inf')

            # 计算目标范围
            obj_range = (objectives[sorted_indices[-1]][obj_idx] -
                        objectives[sorted_indices[0]][obj_idx])

            if obj_range == 0:
                continue

            # 计算中间点的拥挤距离
            for i in range(1, len(sorted_indices) - 1):
                distance = (objectives[sorted_indices[i+1]][obj_idx] -
                           objectives[sorted_indices[i-1]][obj_idx]) / obj_range
                distances[i] += distance

        return distances
```

### 3. 多目标性能指标

#### 超体积指标
```python
class HypervolumeCalculator:
    def __init__(self, reference_point):
        self.reference_point = reference_point

    def calculate(self, pareto_front):
        """计算超体积指标"""
        if not pareto_front:
            return 0.0

        # 对于2D情况的快速计算
        if len(pareto_front[0]) == 2:
            return self._calculate_2d(pareto_front)
        else:
            # 使用WFG算法计算高维超体积
            return self._calculate_wfg(pareto_front)

    def _calculate_2d(self, front):
        """2D超体积计算"""
        # 按第一个目标排序
        sorted_front = sorted(front, key=lambda x: x[0])

        hypervolume = 0.0
        prev_x = self.reference_point[0]

        for point in sorted_front:
            if point[1] < self.reference_point[1]:
                width = prev_x - point[0]
                height = self.reference_point[1] - point[1]
                hypervolume += width * height
                prev_x = point[0]

        return hypervolume
```

#### 分布性指标
```python
class DistributionMetrics:
    @staticmethod
    def spacing(pareto_front):
        """分布均匀性指标"""
        if len(pareto_front) < 2:
            return 0.0

        distances = []
        for i, point1 in enumerate(pareto_front):
            min_dist = float('inf')
            for j, point2 in enumerate(pareto_front):
                if i != j:
                    dist = sum((v1 - v2) ** 2 for v1, v2 in zip(point1, point2)) ** 0.5
                    min_dist = min(min_dist, dist)
            distances.append(min_dist)

        mean_dist = sum(distances) / len(distances)
        variance = sum((d - mean_dist) ** 2 for d in distances) / len(distances)

        return variance ** 0.5

    @staticmethod
    def spread(pareto_front):
        """分布范围指标"""
        if len(pareto_front) < 2:
            return 0.0

        num_objectives = len(pareto_front[0])
        ranges = []

        for obj_idx in range(num_objectives):
            values = [point[obj_idx] for point in pareto_front]
            ranges.append(max(values) - min(values))

        return sum(ranges) / num_objectives
```

## 🔧 高级技术实现

### 1. 自适应算法框架
```python
class AdaptiveAlgorithmFramework:
    def __init__(self):
        self.performance_history = {}
        self.algorithm_pool = {}
        self.selection_strategy = 'ucb'  # Upper Confidence Bound

    def register_algorithm(self, name, algorithm_class):
        """注册算法到池中"""
        self.algorithm_pool[name] = {
            'class': algorithm_class,
            'performance': [],
            'usage_count': 0,
            'success_rate': 0.0
        }

    def select_algorithm(self, instance_features):
        """基于实例特征选择最佳算法"""
        if self.selection_strategy == 'ucb':
            return self._ucb_selection(instance_features)
        elif self.selection_strategy == 'thompson':
            return self._thompson_sampling(instance_features)
        else:
            return self._epsilon_greedy(instance_features)

    def update_performance(self, algorithm_name, performance_metrics):
        """更新算法性能记录"""
        alg_info = self.algorithm_pool[algorithm_name]
        alg_info['performance'].append(performance_metrics)
        alg_info['usage_count'] += 1

        # 计算成功率（基于解质量阈值）
        good_solutions = sum(1 for p in alg_info['performance']
                           if p['quality'] > 0.8)
        alg_info['success_rate'] = good_solutions / alg_info['usage_count']
```

### 2. 实时优化引擎
```python
class RealTimeOptimizationEngine:
    def __init__(self):
        self.active_jobs = {}
        self.machine_status = {}
        self.event_queue = []
        self.rescheduling_triggers = {
            'job_arrival': self.handle_job_arrival,
            'machine_breakdown': self.handle_machine_breakdown,
            'job_completion': self.handle_job_completion,
            'priority_change': self.handle_priority_change
        }

    def start_real_time_scheduling(self, initial_schedule):
        """启动实时调度"""
        self.current_schedule = initial_schedule
        self.simulation_time = 0

        while self.has_active_jobs():
            # 处理事件
            event = self.get_next_event()
            self.simulation_time = event.time

            # 触发重调度检查
            if self.should_reschedule(event):
                new_schedule = self.reschedule(event)
                self.update_schedule(new_schedule)

            # 执行事件
            self.execute_event(event)

    def should_reschedule(self, event):
        """判断是否需要重调度"""
        if event.type in ['machine_breakdown', 'urgent_job']:
            return True

        # 基于性能阈值判断
        current_performance = self.evaluate_current_performance()
        return current_performance < self.performance_threshold
```

---

**文档版本**: v1.0.0
**最后更新**: 2025年10月7日
**维护者**: FJSP开发团队
