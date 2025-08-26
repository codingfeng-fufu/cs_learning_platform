"""
每日名词调度器
在开发服务器运行时自动执行每日名词生成任务
"""

import time
import threading
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
import logging
import pytz

from knowledge_app.services.daily_term_service import DailyTermService
from knowledge_app.models import DailyTerm

logger = logging.getLogger(__name__)


class DailyTermScheduler:
    """每日名词调度器"""
    
    def __init__(self):
        self.service = DailyTermService()
        self.running = False
        self.thread = None
        self.last_check_date = None
        
    def start(self):
        """启动调度器"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print("🚀 每日名词调度器已启动")
        
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("⏹️  每日名词调度器已停止")
        
    def _run_scheduler(self):
        """运行调度器主循环 - 精确的定时任务系统"""
        beijing_tz = pytz.timezone('Asia/Shanghai')
        last_generated_date = None

        print("🕐 定时调度器启动 - 每天零点自动生成名词")

        while self.running:
            try:
                # 获取北京时间
                beijing_now = timezone.now().astimezone(beijing_tz)
                current_date = beijing_now.date()
                current_hour = beijing_now.hour
                current_minute = beijing_now.minute

                # 检查是否到了生成时间（每天00:00-00:05之间）
                is_generation_time = current_hour == 0 and current_minute < 5

                # 检查今天是否还没有生成过
                need_generate = (
                    last_generated_date != current_date and  # 今天还没生成过
                    self._should_generate_term(current_date)  # 确实需要生成
                )

                if is_generation_time and need_generate:
                    print(f"🕛 北京时间 {beijing_now.strftime('%Y-%m-%d %H:%M:%S')} - 零点定时生成每日名词")
                    success = self._generate_daily_term(current_date)
                    if success:
                        last_generated_date = current_date
                        print(f"✅ 定时生成成功，下次生成时间：明天00:00")
                    else:
                        print(f"❌ 定时生成失败，将在5分钟后重试")

                elif not is_generation_time and need_generate:
                    # 如果不在零点时间但需要生成（比如首次启动），立即生成
                    print(f"🔍 北京时间 {beijing_now.strftime('%Y-%m-%d %H:%M:%S')} - 检测到需要补充生成今日名词")
                    success = self._generate_daily_term(current_date)
                    if success:
                        last_generated_date = current_date

                # 显示状态信息
                if current_minute == 0:  # 每小时整点显示状态
                    next_generation = self._get_next_generation_time(beijing_now)
                    print(f"⏰ 北京时间 {beijing_now.strftime('%Y-%m-%d %H:%M:%S')} - 调度器运行中")
                    print(f"   下次生成时间: {next_generation}")

                    existing_term = DailyTerm.objects.filter(
                        display_date=current_date,
                        status='active'
                    ).first()
                    if existing_term:
                        print(f"   今日名词: {existing_term.term}")

                # 动态睡眠时间：零点前后更频繁检查
                if is_generation_time:
                    sleep_time = 60  # 零点时间每分钟检查一次
                elif current_hour == 23 and current_minute >= 55:
                    sleep_time = 60  # 临近零点每分钟检查一次
                else:
                    sleep_time = 1800  # 其他时间每30分钟检查一次

                time.sleep(sleep_time)

            except Exception as e:
                logger.error(f"调度器运行错误: {e}")
                print(f"❌ 调度器错误: {e}")
                time.sleep(300)  # 出错后5分钟后重试
    
    def _should_generate_term(self, date):
        """检查是否需要生成名词"""
        # 检查今日是否已有名词
        existing_term = DailyTerm.objects.filter(
            display_date=date,
            status='active'
        ).first()

        if existing_term:
            # 如果今天已经有名词，更新检查日期
            self.last_check_date = date
            return False

        # 如果今天已经检查过但没有生成成功，允许重试（但限制重试次数）
        if self.last_check_date == date:
            # 检查是否有失败的生成记录
            failed_attempts = DailyTerm.objects.filter(
                display_date=date,
                status='failed'
            ).count()

            # 如果失败次数少于3次，允许重试
            return failed_attempts < 3

        return True

    def _get_next_generation_time(self, current_time):
        """获取下次生成时间"""
        from datetime import timedelta

        beijing_tz = pytz.timezone('Asia/Shanghai')

        # 如果当前时间还没到今天的零点，下次生成就是今天零点
        if current_time.hour > 0 or current_time.minute >= 5:
            # 明天零点
            next_date = current_time.date() + timedelta(days=1)
            next_time = beijing_tz.localize(datetime.combine(next_date, datetime.min.time()))
        else:
            # 今天零点（如果还在零点时间窗口内）
            next_time = beijing_tz.localize(datetime.combine(current_time.date(), datetime.min.time()))

        return next_time.strftime('%Y-%m-%d %H:%M:%S')

    def check_and_generate_daily_term(self):
        """立即检查并生成今日名词（如果需要）"""
        beijing_tz = pytz.timezone('Asia/Shanghai')
        beijing_now = timezone.now().astimezone(beijing_tz)
        current_date = beijing_now.date()

        print(f"🔍 检查今日名词状态 - 北京时间: {beijing_now.strftime('%Y-%m-%d %H:%M:%S')}")

        if self._should_generate_term(current_date):
            print(f"📝 需要生成今日名词")
            self._generate_daily_term(current_date)
        else:
            existing_term = DailyTerm.objects.filter(
                display_date=current_date,
                status='active'
            ).first()
            if existing_term:
                print(f"✅ 今日名词已存在: {existing_term.term}")
            else:
                print(f"⚠️  未找到今日名词，但调度器认为不需要生成")

    def start_scheduler(self):
        """启动定时调度器"""
        if self.running:
            print("⚠️  调度器已在运行中")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print("🚀 定时调度器已启动")

    def _generate_daily_term(self, date):
        """生成每日名词"""
        try:
            print(f"📅 {date} - 开始生成每日名词...")
            
            daily_term = self.service.generate_daily_term(date)
            
            if daily_term:
                print(f"✅ 成功生成每日名词: {daily_term.term}")
                print(f"   分类: {daily_term.category}")
                print(f"   难度: {daily_term.get_difficulty_level_display()}")
            else:
                print(f"❌ 生成每日名词失败")
                
        except Exception as e:
            print(f"❌ 生成每日名词时出错: {e}")
            logger.error(f"生成每日名词失败: {e}")


class Command(BaseCommand):
    help = '启动每日名词调度器（开发环境使用）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-interval',
            type=int,
            default=3600,
            help='检查间隔（秒），默认3600秒（1小时）'
        )
        
        parser.add_argument(
            '--immediate',
            action='store_true',
            help='立即检查并生成今日名词'
        )

    def handle(self, *args, **options):
        check_interval = options['check_interval']
        immediate = options['immediate']
        
        self.stdout.write("🚀 启动每日名词调度器...")
        self.stdout.write(f"⏰ 检查间隔: {check_interval}秒")
        
        service = DailyTermService()
        
        # 立即检查
        if immediate:
            self.stdout.write("🔍 立即检查今日名词...")
            current_date = timezone.now().date()
            
            existing_term = DailyTerm.objects.filter(
                display_date=current_date,
                status='active'
            ).first()
            
            if existing_term:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ 今日名词已存在: {existing_term.term}")
                )
            else:
                self.stdout.write("📝 生成今日名词...")
                try:
                    daily_term = service.generate_daily_term(current_date)
                    if daily_term:
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ 成功生成: {daily_term.term}")
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR("❌ 生成失败")
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"❌ 生成错误: {e}")
                    )
        
        # 启动后台调度器
        scheduler = DailyTermScheduler()
        
        try:
            scheduler.start()
            
            self.stdout.write(
                self.style.SUCCESS("✅ 调度器已启动，按 Ctrl+C 停止")
            )
            
            # 保持运行
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.stdout.write("\n⏹️  正在停止调度器...")
            scheduler.stop()
            self.stdout.write(
                self.style.SUCCESS("✅ 调度器已停止")
            )


# 全局调度器实例（用于开发服务器集成）
_global_scheduler = None

def start_scheduler():
    """启动全局调度器"""
    global _global_scheduler
    if _global_scheduler is None:
        _global_scheduler = DailyTermScheduler()
        _global_scheduler.start()

def stop_scheduler():
    """停止全局调度器"""
    global _global_scheduler
    if _global_scheduler:
        _global_scheduler.stop()
        _global_scheduler = None
