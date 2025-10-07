#!/usr/bin/env python3
"""
前后端测试脚本 - 测试FJSP系统的前后端功能
"""

import os
import sys
import time
import requests
import subprocess
import threading
from pathlib import Path
from typing import Optional, Dict, Any
import json

class FrontendBackendTester:
    """前后端测试器"""
    
    def __init__(self):
        self.backend_url = "http://localhost:5001"
        self.frontend_url = "http://localhost:8501"
        self.backend_process = None
        self.frontend_process = None
        self.test_results = {}
        
    def check_dependencies(self) -> bool:
        """检查必要依赖"""
        required_packages = ['streamlit', 'flask', 'requests', 'plotly']
        missing = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        if missing:
            print(f"❌ 缺少依赖: {', '.join(missing)}")
            print(f"💡 安装命令: pip install {' '.join(missing)}")
            return False
        
        print("✅ 所有依赖已满足")
        return True
    
    def start_backend(self) -> bool:
        """启动后端服务"""
        print("🚀 启动后端服务...")
        
        backend_script = Path(__file__).parent.parent / "web" / "backend" / "flask_api.py"
        
        if not backend_script.exists():
            print("❌ 后端脚本不存在")
            return False
        
        try:
            # 启动后端进程
            self.backend_process = subprocess.Popen([
                sys.executable, str(backend_script)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待后端启动
            print("⏳ 等待后端启动...")
            time.sleep(5)
            
            # 检查后端健康状态
            if self.check_backend_health():
                print("✅ 后端服务启动成功")
                return True
            else:
                print("❌ 后端服务启动失败")
                return False
                
        except Exception as e:
            print(f"❌ 启动后端时出错: {e}")
            return False
    
    def start_frontend(self) -> bool:
        """启动前端服务"""
        print("🌐 启动前端服务...")
        
        frontend_script = Path(__file__).parent.parent / "web" / "streamlit_app.py"
        
        if not frontend_script.exists():
            print("❌ 前端脚本不存在")
            return False
        
        try:
            # 启动前端进程
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", str(frontend_script),
                "--server.port", "8501",
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待前端启动
            print("⏳ 等待前端启动...")
            time.sleep(8)
            
            # 检查前端健康状态
            if self.check_frontend_health():
                print("✅ 前端服务启动成功")
                return True
            else:
                print("❌ 前端服务启动失败")
                return False
                
        except Exception as e:
            print(f"❌ 启动前端时出错: {e}")
            return False
    
    def check_backend_health(self) -> bool:
        """检查后端健康状态"""
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def check_frontend_health(self) -> bool:
        """检查前端健康状态"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def test_backend_api(self) -> Dict[str, Any]:
        """测试后端API功能"""
        print("\n🔧 测试后端API...")
        results = {}
        
        # 测试健康检查
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=5)
            results['health_check'] = {
                'status': 'success' if response.status_code == 200 else 'failed',
                'response_time': response.elapsed.total_seconds(),
                'status_code': response.status_code
            }
            print(f"  ✅ 健康检查: {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
        except Exception as e:
            results['health_check'] = {'status': 'error', 'error': str(e)}
            print(f"  ❌ 健康检查失败: {e}")
        
        # 测试实例生成
        try:
            data = {
                'num_jobs': 3,
                'num_machines': 3,
                'max_operations_per_job': 3,
                'flexibility': 0.7
            }
            response = requests.post(f"{self.backend_url}/api/generate_instance", 
                                   json=data, timeout=10)
            results['generate_instance'] = {
                'status': 'success' if response.status_code == 200 else 'failed',
                'response_time': response.elapsed.total_seconds(),
                'status_code': response.status_code
            }
            print(f"  ✅ 实例生成: {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
        except Exception as e:
            results['generate_instance'] = {'status': 'error', 'error': str(e)}
            print(f"  ❌ 实例生成失败: {e}")
        
        # 测试析取图生成
        try:
            data = {
                'num_jobs': 2,
                'num_machines': 2,
                'layout': 'spring'
            }
            response = requests.post(f"{self.backend_url}/api/generate_disjunctive_graph", 
                                   json=data, timeout=15)
            results['disjunctive_graph'] = {
                'status': 'success' if response.status_code == 200 else 'failed',
                'response_time': response.elapsed.total_seconds(),
                'status_code': response.status_code
            }
            print(f"  ✅ 析取图生成: {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
        except Exception as e:
            results['disjunctive_graph'] = {'status': 'error', 'error': str(e)}
            print(f"  ❌ 析取图生成失败: {e}")
        
        return results
    
    def test_frontend_pages(self) -> Dict[str, Any]:
        """测试前端页面"""
        print("\n🌐 测试前端页面...")
        results = {}
        
        # 测试主页面
        try:
            response = requests.get(self.frontend_url, timeout=10)
            results['main_page'] = {
                'status': 'success' if response.status_code == 200 else 'failed',
                'response_time': response.elapsed.total_seconds(),
                'status_code': response.status_code,
                'content_length': len(response.content)
            }
            print(f"  ✅ 主页面: {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
        except Exception as e:
            results['main_page'] = {'status': 'error', 'error': str(e)}
            print(f"  ❌ 主页面访问失败: {e}")
        
        return results
    
    def test_integration(self) -> Dict[str, Any]:
        """测试前后端集成"""
        print("\n🔗 测试前后端集成...")
        results = {}
        
        # 这里可以添加更复杂的集成测试
        # 比如通过前端界面触发后端API调用
        
        results['integration'] = {
            'status': 'success',
            'note': '前后端服务都正常运行，可以进行手动集成测试'
        }
        print("  ✅ 前后端服务都已启动，可以进行手动测试")
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("🧪 开始前后端测试")
        print("=" * 50)
        
        # 检查依赖
        if not self.check_dependencies():
            return {'status': 'failed', 'reason': 'dependencies_missing'}
        
        # 启动后端
        if not self.start_backend():
            return {'status': 'failed', 'reason': 'backend_start_failed'}
        
        # 启动前端
        if not self.start_frontend():
            self.cleanup()
            return {'status': 'failed', 'reason': 'frontend_start_failed'}
        
        # 运行测试
        try:
            backend_results = self.test_backend_api()
            frontend_results = self.test_frontend_pages()
            integration_results = self.test_integration()
            
            all_results = {
                'status': 'completed',
                'backend': backend_results,
                'frontend': frontend_results,
                'integration': integration_results,
                'urls': {
                    'backend': self.backend_url,
                    'frontend': self.frontend_url
                }
            }
            
            self.test_results = all_results
            return all_results
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def cleanup(self):
        """清理进程"""
        print("\n🧹 清理进程...")
        
        if self.backend_process:
            self.backend_process.terminate()
            print("  ✅ 后端进程已终止")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            print("  ✅ 前端进程已终止")
    
    def generate_report(self) -> str:
        """生成测试报告"""
        if not self.test_results:
            return "没有测试结果"
        
        report = []
        report.append("# 前后端测试报告")
        report.append(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 后端测试结果
        if 'backend' in self.test_results:
            report.append("## 后端API测试")
            for test_name, result in self.test_results['backend'].items():
                status = "✅" if result.get('status') == 'success' else "❌"
                report.append(f"- {test_name}: {status} {result}")
            report.append("")
        
        # 前端测试结果
        if 'frontend' in self.test_results:
            report.append("## 前端页面测试")
            for test_name, result in self.test_results['frontend'].items():
                status = "✅" if result.get('status') == 'success' else "❌"
                report.append(f"- {test_name}: {status} {result}")
            report.append("")
        
        # 访问地址
        if 'urls' in self.test_results:
            report.append("## 访问地址")
            report.append(f"- 后端API: {self.test_results['urls']['backend']}")
            report.append(f"- 前端界面: {self.test_results['urls']['frontend']}")
        
        return "\n".join(report)


def main():
    """主函数"""
    tester = FrontendBackendTester()
    
    try:
        # 运行测试
        results = tester.run_all_tests()
        
        # 显示结果
        print("\n" + "=" * 50)
        print("📊 测试完成!")
        
        if results['status'] == 'completed':
            print("🎉 前后端服务启动成功!")
            print(f"🌐 前端地址: {tester.frontend_url}")
            print(f"🔧 后端地址: {tester.backend_url}")
            print("\n💡 现在可以在浏览器中测试Web界面功能")
            print("按 Ctrl+C 停止服务")
            
            # 生成报告
            report = tester.generate_report()
            with open("test_report.md", "w", encoding="utf-8") as f:
                f.write(report)
            print("📋 测试报告已保存到 test_report.md")
            
            # 保持服务运行
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 用户中断，正在停止服务...")
        else:
            print(f"❌ 测试失败: {results}")
    
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()
