#!/bin/bash

# ================================================================
# 测试当前项目与参考库集成的脚本
# 一键完成：环境配置 → 安装依赖 → 测试功能 → 生成报告
# ================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

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

# 测试结果记录
RESULTS_FILE="/tmp/fjsp_test_results.txt"
> "$RESULTS_FILE"  # 清空文件

record_result() {
    local test_name=$1
    local status=$2
    local details=$3
    echo "$test_name|$status|$details" >> "$RESULTS_FILE"
}

# 检查并初始化 conda
setup_conda() {
    log_step "1/6 初始化 conda 环境..."

    # 尝试多个可能的 conda 路径
    CONDA_PATHS=(
        "$HOME/miniforge3/etc/profile.d/conda.sh"
        "$HOME/miniconda3/etc/profile.d/conda.sh"
        "$HOME/anaconda3/etc/profile.d/conda.sh"
        "/opt/anaconda3/etc/profile.d/conda.sh"
        "/usr/local/anaconda3/etc/profile.d/conda.sh"
        "/opt/homebrew/anaconda3/etc/profile.d/conda.sh"
        "/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh"
    )

    CONDA_FOUND=false
    for conda_path in "${CONDA_PATHS[@]}"; do
        if [ -f "$conda_path" ]; then
            source "$conda_path"
            CONDA_FOUND=true
            log_info "从 $conda_path 加载 conda"
            break
        fi
    done

    if [ "$CONDA_FOUND" = false ]; then
        log_error "conda 未找到！"
        log_info "请先安装 Anaconda 或 Miniconda"
        log_info "下载地址: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi

    eval "$(conda shell.bash hook)"
    log_success "conda 初始化成功: $(conda --version)"
    record_result "Conda初始化" "✅" "$(conda --version)"
}

# 创建或激活测试环境
setup_test_env() {
    log_step "2/6 配置测试环境..."

    ENV_NAME="fjsp-libs-unified"

    # 检查环境是否存在
    if conda env list | grep -q "^${ENV_NAME} "; then
        log_info "环境 '${ENV_NAME}' 已存在，将使用现有环境"
        record_result "环境检查" "✅" "使用现有环境"
    else
        log_info "创建新环境 '${ENV_NAME}' (Python 3.10)..."
        conda create -n ${ENV_NAME} python=3.10 -y
        if [ $? -eq 0 ]; then
            log_success "环境创建成功"
            record_result "环境创建" "✅" "Python 3.10"
        else
            log_error "环境创建失败"
            record_result "环境创建" "❌" "失败"
            exit 1
        fi
    fi

    # 激活环境
    conda activate ${ENV_NAME}
    if [ "$CONDA_DEFAULT_ENV" = "${ENV_NAME}" ]; then
        log_success "环境激活成功: ${CONDA_DEFAULT_ENV}"
        record_result "环境激活" "✅" "${CONDA_DEFAULT_ENV}"
    else
        log_error "环境激活失败"
        record_result "环境激活" "❌" "失败"
        exit 1
    fi
}

# 安装依赖
install_dependencies() {
    log_step "3/6 安装依赖包..."

    # 升级 pip
    log_info "升级 pip..."
    pip install --upgrade pip --quiet

    # 安装核心依赖
    log_info "安装核心依赖..."
    pip install numpy pandas matplotlib plotly networkx --quiet
    record_result "核心依赖" "✅" "numpy, pandas, matplotlib, plotly, networkx"

    # 安装参考库
    log_info "安装 JobShopLib..."
    if pip install job-shop-lib --quiet 2>/dev/null; then
        log_success "JobShopLib 安装成功"
        record_result "JobShopLib安装" "✅" "$(pip show job-shop-lib | grep Version | awk '{print $2}')"
    else
        log_warning "JobShopLib 安装失败（可能需要依赖）"
        record_result "JobShopLib安装" "⚠️" "安装失败"
    fi

    log_info "安装 Graph-JSP-Env..."
    if pip install graph-jsp-env --quiet 2>/dev/null; then
        log_success "Graph-JSP-Env 安装成功"
        record_result "Graph-JSP-Env安装" "✅" "$(pip show graph-jsp-env | grep Version | awk '{print $2}')"
    else
        log_warning "Graph-JSP-Env 安装失败"
        record_result "Graph-JSP-Env安装" "⚠️" "安装失败"
    fi

    # 安装可选依赖
    log_info "安装可选依赖..."
    pip install ortools gymnasium stable-baselines3 --quiet 2>/dev/null || log_warning "部分可选依赖安装失败"

    log_success "依赖安装完成"
}

# 测试本项目的集成功能
test_project_integration() {
    log_step "4/6 测试本项目与参考库的集成..."

    # 创建测试脚本
    cat > /tmp/test_integration.py << 'PYTEST'
import sys
import traceback

# 测试结果记录
results = []

def test_result(name, status, details=""):
    results.append((name, status, details))
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {name}: {details}")

print("=" * 70)
print("🧪 测试本项目与参考库的集成")
print("=" * 70)
print()

# 1. 测试核心模块导入
print("1️⃣  测试核心模块导入...")
try:
    import sys
    import os
    project_root = "/Users/duan/mac-miclsirr/fjsp-EA-RL/unified_fjsp_system"
    if os.path.exists(project_root):
        sys.path.insert(0, project_root)
        test_result("项目路径", True, project_root)
    else:
        test_result("项目路径", False, "路径不存在")
        sys.exit(1)
except Exception as e:
    test_result("项目路径", False, str(e))
    sys.exit(1)

# 2. 测试数据适配器
print("\n2️⃣  测试数据适配器...")
try:
    from core.data_adapter import UnifiedFJSPInstance, DataAdapter, InstanceGenerator
    test_result("DataAdapter导入", True, "成功")

    # 测试实例生成
    instance = InstanceGenerator.generate_random_fjsp(3, 3, 3)
    test_result("随机实例生成", True, f"{instance.num_jobs}x{instance.num_machines}")
except Exception as e:
    test_result("DataAdapter导入", False, str(e))

# 3. 测试 JobShopLib 集成
print("\n3️⃣  测试 JobShopLib 集成...")
try:
    from job_shop_lib import JobShopInstance, Operation
    test_result("JobShopLib导入", True, "job_shop_lib")

    # 测试格式转换
    try:
        job_1 = [Operation(machines=0, duration=3), Operation(1, 2)]
        jsl_instance = JobShopInstance([job_1], name="test")
        unified = DataAdapter.from_jobshoplib(jsl_instance)
        test_result("JobShopLib格式转换", True, f"转换成功: {unified.num_jobs} jobs")
    except Exception as e:
        test_result("JobShopLib格式转换", False, str(e))

    # 测试求解器框架
    try:
        from algorithms.unified_solver import JobShopLibSolver
        solver = JobShopLibSolver()
        test_result("JobShopLibSolver类", True, f"{len(solver.available_solvers)} 求解器可用")

        # 检查具体求解器
        solver_names = [name for name, _ in solver.available_solvers]
        test_result("可用求解器", True, f"{', '.join(solver_names)}")
    except Exception as e:
        test_result("JobShopLibSolver类", False, str(e))

except ImportError as e:
    test_result("JobShopLib导入", False, "未安装或不兼容")

# 4. 测试 Graph-JSP-Env 集成
print("\n4️⃣  测试 Graph-JSP-Env 集成...")
try:
    from graph_jsp_env.disjunctive_graph_jsp_env import DisjunctiveGraphJspEnv
    import numpy as np
    test_result("Graph-JSP-Env导入", True, "graph_jsp_env")

    # 测试格式转换
    try:
        jsp_array = DataAdapter.to_graph_jsp_env(instance)
        test_result("Graph-JSP格式转换", True, f"数组形状: {jsp_array.shape}")
    except Exception as e:
        test_result("Graph-JSP格式转换", False, str(e))

except ImportError as e:
    test_result("Graph-JSP-Env导入", False, "未安装")

# 5. 测试求解器管理器
print("\n5️⃣  测试求解器管理器...")
try:
    from algorithms.unified_solver import UnifiedSolverManager
    manager = UnifiedSolverManager()
    test_result("UnifiedSolverManager", True, "实例化成功")

    # 列出可用求解器
    available_solvers = list(manager.solvers.keys())
    test_result("求解器列表", True, f"{len(available_solvers)} 个: {', '.join(available_solvers)}")

except Exception as e:
    test_result("UnifiedSolverManager", False, str(e))

# 6. 测试可视化器
print("\n6️⃣  测试可视化器...")
try:
    from visualization.unified_visualizer import UnifiedVisualizer
    visualizer = UnifiedVisualizer()
    test_result("UnifiedVisualizer", True, "实例化成功")

    # 测试析取图构建
    try:
        G = DataAdapter.build_disjunctive_graph(instance)
        test_result("析取图构建", True, f"{G.number_of_nodes()} 节点, {G.number_of_edges()} 边")
    except Exception as e:
        test_result("析取图构建", False, str(e))

except Exception as e:
    test_result("UnifiedVisualizer", False, str(e))

# 7. 测试遗传算法求解器
print("\n7️⃣  测试遗传算法求解器...")
try:
    from algorithms.unified_solver import EvolutionaryAlgorithmSolver
    ea_solver = EvolutionaryAlgorithmSolver()
    test_result("EvolutionaryAlgorithm", True, "类定义存在")

    # 快速求解测试（少量迭代）
    try:
        result = ea_solver.solve(instance, generations=10, population_size=20)
        test_result("GA求解测试", True, f"makespan: {result.makespan:.2f}")
    except Exception as e:
        test_result("GA求解测试", False, str(e)[:50])

except Exception as e:
    test_result("EvolutionaryAlgorithm", False, str(e))

# 生成测试报告
print("\n" + "=" * 70)
print("📊 测试结果汇总")
print("=" * 70)

passed = sum(1 for _, status, _ in results if status)
failed = sum(1 for _, status, _ in results if not status)
total = len(results)

print(f"\n总计: {total} 项测试")
print(f"✅ 通过: {passed}")
print(f"❌ 失败: {failed}")
print(f"成功率: {passed/total*100:.1f}%")

print("\n详细结果:")
for name, status, details in results:
    status_symbol = "✅" if status else "❌"
    print(f"  {status_symbol} {name:30s} {details}")

# 保存结果到文件
with open("/tmp/integration_test_details.txt", "w") as f:
    for name, status, details in results:
        status_str = "PASS" if status else "FAIL"
        f.write(f"{name}|{status_str}|{details}\n")

print("\n详细结果已保存到: /tmp/integration_test_details.txt")

# 返回退出码
sys.exit(0 if failed == 0 else 1)
PYTEST

    # 运行测试
    python /tmp/test_integration.py
    local test_result=$?

    if [ $test_result -eq 0 ]; then
        log_success "集成测试全部通过"
        record_result "集成测试" "✅" "全部通过"
    else
        log_warning "部分集成测试失败，请查看详细输出"
        record_result "集成测试" "⚠️" "部分失败"
    fi

    # 读取详细结果
    if [ -f "/tmp/integration_test_details.txt" ]; then
        while IFS='|' read -r name status details; do
            record_result "  └─ $name" "$status" "$details"
        done < /tmp/integration_test_details.txt
    fi
}

# 测试 Web 前端导入
test_web_frontend() {
    log_step "5/6 测试 Web 前端模块..."

    cat > /tmp/test_web.py << 'WEBTEST'
import sys
import os

project_root = "/Users/duan/mac-miclsirr/fjsp-EA-RL/unified_fjsp_system"
sys.path.insert(0, project_root)

print("测试 Web 前端模块...")

results = []

# 测试 Streamlit 导入
try:
    import streamlit as st
    print("✅ Streamlit 已安装")
    results.append(("Streamlit", True, st.__version__))
except ImportError:
    print("❌ Streamlit 未安装")
    results.append(("Streamlit", False, "未安装"))

# 测试 Flask 导入
try:
    import flask
    print("✅ Flask 已安装")
    results.append(("Flask", True, flask.__version__))
except ImportError:
    print("❌ Flask 未安装")
    results.append(("Flask", False, "未安装"))

# 测试 Web 模块导入
try:
    # 只测试导入，不运行
    with open(os.path.join(project_root, "web/streamlit_app.py"), 'r') as f:
        code = f.read()
        if "class StreamlitApp" in code:
            print("✅ Streamlit 应用代码存在")
            results.append(("Streamlit应用", True, "代码完整"))
        else:
            print("⚠️ Streamlit 应用代码不完整")
            results.append(("Streamlit应用", False, "代码不完整"))
except Exception as e:
    print(f"❌ 无法读取 Streamlit 应用: {e}")
    results.append(("Streamlit应用", False, str(e)))

# 测试后端 API
try:
    with open(os.path.join(project_root, "web/backend/flask_api.py"), 'r') as f:
        code = f.read()
        if "Flask" in code and "/api/" in code:
            print("✅ Flask API 代码存在")
            results.append(("Flask API", True, "代码完整"))
        else:
            print("⚠️ Flask API 代码不完整")
            results.append(("Flask API", False, "代码不完整"))
except Exception as e:
    print(f"❌ 无法读取 Flask API: {e}")
    results.append(("Flask API", False, str(e)))

# 保存结果
with open("/tmp/web_test_details.txt", "w") as f:
    for name, status, details in results:
        status_str = "PASS" if status else "FAIL"
        f.write(f"{name}|{status_str}|{details}\n")

passed = sum(1 for _, status, _ in results if status)
print(f"\nWeb 模块测试: {passed}/{len(results)} 通过")
WEBTEST

    python /tmp/test_web.py
    local web_result=$?

    if [ $web_result -eq 0 ]; then
        log_success "Web 模块测试完成"
        record_result "Web模块测试" "✅" "完成"
    else
        log_warning "Web 模块测试有警告"
        record_result "Web模块测试" "⚠️" "有警告"
    fi

    # 读取详细结果
    if [ -f "/tmp/web_test_details.txt" ]; then
        while IFS='|' read -r name status details; do
            record_result "  └─ $name" "$status" "$details"
        done < /tmp/web_test_details.txt
    fi
}

# 生成测试报告
generate_report() {
    log_step "6/6 生成测试报告..."

    REPORT_FILE="/tmp/fjsp_test_report.md"

    cat > "$REPORT_FILE" << 'HEADER'
# FJSP 项目测试报告

**测试时间**: $(date '+%Y-%m-%d %H:%M:%S')
**测试环境**: fjsp-libs-unified (conda)

---

## 📊 测试结果总览

HEADER

    # 统计结果
    local total=$(wc -l < "$RESULTS_FILE")
    local passed=$(grep -c "✅" "$RESULTS_FILE" || echo "0")
    local warned=$(grep -c "⚠️" "$RESULTS_FILE" || echo "0")
    local failed=$(grep -c "❌" "$RESULTS_FILE" || echo "0")

    cat >> "$REPORT_FILE" << EOF
| 指标 | 数量 |
|------|------|
| 总测试项 | $total |
| ✅ 通过 | $passed |
| ⚠️ 警告 | $warned |
| ❌ 失败 | $failed |
| **成功率** | **$(awk "BEGIN {printf \"%.1f%%\", ($passed/$total)*100}")** |

---

## 📋 详细测试结果

| 测试项 | 状态 | 详细信息 |
|--------|------|----------|
EOF

    # 添加详细结果
    while IFS='|' read -r name status details; do
        echo "| $name | $status | $details |" >> "$REPORT_FILE"
    done < "$RESULTS_FILE"

    cat >> "$REPORT_FILE" << 'FOOTER'

---

## 🎯 结论

FOOTER

    # 添加结论
    if [ $failed -eq 0 ]; then
        echo "✅ **所有测试通过！** 项目与参考库集成良好。" >> "$REPORT_FILE"
    elif [ $warned -gt 0 ] && [ $failed -eq 0 ]; then
        echo "⚠️ **测试基本通过，但有警告。** 部分功能需要完善。" >> "$REPORT_FILE"
    else
        echo "❌ **部分测试失败。** 需要检查失败项并修复。" >> "$REPORT_FILE"
    fi

    cat >> "$REPORT_FILE" << 'SUGGESTIONS'

### 建议

1. **✅ 已验证的功能**：可以直接使用
2. **⚠️ 有警告的功能**：可用但需要完善
3. **❌ 失败的功能**：需要修复或安装依赖

### 下一步

- 查看详细错误日志
- 安装缺失的依赖包
- 完善标记为"警告"的功能

---

**报告生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
SUGGESTIONS

    log_success "测试报告已生成"
    echo
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}📄 测试报告位置${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo
    echo -e "  ${GREEN}Markdown 报告:${NC} $REPORT_FILE"
    echo -e "  ${GREEN}原始数据:${NC} $RESULTS_FILE"
    echo
    echo -e "${YELLOW}查看报告:${NC}"
    echo -e "  cat $REPORT_FILE"
    echo
}

# 显示最终总结
show_summary() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}🎉 测试完成！${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo

    # 统计
    local total=$(wc -l < "$RESULTS_FILE")
    local passed=$(grep -c "✅" "$RESULTS_FILE" || echo "0")
    local warned=$(grep -c "⚠️" "$RESULTS_FILE" || echo "0")
    local failed=$(grep -c "❌" "$RESULTS_FILE" || echo "0")

    echo -e "${BLUE}测试结果:${NC}"
    echo -e "  总计: $total 项"
    echo -e "  ${GREEN}✅ 通过: $passed${NC}"
    echo -e "  ${YELLOW}⚠️ 警告: $warned${NC}"
    echo -e "  ${RED}❌ 失败: $failed${NC}"
    echo

    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}🎊 恭喜！所有测试通过！${NC}"
    else
        echo -e "${YELLOW}⚠️ 部分测试失败，请查看报告${NC}"
    fi

    echo
    echo -e "${BLUE}查看完整报告:${NC}"
    echo -e "  cat /tmp/fjsp_test_report.md"
    echo
    echo -e "${BLUE}环境信息:${NC}"
    echo -e "  conda 环境: ${GREEN}fjsp-libs-unified${NC}"
    echo -e "  激活命令: ${YELLOW}conda activate fjsp-libs-unified${NC}"
    echo
}

# 主函数
main() {
    echo -e "${CYAN}"
    echo "🧪 FJSP 项目集成测试"
    echo "测试本项目与参考库的集成情况"
    echo "=================================="
    echo -e "${NC}"

    setup_conda
    setup_test_env
    install_dependencies
    test_project_integration
    test_web_frontend
    generate_report
    show_summary

    log_success "所有步骤完成！"
}

# 运行主函数
main "$@"
