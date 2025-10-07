#!/bin/bash

# 最简化启动脚本
set -e

ENV_NAME="fjsp-system"
BACKEND_PORT=5001
FRONTEND_PORT=8501

echo "🏭 启动FJSP系统..."

# 检查conda
if ! command -v conda &> /dev/null; then
    echo "❌ conda未安装"
    exit 1
fi

# 删除旧环境
conda env remove -n ${ENV_NAME} -y 2>/dev/null || true

# 创建环境
echo "📦 创建环境..."
conda create -n ${ENV_NAME} python=3.10 -y

# 激活环境
eval "$(conda shell.bash hook)"
conda activate ${ENV_NAME}

# 安装依赖
echo "📦 安装依赖..."
pip install streamlit flask flask-cors flask-socketio python-socketio plotly pandas numpy matplotlib networkx

# 检查并停止端口占用的服务
check_and_kill_port() {
    local port=$1
    local service_name=$2

    echo "🔍 检查端口 $port ($service_name)..."

    # 检查端口是否被占用
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  端口 $port 被占用，正在查找占用进程..."

        # 获取占用端口的进程信息
        local pids=$(lsof -ti:$port)
        for pid in $pids; do
            if ps -p $pid > /dev/null 2>&1; then
                local process_info=$(ps -p $pid -o pid,ppid,comm,args --no-headers 2>/dev/null || echo "未知进程")
                echo "📋 发现进程: $process_info"

                # 尝试优雅关闭
                echo "🔄 尝试优雅关闭进程 $pid..."
                kill -TERM $pid 2>/dev/null

                # 等待3秒
                sleep 3

                # 检查进程是否还在运行
                if ps -p $pid > /dev/null 2>&1; then
                    echo "💥 强制关闭进程 $pid..."
                    kill -9 $pid 2>/dev/null
                    sleep 1
                fi

                # 再次检查
                if ps -p $pid > /dev/null 2>&1; then
                    echo "❌ 无法关闭进程 $pid"
                else
                    echo "✅ 成功关闭进程 $pid"
                fi
            fi
        done

        # 最终检查端口是否释放
        sleep 2
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "❌ 端口 $port 仍被占用，尝试强制释放..."
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
            sleep 2
        else
            echo "✅ 端口 $port 已释放"
        fi
    else
        echo "✅ 端口 $port 空闲"
    fi
}

# 停止现有服务
echo "🛑 检查并停止端口占用的服务..."
check_and_kill_port $BACKEND_PORT "后端API"
check_and_kill_port $FRONTEND_PORT "前端Web"

echo "⏳ 等待端口完全释放..."
sleep 3

# 验证端口是否真正空闲
verify_port_free() {
    local port=$1
    local service_name=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ 端口 $port 仍被占用，无法启动 $service_name"
        echo "📋 当前占用进程:"
        lsof -Pi :$port -sTCP:LISTEN
        return 1
    else
        echo "✅ 端口 $port 确认空闲，可以启动 $service_name"
        return 0
    fi
}

# 启动后端
echo "🚀 启动后端服务..."

# 验证后端端口
if ! verify_port_free $BACKEND_PORT "后端API"; then
    echo "❌ 后端启动失败：端口被占用"
    exit 1
fi

cd web/backend
nohup python flask_api.py > /tmp/backend.log 2>&1 &
backend_pid=$!
cd ../..

echo "📋 后端进程 PID: $backend_pid"

# 等待后端启动
echo "⏳ 等待后端服务启动..."
backend_started=false
for i in {1..30}; do
    # 检查进程是否还在运行
    if ! ps -p $backend_pid > /dev/null 2>&1; then
        echo "❌ 后端进程异常退出"
        echo "📋 后端日志:"
        cat /tmp/backend.log
        exit 1
    fi

    # 检查API是否响应
    if curl -s http://localhost:$BACKEND_PORT/api/health >/dev/null 2>&1; then
        echo "✅ 后端服务启动成功 (PID: $backend_pid, Port: $BACKEND_PORT)"
        backend_started=true
        break
    fi

    echo "⏳ 等待中... ($i/30)"
    sleep 1
done

if [ "$backend_started" = false ]; then
    echo "❌ 后端启动超时"
    echo "📋 后端日志:"
    cat /tmp/backend.log
    kill $backend_pid 2>/dev/null
    exit 1
fi

# 启动前端
echo "🚀 启动前端服务..."

# 验证前端端口
if ! verify_port_free $FRONTEND_PORT "前端Web"; then
    echo "❌ 前端启动失败：端口被占用"
    kill $backend_pid 2>/dev/null
    exit 1
fi

nohup streamlit run web/streamlit_app.py --server.port $FRONTEND_PORT --server.address 0.0.0.0 --server.headless true > /tmp/frontend.log 2>&1 &
frontend_pid=$!

echo "📋 前端进程 PID: $frontend_pid"

# 等待前端启动
echo "⏳ 等待前端服务启动..."
frontend_started=false
for i in {1..30}; do
    # 检查进程是否还在运行
    if ! ps -p $frontend_pid > /dev/null 2>&1; then
        echo "❌ 前端进程异常退出"
        echo "📋 前端日志:"
        cat /tmp/frontend.log
        kill $backend_pid 2>/dev/null
        exit 1
    fi

    # 检查Web服务是否响应
    if curl -s http://localhost:$FRONTEND_PORT >/dev/null 2>&1; then
        echo "✅ 前端服务启动成功 (PID: $frontend_pid, Port: $FRONTEND_PORT)"
        frontend_started=true
        break
    fi

    echo "⏳ 等待中... ($i/30)"
    sleep 1
done

if [ "$frontend_started" = false ]; then
    echo "❌ 前端启动超时"
    echo "📋 前端日志:"
    cat /tmp/frontend.log
    kill $backend_pid $frontend_pid 2>/dev/null
    exit 1
fi

# 保存PID到文件
echo $backend_pid > /tmp/fjsp_backend.pid
echo $frontend_pid > /tmp/fjsp_frontend.pid

# 显示启动成功信息
echo ""
echo "🎉 系统启动完成！"
echo "=========================================="
echo "🌐 前端Web应用: http://localhost:$FRONTEND_PORT"
echo "📡 后端API服务: http://localhost:$BACKEND_PORT"
echo "📋 后端进程PID: $backend_pid"
echo "📋 前端进程PID: $frontend_pid"
echo ""
echo "📁 日志文件:"
echo "   后端: /tmp/backend.log"
echo "   前端: /tmp/frontend.log"
echo ""
echo "🛑 停止服务方法:"
echo "   1. 按 Ctrl+C"
echo "   2. 运行: kill $backend_pid $frontend_pid"
echo "   3. 重新运行此脚本会自动停止旧服务"
echo "=========================================="
echo ""
echo "📊 服务状态监控中... (按 Ctrl+C 停止)"

# 优雅停止函数
graceful_shutdown() {
    echo ""
    echo "🛑 正在停止服务..."

    # 停止后端
    if ps -p $backend_pid > /dev/null 2>&1; then
        echo "🔄 停止后端服务 (PID: $backend_pid)..."
        kill -TERM $backend_pid 2>/dev/null
        sleep 2
        if ps -p $backend_pid > /dev/null 2>&1; then
            echo "💥 强制停止后端服务..."
            kill -9 $backend_pid 2>/dev/null
        fi
    fi

    # 停止前端
    if ps -p $frontend_pid > /dev/null 2>&1; then
        echo "🔄 停止前端服务 (PID: $frontend_pid)..."
        kill -TERM $frontend_pid 2>/dev/null
        sleep 2
        if ps -p $frontend_pid > /dev/null 2>&1; then
            echo "💥 强制停止前端服务..."
            kill -9 $frontend_pid 2>/dev/null
        fi
    fi

    # 清理PID文件
    rm -f /tmp/fjsp_backend.pid /tmp/fjsp_frontend.pid

    echo "✅ 所有服务已停止"
    exit 0
}

# 设置信号处理
trap 'graceful_shutdown' INT TERM

# 服务监控循环
monitor_count=0
while true; do
    sleep 10
    monitor_count=$((monitor_count + 1))

    # 检查后端服务
    if ! ps -p $backend_pid > /dev/null 2>&1; then
        echo "❌ 后端服务异常停止 (PID: $backend_pid)"
        echo "📋 后端日志:"
        tail -20 /tmp/backend.log
        break
    fi

    # 检查前端服务
    if ! ps -p $frontend_pid > /dev/null 2>&1; then
        echo "❌ 前端服务异常停止 (PID: $frontend_pid)"
        echo "📋 前端日志:"
        tail -20 /tmp/frontend.log
        break
    fi

    # 每分钟显示一次状态
    if [ $((monitor_count % 6)) -eq 0 ]; then
        echo "📊 服务运行正常 (运行时间: $((monitor_count * 10))秒)"
        echo "   后端: http://localhost:$BACKEND_PORT/api/health"
        echo "   前端: http://localhost:$FRONTEND_PORT"
    fi
done

# 如果到达这里，说明有服务异常停止
echo "🛑 检测到服务异常，正在清理..."
graceful_shutdown
