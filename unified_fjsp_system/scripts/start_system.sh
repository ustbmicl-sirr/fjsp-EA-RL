#!/bin/bash

# 统一FJSP系统启动脚本
# 自动管理conda环境、检查依赖、启动前后端服务

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
ENV_NAME="fjsp-system"
BACKEND_PORT=5001
FRONTEND_PORT=8501
BACKEND_PID_FILE="/tmp/fjsp_backend.pid"
FRONTEND_PID_FILE="/tmp/fjsp_frontend.pid"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 检查conda是否安装
check_conda() {
    log_step "检查conda环境..."
    
    if ! command -v conda &> /dev/null; then
        log_error "conda未安装，请先安装Anaconda或Miniconda"
        echo "下载地址: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi
    
    log_success "conda已安装: $(conda --version)"
}

# 检查并创建conda环境
setup_conda_env() {
    log_step "设置conda环境..."
    
    # 检查环境是否存在
    if conda env list | grep -q "^${ENV_NAME} "; then
        log_info "conda环境 '${ENV_NAME}' 已存在"
    else
        log_info "创建conda环境 '${ENV_NAME}'..."
        
        if [ -f "environment.yml" ]; then
            log_info "从environment.yml创建环境..."
            conda env create -f environment.yml
            if [ $? -eq 0 ]; then
                log_success "从environment.yml创建环境成功"
            else
                log_warning "environment.yml创建失败，使用基础配置"
                conda create -n ${ENV_NAME} python=3.10 numpy pandas matplotlib plotly flask networkx requests -y
                log_success "创建基础环境成功"
            fi
        else
            log_warning "environment.yml不存在，使用基础配置创建环境"
            conda create -n ${ENV_NAME} python=3.10 numpy pandas matplotlib plotly flask networkx requests -y
            log_success "创建基础环境成功"
        fi
    fi
}

# 激活conda环境
activate_conda_env() {
    log_step "激活conda环境..."
    
    # 初始化conda（如果需要）
    eval "$(conda shell.bash hook)"
    
    # 激活环境
    conda activate ${ENV_NAME}
    
    if [ "$CONDA_DEFAULT_ENV" = "${ENV_NAME}" ]; then
        log_success "环境激活成功: ${CONDA_DEFAULT_ENV}"
    else
        log_error "环境激活失败"
        exit 1
    fi
}

# 检查Python依赖
check_dependencies() {
    log_step "检查Python依赖..."
    
    # 必需的包列表
    required_packages=(
        "numpy"
        "pandas" 
        "matplotlib"
        "plotly"
        "streamlit"
        "flask"
        "flask_cors"
        "flask_socketio"
        "networkx"
        "requests"
    )
    
    missing_packages=()
    
    for package in "${required_packages[@]}"; do
        if ! python -c "import ${package}" 2>/dev/null; then
            missing_packages+=("${package}")
        fi
    done
    
    if [ ${#missing_packages[@]} -eq 0 ]; then
        log_success "所有必需依赖已安装"
        return 0
    else
        log_warning "缺少以下依赖: ${missing_packages[*]}"
        return 1
    fi
}

# 安装依赖
install_dependencies() {
    log_step "安装Python依赖..."
    
    # 更新pip
    python -m pip install --upgrade pip
    
    # 安装基础依赖
    log_info "安装基础依赖..."
    pip install streamlit flask-cors flask-socketio python-socketio

    # 安装可选依赖（逐个安装，避免一个失败影响全部）
    log_info "安装可选依赖..."

    optional_packages=(
        "job-shop-lib"
        "ortools"
        "gymnasium"
        "stable-baselines3"
        "loguru"
        "pytest"
        "black"
        "flake8"
    )

    for package in "${optional_packages[@]}"; do
        log_info "安装 ${package}..."
        if pip install "${package}" 2>/dev/null; then
            log_success "${package} 安装成功"
        else
            log_warning "${package} 安装失败，跳过"
        fi
    done
    
    log_success "依赖安装完成"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口空闲
    fi
}

# 检查并停止端口占用的服务
check_and_kill_port() {
    local port=$1
    local service_name=$2

    log_info "🔍 检查端口 $port ($service_name)..."

    # 检查端口是否被占用
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "⚠️  端口 $port 被占用，正在查找占用进程..."

        # 获取占用端口的进程信息
        local pids=$(lsof -ti:$port)
        for pid in $pids; do
            if ps -p $pid > /dev/null 2>&1; then
                # 获取进程名称
                local process_name=$(ps -p $pid -o comm= 2>/dev/null)
                local process_info=$(ps -p $pid -o pid,ppid,comm,args 2>/dev/null || echo "未知进程")
                log_info "📋 发现进程: $process_info"

                # 验证是否是Python/Streamlit/Flask相关进程
                if [[ "$process_name" =~ ^(python|streamlit|flask) ]] || \
                   [[ "$process_info" =~ (streamlit|flask_api|fjsp) ]]; then
                    log_info "✅ 确认为系统相关进程，准备关闭..."

                    # 尝试优雅关闭
                    log_info "🔄 尝试优雅关闭进程 $pid..."
                    kill -TERM $pid 2>/dev/null

                    # 等待3秒
                    sleep 3

                    # 检查进程是否还在运行
                    if ps -p $pid > /dev/null 2>&1; then
                        log_warning "💥 强制关闭进程 $pid..."
                        kill -9 $pid 2>/dev/null
                        sleep 1
                    fi

                    # 再次检查
                    if ps -p $pid > /dev/null 2>&1; then
                        log_error "❌ 无法关闭进程 $pid"
                    else
                        log_success "✅ 成功关闭进程 $pid"
                    fi
                else
                    log_warning "⚠️  进程 $pid ($process_name) 可能不是系统服务，跳过关闭"
                    log_warning "    如需关闭，请手动执行: kill $pid"
                fi
            fi
        done

        # 最终检查端口是否释放
        sleep 2
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_warning "❌ 端口 $port 仍被占用"
            log_info "请手动检查: lsof -i:$port"
        else
            log_success "✅ 端口 $port 已释放"
        fi
    else
        log_success "✅ 端口 $port 空闲"
    fi
}

# 停止现有服务
stop_services() {
    log_step "停止现有服务..."

    # 停止后端
    if [ -f "$BACKEND_PID_FILE" ]; then
        backend_pid=$(cat "$BACKEND_PID_FILE")
        if kill -0 "$backend_pid" 2>/dev/null; then
            log_info "停止后端服务 (PID: $backend_pid)"
            kill "$backend_pid"
            rm -f "$BACKEND_PID_FILE"
        fi
    fi

    # 停止前端
    if [ -f "$FRONTEND_PID_FILE" ]; then
        frontend_pid=$(cat "$FRONTEND_PID_FILE")
        if kill -0 "$frontend_pid" 2>/dev/null; then
            log_info "停止前端服务 (PID: $frontend_pid)"
            kill "$frontend_pid"
            rm -f "$FRONTEND_PID_FILE"
        fi
    fi

    # 智能端口管理
    check_and_kill_port $BACKEND_PORT "后端API"
    check_and_kill_port $FRONTEND_PORT "前端Web"

    log_info "⏳ 等待端口完全释放..."
    sleep 3
}

# 验证端口是否真正空闲
verify_port_free() {
    local port=$1
    local service_name=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_error "❌ 端口 $port 仍被占用，无法启动 $service_name"
        log_info "📋 当前占用进程:"
        lsof -Pi :$port -sTCP:LISTEN
        return 1
    else
        log_success "✅ 端口 $port 确认空闲，可以启动 $service_name"
        return 0
    fi
}

# 启动后端服务
start_backend() {
    log_step "启动后端API服务..."

    # 验证后端端口
    if ! verify_port_free $BACKEND_PORT "后端API"; then
        log_error "❌ 后端启动失败：端口被占用"
        exit 1
    fi
    
    # 启动Flask后端
    cd ../web/backend
    nohup python flask_api.py > /tmp/fjsp_backend.log 2>&1 &
    backend_pid=$!
    echo $backend_pid > "$BACKEND_PID_FILE"
    cd ../../scripts
    
    # 等待后端启动
    log_info "等待后端服务启动..."
    for i in {1..30}; do
        if curl -s http://localhost:$BACKEND_PORT/api/health >/dev/null 2>&1; then
            log_success "后端服务启动成功 (PID: $backend_pid, Port: $BACKEND_PORT)"
            return 0
        fi
        sleep 1
    done
    
    log_error "后端服务启动失败"
    cat /tmp/fjsp_backend.log
    exit 1
}

# 启动前端服务
start_frontend() {
    log_step "启动前端Web应用..."

    # 验证前端端口
    if ! verify_port_free $FRONTEND_PORT "前端Web"; then
        log_error "❌ 前端启动失败：端口被占用"
        # 停止已启动的后端服务
        if [ -f "$BACKEND_PID_FILE" ]; then
            backend_pid=$(cat "$BACKEND_PID_FILE")
            kill $backend_pid 2>/dev/null
            rm -f "$BACKEND_PID_FILE"
        fi
        exit 1
    fi
    
    # 启动Streamlit前端
    nohup streamlit run ../web/streamlit_app.py --server.port $FRONTEND_PORT --server.address 0.0.0.0 --server.headless true > /tmp/fjsp_frontend.log 2>&1 &
    frontend_pid=$!
    echo $frontend_pid > "$FRONTEND_PID_FILE"
    
    # 等待前端启动
    log_info "等待前端服务启动..."
    for i in {1..30}; do
        if curl -s http://localhost:$FRONTEND_PORT >/dev/null 2>&1; then
            log_success "前端服务启动成功 (PID: $frontend_pid, Port: $FRONTEND_PORT)"
            return 0
        fi
        sleep 1
    done
    
    log_error "前端服务启动失败"
    cat /tmp/fjsp_frontend.log
    exit 1
}

# 显示服务状态
show_status() {
    echo
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}🎉 统一FJSP系统启动完成${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo
    echo -e "${GREEN}✅ 推荐访问 (Web界面):${NC}"
    echo -e "   🌐 ${CYAN}http://localhost:$FRONTEND_PORT${NC}"
    echo
    echo -e "${BLUE}🔧 后端API服务:${NC}"
    echo -e "   📡 健康检查: ${CYAN}http://localhost:$BACKEND_PORT/api/health${NC}"
    echo -e "   📋 API根路径: ${CYAN}http://localhost:$BACKEND_PORT/api/${NC}"
    echo
    echo -e "${RED}⚠️  重要提示:${NC}"
    echo -e "   ${RED}❌ 不要访问${NC}: http://localhost:$BACKEND_PORT (会显示404)"
    echo -e "   ${GREEN}✅ 请使用${NC}: http://localhost:$FRONTEND_PORT (完整Web界面)"
    echo
    echo -e "${YELLOW}🧪 快速测试:${NC}"
    echo -e "   curl http://localhost:$BACKEND_PORT/api/health"
    echo
    echo -e "${YELLOW}📁 日志文件:${NC}"
    echo -e "   后端: /tmp/fjsp_backend.log"
    echo -e "   前端: /tmp/fjsp_frontend.log"
    echo
    echo -e "${YELLOW}🛑 停止服务:${NC}"
    echo -e "   运行: $0 stop 或按 Ctrl+C"
    echo
    echo -e "${CYAN}========================================${NC}"
}

# 主函数
main() {
    echo -e "${CYAN}"
    echo "🏭 统一FJSP求解与可视化系统"
    echo "=================================="
    echo -e "${NC}"
    
    # 解析命令行参数
    case "${1:-start}" in
        "stop")
            stop_services
            log_success "服务已停止"
            exit 0
            ;;
        "restart")
            stop_services
            sleep 2
            ;;
        "start"|"")
            # 继续执行启动流程
            ;;
        *)
            echo "用法: $0 [start|stop|restart]"
            exit 1
            ;;
    esac
    
    # 执行启动流程
    check_conda
    setup_conda_env
    activate_conda_env
    
    if ! check_dependencies; then
        install_dependencies
    fi
    
    stop_services
    start_backend
    start_frontend
    show_status
    
    # 保持脚本运行，监控服务状态
    log_info "按 Ctrl+C 停止所有服务"
    trap 'stop_services; log_success "服务已停止"; exit 0' INT
    
    while true; do
        sleep 10
        # 检查服务是否还在运行
        if ! kill -0 $(cat "$BACKEND_PID_FILE" 2>/dev/null) 2>/dev/null; then
            log_error "后端服务异常停止"
            break
        fi
        if ! kill -0 $(cat "$FRONTEND_PID_FILE" 2>/dev/null) 2>/dev/null; then
            log_error "前端服务异常停止"
            break
        fi
    done
}

# 运行主函数
main "$@"
