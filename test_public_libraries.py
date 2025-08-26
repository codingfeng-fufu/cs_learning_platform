#!/usr/bin/env python
"""
测试公开题库页面功能
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

def test_public_libraries_page():
    """测试公开题库页面"""
    print("🧪 开始测试公开题库页面...")
    
    # 创建测试客户端
    client = Client()
    
    # 1. 测试未登录用户访问
    print("\n1️⃣ 测试未登录用户访问公开题库页面...")
    try:
        public_url = reverse('knowledge_app:public_libraries')
        response = client.get(public_url)
        
        if response.status_code == 200:
            print(f"✅ 未登录用户可以访问公开题库页面")
            print(f"   页面大小: {len(response.content)} 字节")
        else:
            print(f"❌ 页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 页面访问失败: {e}")
        return False
    
    # 2. 测试登录用户访问
    print("\n2️⃣ 测试登录用户访问公开题库页面...")
    try:
        # 获取测试用户
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            # 尝试获取任何用户
            user = User.objects.first()
            if not user:
                print("❌ 未找到任何用户")
                return False
        print(f"✅ 使用测试用户: {user.username}")
        
        # 登录用户
        client.force_login(user)
        response = client.get(public_url)
        
        if response.status_code == 200:
            print(f"✅ 登录用户可以访问公开题库页面")
            print(f"   页面大小: {len(response.content)} 字节")
        else:
            print(f"❌ 登录用户页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 登录用户页面访问失败: {e}")
        return False
    
    # 3. 测试搜索功能
    print("\n3️⃣ 测试搜索功能...")
    try:
        search_url = f"{public_url}?search=测试"
        response = client.get(search_url)
        
        if response.status_code == 200:
            print(f"✅ 搜索功能正常")
            
            # 检查页面内容
            content = response.content.decode('utf-8')
            if '搜索' in content:
                print("✅ 搜索界面显示正常")
            else:
                print("⚠️ 搜索界面可能有问题")
        else:
            print(f"❌ 搜索功能失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 搜索功能测试失败: {e}")
        return False
    
    # 4. 检查公开分享数据
    print("\n4️⃣ 检查公开分享数据...")
    try:
        public_shares = LibraryShare.objects.filter(
            share_type='public',
            is_active=True
        ).count()
        
        print(f"✅ 当前公开分享数量: {public_shares}")
        
        if public_shares == 0:
            print("💡 提示: 当前没有公开分享，页面会显示空状态")
        else:
            print(f"✅ 有 {public_shares} 个公开分享可以显示")
            
    except Exception as e:
        print(f"❌ 数据检查失败: {e}")
        return False
    
    # 5. 创建一个公开分享用于测试
    print("\n5️⃣ 创建公开分享用于测试...")
    try:
        # 获取一个题库
        library = QuizLibrary.objects.first()
        if not library:
            print("❌ 没有找到题库")
            return False
        
        # 检查是否已经有公开分享
        existing_share = LibraryShare.objects.filter(
            library=library,
            share_type='public',
            is_active=True
        ).first()
        
        if not existing_share:
            # 创建公开分享
            public_share = LibraryShare.objects.create(
                library=library,
                shared_by=library.owner,
                share_type='public',
                permission='copy',
                message='这是一个测试公开分享'
            )
            print(f"✅ 创建公开分享成功: {public_share}")
        else:
            print(f"✅ 已存在公开分享: {existing_share}")
        
        # 再次访问公开题库页面
        response = client.get(public_url)
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if library.name in content:
                print("✅ 公开分享在页面中正确显示")
            else:
                print("⚠️ 公开分享可能未在页面中显示")
        
    except Exception as e:
        print(f"❌ 创建公开分享失败: {e}")
        return False
    
    print("\n🎉 公开题库页面测试完成！")
    return True

def print_public_shares_summary():
    """打印公开分享摘要"""
    print("\n" + "="*50)
    print("📊 公开分享摘要")
    print("="*50)
    
    try:
        # 统计公开分享
        public_shares = LibraryShare.objects.filter(
            share_type='public',
            is_active=True
        ).select_related('library', 'shared_by')
        
        print(f"🌍 公开分享总数: {public_shares.count()}")
        
        if public_shares.exists():
            print(f"\n📋 公开分享列表:")
            for i, share in enumerate(public_shares[:5], 1):
                print(f"   {i}. {share.library.name}")
                print(f"      分享者: {share.shared_by.username}")
                print(f"      权限: {share.get_permission_display}")
                print(f"      访问次数: {share.access_count}")
                print(f"      创建时间: {share.created_at.strftime('%Y-%m-%d %H:%M')}")
                if share.message:
                    print(f"      留言: {share.message}")
                print()
        else:
            print("   暂无公开分享")
        
    except Exception as e:
        print(f"❌ 统计数据获取失败: {e}")

if __name__ == '__main__':
    try:
        success = test_public_libraries_page()
        print_public_shares_summary()
        
        if success:
            print("\n✅ 公开题库页面测试通过！")
            print("💡 现在可以访问: http://127.0.0.1:8000/quiz/shares/public/")
            sys.exit(0)
        else:
            print("\n❌ 公开题库页面测试失败！")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
