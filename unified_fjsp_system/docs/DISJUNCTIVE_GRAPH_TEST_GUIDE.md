# 📊 FJSP析取图可视化功能测试指南

## 🎯 测试目标

验证FJSP系统的析取图可视化功能是否正常工作，包括：
- 实例生成和数据结构
- 析取图构建算法
- 可视化渲染和交互
- API接口调用
- Web界面集成

## 🔧 测试环境

### 系统要求
- Python 3.10+
- Conda环境: fjsp-system
- 浏览器: Chrome/Firefox/Safari
- 网络: localhost访问

### 服务状态
- 后端API: http://localhost:5001
- 前端Web: http://localhost:8501

## 📋 测试步骤

### 步骤1: 启动系统

```bash
cd unified_fjsp_system
./start_system.sh
```

**预期结果**:
- ✅ 后端服务启动成功 (PID: XXXX, Port: 5001)
- ✅ 前端服务启动成功 (PID: XXXX, Port: 8501)
- ✅ 系统显示访问地址

### 步骤2: API功能测试

#### 2.1 健康检查
```bash
curl -s http://localhost:5001/api/health
```

**预期结果**:
```json
{"status":"healthy","timestamp":"2025-10-07T10:59:55.692936","version":"1.0.0"}
```

#### 2.2 创建FJSP实例
```bash
curl -X POST http://localhost:5001/api/instances \
  -H "Content-Type: application/json" \
  -d '{
    "type": "random",
    "num_jobs": 3,
    "num_machines": 3,
    "max_operations_per_job": 3,
    "flexibility": 0.7
  }'
```

**预期结果**:
```json
{
  "created_at": "2025-10-07T10:59:55.692936",
  "instance_id": "f0cf50ee-fb90-4374-8b33-55e8a5d74098",
  "name": "简化实例_3x3",
  "num_jobs": 3,
  "num_machines": 3,
  "num_operations": 9
}
```

#### 2.3 获取实例详情
```bash
curl -s http://localhost:5001/api/instances/{instance_id}
```

**预期结果**:
- 包含完整的工序信息
- 每个工序有job_id, operation_id, machines, processing_times
- 数据结构正确

#### 2.4 生成析取图可视化
```bash
curl -s "http://localhost:5001/api/instances/{instance_id}/visualize/disjunctive_graph?layout=spring" -o disjunctive_graph.html
```

**预期结果**:
- 生成完整的HTML文件
- 包含Plotly.js库
- 包含交互式图表代码

### 步骤3: 析取图结构验证

#### 3.1 节点验证
**检查项目**:
- ✅ 每个工序对应一个节点 (格式: J{job_id}_O{operation_id})
- ✅ 节点包含工序信息 (job_id, operation_id, machines, processing_times)
- ✅ 节点总数 = 工件数 × 每个工件的工序数

**示例**: 3个工件，每个3道工序 → 9个节点
- J0_O0, J0_O1, J0_O2 (工件0的3道工序)
- J1_O0, J1_O1, J1_O2 (工件1的3道工序)  
- J2_O0, J2_O1, J2_O2 (工件2的3道工序)

#### 3.2 边验证
**合取边 (蓝色)**:
- ✅ 同一工件内工序间的顺序约束
- ✅ 方向: J{i}_O{j} → J{i}_O{j+1}

**析取边 (红色)**:
- ✅ 不同工件在同一机器上的冲突约束
- ✅ 双向边: J{i}_O{j} ↔ J{k}_O{l} (当两个工序可在同一机器上加工)

### 步骤4: 可视化功能测试

#### 4.1 布局测试
测试不同布局算法:

```bash
# 弹簧布局
curl -s "http://localhost:5001/api/instances/{instance_id}/visualize/disjunctive_graph?layout=spring" -o spring_layout.html

# 层次布局  
curl -s "http://localhost:5001/api/instances/{instance_id}/visualize/disjunctive_graph?layout=hierarchical" -o hierarchical_layout.html

# 随机布局
curl -s "http://localhost:5001/api/instances/{instance_id}/visualize/disjunctive_graph?layout=random" -o random_layout.html
```

**预期结果**:
- ✅ 三种布局都能正常生成
- ✅ 节点位置不同但连接关系相同
- ✅ 图表清晰可读

#### 4.2 交互功能测试
在浏览器中打开生成的HTML文件:

```bash
open disjunctive_graph.html
```

**检查项目**:
- ✅ 鼠标悬停显示节点信息
- ✅ 可以缩放和平移
- ✅ 边的颜色区分 (蓝色=合取边, 红色=析取边)
- ✅ 节点标签清晰可见
- ✅ 图例和标题正确显示

### 步骤5: Web界面集成测试

#### 5.1 访问前端界面
```bash
open http://localhost:8501
```

#### 5.2 完整流程测试
1. **生成实例**:
   - 在侧边栏选择"随机生成"
   - 设置参数: 工件数=3, 机器数=3, 工序数=3
   - 点击"生成实例"

2. **配置可视化**:
   - 在"可视化选项"中勾选"析取图"
   - 选择布局类型

3. **查看结果**:
   - 主界面显示实例信息
   - 析取图正确渲染
   - 交互功能正常

**预期结果**:
- ✅ 实例生成成功
- ✅ 析取图在Web界面中正确显示
- ✅ 所有交互功能正常工作

## 🔍 故障排除

### 常见问题

#### 问题1: API返回404错误
**原因**: 后端服务未启动或路由配置错误
**解决**: 
```bash
./start_system.sh stop
./start_system.sh
```

#### 问题2: 析取图显示空白
**原因**: 实例数据为空或可视化代码错误
**解决**: 检查实例是否正确创建，查看浏览器控制台错误

#### 问题3: 节点重叠或布局混乱
**原因**: 布局算法参数不当
**解决**: 尝试不同的布局类型 (spring/hierarchical/random)

#### 问题4: 交互功能失效
**原因**: Plotly.js库加载失败
**解决**: 检查网络连接，确保HTML文件完整

### 日志检查

```bash
# 后端日志
tail -f /tmp/fjsp_backend.log

# 前端日志  
tail -f /tmp/fjsp_frontend.log
```

## ✅ 测试验收标准

### 功能完整性
- [ ] API接口正常响应
- [ ] 实例创建和获取功能正常
- [ ] 析取图可视化生成成功
- [ ] 三种布局算法都能工作
- [ ] Web界面集成无误

### 数据正确性
- [ ] 节点数量 = 工件数 × 工序数
- [ ] 合取边正确表示工序顺序约束
- [ ] 析取边正确表示机器冲突约束
- [ ] 节点信息完整准确

### 用户体验
- [ ] 图表清晰易读
- [ ] 交互响应流畅
- [ ] 布局美观合理
- [ ] 错误处理友好

### 性能要求
- [ ] API响应时间 < 2秒
- [ ] 图表渲染时间 < 3秒
- [ ] 交互延迟 < 100ms
- [ ] 内存使用合理

## 📊 测试报告模板

```
测试日期: 2025-10-07
测试人员: [姓名]
系统版本: 1.0.0

测试结果:
✅ API功能测试: 通过
✅ 析取图构建: 通过  
✅ 可视化渲染: 通过
✅ 交互功能: 通过
✅ Web界面集成: 通过

发现问题:
- [问题描述]
- [解决方案]

总体评价: 通过/不通过
备注: [其他说明]
```

---

**注意**: 本测试指南基于简化模式运行，如需测试完整功能，请确保安装所有依赖库 (job-shop-lib, ortools等)。
