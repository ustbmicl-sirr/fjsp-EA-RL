"""
统一可视化模块 - 融合多种可视化方式
"""
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from datetime import datetime, timedelta

try:
    from ..core.data_adapter import UnifiedFJSPInstance, DataAdapter
    from ..algorithms.unified_solver import SolutionResult
except ImportError:
    # 当作为模块直接导入时使用绝对导入
    from core.data_adapter import UnifiedFJSPInstance, DataAdapter
    from algorithms.unified_solver import SolutionResult


class UnifiedVisualizer:
    """统一可视化器"""
    
    def __init__(self, style: str = 'plotly'):
        self.style = style  # 'plotly', 'matplotlib', 'both'
        self.color_palette = px.colors.qualitative.Set3
        
    def plot_gantt_chart(self, instance: UnifiedFJSPInstance, 
                        solution: SolutionResult,
                        interactive: bool = True) -> go.Figure:
        """绘制甘特图"""
        if interactive and self.style in ['plotly', 'both']:
            return self._plot_gantt_plotly(instance, solution)
        else:
            return self._plot_gantt_matplotlib(instance, solution)
    
    def _plot_gantt_plotly(self, instance: UnifiedFJSPInstance, 
                          solution: SolutionResult) -> go.Figure:
        """使用Plotly绘制交互式甘特图"""
        fig = go.Figure()
        
        # 解析调度方案
        schedule_data = self._extract_schedule_data(instance, solution)
        
        # 为每个作业分配颜色
        job_colors = {i: self.color_palette[i % len(self.color_palette)] 
                     for i in range(instance.num_jobs)}
        
        # 添加甘特条
        for machine_id in range(instance.num_machines):
            machine_tasks = [task for task in schedule_data 
                           if task['machine'] == machine_id]
            
            for task in machine_tasks:
                fig.add_trace(go.Scatter(
                    x=[task['start'], task['end'], task['end'], task['start'], task['start']],
                    y=[machine_id-0.4, machine_id-0.4, machine_id+0.4, machine_id+0.4, machine_id-0.4],
                    fill='toself',
                    fillcolor=job_colors[task['job_id']],
                    line=dict(color='black', width=1),
                    mode='lines',
                    name=f"Job {task['job_id']}",
                    text=f"J{task['job_id']}_O{task['operation_id']}<br>"
                         f"Duration: {task['duration']}<br>"
                         f"Start: {task['start']}<br>"
                         f"End: {task['end']}",
                    hoverinfo='text',
                    showlegend=machine_id == 0  # 只在第一个机器显示图例
                ))
        
        # 更新布局
        fig.update_layout(
            title=f"FJSP Gantt Chart - {instance.name}<br>"
                  f"Algorithm: {solution.algorithm}, Makespan: {solution.makespan:.2f}",
            xaxis_title="Time",
            yaxis_title="Machine",
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(instance.num_machines)),
                ticktext=[f"Machine {i}" for i in range(instance.num_machines)]
            ),
            height=max(400, instance.num_machines * 60),
            hovermode='closest'
        )
        
        return fig
    
    def _plot_gantt_matplotlib(self, instance: UnifiedFJSPInstance, 
                              solution: SolutionResult) -> plt.Figure:
        """使用Matplotlib绘制甘特图"""
        fig, ax = plt.subplots(figsize=(12, max(6, instance.num_machines * 0.8)))
        
        # 解析调度方案
        schedule_data = self._extract_schedule_data(instance, solution)
        
        # 为每个作业分配颜色
        colors = plt.cm.Set3(np.linspace(0, 1, instance.num_jobs))
        
        # 绘制甘特条
        for task in schedule_data:
            ax.barh(task['machine'], task['duration'], 
                   left=task['start'], height=0.6,
                   color=colors[task['job_id']], 
                   alpha=0.8, edgecolor='black')
            
            # 添加文本标签
            ax.text(task['start'] + task['duration']/2, task['machine'],
                   f"J{task['job_id']}_O{task['operation_id']}", 
                   ha='center', va='center', fontsize=8)
        
        # 设置坐标轴
        ax.set_xlabel('Time')
        ax.set_ylabel('Machine')
        ax.set_yticks(range(instance.num_machines))
        ax.set_yticklabels([f'Machine {i}' for i in range(instance.num_machines)])
        ax.set_title(f'FJSP Gantt Chart - {instance.name}\n'
                    f'Algorithm: {solution.algorithm}, Makespan: {solution.makespan:.2f}')
        
        # 添加图例
        legend_elements = [plt.Rectangle((0,0),1,1, facecolor=colors[i], 
                                       label=f'Job {i}') 
                          for i in range(instance.num_jobs)]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        return fig
    
    def plot_disjunctive_graph(self, instance: UnifiedFJSPInstance,
                              solution: Optional[SolutionResult] = None,
                              layout: str = 'spring') -> go.Figure:
        """绘制析取图"""
        G = DataAdapter.build_disjunctive_graph(instance)
        
        # 选择布局
        if layout == 'spring':
            pos = nx.spring_layout(G, k=3, iterations=50)
        elif layout == 'hierarchical':
            pos = self._hierarchical_layout(G, instance)
        else:
            pos = nx.random_layout(G)
        
        # 创建Plotly图
        fig = go.Figure()
        
        # 绘制边
        edge_trace = []
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_type = edge[2].get('edge_type', 'unknown')
            color = 'blue' if edge_type == 'conjunctive' else 'red'
            width = 2 if edge_type == 'conjunctive' else 1
            dash = 'solid' if edge_type == 'conjunctive' else 'dash'
            
            fig.add_trace(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode='lines',
                line=dict(color=color, width=width, dash=dash),
                showlegend=False,
                hoverinfo='none'
            ))
        
        # 绘制节点
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        node_sizes = []
        
        for node in G.nodes(data=True):
            x, y = pos[node[0]]
            node_x.append(x)
            node_y.append(y)
            
            node_type = node[1].get('node_type', 'operation')
            if node_type == 'source':
                node_text.append('SOURCE')
                node_colors.append('green')
                node_sizes.append(20)
            elif node_type == 'sink':
                node_text.append('SINK')
                node_colors.append('red')
                node_sizes.append(20)
            else:
                job_id = node[1].get('job_id', 0)
                op_id = node[1].get('operation_id', 0)
                node_text.append(f'J{job_id}_O{op_id}')
                node_colors.append(self.color_palette[job_id % len(self.color_palette)])
                node_sizes.append(15)
        
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(size=node_sizes, color=node_colors, line=dict(width=2, color='black')),
            text=node_text,
            textposition="middle center",
            textfont=dict(size=10),
            hoverinfo='text',
            name='Operations'
        ))
        
        # 更新布局
        fig.update_layout(
            title=f"Disjunctive Graph - {instance.name}",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Blue edges: Conjunctive (job sequence)<br>Red edges: Disjunctive (machine conflicts)",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        return fig
    
    def plot_convergence_comparison(self, results: Dict[str, SolutionResult]) -> go.Figure:
        """绘制算法收敛性比较"""
        fig = go.Figure()
        
        for alg_name, result in results.items():
            if result.convergence_history:
                fig.add_trace(go.Scatter(
                    x=list(range(len(result.convergence_history))),
                    y=result.convergence_history,
                    mode='lines+markers',
                    name=f"{alg_name} (Final: {result.makespan:.2f})",
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            title="Algorithm Convergence Comparison",
            xaxis_title="Iteration/Generation",
            yaxis_title="Makespan",
            hovermode='x unified'
        )
        
        return fig
    
    def plot_algorithm_comparison(self, results: Dict[str, SolutionResult]) -> go.Figure:
        """绘制算法性能比较"""
        algorithms = list(results.keys())
        makespans = [results[alg].makespan for alg in algorithms]
        times = [results[alg].computation_time for alg in algorithms]
        
        # 创建子图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Makespan Comparison', 'Computation Time Comparison'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Makespan比较
        fig.add_trace(
            go.Bar(x=algorithms, y=makespans, name='Makespan',
                  marker_color='lightblue'),
            row=1, col=1
        )
        
        # 计算时间比较
        fig.add_trace(
            go.Bar(x=algorithms, y=times, name='Time (s)',
                  marker_color='lightcoral'),
            row=1, col=2
        )
        
        fig.update_layout(
            title="Algorithm Performance Comparison",
            showlegend=False,
            height=400
        )
        
        return fig
    
    def create_dashboard(self, instance: UnifiedFJSPInstance,
                        results: Dict[str, SolutionResult]) -> go.Figure:
        """创建综合仪表板"""
        # 选择最佳解
        best_alg = min(results.keys(), key=lambda x: results[x].makespan)
        best_solution = results[best_alg]
        
        # 创建子图布局
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                f'Best Solution Gantt Chart ({best_alg})',
                'Algorithm Comparison',
                'Convergence History',
                'Solution Statistics'
            ),
            specs=[
                [{"colspan": 2}, None],
                [{"type": "bar"}, {"type": "table"}]
            ],
            vertical_spacing=0.12
        )
        
        # 1. 甘特图（简化版）
        schedule_data = self._extract_schedule_data(instance, best_solution)
        job_colors = {i: self.color_palette[i % len(self.color_palette)] 
                     for i in range(instance.num_jobs)}
        
        for task in schedule_data:
            fig.add_trace(
                go.Scatter(
                    x=[task['start'], task['end'], task['end'], task['start'], task['start']],
                    y=[task['machine']-0.4, task['machine']-0.4, 
                       task['machine']+0.4, task['machine']+0.4, task['machine']-0.4],
                    fill='toself',
                    fillcolor=job_colors[task['job_id']],
                    line=dict(color='black', width=1),
                    mode='lines',
                    showlegend=False,
                    name=f"J{task['job_id']}"
                ),
                row=1, col=1
            )
        
        # 2. 算法比较
        algorithms = list(results.keys())
        makespans = [results[alg].makespan for alg in algorithms]
        
        fig.add_trace(
            go.Bar(x=algorithms, y=makespans, name='Makespan',
                  marker_color='lightblue', showlegend=False),
            row=2, col=1
        )
        
        # 3. 统计表格
        stats_data = []
        for alg, result in results.items():
            stats_data.append([
                alg,
                f"{result.makespan:.2f}",
                f"{result.computation_time:.2f}s",
                str(result.iterations)
            ])
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Algorithm', 'Makespan', 'Time', 'Iterations'],
                           fill_color='lightgray'),
                cells=dict(values=list(zip(*stats_data)),
                          fill_color='white')
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title=f"FJSP Solution Dashboard - {instance.name}",
            height=800,
            showlegend=False
        )
        
        return fig
    
    def _extract_schedule_data(self, instance: UnifiedFJSPInstance, 
                              solution: SolutionResult) -> List[Dict]:
        """从求解结果中提取调度数据"""
        schedule_data = []
        
        # 根据不同的求解器类型解析调度数据
        if 'machine_schedules' in solution.schedule:
            # 进化算法格式
            machine_schedules = solution.schedule['machine_schedules']
            
            for machine_id, tasks in machine_schedules.items():
                for i, (start_time, end_time) in enumerate(tasks):
                    # 简化：假设任务按顺序对应工序
                    if i < len(instance.operations):
                        op = instance.operations[i]
                        schedule_data.append({
                            'job_id': op.job_id,
                            'operation_id': op.operation_id,
                            'machine': machine_id,
                            'start': start_time,
                            'end': end_time,
                            'duration': end_time - start_time
                        })
        
        elif 'jobshoplib_schedule' in solution.schedule:
            # JobShopLib格式 - 需要进一步解析
            # 这里提供一个简化的示例
            for i, op in enumerate(instance.operations):
                # 模拟调度数据
                start_time = i * 10  # 简化
                duration = op.processing_times[0] if op.processing_times else 5
                schedule_data.append({
                    'job_id': op.job_id,
                    'operation_id': op.operation_id,
                    'machine': op.machines[0] if op.machines else 0,
                    'start': start_time,
                    'end': start_time + duration,
                    'duration': duration
                })
        
        else:
            # 默认格式 - 生成模拟数据
            for i, op in enumerate(instance.operations):
                start_time = i * 8
                duration = op.processing_times[0] if op.processing_times else 5
                schedule_data.append({
                    'job_id': op.job_id,
                    'operation_id': op.operation_id,
                    'machine': op.machines[0] if op.machines else 0,
                    'start': start_time,
                    'end': start_time + duration,
                    'duration': duration
                })
        
        return schedule_data
    
    def _hierarchical_layout(self, G: nx.DiGraph, instance: UnifiedFJSPInstance) -> Dict:
        """分层布局算法"""
        pos = {}
        
        # 按作业分层
        job_positions = {}
        for job_id in range(instance.num_jobs):
            job_operations = [op for op in instance.operations if op.job_id == job_id]
            for i, op in enumerate(sorted(job_operations, key=lambda x: x.operation_id)):
                node_id = f"J{op.job_id}_O{op.operation_id}"
                pos[node_id] = (i * 2, job_id * 2)
        
        # 源点和汇点
        pos['SOURCE'] = (-1, instance.num_jobs)
        pos['SINK'] = (max([x for x, y in pos.values()]) + 1, instance.num_jobs)
        
        return pos


# 使用示例
if __name__ == "__main__":
    from ..core.data_adapter import InstanceGenerator
    from ..algorithms.unified_solver import UnifiedSolverManager
    
    # 生成测试实例
    instance = InstanceGenerator.generate_random_fjsp(3, 3, 3)
    
    # 求解
    manager = UnifiedSolverManager()
    results = manager.solve_parallel(instance, ['evolutionary'])
    
    # 可视化
    visualizer = UnifiedVisualizer()
    
    if results:
        best_result = list(results.values())[0]
        
        # 甘特图
        gantt_fig = visualizer.plot_gantt_chart(instance, best_result)
        gantt_fig.show()
        
        # 析取图
        graph_fig = visualizer.plot_disjunctive_graph(instance)
        graph_fig.show()
        
        # 仪表板
        dashboard_fig = visualizer.create_dashboard(instance, results)
        dashboard_fig.show()
