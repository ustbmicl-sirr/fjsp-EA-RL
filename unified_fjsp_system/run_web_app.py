#!/usr/bin/env python3
"""
启动脚本 - 运行统一FJSP系统Web应用
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_dependencies():
    """检查必要的依赖"""
    required_packages = [
        'streamlit',
        'plotly', 
        'pandas',
        'numpy',
        'networkx',
        'matplotlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True


def check_optional_dependencies():
    """检查可选依赖"""
    optional_packages = {
        'job_shop_lib': 'JobShopLib integration',
        'graph_jsp_env': 'Graph-JSP-Env integration', 
        'ortools': 'OR-Tools constraint programming',
        'gymnasium': 'Reinforcement learning environments',
        'stable_baselines3': 'RL algorithms'
    }
    
    available_packages = []
    missing_packages = []
    
    for package, description in optional_packages.items():
        try:
            __import__(package)
            available_packages.append((package, description))
        except ImportError:
            missing_packages.append((package, description))
    
    if available_packages:
        print("✅ Available optional packages:")
        for package, desc in available_packages:
            print(f"   - {package}: {desc}")
    
    if missing_packages:
        print("\n⚠️  Missing optional packages (some features may be limited):")
        for package, desc in missing_packages:
            print(f"   - {package}: {desc}")
        print("\n💡 Install optional packages with:")
        print("   pip install job-shop-lib graph-jsp-env ortools gymnasium stable-baselines3")


def run_streamlit_app(port=8501, host='localhost'):
    """运行Streamlit应用"""
    app_path = Path(__file__).parent / 'web' / 'streamlit_app.py'
    
    if not app_path.exists():
        print(f"❌ Streamlit app not found at: {app_path}")
        return False
    
    print(f"🚀 Starting Streamlit app on http://{host}:{port}")
    print("📱 The app will open in your default browser automatically.")
    print("🛑 Press Ctrl+C to stop the server.")
    
    try:
        cmd = [
            sys.executable, '-m', 'streamlit', 'run',
            str(app_path),
            '--server.port', str(port),
            '--server.address', host,
            '--server.headless', 'false',
            '--browser.gatherUsageStats', 'false'
        ]
        
        subprocess.run(cmd, check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit app: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Streamlit app stopped by user.")
        return True


def run_example():
    """运行基础示例"""
    example_path = Path(__file__).parent / 'examples' / 'basic_usage.py'
    
    if not example_path.exists():
        print(f"❌ Example not found at: {example_path}")
        return False
    
    print("🧪 Running basic usage example...")
    
    try:
        subprocess.run([sys.executable, str(example_path)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run example: {e}")
        return False


def setup_environment():
    """设置环境"""
    # 添加当前目录到Python路径
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # 设置环境变量
    os.environ['PYTHONPATH'] = str(current_dir)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Unified FJSP System Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_web_app.py                    # Run web app on default port
  python run_web_app.py --port 8080        # Run web app on port 8080
  python run_web_app.py --example          # Run basic usage example
  python run_web_app.py --check            # Check dependencies only
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8501,
        help='Port for Streamlit app (default: 8501)'
    )
    
    parser.add_argument(
        '--host',
        default='localhost',
        help='Host for Streamlit app (default: localhost)'
    )
    
    parser.add_argument(
        '--example', '-e',
        action='store_true',
        help='Run basic usage example instead of web app'
    )
    
    parser.add_argument(
        '--check', '-c',
        action='store_true',
        help='Check dependencies only'
    )
    
    args = parser.parse_args()
    
    print("🏭 Unified FJSP System Launcher")
    print("=" * 40)
    
    # 设置环境
    setup_environment()
    
    # 检查依赖
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        return 1
    
    print("✅ All required dependencies are available!")
    
    # 检查可选依赖
    print("\n🔍 Checking optional dependencies...")
    check_optional_dependencies()
    
    if args.check:
        print("\n✅ Dependency check completed!")
        return 0
    
    if args.example:
        print("\n🧪 Running example...")
        success = run_example()
        return 0 if success else 1
    
    # 运行Web应用
    print("\n🌐 Starting web application...")
    success = run_streamlit_app(args.port, args.host)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
