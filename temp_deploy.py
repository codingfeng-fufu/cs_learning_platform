#!/usr/bin/env python3
"""
临时部署脚本 - 让别人可以访问您的Django网站
作者：冯宗林
使用方法：python temp_deploy.py
"""

import os
import sys
import socket
import subprocess
import threading
import time
from urllib.parse import urlparse

def get_local_ip():
    """获取本机IP地址"""
    try:
        # 连接到一个远程地址来获取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def check_port(port):
    """检查端口是否可用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def start_ngrok(port):
    """启动ngrok内网穿透"""
    try:
        print("🌐 正在启动ngrok内网穿透...")
        process = subprocess.Popen(
            ['ngrok', 'http', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待ngrok启动
        time.sleep(3)
        
        # 获取ngrok的公网地址
        try:
            import requests
            response = requests.get('http://localhost:4040/api/tunnels')
            tunnels = response.json()['tunnels']
            if tunnels:
                public_url = tunnels[0]['public_url']
                return public_url, process
        except:
            pass
            
        return None, process
    except FileNotFoundError:
        print("❌ 未找到ngrok，请先安装ngrok")
        return None, None

def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🚀 CS学习平台 - 临时部署工具")
    print("作者：冯宗林 (计科23级)")
    print("=" * 60)

def print_access_info(local_ip, port, ngrok_url=None):
    """打印访问信息"""
    print("\n✅ 服务器启动成功！")
    print("📍 访问地址：")
    print(f"   本地访问: http://localhost:{port}")
    print(f"   局域网访问: http://{local_ip}:{port}")
    
    if ngrok_url:
        print(f"   公网访问: {ngrok_url}")
        print("   🌍 任何人都可以通过公网地址访问您的网站！")
    else:
        print("   🏠 仅局域网内的用户可以访问")
    
    print("\n📋 分享给测试用户：")
    if ngrok_url:
        print(f"   请访问：{ngrok_url}")
    else:
        print(f"   请访问：http://{local_ip}:{port}")
        print("   注意：需要在同一WiFi网络下")
    
    print("\n⚠️  注意事项：")
    print("   - 这是临时部署，仅用于测试")
    print("   - 请不要在生产环境使用")
    print("   - 按 Ctrl+C 停止服务器")

def main():
    print_banner()
    
    # 检查Django项目
    if not os.path.exists('manage.py'):
        print("❌ 未找到manage.py文件，请在Django项目根目录运行此脚本")
        sys.exit(1)
    
    # 获取本机IP
    local_ip = get_local_ip()
    port = 8000
    
    # 检查端口
    if not check_port(port):
        print(f"❌ 端口 {port} 已被占用，请先停止其他服务")
        sys.exit(1)
    
    print(f"🔍 检测到本机IP: {local_ip}")
    
    # 询问是否使用ngrok
    use_ngrok = input("🌐 是否使用ngrok进行内网穿透？(y/N): ").lower().strip()
    
    ngrok_url = None
    ngrok_process = None
    
    if use_ngrok == 'y':
        ngrok_url, ngrok_process = start_ngrok(port)
        if not ngrok_url:
            print("⚠️  ngrok启动失败，将使用局域网访问模式")
    
    # 启动Django服务器
    print("🚀 正在启动Django服务器...")
    
    try:
        # 修改ALLOWED_HOSTS（如果需要）
        settings_path = 'cs_learning_platform/settings.py'
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "ALLOWED_HOSTS = ['*']" not in content:
                print("⚙️  正在修改ALLOWED_HOSTS设置...")
                content = content.replace(
                    "ALLOWED_HOSTS = []",
                    "ALLOWED_HOSTS = ['*']  # 临时设置，仅用于测试"
                )
                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        # 启动服务器
        django_process = subprocess.Popen([
            sys.executable, 'manage.py', 'runserver', f'0.0.0.0:{port}'
        ])
        
        # 等待服务器启动
        time.sleep(2)
        
        # 打印访问信息
        print_access_info(local_ip, port, ngrok_url)
        
        # 等待用户停止
        try:
            django_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 正在停止服务器...")
            django_process.terminate()
            if ngrok_process:
                ngrok_process.terminate()
            print("✅ 服务器已停止")
    
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        if ngrok_process:
            ngrok_process.terminate()

if __name__ == "__main__":
    main()
