#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cs_learning_platform.settings')
django.setup()

from knowledge_app.models import DailyTerm

def check_daily_term():
    print("=== 检查每日名词数据 ===")
    
    # 获取今日名词
    today_term = DailyTerm.get_today_term()
    print(f"Today term: {today_term}")
    
    if today_term:
        print(f"ID: {today_term.id}")
        print(f"Term: {today_term.term}")
        print(f"Category: {today_term.category}")
        print(f"Difficulty: {today_term.difficulty_level}")
        print(f"Explanation: {today_term.explanation[:100]}...")
    else:
        print("没有找到今日名词")
        
        # 检查是否有任何活跃的名词
        active_terms = DailyTerm.objects.filter(status='active')
        print(f"活跃名词总数: {active_terms.count()}")
        
        if active_terms.exists():
            latest = active_terms.order_by('-display_date').first()
            print(f"最新名词: {latest.term} ({latest.display_date})")

if __name__ == "__main__":
    check_daily_term()
