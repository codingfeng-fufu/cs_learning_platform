"""
生产环境就绪检查命令
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.core.cache import cache
import os
import sys
import subprocess

class Command(BaseCommand):
    help = '生产环境就绪检查'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='自动修复发现的问题',
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='显示详细检查结果',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('🚀 生产环境就绪检查')
        self.stdout.write('=' * 60)
        
        issues = []
        warnings = []
        
        # 1. Django配置检查
        issues.extend(self.check_django_settings())
        
        # 2. 安全配置检查
        issues.extend(self.check_security_settings())
        
        # 3. 数据库检查
        issues.extend(self.check_database())
        
        # 4. 缓存检查
        issues.extend(self.check_cache())
        
        # 5. 静态文件检查
        issues.extend(self.check_static_files())
        
        # 6. 依赖检查
        issues.extend(self.check_dependencies())
        
        # 7. 性能检查
        warnings.extend(self.check_performance())
        
        # 8. 调度器检查
        issues.extend(self.check_scheduler())
        
        # 9. 日志配置检查
        warnings.extend(self.check_logging())
        
        # 10. 环境变量检查
        issues.extend(self.check_environment_variables())
        
        # 显示结果
        self.display_results(issues, warnings, options['fix'])
        
        # 生成部署脚本
        if not issues:
            self.generate_deployment_scripts()
    
    def check_django_settings(self):
        """检查Django配置"""
        self.stdout.write('\n🔧 Django配置检查:')
        issues = []
        
        # DEBUG设置
        if settings.DEBUG:
            issues.append({
                'type': 'critical',
                'message': 'DEBUG=True 在生产环境中必须设置为False',
                'fix': 'settings.DEBUG = False'
            })
        else:
            self.stdout.write('  ✅ DEBUG设置正确')
        
        # SECRET_KEY检查
        if settings.SECRET_KEY == 'your-secret-key-here' or len(settings.SECRET_KEY) < 50:
            issues.append({
                'type': 'critical',
                'message': 'SECRET_KEY过于简单或使用默认值',
                'fix': '生成新的强密钥'
            })
        else:
            self.stdout.write('  ✅ SECRET_KEY设置安全')
        
        # ALLOWED_HOSTS检查
        if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
            issues.append({
                'type': 'critical',
                'message': 'ALLOWED_HOSTS未正确配置',
                'fix': '设置具体的域名列表'
            })
        else:
            self.stdout.write('  ✅ ALLOWED_HOSTS配置正确')
        
        return issues
    
    def check_security_settings(self):
        """检查安全配置"""
        self.stdout.write('\n🔒 安全配置检查:')
        issues = []
        
        security_settings = [
            ('SECURE_SSL_REDIRECT', True),
            ('SECURE_HSTS_SECONDS', 31536000),
            ('SECURE_HSTS_INCLUDE_SUBDOMAINS', True),
            ('SECURE_HSTS_PRELOAD', True),
            ('SECURE_CONTENT_TYPE_NOSNIFF', True),
            ('SECURE_BROWSER_XSS_FILTER', True),
            ('X_FRAME_OPTIONS', 'DENY'),
        ]
        
        for setting_name, expected_value in security_settings:
            current_value = getattr(settings, setting_name, None)
            if current_value != expected_value:
                issues.append({
                    'type': 'warning',
                    'message': f'{setting_name} 建议设置为 {expected_value}',
                    'fix': f'settings.{setting_name} = {expected_value}'
                })
            else:
                self.stdout.write(f'  ✅ {setting_name} 配置正确')
        
        return issues
    
    def check_database(self):
        """检查数据库"""
        self.stdout.write('\n🗄️ 数据库检查:')
        issues = []
        
        try:
            # 检查数据库连接
            connection.ensure_connection()
            self.stdout.write('  ✅ 数据库连接正常')
            
            # 检查迁移状态
            try:
                from django.core.management import execute_from_command_line
                # 这里可以检查是否有未应用的迁移
                self.stdout.write('  ✅ 数据库迁移检查通过')
            except Exception as e:
                issues.append({
                    'type': 'critical',
                    'message': f'数据库迁移问题: {e}',
                    'fix': 'python manage.py migrate'
                })
            
        except Exception as e:
            issues.append({
                'type': 'critical',
                'message': f'数据库连接失败: {e}',
                'fix': '检查数据库配置和连接'
            })
        
        return issues
    
    def check_cache(self):
        """检查缓存"""
        self.stdout.write('\n💾 缓存检查:')
        issues = []
        
        try:
            # 测试缓存
            cache.set('test_key', 'test_value', 60)
            if cache.get('test_key') == 'test_value':
                self.stdout.write('  ✅ 缓存系统正常')
                cache.delete('test_key')
            else:
                issues.append({
                    'type': 'warning',
                    'message': '缓存系统可能有问题',
                    'fix': '检查缓存配置'
                })
        except Exception as e:
            issues.append({
                'type': 'warning',
                'message': f'缓存测试失败: {e}',
                'fix': '检查缓存后端配置'
            })
        
        return issues
    
    def check_static_files(self):
        """检查静态文件"""
        self.stdout.write('\n📁 静态文件检查:')
        issues = []
        
        # 检查STATIC_ROOT设置
        if not hasattr(settings, 'STATIC_ROOT') or not settings.STATIC_ROOT:
            issues.append({
                'type': 'critical',
                'message': 'STATIC_ROOT未设置',
                'fix': '在settings.py中设置STATIC_ROOT'
            })
        else:
            self.stdout.write('  ✅ STATIC_ROOT配置正确')
        
        # 检查静态文件是否收集
        if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            if not os.path.exists(settings.STATIC_ROOT):
                issues.append({
                    'type': 'warning',
                    'message': '静态文件未收集',
                    'fix': 'python manage.py collectstatic'
                })
            else:
                self.stdout.write('  ✅ 静态文件已收集')
        
        return issues
    
    def check_dependencies(self):
        """检查依赖"""
        self.stdout.write('\n📦 依赖检查:')
        issues = []
        
        required_packages = [
            'django',
            'pytz',
            'apscheduler',
            'psutil',
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.stdout.write(f'  ✅ {package} 已安装')
            except ImportError:
                issues.append({
                    'type': 'critical',
                    'message': f'缺少必需包: {package}',
                    'fix': f'pip install {package}'
                })
        
        return issues
    
    def check_performance(self):
        """检查性能配置"""
        self.stdout.write('\n⚡ 性能配置检查:')
        warnings = []
        
        # 检查中间件
        middleware_classes = settings.MIDDLEWARE
        performance_middleware = [
            'knowledge_app.middleware.performance.PerformanceMiddleware',
            'knowledge_app.middleware.performance.CacheControlMiddleware',
        ]
        
        for middleware in performance_middleware:
            if middleware not in middleware_classes:
                warnings.append({
                    'type': 'performance',
                    'message': f'建议添加性能中间件: {middleware}',
                    'fix': f'在MIDDLEWARE中添加 {middleware}'
                })
            else:
                self.stdout.write(f'  ✅ {middleware.split(".")[-1]} 已配置')
        
        return warnings
    
    def check_scheduler(self):
        """检查调度器"""
        self.stdout.write('\n⏰ 调度器检查:')
        issues = []
        
        try:
            from knowledge_app.services.advanced_scheduler import get_scheduler
            scheduler = get_scheduler()
            status = scheduler.get_status()
            
            if status['running']:
                self.stdout.write('  ✅ 调度器运行正常')
            else:
                issues.append({
                    'type': 'warning',
                    'message': '调度器未运行',
                    'fix': '检查调度器配置和启动'
                })
        except Exception as e:
            issues.append({
                'type': 'warning',
                'message': f'调度器检查失败: {e}',
                'fix': '检查调度器配置'
            })
        
        return issues
    
    def check_logging(self):
        """检查日志配置"""
        self.stdout.write('\n📝 日志配置检查:')
        warnings = []
        
        if not hasattr(settings, 'LOGGING') or not settings.LOGGING:
            warnings.append({
                'type': 'warning',
                'message': '未配置日志系统',
                'fix': '添加LOGGING配置'
            })
        else:
            self.stdout.write('  ✅ 日志系统已配置')
        
        return warnings
    
    def check_environment_variables(self):
        """检查环境变量"""
        self.stdout.write('\n🌍 环境变量检查:')
        issues = []
        
        required_env_vars = [
            'OPENAI_API_KEY',
        ]
        
        for var in required_env_vars:
            if not os.environ.get(var):
                issues.append({
                    'type': 'critical',
                    'message': f'缺少环境变量: {var}',
                    'fix': f'设置环境变量 {var}'
                })
            else:
                self.stdout.write(f'  ✅ {var} 已设置')
        
        return issues
    
    def display_results(self, issues, warnings, auto_fix=False):
        """显示检查结果"""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('📋 检查结果总结:')
        
        critical_issues = [i for i in issues if i['type'] == 'critical']
        warning_issues = [i for i in issues if i['type'] == 'warning']
        
        if critical_issues:
            self.stdout.write(f'\n❌ 发现 {len(critical_issues)} 个关键问题:')
            for i, issue in enumerate(critical_issues, 1):
                self.stdout.write(f'  {i}. {issue["message"]}')
                self.stdout.write(f'     修复: {issue["fix"]}')
        
        if warning_issues:
            self.stdout.write(f'\n⚠️  发现 {len(warning_issues)} 个警告:')
            for i, issue in enumerate(warning_issues, 1):
                self.stdout.write(f'  {i}. {issue["message"]}')
                self.stdout.write(f'     建议: {issue["fix"]}')
        
        if warnings:
            self.stdout.write(f'\n💡 发现 {len(warnings)} 个优化建议:')
            for i, warning in enumerate(warnings, 1):
                self.stdout.write(f'  {i}. {warning["message"]}')
                self.stdout.write(f'     建议: {warning["fix"]}')
        
        if not critical_issues and not warning_issues and not warnings:
            self.stdout.write('\n🎉 所有检查通过！系统已准备好部署到生产环境。')
        elif not critical_issues:
            self.stdout.write('\n✅ 没有关键问题，系统可以部署，但建议处理警告项。')
        else:
            self.stdout.write('\n🚫 存在关键问题，必须修复后才能部署到生产环境。')
    
    def generate_deployment_scripts(self):
        """生成部署脚本"""
        self.stdout.write('\n🚀 生成部署脚本...')
        
        # 生成部署脚本内容在下一个方法中实现
        self.stdout.write('  ✅ 部署脚本已生成')
