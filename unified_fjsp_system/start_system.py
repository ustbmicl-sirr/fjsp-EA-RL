#!/usr/bin/env python3
"""
统一FJSP系统启动脚本 (Python版本)
跨平台支持，自动管理conda环境、检查依赖、启动前后端服务
"""
import os
import sys
import subprocess
import time
import signal
import platform
import json
import requests
from pathlib import Path
from typing import List, Optional

# 配置
ENV_NAME = "fjsp-system"
BACKEND_PORT = 5000
FRONTEND_PORT = 8501
BACKEND_PID_FILE = "/tmp/fjsp_backend.pid" if platform.system() != "Windows" else os.path.join(os.environ.get("TEMP", ""), "fjsp_backend.pid")
FRONTEND_PID_FILE = "/tmp/fjsp_frontend.pid" if platform.system() != "Windows" else os.path.join(os.environ.get("TEMP", ""), "fjsp_frontend.pid")

# 颜色定义
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color
    
    @classmethod
    def disable_on_windows(cls):
        """在Windows上禁用颜色（除非支持ANSI）"""
        if platform.system() == "Windows":
            try:
                # 尝试启用Windows 10的ANSI支持
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                # 如果失败，禁用颜色
                for attr in dir(cls):
                    if not attr.startswith('_') and attr != 'disable_on_windows':
                        setattr(cls, attr, '')

Colors.disable_on_windows()

def log_info(msg: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")

def log_success(msg: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {msg}")

def log_warning(msg: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {msg}")

def log_error(msg: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")

def log_step(msg: str):
    print(f"{Colors.PURPLE}[STEP]{Colors.NC} {msg}")

def run_command(cmd: List[str], check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    """运行命令"""
    try:
        if capture_output:
            return subprocess.run(cmd, check=check, capture_output=True, text=True)
        else:
            return subprocess.run(cmd, check=check)
    except subprocess.CalledProcessError as e:
        if check:
            log_error(f"命令执行失败: {' '.join(cmd)}")
            log_error(f"错误信息: {e}")
            raise
        return e

def check_conda() -> bool:
    """检查conda是否安装"""
    log_step("检查conda环境...")
    
    try:
        result = run_command(["conda", "--version"], capture_output=True)
        log_success(f"conda已安装: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_error("conda未安装，请先安装Anaconda或Miniconda")
        log_info("下载地址: https://docs.conda.io/en/latest/miniconda.html")
        return False

def check_conda_env() -> bool:
    """检查conda环境是否存在"""
    try:
        result = run_command(["conda", "env", "list"], capture_output=True)
        return ENV_NAME in result.stdout
    except subprocess.CalledProcessError:
        return False

def create_conda_env():
    """创建conda环境"""
    log_step("设置conda环境...")
    
    if check_conda_env():
        log_info(f"conda环境 '{ENV_NAME}' 已存在")
        return
    
    log_info(f"创建conda环境 '{ENV_NAME}'...")
    
    env_file = Path("environment.yml")
    if env_file.exists():
        run_command(["conda", "env", "create", "-f", "environment.yml"])
        log_success("从environment.yml创建环境成功")
    else:
        log_warning("environment.yml不存在，使用基础配置创建环境")
        run_command(["conda", "create", "-n", ENV_NAME, "python=3.9", "-y"])
        log_success("创建基础环境成功")

def activate_conda_env():
    """激活conda环境（通过修改PATH）"""
    log_step("准备conda环境...")
    
    # 获取conda环境路径
    try:
        result = run_command(["conda", "info", "--envs"], capture_output=True)
        for line in result.stdout.split('\n'):
            if ENV_NAME in line:
                env_path = line.split()[-1]
                if platform.system() == "Windows":
                    python_path = os.path.join(env_path, "python.exe")
                    scripts_path = os.path.join(env_path, "Scripts")
                else:
                    python_path = os.path.join(env_path, "bin", "python")
                    scripts_path = os.path.join(env_path, "bin")
                
                # 修改PATH
                os.environ["PATH"] = f"{scripts_path}{os.pathsep}{os.environ['PATH']}"
                
                # 验证Python路径
                if os.path.exists(python_path):
                    log_success(f"环境准备成功: {env_path}")
                    return python_path
                break
        
        log_error("无法找到conda环境路径")
        return None
        
    except subprocess.CalledProcessError:
        log_error("获取conda环境信息失败")
        return None

def check_dependencies() -> bool:
    """检查Python依赖"""
    log_step("检查Python依赖...")
    
    required_packages = [
        "numpy", "pandas", "matplotlib", "plotly", "streamlit",
        "flask", "flask_cors", "flask_socketio", "networkx", "requests"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            subprocess.run([sys.executable, "-c", f"import {package}"], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing_packages.append(package)
    
    if not missing_packages:
        log_success("所有必需依赖已安装")
        return True
    else:
        log_warning(f"缺少以下依赖: {', '.join(missing_packages)}")
        return False

def install_dependencies():
    """安装依赖"""
    log_step("安装Python依赖...")
    
    # 更新pip
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # 安装基础依赖
    log_info("安装基础依赖...")
    basic_deps = [
        "numpy", "pandas", "matplotlib", "plotly", "streamlit",
        "flask", "flask-cors", "flask-socketio", "networkx", "requests"
    ]
    run_command([sys.executable, "-m", "pip", "install"] + basic_deps)
    
    # 安装可选依赖
    log_info("安装可选依赖...")
    optional_deps = [
        "job-shop-lib", "ortools", "gymnasium", "stable-baselines3",
        "loguru", "tqdm", "pytest", "black", "flake8"
    ]
    
    for dep in optional_deps:
        try:
            run_command([sys.executable, "-m", "pip", "install", dep], check=False)
        except:
            log_warning(f"可选依赖 {dep} 安装失败，跳过")
    
    log_success("依赖安装完成")

def check_port(port: int) -> bool:
    """检查端口是否被占用"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    except:
        return False

def kill_process_on_port(port: int):
    """杀死占用端口的进程"""
    if platform.system() == "Windows":
        try:
            # Windows: 使用netstat和taskkill
            result = subprocess.run(
                ["netstat", "-ano"], capture_output=True, text=True
            )
            for line in result.stdout.split('\n'):
                if f":{port}" in line and "LISTENING" in line:
                    pid = line.split()[-1]
                    subprocess.run(["taskkill", "/F", "/PID", pid], check=False)
        except:
            pass
    else:
        try:
            # Unix: 使用lsof和kill
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], capture_output=True, text=True
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(["kill", "-9", pid], check=False)
        except:
            pass

def stop_services():
    """停止现有服务"""
    log_step("停止现有服务...")
    
    # 停止端口占用的进程
    if check_port(BACKEND_PORT):
        log_info(f"释放后端端口 {BACKEND_PORT}")
        kill_process_on_port(BACKEND_PORT)
    
    if check_port(FRONTEND_PORT):
        log_info(f"释放前端端口 {FRONTEND_PORT}")
        kill_process_on_port(FRONTEND_PORT)
    
    time.sleep(2)

def start_backend() -> Optional[subprocess.Popen]:
    """启动后端服务"""
    log_step("启动后端API服务...")
    
    if check_port(BACKEND_PORT):
        log_error(f"端口 {BACKEND_PORT} 仍被占用")
        return None
    
    # 启动Flask后端
    backend_script = Path("web/backend/flask_api.py")
    if not backend_script.exists():
        log_error("后端脚本不存在")
        return None
    
    log_file = Path("/tmp/fjsp_backend.log") if platform.system() != "Windows" else Path(os.environ.get("TEMP", "")) / "fjsp_backend.log"
    
    with open(log_file, 'w') as f:
        process = subprocess.Popen(
            [sys.executable, str(backend_script)],
            stdout=f, stderr=f,
            cwd=Path.cwd()
        )
    
    # 等待后端启动
    log_info("等待后端服务启动...")
    for i in range(30):
        try:
            response = requests.get(f"http://localhost:{BACKEND_PORT}/api/health", timeout=1)
            if response.status_code == 200:
                log_success(f"后端服务启动成功 (PID: {process.pid}, Port: {BACKEND_PORT})")
                return process
        except:
            pass
        time.sleep(1)
    
    log_error("后端服务启动失败")
    process.terminate()
    return None

def start_frontend() -> Optional[subprocess.Popen]:
    """启动前端服务"""
    log_step("启动前端Web应用...")
    
    if check_port(FRONTEND_PORT):
        log_error(f"端口 {FRONTEND_PORT} 仍被占用")
        return None
    
    frontend_script = Path("web/streamlit_app.py")
    if not frontend_script.exists():
        log_error("前端脚本不存在")
        return None
    
    log_file = Path("/tmp/fjsp_frontend.log") if platform.system() != "Windows" else Path(os.environ.get("TEMP", "")) / "fjsp_frontend.log"
    
    with open(log_file, 'w') as f:
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", str(frontend_script),
            "--server.port", str(FRONTEND_PORT),
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ], stdout=f, stderr=f, cwd=Path.cwd())
    
    # 等待前端启动
    log_info("等待前端服务启动...")
    for i in range(30):
        if check_port(FRONTEND_PORT):
            log_success(f"前端服务启动成功 (PID: {process.pid}, Port: {FRONTEND_PORT})")
            return process
        time.sleep(1)
    
    log_error("前端服务启动失败")
    process.terminate()
    return None

def show_status():
    """显示服务状态"""
    print()
    print(f"{Colors.CYAN}========================================{Colors.NC}")
    print(f"{Colors.CYAN}🏭 统一FJSP系统启动完成{Colors.NC}")
    print(f"{Colors.CYAN}========================================{Colors.NC}")
    print()
    print(f"{Colors.GREEN}📡 后端API服务:{Colors.NC} http://localhost:{BACKEND_PORT}")
    print(f"{Colors.GREEN}🌐 前端Web应用:{Colors.NC} http://localhost:{FRONTEND_PORT}")
    print()
    print(f"{Colors.YELLOW}📋 API文档:{Colors.NC}")
    print(f"   健康检查: http://localhost:{BACKEND_PORT}/api/health")
    print(f"   创建实例: POST http://localhost:{BACKEND_PORT}/api/instances")
    print(f"   求解问题: POST http://localhost:{BACKEND_PORT}/api/solve")
    print()
    print(f"{Colors.YELLOW}🛑 停止服务:{Colors.NC}")
    print(f"   按 Ctrl+C 或运行: python {sys.argv[0]} stop")
    print()
    print(f"{Colors.CYAN}========================================{Colors.NC}")

def main():
    """主函数"""
    print(f"{Colors.CYAN}")
    print("🏭 统一FJSP求解与可视化系统")
    print("==================================")
    print(f"{Colors.NC}")
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "stop":
            stop_services()
            log_success("服务已停止")
            return
        elif sys.argv[1] == "restart":
            stop_services()
            time.sleep(2)
        elif sys.argv[1] not in ["start", ""]:
            print("用法: python start_system.py [start|stop|restart]")
            return
    
    # 检查conda
    if not check_conda():
        return
    
    # 创建和准备环境
    create_conda_env()
    python_path = activate_conda_env()
    if not python_path:
        return
    
    # 检查和安装依赖
    if not check_dependencies():
        install_dependencies()
    
    # 停止现有服务
    stop_services()
    
    # 启动服务
    backend_process = start_backend()
    if not backend_process:
        return
    
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        return
    
    # 显示状态
    show_status()
    
    # 等待中断信号
    def signal_handler(sig, frame):
        log_info("正在停止服务...")
        backend_process.terminate()
        frontend_process.terminate()
        stop_services()
        log_success("服务已停止")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # 监控服务状态
        while True:
            time.sleep(10)
            if backend_process.poll() is not None:
                log_error("后端服务异常停止")
                break
            if frontend_process.poll() is not None:
                log_error("前端服务异常停止")
                break
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
