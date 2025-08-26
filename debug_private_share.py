#!/usr/bin/env python
"""
调试私密分享功能
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

from knowledge_app.personal_quiz_models import QuizLibrary, LibraryShare

User = get_user_model()

def debug_private_share():
    """调试私密分享功能"""
    print("🔍 开始调试私密分享功能...")
    
    # 创建测试客户端
    client = Client()
    
    # 1. 检查用户和题库
    print("\n1️⃣ 检查用户和题库...")
    try:
        # 获取用户
        users = User.objects.all()[:5]
        print(f"✅ 系统中的用户:")
        for user in users:
            print(f"   • {user.username} (ID: {user.id}, 活跃: {user.is_active})")
        
        if len(users) < 2:
            print("❌ 需要至少2个用户来测试私密分享")
            return False
        
        user1 = users[0]  # 分享者
        user2 = users[1]  # 接收者
        
        # 获取题库
        library = QuizLibrary.objects.filter(owner=user1).first()
        if not library:
            print(f"❌ 用户 {user1.username} 没有题库")
            return False
        
        print(f"✅ 使用题库: {library.name} (ID: {library.id})")
        print(f"✅ 分享者: {user1.username}")
        print(f"✅ 接收者: {user2.username}")
        
    except Exception as e:
        print(f"❌ 检查用户和题库失败: {e}")
        return False
    
    # 2. 登录分享者
    print("\n2️⃣ 登录分享者...")
    try:
        client.force_login(user1)
        print(f"✅ 已登录用户: {user1.username}")
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return False
    
    # 3. 访问分享页面
    print("\n3️⃣ 访问分享页面...")
    try:
        share_url = reverse('knowledge_app:share_library', args=[library.id])
        response = client.get(share_url)
        
        if response.status_code == 200:
            print(f"✅ 分享页面访问成功: {share_url}")
        else:
            print(f"❌ 分享页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 访问分享页面失败: {e}")
        return False
    
    # 4. 测试私密分享POST请求
    print("\n4️⃣ 测试私密分享POST请求...")
    try:
        share_data = {
            'share_type': 'private',
            'shared_to_username': user2.username,
            'permission': 'copy',
            'message': '这是一个调试测试分享',
            'expires_days': '7'
        }
        
        print(f"📤 发送分享数据: {share_data}")
        
        response = client.post(share_url, share_data, follow=True)
        
        print(f"📥 响应状态码: {response.status_code}")
        if hasattr(response, 'redirect_chain'):
            print(f"📥 重定向链: {[r[0] for r in response.redirect_chain]}")
        else:
            print("📥 没有重定向")
        
        # 检查响应内容中的消息
        content = response.content.decode('utf-8')
        if '成功分享给' in content:
            print("✅ 发现成功消息")
        elif '请输入要分享给的用户名' in content:
            print("❌ 用户名为空错误")
        elif '不存在' in content:
            print("❌ 用户不存在错误")
        elif '不能分享给自己' in content:
            print("❌ 不能分享给自己错误")
        elif '已经分享给' in content:
            print("⚠️ 已经分享过了")
        else:
            print("⚠️ 未找到明确的错误或成功消息")
        
        # 检查数据库中的分享记录
        share = LibraryShare.objects.filter(
            library=library,
            shared_by=user1,
            shared_to=user2,
            share_type='private'
        ).first()
        
        if share:
            print(f"✅ 数据库中找到分享记录: {share}")
            print(f"   分享类型: {share.share_type}")
            print(f"   权限: {share.permission}")
            print(f"   留言: {share.message}")
            print(f"   是否活跃: {share.is_active}")
        else:
            print("❌ 数据库中未找到分享记录")
            
    except Exception as e:
        print(f"❌ 私密分享测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. 检查现有分享记录
    print("\n5️⃣ 检查现有分享记录...")
    try:
        all_shares = LibraryShare.objects.filter(library=library).order_by('-created_at')
        print(f"📊 题库 '{library.name}' 的所有分享记录:")
        
        for i, share in enumerate(all_shares, 1):
            print(f"   {i}. {share}")
            print(f"      类型: {share.share_type}")
            print(f"      分享给: {share.shared_to.username if share.shared_to else '公开'}")
            print(f"      权限: {share.permission}")
            print(f"      活跃: {share.is_active}")
            print(f"      创建时间: {share.created_at}")
            print()
            
    except Exception as e:
        print(f"❌ 检查分享记录失败: {e}")
        return False
    
    print("\n🎉 私密分享调试完成！")
    return True

def check_form_data():
    """检查表单数据处理"""
    print("\n" + "="*50)
    print("🔍 检查表单数据处理")
    print("="*50)
    
    try:
        # 模拟表单数据
        test_data = {
            'share_type': 'private',
            'shared_to_username': 'testuser',
            'permission': 'copy',
            'message': 'test message',
            'expires_days': '7'
        }
        
        print("📝 模拟表单数据:")
        for key, value in test_data.items():
            print(f"   {key}: '{value}'")
        
        # 检查数据类型
        share_type = test_data.get('share_type')
        shared_to_username = test_data.get('shared_to_username')
        permission = test_data.get('permission', 'view')
        message = test_data.get('message', '')
        expires_days = test_data.get('expires_days')
        
        print(f"\n📊 解析后的数据:")
        print(f"   share_type: '{share_type}' (类型: {type(share_type)})")
        print(f"   shared_to_username: '{shared_to_username}' (类型: {type(shared_to_username)})")
        print(f"   permission: '{permission}' (类型: {type(permission)})")
        print(f"   message: '{message}' (类型: {type(message)})")
        print(f"   expires_days: '{expires_days}' (类型: {type(expires_days)})")
        
        # 检查条件判断
        print(f"\n🔍 条件判断:")
        print(f"   share_type == 'private': {share_type == 'private'}")
        print(f"   shared_to_username 是否为空: {not shared_to_username}")
        print(f"   expires_days 是否为数字: {expires_days and expires_days.isdigit()}")
        
    except Exception as e:
        print(f"❌ 检查表单数据失败: {e}")

if __name__ == '__main__':
    try:
        success = debug_private_share()
        check_form_data()
        
        if success:
            print("\n✅ 私密分享调试完成！")
        else:
            print("\n❌ 私密分享调试发现问题！")
            
    except Exception as e:
        print(f"\n💥 调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
