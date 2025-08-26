#!/usr/bin/env python
"""
安装定时调度器依赖的脚本
"""

import subprocess
import sys
import os

def install_package(package_name):
    """安装Python包"""
    try:
        print(f"📦 正在安装 {package_name}...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', package_name
        ], capture_output=True, text=True, check=True)
        
        print(f"✅ {package_name} 安装成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {package_name} 安装失败:")
        print(f"   错误信息: {e.stderr}")
        return False

def check_package(package_name):
    """检查包是否已安装"""
    try:
        __import__(package_name)
        print(f"✅ {package_name} 已安装")
        return True
    except ImportError:
        print(f"❌ {package_name} 未安装")
        return False

def main():
    print("🚀 定时调度器依赖安装工具")
    print("=" * 40)
    
    # 需要安装的包
    packages = [
        'apscheduler',  # 高级定时任务调度器
        'pytz',         # 时区处理（通常已安装）
    ]
    
    print("🔍 检查当前安装状态...")
    
    # 检查已安装的包
    installed = []
    need_install = []
    
    for package in packages:
        if check_package(package):
            installed.append(package)
        else:
            need_install.append(package)
    
    if not need_install:
        print("\n🎉 所有依赖都已安装！")
        return True
    
    print(f"\n📋 需要安装的包: {', '.join(need_install)}")
    
    # 询问是否安装
    response = input("\n是否现在安装这些包？(y/n): ").lower().strip()
    if response not in ['y', 'yes', '是']:
        print("⏸️  安装已取消")
        return False
    
    # 安装包
    success_count = 0
    for package in need_install:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 安装结果: {success_count}/{len(need_install)} 个包安装成功")
    
    if success_count == len(need_install):
        print("🎉 所有依赖安装完成！")
        print("\n💡 现在您可以使用高级定时调度器了")
        print("   重启Django服务器以启用新的调度器")
        return True
    else:
        print("⚠️  部分依赖安装失败，将使用基础调度器")
        return False

def create_requirements_file():
    """创建requirements文件"""
    requirements_content = """# 定时调度器依赖
apscheduler>=3.10.0
pytz>=2023.3
"""
    
    with open('scheduler_requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    print("📝 已创建 scheduler_requirements.txt 文件")
    print("   您也可以使用: pip install -r scheduler_requirements.txt")

if __name__ == "__main__":
    try:
        success = main()
        
        # 创建requirements文件
        create_requirements_file()
        
        if success:
            print("\n🔧 使用说明:")
            print("1. 重启Django服务器")
            print("2. 查看控制台输出，确认调度器启动")
            print("3. 调度器将在每天00:00自动生成名词")
            print("4. 使用 python manage.py scheduler_status 查看状态")
        
    except KeyboardInterrupt:
        print("\n⏸️  安装已中断")
    except Exception as e:
        print(f"\n❌ 安装过程出错: {e}")
        import traceback
        traceback.print_exc()
