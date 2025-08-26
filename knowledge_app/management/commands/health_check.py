"""
系统健康检查命令
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import time
import json
import os
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = '系统健康检查'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['text', 'json'],
            default='text',
            help='输出格式',
        )
        parser.add_argument(
            '--save-report',
            action='store_true',
            help='保存健康检查报告',
        )
    
    def handle(self, *args, **options):
        start_time = time.time()
        
        health_data = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'checks': {},
            'metrics': {},
            'warnings': [],
            'errors': []
        }
        
        # 执行各项检查
        self.check_database(health_data)
        self.check_cache(health_data)
        self.check_scheduler(health_data)
        self.check_disk_space(health_data)
        self.check_memory_usage(health_data)
        self.check_api_connectivity(health_data)
        self.check_daily_term_status(health_data)
        
        # 计算总体状态
        health_data['response_time'] = round((time.time() - start_time) * 1000, 2)
        
        if health_data['errors']:
            health_data['status'] = 'unhealthy'
        elif health_data['warnings']:
            health_data['status'] = 'warning'
        
        # 输出结果
        if options['format'] == 'json':
            self.stdout.write(json.dumps(health_data, indent=2))
        else:
            self.display_text_report(health_data)
        
        # 保存报告
        if options['save_report']:
            self.save_health_report(health_data)
        
        # 设置退出码
        if health_data['status'] == 'unhealthy':
            exit(1)
        elif health_data['status'] == 'warning':
            exit(2)
    
    def check_database(self, health_data):
        """检查数据库连接"""
        try:
            start_time = time.time()
            connection.ensure_connection()
            
            # 执行简单查询
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            response_time = (time.time() - start_time) * 1000
            
            health_data['checks']['database'] = {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'message': '数据库连接正常'
            }
            
            if response_time > 100:
                health_data['warnings'].append('数据库响应时间较慢')
                
        except Exception as e:
            health_data['checks']['database'] = {
                'status': 'unhealthy',
                'message': f'数据库连接失败: {str(e)}'
            }
            health_data['errors'].append(f'数据库错误: {str(e)}')
    
    def check_cache(self, health_data):
        """检查缓存系统"""
        try:
            start_time = time.time()
            test_key = 'health_check_test'
            test_value = 'test_value'
            
            # 测试缓存写入
            cache.set(test_key, test_value, 60)
            
            # 测试缓存读取
            cached_value = cache.get(test_key)
            
            # 清理测试数据
            cache.delete(test_key)
            
            response_time = (time.time() - start_time) * 1000
            
            if cached_value == test_value:
                health_data['checks']['cache'] = {
                    'status': 'healthy',
                    'response_time_ms': round(response_time, 2),
                    'message': '缓存系统正常'
                }
            else:
                health_data['checks']['cache'] = {
                    'status': 'unhealthy',
                    'message': '缓存读写测试失败'
                }
                health_data['errors'].append('缓存系统异常')
                
        except Exception as e:
            health_data['checks']['cache'] = {
                'status': 'unhealthy',
                'message': f'缓存系统错误: {str(e)}'
            }
            health_data['errors'].append(f'缓存错误: {str(e)}')
    
    def check_scheduler(self, health_data):
        """检查调度器状态"""
        try:
            from knowledge_app.services.advanced_scheduler import get_scheduler
            scheduler = get_scheduler()
            status = scheduler.get_status()
            
            if status['running']:
                health_data['checks']['scheduler'] = {
                    'status': 'healthy',
                    'message': '调度器运行正常',
                    'scheduler_type': status.get('scheduler_type', 'unknown'),
                    'today_term_exists': status.get('today_term_exists', False)
                }
                
                if not status.get('today_term_exists', False):
                    health_data['warnings'].append('今日名词不存在')
            else:
                health_data['checks']['scheduler'] = {
                    'status': 'unhealthy',
                    'message': '调度器未运行'
                }
                health_data['errors'].append('调度器未运行')
                
        except Exception as e:
            health_data['checks']['scheduler'] = {
                'status': 'unhealthy',
                'message': f'调度器检查失败: {str(e)}'
            }
            health_data['warnings'].append(f'调度器检查异常: {str(e)}')
    
    def check_disk_space(self, health_data):
        """检查磁盘空间"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('.')
            
            free_percent = (free / total) * 100
            used_percent = (used / total) * 100
            
            health_data['metrics']['disk_space'] = {
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'free_gb': round(free / (1024**3), 2),
                'used_percent': round(used_percent, 1),
                'free_percent': round(free_percent, 1)
            }
            
            if free_percent < 10:
                health_data['checks']['disk_space'] = {
                    'status': 'unhealthy',
                    'message': f'磁盘空间不足: {free_percent:.1f}% 剩余'
                }
                health_data['errors'].append('磁盘空间严重不足')
            elif free_percent < 20:
                health_data['checks']['disk_space'] = {
                    'status': 'warning',
                    'message': f'磁盘空间较少: {free_percent:.1f}% 剩余'
                }
                health_data['warnings'].append('磁盘空间不足')
            else:
                health_data['checks']['disk_space'] = {
                    'status': 'healthy',
                    'message': f'磁盘空间充足: {free_percent:.1f}% 剩余'
                }
                
        except Exception as e:
            health_data['checks']['disk_space'] = {
                'status': 'unknown',
                'message': f'磁盘空间检查失败: {str(e)}'
            }
    
    def check_memory_usage(self, health_data):
        """检查内存使用"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            health_data['metrics']['memory'] = {
                'total_mb': round(memory.total / (1024**2), 2),
                'used_mb': round(memory.used / (1024**2), 2),
                'free_mb': round(memory.available / (1024**2), 2),
                'used_percent': memory.percent
            }
            
            if memory.percent > 90:
                health_data['checks']['memory'] = {
                    'status': 'unhealthy',
                    'message': f'内存使用过高: {memory.percent}%'
                }
                health_data['errors'].append('内存使用率过高')
            elif memory.percent > 80:
                health_data['checks']['memory'] = {
                    'status': 'warning',
                    'message': f'内存使用较高: {memory.percent}%'
                }
                health_data['warnings'].append('内存使用率较高')
            else:
                health_data['checks']['memory'] = {
                    'status': 'healthy',
                    'message': f'内存使用正常: {memory.percent}%'
                }
                
        except ImportError:
            health_data['checks']['memory'] = {
                'status': 'unknown',
                'message': 'psutil未安装，无法检查内存'
            }
        except Exception as e:
            health_data['checks']['memory'] = {
                'status': 'unknown',
                'message': f'内存检查失败: {str(e)}'
            }
    
    def check_api_connectivity(self, health_data):
        """检查API连接"""
        try:
            api_key = getattr(settings, 'OPENAI_API_KEY', '')
            if api_key:
                health_data['checks']['api'] = {
                    'status': 'healthy',
                    'message': 'API密钥已配置'
                }
            else:
                health_data['checks']['api'] = {
                    'status': 'warning',
                    'message': 'API密钥未配置'
                }
                health_data['warnings'].append('API密钥未配置')
                
        except Exception as e:
            health_data['checks']['api'] = {
                'status': 'unknown',
                'message': f'API检查失败: {str(e)}'
            }
    
    def check_daily_term_status(self, health_data):
        """检查每日名词状态"""
        try:
            from knowledge_app.models import DailyTerm
            from django.utils import timezone
            import pytz
            
            beijing_tz = pytz.timezone('Asia/Shanghai')
            today = timezone.now().astimezone(beijing_tz).date()
            
            today_term = DailyTerm.objects.filter(
                display_date=today, 
                status='active'
            ).first()
            
            if today_term:
                health_data['checks']['daily_term'] = {
                    'status': 'healthy',
                    'message': f'今日名词存在: {today_term.term}',
                    'term': today_term.term,
                    'category': today_term.category
                }
            else:
                health_data['checks']['daily_term'] = {
                    'status': 'warning',
                    'message': '今日名词不存在'
                }
                health_data['warnings'].append('今日名词缺失')
                
        except Exception as e:
            health_data['checks']['daily_term'] = {
                'status': 'unknown',
                'message': f'每日名词检查失败: {str(e)}'
            }
    
    def display_text_report(self, health_data):
        """显示文本格式报告"""
        status_colors = {
            'healthy': self.style.SUCCESS,
            'warning': self.style.WARNING,
            'unhealthy': self.style.ERROR,
            'unknown': self.style.WARNING
        }
        
        overall_color = status_colors.get(health_data['status'], self.style.WARNING)
        
        self.stdout.write('🏥 系统健康检查报告')
        self.stdout.write('=' * 50)
        self.stdout.write(f'时间: {health_data["timestamp"]}')
        self.stdout.write(f'总体状态: {overall_color(health_data["status"].upper())}')
        self.stdout.write(f'响应时间: {health_data["response_time"]}ms')
        self.stdout.write('')
        
        # 显示检查结果
        self.stdout.write('📋 检查结果:')
        for check_name, check_data in health_data['checks'].items():
            status = check_data['status']
            message = check_data['message']
            color = status_colors.get(status, self.style.WARNING)
            
            self.stdout.write(f'  {check_name}: {color(status.upper())} - {message}')
            
            if 'response_time_ms' in check_data:
                self.stdout.write(f'    响应时间: {check_data["response_time_ms"]}ms')
        
        # 显示指标
        if health_data['metrics']:
            self.stdout.write('\n📊 系统指标:')
            for metric_name, metric_data in health_data['metrics'].items():
                self.stdout.write(f'  {metric_name}:')
                for key, value in metric_data.items():
                    self.stdout.write(f'    {key}: {value}')
        
        # 显示警告和错误
        if health_data['warnings']:
            self.stdout.write(f'\n⚠️  警告 ({len(health_data["warnings"])}):')
            for warning in health_data['warnings']:
                self.stdout.write(f'  - {warning}')
        
        if health_data['errors']:
            self.stdout.write(f'\n❌ 错误 ({len(health_data["errors"])}):')
            for error in health_data['errors']:
                self.stdout.write(f'  - {error}')
        
        if not health_data['warnings'] and not health_data['errors']:
            self.stdout.write(f'\n{self.style.SUCCESS("✅ 系统运行正常，所有检查通过！")}')
    
    def save_health_report(self, health_data):
        """保存健康检查报告"""
        reports_dir = 'health_reports'
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(reports_dir, f'health_report_{timestamp}.json')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(health_data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(f'\n📄 健康检查报告已保存: {report_file}')
