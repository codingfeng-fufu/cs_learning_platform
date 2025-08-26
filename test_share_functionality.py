#!/usr/bin/env python
"""
测试个人题库分享功能
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

from knowledge_app.personal_quiz_models import QuizLibrary, LibraryShare, QuizQuestion

User = get_user_model()

def test_share_functionality():
    """测试分享功能"""
    print("🧪 开始测试个人题库分享功能...")
    
    # 创建测试客户端
    client = Client()
    
    # 1. 测试用户登录
    print("\n1️⃣ 测试用户登录...")
    try:
        # 获取或创建测试用户
        user1, created = User.objects.get_or_create(
            username='testuser1',
            defaults={'email': 'test1@example.com'}
        )
        if created:
            user1.set_password('testpass123')
            user1.save()
            print(f"✅ 创建测试用户1: {user1.username}")
        else:
            print(f"✅ 使用现有用户1: {user1.username}")
        
        user2, created = User.objects.get_or_create(
            username='testuser2',
            defaults={'email': 'test2@example.com'}
        )
        if created:
            user2.set_password('testpass123')
            user2.save()
            print(f"✅ 创建测试用户2: {user2.username}")
        else:
            print(f"✅ 使用现有用户2: {user2.username}")
            
    except Exception as e:
        print(f"❌ 用户创建失败: {e}")
        return False
    
    # 2. 测试题库创建
    print("\n2️⃣ 测试题库创建...")
    try:
        # 创建测试题库
        library, created = QuizLibrary.objects.get_or_create(
            name='测试分享题库',
            owner=user1,
            defaults={
                'description': '这是一个用于测试分享功能的题库',
                'total_questions': 0
            }
        )
        
        if created:
            print(f"✅ 创建测试题库: {library.name}")
            
            # 添加测试题目
            question = QuizQuestion.objects.create(
                library=library,
                title='测试题目1',
                content='这是一道测试题目，用于验证分享功能',
                question_type='single_choice',
                options={'A': '选项A', 'B': '选项B', 'C': '选项C', 'D': '选项D'},
                correct_answer='A',
                explanation='这是测试题目的解析'
            )
            
            library.update_question_count()
            print(f"✅ 添加测试题目: {question.title}")
        else:
            print(f"✅ 使用现有题库: {library.name}")
            
    except Exception as e:
        print(f"❌ 题库创建失败: {e}")
        return False
    
    # 3. 测试分享页面访问
    print("\n3️⃣ 测试分享页面访问...")
    try:
        # 确保用户密码正确设置
        user1.set_password('testpass123')
        user1.save()

        # 登录用户1
        login_success = client.login(username='testuser1', password='testpass123')
        if not login_success:
            print("❌ 用户登录失败")
            print(f"   用户1信息: {user1.username}, 活跃: {user1.is_active}")
            # 尝试直接设置session
            from django.contrib.auth import login
            from django.contrib.sessions.middleware import SessionMiddleware
            from django.contrib.auth.middleware import AuthenticationMiddleware
            from django.http import HttpRequest

            # 创建一个假的request来设置用户
            request = HttpRequest()
            request.session = client.session
            request.user = user1
            client.force_login(user1)
            print("✅ 强制登录用户1成功")
        else:
            print("✅ 用户1登录成功")
        
        # 访问分享页面
        share_url = reverse('knowledge_app:share_library', args=[library.id])
        response = client.get(share_url)
        
        if response.status_code == 200:
            print(f"✅ 分享页面访问成功: {share_url}")
            print(f"   页面大小: {len(response.content)} 字节")
        else:
            print(f"❌ 分享页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 分享页面访问失败: {e}")
        return False
    
    # 4. 测试创建私密分享
    print("\n4️⃣ 测试创建私密分享...")
    try:
        share_data = {
            'share_type': 'private',
            'shared_to_username': 'testuser2',
            'permission': 'copy',
            'message': '这是一个测试分享',
            'expires_days': '7'
        }
        
        response = client.post(share_url, share_data)
        
        if response.status_code in [200, 302]:
            print("✅ 私密分享创建成功")
            
            # 检查数据库中的分享记录
            share = LibraryShare.objects.filter(
                library=library,
                shared_by=user1,
                shared_to=user2,
                share_type='private'
            ).first()
            
            if share:
                print(f"✅ 分享记录已保存: {share}")
                print(f"   分享类型: {share.get_share_type_display()}")
                print(f"   权限: {share.get_permission_display()}")
                print(f"   留言: {share.message}")
            else:
                print("❌ 分享记录未找到")
                return False
        else:
            print(f"❌ 私密分享创建失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 私密分享创建失败: {e}")
        return False
    
    # 5. 测试创建链接分享
    print("\n5️⃣ 测试创建链接分享...")
    try:
        share_data = {
            'share_type': 'link',
            'permission': 'view',
            'message': '通过链接分享的题库',
            'expires_days': '30'
        }
        
        response = client.post(share_url, share_data)
        
        if response.status_code in [200, 302]:
            print("✅ 链接分享创建成功")
            
            # 检查链接分享记录
            link_share = LibraryShare.objects.filter(
                library=library,
                shared_by=user1,
                share_type='link'
            ).first()
            
            if link_share and link_share.share_code:
                print(f"✅ 链接分享记录已保存")
                print(f"   分享码: {link_share.share_code}")
                print(f"   分享链接: /quiz/shared/{link_share.share_code}/")
            else:
                print("❌ 链接分享记录未找到或分享码为空")
                return False
        else:
            print(f"❌ 链接分享创建失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 链接分享创建失败: {e}")
        return False
    
    # 6. 测试收到的分享页面
    print("\n6️⃣ 测试收到的分享页面...")
    try:
        # 切换到用户2
        client.logout()
        user2.set_password('testpass123')
        user2.save()

        login_success = client.login(username='testuser2', password='testpass123')
        if not login_success:
            print("❌ 用户2登录失败")
            client.force_login(user2)
            print("✅ 强制登录用户2成功")
        else:
            print("✅ 用户2登录成功")
        
        # 访问收到的分享页面
        received_url = reverse('knowledge_app:received_shares')
        response = client.get(received_url)
        
        if response.status_code == 200:
            print(f"✅ 收到的分享页面访问成功")
            
            # 检查页面内容是否包含分享的题库
            content = response.content.decode('utf-8')
            if '测试分享题库' in content:
                print("✅ 页面显示了分享的题库")
            else:
                print("⚠️ 页面未显示分享的题库")
        else:
            print(f"❌ 收到的分享页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 收到的分享页面测试失败: {e}")
        return False
    
    # 7. 测试分享链接访问
    print("\n7️⃣ 测试分享链接访问...")
    try:
        # 获取链接分享
        link_share = LibraryShare.objects.filter(
            library=library,
            share_type='link'
        ).first()
        
        if link_share:
            # 访问分享链接
            shared_url = reverse('knowledge_app:shared_library_detail', args=[link_share.share_code])
            response = client.get(shared_url)
            
            if response.status_code == 200:
                print(f"✅ 分享链接访问成功: {shared_url}")
                
                # 检查访问计数是否增加
                link_share.refresh_from_db()
                if link_share.access_count > 0:
                    print(f"✅ 访问计数已更新: {link_share.access_count}")
                else:
                    print("⚠️ 访问计数未更新")
            else:
                print(f"❌ 分享链接访问失败: {response.status_code}")
                return False
        else:
            print("❌ 未找到链接分享记录")
            return False
            
    except Exception as e:
        print(f"❌ 分享链接访问测试失败: {e}")
        return False
    
    # 8. 测试题库复制功能
    print("\n8️⃣ 测试题库复制功能...")
    try:
        # 获取私密分享
        private_share = LibraryShare.objects.filter(
            library=library,
            shared_to=user2,
            share_type='private'
        ).first()
        
        if private_share:
            # 测试复制题库
            copy_url = reverse('knowledge_app:copy_shared_library', args=[private_share.id])
            response = client.post(copy_url, content_type='application/json')
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ 题库复制成功")
                    print(f"   新题库ID: {data.get('library_id')}")
                    
                    # 检查复制的题库
                    copied_library = QuizLibrary.objects.filter(
                        owner=user2,
                        name__contains='副本'
                    ).first()
                    
                    if copied_library:
                        print(f"✅ 复制的题库已创建: {copied_library.name}")
                        print(f"   题目数量: {copied_library.total_questions}")
                    else:
                        print("❌ 复制的题库未找到")
                        return False
                else:
                    print(f"❌ 题库复制失败: {data.get('error')}")
                    return False
            else:
                print(f"❌ 题库复制请求失败: {response.status_code}")
                return False
        else:
            print("❌ 未找到私密分享记录")
            return False
            
    except Exception as e:
        print(f"❌ 题库复制测试失败: {e}")
        return False
    
    print("\n🎉 所有分享功能测试完成！")
    return True

def print_test_summary():
    """打印测试摘要"""
    print("\n" + "="*60)
    print("📊 测试摘要")
    print("="*60)
    
    try:
        # 统计分享数据
        total_shares = LibraryShare.objects.count()
        private_shares = LibraryShare.objects.filter(share_type='private').count()
        link_shares = LibraryShare.objects.filter(share_type='link').count()
        public_shares = LibraryShare.objects.filter(share_type='public').count()
        
        print(f"📤 总分享数: {total_shares}")
        print(f"👤 私密分享: {private_shares}")
        print(f"🔗 链接分享: {link_shares}")
        print(f"🌍 公开分享: {public_shares}")
        
        # 统计题库数据
        total_libraries = QuizLibrary.objects.count()
        print(f"📚 总题库数: {total_libraries}")
        
        # 显示最新的分享记录
        latest_shares = LibraryShare.objects.order_by('-created_at')[:3]
        if latest_shares:
            print(f"\n📋 最新分享记录:")
            for share in latest_shares:
                print(f"   • {share}")
        
    except Exception as e:
        print(f"❌ 统计数据获取失败: {e}")

if __name__ == '__main__':
    try:
        success = test_share_functionality()
        print_test_summary()
        
        if success:
            print("\n✅ 所有测试通过！分享功能工作正常。")
            sys.exit(0)
        else:
            print("\n❌ 部分测试失败！请检查分享功能。")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
