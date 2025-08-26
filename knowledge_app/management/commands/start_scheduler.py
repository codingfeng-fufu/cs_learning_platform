"""
手动启动每日名词调度器的管理命令
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
import pytz

class Command(BaseCommand):
    help = '手动启动每日名词调度器'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='只检查一次，不启动定时调度器',
        )
        parser.add_argument(
            '--force-generate',
            action='store_true',
            help='强制生成今日名词（即使已存在）',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('🚀 手动启动每日名词调度器...')
        
        try:
            from knowledge_app.management.commands.start_daily_term_scheduler import DailyTermScheduler
            from knowledge_app.models import DailyTerm
            
            scheduler = DailyTermScheduler()
            
            # 显示当前状态
            beijing_tz = pytz.timezone('Asia/Shanghai')
            today = timezone.now().astimezone(beijing_tz).date()
            
            self.stdout.write(f'📅 当前日期: {today}')
            
            existing_term = DailyTerm.objects.filter(display_date=today, status='active').first()
            if existing_term:
                self.stdout.write(f'✅ 今日名词已存在: {existing_term.term}')
            else:
                self.stdout.write('❌ 今日名词不存在')
            
            # 强制生成
            if options['force_generate']:
                self.stdout.write('🔧 强制生成今日名词...')
                
                # 如果已存在，先删除
                if existing_term:
                    existing_term.delete()
                    self.stdout.write('🗑️  已删除现有名词')
                
                # 生成新名词
                scheduler._generate_daily_term(today)
                
            elif options['check_only']:
                # 只检查一次
                self.stdout.write('🔍 检查是否需要生成今日名词...')
                scheduler.check_and_generate_daily_term()
                
            else:
                # 启动完整的调度器
                self.stdout.write('🔍 立即检查是否需要生成今日名词...')
                scheduler.check_and_generate_daily_term()
                
                self.stdout.write('⏰ 启动定时调度器...')
                scheduler.start_scheduler()
                
                self.stdout.write(self.style.SUCCESS('✅ 调度器启动成功'))
                self.stdout.write('💡 调度器将在后台运行，每小时检查一次')
                
                # 保持运行
                try:
                    import time
                    while True:
                        time.sleep(60)  # 每分钟检查一次是否还在运行
                        if not scheduler.running:
                            break
                except KeyboardInterrupt:
                    self.stdout.write('\n⏹️  收到中断信号，停止调度器...')
                    scheduler.stop()
                    self.stdout.write('✅ 调度器已停止')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 启动失败: {e}'))
            import traceback
            traceback.print_exc()
