# API 参考文档

## 📊 核心数据结构

### UnifiedOperation

表示FJSP中的单个操作。

```python
@dataclass
class UnifiedOperation:
    job_id: int                    # 作业ID
    operation_id: int              # 操作ID  
    machines: List[int]            # 可用机器列表
    processing_times: List[float]  # 对应机器的处理时间
    setup_time: float = 0.0        # 设置时间
    due_date: Optional[float] = None # 截止时间
    release_time: float = 0.0      # 释放时间
```

**示例**:
```python
operation = UnifiedOperation(
    job_id=0,
    operation_id=0,
    machines=[0, 1, 2],
    processing_times=[10.0, 12.0, 8.0],
    setup_time=2.0
)
```

### UnifiedFJSPInstance

表示完整的FJSP实例。

```python
@dataclass
class UnifiedFJSPInstance:
    name: str                           # 实例名称
    num_jobs: int                       # 作业数量
    num_machines: int                   # 机器数量
    operations: List[UnifiedOperation]  # 操作列表
    metadata: Dict[str, Any] = None     # 元数据
```

**方法**:
- `get_operation_by_id(job_id, op_id)`: 根据ID获取操作
- `get_operations_by_job(job_id)`: 获取指定作业的所有操作
- `validate()`: 验证实例数据完整性

### SolutionResult

表示求解结果。

```python
@dataclass
class SolutionResult:
    schedule: Dict[str, Any]           # 调度方案
    makespan: float                    # 最大完工时间
    objectives: Dict[str, float]       # 目标函数值
    algorithm: str                     # 使用的算法
    computation_time: float            # 计算时间
    iterations: int = 0                # 迭代次数
    convergence_history: List[float] = None # 收敛历史
    metadata: Dict[str, Any] = None    # 元数据
```

## 🔄 数据适配器 API

### DataAdapter

提供多种数据格式之间的转换。

```python
class DataAdapter:
    @staticmethod
    def from_jobshoplib(instance) -> UnifiedFJSPInstance:
        """从JobShopLib格式转换"""
        
    @staticmethod  
    def to_jobshoplib(instance: UnifiedFJSPInstance):
        """转换为JobShopLib格式"""
        
    @staticmethod
    def to_graph_jsp_env(instance: UnifiedFJSPInstance) -> np.ndarray:
        """转换为Graph-JSP-Env格式"""
        
    @staticmethod
    def to_schlably_format(instance: UnifiedFJSPInstance) -> Dict:
        """转换为Schlably格式"""
        
    @staticmethod
    def build_disjunctive_graph(instance: UnifiedFJSPInstance) -> nx.DiGraph:
        """构建析取图"""
```

**示例**:
```python
# 构建析取图
graph = DataAdapter.build_disjunctive_graph(instance)
print(f"节点数: {graph.number_of_nodes()}")
print(f"边数: {graph.number_of_edges()}")

# 转换格式
jsp_array = DataAdapter.to_graph_jsp_env(instance)
schlably_dict = DataAdapter.to_schlably_format(instance)
```

### InstanceGenerator

生成和加载FJSP实例。

```python
class InstanceGenerator:
    @staticmethod
    def generate_random_fjsp(
        num_jobs: int,
        num_machines: int, 
        max_operations_per_job: int,
        flexibility: float = 0.5,
        processing_time_range: Tuple[int, int] = (1, 20)
    ) -> UnifiedFJSPInstance:
        """生成随机FJSP实例"""
        
    @staticmethod
    def load_benchmark(name: str) -> UnifiedFJSPInstance:
        """加载基准实例"""
        
    @staticmethod
    def parse_file(filepath: str) -> UnifiedFJSPInstance:
        """解析文件实例"""
```

**示例**:
```python
# 生成随机实例
instance = InstanceGenerator.generate_random_fjsp(
    num_jobs=5,
    num_machines=4,
    max_operations_per_job=3,
    flexibility=0.6
)

# 加载基准实例
benchmark = InstanceGenerator.load_benchmark("ft06")
```

## 🧠 求解器 API

### BaseSolver

所有求解器的抽象基类。

```python
class BaseSolver(ABC):
    def __init__(self, name: str):
        """初始化求解器"""
        
    def add_callback(self, callback: Callable):
        """添加进度回调函数"""
        
    def notify_callbacks(self, data: Dict[str, Any]):
        """通知回调函数"""
        
    @abstractmethod
    def solve(self, instance: UnifiedFJSPInstance, **kwargs) -> SolutionResult:
        """求解FJSP实例"""
```

### EvolutionaryAlgorithmSolver

进化算法求解器。

```python
class EvolutionaryAlgorithmSolver(BaseSolver):
    def solve(self, instance: UnifiedFJSPInstance, **kwargs) -> SolutionResult:
        """使用进化算法求解"""
```

**参数**:
- `population_size`: 种群大小 (默认: 50)
- `generations`: 进化代数 (默认: 100)
- `mutation_rate`: 变异率 (默认: 0.1)
- `crossover_rate`: 交叉率 (默认: 0.8)

**示例**:
```python
solver = EvolutionaryAlgorithmSolver()
result = solver.solve(
    instance,
    population_size=100,
    generations=200,
    mutation_rate=0.15,
    crossover_rate=0.85
)
```

### ReinforcementLearningSolver

强化学习求解器。

```python
class ReinforcementLearningSolver(BaseSolver):
    def solve(self, instance: UnifiedFJSPInstance, **kwargs) -> SolutionResult:
        """使用强化学习求解"""
```

**参数**:
- `max_steps`: 最大步数 (默认: 1000)
- `algorithm`: RL算法 (默认: "random")

### UnifiedSolverManager

求解器管理器。

```python
class UnifiedSolverManager:
    def __init__(self):
        """初始化管理器"""
        
    def add_global_callback(self, callback: Callable):
        """添加全局回调函数"""
        
    def solve_parallel(
        self, 
        instance: UnifiedFJSPInstance,
        algorithms: List[str], 
        **kwargs
    ) -> Dict[str, SolutionResult]:
        """并行运行多个算法"""
        
    def get_solver(self, name: str) -> BaseSolver:
        """获取指定求解器"""
```

**示例**:
```python
manager = UnifiedSolverManager()

# 添加监控回调
def progress_callback(data):
    print(f"进度: {data}")

manager.add_global_callback(progress_callback)

# 并行求解
results = manager.solve_parallel(
    instance, 
    algorithms=['evolutionary', 'reinforcement'],
    population_size=50,
    generations=100
)
```

## 📈 可视化 API

### UnifiedVisualizer

统一可视化器。

```python
class UnifiedVisualizer:
    def __init__(self, style: str = 'plotly'):
        """初始化可视化器"""
        
    def plot_gantt_chart(
        self, 
        instance: UnifiedFJSPInstance,
        solution: SolutionResult,
        interactive: bool = True
    ) -> go.Figure:
        """绘制甘特图"""
        
    def plot_disjunctive_graph(
        self,
        instance: UnifiedFJSPInstance,
        solution: Optional[SolutionResult] = None,
        layout: str = 'spring'
    ) -> go.Figure:
        """绘制析取图"""
        
    def plot_convergence_comparison(
        self, 
        results: Dict[str, SolutionResult]
    ) -> go.Figure:
        """绘制收敛性比较"""
        
    def plot_algorithm_comparison(
        self, 
        results: Dict[str, SolutionResult]
    ) -> go.Figure:
        """绘制算法性能比较"""
        
    def create_dashboard(
        self,
        instance: UnifiedFJSPInstance,
        results: Dict[str, SolutionResult]
    ) -> go.Figure:
        """创建综合仪表板"""
```

**示例**:
```python
visualizer = UnifiedVisualizer()

# 甘特图
gantt_fig = visualizer.plot_gantt_chart(instance, result)
gantt_fig.show()

# 析取图
graph_fig = visualizer.plot_disjunctive_graph(instance, layout='hierarchical')
graph_fig.show()

# 算法比较
comparison_fig = visualizer.plot_algorithm_comparison(results)
comparison_fig.write_html("comparison.html")
```

## 🌐 Web应用 API

### StreamlitApp

Streamlit Web应用主类。

```python
class StreamlitApp:
    def __init__(self):
        """初始化应用"""
        
    def run(self):
        """运行应用"""
        
    def solve_problem(self, algorithms: List[str], params: Dict[str, Any]):
        """求解问题"""
```

## 🔧 实用工具

### 进度监控

```python
def create_progress_callback():
    """创建进度监控回调"""
    def callback(data):
        if 'generation' in data:
            print(f"代数 {data['generation']}: 最佳适应度 = {data['best_fitness']:.2f}")
        elif 'step' in data:
            print(f"步骤 {data['step']}: 奖励 = {data['reward']:.2f}")
    return callback

# 使用示例
solver.add_callback(create_progress_callback())
```

### 结果分析

```python
def analyze_results(results: Dict[str, SolutionResult]):
    """分析求解结果"""
    best_alg = min(results.keys(), key=lambda x: results[x].makespan)
    best_makespan = results[best_alg].makespan
    
    print(f"最佳算法: {best_alg}")
    print(f"最佳makespan: {best_makespan:.2f}")
    
    for alg, result in results.items():
        improvement = (result.makespan / best_makespan - 1) * 100
        print(f"{alg}: {result.makespan:.2f} (+{improvement:.1f}%)")
```

### 数据导出

```python
def export_results(results: Dict[str, SolutionResult], format: str = 'json'):
    """导出求解结果"""
    if format == 'json':
        import json
        data = {alg: {
            'makespan': result.makespan,
            'computation_time': result.computation_time,
            'iterations': result.iterations
        } for alg, result in results.items()}
        
        with open('results.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    elif format == 'csv':
        import pandas as pd
        df = pd.DataFrame([{
            'algorithm': alg,
            'makespan': result.makespan,
            'computation_time': result.computation_time,
            'iterations': result.iterations
        } for alg, result in results.items()])
        
        df.to_csv('results.csv', index=False)
```

## 🚀 快速开始示例

```python
from unified_fjsp_system import *

# 1. 生成实例
instance = InstanceGenerator.generate_random_fjsp(3, 3, 3)

# 2. 创建求解器
manager = UnifiedSolverManager()

# 3. 求解
results = manager.solve_parallel(
    instance, 
    algorithms=['evolutionary']
)

# 4. 可视化
visualizer = UnifiedVisualizer()
fig = visualizer.plot_gantt_chart(instance, list(results.values())[0])
fig.show()
```

---

**注意**: 所有API都支持类型提示，建议使用支持类型检查的IDE以获得更好的开发体验。
