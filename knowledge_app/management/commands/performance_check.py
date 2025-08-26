"""
性能检查管理命令
分析系统性能并提供优化建议
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import connection
from django.conf import settings
import os
import time
import psutil
import requests
from pathlib import Path


class Command(BaseCommand):
    help = '检查系统性能并提供优化建议'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='显示详细的性能分析报告'
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='自动修复发现的性能问题'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 开始性能检查...\n')
        )
        
        # 执行各项检查
        results = {
            'database': self.check_database_performance(),
            'cache': self.check_cache_performance(),
            'static_files': self.check_static_files(),
            'memory': self.check_memory_usage(),
            'disk': self.check_disk_usage(),
            'network': self.check_network_performance(),
            'templates': self.check_template_performance(),
        }
        
        # 显示结果
        self.display_results(results, options['detailed'])
        
        # 自动修复（如果启用）
        if options['fix']:
            self.auto_fix_issues(results)
        
        # 生成优化建议
        self.generate_recommendations(results)
    
    def check_database_performance(self):
        """检查数据库性能"""
        self.stdout.write('📊 检查数据库性能...')
        
        results = {
            'status': 'good',
            'issues': [],
            'metrics': {}
        }
        
        try:
            # 测试数据库连接时间
            start_time = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            connection_time = time.time() - start_time
            
            results['metrics']['connection_time'] = connection_time
            
            if connection_time > 0.1:
                results['status'] = 'warning'
                results['issues'].append(f'数据库连接时间过长: {connection_time:.3f}s')
            
            # 检查数据库查询
            if settings.DEBUG:
                # 执行一个测试查询来检查性能
                start_time = time.time()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM django_session")
                    cursor.fetchone()
                query_time = time.time() - start_time
                
                results['metrics']['query_time'] = query_time
                
                if query_time > 0.05:
                    results['status'] = 'warning'
                    results['issues'].append(f'查询执行时间过长: {query_time:.3f}s')
            
            # 检查数据库索引（简化版）
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.statistics 
                    WHERE table_schema = DATABASE()
                """)
                index_count = cursor.fetchone()[0] if cursor.rowcount > 0 else 0
                results['metrics']['index_count'] = index_count
                
                if index_count < 5:
                    results['status'] = 'warning'
                    results['issues'].append('数据库索引数量较少，可能影响查询性能')
        
        except Exception as e:
            results['status'] = 'error'
            results['issues'].append(f'数据库检查失败: {str(e)}')
        
        return results
    
    def check_cache_performance(self):
        """检查缓存性能"""
        self.stdout.write('💾 检查缓存性能...')
        
        results = {
            'status': 'good',
            'issues': [],
            'metrics': {}
        }
        
        try:
            # 测试缓存写入性能
            test_key = 'performance_test_key'
            test_data = 'x' * 1024  # 1KB数据
            
            start_time = time.time()
            cache.set(test_key, test_data, 60)
            write_time = time.time() - start_time
            
            # 测试缓存读取性能
            start_time = time.time()
            cached_data = cache.get(test_key)
            read_time = time.time() - start_time
            
            # 清理测试数据
            cache.delete(test_key)
            
            results['metrics']['write_time'] = write_time
            results['metrics']['read_time'] = read_time
            
            if write_time > 0.01:
                results['status'] = 'warning'
                results['issues'].append(f'缓存写入时间过长: {write_time:.3f}s')
            
            if read_time > 0.005:
                results['status'] = 'warning'
                results['issues'].append(f'缓存读取时间过长: {read_time:.3f}s')
            
            if cached_data != test_data:
                results['status'] = 'error'
                results['issues'].append('缓存数据完整性检查失败')
        
        except Exception as e:
            results['status'] = 'error'
            results['issues'].append(f'缓存检查失败: {str(e)}')
        
        return results
    
    def check_static_files(self):
        """检查静态文件性能"""
        self.stdout.write('📁 检查静态文件...')
        
        results = {
            'status': 'good',
            'issues': [],
            'metrics': {}
        }
        
        try:
            static_root = Path(settings.STATIC_ROOT) if hasattr(settings, 'STATIC_ROOT') else Path('static')
            
            if static_root.exists():
                # 统计文件大小
                total_size = 0
                file_count = 0
                large_files = []
                
                for file_path in static_root.rglob('*'):
                    if file_path.is_file():
                        file_size = file_path.stat().st_size
                        total_size += file_size
                        file_count += 1
                        
                        # 检查大文件
                        if file_size > 1024 * 1024:  # 1MB
                            large_files.append((str(file_path), file_size))
                
                results['metrics']['total_size'] = total_size
                results['metrics']['file_count'] = file_count
                results['metrics']['large_files'] = len(large_files)
                
                # 检查是否有过大的文件
                if large_files:
                    results['status'] = 'warning'
                    results['issues'].append(f'发现 {len(large_files)} 个大文件 (>1MB)')
                
                # 检查总大小
                if total_size > 50 * 1024 * 1024:  # 50MB
                    results['status'] = 'warning'
                    results['issues'].append(f'静态文件总大小过大: {total_size / 1024 / 1024:.1f}MB')
            
            else:
                results['status'] = 'warning'
                results['issues'].append('静态文件目录不存在')
        
        except Exception as e:
            results['status'] = 'error'
            results['issues'].append(f'静态文件检查失败: {str(e)}')
        
        return results
    
    def check_memory_usage(self):
        """检查内存使用情况"""
        self.stdout.write('🧠 检查内存使用...')
        
        results = {
            'status': 'good',
            'issues': [],
            'metrics': {}
        }
        
        try:
            # 系统内存
            memory = psutil.virtual_memory()
            results['metrics']['total_memory'] = memory.total
            results['metrics']['available_memory'] = memory.available
            results['metrics']['memory_percent'] = memory.percent
            
            if memory.percent > 80:
                results['status'] = 'warning'
                results['issues'].append(f'系统内存使用率过高: {memory.percent:.1f}%')
            
            # 当前进程内存
            process = psutil.Process()
            process_memory = process.memory_info()
            results['metrics']['process_memory'] = process_memory.rss
            
            # 检查内存泄漏迹象
            if process_memory.rss > 500 * 1024 * 1024:  # 500MB
                results['status'] = 'warning'
                results['issues'].append(f'进程内存使用过高: {process_memory.rss / 1024 / 1024:.1f}MB')
        
        except Exception as e:
            results['status'] = 'error'
            results['issues'].append(f'内存检查失败: {str(e)}')
        
        return results
    
    def check_disk_usage(self):
        """检查磁盘使用情况"""
        self.stdout.write('💿 检查磁盘使用...')
        
        results = {
            'status': 'good',
            'issues': [],
            'metrics': {}
        }
        
        try:
            disk_usage = psutil.disk_usage('/')
            results['metrics']['total_disk'] = disk_usage.total
            results['metrics']['free_disk'] = disk_usage.free
            results['metrics']['disk_percent'] = (disk_usage.used / disk_usage.total) * 100
            
            if results['metrics']['disk_percent'] > 90:
                results['status'] = 'error'
                results['issues'].append(f'磁盘空间不足: {results["metrics"]["disk_percent"]:.1f}%')
            elif results['metrics']['disk_percent'] > 80:
                results['status'] = 'warning'
                results['issues'].append(f'磁盘空间紧张: {results["metrics"]["disk_percent"]:.1f}%')
        
        except Exception as e:
            results['status'] = 'error'
            results['issues'].append(f'磁盘检查失败: {str(e)}')
        
        return results
    
    def check_network_performance(self):
        """检查网络性能"""
        self.stdout.write('🌐 检查网络性能...')
        
        results = {
            'status': 'good',
            'issues': [],
            'metrics': {}
        }
        
        try:
            # 测试本地连接
            start_time = time.time()
            response = requests.get('http://127.0.0.1:8000/', timeout=5)
            response_time = time.time() - start_time
            
            results['metrics']['local_response_time'] = response_time
            results['metrics']['status_code'] = response.status_code
            
            if response_time > 2.0:
                results['status'] = 'warning'
                results['issues'].append(f'本地响应时间过长: {response_time:.3f}s')
            
            if response.status_code != 200:
                results['status'] = 'error'
                results['issues'].append(f'服务器响应异常: {response.status_code}')
        
        except requests.exceptions.RequestException as e:
            results['status'] = 'error'
            results['issues'].append(f'网络连接失败: {str(e)}')
        except Exception as e:
            results['status'] = 'warning'
            results['issues'].append(f'网络检查失败: {str(e)}')
        
        return results
    
    def check_template_performance(self):
        """检查模板性能"""
        self.stdout.write('📄 检查模板性能...')
        
        results = {
            'status': 'good',
            'issues': [],
            'metrics': {}
        }
        
        try:
            template_dirs = settings.TEMPLATES[0]['DIRS'] if settings.TEMPLATES else []
            template_count = 0
            large_templates = []
            
            for template_dir in template_dirs:
                template_path = Path(template_dir)
                if template_path.exists():
                    for template_file in template_path.rglob('*.html'):
                        template_count += 1
                        file_size = template_file.stat().st_size
                        
                        if file_size > 50 * 1024:  # 50KB
                            large_templates.append((str(template_file), file_size))
            
            results['metrics']['template_count'] = template_count
            results['metrics']['large_templates'] = len(large_templates)
            
            if large_templates:
                results['status'] = 'warning'
                results['issues'].append(f'发现 {len(large_templates)} 个大模板文件 (>50KB)')
        
        except Exception as e:
            results['status'] = 'error'
            results['issues'].append(f'模板检查失败: {str(e)}')
        
        return results
    
    def display_results(self, results, detailed=False):
        """显示检查结果"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 性能检查报告'))
        self.stdout.write('='*60 + '\n')
        
        for category, result in results.items():
            status_icon = {
                'good': '✅',
                'warning': '⚠️',
                'error': '❌'
            }.get(result['status'], '❓')
            
            self.stdout.write(f"{status_icon} {category.upper()}: {result['status'].upper()}")
            
            if result['issues']:
                for issue in result['issues']:
                    self.stdout.write(f"   • {issue}")
            
            if detailed and result['metrics']:
                self.stdout.write("   指标:")
                for metric, value in result['metrics'].items():
                    if isinstance(value, float):
                        self.stdout.write(f"     - {metric}: {value:.3f}")
                    else:
                        self.stdout.write(f"     - {metric}: {value}")
            
            self.stdout.write('')
    
    def auto_fix_issues(self, results):
        """自动修复问题"""
        self.stdout.write(self.style.WARNING('🔧 开始自动修复...\n'))
        
        fixed_count = 0
        
        # 清理缓存
        if results['cache']['status'] != 'good':
            try:
                cache.clear()
                self.stdout.write('✅ 已清理缓存')
                fixed_count += 1
            except Exception as e:
                self.stdout.write(f'❌ 缓存清理失败: {e}')
        
        # 清理临时文件
        try:
            import tempfile
            import shutil
            temp_dir = Path(tempfile.gettempdir())
            for temp_file in temp_dir.glob('django_*'):
                if temp_file.is_file():
                    temp_file.unlink()
            self.stdout.write('✅ 已清理临时文件')
            fixed_count += 1
        except Exception as e:
            self.stdout.write(f'❌ 临时文件清理失败: {e}')
        
        self.stdout.write(f'\n🎉 自动修复完成，共修复 {fixed_count} 个问题')
    
    def generate_recommendations(self, results):
        """生成优化建议"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('💡 优化建议'))
        self.stdout.write('='*60 + '\n')
        
        recommendations = []
        
        # 数据库优化建议
        if results['database']['status'] != 'good':
            recommendations.extend([
                "考虑添加数据库索引以提升查询性能",
                "使用select_related()和prefetch_related()优化ORM查询",
                "考虑使用数据库连接池",
            ])
        
        # 缓存优化建议
        if results['cache']['status'] != 'good':
            recommendations.extend([
                "考虑使用Redis作为缓存后端",
                "增加页面级缓存",
                "使用模板片段缓存",
            ])
        
        # 静态文件优化建议
        if results['static_files']['status'] != 'good':
            recommendations.extend([
                "压缩CSS和JavaScript文件",
                "优化图片大小和格式",
                "使用CDN加速静态资源",
                "启用Gzip压缩",
            ])
        
        # 内存优化建议
        if results['memory']['status'] != 'good':
            recommendations.extend([
                "检查是否存在内存泄漏",
                "优化数据库查询以减少内存使用",
                "考虑增加服务器内存",
            ])
        
        # 通用优化建议
        recommendations.extend([
            "启用Django的缓存中间件",
            "使用异步视图处理耗时操作",
            "实施数据库查询优化",
            "考虑使用负载均衡",
        ])
        
        for i, recommendation in enumerate(recommendations, 1):
            self.stdout.write(f"{i}. {recommendation}")
        
        self.stdout.write(f'\n📈 总共 {len(recommendations)} 条优化建议')
