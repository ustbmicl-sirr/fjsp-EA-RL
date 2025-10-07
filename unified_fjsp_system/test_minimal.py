#!/usr/bin/env python3
"""
最小化测试脚本 - 验证核心功能
"""
import sys
import os
import traceback
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_basic_imports():
    """测试基础导入"""
    print("🔍 测试基础导入...")
    
    try:
        import numpy as np
        print("✅ numpy导入成功")
    except ImportError as e:
        print(f"❌ numpy导入失败: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas导入成功")
    except ImportError as e:
        print(f"❌ pandas导入失败: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✅ matplotlib导入成功")
    except ImportError as e:
        print(f"❌ matplotlib导入失败: {e}")
        return False
    
    try:
        import plotly.graph_objects as go
        print("✅ plotly导入成功")
    except ImportError as e:
        print(f"❌ plotly导入失败: {e}")
        return False
    
    try:
        import networkx as nx
        print("✅ networkx导入成功")
    except ImportError as e:
        print(f"❌ networkx导入失败: {e}")
        return False
    
    return True

def test_web_imports():
    """测试Web相关导入"""
    print("\n🌐 测试Web框架导入...")
    
    try:
        import streamlit as st
        print("✅ streamlit导入成功")
    except ImportError as e:
        print(f"❌ streamlit导入失败: {e}")
        return False
    
    try:
        import flask
        print("✅ flask导入成功")
    except ImportError as e:
        print(f"❌ flask导入失败: {e}")
        return False
    
    try:
        import flask_cors
        print("✅ flask-cors导入成功")
    except ImportError as e:
        print(f"❌ flask-cors导入失败: {e}")
        return False
    
    try:
        import flask_socketio
        print("✅ flask-socketio导入成功")
    except ImportError as e:
        print(f"❌ flask-socketio导入失败: {e}")
        return False
    
    return True

def test_core_modules():
    """测试核心模块"""
    print("\n📊 测试核心模块...")
    
    try:
        from core.data_adapter import UnifiedFJSPInstance, InstanceGenerator
        print("✅ 核心数据适配器导入成功")
        
        # 测试实例生成
        instance = InstanceGenerator.generate_random_fjsp(2, 2, 2)
        print(f"✅ 实例生成成功: {instance.name}")
        
        return True
    except Exception as e:
        print(f"❌ 核心模块测试失败: {e}")
        traceback.print_exc()
        return False

def test_algorithm_modules():
    """测试算法模块"""
    print("\n🧠 测试算法模块...")
    
    try:
        from algorithms.unified_solver import UnifiedSolverManager
        print("✅ 统一求解器导入成功")
        
        manager = UnifiedSolverManager()
        print("✅ 求解器管理器创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 算法模块测试失败: {e}")
        traceback.print_exc()
        return False

def test_visualization_modules():
    """测试可视化模块"""
    print("\n📈 测试可视化模块...")
    
    try:
        from visualization.unified_visualizer import UnifiedVisualizer
        print("✅ 统一可视化器导入成功")
        
        visualizer = UnifiedVisualizer()
        print("✅ 可视化器创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 可视化模块测试失败: {e}")
        traceback.print_exc()
        return False

def test_optional_libraries():
    """测试可选库"""
    print("\n📚 测试可选库...")
    
    optional_libs = {
        'job_shop_lib': 'JobShopLib',
        'ortools': 'OR-Tools',
        'gymnasium': 'Gymnasium',
        'stable_baselines3': 'Stable-Baselines3'
    }
    
    available = []
    missing = []
    
    for lib, name in optional_libs.items():
        try:
            __import__(lib)
            print(f"✅ {name} 可用")
            available.append(name)
        except ImportError:
            print(f"⚠️  {name} 不可用")
            missing.append(name)
    
    print(f"\n📊 可选库状态: {len(available)}/{len(optional_libs)} 可用")
    if missing:
        print(f"缺少: {', '.join(missing)}")
    
    return True

def test_simple_workflow():
    """测试简单工作流"""
    print("\n🔄 测试简单工作流...")
    
    try:
        # 导入模块
        from core.data_adapter import InstanceGenerator
        from algorithms.unified_solver import UnifiedSolverManager
        from visualization.unified_visualizer import UnifiedVisualizer
        
        # 生成实例
        instance = InstanceGenerator.generate_random_fjsp(2, 2, 2)
        print(f"✅ 生成实例: {instance.num_jobs}作业, {instance.num_machines}机器")
        
        # 创建求解器
        manager = UnifiedSolverManager()
        ea_solver = manager.get_solver('evolutionary')
        
        # 简单求解（小参数）
        result = ea_solver.solve(
            instance,
            population_size=5,
            generations=10
        )
        print(f"✅ 求解完成: makespan={result.makespan:.2f}")
        
        # 创建可视化
        visualizer = UnifiedVisualizer()
        fig = visualizer.plot_gantt_chart(instance, result)
        print("✅ 甘特图生成成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🏭 统一FJSP系统 - 最小化测试")
    print("=" * 40)
    
    tests = [
        ("基础导入", test_basic_imports),
        ("Web框架", test_web_imports),
        ("核心模块", test_core_modules),
        ("算法模块", test_algorithm_modules),
        ("可视化模块", test_visualization_modules),
        ("可选库", test_optional_libraries),
        ("简单工作流", test_simple_workflow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用")
        return 0
    else:
        print(f"⚠️  {total - passed} 个测试失败")
        print("\n💡 建议:")
        print("1. 检查conda环境是否正确激活")
        print("2. 运行: pip install streamlit flask flask-cors flask-socketio")
        print("3. 检查Python路径设置")
        return 1

if __name__ == "__main__":
    sys.exit(main())
