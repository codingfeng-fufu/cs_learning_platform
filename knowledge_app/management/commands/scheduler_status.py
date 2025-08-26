"""
查看调度器状态的管理命令
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
import pytz

class Command(BaseCommand):
    help = '查看每日名词调度器状态'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='显示详细状态信息',
        )
        parser.add_argument(
            '--restart',
            action='store_true',
            help='重启调度器',
        )
    
    def handle(self, *args, **options):
        if options['restart']:
            self.restart_scheduler()
        else:
            self.show_status(detailed=options['detailed'])
    
    def show_status(self, detailed=False):
        """显示调度器状态"""
        self.stdout.write('📊 每日名词调度器状态')
        self.stdout.write('=' * 40)
        
        # 检查当前名词状态
        self.check_current_term()
        
        # 检查调度器状态
        self.check_scheduler_status(detailed)
        
        # 显示最近的名词
        if detailed:
            self.show_recent_terms()
        
        # 显示下次执行时间
        self.show_next_execution()
    
    def check_current_term(self):
        """检查当前名词状态"""
        from knowledge_app.models import DailyTerm
        
        beijing_tz = pytz.timezone('Asia/Shanghai')
        beijing_now = timezone.now().astimezone(beijing_tz)
        today = beijing_now.date()
        
        self.stdout.write(f'\n📅 当前时间: {beijing_now.strftime("%Y-%m-%d %H:%M:%S")} (北京时间)')
        
        today_term = DailyTerm.objects.filter(display_date=today, status='active').first()
        if today_term:
            self.stdout.write(self.style.SUCCESS(f'✅ 今日名词: {today_term.term}'))
            self.stdout.write(f'   分类: {today_term.category}')
            self.stdout.write(f'   难度: {today_term.get_difficulty_level_display()}')
            self.stdout.write(f'   创建时间: {today_term.created_at.strftime("%Y-%m-%d %H:%M:%S")}')
        else:
            self.stdout.write(self.style.ERROR('❌ 今日名词不存在'))
    
    def check_scheduler_status(self, detailed=False):
        """检查调度器状态"""
        self.stdout.write('\n🔧 调度器状态:')
        
        try:
            # 尝试获取高级调度器状态
            from knowledge_app.services.advanced_scheduler import get_scheduler
            scheduler = get_scheduler()
            status = scheduler.get_status()
            
            if status['running']:
                self.stdout.write(self.style.SUCCESS('✅ 高级调度器正在运行'))
                self.stdout.write(f'   调度器类型: {status["scheduler_type"]}')
                
                if detailed and 'scheduled_jobs' in status:
                    self.stdout.write('\n📋 已安排的任务:')
                    for job in status['scheduled_jobs']:
                        self.stdout.write(f'   • {job["name"]}: {job["next_run"]}')
            else:
                self.stdout.write(self.style.WARNING('⚠️  高级调度器未运行'))
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  无法获取高级调度器状态: {e}'))
            
            # 检查基础调度器
            try:
                from knowledge_app.management.commands.start_daily_term_scheduler import _global_scheduler
                if _global_scheduler and _global_scheduler.running:
                    self.stdout.write(self.style.SUCCESS('✅ 基础调度器正在运行'))
                else:
                    self.stdout.write(self.style.ERROR('❌ 基础调度器未运行'))
            except Exception as e2:
                self.stdout.write(self.style.ERROR(f'❌ 无法检查调度器状态: {e2}'))
    
    def show_recent_terms(self):
        """显示最近的名词"""
        from knowledge_app.models import DailyTerm
        
        self.stdout.write('\n📋 最近7天的名词:')
        recent_terms = DailyTerm.objects.filter(status='active').order_by('-display_date')[:7]
        
        if recent_terms:
            for term in recent_terms:
                self.stdout.write(f'   {term.display_date}: {term.term}')
        else:
            self.stdout.write('   没有找到名词记录')
    
    def show_next_execution(self):
        """显示下次执行时间"""
        beijing_tz = pytz.timezone('Asia/Shanghai')
        beijing_now = timezone.now().astimezone(beijing_tz)
        
        # 计算下次零点时间
        from datetime import datetime, timedelta
        
        if beijing_now.hour == 0 and beijing_now.minute < 5:
            # 如果现在就在零点时间窗口内
            next_execution = "现在就是执行时间！"
        else:
            # 计算明天零点
            tomorrow = beijing_now.date() + timedelta(days=1)
            next_midnight = beijing_tz.localize(datetime.combine(tomorrow, datetime.min.time()))
            next_execution = next_midnight.strftime('%Y-%m-%d %H:%M:%S')
        
        self.stdout.write(f'\n⏰ 下次自动生成时间: {next_execution}')
        
        # 显示距离下次执行的时间
        if next_execution != "现在就是执行时间！":
            tomorrow = beijing_now.date() + timedelta(days=1)
            next_midnight = beijing_tz.localize(datetime.combine(tomorrow, datetime.min.time()))
            time_diff = next_midnight - beijing_now
            hours = int(time_diff.total_seconds() // 3600)
            minutes = int((time_diff.total_seconds() % 3600) // 60)
            self.stdout.write(f'   距离下次执行: {hours}小时{minutes}分钟')
    
    def restart_scheduler(self):
        """重启调度器"""
        self.stdout.write('🔄 重启调度器...')
        
        try:
            # 停止现有调度器
            from knowledge_app.services.advanced_scheduler import stop_advanced_scheduler, start_advanced_scheduler
            
            self.stdout.write('⏹️  停止现有调度器...')
            stop_advanced_scheduler()
            
            self.stdout.write('🚀 启动新调度器...')
            scheduler = start_advanced_scheduler()
            
            self.stdout.write(self.style.SUCCESS('✅ 调度器重启成功'))
            
            # 显示状态
            status = scheduler.get_status()
            if status['running']:
                self.stdout.write(f'   调度器类型: {status["scheduler_type"]}')
                if 'scheduled_jobs' in status:
                    self.stdout.write('   已安排的任务:')
                    for job in status['scheduled_jobs']:
                        self.stdout.write(f'     • {job["name"]}: {job["next_run"]}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 重启失败: {e}'))
            import traceback
            traceback.print_exc()
    
    def handle_no_args(self, **options):
        """处理无参数情况"""
        self.show_status()
