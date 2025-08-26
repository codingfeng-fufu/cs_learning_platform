"""
检查并生成每日名词的管理命令
可以手动运行来确保每日名词正常生成
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import pytz
from knowledge_app.models import DailyTerm
from knowledge_app.services.daily_term_service import DailyTermService


class Command(BaseCommand):
    help = '检查并生成每日名词'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='指定日期 (YYYY-MM-DD)，默认为今天',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新生成，即使已存在',
        )
        parser.add_argument(
            '--check-missing',
            action='store_true',
            help='检查并生成最近7天缺失的名词',
        )

    def handle(self, *args, **options):
        beijing_tz = pytz.timezone('Asia/Shanghai')
        
        if options['check_missing']:
            self.check_and_generate_missing_terms(beijing_tz)
        else:
            target_date = self.get_target_date(options['date'], beijing_tz)
            self.check_and_generate_term(target_date, options['force'])

    def get_target_date(self, date_str, beijing_tz):
        """获取目标日期"""
        if date_str:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f'日期格式错误: {date_str}，请使用 YYYY-MM-DD 格式')
                )
                return None
        else:
            return timezone.now().astimezone(beijing_tz).date()

    def check_and_generate_term(self, target_date, force=False):
        """检查并生成指定日期的名词"""
        if not target_date:
            return

        self.stdout.write(f'检查日期: {target_date}')

        # 检查是否已存在
        existing_term = DailyTerm.objects.filter(
            display_date=target_date,
            status='active'
        ).first()

        if existing_term and not force:
            self.stdout.write(
                self.style.SUCCESS(f'✅ {target_date} 的每日名词已存在: {existing_term.term}')
            )
            return

        if existing_term and force:
            self.stdout.write(f'🔄 强制重新生成 {target_date} 的每日名词...')
            # 将现有名词标记为已替换
            existing_term.status = 'replaced'
            existing_term.save()

        # 生成新名词
        self.stdout.write(f'📝 正在生成 {target_date} 的每日名词...')
        
        try:
            service = DailyTermService()
            daily_term = service.generate_daily_term(target_date)
            
            if daily_term:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ 成功生成每日名词: {daily_term.term}')
                )
                self.stdout.write(f'   分类: {daily_term.category}')
                self.stdout.write(f'   难度: {daily_term.difficulty_level}')
                self.stdout.write(f'   日期: {daily_term.display_date}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ 生成 {target_date} 的每日名词失败')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 生成过程中出错: {str(e)}')
            )

    def check_and_generate_missing_terms(self, beijing_tz):
        """检查并生成最近7天缺失的名词"""
        self.stdout.write('🔍 检查最近7天的每日名词...')
        
        today = timezone.now().astimezone(beijing_tz).date()
        missing_dates = []
        
        for i in range(7):
            check_date = today - timedelta(days=i)
            existing_term = DailyTerm.objects.filter(
                display_date=check_date,
                status='active'
            ).first()
            
            if existing_term:
                self.stdout.write(f'✅ {check_date}: {existing_term.term}')
            else:
                self.stdout.write(f'❌ {check_date}: 缺失')
                missing_dates.append(check_date)
        
        if not missing_dates:
            self.stdout.write(
                self.style.SUCCESS('🎉 最近7天的每日名词都已存在！')
            )
            return
        
        self.stdout.write(f'📝 发现 {len(missing_dates)} 个缺失的日期，开始生成...')
        
        service = DailyTermService()
        success_count = 0
        
        for missing_date in reversed(missing_dates):  # 从最早的日期开始生成
            try:
                self.stdout.write(f'正在生成 {missing_date} 的名词...')
                daily_term = service.generate_daily_term(missing_date)
                
                if daily_term:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {missing_date}: {daily_term.term}')
                    )
                    success_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ {missing_date}: 生成失败')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ {missing_date}: 生成出错 - {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'🎉 完成！成功生成 {success_count}/{len(missing_dates)} 个名词')
        )
