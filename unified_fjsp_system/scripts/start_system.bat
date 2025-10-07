@echo off
REM 统一FJSP系统启动脚本 (Windows版本)
REM 自动管理conda环境、检查依赖、启动前后端服务

setlocal enabledelayedexpansion

REM 配置
set ENV_NAME=fjsp-system
set BACKEND_PORT=5000
set FRONTEND_PORT=8501
set BACKEND_PID_FILE=%TEMP%\fjsp_backend.pid
set FRONTEND_PID_FILE=%TEMP%\fjsp_frontend.pid

REM 颜色定义 (Windows 10+)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "PURPLE=[95m"
set "CYAN=[96m"
set "NC=[0m"

echo %CYAN%
echo 🏭 统一FJSP求解与可视化系统
echo ==================================
echo %NC%

REM 检查参数
if "%1"=="stop" goto stop_services
if "%1"=="restart" (
    call :stop_services
    timeout /t 2 /nobreak >nul
)

REM 检查conda
echo %BLUE%[STEP]%NC% 检查conda环境...
where conda >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% conda未安装，请先安装Anaconda或Miniconda
    echo 下载地址: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('conda --version') do set CONDA_VERSION=%%i
echo %GREEN%[SUCCESS]%NC% conda已安装: !CONDA_VERSION!

REM 检查并创建环境
echo %BLUE%[STEP]%NC% 设置conda环境...
conda env list | findstr /c:"%ENV_NAME%" >nul
if errorlevel 1 (
    echo %BLUE%[INFO]%NC% 创建conda环境 '%ENV_NAME%'...
    if exist environment.yml (
        conda env create -f environment.yml
        echo %GREEN%[SUCCESS]%NC% 从environment.yml创建环境成功
    ) else (
        echo %YELLOW%[WARNING]%NC% environment.yml不存在，使用基础配置创建环境
        conda create -n %ENV_NAME% python=3.9 -y
        echo %GREEN%[SUCCESS]%NC% 创建基础环境成功
    )
) else (
    echo %BLUE%[INFO]%NC% conda环境 '%ENV_NAME%' 已存在
)

REM 激活环境
echo %BLUE%[STEP]%NC% 激活conda环境...
call conda activate %ENV_NAME%
if errorlevel 1 (
    echo %RED%[ERROR]%NC% 环境激活失败
    pause
    exit /b 1
)
echo %GREEN%[SUCCESS]%NC% 环境激活成功

REM 检查依赖
echo %BLUE%[STEP]%NC% 检查Python依赖...
set MISSING_DEPS=0

python -c "import numpy" 2>nul || set MISSING_DEPS=1
python -c "import pandas" 2>nul || set MISSING_DEPS=1
python -c "import matplotlib" 2>nul || set MISSING_DEPS=1
python -c "import plotly" 2>nul || set MISSING_DEPS=1
python -c "import streamlit" 2>nul || set MISSING_DEPS=1
python -c "import flask" 2>nul || set MISSING_DEPS=1
python -c "import flask_cors" 2>nul || set MISSING_DEPS=1
python -c "import flask_socketio" 2>nul || set MISSING_DEPS=1
python -c "import networkx" 2>nul || set MISSING_DEPS=1
python -c "import requests" 2>nul || set MISSING_DEPS=1

if !MISSING_DEPS!==1 (
    echo %YELLOW%[WARNING]%NC% 缺少必需依赖，正在安装...
    call :install_dependencies
) else (
    echo %GREEN%[SUCCESS]%NC% 所有必需依赖已安装
)

REM 停止现有服务
call :stop_services

REM 启动后端
echo %BLUE%[STEP]%NC% 启动后端API服务...
cd ..\web\backend
start /b python flask_api.py > %TEMP%\fjsp_backend.log 2>&1
cd ..\..\scripts

REM 等待后端启动
echo %BLUE%[INFO]%NC% 等待后端服务启动...
set BACKEND_READY=0
for /l %%i in (1,1,30) do (
    timeout /t 1 /nobreak >nul
    curl -s http://localhost:%BACKEND_PORT%/api/health >nul 2>&1
    if not errorlevel 1 (
        set BACKEND_READY=1
        goto backend_ready
    )
)

:backend_ready
if !BACKEND_READY!==1 (
    echo %GREEN%[SUCCESS]%NC% 后端服务启动成功 (Port: %BACKEND_PORT%)
) else (
    echo %RED%[ERROR]%NC% 后端服务启动失败
    type %TEMP%\fjsp_backend.log
    pause
    exit /b 1
)

REM 启动前端
echo %BLUE%[STEP]%NC% 启动前端Web应用...
start /b streamlit run ..\web\streamlit_app.py --server.port %FRONTEND_PORT% --server.address 0.0.0.0 --server.headless true > %TEMP%\fjsp_frontend.log 2>&1

REM 等待前端启动
echo %BLUE%[INFO]%NC% 等待前端服务启动...
set FRONTEND_READY=0
for /l %%i in (1,1,30) do (
    timeout /t 1 /nobreak >nul
    curl -s http://localhost:%FRONTEND_PORT% >nul 2>&1
    if not errorlevel 1 (
        set FRONTEND_READY=1
        goto frontend_ready
    )
)

:frontend_ready
if !FRONTEND_READY!==1 (
    echo %GREEN%[SUCCESS]%NC% 前端服务启动成功 (Port: %FRONTEND_PORT%)
) else (
    echo %RED%[ERROR]%NC% 前端服务启动失败
    type %TEMP%\fjsp_frontend.log
    pause
    exit /b 1
)

REM 显示状态
echo.
echo %CYAN%========================================%NC%
echo %CYAN%🎉 统一FJSP系统启动完成%NC%
echo %CYAN%========================================%NC%
echo.
echo %GREEN%✅ 推荐访问 (Web界面):%NC%
echo    🌐 http://localhost:%FRONTEND_PORT%
echo.
echo %BLUE%🔧 后端API服务:%NC%
echo    📡 健康检查: http://localhost:%BACKEND_PORT%/api/health
echo    📋 API根路径: http://localhost:%BACKEND_PORT%/api/
echo.
echo %RED%⚠️  重要提示:%NC%
echo    %RED%❌ 不要访问%NC%: http://localhost:%BACKEND_PORT% (会显示404)
echo    %GREEN%✅ 请使用%NC%: http://localhost:%FRONTEND_PORT% (完整Web界面)
echo.
echo %YELLOW%🧪 快速测试:%NC%
echo    curl http://localhost:%BACKEND_PORT%/api/health
echo.
echo %YELLOW%📁 日志文件:%NC%
echo    后端: %TEMP%\fjsp_backend.log
echo    前端: %TEMP%\fjsp_frontend.log
echo.
echo %YELLOW%🛑 停止服务:%NC%
echo    运行: %~nx0 stop 或按任意键
echo.
echo %CYAN%========================================%NC%
echo.
echo %BLUE%[INFO]%NC% 按任意键停止所有服务...
pause >nul

goto stop_services

REM 安装依赖函数
:install_dependencies
echo %BLUE%[STEP]%NC% 安装Python依赖...
python -m pip install --upgrade pip
echo %BLUE%[INFO]%NC% 安装基础依赖...
pip install numpy pandas matplotlib plotly streamlit flask flask-cors flask-socketio networkx requests
echo %BLUE%[INFO]%NC% 安装可选依赖...
pip install job-shop-lib ortools gymnasium stable-baselines3 loguru tqdm pytest black flake8 2>nul || (
    echo %YELLOW%[WARNING]%NC% 部分可选依赖安装失败，系统仍可正常运行
)
echo %GREEN%[SUCCESS]%NC% 依赖安装完成
goto :eof

REM 停止服务函数
:stop_services
echo %BLUE%[STEP]%NC% 停止现有服务...

REM 停止占用端口的进程
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%BACKEND_PORT%') do (
    taskkill /f /pid %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%FRONTEND_PORT%') do (
    taskkill /f /pid %%a >nul 2>&1
)

REM 停止Python进程
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im streamlit.exe >nul 2>&1

timeout /t 2 /nobreak >nul

if "%1"=="stop" (
    echo %GREEN%[SUCCESS]%NC% 服务已停止
    pause
    exit /b 0
)
goto :eof
