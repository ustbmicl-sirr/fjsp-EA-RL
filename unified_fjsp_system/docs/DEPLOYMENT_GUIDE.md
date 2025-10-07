# 🚀 部署指南

## 📋 系统架构

当前的统一FJSP系统采用**前后端分离架构**：

### 🔧 后端 (Backend)
- **技术栈**: Flask + Flask-SocketIO
- **端口**: 5000
- **功能**: 
  - RESTful API接口
  - WebSocket实时通信
  - FJSP实例管理
  - 算法求解服务
  - 结果可视化生成

### 🌐 前端 (Frontend)  
- **技术栈**: Streamlit
- **端口**: 8501
- **功能**:
  - 用户交互界面
  - 参数配置
  - 实时进度监控
  - 结果展示

### 📡 通信方式
- **HTTP API**: 前端调用后端REST接口
- **WebSocket**: 实时进度更新和状态同步
- **本地模式**: 前端也可独立运行（无后端时）

## 🛠️ 快速启动

### 方法1: 自动化脚本（推荐）

#### Linux/macOS:
```bash
cd unified_fjsp_system
./start_system.sh
```

#### Windows:
```cmd
cd unified_fjsp_system
start_system.bat
```

#### 跨平台Python脚本:
```bash
cd unified_fjsp_system
python start_system.py
```

### 方法2: 手动启动

#### 1. 创建conda环境
```bash
# 创建环境
conda env create -f environment.yml

# 或者手动创建
conda create -n fjsp-system python=3.9 -y
conda activate fjsp-system
```

#### 2. 安装依赖
```bash
# 基础依赖
pip install numpy pandas matplotlib plotly streamlit flask flask-cors flask-socketio networkx requests

# 可选依赖
pip install job-shop-lib ortools gymnasium stable-baselines3
```

#### 3. 启动后端
```bash
cd web/backend
python flask_api.py
```

#### 4. 启动前端（新终端）
```bash
streamlit run web/streamlit_app.py --server.port 8501
```

## 🔧 配置说明

### 端口配置
- **后端端口**: 5000 (可在flask_api.py中修改)
- **前端端口**: 8501 (可在启动命令中指定)

### 环境变量
```bash
# API基础URL
export API_BASE_URL="http://localhost:5000/api"

# WebSocket URL  
export WEBSOCKET_URL="http://localhost:5000"

# 日志级别
export LOG_LEVEL="INFO"
```

### 配置文件
- `environment.yml`: conda环境配置
- `requirements.txt`: Python依赖列表
- `web/backend/flask_api.py`: 后端API配置

## 📊 API接口文档

### 健康检查
```http
GET /api/health
```

### 创建FJSP实例
```http
POST /api/instances
Content-Type: application/json

{
  "type": "random",
  "num_jobs": 3,
  "num_machines": 3,
  "max_operations_per_job": 3,
  "flexibility": 0.5
}
```

### 求解问题
```http
POST /api/solve
Content-Type: application/json

{
  "instance_id": "uuid",
  "algorithms": ["evolutionary", "reinforcement"],
  "parameters": {
    "population_size": 50,
    "generations": 100
  }
}
```

### 获取结果
```http
GET /api/results/{session_id}
```

### 生成可视化
```http
GET /api/visualize/{session_id}/{viz_type}
```
支持的可视化类型: `gantt`, `disjunctive_graph`, `convergence`, `comparison`, `dashboard`

## 🔌 WebSocket事件

### 连接事件
```javascript
// 连接到WebSocket
socket.connect();

// 加入会话房间
socket.emit('join_session', {session_id: 'uuid'});

// 监听进度更新
socket.on('progress_update', (data) => {
    console.log('Progress:', data);
});

// 监听求解完成
socket.on('solve_complete', (data) => {
    console.log('Solve completed:', data);
});
```

## 🐳 Docker部署

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000 8501

CMD ["python", "start_system.py"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  fjsp-backend:
    build: .
    ports:
      - "5000:5000"
    command: python web/backend/flask_api.py
    
  fjsp-frontend:
    build: .
    ports:
      - "8501:8501"
    command: streamlit run web/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
    depends_on:
      - fjsp-backend
```

### 启动Docker
```bash
# 构建和启动
docker-compose up --build

# 后台运行
docker-compose up -d
```

## 🔍 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查看端口占用
lsof -i :5000
lsof -i :8501

# 杀死进程
kill -9 <PID>
```

#### 2. conda环境问题
```bash
# 重新创建环境
conda env remove -n fjsp-system
conda env create -f environment.yml
```

#### 3. 依赖安装失败
```bash
# 更新pip
pip install --upgrade pip

# 清理缓存
pip cache purge

# 重新安装
pip install -r requirements.txt
```

#### 4. 后端连接失败
- 检查后端是否启动: `curl http://localhost:5000/api/health`
- 检查防火墙设置
- 确认端口配置正确

#### 5. 前端无法访问
- 检查Streamlit是否启动
- 确认浏览器地址: `http://localhost:8501`
- 检查网络代理设置

### 日志查看
```bash
# 后端日志
tail -f /tmp/fjsp_backend.log

# 前端日志  
tail -f /tmp/fjsp_frontend.log

# 系统日志
journalctl -f -u fjsp-system
```

## 📈 性能优化

### 后端优化
- 使用Gunicorn部署Flask应用
- 配置Redis缓存
- 启用数据库连接池

### 前端优化
- 启用Streamlit缓存
- 优化图表渲染
- 减少不必要的重新计算

### 系统优化
- 增加内存限制
- 配置并发数
- 启用负载均衡

## 🔒 安全配置

### 生产环境建议
- 修改默认密钥
- 启用HTTPS
- 配置防火墙
- 限制API访问频率
- 添加用户认证

### 配置示例
```python
# Flask配置
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['WTF_CSRF_ENABLED'] = True

# CORS配置
CORS(app, origins=['https://yourdomain.com'])
```

## 📞 技术支持

### 获取帮助
- 查看日志文件
- 运行系统测试: `python test_system.py`
- 检查依赖状态: `python -c "import unified_fjsp_system; unified_fjsp_system.print_system_info()"`

### 联系方式
- GitHub Issues
- 技术文档
- 社区论坛

---

**部署成功后访问**: 
- 🌐 前端界面: http://localhost:8501
- 📡 后端API: http://localhost:5000/api/health
