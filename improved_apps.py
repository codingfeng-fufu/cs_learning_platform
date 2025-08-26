"""
改进的apps.py配置
解决调度器启动问题
"""

from django.apps import AppConfig
import os
import threading
import time
from django.conf import settings

class KnowledgeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'knowledge_app'
    
    def ready(self):
        """应用准备就绪时的初始化"""
        # 导入信号处理器
        from . import signals
        
        # 启动每日名词调度器
        self.start_daily_term_scheduler()
    
    def start_daily_term_scheduler(self):
        """启动每日名词调度器"""
        # 检查是否应该启动调度器
        if not self.should_start_scheduler():
            print("⏸️  跳过调度器启动")
            return
        
        print("🚀 启动每日名词调度器...")
        
        try:
            # 延迟启动，确保Django完全初始化
            def delayed_start():
                time.sleep(5)  # 等待5秒
                self._start_scheduler_thread()
            
            # 在后台线程中启动
            thread = threading.Thread(target=delayed_start, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"❌ 启动调度器失败: {e}")
    
    def should_start_scheduler(self):
        """判断是否应该启动调度器"""
        # 检查多个条件
        conditions = [
            # 开发服务器标识
            os.environ.get('RUN_MAIN') == 'true',
            # 或者是生产环境
            not settings.DEBUG,
            # 或者明确设置了启动标识
            os.environ.get('START_SCHEDULER') == 'true',
            # 或者是manage.py runserver命令
            'runserver' in ' '.join(os.sys.argv) if hasattr(os, 'sys') else False
        ]
        
        should_start = any(conditions)
        
        print(f"📊 调度器启动条件检查:")
        print(f"  RUN_MAIN: {os.environ.get('RUN_MAIN')}")
        print(f"  DEBUG: {settings.DEBUG}")
        print(f"  START_SCHEDULER: {os.environ.get('START_SCHEDULER')}")
        print(f"  命令行参数: {' '.join(getattr(os.sys, 'argv', []))}")
        print(f"  结果: {'启动' if should_start else '跳过'}")
        
        return should_start
    
    def _start_scheduler_thread(self):
        """在线程中启动调度器"""
        try:
            from .management.commands.start_daily_term_scheduler import DailyTermScheduler
            
            scheduler = DailyTermScheduler()
            
            # 立即检查一次
            print("🔍 立即检查是否需要生成今日名词...")
            scheduler.check_and_generate_daily_term()
            
            # 启动定时检查
            print("⏰ 启动定时检查...")
            scheduler.start_scheduler()
            
        except Exception as e:
            print(f"❌ 调度器线程启动失败: {e}")
            import traceback
            traceback.print_exc()

# 备用启动方法：使用Django信号
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def start_scheduler_after_migrate(sender, **kwargs):
    """在数据库迁移后启动调度器"""
    if sender.name == 'knowledge_app':
        print("📡 数据库迁移完成，准备启动调度器...")
        
        # 延迟启动
        def delayed_scheduler_start():
            time.sleep(10)  # 等待10秒确保一切就绪
            try:
                from knowledge_app.management.commands.start_daily_term_scheduler import DailyTermScheduler
                scheduler = DailyTermScheduler()
                scheduler.check_and_generate_daily_term()
                print("✅ 备用调度器启动成功")
            except Exception as e:
                print(f"❌ 备用调度器启动失败: {e}")
        
        thread = threading.Thread(target=delayed_scheduler_start, daemon=True)
        thread.start()

# 手动启动函数
def manual_start_scheduler():
    """手动启动调度器的函数"""
    print("🔧 手动启动每日名词调度器...")
    
    try:
        from knowledge_app.management.commands.start_daily_term_scheduler import DailyTermScheduler
        
        scheduler = DailyTermScheduler()
        
        # 立即检查
        scheduler.check_and_generate_daily_term()
        
        # 启动定时任务
        scheduler.start_scheduler()
        
        print("✅ 手动启动成功")
        return True
        
    except Exception as e:
        print(f"❌ 手动启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 创建一个管理命令来手动启动
def create_manual_command():
    """创建手动启动命令"""
    command_content = '''
from django.core.management.base import BaseCommand
from knowledge_app.apps import manual_start_scheduler

class Command(BaseCommand):
    help = '手动启动每日名词调度器'
    
    def handle(self, *args, **options):
        self.stdout.write('🚀 手动启动每日名词调度器...')
        
        success = manual_start_scheduler()
        
        if success:
            self.stdout.write(self.style.SUCCESS('✅ 调度器启动成功'))
        else:
            self.stdout.write(self.style.ERROR('❌ 调度器启动失败'))
'''
    
    # 保存命令文件
    import os
    command_dir = 'knowledge_app/management/commands'
    os.makedirs(command_dir, exist_ok=True)
    
    with open(f'{command_dir}/start_scheduler.py', 'w', encoding='utf-8') as f:
        f.write(command_content)
    
    print("📝 已创建手动启动命令: python manage.py start_scheduler")

# 环境检查函数
def check_scheduler_environment():
    """检查调度器运行环境"""
    print("🔍 检查调度器运行环境...")
    
    issues = []
    
    # 检查环境变量
    if not os.environ.get('RUN_MAIN') and settings.DEBUG:
        issues.append("开发环境下RUN_MAIN环境变量未设置")
    
    # 检查API配置
    try:
        from django.conf import settings
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            issues.append("OpenAI API密钥未配置")
    except:
        issues.append("无法检查API配置")
    
    # 检查数据库连接
    try:
        from django.db import connection
        connection.ensure_connection()
        print("✅ 数据库连接正常")
    except Exception as e:
        issues.append(f"数据库连接问题: {e}")
    
    if issues:
        print("⚠️  发现以下问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ 环境检查通过")
        return True

if __name__ == "__main__":
    # 如果直接运行此文件，进行环境检查
    check_scheduler_environment()
    create_manual_command()
