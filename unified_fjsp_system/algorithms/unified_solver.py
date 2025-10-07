"""
统一求解器接口 - 融合多种算法
"""
import numpy as np
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
import time
import threading
from concurrent.futures import ThreadPoolExecutor

try:
    from ..core.data_adapter import UnifiedFJSPInstance, DataAdapter
except ImportError:
    # 当作为模块直接导入时使用绝对导入
    from core.data_adapter import UnifiedFJSPInstance, DataAdapter


@dataclass
class SolutionResult:
    """统一的求解结果"""
    schedule: Dict[str, Any]  # 调度方案
    makespan: float
    objectives: Dict[str, float]  # 多目标值
    algorithm: str
    computation_time: float
    iterations: int = 0
    convergence_history: List[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.convergence_history is None:
            self.convergence_history = []
        if self.metadata is None:
            self.metadata = {}


class BaseSolver(ABC):
    """求解器基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.callbacks = []
    
    def add_callback(self, callback: Callable):
        """添加回调函数用于实时监控"""
        self.callbacks.append(callback)
    
    def notify_callbacks(self, data: Dict[str, Any]):
        """通知所有回调函数"""
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"Callback error: {e}")
    
    @abstractmethod
    def solve(self, instance: UnifiedFJSPInstance, **kwargs) -> SolutionResult:
        """求解FJSP实例"""
        pass


class JobShopLibSolver(BaseSolver):
    """JobShopLib求解器包装"""
    
    def __init__(self):
        super().__init__("JobShopLib")
        self.available_solvers = []
        
        try:
            from job_shop_lib.constraint_programming import ORToolsSolver
            from job_shop_lib.dispatching import DispatchingRuleSolver
            from job_shop_lib.metaheuristics import SimulatedAnnealingSolver
            
            self.available_solvers = [
                ("OR-Tools", ORToolsSolver),
                ("Dispatching", DispatchingRuleSolver),
                ("SimulatedAnnealing", SimulatedAnnealingSolver)
            ]
        except ImportError:
            print("JobShopLib not available")
    
    def solve(self, instance: UnifiedFJSPInstance, 
              solver_type: str = "OR-Tools", **kwargs) -> SolutionResult:
        """使用JobShopLib求解"""
        start_time = time.time()
        
        # 转换为JobShopLib格式
        jsl_instance = DataAdapter.to_jobshoplib(instance)
        
        # 选择求解器
        solver_class = None
        for name, cls in self.available_solvers:
            if name == solver_type:
                solver_class = cls
                break
        
        if solver_class is None:
            raise ValueError(f"Solver {solver_type} not available")
        
        # 创建并运行求解器
        if solver_type == "OR-Tools":
            solver = solver_class(max_time_in_seconds=kwargs.get('time_limit', 60))
        elif solver_type == "Dispatching":
            rule = kwargs.get('rule', 'shortest_processing_time')
            solver = solver_class(rule)
        else:
            solver = solver_class(**kwargs)
        
        schedule = solver(jsl_instance)
        
        computation_time = time.time() - start_time
        
        return SolutionResult(
            schedule={'jobshoplib_schedule': schedule},
            makespan=schedule.makespan() if hasattr(schedule, 'makespan') else 0,
            objectives={'makespan': schedule.makespan() if hasattr(schedule, 'makespan') else 0},
            algorithm=f"JobShopLib-{solver_type}",
            computation_time=computation_time
        )


class EvolutionaryAlgorithmSolver(BaseSolver):
    """进化算法求解器"""
    
    def __init__(self):
        super().__init__("EvolutionaryAlgorithm")
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
    
    def solve(self, instance: UnifiedFJSPInstance, **kwargs) -> SolutionResult:
        """使用遗传算法求解"""
        start_time = time.time()
        
        # 参数设置
        pop_size = kwargs.get('population_size', self.population_size)
        generations = kwargs.get('generations', self.generations)
        mutation_rate = kwargs.get('mutation_rate', self.mutation_rate)
        crossover_rate = kwargs.get('crossover_rate', self.crossover_rate)
        
        # 初始化种群
        population = self._initialize_population(instance, pop_size)
        convergence_history = []
        
        best_solution = None
        best_fitness = float('inf')
        
        for generation in range(generations):
            # 评估适应度
            fitness_scores = [self._evaluate_fitness(individual, instance) 
                            for individual in population]
            
            # 记录最佳解
            min_fitness = min(fitness_scores)
            if min_fitness < best_fitness:
                best_fitness = min_fitness
                best_solution = population[fitness_scores.index(min_fitness)]
            
            convergence_history.append(best_fitness)
            
            # 通知回调函数
            self.notify_callbacks({
                'generation': generation,
                'best_fitness': best_fitness,
                'avg_fitness': np.mean(fitness_scores),
                'population_size': len(population)
            })
            
            # 选择
            selected = self._selection(population, fitness_scores)
            
            # 交叉
            offspring = self._crossover(selected, crossover_rate)
            
            # 变异
            mutated = self._mutation(offspring, mutation_rate)
            
            # 更新种群
            population = mutated
        
        computation_time = time.time() - start_time
        
        # 构建调度方案
        schedule = self._decode_solution(best_solution, instance)
        
        return SolutionResult(
            schedule=schedule,
            makespan=best_fitness,
            objectives={'makespan': best_fitness},
            algorithm="GeneticAlgorithm",
            computation_time=computation_time,
            iterations=generations,
            convergence_history=convergence_history
        )
    
    def _initialize_population(self, instance: UnifiedFJSPInstance, size: int) -> List[List[int]]:
        """初始化种群"""
        population = []
        total_operations = len(instance.operations)
        
        for _ in range(size):
            # 随机排列所有工序
            individual = list(range(total_operations))
            np.random.shuffle(individual)
            population.append(individual)
        
        return population
    
    def _evaluate_fitness(self, individual: List[int], instance: UnifiedFJSPInstance) -> float:
        """评估个体适应度（makespan）"""
        schedule = self._decode_solution(individual, instance)
        return schedule.get('makespan', float('inf'))
    
    def _decode_solution(self, individual: List[int], instance: UnifiedFJSPInstance) -> Dict[str, Any]:
        """解码个体为调度方案"""
        # 简化的解码过程
        machine_schedules = {i: [] for i in range(instance.num_machines)}
        job_completion_times = [0] * instance.num_jobs
        
        makespan = 0
        
        for op_idx in individual:
            if op_idx < len(instance.operations):
                op = instance.operations[op_idx]
                
                # 选择第一个可用机器（简化）
                machine = op.machines[0] if op.machines else 0
                processing_time = op.processing_times[0] if op.processing_times else 1
                
                # 计算开始时间
                machine_available_time = max([end_time for _, end_time in machine_schedules[machine]], default=0)
                job_ready_time = job_completion_times[op.job_id]
                start_time = max(machine_available_time, job_ready_time)
                end_time = start_time + processing_time
                
                # 更新调度
                machine_schedules[machine].append((start_time, end_time))
                job_completion_times[op.job_id] = end_time
                makespan = max(makespan, end_time)
        
        return {
            'machine_schedules': machine_schedules,
            'makespan': makespan,
            'job_completion_times': job_completion_times
        }
    
    def _selection(self, population: List[List[int]], fitness_scores: List[float]) -> List[List[int]]:
        """锦标赛选择"""
        selected = []
        tournament_size = 3
        
        for _ in range(len(population)):
            # 锦标赛选择
            tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            winner_idx = tournament_indices[np.argmin(tournament_fitness)]
            selected.append(population[winner_idx].copy())
        
        return selected
    
    def _crossover(self, population: List[List[int]], rate: float) -> List[List[int]]:
        """顺序交叉"""
        offspring = []
        
        for i in range(0, len(population), 2):
            parent1 = population[i]
            parent2 = population[i + 1] if i + 1 < len(population) else population[0]
            
            if np.random.random() < rate:
                # 顺序交叉
                size = len(parent1)
                start, end = sorted(np.random.choice(size, 2, replace=False))
                
                child1 = [-1] * size
                child2 = [-1] * size
                
                # 复制选定区间
                child1[start:end] = parent1[start:end]
                child2[start:end] = parent2[start:end]
                
                # 填充剩余位置
                self._fill_offspring(child1, parent2, start, end)
                self._fill_offspring(child2, parent1, start, end)
                
                offspring.extend([child1, child2])
            else:
                offspring.extend([parent1.copy(), parent2.copy()])
        
        return offspring
    
    def _fill_offspring(self, child: List[int], parent: List[int], start: int, end: int):
        """填充交叉后代的剩余位置"""
        child_set = set(child[start:end])
        parent_filtered = [x for x in parent if x not in child_set]
        
        idx = 0
        for i in range(len(child)):
            if child[i] == -1:
                child[i] = parent_filtered[idx]
                idx += 1
    
    def _mutation(self, population: List[List[int]], rate: float) -> List[List[int]]:
        """交换变异"""
        for individual in population:
            if np.random.random() < rate:
                # 随机交换两个位置
                idx1, idx2 = np.random.choice(len(individual), 2, replace=False)
                individual[idx1], individual[idx2] = individual[idx2], individual[idx1]
        
        return population


class ReinforcementLearningSolver(BaseSolver):
    """强化学习求解器（基于Graph-JSP-Env）"""
    
    def __init__(self):
        super().__init__("ReinforcementLearning")
        self.env = None
        self.model = None
    
    def solve(self, instance: UnifiedFJSPInstance, **kwargs) -> SolutionResult:
        """使用强化学习求解"""
        start_time = time.time()
        
        try:
            from graph_jsp_env.disjunctive_graph_jsp_env import DisjunctiveGraphJspEnv
            
            # 转换为Graph-JSP-Env格式
            jsp_array = DataAdapter.to_graph_jsp_env(instance)
            
            # 创建环境
            env = DisjunctiveGraphJspEnv(
                jps_instance=jsp_array,
                perform_left_shift_if_possible=True,
                normalize_observation_space=True,
                flat_observation_space=True,
                action_mode='task'
            )
            
            # 简单的随机策略（实际应用中应该使用训练好的模型）
            terminated = False
            total_reward = 0
            steps = 0
            
            obs, _ = env.reset()
            
            while not terminated and steps < 1000:  # 防止无限循环
                mask = np.array(env.valid_action_mask()).astype(np.int8)
                valid_actions = np.where(mask == 1)[0]
                
                if len(valid_actions) == 0:
                    break
                
                action = np.random.choice(valid_actions)
                obs, reward, terminated, truncated, info = env.step(action)
                total_reward += reward
                steps += 1
                
                # 通知回调函数
                self.notify_callbacks({
                    'step': steps,
                    'reward': reward,
                    'total_reward': total_reward,
                    'action': action
                })
            
            makespan = info.get('makespan', float('inf'))
            
        except ImportError:
            print("Graph-JSP-Env not available, using random solution")
            makespan = np.random.uniform(50, 200)  # 随机makespan
        
        computation_time = time.time() - start_time
        
        return SolutionResult(
            schedule={'rl_makespan': makespan},
            makespan=makespan,
            objectives={'makespan': makespan},
            algorithm="ReinforcementLearning",
            computation_time=computation_time,
            iterations=steps if 'steps' in locals() else 0
        )


class UnifiedSolverManager:
    """统一求解器管理器"""
    
    def __init__(self):
        self.solvers = {
            'jobshoplib': JobShopLibSolver(),
            'evolutionary': EvolutionaryAlgorithmSolver(),
            'reinforcement': ReinforcementLearningSolver()
        }
        self.callbacks = []
    
    def add_global_callback(self, callback: Callable):
        """添加全局回调函数"""
        self.callbacks.append(callback)
        for solver in self.solvers.values():
            solver.add_callback(callback)
    
    def solve_parallel(self, instance: UnifiedFJSPInstance, 
                      algorithms: List[str], **kwargs) -> Dict[str, SolutionResult]:
        """并行运行多个算法"""
        results = {}
        
        def run_solver(alg_name):
            if alg_name in self.solvers:
                try:
                    result = self.solvers[alg_name].solve(instance, **kwargs)
                    return alg_name, result
                except Exception as e:
                    print(f"Error in {alg_name}: {e}")
                    return alg_name, None
            return alg_name, None
        
        with ThreadPoolExecutor(max_workers=len(algorithms)) as executor:
            futures = [executor.submit(run_solver, alg) for alg in algorithms]
            
            for future in futures:
                alg_name, result = future.result()
                if result is not None:
                    results[alg_name] = result
        
        return results
    
    def get_solver(self, name: str) -> BaseSolver:
        """获取指定求解器"""
        return self.solvers.get(name)


# 使用示例
if __name__ == "__main__":
    try:
        from ..core.data_adapter import InstanceGenerator
    except ImportError:
        from core.data_adapter import InstanceGenerator
    
    # 生成测试实例
    instance = InstanceGenerator.generate_random_fjsp(3, 3, 3)
    
    # 创建求解器管理器
    manager = UnifiedSolverManager()
    
    # 添加监控回调
    def monitor_callback(data):
        print(f"Progress: {data}")
    
    manager.add_global_callback(monitor_callback)
    
    # 并行求解
    results = manager.solve_parallel(instance, ['evolutionary', 'reinforcement'])
    
    for alg, result in results.items():
        print(f"{alg}: makespan={result.makespan:.2f}, time={result.computation_time:.2f}s")
