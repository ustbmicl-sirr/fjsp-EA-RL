#!/bin/bash

# 快速启动脚本 - 解决依赖问题
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

ENV_NAME="fjsp-system"
BACKEND_PORT=5000
FRONTEND_PORT=8501

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

echo -e "${CYAN}"
echo "🏭 统一FJSP系统快速启动"
echo "========================"
echo -e "${NC}"

# 检查conda
if ! command -v conda &> /dev/null; then
    log_error "conda未安装，请先安装Anaconda或Miniconda"
    exit 1
fi

log_success "conda已安装: $(conda --version)"

# 删除现有环境（如果存在）
if conda env list | grep -q "^${ENV_NAME} "; then
    log_info "删除现有环境 '${ENV_NAME}'..."
    conda env remove -n ${ENV_NAME} -y
fi

# 创建新环境
log_info "创建新的conda环境..."
conda create -n ${ENV_NAME} python=3.10 numpy pandas matplotlib scipy networkx pyyaml requests -c conda-forge -y

# 激活环境
log_info "激活环境..."
eval "$(conda shell.bash hook)"
conda activate ${ENV_NAME}

if [ "$CONDA_DEFAULT_ENV" != "${ENV_NAME}" ]; then
    log_error "环境激活失败"
    exit 1
fi

log_success "环境激活成功: ${CONDA_DEFAULT_ENV}"

# 安装pip依赖
log_info "安装Web框架依赖..."
pip install plotly streamlit flask flask-cors flask-socketio python-socketio

# 安装可选依赖
log_info "安装可选依赖..."
pip install loguru tqdm 2>/dev/null || log_warning "loguru/tqdm 安装失败，跳过"

# 尝试安装job-shop-lib（可能失败）
log_info "尝试安装job-shop-lib..."
if pip install job-shop-lib 2>/dev/null; then
    log_success "job-shop-lib 安装成功"
else
    log_warning "job-shop-lib 安装失败，系统将使用内置算法"
fi

# 尝试安装ortools（可能失败）
log_info "尝试安装ortools..."
if pip install ortools 2>/dev/null; then
    log_success "ortools 安装成功"
else
    log_warning "ortools 安装失败，约束编程功能不可用"
fi

# 停止现有服务
log_info "停止现有服务..."
if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
fi

if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
fi

sleep 2

# 启动后端
log_info "启动后端服务..."
cd web/backend
nohup python flask_api.py > /tmp/fjsp_backend.log 2>&1 &
backend_pid=$!
cd ../..

# 等待后端启动
log_info "等待后端启动..."
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/api/health >/dev/null 2>&1; then
        log_success "后端启动成功 (PID: $backend_pid)"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        log_error "后端启动失败"
        cat /tmp/fjsp_backend.log
        exit 1
    fi
done

# 启动前端
log_info "启动前端服务..."
nohup streamlit run web/streamlit_app.py --server.port $FRONTEND_PORT --server.address 0.0.0.0 --server.headless true > /tmp/fjsp_frontend.log 2>&1 &
frontend_pid=$!

# 等待前端启动
log_info "等待前端启动..."
for i in {1..30}; do
    if curl -s http://localhost:$FRONTEND_PORT >/dev/null 2>&1; then
        log_success "前端启动成功 (PID: $frontend_pid)"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        log_error "前端启动失败"
        cat /tmp/fjsp_frontend.log
        exit 1
    fi
done

# 显示状态
echo
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}🎉 系统启动成功！${NC}"
echo -e "${CYAN}========================================${NC}"
echo
echo -e "${GREEN}🌐 前端界面:${NC} http://localhost:$FRONTEND_PORT"
echo -e "${GREEN}📡 后端API:${NC} http://localhost:$BACKEND_PORT/api/health"
echo
echo -e "${YELLOW}📁 日志文件:${NC}"
echo -e "   后端: /tmp/fjsp_backend.log"
echo -e "   前端: /tmp/fjsp_frontend.log"
echo
echo -e "${YELLOW}🛑 停止服务:${NC}"
echo -e "   kill $backend_pid $frontend_pid"
echo
echo -e "${CYAN}========================================${NC}"

# 保存PID
echo $backend_pid > /tmp/fjsp_backend.pid
echo $frontend_pid > /tmp/fjsp_frontend.pid

echo -e "${BLUE}[INFO]${NC} 按 Ctrl+C 停止所有服务"

# 等待中断信号
trap 'echo; log_info "正在停止服务..."; kill $backend_pid $frontend_pid 2>/dev/null; log_success "服务已停止"; exit 0' INT

while true; do
    sleep 10
    if ! kill -0 $backend_pid 2>/dev/null; then
        log_error "后端服务异常停止"
        break
    fi
    if ! kill -0 $frontend_pid 2>/dev/null; then
        log_error "前端服务异常停止"
        break
    fi
done
