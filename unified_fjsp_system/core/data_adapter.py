"""
统一数据适配器 - 融合JobShopLib, Schlably, Graph-JSP-Env的数据格式
"""
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import networkx as nx

try:
    from job_shop_lib import JobShopInstance, Operation as JSLOperation
    HAS_JOBSHOPLIB = True
except ImportError:
    HAS_JOBSHOPLIB = False

try:
    from graph_jsp_env.disjunctive_graph_jsp_env import DisjunctiveGraphJspEnv
    HAS_GRAPH_JSP = True
except ImportError:
    HAS_GRAPH_JSP = False


@dataclass
class UnifiedOperation:
    """统一的工序表示"""
    job_id: int
    operation_id: int
    machines: List[int]  # 可选机器列表
    processing_times: List[int]  # 对应的加工时间
    setup_time: int = 0
    due_date: Optional[int] = None
    release_time: int = 0


@dataclass
class UnifiedFJSPInstance:
    """统一的FJSP实例表示"""
    name: str
    num_jobs: int
    num_machines: int
    operations: List[UnifiedOperation]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DataAdapter:
    """数据格式转换适配器"""
    
    @staticmethod
    def from_jobshoplib(instance) -> UnifiedFJSPInstance:
        """从JobShopLib格式转换"""
        if not HAS_JOBSHOPLIB:
            raise ImportError("JobShopLib not installed")
            
        operations = []
        for job_id, job in enumerate(instance.jobs):
            for op_id, operation in enumerate(job):
                # JobShopLib的Operation可能只有单个机器
                machines = [operation.machines] if isinstance(operation.machines, int) else operation.machines
                times = [operation.duration] if isinstance(operation.duration, int) else operation.duration
                
                unified_op = UnifiedOperation(
                    job_id=job_id,
                    operation_id=op_id,
                    machines=machines,
                    processing_times=times
                )
                operations.append(unified_op)
        
        return UnifiedFJSPInstance(
            name=getattr(instance, 'name', 'unnamed'),
            num_jobs=len(instance.jobs),
            num_machines=instance.num_machines,
            operations=operations,
            metadata=getattr(instance, 'metadata', {})
        )
    
    @staticmethod
    def to_jobshoplib(instance: UnifiedFJSPInstance):
        """转换为JobShopLib格式"""
        if not HAS_JOBSHOPLIB:
            raise ImportError("JobShopLib not installed")
            
        jobs = [[] for _ in range(instance.num_jobs)]
        
        for op in instance.operations:
            # 如果有多个机器选择，取第一个作为默认
            machine = op.machines[0] if op.machines else 0
            duration = op.processing_times[0] if op.processing_times else 1
            
            jsl_op = JSLOperation(machines=machine, duration=duration)
            jobs[op.job_id].append(jsl_op)
        
        return JobShopInstance(jobs, name=instance.name, **instance.metadata)
    
    @staticmethod
    def to_graph_jsp_env(instance: UnifiedFJSPInstance) -> np.ndarray:
        """转换为Graph-JSP-Env格式"""
        if not HAS_GRAPH_JSP:
            raise ImportError("graph-jsp-env not installed")
            
        # 构建Graph-JSP-Env需要的numpy数组格式
        # [machines, processing_times] for each job
        max_ops = max(len([op for op in instance.operations if op.job_id == j]) 
                     for j in range(instance.num_jobs))
        
        machines_array = np.zeros((instance.num_jobs, max_ops), dtype=int)
        times_array = np.zeros((instance.num_jobs, max_ops), dtype=int)
        
        for op in instance.operations:
            if op.job_id < instance.num_jobs and op.operation_id < max_ops:
                # 取第一个可选机器和对应时间
                machines_array[op.job_id, op.operation_id] = op.machines[0] if op.machines else 0
                times_array[op.job_id, op.operation_id] = op.processing_times[0] if op.processing_times else 1
        
        return np.array([machines_array, times_array])
    
    @staticmethod
    def to_schlably_format(instance: UnifiedFJSPInstance) -> Dict[str, Any]:
        """转换为Schlably格式"""
        # Schlably使用类似的数据结构，但可能需要特定的任务表示
        tasks = []
        
        for op in instance.operations:
            task = {
                'job_id': op.job_id,
                'operation_id': op.operation_id,
                'machines': op.machines,
                'processing_times': op.processing_times,
                'setup_time': op.setup_time,
                'due_date': op.due_date,
                'release_time': op.release_time
            }
            tasks.append(task)
        
        return {
            'name': instance.name,
            'num_jobs': instance.num_jobs,
            'num_machines': instance.num_machines,
            'tasks': tasks,
            'metadata': instance.metadata
        }
    
    @staticmethod
    def build_disjunctive_graph(instance: UnifiedFJSPInstance) -> nx.DiGraph:
        """构建析取图"""
        G = nx.DiGraph()
        
        # 添加源点和汇点
        source = 'SOURCE'
        sink = 'SINK'
        G.add_node(source, node_type='source')
        G.add_node(sink, node_type='sink')
        
        # 为每个工序创建节点
        operation_nodes = {}
        for op in instance.operations:
            node_id = f"J{op.job_id}_O{op.operation_id}"
            operation_nodes[(op.job_id, op.operation_id)] = node_id
            
            G.add_node(node_id, 
                      node_type='operation',
                      job_id=op.job_id,
                      operation_id=op.operation_id,
                      machines=op.machines,
                      processing_times=op.processing_times,
                      setup_time=op.setup_time)
        
        # 添加合取边（同一作业内的工序顺序）
        job_operations = {}
        for op in instance.operations:
            if op.job_id not in job_operations:
                job_operations[op.job_id] = []
            job_operations[op.job_id].append(op)
        
        for job_id, ops in job_operations.items():
            # 按operation_id排序
            ops.sort(key=lambda x: x.operation_id)
            
            # 连接源点到第一个工序
            if ops:
                first_node = operation_nodes[(job_id, ops[0].operation_id)]
                G.add_edge(source, first_node, edge_type='conjunctive')
            
            # 连接工序间的合取边
            for i in range(len(ops) - 1):
                current_node = operation_nodes[(job_id, ops[i].operation_id)]
                next_node = operation_nodes[(job_id, ops[i+1].operation_id)]
                G.add_edge(current_node, next_node, edge_type='conjunctive')
            
            # 连接最后一个工序到汇点
            if ops:
                last_node = operation_nodes[(job_id, ops[-1].operation_id)]
                G.add_edge(last_node, sink, edge_type='conjunctive')
        
        # 添加析取边（同一机器上的不同作业工序）
        machine_operations = {}
        for op in instance.operations:
            for machine in op.machines:
                if machine not in machine_operations:
                    machine_operations[machine] = []
                machine_operations[machine].append(op)
        
        for machine, ops in machine_operations.items():
            # 为同一机器上的所有工序添加析取边
            for i in range(len(ops)):
                for j in range(i + 1, len(ops)):
                    if ops[i].job_id != ops[j].job_id:  # 不同作业
                        node1 = operation_nodes[(ops[i].job_id, ops[i].operation_id)]
                        node2 = operation_nodes[(ops[j].job_id, ops[j].operation_id)]
                        
                        # 添加双向析取边
                        G.add_edge(node1, node2, edge_type='disjunctive', machine=machine)
                        G.add_edge(node2, node1, edge_type='disjunctive', machine=machine)
        
        return G


class InstanceGenerator:
    """统一的实例生成器"""
    
    @staticmethod
    def generate_random_fjsp(num_jobs: int, num_machines: int, 
                           max_operations_per_job: int = 5,
                           min_processing_time: int = 1,
                           max_processing_time: int = 10,
                           flexibility: float = 0.5) -> UnifiedFJSPInstance:
        """生成随机FJSP实例"""
        operations = []
        
        for job_id in range(num_jobs):
            num_operations = np.random.randint(1, max_operations_per_job + 1)
            
            for op_id in range(num_operations):
                # 根据灵活性确定可选机器数量
                num_available_machines = max(1, int(num_machines * flexibility))
                available_machines = np.random.choice(
                    num_machines, 
                    size=num_available_machines, 
                    replace=False
                ).tolist()
                
                # 为每台可选机器生成加工时间
                processing_times = [
                    np.random.randint(min_processing_time, max_processing_time + 1)
                    for _ in available_machines
                ]
                
                operation = UnifiedOperation(
                    job_id=job_id,
                    operation_id=op_id,
                    machines=available_machines,
                    processing_times=processing_times
                )
                operations.append(operation)
        
        return UnifiedFJSPInstance(
            name=f"Random_FJSP_{num_jobs}x{num_machines}",
            num_jobs=num_jobs,
            num_machines=num_machines,
            operations=operations,
            metadata={
                'generated': True,
                'flexibility': flexibility,
                'max_operations_per_job': max_operations_per_job
            }
        )


# 使用示例
if __name__ == "__main__":
    # 生成随机实例
    instance = InstanceGenerator.generate_random_fjsp(3, 3, 3)
    print(f"Generated instance: {instance.name}")
    print(f"Operations: {len(instance.operations)}")
    
    # 构建析取图
    graph = DataAdapter.build_disjunctive_graph(instance)
    print(f"Graph nodes: {graph.number_of_nodes()}")
    print(f"Graph edges: {graph.number_of_edges()}")
