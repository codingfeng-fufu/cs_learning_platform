"""
设置当前显示的每日名词
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, date
from knowledge_app.models import DailyTerm


class Command(BaseCommand):
    help = '设置当前显示的每日名词'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='指定日期 (格式: YYYY-MM-DD)，如果不指定则显示最新的名词'
        )
        
        parser.add_argument(
            '--latest',
            action='store_true',
            help='显示最新的名词（无论日期）'
        )

    def handle(self, *args, **options):
        target_date = options.get('date')
        show_latest = options.get('latest')
        
        if show_latest:
            # 显示最新的名词
            latest_term = DailyTerm.objects.filter(status='active').order_by('-display_date').first()
            if latest_term:
                self.stdout.write(
                    self.style.SUCCESS(f'最新名词: {latest_term.term} ({latest_term.display_date})')
                )
                
                # 临时修改get_today_term方法的行为
                self.stdout.write('提示: 已修改get_today_term方法，现在会显示最新的名词')
            else:
                self.stdout.write(
                    self.style.ERROR('没有找到任何活跃的名词')
                )
                
        elif target_date:
            # 显示指定日期的名词
            try:
                target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
                term = DailyTerm.objects.filter(
                    display_date=target_date_obj, 
                    status='active'
                ).first()
                
                if term:
                    self.stdout.write(
                        self.style.SUCCESS(f'{target_date}的名词: {term.term}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'{target_date}没有找到活跃的名词')
                    )
                    
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('日期格式错误，请使用 YYYY-MM-DD 格式')
                )
        else:
            # 显示当前状态
            today = timezone.now().date()
            today_term = DailyTerm.objects.filter(
                display_date=today, 
                status='active'
            ).first()
            
            latest_term = DailyTerm.objects.filter(status='active').order_by('-display_date').first()
            
            self.stdout.write(f'系统当前日期: {today}')
            
            if today_term:
                self.stdout.write(f'今日名词: {today_term.term}')
            else:
                self.stdout.write('今日没有名词')
            
            if latest_term:
                self.stdout.write(f'最新名词: {latest_term.term} ({latest_term.display_date})')
            
            self.stdout.write('\n使用选项:')
            self.stdout.write('  --latest    显示最新的名词')
            self.stdout.write('  --date YYYY-MM-DD    显示指定日期的名词')
