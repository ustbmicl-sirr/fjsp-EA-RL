# 🎯 多目标帕累托最优扩展实现指南

## 📋 概述

本文档详细说明如何在现有FJSP系统基础上实现多目标优化和帕累托最优功能，包括算法扩展、性能指标和可视化增强。

## 🏗️ 核心扩展架构

### 1. 多目标优化管理器

```python
# unified_fjsp_system/algorithms/multi_objective_manager.py
class MultiObjectiveManager:
    def __init__(self):
        self.objectives = {}
        self.pareto_archive = ParetoArchive()
        self.performance_metrics = MultiObjectiveMetrics()
        
    def register_objective(self, name, function, weight=1.0, minimize=True):
        """注册目标函数"""
        self.objectives[name] = {
            'function': function,
            'weight': weight,
            'minimize': minimize,
            'normalization_factor': 1.0
        }
    
    def evaluate_solution(self, solution, instance):
        """评估解的所有目标值"""
        objective_values = {}
        for name, obj_info in self.objectives.items():
            value = obj_info['function'](solution, instance)
            if not obj_info['minimize']:
                value = -value  # 转换为最小化问题
            objective_values[name] = value
        return objective_values
    
    def solve_multi_objective(self, instance, algorithms, max_evaluations=10000):
        """多目标求解主流程"""
        all_solutions = []
        
        for algorithm in algorithms:
            # 为每个算法设置多目标适应度函数
            algorithm.set_fitness_function(self.scalarized_fitness)
            
            # 运行算法
            solutions = algorithm.solve(instance, max_evaluations // len(algorithms))
            all_solutions.extend(solutions)
        
        # 构建帕累托前沿
        pareto_front = self.build_pareto_front(all_solutions, instance)
        
        # 计算性能指标
        metrics = self.calculate_performance_metrics(pareto_front)
        
        return {
            'pareto_front': pareto_front,
            'metrics': metrics,
            'all_solutions': all_solutions
        }
```

### 2. 帕累托归档管理

```python
class ParetoArchive:
    def __init__(self, max_size=100):
        self.solutions = []
        self.objectives = []
        self.max_size = max_size
        
    def add_solution(self, solution, objective_values):
        """添加解到帕累托归档"""
        obj_vector = list(objective_values.values())
        
        # 检查是否被现有解支配
        dominated_indices = []
        is_dominated = False
        
        for i, existing_obj in enumerate(self.objectives):
            dominance = self._compare_objectives(obj_vector, existing_obj)
            if dominance == -1:  # 新解被支配
                is_dominated = True
                break
            elif dominance == 1:  # 新解支配现有解
                dominated_indices.append(i)
        
        if not is_dominated:
            # 移除被支配的解
            for i in sorted(dominated_indices, reverse=True):
                del self.solutions[i]
                del self.objectives[i]
            
            # 添加新解
            self.solutions.append(solution)
            self.objectives.append(obj_vector)
            
            # 如果超过最大容量，使用拥挤距离选择
            if len(self.solutions) > self.max_size:
                self._maintain_diversity()
    
    def _compare_objectives(self, obj1, obj2):
        """比较两个目标向量的支配关系"""
        better_count = 0
        worse_count = 0
        
        for v1, v2 in zip(obj1, obj2):
            if v1 < v2:
                better_count += 1
            elif v1 > v2:
                worse_count += 1
        
        if better_count > 0 and worse_count == 0:
            return 1   # obj1 支配 obj2
        elif worse_count > 0 and better_count == 0:
            return -1  # obj2 支配 obj1
        else:
            return 0   # 非支配关系
    
    def _maintain_diversity(self):
        """维护解集多样性"""
        # 计算拥挤距离
        distances = self._calculate_crowding_distances()
        
        # 移除拥挤距离最小的解
        min_distance_idx = distances.index(min(distances))
        del self.solutions[min_distance_idx]
        del self.objectives[min_distance_idx]
```

### 3. 多目标算法实现

#### NSGA-II 多目标实现
```python
class MultiObjectiveNSGAII(BaseSolver):
    def __init__(self, population_size=100, max_generations=500):
        super().__init__("MO-NSGA-II")
        self.population_size = population_size
        self.max_generations = max_generations
        self.crossover_rate = 0.9
        self.mutation_rate = 0.1
        
    def solve(self, instance, objectives=['makespan', 'flowtime', 'tardiness']):
        """多目标NSGA-II求解"""
        # 初始化种群
        population = self.initialize_population(instance)
        
        for generation in range(self.max_generations):
            # 评估目标函数
            objective_values = []
            for individual in population:
                values = self.evaluate_multiple_objectives(individual, instance, objectives)
                objective_values.append(values)
            
            # 非支配排序
            fronts = self.fast_non_dominated_sort(population, objective_values)
            
            # 计算拥挤距离
            for front in fronts:
                self.calculate_crowding_distance(front, objective_values)
            
            # 生成下一代
            new_population = []
            front_idx = 0
            
            while len(new_population) + len(fronts[front_idx]) <= self.population_size:
                new_population.extend(fronts[front_idx])
                front_idx += 1
            
            # 如果需要从最后一个前沿选择部分个体
            if len(new_population) < self.population_size:
                remaining = self.population_size - len(new_population)
                last_front = fronts[front_idx]
                
                # 按拥挤距离排序并选择
                last_front.sort(key=lambda x: x.crowding_distance, reverse=True)
                new_population.extend(last_front[:remaining])
            
            # 交叉和变异
            offspring = self.crossover_and_mutation(new_population, instance)
            population = new_population + offspring
            
            # 回调通知
            self.notify_callbacks({
                'generation': generation,
                'pareto_front_size': len(fronts[0]),
                'hypervolume': self.calculate_hypervolume(fronts[0], objective_values)
            })
        
        # 返回第一前沿作为帕累托最优解
        final_fronts = self.fast_non_dominated_sort(population, objective_values)
        return [(population[i], objective_values[i]) for i in final_fronts[0]]
```

#### 多目标粒子群优化
```python
class MultiObjectivePSO(BaseSolver):
    def __init__(self, swarm_size=50, max_iterations=300):
        super().__init__("MO-PSO")
        self.swarm_size = swarm_size
        self.max_iterations = max_iterations
        self.w = 0.5  # 惯性权重
        self.c1 = 2.0  # 个体学习因子
        self.c2 = 2.0  # 社会学习因子
        
    def solve(self, instance, objectives=['makespan', 'flowtime']):
        """多目标粒子群优化"""
        # 初始化粒子群
        particles = self.initialize_swarm(instance)
        velocities = self.initialize_velocities(instance)
        
        # 个体最优和全局最优
        personal_best = particles.copy()
        global_best_archive = ParetoArchive()
        
        for iteration in range(self.max_iterations):
            for i, particle in enumerate(particles):
                # 评估粒子
                obj_values = self.evaluate_multiple_objectives(particle, instance, objectives)
                
                # 更新个体最优
                if self.dominates(obj_values, personal_best[i].objectives):
                    personal_best[i] = particle.copy()
                    personal_best[i].objectives = obj_values
                
                # 添加到全局归档
                global_best_archive.add_solution(particle, obj_values)
                
                # 更新速度和位置
                leader = self.select_leader(global_best_archive)
                velocities[i] = self.update_velocity(velocities[i], particle, 
                                                   personal_best[i], leader)
                particles[i] = self.update_position(particle, velocities[i], instance)
            
            # 自适应参数调整
            self.w = 0.9 - 0.4 * iteration / self.max_iterations
            
            self.notify_callbacks({
                'iteration': iteration,
                'archive_size': len(global_best_archive.solutions),
                'best_makespan': min(sol.objectives[0] for sol in global_best_archive.solutions)
            })
        
        return [(sol, obj) for sol, obj in zip(global_best_archive.solutions, 
                                              global_best_archive.objectives)]
```

## 📊 性能指标实现

### 1. 超体积指标
```python
class HypervolumeIndicator:
    def __init__(self, reference_point):
        self.reference_point = reference_point
    
    def calculate(self, pareto_front):
        """计算超体积指标"""
        if len(pareto_front) == 0:
            return 0.0
        
        # 预处理：移除被参考点支配的解
        valid_points = [point for point in pareto_front 
                       if all(p < r for p, r in zip(point, self.reference_point))]
        
        if len(valid_points) == 0:
            return 0.0
        
        # 使用递归算法计算超体积
        return self._calculate_hypervolume_recursive(valid_points, len(valid_points[0]))
    
    def _calculate_hypervolume_recursive(self, points, dimension):
        """递归计算超体积"""
        if dimension == 1:
            # 一维情况：直接计算
            return max(self.reference_point[0] - min(p[0] for p in points), 0)
        
        # 多维情况：使用分治法
        points.sort(key=lambda x: x[dimension-1])
        hypervolume = 0.0
        
        for i, point in enumerate(points):
            if i == 0 or point[dimension-1] != points[i-1][dimension-1]:
                # 创建子问题
                dominated_points = [p[:dimension-1] for p in points[i:] 
                                  if all(p[j] <= point[j] for j in range(dimension-1))]
                
                if dominated_points:
                    sub_hypervolume = self._calculate_hypervolume_recursive(
                        dominated_points, dimension-1)
                    
                    height = (self.reference_point[dimension-1] - point[dimension-1])
                    hypervolume += sub_hypervolume * height
        
        return hypervolume
```

### 2. 收敛性和分布性指标
```python
class ConvergenceMetrics:
    @staticmethod
    def generational_distance(pareto_front, true_pareto_front):
        """代距离指标"""
        if not pareto_front or not true_pareto_front:
            return float('inf')
        
        total_distance = 0.0
        for point in pareto_front:
            min_distance = min(
                sum((p1 - p2) ** 2 for p1, p2 in zip(point, true_point)) ** 0.5
                for true_point in true_pareto_front
            )
            total_distance += min_distance
        
        return total_distance / len(pareto_front)
    
    @staticmethod
    def inverted_generational_distance(pareto_front, true_pareto_front):
        """反向代距离指标"""
        return ConvergenceMetrics.generational_distance(true_pareto_front, pareto_front)
    
    @staticmethod
    def spacing_metric(pareto_front):
        """间距指标"""
        if len(pareto_front) < 2:
            return 0.0
        
        distances = []
        for i, point1 in enumerate(pareto_front):
            min_dist = float('inf')
            for j, point2 in enumerate(pareto_front):
                if i != j:
                    dist = sum((p1 - p2) ** 2 for p1, p2 in zip(point1, point2)) ** 0.5
                    min_dist = min(min_dist, dist)
            distances.append(min_dist)
        
        mean_distance = sum(distances) / len(distances)
        variance = sum((d - mean_distance) ** 2 for d in distances) / len(distances)
        
        return variance ** 0.5
```

## 🎨 多目标可视化扩展

### 1. 帕累托前沿可视化
```python
# unified_fjsp_system/visualization/multi_objective_visualizer.py
class MultiObjectiveVisualizer(UnifiedVisualizer):
    def plot_pareto_front_2d(self, pareto_front, objective_names, title="帕累托前沿"):
        """2D帕累托前沿可视化"""
        fig = go.Figure()
        
        if pareto_front:
            x_values = [sol[1][0] for sol in pareto_front]
            y_values = [sol[1][1] for sol in pareto_front]
            
            # 添加帕累托前沿点
            fig.add_trace(go.Scatter(
                x=x_values, y=y_values,
                mode='markers+lines',
                name='帕累托前沿',
                marker=dict(size=10, color='red', symbol='circle'),
                line=dict(color='red', width=2)
            ))
            
            # 添加理想点
            ideal_point = [min(x_values), min(y_values)]
            fig.add_trace(go.Scatter(
                x=[ideal_point[0]], y=[ideal_point[1]],
                mode='markers',
                name='理想点',
                marker=dict(size=15, color='green', symbol='star')
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=objective_names[0],
            yaxis_title=objective_names[1],
            showlegend=True,
            hovermode='closest'
        )
        
        return fig
    
    def plot_pareto_front_3d(self, pareto_front, objective_names):
        """3D帕累托前沿可视化"""
        fig = go.Figure()
        
        if pareto_front and len(objective_names) >= 3:
            x_values = [sol[1][0] for sol in pareto_front]
            y_values = [sol[1][1] for sol in pareto_front]
            z_values = [sol[1][2] for sol in pareto_front]
            
            fig.add_trace(go.Scatter3d(
                x=x_values, y=y_values, z=z_values,
                mode='markers',
                name='帕累托前沿',
                marker=dict(size=8, color='blue', opacity=0.8)
            ))
        
        fig.update_layout(
            title='3D帕累托前沿',
            scene=dict(
                xaxis_title=objective_names[0],
                yaxis_title=objective_names[1],
                zaxis_title=objective_names[2]
            )
        )
        
        return fig
    
    def plot_objective_space_evolution(self, evolution_data):
        """目标空间演化动画"""
        frames = []
        
        for generation, front in evolution_data.items():
            x_values = [sol[1][0] for sol in front]
            y_values = [sol[1][1] for sol in front]
            
            frame = go.Frame(
                data=[go.Scatter(x=x_values, y=y_values, mode='markers',
                               marker=dict(size=8, color='red'))],
                name=str(generation)
            )
            frames.append(frame)
        
        fig = go.Figure(
            data=[go.Scatter(x=[], y=[], mode='markers')],
            frames=frames
        )
        
        fig.update_layout(
            title="帕累托前沿演化过程",
            updatemenus=[{
                "buttons": [
                    {"args": [None, {"frame": {"duration": 500}}], 
                     "label": "播放", "method": "animate"},
                    {"args": [[None], {"frame": {"duration": 0}, "mode": "immediate"}], 
                     "label": "暂停", "method": "animate"}
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }]
        )
        
        return fig
```

## 🚀 使用示例

### 1. 基本多目标优化
```python
# 创建多目标管理器
mo_manager = MultiObjectiveManager()

# 注册目标函数
mo_manager.register_objective('makespan', ObjectiveFunctions.makespan, minimize=True)
mo_manager.register_objective('flowtime', ObjectiveFunctions.total_flowtime, minimize=True)
mo_manager.register_objective('energy', ObjectiveFunctions.energy_consumption, minimize=True)

# 创建算法
algorithms = [
    MultiObjectiveNSGAII(population_size=100, max_generations=300),
    MultiObjectivePSO(swarm_size=50, max_iterations=200)
]

# 求解
result = mo_manager.solve_multi_objective(instance, algorithms)

# 可视化结果
visualizer = MultiObjectiveVisualizer()
fig = visualizer.plot_pareto_front_2d(
    result['pareto_front'], 
    ['完工时间', '流程时间']
)
fig.show()
```

### 2. 交互式多目标优化
```python
# 设置用户偏好
preferences = {
    'makespan': {'weight': 0.5, 'aspiration': 100},
    'flowtime': {'weight': 0.3, 'aspiration': 500},
    'energy': {'weight': 0.2, 'aspiration': 1000}
}

# 交互式求解
interactive_optimizer = InteractiveMultiObjective(mo_manager)
interactive_optimizer.set_user_preferences(preferences)
refined_front = interactive_optimizer.interactive_solve(instance)
```

---

**文档版本**: v1.0.0  
**最后更新**: 2025年10月7日
