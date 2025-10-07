#!/usr/bin/env python3
"""
系统测试脚本 - 快速验证统一FJSP系统是否正常工作
"""
import sys
import os
import traceback
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def test_imports():
    """测试模块导入"""
    print("🔍 Testing module imports...")
    
    try:
        from core.data_adapter import UnifiedFJSPInstance, InstanceGenerator, DataAdapter
        print("✅ Core data adapter imported successfully")
    except Exception as e:
        print(f"❌ Failed to import core data adapter: {e}")
        return False
    
    try:
        from algorithms.unified_solver import UnifiedSolverManager
        print("✅ Unified solver imported successfully")
    except Exception as e:
        print(f"❌ Failed to import unified solver: {e}")
        return False
    
    try:
        from visualization.unified_visualizer import UnifiedVisualizer
        print("✅ Unified visualizer imported successfully")
    except Exception as e:
        print(f"❌ Failed to import unified visualizer: {e}")
        return False
    
    return True


def test_instance_generation():
    """测试实例生成"""
    print("\n📊 Testing instance generation...")
    
    try:
        from core.data_adapter import InstanceGenerator
        
        instance = InstanceGenerator.generate_random_fjsp(
            num_jobs=2,
            num_machines=2, 
            max_operations_per_job=2,
            flexibility=0.5
        )
        
        print(f"✅ Generated instance: {instance.name}")
        print(f"   Jobs: {instance.num_jobs}, Machines: {instance.num_machines}")
        print(f"   Operations: {len(instance.operations)}")
        
        return instance
        
    except Exception as e:
        print(f"❌ Failed to generate instance: {e}")
        traceback.print_exc()
        return None


def test_disjunctive_graph():
    """测试析取图构建"""
    print("\n🕸️  Testing disjunctive graph construction...")
    
    try:
        from core.data_adapter import InstanceGenerator, DataAdapter
        
        instance = InstanceGenerator.generate_random_fjsp(2, 2, 2)
        graph = DataAdapter.build_disjunctive_graph(instance)
        
        print(f"✅ Built disjunctive graph:")
        print(f"   Nodes: {graph.number_of_nodes()}")
        print(f"   Edges: {graph.number_of_edges()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to build disjunctive graph: {e}")
        traceback.print_exc()
        return False


def test_evolutionary_solver():
    """测试进化算法求解器"""
    print("\n🧬 Testing evolutionary algorithm solver...")
    
    try:
        from core.data_adapter import InstanceGenerator
        from algorithms.unified_solver import UnifiedSolverManager
        
        instance = InstanceGenerator.generate_random_fjsp(2, 2, 2)
        manager = UnifiedSolverManager()
        
        ea_solver = manager.get_solver('evolutionary')
        result = ea_solver.solve(
            instance,
            population_size=10,
            generations=20,
            mutation_rate=0.1,
            crossover_rate=0.8
        )
        
        print(f"✅ EA solver completed:")
        print(f"   Makespan: {result.makespan:.2f}")
        print(f"   Time: {result.computation_time:.2f}s")
        print(f"   Iterations: {result.iterations}")
        
        return result
        
    except Exception as e:
        print(f"❌ Failed to run evolutionary solver: {e}")
        traceback.print_exc()
        return None


def test_visualization():
    """测试可视化功能"""
    print("\n📊 Testing visualization...")
    
    try:
        from core.data_adapter import InstanceGenerator
        from algorithms.unified_solver import UnifiedSolverManager
        from visualization.unified_visualizer import UnifiedVisualizer
        
        instance = InstanceGenerator.generate_random_fjsp(2, 2, 2)
        manager = UnifiedSolverManager()
        
        # 获取一个简单的解
        ea_solver = manager.get_solver('evolutionary')
        result = ea_solver.solve(instance, population_size=5, generations=10)
        
        visualizer = UnifiedVisualizer()
        
        # 测试甘特图
        gantt_fig = visualizer.plot_gantt_chart(instance, result)
        print("✅ Gantt chart generated successfully")
        
        # 测试析取图
        graph_fig = visualizer.plot_disjunctive_graph(instance)
        print("✅ Disjunctive graph visualization generated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate visualizations: {e}")
        traceback.print_exc()
        return False


def test_data_conversion():
    """测试数据格式转换"""
    print("\n🔄 Testing data format conversion...")
    
    try:
        from core.data_adapter import InstanceGenerator, DataAdapter
        
        instance = InstanceGenerator.generate_random_fjsp(2, 2, 2)
        
        # 测试转换为Graph-JSP-Env格式
        jsp_array = DataAdapter.to_graph_jsp_env(instance)
        print(f"✅ Converted to Graph-JSP-Env format: shape {jsp_array.shape}")
        
        # 测试转换为Schlably格式
        schlably_dict = DataAdapter.to_schlably_format(instance)
        print(f"✅ Converted to Schlably format: {len(schlably_dict)} keys")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to convert data formats: {e}")
        traceback.print_exc()
        return False


def test_parallel_solving():
    """测试并行求解"""
    print("\n🚀 Testing parallel solving...")
    
    try:
        from core.data_adapter import InstanceGenerator
        from algorithms.unified_solver import UnifiedSolverManager
        
        instance = InstanceGenerator.generate_random_fjsp(2, 2, 2)
        manager = UnifiedSolverManager()
        
        # 并行运行多个算法（使用较小的参数以加快测试）
        results = manager.solve_parallel(
            instance, 
            algorithms=['evolutionary'],  # 只测试进化算法
            population_size=5,
            generations=10
        )
        
        print(f"✅ Parallel solving completed:")
        for alg, result in results.items():
            print(f"   {alg}: makespan={result.makespan:.2f}, time={result.computation_time:.2f}s")
        
        return results
        
    except Exception as e:
        print(f"❌ Failed to run parallel solving: {e}")
        traceback.print_exc()
        return None


def main():
    """主测试函数"""
    print("🏭 Unified FJSP System - Quick Test")
    print("=" * 50)
    
    # 测试计数器
    tests_passed = 0
    total_tests = 7
    
    # 1. 测试导入
    if test_imports():
        tests_passed += 1
    
    # 2. 测试实例生成
    if test_instance_generation():
        tests_passed += 1
    
    # 3. 测试析取图
    if test_disjunctive_graph():
        tests_passed += 1
    
    # 4. 测试数据转换
    if test_data_conversion():
        tests_passed += 1
    
    # 5. 测试进化算法
    if test_evolutionary_solver():
        tests_passed += 1
    
    # 6. 测试可视化
    if test_visualization():
        tests_passed += 1
    
    # 7. 测试并行求解
    if test_parallel_solving():
        tests_passed += 1
    
    # 结果总结
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The system is working correctly.")
        print("\n🚀 Next steps:")
        print("   1. Run the web app: python run_web_app.py")
        print("   2. Try the examples: python examples/basic_usage.py")
        return 0
    else:
        print(f"⚠️  {total_tests - tests_passed} tests failed. Please check the errors above.")
        print("\n💡 Common issues:")
        print("   - Missing dependencies: pip install -r requirements.txt")
        print("   - Python path issues: run from the unified_fjsp_system directory")
        return 1


if __name__ == "__main__":
    sys.exit(main())
