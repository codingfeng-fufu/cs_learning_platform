#!/usr/bin/env python
"""
每日名词系统修复脚本
解决自动生成名词的问题
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
import pytz

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CS_Learning_Platform.settings')
django.setup()

from knowledge_app.models import DailyTerm
from knowledge_app.services.daily_term_service import DailyTermService
from django.utils import timezone

def check_current_status():
    """检查当前每日名词状态"""
    print("🔍 检查每日名词系统状态...")
    
    # 获取北京时间
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_now = timezone.now().astimezone(beijing_tz)
    today = beijing_now.date()
    
    print(f"📅 当前北京时间: {beijing_now}")
    print(f"📅 今天日期: {today}")
    
    # 检查今日名词
    today_term = DailyTerm.objects.filter(display_date=today, status='active').first()
    if today_term:
        print(f"✅ 今日名词已存在: {today_term.term}")
        print(f"   创建时间: {today_term.created_at}")
        print(f"   API请求时间: {today_term.api_request_time}")
        return True
    else:
        print("❌ 今日名词不存在")
        return False
    
def check_recent_terms():
    """检查最近的名词"""
    print("\n📋 最近的名词记录:")
    recent_terms = DailyTerm.objects.filter(status='active').order_by('-display_date')[:7]
    
    if not recent_terms:
        print("❌ 没有找到任何名词记录")
        return
    
    for term in recent_terms:
        print(f"  {term.display_date}: {term.term} (创建: {term.created_at.strftime('%m-%d %H:%M')})")

def generate_today_term():
    """生成今日名词"""
    print("\n🚀 开始生成今日名词...")
    
    service = DailyTermService()
    beijing_tz = pytz.timezone('Asia/Shanghai')
    today = timezone.now().astimezone(beijing_tz).date()
    
    try:
        daily_term = service.generate_daily_term(today)
        
        if daily_term:
            print(f"✅ 成功生成今日名词: {daily_term.term}")
            print(f"   分类: {daily_term.category}")
            print(f"   难度: {daily_term.get_difficulty_level_display()}")
            print(f"   创建时间: {daily_term.created_at}")
            return True
        else:
            print("❌ 生成今日名词失败")
            return False
            
    except Exception as e:
        print(f"❌ 生成今日名词时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scheduler_logic():
    """测试调度器逻辑"""
    print("\n🧪 测试调度器逻辑...")
    
    try:
        from knowledge_app.management.commands.start_daily_term_scheduler import DailyTermScheduler
        
        scheduler = DailyTermScheduler()
        beijing_tz = pytz.timezone('Asia/Shanghai')
        today = timezone.now().astimezone(beijing_tz).date()
        
        should_generate = scheduler._should_generate_term(today)
        print(f"📊 调度器判断今日是否需要生成名词: {should_generate}")
        
        if should_generate:
            print("✅ 调度器逻辑正常，应该生成今日名词")
        else:
            print("⚠️  调度器认为不需要生成名词")
            
        return should_generate
        
    except Exception as e:
        print(f"❌ 测试调度器逻辑时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_get_today_term_method():
    """修复get_today_term方法"""
    print("\n🔧 检查get_today_term方法...")
    
    # 检查当前的get_today_term方法是否有临时修改
    beijing_tz = pytz.timezone('Asia/Shanghai')
    today = timezone.now().astimezone(beijing_tz).date()
    
    # 使用原始逻辑获取今日名词
    try:
        today_term_original = DailyTerm.objects.get(display_date=today, status='active')
        print(f"✅ 原始逻辑找到今日名词: {today_term_original.term}")
    except DailyTerm.DoesNotExist:
        print("❌ 原始逻辑没有找到今日名词")
    
    # 使用当前的get_today_term方法
    current_term = DailyTerm.get_today_term()
    if current_term:
        print(f"📋 当前get_today_term返回: {current_term.term} (日期: {current_term.display_date})")
        if current_term.display_date != today:
            print("⚠️  警告: get_today_term返回的不是今日名词！")
    else:
        print("❌ get_today_term返回None")

def check_environment():
    """检查环境变量"""
    print("\n🌍 检查环境变量...")
    
    run_main = os.environ.get('RUN_MAIN')
    print(f"RUN_MAIN环境变量: {run_main}")
    
    if run_main == 'true':
        print("✅ 环境变量正确，调度器应该启动")
    else:
        print("⚠️  环境变量不正确，调度器可能不会启动")
        print("💡 建议: 在开发服务器启动时设置 RUN_MAIN=true")

def main():
    """主函数"""
    print("🚀 每日名词系统诊断和修复工具")
    print("=" * 50)
    
    # 1. 检查当前状态
    has_today_term = check_current_status()
    
    # 2. 检查最近的名词
    check_recent_terms()
    
    # 3. 检查环境变量
    check_environment()
    
    # 4. 测试调度器逻辑
    should_generate = test_scheduler_logic()
    
    # 5. 检查get_today_term方法
    fix_get_today_term_method()
    
    # 6. 如果没有今日名词且应该生成，则生成
    if not has_today_term and should_generate:
        print("\n" + "=" * 50)
        print("🔧 开始修复...")
        success = generate_today_term()
        
        if success:
            print("\n✅ 修复完成！今日名词已生成")
        else:
            print("\n❌ 修复失败，请检查API配置和网络连接")
    elif has_today_term:
        print("\n✅ 系统正常，今日名词已存在")
    else:
        print("\n⚠️  调度器认为不需要生成名词，可能存在逻辑问题")
    
    print("\n" + "=" * 50)
    print("🔍 诊断建议:")
    print("1. 确保开发服务器启动时设置了 RUN_MAIN=true 环境变量")
    print("2. 检查调度器是否正常启动（查看控制台输出）")
    print("3. 确认API密钥配置正确")
    print("4. 检查网络连接是否正常")
    print("5. 考虑使用cron任务作为备用方案")

if __name__ == "__main__":
    main()
