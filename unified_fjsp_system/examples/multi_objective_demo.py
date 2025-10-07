#!/usr/bin/env python3
"""
多目标FJSP优化演示
展示如何使用系统进行多目标优化和帕累托前沿分析
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import json

# 简化的多目标优化实现（用于演示）
class MultiObjectiveDemo:
    def __init__(self):
        self.objectives = ['makespan', 'flowtime', 'tardiness', 'energy']
        self.pareto_solutions = []
        
    def generate_sample_instance(self, num_jobs=10, num_machines=5):
        """生成示例FJSP实例"""
        instance = {
            'name': f'Demo_{num_jobs}x{num_machines}',
            'num_jobs': num_jobs,
            'num_machines': num_machines,
            'operations': []
        }
        
        # 生成工序
        for job_id in range(num_jobs):
            num_ops = np.random.randint(2, 5)  # 每个工件2-4道工序
            for op_id in range(num_ops):
                # 随机选择可用机器
                available_machines = np.random.choice(
                    num_machines, 
                    size=np.random.randint(1, min(3, num_machines)+1), 
                    replace=False
                )
                
                processing_times = {}
                for machine in available_machines:
                    processing_times[machine] = np.random.randint(5, 20)
                
                operation = {
                    'job_id': job_id,
                    'operation_id': op_id,
                    'machines': list(available_machines),
                    'processing_times': processing_times,
                    'setup_time': np.random.randint(0, 5)
                }
                instance['operations'].append(operation)
        
        return instance
    
    def evaluate_objectives(self, solution, instance):
        """评估解的多个目标函数值"""
        # 模拟目标函数计算
        num_jobs = instance['num_jobs']
        num_machines = instance['num_machines']
        num_operations = len(instance['operations'])
        
        # 基于实例规模的基础值
        base_makespan = num_jobs * 10 + np.random.normal(0, 5)
        base_flowtime = num_jobs * 15 + np.random.normal(0, 8)
        base_tardiness = max(0, num_jobs * 5 + np.random.normal(0, 10))
        base_energy = num_machines * 50 + np.random.normal(0, 15)
        
        # 添加解相关的变化
        solution_factor = np.random.uniform(0.8, 1.2)
        
        objectives = {
            'makespan': max(1, base_makespan * solution_factor),
            'flowtime': max(1, base_flowtime * solution_factor),
            'tardiness': max(0, base_tardiness * solution_factor),
            'energy': max(1, base_energy * solution_factor)
        }
        
        return objectives
    
    def generate_pareto_front(self, instance, num_solutions=50):
        """生成模拟的帕累托前沿"""
        print(f"🎯 生成 {num_solutions} 个候选解...")
        
        all_solutions = []
        all_objectives = []
        
        # 生成候选解
        for i in range(num_solutions * 3):  # 生成更多解，然后筛选
            solution = f"solution_{i}"
            objectives = self.evaluate_objectives(solution, instance)
            
            all_solutions.append(solution)
            all_objectives.append(list(objectives.values()))
        
        # 提取帕累托前沿
        pareto_indices = self.extract_pareto_front(all_objectives)
        
        self.pareto_solutions = []
        for idx in pareto_indices:
            self.pareto_solutions.append({
                'solution': all_solutions[idx],
                'objectives': {
                    'makespan': all_objectives[idx][0],
                    'flowtime': all_objectives[idx][1],
                    'tardiness': all_objectives[idx][2],
                    'energy': all_objectives[idx][3]
                }
            })
        
        print(f"✅ 帕累托前沿包含 {len(self.pareto_solutions)} 个解")
        return self.pareto_solutions
    
    def extract_pareto_front(self, objectives):
        """提取帕累托前沿"""
        pareto_indices = []
        
        for i, obj1 in enumerate(objectives):
            is_dominated = False
            
            for j, obj2 in enumerate(objectives):
                if i != j and self.dominates(obj2, obj1):
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_indices.append(i)
        
        return pareto_indices
    
    def dominates(self, obj1, obj2):
        """判断obj1是否支配obj2（假设所有目标都是最小化）"""
        better_count = 0
        worse_count = 0
        
        for v1, v2 in zip(obj1, obj2):
            if v1 < v2:
                better_count += 1
            elif v1 > v2:
                worse_count += 1
        
        return better_count > 0 and worse_count == 0
    
    def calculate_hypervolume(self, reference_point=None):
        """计算超体积指标"""
        if not self.pareto_solutions:
            return 0.0
        
        if reference_point is None:
            # 使用最差值作为参考点
            max_values = {}
            for obj in self.objectives:
                max_values[obj] = max(sol['objectives'][obj] for sol in self.pareto_solutions)
            reference_point = [max_values[obj] * 1.1 for obj in self.objectives]
        
        # 简化的2D超体积计算
        if len(self.objectives) >= 2:
            points = [(sol['objectives']['makespan'], sol['objectives']['flowtime']) 
                     for sol in self.pareto_solutions]
            points.sort()
            
            hypervolume = 0.0
            prev_x = reference_point[0]
            
            for x, y in points:
                if y < reference_point[1]:
                    width = prev_x - x
                    height = reference_point[1] - y
                    hypervolume += width * height
                    prev_x = x
            
            return hypervolume
        
        return 0.0
    
    def visualize_pareto_front_2d(self):
        """2D帕累托前沿可视化"""
        if not self.pareto_solutions:
            return None
        
        # 提取目标值
        makespan_values = [sol['objectives']['makespan'] for sol in self.pareto_solutions]
        flowtime_values = [sol['objectives']['flowtime'] for sol in self.pareto_solutions]
        
        fig = go.Figure()
        
        # 添加帕累托前沿点
        fig.add_trace(go.Scatter(
            x=makespan_values,
            y=flowtime_values,
            mode='markers+lines',
            name='帕累托前沿',
            marker=dict(size=10, color='red', symbol='circle'),
            line=dict(color='red', width=2, dash='dash'),
            hovertemplate='<b>完工时间</b>: %{x:.2f}<br>' +
                         '<b>流程时间</b>: %{y:.2f}<br>' +
                         '<extra></extra>'
        ))
        
        # 添加理想点
        ideal_makespan = min(makespan_values)
        ideal_flowtime = min(flowtime_values)
        fig.add_trace(go.Scatter(
            x=[ideal_makespan],
            y=[ideal_flowtime],
            mode='markers',
            name='理想点',
            marker=dict(size=15, color='green', symbol='star'),
            hovertemplate='<b>理想点</b><br>' +
                         '<b>完工时间</b>: %{x:.2f}<br>' +
                         '<b>流程时间</b>: %{y:.2f}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title='FJSP多目标优化 - 帕累托前沿 (2D)',
            xaxis_title='完工时间 (Makespan)',
            yaxis_title='总流程时间 (Total Flowtime)',
            showlegend=True,
            hovermode='closest',
            width=800,
            height=600
        )
        
        return fig
    
    def visualize_pareto_front_3d(self):
        """3D帕累托前沿可视化"""
        if not self.pareto_solutions:
            return None
        
        # 提取目标值
        makespan_values = [sol['objectives']['makespan'] for sol in self.pareto_solutions]
        flowtime_values = [sol['objectives']['flowtime'] for sol in self.pareto_solutions]
        tardiness_values = [sol['objectives']['tardiness'] for sol in self.pareto_solutions]
        energy_values = [sol['objectives']['energy'] for sol in self.pareto_solutions]
        
        fig = go.Figure()
        
        # 添加3D散点图
        fig.add_trace(go.Scatter3d(
            x=makespan_values,
            y=flowtime_values,
            z=tardiness_values,
            mode='markers',
            name='帕累托前沿',
            marker=dict(
                size=8,
                color=energy_values,
                colorscale='Viridis',
                colorbar=dict(title="能耗"),
                opacity=0.8
            ),
            hovertemplate='<b>完工时间</b>: %{x:.2f}<br>' +
                         '<b>流程时间</b>: %{y:.2f}<br>' +
                         '<b>延迟时间</b>: %{z:.2f}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title='FJSP多目标优化 - 帕累托前沿 (3D)',
            scene=dict(
                xaxis_title='完工时间',
                yaxis_title='流程时间',
                zaxis_title='延迟时间'
            ),
            width=900,
            height=700
        )
        
        return fig
    
    def visualize_parallel_coordinates(self):
        """平行坐标图可视化"""
        if not self.pareto_solutions:
            return None
        
        # 准备数据
        data = []
        for i, sol in enumerate(self.pareto_solutions):
            row = [i] + [sol['objectives'][obj] for obj in self.objectives]
            data.append(row)
        
        df = pd.DataFrame(data, columns=['解编号'] + self.objectives)
        
        # 标准化数据用于颜色映射
        normalized_makespan = (df['makespan'] - df['makespan'].min()) / (df['makespan'].max() - df['makespan'].min())
        
        fig = go.Figure(data=go.Parcoords(
            line=dict(color=normalized_makespan, colorscale='RdYlBu_r'),
            dimensions=[
                dict(label='完工时间', values=df['makespan']),
                dict(label='流程时间', values=df['flowtime']),
                dict(label='延迟时间', values=df['tardiness']),
                dict(label='能耗', values=df['energy'])
            ]
        ))
        
        fig.update_layout(
            title='FJSP多目标优化 - 平行坐标图',
            width=1000,
            height=600
        )
        
        return fig
    
    def generate_performance_metrics(self):
        """生成性能指标"""
        if not self.pareto_solutions:
            return {}
        
        metrics = {}
        
        # 基本统计
        for obj in self.objectives:
            values = [sol['objectives'][obj] for sol in self.pareto_solutions]
            metrics[f'{obj}_min'] = min(values)
            metrics[f'{obj}_max'] = max(values)
            metrics[f'{obj}_mean'] = np.mean(values)
            metrics[f'{obj}_std'] = np.std(values)
        
        # 帕累托前沿大小
        metrics['pareto_front_size'] = len(self.pareto_solutions)
        
        # 超体积指标
        metrics['hypervolume'] = self.calculate_hypervolume()
        
        # 分布均匀性（简化版）
        if len(self.pareto_solutions) > 1:
            distances = []
            for i, sol1 in enumerate(self.pareto_solutions):
                min_dist = float('inf')
                for j, sol2 in enumerate(self.pareto_solutions):
                    if i != j:
                        dist = sum((sol1['objectives'][obj] - sol2['objectives'][obj])**2 
                                 for obj in self.objectives)**0.5
                        min_dist = min(min_dist, dist)
                distances.append(min_dist)
            
            metrics['spacing'] = np.std(distances)
        else:
            metrics['spacing'] = 0.0
        
        return metrics
    
    def save_results(self, filename='multi_objective_results.json'):
        """保存结果到文件"""
        results = {
            'pareto_solutions': self.pareto_solutions,
            'performance_metrics': self.generate_performance_metrics(),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 结果已保存到 {filename}")

def main():
    """主演示函数"""
    print("🎯 FJSP多目标优化演示")
    print("=" * 50)
    
    # 创建演示实例
    demo = MultiObjectiveDemo()
    
    # 生成测试实例
    print("📋 生成测试实例...")
    instance = demo.generate_sample_instance(num_jobs=15, num_machines=6)
    print(f"✅ 实例: {instance['name']}, {len(instance['operations'])} 个工序")
    
    # 生成帕累托前沿
    pareto_front = demo.generate_pareto_front(instance, num_solutions=30)
    
    # 计算性能指标
    print("\n📊 计算性能指标...")
    metrics = demo.generate_performance_metrics()
    
    print(f"📈 帕累托前沿大小: {metrics['pareto_front_size']}")
    print(f"📈 超体积指标: {metrics['hypervolume']:.2f}")
    print(f"📈 分布均匀性: {metrics['spacing']:.2f}")
    
    print("\n🎯 目标函数统计:")
    for obj in demo.objectives:
        print(f"  {obj}: 最小={metrics[f'{obj}_min']:.2f}, "
              f"最大={metrics[f'{obj}_max']:.2f}, "
              f"平均={metrics[f'{obj}_mean']:.2f}")
    
    # 生成可视化
    print("\n🎨 生成可视化图表...")
    
    # 2D帕累托前沿
    fig_2d = demo.visualize_pareto_front_2d()
    if fig_2d:
        fig_2d.write_html('pareto_front_2d.html')
        print("📊 2D帕累托前沿: pareto_front_2d.html")
    
    # 3D帕累托前沿
    fig_3d = demo.visualize_pareto_front_3d()
    if fig_3d:
        fig_3d.write_html('pareto_front_3d.html')
        print("📊 3D帕累托前沿: pareto_front_3d.html")
    
    # 平行坐标图
    fig_parallel = demo.visualize_parallel_coordinates()
    if fig_parallel:
        fig_parallel.write_html('parallel_coordinates.html')
        print("📊 平行坐标图: parallel_coordinates.html")
    
    # 保存结果
    demo.save_results()
    
    print("\n🎉 多目标优化演示完成！")
    print("💡 打开生成的HTML文件查看交互式可视化结果")

if __name__ == "__main__":
    main()
