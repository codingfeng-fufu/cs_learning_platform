#!/usr/bin/env python3
"""
计算机科学学习平台 - 一键启动脚本

这个脚本会自动完成以下操作：
1. 检查Python版本
2. 安装项目依赖
3. 数据库迁移
4. 初始化示例数据
5. 启动开发服务器

运行方式:
python start.py

作者: CS学习平台
创建时间: 2025
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path


class Colors:
    """终端颜色定义"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_colored(message, color=Colors.OKGREEN):
    """打印彩色消息"""
    print(f"{color}{message}{Colors.ENDC}")


def print_step(step_num, description):
    """打印步骤信息"""
    print_colored(f"\n🔄 步骤 {step_num}: {description}", Colors.OKBLUE)


def print_success(message):
    """打印成功消息"""
    print_colored(f"✅ {message}", Colors.OKGREEN)


def print_warning(message):
    """打印警告消息"""
    print_colored(f"⚠️  {message}", Colors.WARNING)


def print_error(message):
    """打印错误消息"""
    print_colored(f"❌ {message}", Colors.FAIL)


def run_command(command, description, check=True, capture_output=True):
    """
    执行命令并显示结果

    Args:
        command (str): 要执行的命令
        description (str): 命令描述
        check (bool): 是否检查返回码
        capture_output (bool): 是否捕获输出

    Returns:
        bool: 命令是否执行成功
    """
    print(f"  执行: {command}")

    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                command,
                shell=True,
                check=check,
                capture_output=capture_output,
                text=True,
                encoding='utf-8'
            )
        else:
            result = subprocess.run(
                command.split(),
                check=check,
                capture_output=capture_output,
                text=True
            )

        if capture_output and result.stdout:
            print(f"  输出: {result.stdout.strip()}")

        print_success(f"{description} 完成")
        return True

    except subprocess.CalledProcessError as e:
        print_error(f"{description} 失败: {e}")
        if capture_output and e.stderr:
            print(f"  错误信息: {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print_error(f"命令未找到: {command.split()[0]}")
        return False


def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    required_major, required_minor = 3, 8

    print(f"当前Python版本: {version.major}.{version.minor}.{version.micro}")

    if version.major < required_major or (version.major == required_major and version.minor < required_minor):
        print_error(f"Python版本过低，需要 {required_major}.{required_minor}+ 版本")
        print_warning("请升级Python后重试")
        return False

    print_success(f"Python版本检查通过")
    return True


def check_project_structure():
    """检查项目结构"""
    required_files = [
        'manage.py',
        'requirements.txt',
        'cs_learning_platform/settings.py',
        'knowledge_app/models.py'
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print_error("缺少必要的项目文件:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print_warning("请确保所有项目文件都已正确创建")
        return False

    print_success("项目结构检查通过")
    return True


def install_dependencies():
    """安装项目依赖"""
    commands = [
        ("pip install --upgrade pip", "升级pip"),
        ("pip install -r requirements.txt", "安装项目依赖")
    ]

    for command, description in commands:
        if not run_command(command, description):
            print_warning(f"{description}失败，尝试继续运行...")

    return True


def setup_database():
    """设置数据库"""
    commands = [
        ("python manage.py makemigrations", "创建数据库迁移文件"),
        ("python manage.py migrate", "执行数据库迁移")
    ]

    for command, description in commands:
        if not run_command(command, description):
            print_error(f"数据库设置失败: {description}")
            return False

    return True


def initialize_data():
    """初始化示例数据"""
    commands = [
        ("python manage.py init_knowledge --clear", "初始化知识点数据")
    ]

    for command, description in commands:
        if not run_command(command, description):
            print_warning(f"{description}失败，可以稍后手动执行")

    return True


def create_superuser():
    """创建超级用户（可选）"""
    print("\n是否创建管理员账号? (y/n): ", end="")

    try:
        choice = input().lower().strip()
        if choice in ['y', 'yes', 'Y', 'YES']:
            success = run_command(
                "python manage.py create_superuser_auto",
                "创建超级用户",
                check=False
            )
            if not success:
                print_warning("自动创建超级用户失败，可以稍后使用 'python manage.py createsuperuser' 手动创建")
    except KeyboardInterrupt:
        print("\n跳过创建超级用户")


def start_server():
    """启动开发服务器"""
    print_step("FINAL", "启动开发服务器")

    print("\n" + "=" * 60)
    print_colored("🎉 准备启动开发服务器...", Colors.HEADER)
    print_colored("📝 访问地址: http://127.0.0.1:8000", Colors.OKBLUE)
    print_colored("🔧 管理后台: http://127.0.0.1:8000/admin/", Colors.OKBLUE)
    print_colored("⚠️  按 Ctrl+C 停止服务器", Colors.WARNING)
    print("=" * 60)

    # 倒计时
    for i in range(3, 0, -1):
        print(f"⏰ {i} 秒后启动服务器...", end="\r")
        time.sleep(1)
    print(" " * 30, end="\r")  # 清除倒计时

    try:
        # 不捕获输出，让服务器日志直接显示
        subprocess.run([sys.executable, "manage.py", "runserver"], check=True)
    except KeyboardInterrupt:
        print_colored("\n👋 服务器已停止", Colors.WARNING)
    except FileNotFoundError:
        print_error("无法找到 manage.py 文件")
    except Exception as e:
        print_error(f"启动服务器失败: {e}")


def show_banner():
    """显示横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║              🎓 计算机科学学习平台                      ║
    ║                CS Learning Platform                  ║
    ║                                                      ║
    ║  一键启动脚本 - 让部署变得简单                          ║
    ╚══════════════════════════════════════════════════════╝
    """
    print_colored(banner, Colors.HEADER)


def show_completion_info():
    """显示完成信息"""
    info = """
🎊 启动完成！你现在可以：

📖 学习功能：
   • 🧮 海明码编码解码 - http://127.0.0.1:8000/learn/hamming-code/
   • 🔍 CRC循环冗余检验 - http://127.0.0.1:8000/learn/crc-check/

🛠️  管理功能：
   • 📊 管理后台 - http://127.0.0.1:8000/admin/
   • 📋 API文档 - 查看views.py中的API接口

🔧 常用命令：
   • python manage.py list_knowledge        # 列出所有知识点
   • python manage.py init_knowledge        # 重新初始化数据
   • python manage.py createsuperuser       # 创建超级用户

📚 项目结构：
   • knowledge_app/algorithms/              # 算法实现
   • knowledge_app/templates/               # HTML模板
   • knowledge_app/management/commands/     # 管理命令

💡 添加新知识点：
   1. 在algorithms/目录添加算法实现
   2. 在templates/目录添加页面模板
   3. 在views.py添加对应的视图和API
   4. 更新数据库记录

❤️  感谢使用！如有问题请查看README.md或提交Issue。
    """
    print_colored(info, Colors.OKGREEN)


def main():
    """主函数"""
    show_banner()

    # 步骤1: 检查Python版本
    print_step(1, "检查Python版本")
    if not check_python_version():
        sys.exit(1)

    # 步骤2: 检查项目结构
    print_step(2, "检查项目结构")
    if not check_project_structure():
        sys.exit(1)

    # 步骤3: 安装依赖
    print_step(3, "安装项目依赖")
    install_dependencies()

    # 步骤4: 设置数据库
    print_step(4, "设置数据库")
    if not setup_database():
        print_error("数据库设置失败，请检查错误信息")
        sys.exit(1)

    # 步骤5: 初始化数据
    print_step(5, "初始化示例数据")
    initialize_data()

    # 步骤6: 创建超级用户（可选）
    print_step(6, "创建管理员账号（可选）")
    create_superuser()

    # 显示完成信息
    show_completion_info()

    # 最后: 启动服务器
    start_server()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n⏹️  启动过程被用户中断", Colors.WARNING)
        sys.exit(1)
    except Exception as e:
        print_error(f"意外错误: {e}")
        print_warning("请检查错误信息并重试，或手动执行各个步骤")
        sys.exit(1)