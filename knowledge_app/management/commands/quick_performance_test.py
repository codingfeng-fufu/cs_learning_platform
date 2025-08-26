"""
快速性能测试命令
"""

from django.core.management.base import BaseCommand
from django.test import Client
from django.core.cache import cache
import time

class Command(BaseCommand):
    help = '快速性能测试'
    
    def handle(self, *args, **options):
        self.stdout.write('🚀 快速性能测试开始...')
        self.stdout.write('=' * 50)
        
        # 清理缓存以获得真实的性能数据
        cache.clear()
        self.stdout.write('🧹 已清理缓存')
        
        client = Client()
        
        # 测试页面
        test_pages = [
            ('首页', '/'),
            ('每日名词', '/daily-term/'),
            ('CS宇宙', '/universe/'),
            ('关于页面', '/about/'),
        ]
        
        results = []
        
        self.stdout.write('\n📊 页面加载性能测试:')
        self.stdout.write('-' * 30)
        
        for page_name, url in test_pages:
            # 第一次请求（无缓存）
            start_time = time.time()
            response1 = client.get(url)
            first_load_time = (time.time() - start_time) * 1000
            
            # 第二次请求（有缓存）
            start_time = time.time()
            response2 = client.get(url)
            cached_load_time = (time.time() - start_time) * 1000
            
            # 计算缓存效果
            cache_improvement = ((first_load_time - cached_load_time) / first_load_time) * 100
            
            results.append({
                'name': page_name,
                'first_load': first_load_time,
                'cached_load': cached_load_time,
                'improvement': cache_improvement,
                'status': response1.status_code
            })
            
            # 显示结果
            status_color = self.style.SUCCESS if response1.status_code == 200 else self.style.ERROR
            first_color = self.style.SUCCESS if first_load_time < 500 else (
                self.style.WARNING if first_load_time < 1000 else self.style.ERROR
            )
            cached_color = self.style.SUCCESS if cached_load_time < 200 else self.style.WARNING
            
            self.stdout.write(f'{page_name}:')
            self.stdout.write(f'  状态: {status_color(response1.status_code)}')
            self.stdout.write(f'  首次加载: {first_color(f"{first_load_time:.2f}ms")}')
            self.stdout.write(f'  缓存加载: {cached_color(f"{cached_load_time:.2f}ms")}')
            if cache_improvement > 0:
                self.stdout.write(f'  缓存提升: {self.style.SUCCESS(f"{cache_improvement:.1f}%")}')
            self.stdout.write('')
        
        # 性能总结
        self.stdout.write('📋 性能总结:')
        self.stdout.write('-' * 30)
        
        avg_first_load = sum(r['first_load'] for r in results) / len(results)
        avg_cached_load = sum(r['cached_load'] for r in results) / len(results)
        overall_improvement = ((avg_first_load - avg_cached_load) / avg_first_load) * 100
        
        self.stdout.write(f'平均首次加载时间: {avg_first_load:.2f}ms')
        self.stdout.write(f'平均缓存加载时间: {avg_cached_load:.2f}ms')
        self.stdout.write(f'整体缓存提升: {overall_improvement:.1f}%')
        
        # 性能等级
        if avg_first_load < 300:
            grade = "优秀 🌟"
        elif avg_first_load < 600:
            grade = "良好 👍"
        elif avg_first_load < 1000:
            grade = "一般 😐"
        else:
            grade = "需要优化 ⚠️"
        
        self.stdout.write(f'性能等级: {grade}')
        
        # 测试数据库性能
        self.stdout.write('\n🗄️ 数据库性能测试:')
        self.stdout.write('-' * 30)
        
        from knowledge_app.models import DailyTerm
        
        # 测试简单查询
        start_time = time.time()
        DailyTerm.objects.filter(status='active').count()
        simple_query_time = (time.time() - start_time) * 1000
        
        # 测试复杂查询
        start_time = time.time()
        list(DailyTerm.objects.filter(status='active').order_by('-display_date')[:5])
        complex_query_time = (time.time() - start_time) * 1000
        
        # 测试缓存查询
        start_time = time.time()
        DailyTerm.get_today_term()
        cached_query_time = (time.time() - start_time) * 1000
        
        self.stdout.write(f'简单查询: {simple_query_time:.2f}ms')
        self.stdout.write(f'复杂查询: {complex_query_time:.2f}ms')
        self.stdout.write(f'缓存查询: {cached_query_time:.2f}ms')
        
        # 优化建议
        self.stdout.write('\n💡 优化建议:')
        self.stdout.write('-' * 30)
        
        suggestions = []
        
        if avg_first_load > 1000:
            suggestions.append("页面加载时间过长，建议检查数据库查询和模板复杂度")
        
        if overall_improvement < 20:
            suggestions.append("缓存效果不明显，建议增加更多缓存策略")
        
        if complex_query_time > 100:
            suggestions.append("数据库查询较慢，建议添加索引或优化查询")
        
        slow_pages = [r for r in results if r['first_load'] > 800]
        if slow_pages:
            page_names = [r['name'] for r in slow_pages]
            suggestions.append(f"以下页面较慢需要优化: {', '.join(page_names)}")
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                self.stdout.write(f'{i}. {suggestion}')
        else:
            self.stdout.write('✅ 性能表现良好，无需特别优化')
        
        # 已应用的优化
        self.stdout.write('\n🔧 已应用的优化:')
        self.stdout.write('-' * 30)
        self.stdout.write('✅ 数据库查询缓存')
        self.stdout.write('✅ 今日名词缓存')
        self.stdout.write('✅ 知识点数据缓存')
        self.stdout.write('✅ 模板文件压缩')
        self.stdout.write('✅ 性能监控中间件')
        self.stdout.write('✅ 缓存控制头')
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('🔍 性能测试完成')
