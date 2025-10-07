#!/usr/bin/env python3
"""
FJSP系统性能基准测试脚本
测试系统的各项性能指标和多目标优化功能
"""

import time
import json
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import concurrent.futures
import psutil
import os

class FJSPPerformanceBenchmark:
    def __init__(self, api_base="http://localhost:5001/api"):
        self.api_base = api_base
        self.results = {}
        self.test_instances = self.generate_test_instances()
        
    def generate_test_instances(self):
        """生成不同规模的测试实例"""
        instances = [
            {"name": "small", "num_jobs": 5, "num_machines": 3, "max_ops": 3},
            {"name": "medium", "num_jobs": 10, "num_machines": 5, "max_ops": 4},
            {"name": "large", "num_jobs": 20, "num_machines": 10, "max_ops": 5},
            {"name": "xlarge", "num_jobs": 50, "num_machines": 20, "max_ops": 6}
        ]
        return instances
    
    def test_api_performance(self):
        """测试API响应性能"""
        print("🔍 测试API性能...")
        
        api_tests = [
            ("health_check", "GET", "/health", None),
            ("create_instance", "POST", "/instances", {
                "type": "random", "num_jobs": 5, "num_machines": 3, 
                "max_operations_per_job": 3, "flexibility": 0.7
            })
        ]
        
        api_results = {}
        
        for test_name, method, endpoint, data in api_tests:
            times = []
            success_count = 0
            
            for _ in range(10):  # 每个API测试10次
                start_time = time.time()
                try:
                    if method == "GET":
                        response = requests.get(f"{self.api_base}{endpoint}", timeout=5)
                    else:
                        response = requests.post(f"{self.api_base}{endpoint}", 
                                               json=data, timeout=10)
                    
                    if response.status_code in [200, 201]:
                        success_count += 1
                    
                    times.append(time.time() - start_time)
                    
                except Exception as e:
                    print(f"❌ API测试失败: {e}")
                    times.append(float('inf'))
            
            api_results[test_name] = {
                "avg_response_time": np.mean(times),
                "min_response_time": np.min(times),
                "max_response_time": np.max(times),
                "success_rate": success_count / 10,
                "std_response_time": np.std(times)
            }
        
        self.results["api_performance"] = api_results
        return api_results
    
    def test_scalability(self):
        """测试系统可扩展性"""
        print("📈 测试系统可扩展性...")
        
        scalability_results = {}
        
        for instance_config in self.test_instances:
            print(f"  测试实例: {instance_config['name']}")
            
            # 创建实例
            start_time = time.time()
            try:
                response = requests.post(f"{self.api_base}/instances", 
                                       json={
                                           "type": "random",
                                           "num_jobs": instance_config["num_jobs"],
                                           "num_machines": instance_config["num_machines"],
                                           "max_operations_per_job": instance_config["max_ops"],
                                           "flexibility": 0.7
                                       }, timeout=30)
                
                creation_time = time.time() - start_time
                
                if response.status_code == 200:
                    instance_data = response.json()
                    
                    scalability_results[instance_config["name"]] = {
                        "creation_time": creation_time,
                        "num_jobs": instance_config["num_jobs"],
                        "num_machines": instance_config["num_machines"],
                        "num_operations": instance_data.get("num_operations", 0),
                        "memory_usage": self.get_memory_usage(),
                        "status": "success"
                    }
                else:
                    scalability_results[instance_config["name"]] = {
                        "status": "failed",
                        "error": f"HTTP {response.status_code}"
                    }
                    
            except Exception as e:
                scalability_results[instance_config["name"]] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        self.results["scalability"] = scalability_results
        return scalability_results
    
    def test_visualization_performance(self):
        """测试可视化性能"""
        print("🎨 测试可视化性能...")
        
        # 首先创建一个测试实例
        response = requests.post(f"{self.api_base}/instances", 
                               json={
                                   "type": "random", "num_jobs": 10, "num_machines": 5,
                                   "max_operations_per_job": 4, "flexibility": 0.7
                               })
        
        if response.status_code != 200:
            return {"error": "无法创建测试实例"}
        
        instance_id = response.json()["instance_id"]
        
        viz_tests = [
            ("disjunctive_graph_spring", f"/instances/{instance_id}/visualize/disjunctive_graph?layout=spring"),
            ("disjunctive_graph_hierarchical", f"/instances/{instance_id}/visualize/disjunctive_graph?layout=hierarchical"),
            ("disjunctive_graph_random", f"/instances/{instance_id}/visualize/disjunctive_graph?layout=random")
        ]
        
        viz_results = {}
        
        for test_name, endpoint in viz_tests:
            start_time = time.time()
            try:
                response = requests.get(f"{self.api_base}{endpoint}", timeout=30)
                generation_time = time.time() - start_time
                
                if response.status_code == 200:
                    content_size = len(response.content)
                    viz_results[test_name] = {
                        "generation_time": generation_time,
                        "content_size": content_size,
                        "status": "success"
                    }
                else:
                    viz_results[test_name] = {
                        "status": "failed",
                        "error": f"HTTP {response.status_code}"
                    }
                    
            except Exception as e:
                viz_results[test_name] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        self.results["visualization"] = viz_results
        return viz_results
    
    def test_concurrent_performance(self):
        """测试并发性能"""
        print("⚡ 测试并发性能...")
        
        def create_instance():
            """并发创建实例的函数"""
            try:
                response = requests.post(f"{self.api_base}/instances", 
                                       json={
                                           "type": "random", "num_jobs": 5, "num_machines": 3,
                                           "max_operations_per_job": 3, "flexibility": 0.7
                                       }, timeout=15)
                return {
                    "status": "success" if response.status_code == 200 else "failed",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
            except Exception as e:
                return {"status": "error", "error": str(e)}
        
        concurrent_levels = [1, 5, 10, 20]
        concurrent_results = {}
        
        for level in concurrent_levels:
            print(f"  测试并发级别: {level}")
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=level) as executor:
                futures = [executor.submit(create_instance) for _ in range(level)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            total_time = time.time() - start_time
            success_count = sum(1 for r in results if r["status"] == "success")
            
            concurrent_results[f"level_{level}"] = {
                "total_time": total_time,
                "success_rate": success_count / level,
                "throughput": level / total_time,
                "avg_response_time": np.mean([r.get("response_time", 0) for r in results if "response_time" in r])
            }
        
        self.results["concurrent"] = concurrent_results
        return concurrent_results
    
    def get_memory_usage(self):
        """获取当前内存使用情况"""
        process = psutil.Process(os.getpid())
        return {
            "rss": process.memory_info().rss / 1024 / 1024,  # MB
            "vms": process.memory_info().vms / 1024 / 1024,  # MB
            "percent": process.memory_percent()
        }
    
    def get_system_info(self):
        """获取系统信息"""
        return {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_total": psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
            "memory_available": psutil.virtual_memory().available / 1024 / 1024 / 1024,  # GB
            "memory_percent": psutil.virtual_memory().percent
        }
    
    def run_full_benchmark(self):
        """运行完整的基准测试"""
        print("🏭 开始FJSP系统性能基准测试")
        print("=" * 50)
        
        # 记录系统信息
        self.results["system_info"] = self.get_system_info()
        self.results["timestamp"] = datetime.now().isoformat()
        
        # 运行各项测试
        try:
            self.test_api_performance()
            self.test_scalability()
            self.test_visualization_performance()
            self.test_concurrent_performance()
            
            # 生成报告
            self.generate_report()
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
            return False
        
        return True
    
    def generate_report(self):
        """生成测试报告"""
        print("\n📊 生成性能测试报告...")
        
        # 保存JSON格式的详细结果
        with open("performance_benchmark_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # 生成Markdown报告
        self.generate_markdown_report()
        
        # 生成图表
        self.generate_charts()
        
        print("✅ 报告生成完成:")
        print("  - performance_benchmark_results.json (详细数据)")
        print("  - performance_report.md (Markdown报告)")
        print("  - performance_charts.png (性能图表)")
    
    def generate_markdown_report(self):
        """生成Markdown格式的报告"""
        report = f"""# FJSP系统性能测试报告

## 测试概述
- **测试时间**: {self.results['timestamp']}
- **系统配置**: {self.results['system_info']['cpu_count']}核CPU, {self.results['system_info']['memory_total']:.1f}GB内存

## API性能测试
"""
        
        if "api_performance" in self.results:
            for test_name, metrics in self.results["api_performance"].items():
                report += f"""
### {test_name}
- 平均响应时间: {metrics['avg_response_time']:.3f}s
- 成功率: {metrics['success_rate']:.1%}
- 响应时间标准差: {metrics['std_response_time']:.3f}s
"""
        
        report += "\n## 可扩展性测试\n"
        if "scalability" in self.results:
            report += "| 实例规模 | 工件数 | 机器数 | 创建时间(s) | 内存使用(MB) | 状态 |\n"
            report += "|---------|--------|--------|-------------|--------------|------|\n"
            
            for instance_name, metrics in self.results["scalability"].items():
                if metrics.get("status") == "success":
                    report += f"| {instance_name} | {metrics['num_jobs']} | {metrics['num_machines']} | {metrics['creation_time']:.3f} | {metrics['memory_usage']['rss']:.1f} | ✅ |\n"
                else:
                    report += f"| {instance_name} | - | - | - | - | ❌ |\n"
        
        with open("performance_report.md", "w", encoding="utf-8") as f:
            f.write(report)
    
    def generate_charts(self):
        """生成性能图表"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('FJSP系统性能测试结果', fontsize=16)
        
        # API响应时间图表
        if "api_performance" in self.results:
            api_data = self.results["api_performance"]
            test_names = list(api_data.keys())
            response_times = [api_data[name]["avg_response_time"] for name in test_names]
            
            axes[0, 0].bar(test_names, response_times)
            axes[0, 0].set_title('API平均响应时间')
            axes[0, 0].set_ylabel('时间 (秒)')
            axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 可扩展性图表
        if "scalability" in self.results:
            scalability_data = self.results["scalability"]
            instance_names = []
            creation_times = []
            job_counts = []
            
            for name, metrics in scalability_data.items():
                if metrics.get("status") == "success":
                    instance_names.append(name)
                    creation_times.append(metrics["creation_time"])
                    job_counts.append(metrics["num_jobs"])
            
            if creation_times:
                axes[0, 1].plot(job_counts, creation_times, 'o-')
                axes[0, 1].set_title('实例创建时间 vs 工件数')
                axes[0, 1].set_xlabel('工件数')
                axes[0, 1].set_ylabel('创建时间 (秒)')
        
        # 并发性能图表
        if "concurrent" in self.results:
            concurrent_data = self.results["concurrent"]
            levels = [int(k.split('_')[1]) for k in concurrent_data.keys()]
            throughputs = [concurrent_data[f"level_{level}"]["throughput"] for level in levels]
            
            axes[1, 0].plot(levels, throughputs, 'o-')
            axes[1, 0].set_title('并发吞吐量')
            axes[1, 0].set_xlabel('并发级别')
            axes[1, 0].set_ylabel('吞吐量 (请求/秒)')
        
        # 可视化性能图表
        if "visualization" in self.results:
            viz_data = self.results["visualization"]
            viz_names = []
            generation_times = []
            
            for name, metrics in viz_data.items():
                if metrics.get("status") == "success":
                    viz_names.append(name.replace("disjunctive_graph_", ""))
                    generation_times.append(metrics["generation_time"])
            
            if generation_times:
                axes[1, 1].bar(viz_names, generation_times)
                axes[1, 1].set_title('可视化生成时间')
                axes[1, 1].set_ylabel('时间 (秒)')
                axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('performance_charts.png', dpi=300, bbox_inches='tight')
        plt.close()

def main():
    """主函数"""
    print("🚀 启动FJSP系统性能基准测试")
    
    # 检查API连接
    try:
        response = requests.get("http://localhost:5001/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ 无法连接到FJSP API服务，请确保服务正在运行")
            print("💡 运行 ./start_system.sh 启动服务")
            return
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        print("💡 请确保FJSP系统正在运行")
        return
    
    # 运行基准测试
    benchmark = FJSPPerformanceBenchmark()
    success = benchmark.run_full_benchmark()
    
    if success:
        print("\n🎉 性能基准测试完成！")
        print("📊 查看生成的报告文件了解详细结果")
    else:
        print("\n❌ 性能基准测试失败")

if __name__ == "__main__":
    main()
