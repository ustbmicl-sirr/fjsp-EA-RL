# 🚀 启动脚本目录

这个目录包含系统的各种启动脚本，支持不同平台和使用场景。

## 📋 脚本列表

### 🖥️ 主要启动脚本

#### `start_system.sh` (Linux/Mac)
- **功能**: 完整的系统启动脚本
- **特性**: 
  - 自动检测和管理conda环境
  - 智能端口管理和冲突处理
  - 依赖检查和安装提示
  - 前后端服务启动
  - 错误处理和日志记录

```bash
# 使用方法
./start_system.sh

# 可选参数
./start_system.sh --port 8502  # 自定义端口
./start_system.sh --help       # 查看帮助
```

#### `start_system.py` (跨平台)
- **功能**: Python版本的启动脚本
- **特性**:
  - 跨平台兼容性
  - 依赖检查和验证
  - 可选依赖检测
  - 灵活的配置选项

```bash
# 使用方法
python start_system.py

# 可选参数
python start_system.py --port 8501
python start_system.py --host 0.0.0.0
python start_system.py --example  # 运行示例
```

#### `start_system.bat` (Windows)
- **功能**: Windows批处理启动脚本
- **特性**:
  - Windows环境优化
  - 自动环境检测
  - 错误处理和提示

```cmd
REM 使用方法
start_system.bat

REM 或双击运行
```

## 🎯 使用建议

### 选择合适的启动脚本

#### **Linux/Mac用户**
推荐使用 `start_system.sh`：
- 功能最完整
- 自动环境管理
- 智能错误处理

#### **Windows用户**
推荐使用 `start_system.bat`：
- Windows环境优化
- 简单易用
- 双击启动

#### **开发者/高级用户**
推荐使用 `start_system.py`：
- 更多配置选项
- 跨平台兼容
- 便于调试和定制

### 常见问题解决

#### 端口冲突
```bash
# 使用自定义端口
./start_system.sh --port 8502
python start_system.py --port 8502
```

#### 依赖缺失
```bash
# 检查依赖状态
python start_system.py --check-deps

# 安装基础依赖
pip install -r requirements.txt
```

#### 权限问题 (Linux/Mac)
```bash
# 添加执行权限
chmod +x start_system.sh

# 运行脚本
./start_system.sh
```

## 🔧 脚本功能对比

| 功能 | start_system.sh | start_system.py | start_system.bat |
|------|----------------|-----------------|------------------|
| 平台支持 | Linux/Mac | 跨平台 | Windows |
| 环境管理 | ✅ Conda | ✅ 基础 | ✅ 基础 |
| 端口管理 | ✅ 智能 | ✅ 基础 | ✅ 基础 |
| 依赖检查 | ✅ 完整 | ✅ 详细 | ✅ 基础 |
| 错误处理 | ✅ 高级 | ✅ 标准 | ✅ 基础 |
| 自定义选项 | ✅ 丰富 | ✅ 灵活 | ❌ 固定 |

## 📊 启动流程

### 标准启动流程
1. **环境检查**: 检测Python版本和虚拟环境
2. **依赖验证**: 验证必需和可选依赖
3. **端口管理**: 检查端口占用，处理冲突
4. **服务启动**: 启动Streamlit Web应用
5. **状态监控**: 监控服务状态，提供访问地址

### 错误处理机制
- **依赖缺失**: 提供安装建议和命令
- **端口冲突**: 自动寻找可用端口或终止冲突进程
- **启动失败**: 详细错误信息和解决建议
- **环境问题**: 环境配置检查和修复提示

## 🎨 自定义和扩展

### 添加新的启动选项
可以修改脚本添加新的功能：
- 自定义配置文件路径
- 特定算法模式启动
- 调试模式开关
- 日志级别控制

### 集成到CI/CD
脚本支持自动化部署：
- 无交互模式运行
- 返回状态码
- 日志输出控制

---

**脚本版本**: v1.0.0  
**维护说明**: 定期更新以支持新功能和平台
