# 🧪 测试目录

这个目录包含系统的各种测试脚本，用于验证功能正确性和性能表现。

## 📋 测试文件列表

### 🔧 核心测试

#### `test_system.py` - 系统功能测试
- **功能**: 全面的系统功能验证
- **测试内容**:
  - 数据适配器功能
  - 算法求解器测试
  - 可视化组件测试
  - Web界面基础功能
  - 错误处理机制

```bash
# 运行系统测试
python test_system.py

# 详细输出模式
python test_system.py --verbose

# 测试特定模块
python test_system.py --module data_adapter
```

#### `test_disjunctive_graph.py` - 析取图测试
- **功能**: 专门测试析取图可视化功能
- **测试内容**:
  - 析取图生成算法
  - 图形渲染质量
  - 交互功能验证
  - 不同布局算法
  - 性能基准测试

```bash
# 运行析取图测试
python test_disjunctive_graph.py

# 测试特定布局
python test_disjunctive_graph.py --layout spring

# 生成测试报告
python test_disjunctive_graph.py --report
```

#### `test_minimal.py` - 最小化测试
- **功能**: 简化模式下的基础功能测试
- **测试内容**:
  - 简化模式启动
  - 基础数据结构
  - 核心算法接口
  - 错误恢复机制

```bash
# 运行最小化测试
python test_minimal.py

# 模拟缺失依赖环境
python test_minimal.py --simulate-missing-deps
```

## 🎯 测试分类

### 功能测试 (Functional Tests)
- **数据处理**: 实例生成、格式转换、数据验证
- **算法执行**: 求解器运行、结果验证、性能检查
- **可视化**: 图表生成、交互功能、渲染质量
- **Web界面**: 页面加载、用户交互、数据传输

### 性能测试 (Performance Tests)
- **响应时间**: API调用延迟、页面加载速度
- **吞吐量**: 并发用户处理能力、数据处理速度
- **资源使用**: 内存占用、CPU使用率、磁盘I/O
- **可扩展性**: 大规模实例处理能力

### 兼容性测试 (Compatibility Tests)
- **依赖库**: 不同版本库的兼容性
- **操作系统**: Windows、Linux、macOS支持
- **Python版本**: 3.8+版本兼容性
- **浏览器**: 主流浏览器支持

### 错误处理测试 (Error Handling Tests)
- **异常情况**: 无效输入、网络错误、资源不足
- **恢复机制**: 自动重试、降级模式、错误提示
- **日志记录**: 错误信息记录、调试信息输出

## 🚀 运行测试

### 快速测试
```bash
# 运行所有基础测试
python test_minimal.py && python test_system.py

# 运行可视化测试
python test_disjunctive_graph.py
```

### 完整测试套件
```bash
# 按顺序运行所有测试
for test in test_minimal.py test_system.py test_disjunctive_graph.py; do
    echo "Running $test..."
    python $test
    if [ $? -ne 0 ]; then
        echo "Test $test failed!"
        exit 1
    fi
done
echo "All tests passed!"
```

### 自动化测试
```bash
# 创建测试运行脚本
cat > run_all_tests.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "🧪 Running FJSP System Tests"
echo "=============================="

tests=("test_minimal.py" "test_system.py" "test_disjunctive_graph.py")
passed=0
failed=0

for test in "${tests[@]}"; do
    echo "📋 Running $test..."
    if python "$test"; then
        echo "✅ $test PASSED"
        ((passed++))
    else
        echo "❌ $test FAILED"
        ((failed++))
    fi
    echo ""
done

echo "📊 Test Summary:"
echo "   Passed: $passed"
echo "   Failed: $failed"
echo "   Total:  $((passed + failed))"

if [ $failed -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "💥 Some tests failed!"
    exit 1
fi
EOF

chmod +x run_all_tests.sh
./run_all_tests.sh
```

## 📊 测试报告

### 生成测试报告
```bash
# 生成详细测试报告
python test_system.py --report > test_report.md

# 生成性能报告
python test_disjunctive_graph.py --benchmark > performance_report.md

# 生成覆盖率报告 (需要安装coverage)
pip install coverage
coverage run test_system.py
coverage report
coverage html
```

### 报告内容
- **测试结果**: 通过/失败统计
- **性能指标**: 响应时间、资源使用
- **错误详情**: 失败原因和堆栈跟踪
- **改进建议**: 性能优化和功能改进建议

## 🔧 测试配置

### 环境变量
```bash
# 设置测试模式
export FJSP_TEST_MODE=true

# 设置测试数据目录
export FJSP_TEST_DATA_DIR=./test_data

# 设置日志级别
export FJSP_LOG_LEVEL=DEBUG
```

### 测试数据
- **小规模实例**: 3工件×3机器，快速测试
- **中等规模实例**: 10工件×5机器，功能验证
- **大规模实例**: 50工件×20机器，性能测试
- **边界情况**: 极小/极大实例，异常输入

## 🎯 最佳实践

### 测试前准备
1. 确保所有依赖已安装
2. 检查系统资源充足
3. 关闭其他占用端口的服务
4. 备份重要数据

### 测试执行
1. 按照依赖顺序运行测试
2. 记录测试结果和异常
3. 保存测试日志和报告
4. 分析性能瓶颈

### 测试后处理
1. 清理临时文件
2. 分析测试结果
3. 更新文档和代码
4. 提交改进建议

---

**测试版本**: v1.0.0  
**测试框架**: Python unittest + 自定义测试工具  
**覆盖率目标**: >80%
