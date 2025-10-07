"""
基础使用示例 - 展示统一FJSP系统的核心功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_adapter import InstanceGenerator, DataAdapter
from algorithms.unified_solver import UnifiedSolverManager
from visualization.unified_visualizer import UnifiedVisualizer


def main():
    print("🏭 Unified FJSP System - Basic Usage Example")
    print("=" * 50)
    
    # 1. 生成FJSP实例
    print("\n📊 Step 1: Generating FJSP Instance")
    instance = InstanceGenerator.generate_random_fjsp(
        num_jobs=3,
        num_machines=3,
        max_operations_per_job=3,
        flexibility=0.6
    )
    
    print(f"✅ Generated instance: {instance.name}")
    print(f"   - Jobs: {instance.num_jobs}")
    print(f"   - Machines: {instance.num_machines}")
    print(f"   - Operations: {len(instance.operations)}")
    
    # 显示实例详情
    print("\n📋 Instance Details:")
    for i, op in enumerate(instance.operations):
        print(f"   Operation {i}: Job {op.job_id}, Op {op.operation_id}")
        print(f"     Machines: {op.machines}")
        print(f"     Times: {op.processing_times}")
    
    # 2. 构建析取图
    print("\n🕸️  Step 2: Building Disjunctive Graph")
    graph = DataAdapter.build_disjunctive_graph(instance)
    print(f"✅ Built disjunctive graph:")
    print(f"   - Nodes: {graph.number_of_nodes()}")
    print(f"   - Edges: {graph.number_of_edges()}")
    
    # 3. 创建求解器管理器
    print("\n🧠 Step 3: Setting up Solvers")
    solver_manager = UnifiedSolverManager()
    
    # 添加监控回调
    def progress_callback(data):
        if 'generation' in data:
            if data['generation'] % 20 == 0:  # 每20代显示一次
                print(f"   Generation {data['generation']}: Best = {data['best_fitness']:.2f}")
        elif 'step' in data:
            if data['step'] % 50 == 0:  # 每50步显示一次
                print(f"   RL Step {data['step']}: Reward = {data['reward']:.2f}")
    
    solver_manager.add_global_callback(progress_callback)
    
    # 4. 求解问题
    print("\n🚀 Step 4: Solving Problem")
    
    # 使用进化算法求解
    print("\n🧬 Running Evolutionary Algorithm...")
    try:
        evolutionary_solver = solver_manager.get_solver('evolutionary')
        ea_result = evolutionary_solver.solve(
            instance,
            population_size=30,
            generations=100,
            mutation_rate=0.1,
            crossover_rate=0.8
        )
        print(f"✅ EA Result: Makespan = {ea_result.makespan:.2f}, Time = {ea_result.computation_time:.2f}s")
    except Exception as e:
        print(f"❌ EA Error: {e}")
        ea_result = None
    
    # 使用强化学习求解
    print("\n🤖 Running Reinforcement Learning...")
    try:
        rl_solver = solver_manager.get_solver('reinforcement')
        rl_result = rl_solver.solve(instance)
        print(f"✅ RL Result: Makespan = {rl_result.makespan:.2f}, Time = {rl_result.computation_time:.2f}s")
    except Exception as e:
        print(f"❌ RL Error: {e}")
        rl_result = None
    
    # 收集结果
    results = {}
    if ea_result:
        results['Evolutionary'] = ea_result
    if rl_result:
        results['Reinforcement Learning'] = rl_result
    
    if not results:
        print("❌ No successful solutions found!")
        return
    
    # 5. 可视化结果
    print("\n📊 Step 5: Visualizing Results")
    visualizer = UnifiedVisualizer()
    
    # 找到最佳解
    best_alg = min(results.keys(), key=lambda x: results[x].makespan)
    best_result = results[best_alg]
    
    print(f"🏆 Best Solution: {best_alg} with makespan {best_result.makespan:.2f}")
    
    # 生成可视化
    try:
        # 甘特图
        print("📅 Generating Gantt Chart...")
        gantt_fig = visualizer.plot_gantt_chart(instance, best_result)
        gantt_fig.write_html("gantt_chart.html")
        print("✅ Gantt chart saved to 'gantt_chart.html'")
        
        # 析取图
        print("🕸️  Generating Disjunctive Graph...")
        graph_fig = visualizer.plot_disjunctive_graph(instance)
        graph_fig.write_html("disjunctive_graph.html")
        print("✅ Disjunctive graph saved to 'disjunctive_graph.html'")
        
        # 算法比较（如果有多个结果）
        if len(results) > 1:
            print("⚖️  Generating Algorithm Comparison...")
            comparison_fig = visualizer.plot_algorithm_comparison(results)
            comparison_fig.write_html("algorithm_comparison.html")
            print("✅ Algorithm comparison saved to 'algorithm_comparison.html'")
        
        # 收敛图（如果有收敛历史）
        convergence_results = {alg: result for alg, result in results.items() 
                             if result.convergence_history}
        if convergence_results:
            print("📈 Generating Convergence Plot...")
            convergence_fig = visualizer.plot_convergence_comparison(convergence_results)
            convergence_fig.write_html("convergence_plot.html")
            print("✅ Convergence plot saved to 'convergence_plot.html'")
        
        # 综合仪表板
        print("📋 Generating Dashboard...")
        dashboard_fig = visualizer.create_dashboard(instance, results)
        dashboard_fig.write_html("dashboard.html")
        print("✅ Dashboard saved to 'dashboard.html'")
        
    except Exception as e:
        print(f"❌ Visualization Error: {e}")
    
    # 6. 结果总结
    print("\n📊 Step 6: Results Summary")
    print("=" * 50)
    
    for alg, result in results.items():
        print(f"\n🔹 {alg}:")
        print(f"   Makespan: {result.makespan:.2f}")
        print(f"   Computation Time: {result.computation_time:.2f}s")
        print(f"   Iterations: {result.iterations}")
        if result.convergence_history:
            improvement = result.convergence_history[0] - result.convergence_history[-1]
            print(f"   Improvement: {improvement:.2f}")
    
    # 性能比较
    if len(results) > 1:
        print(f"\n🏆 Performance Ranking:")
        sorted_results = sorted(results.items(), key=lambda x: x[1].makespan)
        for i, (alg, result) in enumerate(sorted_results, 1):
            print(f"   {i}. {alg}: {result.makespan:.2f}")
    
    print("\n🎉 Example completed successfully!")
    print("📁 Check the generated HTML files for interactive visualizations.")


if __name__ == "__main__":
    main()
