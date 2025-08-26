#!/usr/bin/env python
"""
测试学习仪表板页面的脚本
"""
import requests
import json

# 测试配置
BASE_URL = 'http://localhost:8000'
LOGIN_URL = f'{BASE_URL}/users/login/'
DASHBOARD_URL = f'{BASE_URL}/users/learning-dashboard/'

# 测试用户凭据
TEST_EMAIL = 'admin@example.com'
TEST_PASSWORD = 'admin123'

def test_dashboard():
    """测试学习仪表板"""
    session = requests.Session()
    
    try:
        # 1. 获取登录页面（获取CSRF token）
        print("1. 获取登录页面...")
        login_page = session.get(LOGIN_URL)
        print(f"登录页面状态: {login_page.status_code}")
        
        # 从页面中提取CSRF token
        csrf_token = None
        for line in login_page.text.split('\n'):
            if 'csrfmiddlewaretoken' in line and 'value=' in line:
                start = line.find('value="') + 7
                end = line.find('"', start)
                csrf_token = line[start:end]
                break
        
        if not csrf_token:
            print("❌ 无法获取CSRF token")
            return
        
        print(f"✅ CSRF token: {csrf_token[:20]}...")
        
        # 2. 登录
        print("2. 尝试登录...")
        login_data = {
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_response = session.post(LOGIN_URL, data=login_data)
        print(f"登录响应状态: {login_response.status_code}")
        
        if login_response.status_code == 200 and 'login' not in login_response.url:
            print("✅ 登录成功")
        else:
            print("❌ 登录失败")
            print(f"重定向到: {login_response.url}")
            return
        
        # 3. 访问学习仪表板
        print("3. 访问学习仪表板...")
        dashboard_response = session.get(DASHBOARD_URL)
        print(f"仪表板页面状态: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            print("✅ 学习仪表板页面加载成功")
            
            # 检查页面内容
            content = dashboard_response.text
            if '学习仪表板' in content:
                print("✅ 页面标题正确")
            if '学习进度详情' in content:
                print("✅ 进度详情部分存在")
            if '学习日历' in content:
                print("✅ 学习日历部分存在")
            if 'chart-container' in content:
                print("✅ 图表容器存在")
                
            print(f"页面长度: {len(content)} 字符")
            
        else:
            print("❌ 学习仪表板页面加载失败")
            print(f"状态码: {dashboard_response.status_code}")
        
        # 4. 测试API端点
        print("4. 测试API端点...")
        
        # 测试学习统计API
        stats_response = session.get(f'{BASE_URL}/users/api/learning-stats/')
        print(f"学习统计API状态: {stats_response.status_code}")
        
        # 测试周图表API
        weekly_response = session.get(f'{BASE_URL}/users/api/weekly-chart/')
        print(f"周图表API状态: {weekly_response.status_code}")
        
        # 测试日历API
        calendar_response = session.get(f'{BASE_URL}/users/api/learning-calendar/')
        print(f"日历API状态: {calendar_response.status_code}")
        
        if all(r.status_code == 200 for r in [stats_response, weekly_response, calendar_response]):
            print("✅ 所有API端点正常工作")
        else:
            print("⚠️ 部分API端点可能有问题")
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")

if __name__ == '__main__':
    print("🧪 开始测试学习仪表板...")
    test_dashboard()
    print("🏁 测试完成")
