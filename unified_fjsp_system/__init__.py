"""
Unified FJSP System - 统一的柔性作业车间调度问题求解与可视化系统

这个系统融合了多个优秀的开源库：
- JobShopLib: 约束编程、调度规则、元启发式
- Schlably: 深度强化学习框架  
- Graph-JSP-Env: 基于图的强化学习环境

主要功能：
- 统一的数据格式和接口
- 多种求解算法（进化算法、强化学习、约束编程）
- 丰富的可视化功能（甘特图、析取图、性能比较）
- Web界面和交互式仪表板
"""

__version__ = "1.0.0"
__author__ = "FJSP System Team"
__email__ = "contact@fjsp-system.com"

# 导入核心模块
try:
    from .core.data_adapter import (
        UnifiedFJSPInstance,
        UnifiedOperation, 
        DataAdapter,
        InstanceGenerator
    )
    
    from .algorithms.unified_solver import (
        UnifiedSolverManager,
        SolutionResult,
        BaseSolver
    )
    
    from .visualization.unified_visualizer import (
        UnifiedVisualizer
    )
    
    __all__ = [
        'UnifiedFJSPInstance',
        'UnifiedOperation',
        'DataAdapter', 
        'InstanceGenerator',
        'UnifiedSolverManager',
        'SolutionResult',
        'BaseSolver',
        'UnifiedVisualizer'
    ]
    
except ImportError as e:
    # 如果导入失败，提供友好的错误信息
    import warnings
    warnings.warn(f"Some modules could not be imported: {e}")
    __all__ = []


def get_version():
    """获取版本信息"""
    return __version__


def check_dependencies():
    """检查依赖包是否可用"""
    dependencies = {
        'required': {
            'numpy': 'NumPy',
            'pandas': 'Pandas', 
            'matplotlib': 'Matplotlib',
            'plotly': 'Plotly',
            'networkx': 'NetworkX',
            'streamlit': 'Streamlit'
        },
        'optional': {
            'job_shop_lib': 'JobShopLib',
            'graph_jsp_env': 'Graph-JSP-Env',
            'ortools': 'OR-Tools',
            'gymnasium': 'Gymnasium',
            'stable_baselines3': 'Stable Baselines3'
        }
    }
    
    status = {
        'required': {},
        'optional': {}
    }
    
    for category, packages in dependencies.items():
        for package, name in packages.items():
            try:
                __import__(package)
                status[category][package] = True
            except ImportError:
                status[category][package] = False
    
    return status


def print_system_info():
    """打印系统信息"""
    print(f"Unified FJSP System v{__version__}")
    print("=" * 40)
    
    status = check_dependencies()
    
    print("\n📦 Required Dependencies:")
    for package, available in status['required'].items():
        icon = "✅" if available else "❌"
        print(f"  {icon} {package}")
    
    print("\n📦 Optional Dependencies:")
    for package, available in status['optional'].items():
        icon = "✅" if available else "⚠️ "
        print(f"  {icon} {package}")
    
    missing_required = [pkg for pkg, avail in status['required'].items() if not avail]
    if missing_required:
        print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
        print("   Install with: pip install " + " ".join(missing_required))
    
    missing_optional = [pkg for pkg, avail in status['optional'].items() if not avail]
    if missing_optional:
        print(f"\n⚠️  Missing optional packages: {', '.join(missing_optional)}")
        print("   Install with: pip install " + " ".join(missing_optional))
    
    print("\n🚀 Quick Start:")
    print("   python run_web_app.py              # Launch web interface")
    print("   python examples/basic_usage.py     # Run basic example")


if __name__ == "__main__":
    print_system_info()
