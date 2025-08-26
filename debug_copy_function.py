#!/usr/bin/env python
"""
调试复制功能
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cs_learning_platform.settings')
django.setup()

from knowledge_app.personal_quiz_models import QuizLibrary, LibraryShare, LibraryCopy

User = get_user_model()

def debug_copy_function():
    """调试复制功能"""
    print("🔍 开始调试复制功能...")
    
    # 创建测试客户端
    client = Client()
    
    # 1. 获取测试数据
    print("\n1️⃣ 获取测试数据...")
    try:
        # 获取用户lyn
        user_lyn = User.objects.get(username='lyn')
        print(f"✅ 测试用户: {user_lyn.username}")
        
        # 获取lyn收到的分享
        shares = LibraryShare.objects.filter(shared_to=user_lyn, is_active=True)
        if not shares.exists():
            print("❌ 用户lyn没有收到任何分享")
            return False
        
        share = shares.first()
        print(f"✅ 找到分享: {share}")
        print(f"   分享ID: {share.id}")
        print(f"   题库: {share.library.name}")
        print(f"   权限: {share.permission}")
        print(f"   可以访问: {share.can_access(user_lyn)}")
        
    except Exception as e:
        print(f"❌ 获取测试数据失败: {e}")
        return False
    
    # 2. 登录用户
    print("\n2️⃣ 登录用户...")
    try:
        client.force_login(user_lyn)
        print(f"✅ 用户 {user_lyn.username} 登录成功")
    except Exception as e:
        print(f"❌ 用户登录失败: {e}")
        return False
    
    # 3. 测试复制API
    print("\n3️⃣ 测试复制API...")
    try:
        copy_url = reverse('knowledge_app:copy_shared_library', args=[share.id])
        print(f"📤 复制URL: {copy_url}")
        
        # 发送POST请求
        response = client.post(copy_url, content_type='application/json')
        print(f"📥 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📥 响应数据: {data}")
                
                if data.get('success'):
                    print("✅ 复制成功")
                    print(f"   消息: {data.get('message')}")
                    print(f"   新题库ID: {data.get('library_id')}")
                    print(f"   重定向URL: {data.get('redirect_url')}")
                    
                    # 检查数据库中的新题库
                    new_library_id = data.get('library_id')
                    if new_library_id:
                        new_library = QuizLibrary.objects.filter(id=new_library_id).first()
                        if new_library:
                            print(f"✅ 新题库已创建: {new_library.name}")
                            print(f"   所有者: {new_library.owner.username}")
                            print(f"   题目数量: {new_library.total_questions}")
                        else:
                            print("❌ 新题库未在数据库中找到")
                    
                    # 检查复制记录
                    copy_record = LibraryCopy.objects.filter(
                        copied_by=user_lyn,
                        share=share
                    ).first()
                    if copy_record:
                        print(f"✅ 复制记录已创建: {copy_record}")
                    else:
                        print("❌ 复制记录未找到")
                        
                else:
                    print(f"❌ 复制失败: {data.get('error')}")
                    return False
                    
            except Exception as e:
                print(f"❌ 解析响应数据失败: {e}")
                print(f"   响应内容: {response.content.decode('utf-8')}")
                return False
        else:
            print(f"❌ 复制请求失败: {response.status_code}")
            print(f"   响应内容: {response.content.decode('utf-8')}")
            return False
            
    except Exception as e:
        print(f"❌ 复制API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. 检查权限
    print("\n4️⃣ 检查权限...")
    try:
        print(f"   分享权限: {share.permission}")
        print(f"   权限允许复制: {share.permission in ['copy', 'edit']}")
        print(f"   用户可以访问: {share.can_access(user_lyn)}")
        print(f"   分享是否活跃: {share.is_active}")
        
        if share.expires_at:
            from django.utils import timezone
            print(f"   分享过期时间: {share.expires_at}")
            print(f"   是否已过期: {share.expires_at < timezone.now()}")
        else:
            print(f"   分享无过期时间")
            
    except Exception as e:
        print(f"❌ 权限检查失败: {e}")
        return False
    
    print("\n🎉 复制功能调试完成！")
    return True

def check_csrf_token():
    """检查CSRF token"""
    print("\n" + "="*50)
    print("🔍 检查CSRF token")
    print("="*50)
    
    try:
        client = Client()
        user_lyn = User.objects.get(username='lyn')
        client.force_login(user_lyn)
        
        # 访问收到的分享页面
        response = client.get('/quiz/shares/received/')
        print(f"收到的分享页面状态码: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'csrfmiddlewaretoken' in content:
                print("✅ 页面包含CSRF token")
                # 提取CSRF token
                import re
                csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', content)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
                    print(f"   CSRF token: {csrf_token[:20]}...")
                else:
                    print("⚠️ 无法提取CSRF token值")
            else:
                print("❌ 页面不包含CSRF token")
        else:
            print(f"❌ 页面访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ CSRF token检查失败: {e}")

def check_javascript_errors():
    """检查可能的JavaScript错误"""
    print("\n" + "="*50)
    print("🔍 检查JavaScript相关问题")
    print("="*50)
    
    try:
        # 检查模板中的JavaScript代码
        template_path = 'templates/knowledge_app/quiz/received_shares.html'
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查关键JavaScript代码
            if 'function copyLibrary' in content:
                print("✅ copyLibrary函数存在")
            else:
                print("❌ copyLibrary函数不存在")
                
            if 'fetch(' in content:
                print("✅ fetch API调用存在")
            else:
                print("❌ fetch API调用不存在")
                
            if 'X-CSRFToken' in content:
                print("✅ CSRF token头部设置存在")
            else:
                print("❌ CSRF token头部设置不存在")
                
            if 'getCookie' in content:
                print("✅ getCookie函数存在")
            else:
                print("❌ getCookie函数不存在")
                
        else:
            print(f"❌ 模板文件不存在: {template_path}")
            
    except Exception as e:
        print(f"❌ JavaScript检查失败: {e}")

if __name__ == '__main__':
    try:
        success = debug_copy_function()
        check_csrf_token()
        check_javascript_errors()
        
        if success:
            print("\n✅ 复制功能调试完成！")
        else:
            print("\n❌ 复制功能调试发现问题！")
            
    except Exception as e:
        print(f"\n💥 调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
