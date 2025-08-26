#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cs_learning_platform.settings')
django.setup()

from knowledge_app.models import DailyTerm

def check_explanation():
    print("=== 检查今日名词explanation内容 ===")
    
    term = DailyTerm.get_today_term()
    if not term:
        print("没有找到今日名词")
        return
    
    print(f"名词: {term.term}")
    print(f"分类: {term.category}")
    print(f"难度: {term.difficulty_level}")
    
    explanation = term.explanation
    print(f"\nExplanation长度: {len(explanation)}")
    
    # 检查特殊字符
    special_chars = ["'", '"', '`', '\n', '\r', '\t']
    print("\n特殊字符统计:")
    for char in special_chars:
        count = explanation.count(char)
        if count > 0:
            print(f"  {repr(char)}: {count}个")
    
    # 显示前200个字符
    print(f"\n前200个字符:")
    print(repr(explanation[:200]))
    
    # 检查是否有可能导致JavaScript错误的内容
    problematic_patterns = [
        "\\n",  # 换行符
        "\\'",  # 转义单引号
        '\\"',  # 转义双引号
        "\\`",  # 转义反引号
    ]
    
    print("\n可能有问题的模式:")
    for pattern in problematic_patterns:
        if pattern in explanation:
            print(f"  发现: {repr(pattern)}")
    
    # 模拟JavaScript字符串
    print("\n模拟JavaScript调用:")
    try:
        # 使用Django的escapejs过滤器
        from django.utils.html import escapejs
        escaped = escapejs(explanation)
        print(f"escapejs后的长度: {len(escaped)}")
        print(f"escapejs后的前100个字符: {repr(escaped[:100])}")
        
        # 检查是否还有问题
        if "'" in escaped:
            print("⚠️  警告: escapejs后仍包含单引号")
        if '"' in escaped:
            print("⚠️  警告: escapejs后仍包含双引号")
        if '`' in escaped:
            print("⚠️  警告: escapejs后仍包含反引号")
            
    except Exception as e:
        print(f"escapejs处理失败: {e}")

if __name__ == "__main__":
    check_explanation()
