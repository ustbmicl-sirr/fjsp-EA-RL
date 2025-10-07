"""
Streamlit Web应用 - 统一FJSP可视化系统前端（改进版，支持后端API）
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Any
import time
import threading
from datetime import datetime
import requests
import json
import socketio

# 导入自定义模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 容错导入
try:
    from core.data_adapter import UnifiedFJSPInstance, InstanceGenerator, DataAdapter
    from algorithms.unified_solver import UnifiedSolverManager, SolutionResult
    from visualization.unified_visualizer import UnifiedVisualizer
    MODULES_AVAILABLE = True
except ImportError as e:
    st.warning(f"核心模块导入失败: {e}")
    st.info("将使用简化模式运行")
    MODULES_AVAILABLE = False

    # 创建简化的类
    class SimpleOperation:
        def __init__(self, job_id, operation_id, machines, processing_times):
            self.job_id = job_id
            self.operation_id = operation_id
            self.machines = machines
            self.processing_times = processing_times
            self.setup_time = 0

    class SimpleInstance:
        def __init__(self, name, num_jobs, num_machines):
            self.name = name
            self.num_jobs = num_jobs
            self.num_machines = num_machines
            self.operations = []
            self.metadata = {}

            # 生成简化的工序
            for job_id in range(num_jobs):
                for op_id in range(3):  # 每个工件3道工序
                    machines = [0, 1] if num_machines > 1 else [0]
                    processing_times = [5, 6] if num_machines > 1 else [5]
                    op = SimpleOperation(job_id, op_id, machines, processing_times)
                    self.operations.append(op)

    class InstanceGenerator:
        @staticmethod
        def generate_random_fjsp(num_jobs, num_machines, max_operations_per_job=3, **kwargs):
            return SimpleInstance(f"简化实例_{num_jobs}x{num_machines}", num_jobs, num_machines)

    class UnifiedSolverManager:
        def solve_async(self, *args, **kwargs):
            return {"makespan": 100.0, "status": "简化求解完成"}

    class UnifiedVisualizer:
        def plot_gantt_chart(self, *args, **kwargs):
            fig = go.Figure()
            fig.add_annotation(text="简化甘特图", x=0.5, y=0.5)
            return fig

# 后端API配置
API_BASE_URL = "http://localhost:5001/api"
WEBSOCKET_URL = "http://localhost:5001"


class StreamlitApp:
    """Streamlit应用主类（改进版，支持前后端分离）"""

    def __init__(self):
        self.solver_manager = UnifiedSolverManager()
        self.visualizer = UnifiedVisualizer()
        self.setup_page_config()
        self.initialize_session_state()
        self.check_backend_connection()

    def setup_page_config(self):
        """设置页面配置"""
        st.set_page_config(
            page_title="统一FJSP求解与可视化系统",
            page_icon="🏭",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def initialize_session_state(self):
        """初始化会话状态"""
        if 'instance' not in st.session_state:
            st.session_state.instance = None
        if 'instance_id' not in st.session_state:
            st.session_state.instance_id = None
        if 'results' not in st.session_state:
            st.session_state.results = {}
        if 'session_id' not in st.session_state:
            st.session_state.session_id = None
        if 'solving_progress' not in st.session_state:
            st.session_state.solving_progress = {}
        if 'real_time_data' not in st.session_state:
            st.session_state.real_time_data = {}
        if 'backend_mode' not in st.session_state:
            st.session_state.backend_mode = True  # 默认使用后端API

    def check_backend_connection(self):
        """检查后端连接"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                st.session_state.backend_available = True
            else:
                st.session_state.backend_available = False
        except:
            st.session_state.backend_available = False
    
    def run(self):
        """运行应用"""
        st.title("🏭 统一FJSP求解与可视化系统")
        st.markdown("---")

        # 侧边栏
        self.render_sidebar()

        # 主内容区域
        if st.session_state.instance is None:
            self.render_welcome_page()
        else:
            self.render_main_interface()
    
    def render_sidebar(self):
        """渲染侧边栏"""
        with st.sidebar:
            st.header("📋 问题设置")

            # 实例生成/加载
            st.subheader("1. 实例配置")

            instance_source = st.radio(
                "选择实例来源:",
                ["随机生成", "加载基准实例", "上传文件"]
            )

            if instance_source == "随机生成":
                self.render_random_instance_config()
            elif instance_source == "加载基准实例":
                self.render_benchmark_loader()
            else:
                self.render_file_uploader()

            st.markdown("---")

            # 算法配置
            if st.session_state.instance is not None:
                st.subheader("2. 算法配置")
                self.render_algorithm_config()

                st.markdown("---")

                # 可视化选项
                st.subheader("3. 可视化选项")
                self.render_visualization_config()
    
    def render_random_instance_config(self):
        """渲染随机实例配置"""
        col1, col2 = st.columns(2)

        with col1:
            num_jobs = st.slider("工件数量", 2, 10, 3)
            num_machines = st.slider("机器数量", 2, 8, 3)

        with col2:
            max_ops = st.slider("每个工件最大工序数", 1, 6, 3)
            flexibility = st.slider("柔性度", 0.1, 1.0, 0.5, 0.1)

        if st.button("生成实例", type="primary"):
            with st.spinner("正在生成实例..."):
                instance = InstanceGenerator.generate_random_fjsp(
                    num_jobs=num_jobs,
                    num_machines=num_machines,
                    max_operations_per_job=max_ops,
                    flexibility=flexibility
                )
                st.session_state.instance = instance
                st.session_state.results = {}
                st.success(f"已生成实例: {instance.name}")
                st.rerun()
    
    def render_benchmark_loader(self):
        """渲染基准实例加载器"""
        benchmark_instances = [
            "ft06", "ft10", "ft20", "la01", "la02", "la03",
            "abz5", "abz6", "orb01", "orb02"
        ]

        selected_benchmark = st.selectbox(
            "选择基准实例:",
            benchmark_instances
        )

        if st.button("加载基准实例", type="primary"):
            try:
                # 这里需要实际的基准实例加载逻辑
                # 暂时生成一个模拟实例
                instance = InstanceGenerator.generate_random_fjsp(6, 6, max_operations_per_job=4)
                instance.name = selected_benchmark
                st.session_state.instance = instance
                st.session_state.results = {}
                st.success(f"已加载基准实例: {selected_benchmark}")
                st.rerun()
            except Exception as e:
                st.error(f"加载基准实例失败: {e}")
    
    def render_file_uploader(self):
        """渲染文件上传器"""
        uploaded_file = st.file_uploader(
            "上传FJSP实例文件",
            type=['txt', 'fjs', 'json']
        )

        if uploaded_file is not None:
            if st.button("解析文件", type="primary"):
                try:
                    # 这里需要实际的文件解析逻辑
                    # 暂时生成一个模拟实例
                    instance = InstanceGenerator.generate_random_fjsp(4, 4, max_operations_per_job=3)
                    instance.name = uploaded_file.name
                    st.session_state.instance = instance
                    st.session_state.results = {}
                    st.success(f"已解析文件: {uploaded_file.name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"文件解析失败: {e}")
    
    def render_algorithm_config(self):
        """渲染算法配置"""
        st.write("**可用算法:**")

        # 算法选择
        use_jobshoplib = st.checkbox("JobShopLib求解器", value=True)
        use_evolutionary = st.checkbox("进化算法", value=True)
        use_reinforcement = st.checkbox("强化学习", value=False)

        # 参数配置
        with st.expander("算法参数"):
            if use_evolutionary:
                st.write("**进化算法:**")
                col1, col2 = st.columns(2)
                with col1:
                    pop_size = st.number_input("种群大小", 10, 200, 50)
                    generations = st.number_input("迭代代数", 10, 500, 100)
                with col2:
                    mutation_rate = st.slider("变异率", 0.01, 0.5, 0.1)
                    crossover_rate = st.slider("交叉率", 0.5, 1.0, 0.8)

            if use_jobshoplib:
                st.write("**JobShopLib:**")
                solver_type = st.selectbox(
                    "求解器类型",
                    ["OR-Tools", "调度规则", "模拟退火"]
                )
                time_limit = st.number_input("时间限制 (秒)", 1, 300, 60)
        
        # 求解按钮
        selected_algorithms = []
        if use_jobshoplib:
            selected_algorithms.append('jobshoplib')
        if use_evolutionary:
            selected_algorithms.append('evolutionary')
        if use_reinforcement:
            selected_algorithms.append('reinforcement')

        if st.button("🚀 开始求解", type="primary", disabled=not selected_algorithms):
            self.solve_problem(selected_algorithms, {
                'population_size': pop_size if use_evolutionary else 50,
                'generations': generations if use_evolutionary else 100,
                'mutation_rate': mutation_rate if use_evolutionary else 0.1,
                'crossover_rate': crossover_rate if use_evolutionary else 0.8,
                'solver_type': solver_type if use_jobshoplib else "OR-Tools",
                'time_limit': time_limit if use_jobshoplib else 60
            })
    
    def render_visualization_config(self):
        """渲染可视化配置"""
        st.write("**可视化选项:**")

        show_gantt = st.checkbox("甘特图", value=True)
        show_graph = st.checkbox("析取图", value=True)
        show_convergence = st.checkbox("收敛曲线", value=True)
        show_comparison = st.checkbox("算法对比", value=True)

        # 实时监控
        real_time_monitoring = st.checkbox("实时监控", value=True)

        return {
            'show_gantt': show_gantt,
            'show_graph': show_graph,
            'show_convergence': show_convergence,
            'show_comparison': show_comparison,
            'real_time_monitoring': real_time_monitoring
        }
    
    def render_welcome_page(self):
        """渲染欢迎页面"""
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("""
            ## 欢迎使用统一FJSP求解系统! 🎯

            本系统集成了多种最先进的柔性作业车间调度问题(FJSP)求解方法:

            ### 🔧 **集成库:**
            - **JobShopLib**: 约束编程、调度规则、元启发式算法
            - **Schlably**: 深度强化学习框架
            - **Graph-JSP-Env**: 基于图的强化学习环境

            ### 🧠 **算法:**
            - **进化算法**: 遗传算法及自定义算子
            - **强化学习**: DQN、PPO等强化学习方法
            - **约束编程**: OR-Tools CP-SAT求解器
            - **元启发式**: 模拟退火、局部搜索

            ### 📊 **可视化:**
            - 交互式甘特图
            - 析取图表示
            - 实时收敛监控
            - 算法性能对比

            ### 🚀 **开始使用:**
            1. 在侧边栏配置FJSP实例
            2. 选择要运行的算法
            3. 可视化和对比结果

            ---
            *从生成随机实例或加载基准问题开始吧!*
            """)
    
    def render_main_interface(self):
        """渲染主界面"""
        # 实例信息
        self.render_instance_info()

        # 结果展示
        if st.session_state.results:
            self.render_results()
        else:
            st.info("在侧边栏配置算法并点击'开始求解'来开始!")

    def render_instance_info(self):
        """渲染实例信息"""
        st.subheader("📊 问题实例")

        instance = st.session_state.instance

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("工件数", instance.num_jobs)
        with col2:
            st.metric("机器数", instance.num_machines)
        with col3:
            st.metric("工序数", len(instance.operations))
        with col4:
            flexibility = np.mean([len(op.machines) for op in instance.operations]) / instance.num_machines
            st.metric("平均柔性度", f"{flexibility:.2f}")
        
        # 实例详细信息
        with st.expander("实例详情"):
            # 创建操作表格
            operations_data = []
            for op in instance.operations:
                operations_data.append({
                    '工件': op.job_id,
                    '工序': op.operation_id,
                    '可用机器': ', '.join(map(str, op.machines)),
                    '加工时间': ', '.join(map(str, op.processing_times)),
                    '设置时间': op.setup_time
                })

            df = pd.DataFrame(operations_data)
            st.dataframe(df, use_container_width=True)
    
    def render_results(self):
        """渲染求解结果"""
        st.subheader("🎯 求解结果")

        results = st.session_state.results

        # 结果摘要
        if results:
            best_alg = min(results.keys(), key=lambda x: results[x].makespan)
            best_makespan = results[best_alg].makespan

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("最佳算法", best_alg)
            with col2:
                st.metric("最佳完工时间", f"{best_makespan:.2f}")
            with col3:
                avg_time = np.mean([r.computation_time for r in results.values()])
                st.metric("平均计算时间", f"{avg_time:.2f}秒")
            with col4:
                st.metric("测试算法数", len(results))
        
        # 可视化选项
        viz_config = self.render_visualization_config()
        
        # 渲染各种图表
        if viz_config['show_gantt'] and results:
            self.render_gantt_charts()
        
        if viz_config['show_graph']:
            self.render_disjunctive_graph()
        
        if viz_config['show_convergence'] and results:
            self.render_convergence_plots()
        
        if viz_config['show_comparison'] and len(results) > 1:
            self.render_algorithm_comparison()
    
    def render_gantt_charts(self):
        """渲染甘特图"""
        st.subheader("📅 甘特图")

        results = st.session_state.results
        instance = st.session_state.instance

        # 选择要显示的算法
        selected_alg = st.selectbox(
            "选择甘特图显示的算法:",
            list(results.keys())
        )

        if selected_alg in results:
            fig = self.visualizer.plot_gantt_chart(instance, results[selected_alg])
            st.plotly_chart(fig, use_container_width=True)

    def render_disjunctive_graph(self):
        """渲染析取图"""
        st.subheader("🕸️ 析取图")

        instance = st.session_state.instance

        layout_type = st.selectbox(
            "图布局:",
            ["弹簧布局", "层次布局", "随机布局"]
        )

        layout_map = {"弹簧布局": "spring", "层次布局": "hierarchical", "随机布局": "random"}
        fig = self.visualizer.plot_disjunctive_graph(instance, layout=layout_map[layout_type])
        st.plotly_chart(fig, use_container_width=True)

    def render_convergence_plots(self):
        """渲染收敛图"""
        st.subheader("📈 收敛分析")

        results = st.session_state.results

        # 过滤有收敛历史的结果
        convergence_results = {alg: result for alg, result in results.items()
                             if result.convergence_history}

        if convergence_results:
            fig = self.visualizer.plot_convergence_comparison(convergence_results)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("所选算法没有可用的收敛数据。")

    def render_algorithm_comparison(self):
        """渲染算法比较"""
        st.subheader("⚖️ 算法对比")

        results = st.session_state.results

        fig = self.visualizer.plot_algorithm_comparison(results)
        st.plotly_chart(fig, use_container_width=True)

        # 详细比较表格
        comparison_data = []
        for alg, result in results.items():
            comparison_data.append({
                '算法': alg,
                '完工时间': f"{result.makespan:.2f}",
                '计算时间(秒)': f"{result.computation_time:.2f}",
                '迭代次数': result.iterations,
                '相对性能': f"{(result.makespan / min(r.makespan for r in results.values()) - 1) * 100:.1f}%"
            })

        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)
    
    def solve_problem(self, algorithms: List[str], params: Dict[str, Any]):
        """求解问题"""
        instance = st.session_state.instance
        
        # 创建进度条和状态显示
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 实时监控回调
        def monitoring_callback(data):
            if 'generation' in data:
                progress = data['generation'] / params.get('generations', 100)
                progress_bar.progress(min(progress, 1.0))
                status_text.text(f"第{data['generation']}代: 最佳适应度 = {data['best_fitness']:.2f}")
            elif 'step' in data:
                status_text.text(f"强化学习步骤 {data['step']}: 奖励 = {data['reward']:.2f}")

        self.solver_manager.add_global_callback(monitoring_callback)

        try:
            with st.spinner("正在求解问题..."):
                results = self.solver_manager.solve_parallel(instance, algorithms, **params)
                st.session_state.results = results

                if results:
                    best_alg = min(results.keys(), key=lambda x: results[x].makespan)
                    best_makespan = results[best_alg].makespan
                    st.success(f"✅ 求解完成! 最佳解: {best_alg} 完工时间 {best_makespan:.2f}")
                else:
                    st.error("❌ 未找到解!")

                progress_bar.progress(1.0)
                status_text.text("求解完成!")

        except Exception as e:
            st.error(f"❌ 求解过程中出错: {e}")
        
        finally:
            # 清理回调
            self.solver_manager.callbacks.clear()
            for solver in self.solver_manager.solvers.values():
                solver.callbacks.clear()


# 应用入口
def main():
    app = StreamlitApp()
    app.run()


if __name__ == "__main__":
    main()
