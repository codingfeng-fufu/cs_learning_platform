#!/usr/bin/env python
"""
生产环境启动脚本
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

def setup_environment():
    """设置生产环境"""
    print("🔧 设置生产环境...")
    
    # 设置环境变量
    env_vars = {
        'DJANGO_SETTINGS_MODULE': 'cs_learning_platform.settings',
        'START_SCHEDULER': 'true',
        'RUN_MAIN': 'true',
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"  设置 {key}={value}")
    
    # 检查必需的环境变量
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  缺少环境变量: {', '.join(missing_vars)}")
        print("请设置这些环境变量后重新启动")
        
        # 提供示例
        print("\n示例:")
        for var in missing_vars:
            if var == 'OPENAI_API_KEY':
                print(f"export {var}='your-openai-api-key-here'")
            else:
                print(f"export {var}='your-value-here'")
        
        return False
    
    return True

def optimize_system():
    """系统优化"""
    print("⚡ 执行系统优化...")
    
    try:
        # 运行内存优化
        print("  运行内存优化...")
        subprocess.run([sys.executable, 'memory_optimization.py'], check=True)
        
        # 运行静态资源优化
        print("  优化静态资源...")
        subprocess.run([sys.executable, 'optimize_static_resources.py'], check=True)
        
        print("✅ 系统优化完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 优化失败: {e}")
        return False

def check_dependencies():
    """检查依赖"""
    print("📦 检查依赖...")
    
    required_packages = [
        'django',
        'pytz', 
        'apscheduler',
        'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("正在自动安装...")
        
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages, check=True)
            print("✅ 依赖安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败，请手动安装")
            return False
    
    return True

def prepare_database():
    """准备数据库"""
    print("🗄️ 准备数据库...")
    
    try:
        # 检查迁移
        print("  检查数据库迁移...")
        subprocess.run([
            sys.executable, 'manage.py', 'makemigrations', '--check'
        ], check=True, capture_output=True)
        
        # 应用迁移
        print("  应用数据库迁移...")
        subprocess.run([
            sys.executable, 'manage.py', 'migrate', '--noinput'
        ], check=True)
        
        print("✅ 数据库准备完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 数据库准备失败: {e}")
        return False

def collect_static():
    """收集静态文件"""
    print("📁 收集静态文件...")
    
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'collectstatic', '--noinput'
        ], check=True)
        
        print("✅ 静态文件收集完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 静态文件收集失败: {e}")
        return False

def start_scheduler():
    """启动调度器"""
    print("⏰ 启动调度器...")
    
    try:
        # 检查调度器状态
        result = subprocess.run([
            sys.executable, 'manage.py', 'scheduler_status'
        ], capture_output=True, text=True)
        
        if "运行正常" in result.stdout:
            print("✅ 调度器已在运行")
        else:
            print("  启动调度器...")
            # 这里不直接启动，因为调度器会在Django启动时自动启动
            print("✅ 调度器将在Django启动时自动启动")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  调度器检查失败: {e}")
        return True  # 不阻止启动

def health_check():
    """健康检查"""
    print("🏥 执行健康检查...")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'health_check'
        ], capture_output=True, text=True, timeout=30)
        
        if "HEALTHY" in result.stdout or "WARNING" in result.stdout:
            print("✅ 健康检查通过")
            return True
        else:
            print("⚠️  健康检查发现问题:")
            print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  健康检查超时")
        return False
    except subprocess.CalledProcessError as e:
        print(f"⚠️  健康检查失败: {e}")
        return False

def start_django_server():
    """启动Django服务器"""
    print("🚀 启动Django服务器...")
    
    try:
        # 使用开发服务器（生产环境建议使用Gunicorn）
        cmd = [sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000']
        
        print(f"执行命令: {' '.join(cmd)}")
        print("服务器将在 http://0.0.0.0:8000 启动")
        print("按 Ctrl+C 停止服务器")
        
        # 启动服务器
        process = subprocess.Popen(cmd)
        
        # 等待启动
        time.sleep(5)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ Django服务器启动成功")
            
            # 等待进程结束
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n⏹️  收到停止信号，正在关闭服务器...")
                process.terminate()
                process.wait()
                print("✅ 服务器已停止")
        else:
            print("❌ Django服务器启动失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 启动服务器时出错: {e}")
        return False

def main():
    """主函数"""
    print("🚀 CS Learning Platform 生产环境启动")
    print("=" * 60)
    
    # 检查当前目录
    if not Path('manage.py').exists():
        print("❌ 请在Django项目根目录下运行此脚本")
        sys.exit(1)
    
    # 执行启动步骤
    steps = [
        ("环境设置", setup_environment),
        ("依赖检查", check_dependencies),
        ("系统优化", optimize_system),
        ("数据库准备", prepare_database),
        ("静态文件收集", collect_static),
        ("调度器启动", start_scheduler),
        ("健康检查", health_check),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ {step_name}失败，启动中止")
            sys.exit(1)
        print(f"✅ {step_name}完成")
    
    print("\n" + "=" * 60)
    print("🎉 所有准备工作完成，启动Django服务器...")
    print("=" * 60)
    
    # 启动Django服务器
    start_django_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  启动已中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 启动过程中出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
