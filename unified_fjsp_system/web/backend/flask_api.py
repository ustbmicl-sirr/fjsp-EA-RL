"""
Flask后端API - 提供RESTful接口
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
import json
import uuid
import threading
import time
from datetime import datetime
from typing import Dict, Any
import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 容错导入
try:
    from core.data_adapter import InstanceGenerator, DataAdapter, UnifiedFJSPInstance
    from algorithms.unified_solver import UnifiedSolverManager, SolutionResult
    from visualization.unified_visualizer import UnifiedVisualizer
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"警告: 核心模块导入失败: {e}")
    print("将使用简化模式运行")
    MODULES_AVAILABLE = False

    # 创建简化的类
    class InstanceGenerator:
        @staticmethod
        def generate_random_fjsp(num_jobs, num_machines, max_operations_per_job=3, **kwargs):
            # 创建简化的实例对象
            class SimpleInstance:
                def __init__(self, name, num_jobs, num_machines):
                    self.name = name
                    self.num_jobs = num_jobs
                    self.num_machines = num_machines
                    self.operations = []
                    self.metadata = {}

                    # 生成简化的工序
                    for job_id in range(num_jobs):
                        for op_id in range(max_operations_per_job):
                            op = type('Operation', (), {
                                'job_id': job_id,
                                'operation_id': op_id,
                                'machines': [0, 1] if num_machines > 1 else [0],
                                'processing_times': [5, 6] if num_machines > 1 else [5],
                                'setup_time': 0
                            })()
                            self.operations.append(op)

            return SimpleInstance(f"简化实例_{num_jobs}x{num_machines}", num_jobs, num_machines)

    class SolutionResult:
        """简化的求解结果"""
        def __init__(self, makespan, computation_time=0, iterations=0, convergence_history=None):
            self.makespan = makespan
            self.computation_time = computation_time
            self.iterations = iterations
            self.convergence_history = convergence_history or []
            self.schedule = {"simplified": True}
            self.objectives = {"makespan": makespan}
            self.algorithm = "Simplified"

    class UnifiedSolverManager:
        def __init__(self):
            self.callbacks = []

        def add_global_callback(self, callback):
            """添加全局回调"""
            self.callbacks.append(callback)

        def solve_parallel(self, instance, algorithms, **kwargs):
            """简化的并行求解"""
            import random
            results = {}
            for alg in algorithms:
                # 模拟求解
                makespan = random.uniform(50, 200)
                results[alg] = SolutionResult(
                    makespan=makespan,
                    computation_time=random.uniform(0.1, 1.0),
                    iterations=100,
                    convergence_history=[makespan] * 10
                )
            return results

    class UnifiedVisualizer:
        def generate_dashboard_html(self, *args, **kwargs):
            return "<html><body><h1>简化可视化</h1></body></html>"

        def plot_disjunctive_graph(self, instance, layout='spring'):
            """简化的析取图可视化"""
            import plotly.graph_objects as go
            import networkx as nx

            # 创建简化的析取图
            G = nx.DiGraph()

            # 添加节点
            for i, op in enumerate(instance.operations):
                node_id = f"J{op.job_id}_O{op.operation_id}"
                G.add_node(node_id, job_id=op.job_id, operation_id=op.operation_id)

            # 添加简化的边
            nodes = list(G.nodes())
            for i in range(len(nodes)-1):
                G.add_edge(nodes[i], nodes[i+1])

            # 布局
            if layout == 'spring':
                pos = nx.spring_layout(G)
            elif layout == 'hierarchical':
                pos = nx.spring_layout(G)  # 简化为spring布局
            else:
                pos = nx.random_layout(G)

            # 创建Plotly图
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            node_x = []
            node_y = []
            node_text = []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)

            fig = go.Figure()

            # 添加边
            fig.add_trace(go.Scatter(x=edge_x, y=edge_y,
                                   line=dict(width=2, color='blue'),
                                   hoverinfo='none',
                                   mode='lines'))

            # 添加节点
            fig.add_trace(go.Scatter(x=node_x, y=node_y,
                                   mode='markers+text',
                                   text=node_text,
                                   textposition="middle center",
                                   hoverinfo='text',
                                   marker=dict(size=20, color='lightblue')))

            fig.update_layout(
                title=f"析取图 - {instance.name}",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[dict(
                    text="简化析取图可视化",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color='gray', size=12)
                )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )

            return fig

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fjsp_system_secret_key'
CORS(app)  # 允许跨域请求
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局存储
instances = {}  # 存储FJSP实例
results = {}    # 存储求解结果
sessions = {}   # 存储会话信息

solver_manager = UnifiedSolverManager()
visualizer = UnifiedVisualizer()


class ProgressTracker:
    """进度跟踪器"""
    def __init__(self, session_id: str, solver_manager):
        self.session_id = session_id
        self.progress_data = []
        self.solver_manager = solver_manager

    def __call__(self, data: Dict[str, Any]):
        """进度回调函数"""
        data['timestamp'] = datetime.now().isoformat()
        self.progress_data.append(data)

        # 通过WebSocket发送实时进度
        socketio.emit('progress_update', {
            'session_id': self.session_id,
            'data': data
        }, room=self.session_id)

    def cleanup(self):
        """清理回调函数"""
        if self.solver_manager and hasattr(self.solver_manager, 'callbacks'):
            if self in self.solver_manager.callbacks:
                self.solver_manager.callbacks.remove(self)
            # 清理各个求解器的回调
            if hasattr(self.solver_manager, 'solvers'):
                for solver in self.solver_manager.solvers.values():
                    if hasattr(solver, 'callbacks') and self in solver.callbacks:
                        solver.callbacks.remove(self)


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/instances', methods=['POST'])
def create_instance():
    """创建FJSP实例"""
    try:
        data = request.get_json()
        instance_type = data.get('type', 'random')

        if instance_type == 'random':
            # 参数验证
            num_jobs = data.get('num_jobs', 3)
            num_machines = data.get('num_machines', 3)
            max_operations_per_job = data.get('max_operations_per_job', 3)
            flexibility = data.get('flexibility', 0.5)

            # 检查参数合法性
            if not (1 <= num_jobs <= 1000):
                return jsonify({'error': 'num_jobs must be between 1 and 1000'}), 400
            if not (1 <= num_machines <= 100):
                return jsonify({'error': 'num_machines must be between 1 and 100'}), 400
            if not (1 <= max_operations_per_job <= 50):
                return jsonify({'error': 'max_operations_per_job must be between 1 and 50'}), 400
            if not (0 <= flexibility <= 1):
                return jsonify({'error': 'flexibility must be between 0 and 1'}), 400

            instance = InstanceGenerator.generate_random_fjsp(
                num_jobs=num_jobs,
                num_machines=num_machines,
                max_operations_per_job=max_operations_per_job,
                flexibility=flexibility
            )
        elif instance_type == 'benchmark':
            benchmark_name = data.get('name', 'ft06')
            if not hasattr(InstanceGenerator, 'load_benchmark'):
                return jsonify({'error': 'Benchmark loading not supported in simplified mode'}), 400
            instance = InstanceGenerator.load_benchmark(benchmark_name)
        else:
            return jsonify({'error': 'Unsupported instance type'}), 400

        instance_id = str(uuid.uuid4())
        instances[instance_id] = instance

        return jsonify({
            'instance_id': instance_id,
            'name': instance.name,
            'num_jobs': instance.num_jobs,
            'num_machines': instance.num_machines,
            'num_operations': len(instance.operations),
            'created_at': datetime.now().isoformat()
        })

    except ValueError as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/instances/<instance_id>', methods=['GET'])
def get_instance(instance_id):
    """获取FJSP实例详情"""
    if instance_id not in instances:
        return jsonify({'error': 'Instance not found'}), 404
    
    instance = instances[instance_id]
    
    # 构建操作详情
    operations_data = []
    for op in instance.operations:
        operations_data.append({
            'job_id': op.job_id,
            'operation_id': op.operation_id,
            'machines': op.machines,
            'processing_times': op.processing_times,
            'setup_time': op.setup_time
        })
    
    return jsonify({
        'instance_id': instance_id,
        'name': instance.name,
        'num_jobs': instance.num_jobs,
        'num_machines': instance.num_machines,
        'operations': operations_data,
        'metadata': instance.metadata or {}
    })


@app.route('/api/instances', methods=['GET'])
def list_instances():
    """列出所有实例"""
    instance_list = []
    for instance_id, instance in instances.items():
        instance_list.append({
            'instance_id': instance_id,
            'name': instance.name,
            'num_jobs': instance.num_jobs,
            'num_machines': instance.num_machines,
            'num_operations': len(instance.operations)
        })
    
    return jsonify({'instances': instance_list})


@app.route('/api/solve', methods=['POST'])
def solve_problem():
    """求解FJSP问题"""
    try:
        data = request.get_json()
        instance_id = data.get('instance_id')
        algorithms = data.get('algorithms', ['evolutionary'])
        params = data.get('parameters', {})

        if instance_id not in instances:
            return jsonify({'error': 'Instance not found'}), 404

        instance = instances[instance_id]
        session_id = str(uuid.uuid4())

        # 创建进度跟踪器
        progress_tracker = ProgressTracker(session_id, solver_manager)
        solver_manager.add_global_callback(progress_tracker)

        # 设置超时时间（默认5分钟）
        timeout = params.get('timeout', 300)

        def solve_async():
            """异步求解"""
            try:
                # 使用超时控制
                solve_results = {}
                start_time = time.time()

                solve_results = solver_manager.solve_parallel(
                    instance, algorithms, **params
                )

                # 检查是否超时
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"求解超时 ({timeout}秒)")

                results[session_id] = solve_results

                # 通知求解完成
                socketio.emit('solve_complete', {
                    'session_id': session_id,
                    'success': True,
                    'results_summary': {
                        alg: {
                            'makespan': result.makespan,
                            'computation_time': result.computation_time,
                            'iterations': result.iterations
                        } for alg, result in solve_results.items() if result is not None
                    }
                }, room=session_id)

            except Exception as e:
                socketio.emit('solve_complete', {
                    'session_id': session_id,
                    'success': False,
                    'error': str(e)
                }, room=session_id)
            finally:
                # 清理回调函数
                progress_tracker.cleanup()
                # 更新会话状态
                if session_id in sessions:
                    sessions[session_id]['status'] = 'completed'

        # 启动异步求解
        thread = threading.Thread(target=solve_async)
        thread.daemon = True
        thread.start()

        sessions[session_id] = {
            'instance_id': instance_id,
            'algorithms': algorithms,
            'parameters': params,
            'status': 'running',
            'created_at': datetime.now().isoformat(),
            'tracker': progress_tracker
        }

        return jsonify({
            'session_id': session_id,
            'status': 'started',
            'message': 'Solving started, use WebSocket to monitor progress'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/results/<session_id>', methods=['GET'])
def get_results(session_id):
    """获取求解结果"""
    if session_id not in results:
        return jsonify({'error': 'Results not found'}), 404
    
    solve_results = results[session_id]
    
    results_data = {}
    for alg, result in solve_results.items():
        results_data[alg] = {
            'makespan': result.makespan,
            'computation_time': result.computation_time,
            'iterations': result.iterations,
            'algorithm': result.algorithm,
            'objectives': result.objectives,
            'convergence_history': result.convergence_history
        }
    
    return jsonify({
        'session_id': session_id,
        'results': results_data
    })


@app.route('/api/instances/<instance_id>/visualize/<viz_type>', methods=['GET'])
def generate_instance_visualization(instance_id, viz_type):
    """生成基于实例的可视化图表（不需要求解结果）"""
    if instance_id not in instances:
        return jsonify({'error': 'Instance not found'}), 404

    instance = instances[instance_id]
    layout = request.args.get('layout', 'spring')

    try:
        if viz_type == 'disjunctive_graph':
            fig = visualizer.plot_disjunctive_graph(instance, layout=layout)
        else:
            return jsonify({'error': 'Unsupported visualization type for instance'}), 400

        # 返回HTML格式
        html_content = fig.to_html(include_plotlyjs=True)
        return html_content, 200, {'Content-Type': 'text/html'}

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/visualize/<session_id>/<viz_type>', methods=['GET'])
def generate_visualization(session_id, viz_type):
    """生成可视化图表"""
    if session_id not in results:
        return jsonify({'error': 'Results not found'}), 404

    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404

    instance_id = sessions[session_id]['instance_id']
    if instance_id not in instances:
        return jsonify({'error': 'Instance not found'}), 404

    instance = instances[instance_id]
    solve_results = results[session_id]

    try:
        # 过滤掉None结果
        valid_results = {alg: res for alg, res in solve_results.items() if res is not None}

        if not valid_results:
            return jsonify({'error': 'No valid results available'}), 400

        if viz_type == 'gantt':
            # 选择最佳结果
            best_alg = min(valid_results.keys(), key=lambda x: valid_results[x].makespan)
            best_result = valid_results[best_alg]

            # 验证结果格式
            if not hasattr(best_result, 'schedule'):
                return jsonify({'error': 'Invalid result format'}), 400

            fig = visualizer.plot_gantt_chart(instance, best_result)

        elif viz_type == 'disjunctive_graph':
            fig = visualizer.plot_disjunctive_graph(instance)

        elif viz_type == 'convergence':
            fig = visualizer.plot_convergence_comparison(valid_results)

        elif viz_type == 'comparison':
            fig = visualizer.plot_algorithm_comparison(valid_results)

        elif viz_type == 'dashboard':
            fig = visualizer.create_dashboard(instance, valid_results)

        else:
            return jsonify({'error': 'Unsupported visualization type'}), 400

        # 转换为JSON格式
        fig_json = fig.to_json()

        return jsonify({
            'session_id': session_id,
            'visualization_type': viz_type,
            'figure': json.loads(fig_json)
        })

    except AttributeError as e:
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/<session_id>/<format>', methods=['GET'])
def export_results(session_id, format):
    """导出结果"""
    if session_id not in results:
        return jsonify({'error': 'Results not found'}), 404
    
    solve_results = results[session_id]
    
    try:
        if format == 'json':
            export_data = {
                'session_id': session_id,
                'export_time': datetime.now().isoformat(),
                'results': {
                    alg: {
                        'makespan': result.makespan,
                        'computation_time': result.computation_time,
                        'iterations': result.iterations,
                        'convergence_history': result.convergence_history
                    } for alg, result in solve_results.items()
                }
            }
            
            filename = f'fjsp_results_{session_id[:8]}.json'
            filepath = f'/tmp/{filename}'
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return send_file(filepath, as_attachment=True, download_name=filename)
            
        else:
            return jsonify({'error': 'Unsupported export format'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to FJSP solver'})


@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    print(f'Client disconnected: {request.sid}')


@socketio.on('join_session')
def handle_join_session(data):
    """加入会话房间"""
    session_id = data.get('session_id')
    if session_id:
        join_room(session_id)
        emit('joined_session', {'session_id': session_id})


if __name__ == '__main__':
    print("🚀 Starting FJSP Backend API Server...")
    print("📡 API Endpoints:")
    print("   GET  /api/health")
    print("   POST /api/instances")
    print("   GET  /api/instances/<id>")
    print("   POST /api/solve")
    print("   GET  /api/results/<session_id>")
    print("   GET  /api/visualize/<session_id>/<type>")
    print("🔌 WebSocket: Real-time progress updates")
    print("🌐 Server running on http://localhost:5000")

    socketio.run(app, host='0.0.0.0', port=5001, debug=False, allow_unsafe_werkzeug=True)
