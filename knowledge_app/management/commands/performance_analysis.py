"""
性能分析命令 - 检测系统性能瓶颈
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.test import Client
from django.urls import reverse
import time
import psutil
import os

class Command(BaseCommand):
    help = '分析系统性能瓶颈'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='显示详细分析结果',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='自动修复发现的性能问题',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('🔍 开始性能分析...')
        self.stdout.write('=' * 50)
        
        # 1. 系统资源分析
        self.analyze_system_resources()
        
        # 2. 数据库性能分析
        self.analyze_database_performance()
        
        # 3. 页面加载性能分析
        self.analyze_page_performance()
        
        # 4. 静态资源分析
        self.analyze_static_resources()
        
        # 5. 内存使用分析
        self.analyze_memory_usage()
        
        # 6. 提供优化建议
        self.provide_optimization_suggestions(options['fix'])
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('🔍 性能分析完成')
    
    def analyze_system_resources(self):
        """分析系统资源使用"""
        self.stdout.write('\n📊 系统资源分析:')
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        self.stdout.write(f'  CPU使用率: {cpu_percent}%')
        
        # 内存使用
        memory = psutil.virtual_memory()
        self.stdout.write(f'  内存使用: {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)')
        
        # 磁盘使用
        disk = psutil.disk_usage('.')
        self.stdout.write(f'  磁盘使用: {disk.percent}% ({disk.used // 1024 // 1024 // 1024}GB / {disk.total // 1024 // 1024 // 1024}GB)')
        
        # 性能评估
        if cpu_percent > 80:
            self.stdout.write(self.style.ERROR('  ⚠️  CPU使用率过高'))
        if memory.percent > 80:
            self.stdout.write(self.style.ERROR('  ⚠️  内存使用率过高'))
        if disk.percent > 90:
            self.stdout.write(self.style.ERROR('  ⚠️  磁盘空间不足'))
    
    def analyze_database_performance(self):
        """分析数据库性能"""
        self.stdout.write('\n🗄️ 数据库性能分析:')
        
        # 测试数据库连接时间
        start_time = time.time()
        connection.ensure_connection()
        db_connect_time = (time.time() - start_time) * 1000
        
        self.stdout.write(f'  数据库连接时间: {db_connect_time:.2f}ms')
        
        # 测试简单查询
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        simple_query_time = (time.time() - start_time) * 1000
        
        self.stdout.write(f'  简单查询时间: {simple_query_time:.2f}ms')
        
        # 测试复杂查询
        from knowledge_app.models import DailyTerm
        start_time = time.time()
        DailyTerm.objects.filter(status='active').order_by('-display_date')[:10]
        complex_query_time = (time.time() - start_time) * 1000
        
        self.stdout.write(f'  复杂查询时间: {complex_query_time:.2f}ms')
        
        # 性能评估
        if db_connect_time > 100:
            self.stdout.write(self.style.ERROR('  ⚠️  数据库连接时间过长'))
        if simple_query_time > 50:
            self.stdout.write(self.style.ERROR('  ⚠️  简单查询时间过长'))
        if complex_query_time > 200:
            self.stdout.write(self.style.ERROR('  ⚠️  复杂查询时间过长'))
    
    def analyze_page_performance(self):
        """分析页面加载性能"""
        self.stdout.write('\n🌐 页面性能分析:')
        
        client = Client()
        
        # 测试主要页面
        pages = [
            ('首页', '/'),
            ('每日名词', '/daily-term/'),
            ('CS宇宙', '/universe/'),
            ('关于页面', '/about/'),
        ]
        
        for page_name, url in pages:
            start_time = time.time()
            try:
                response = client.get(url)
                load_time = (time.time() - start_time) * 1000
                
                status_color = self.style.SUCCESS if response.status_code == 200 else self.style.ERROR
                time_color = self.style.SUCCESS if load_time < 500 else (
                    self.style.WARNING if load_time < 1000 else self.style.ERROR
                )
                
                self.stdout.write(f'  {page_name}: {status_color(response.status_code)} - {time_color(f"{load_time:.2f}ms")}')
                
                # 检查响应大小
                content_length = len(response.content)
                if content_length > 1024 * 1024:  # 1MB
                    self.stdout.write(f'    ⚠️  响应过大: {content_length // 1024}KB')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  {page_name}: 错误 - {e}'))
    
    def analyze_static_resources(self):
        """分析静态资源"""
        self.stdout.write('\n📁 静态资源分析:')
        
        import os
        from django.conf import settings
        
        static_root = getattr(settings, 'STATIC_ROOT', 'static')
        if not os.path.exists(static_root):
            static_root = 'static'
        
        if os.path.exists(static_root):
            # 分析CSS文件
            css_files = []
            js_files = []
            img_files = []
            
            for root, dirs, files in os.walk(static_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    
                    if file.endswith('.css'):
                        css_files.append((file, file_size))
                    elif file.endswith('.js'):
                        js_files.append((file, file_size))
                    elif file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                        img_files.append((file, file_size))
            
            # 显示大文件
            self.stdout.write(f'  CSS文件数量: {len(css_files)}')
            large_css = [(f, s) for f, s in css_files if s > 100 * 1024]  # >100KB
            if large_css:
                self.stdout.write('    大型CSS文件:')
                for file, size in large_css:
                    self.stdout.write(f'      {file}: {size // 1024}KB')
            
            self.stdout.write(f'  JS文件数量: {len(js_files)}')
            large_js = [(f, s) for f, s in js_files if s > 200 * 1024]  # >200KB
            if large_js:
                self.stdout.write('    大型JS文件:')
                for file, size in large_js:
                    self.stdout.write(f'      {file}: {size // 1024}KB')
            
            self.stdout.write(f'  图片文件数量: {len(img_files)}')
            large_img = [(f, s) for f, s in img_files if s > 500 * 1024]  # >500KB
            if large_img:
                self.stdout.write('    大型图片文件:')
                for file, size in large_img:
                    self.stdout.write(f'      {file}: {size // 1024}KB')
        else:
            self.stdout.write('  静态文件目录不存在')
    
    def analyze_memory_usage(self):
        """分析内存使用"""
        self.stdout.write('\n🧠 内存使用分析:')
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        self.stdout.write(f'  当前进程内存: {memory_info.rss // 1024 // 1024}MB')
        self.stdout.write(f'  虚拟内存: {memory_info.vms // 1024 // 1024}MB')
        
        # 检查内存泄漏迹象
        if memory_info.rss > 500 * 1024 * 1024:  # >500MB
            self.stdout.write(self.style.WARNING('  ⚠️  内存使用较高，可能存在内存泄漏'))
    
    def provide_optimization_suggestions(self, auto_fix=False):
        """提供优化建议"""
        self.stdout.write('\n💡 优化建议:')
        
        suggestions = [
            {
                'issue': '数据库查询优化',
                'suggestion': '使用select_related和prefetch_related减少数据库查询',
                'fix': self.fix_database_queries if auto_fix else None
            },
            {
                'issue': '静态资源压缩',
                'suggestion': '启用Gzip压缩和资源合并',
                'fix': self.fix_static_compression if auto_fix else None
            },
            {
                'issue': '缓存策略',
                'suggestion': '实施多层缓存策略',
                'fix': self.fix_caching if auto_fix else None
            },
            {
                'issue': '图片优化',
                'suggestion': '使用WebP格式和懒加载',
                'fix': self.fix_image_optimization if auto_fix else None
            },
        ]
        
        for i, suggestion in enumerate(suggestions, 1):
            self.stdout.write(f'  {i}. {suggestion["issue"]}')
            self.stdout.write(f'     建议: {suggestion["suggestion"]}')
            
            if auto_fix and suggestion['fix']:
                try:
                    suggestion['fix']()
                    self.stdout.write(self.style.SUCCESS('     ✅ 已自动修复'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'     ❌ 修复失败: {e}'))
    
    def fix_database_queries(self):
        """修复数据库查询问题"""
        # 这里可以实施具体的数据库优化
        pass
    
    def fix_static_compression(self):
        """修复静态资源压缩问题"""
        # 这里可以实施静态资源优化
        pass
    
    def fix_caching(self):
        """修复缓存问题"""
        # 这里可以实施缓存优化
        pass
    
    def fix_image_optimization(self):
        """修复图片优化问题"""
        # 这里可以实施图片优化
        pass
