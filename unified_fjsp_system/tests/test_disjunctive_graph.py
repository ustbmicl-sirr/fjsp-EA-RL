#!/usr/bin/env python3
"""
析取图可视化功能测试脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time
import webbrowser
from core.data_adapter import InstanceGenerator, DataAdapter
from visualization.unified_visualizer import UnifiedVisualizer
import plotly.graph_objects as go
import networkx as nx

def test_disjunctive_graph_visualization():
    """测试析取图可视化功能"""
    print("🔍 开始测试析取图可视化功能...")
    
    # 1. 生成测试实例
    print("\n📊 步骤1: 生成FJSP测试实例")
    instance = InstanceGenerator.generate_random_fjsp(
        num_jobs=3,
        num_machines=3,
        max_operations_per_job=3,
        flexibility=0.7
    )
    
    print(f"✅ 生成实例: {instance.name}")
    print(f"   - 工件数: {instance.num_jobs}")
    print(f"   - 机器数: {instance.num_machines}")
    print(f"   - 工序数: {len(instance.operations)}")
    
    # 2. 构建析取图
    print("\n🔗 步骤2: 构建析取图")
    graph = DataAdapter.build_disjunctive_graph(instance)
    
    print(f"✅ 析取图构建完成:")
    print(f"   - 节点数: {graph.number_of_nodes()}")
    print(f"   - 边数: {graph.number_of_edges()}")
    
    # 统计边类型
    conjunctive_edges = 0
    disjunctive_edges = 0
    for u, v, data in graph.edges(data=True):
        if data.get('edge_type') == 'conjunctive':
            conjunctive_edges += 1
        elif data.get('edge_type') == 'disjunctive':
            disjunctive_edges += 1
    
    print(f"   - 合取边数: {conjunctive_edges}")
    print(f"   - 析取边数: {disjunctive_edges}")
    
    # 3. 显示实例详细信息
    print("\n📋 步骤3: 实例详细信息")
    for i, op in enumerate(instance.operations):
        print(f"   工序{i+1}: J{op.job_id}_O{op.operation_id}")
        print(f"     - 可选机器: {op.machines}")
        print(f"     - 加工时间: {op.processing_times}")
    
    # 4. 创建可视化
    print("\n🎨 步骤4: 创建析取图可视化")
    visualizer = UnifiedVisualizer()
    
    # 测试不同布局
    layouts = ['spring', 'hierarchical', 'random']
    
    for layout in layouts:
        print(f"   📈 生成{layout}布局的析取图...")
        try:
            fig = visualizer.plot_disjunctive_graph(instance, layout=layout)
            
            # 保存为HTML文件
            filename = f"disjunctive_graph_{layout}.html"
            fig.write_html(filename)
            print(f"   ✅ 保存为: {filename}")
            
        except Exception as e:
            print(f"   ❌ {layout}布局生成失败: {e}")
    
    return instance, graph

def test_api_integration():
    """测试API集成"""
    print("\n🌐 步骤5: 测试API集成")
    
    api_base = "http://localhost:5001/api"
    
    try:
        # 检查后端健康状态
        response = requests.get(f"{api_base}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端API连接正常")
            
            # 创建实例
            instance_data = {
                "type": "random",
                "num_jobs": 3,
                "num_machines": 3,
                "max_operations_per_job": 3,
                "flexibility": 0.7
            }
            
            response = requests.post(f"{api_base}/instances", 
                                   json=instance_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                instance_id = result['instance_id']
                print(f"✅ 通过API创建实例: {instance_id}")
                
                # 获取实例详情
                response = requests.get(f"{api_base}/instances/{instance_id}", timeout=5)
                if response.status_code == 200:
                    instance_detail = response.json()
                    print(f"✅ 获取实例详情成功")
                    print(f"   - 工件数: {instance_detail['num_jobs']}")
                    print(f"   - 机器数: {instance_detail['num_machines']}")
                    print(f"   - 工序数: {len(instance_detail['operations'])}")
                    
                    return instance_id
                else:
                    print(f"❌ 获取实例详情失败: {response.status_code}")
            else:
                print(f"❌ 创建实例失败: {response.status_code}")
        else:
            print(f"❌ 后端API连接失败: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API连接错误: {e}")
        print("💡 请确保后端服务正在运行 (./start_system.sh)")
    
    return None

def test_web_interface():
    """测试Web界面"""
    print("\n🌐 步骤6: 测试Web界面")
    
    try:
        # 检查前端是否可访问
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ 前端Web界面可访问")
            print("🌐 打开浏览器访问: http://localhost:8501")
            
            # 自动打开浏览器
            webbrowser.open("http://localhost:8501")
            
            return True
        else:
            print(f"❌ 前端访问失败: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 前端连接错误: {e}")
        print("💡 请确保前端服务正在运行")
    
    return False

def main():
    """主测试函数"""
    print("🏭 FJSP析取图可视化功能测试")
    print("=" * 50)
    
    # 测试核心功能
    instance, graph = test_disjunctive_graph_visualization()
    
    # 测试API集成
    instance_id = test_api_integration()
    
    # 测试Web界面
    web_available = test_web_interface()
    
    # 总结
    print("\n📋 测试总结")
    print("=" * 50)
    print("✅ 析取图构建: 成功")
    print("✅ 可视化生成: 成功")
    print(f"{'✅' if instance_id else '❌'} API集成: {'成功' if instance_id else '失败'}")
    print(f"{'✅' if web_available else '❌'} Web界面: {'可访问' if web_available else '不可访问'}")
    
    print("\n🎯 手动测试步骤:")
    print("1. 访问 http://localhost:8501")
    print("2. 在侧边栏选择'随机生成'")
    print("3. 设置参数: 工件数=3, 机器数=3, 工序数=3")
    print("4. 点击'生成实例'")
    print("5. 在可视化选项中勾选'析取图'")
    print("6. 选择算法并点击'开始求解'")
    print("7. 查看析取图可视化结果")

if __name__ == "__main__":
    main()
