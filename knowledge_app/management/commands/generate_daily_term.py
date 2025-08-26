"""
每日名词生成管理命令
用于定时任务调度，每日自动生成计算机专业名词
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import date, timedelta
import logging

from knowledge_app.services.daily_term_service import DailyTermService
from knowledge_app.models import DailyTerm

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '生成每日计算机专业名词解释'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='指定日期 (YYYY-MM-DD)，默认为今天'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新生成，即使已存在'
        )
        
        parser.add_argument(
            '--batch',
            type=int,
            help='批量生成多天的名词（从今天开始）'
        )
        
        parser.add_argument(
            '--backfill',
            type=int,
            help='回填过去N天的名词'
        )

    def handle(self, *args, **options):
        service = DailyTermService()
        
        try:
            if options['batch']:
                self.handle_batch_generation(service, options['batch'])
            elif options['backfill']:
                self.handle_backfill(service, options['backfill'])
            else:
                self.handle_single_generation(service, options)
                
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise CommandError(f"生成每日名词失败: {e}")

    def handle_single_generation(self, service, options):
        """处理单个日期的名词生成"""
        target_date = self.parse_date(options.get('date'))
        force = options.get('force', False)
        
        self.stdout.write(f"正在为 {target_date} 生成每日名词...")
        
        # 检查是否已存在
        if not force:
            existing = DailyTerm.objects.filter(
                display_date=target_date,
                status='active'
            ).first()
            
            if existing:
                self.stdout.write(
                    self.style.WARNING(
                        f"日期 {target_date} 已存在名词: {existing.term}"
                    )
                )
                return
        
        # 如果强制重新生成，先将现有的设为归档状态
        if force:
            DailyTerm.objects.filter(
                display_date=target_date,
                status='active'
            ).update(status='archived')
        
        # 生成新名词
        daily_term = service.generate_daily_term(target_date)
        
        if daily_term:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ 成功生成每日名词: {daily_term.term}\n"
                    f"   分类: {daily_term.category}\n"
                    f"   难度: {daily_term.get_difficulty_level_display()}\n"
                    f"   日期: {daily_term.display_date}"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR("❌ 生成每日名词失败")
            )

    def handle_batch_generation(self, service, days):
        """批量生成多天的名词"""
        self.stdout.write(f"正在批量生成未来 {days} 天的名词...")
        
        success_count = 0
        failed_count = 0
        
        for i in range(days):
            target_date = timezone.now().date() + timedelta(days=i)
            
            # 检查是否已存在
            if DailyTerm.objects.filter(
                display_date=target_date,
                status='active'
            ).exists():
                self.stdout.write(f"⏭️  {target_date} 已存在名词，跳过")
                continue
            
            self.stdout.write(f"正在生成 {target_date} 的名词...")
            
            daily_term = service.generate_daily_term(target_date)
            
            if daily_term:
                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ {target_date}: {daily_term.term}")
                )
            else:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f"❌ {target_date}: 生成失败")
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n批量生成完成: 成功 {success_count} 个，失败 {failed_count} 个"
            )
        )

    def handle_backfill(self, service, days):
        """回填过去几天的名词"""
        self.stdout.write(f"正在回填过去 {days} 天的名词...")
        
        success_count = 0
        failed_count = 0
        
        for i in range(1, days + 1):
            target_date = timezone.now().date() - timedelta(days=i)
            
            # 检查是否已存在
            if DailyTerm.objects.filter(
                display_date=target_date,
                status='active'
            ).exists():
                self.stdout.write(f"⏭️  {target_date} 已存在名词，跳过")
                continue
            
            self.stdout.write(f"正在回填 {target_date} 的名词...")
            
            daily_term = service.generate_daily_term(target_date)
            
            if daily_term:
                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ {target_date}: {daily_term.term}")
                )
            else:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f"❌ {target_date}: 生成失败")
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n回填完成: 成功 {success_count} 个，失败 {failed_count} 个"
            )
        )

    def parse_date(self, date_str):
        """解析日期字符串"""
        if not date_str:
            return timezone.now().date()
        
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            raise CommandError(f"无效的日期格式: {date_str}，请使用 YYYY-MM-DD 格式")


# 使用示例：
# python manage.py generate_daily_term                    # 生成今天的名词
# python manage.py generate_daily_term --date 2024-01-15  # 生成指定日期的名词
# python manage.py generate_daily_term --force            # 强制重新生成今天的名词
# python manage.py generate_daily_term --batch 7          # 批量生成未来7天的名词
# python manage.py generate_daily_term --backfill 7       # 回填过去7天的名词
