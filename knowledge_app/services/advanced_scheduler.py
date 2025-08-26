"""
高级定时调度器 - 使用APScheduler实现精确的定时任务
"""

import os
import sys
import django
from datetime import datetime, time
import pytz
import logging
from typing import Optional

# 设置Django环境
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CS_Learning_Platform.settings')
    django.setup()

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.executors.pool import ThreadPoolExecutor
    from apscheduler.jobstores.memory import MemoryJobStore
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    print("⚠️  APScheduler未安装，使用基础调度器")

from django.utils import timezone
from knowledge_app.models import DailyTerm
from knowledge_app.services.daily_term_service import DailyTermService

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedDailyTermScheduler:
    """高级每日名词调度器"""
    
    def __init__(self):
        self.scheduler = None
        self.running = False
        self.beijing_tz = pytz.timezone('Asia/Shanghai')
        
        if APSCHEDULER_AVAILABLE:
            self._setup_apscheduler()
        else:
            print("📝 将使用基础定时器")
    
    def _setup_apscheduler(self):
        """设置APScheduler"""
        # 配置作业存储和执行器
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(max_workers=2)
        }
        job_defaults = {
            'coalesce': True,  # 合并错过的作业
            'max_instances': 1,  # 同一时间只运行一个实例
            'misfire_grace_time': 300  # 错过执行时间5分钟内仍可执行
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=self.beijing_tz
        )
    
    def start(self):
        """启动调度器"""
        if self.running:
            print("⚠️  调度器已在运行中")
            return
        
        print("🚀 启动高级定时调度器...")
        
        # 立即检查一次
        self._immediate_check()
        
        if APSCHEDULER_AVAILABLE and self.scheduler:
            self._start_apscheduler()
        else:
            self._start_basic_scheduler()
        
        self.running = True
        print("✅ 定时调度器已启动")
    
    def _start_apscheduler(self):
        """启动APScheduler"""
        # 添加每日零点的定时任务
        self.scheduler.add_job(
            func=self._generate_daily_term_job,
            trigger=CronTrigger(hour=0, minute=0, second=0),  # 每天00:00:00
            id='daily_term_generation',
            name='每日名词生成任务',
            replace_existing=True
        )
        
        # 添加备用检查任务（每天00:05）
        self.scheduler.add_job(
            func=self._backup_check_job,
            trigger=CronTrigger(hour=0, minute=5, second=0),  # 每天00:05:00
            id='daily_term_backup_check',
            name='每日名词备用检查',
            replace_existing=True
        )
        
        # 添加状态监控任务（每小时）
        self.scheduler.add_job(
            func=self._status_monitor_job,
            trigger=CronTrigger(minute=0),  # 每小时整点
            id='status_monitor',
            name='状态监控',
            replace_existing=True
        )
        
        # 启动调度器
        self.scheduler.start()
        
        # 显示已安排的任务
        self._show_scheduled_jobs()
    
    def _start_basic_scheduler(self):
        """启动基础调度器"""
        import threading
        
        def basic_scheduler_loop():
            import time
            last_generated_date = None
            
            while self.running:
                try:
                    beijing_now = timezone.now().astimezone(self.beijing_tz)
                    current_date = beijing_now.date()
                    current_hour = beijing_now.hour
                    current_minute = beijing_now.minute
                    
                    # 零点时间窗口（00:00-00:05）
                    is_generation_time = current_hour == 0 and current_minute < 5
                    
                    if is_generation_time and last_generated_date != current_date:
                        if self._should_generate_term(current_date):
                            print(f"🕛 零点定时生成 - {beijing_now.strftime('%Y-%m-%d %H:%M:%S')}")
                            success = self._generate_daily_term(current_date)
                            if success:
                                last_generated_date = current_date
                    
                    # 动态睡眠
                    if is_generation_time or (current_hour == 23 and current_minute >= 55):
                        time.sleep(60)  # 零点前后每分钟检查
                    else:
                        time.sleep(1800)  # 其他时间每30分钟检查
                        
                except Exception as e:
                    logger.error(f"基础调度器错误: {e}")
                    time.sleep(300)
        
        thread = threading.Thread(target=basic_scheduler_loop, daemon=True)
        thread.start()
    
    def _immediate_check(self):
        """立即检查当前状态"""
        beijing_now = timezone.now().astimezone(self.beijing_tz)
        current_date = beijing_now.date()
        
        print(f"🔍 立即检查 - 北京时间: {beijing_now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self._should_generate_term(current_date):
            print("📝 检测到需要生成今日名词，立即执行...")
            self._generate_daily_term(current_date)
        else:
            existing_term = DailyTerm.objects.filter(
                display_date=current_date, 
                status='active'
            ).first()
            if existing_term:
                print(f"✅ 今日名词已存在: {existing_term.term}")
            else:
                print("⚠️  未找到今日名词，但系统认为不需要生成")
    
    def _generate_daily_term_job(self):
        """定时生成任务"""
        beijing_now = timezone.now().astimezone(self.beijing_tz)
        current_date = beijing_now.date()
        
        print(f"🕛 定时任务触发 - {beijing_now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self._should_generate_term(current_date):
            self._generate_daily_term(current_date)
        else:
            print("✅ 今日名词已存在，跳过生成")
    
    def _backup_check_job(self):
        """备用检查任务"""
        beijing_now = timezone.now().astimezone(self.beijing_tz)
        current_date = beijing_now.date()
        
        print(f"🔍 备用检查 - {beijing_now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self._should_generate_term(current_date):
            print("⚠️  零点生成可能失败，执行备用生成...")
            self._generate_daily_term(current_date)
    
    def _status_monitor_job(self):
        """状态监控任务"""
        beijing_now = timezone.now().astimezone(self.beijing_tz)
        current_date = beijing_now.date()
        
        existing_term = DailyTerm.objects.filter(
            display_date=current_date, 
            status='active'
        ).first()
        
        if existing_term:
            print(f"⏰ 状态监控 - {beijing_now.strftime('%H:%M')} - 今日名词: {existing_term.term}")
        else:
            print(f"⚠️  状态监控 - {beijing_now.strftime('%H:%M')} - 今日名词缺失！")
    
    def _should_generate_term(self, date) -> bool:
        """检查是否需要生成名词"""
        existing_term = DailyTerm.objects.filter(
            display_date=date,
            status='active'
        ).first()
        
        return existing_term is None
    
    def _generate_daily_term(self, date) -> bool:
        """生成每日名词"""
        try:
            service = DailyTermService()
            daily_term = service.generate_daily_term(date)
            
            if daily_term:
                print(f"✅ 成功生成每日名词: {daily_term.term}")
                return True
            else:
                print("❌ 生成每日名词失败")
                return False
                
        except Exception as e:
            print(f"❌ 生成每日名词时出错: {e}")
            logger.error(f"生成每日名词错误: {e}")
            return False
    
    def _show_scheduled_jobs(self):
        """显示已安排的任务"""
        if not self.scheduler:
            return
            
        print("\n📋 已安排的定时任务:")
        for job in self.scheduler.get_jobs():
            next_run = job.next_run_time
            if next_run:
                next_run_str = next_run.strftime('%Y-%m-%d %H:%M:%S')
                print(f"  • {job.name}: 下次执行 {next_run_str}")
        print()
    
    def stop(self):
        """停止调度器"""
        if not self.running:
            return
            
        print("⏹️  停止定时调度器...")
        self.running = False
        
        if self.scheduler and APSCHEDULER_AVAILABLE:
            self.scheduler.shutdown(wait=False)
        
        print("✅ 调度器已停止")
    
    def get_status(self) -> dict:
        """获取调度器状态"""
        beijing_now = timezone.now().astimezone(self.beijing_tz)
        current_date = beijing_now.date()
        
        existing_term = DailyTerm.objects.filter(
            display_date=current_date, 
            status='active'
        ).first()
        
        status = {
            'running': self.running,
            'current_time': beijing_now.strftime('%Y-%m-%d %H:%M:%S'),
            'today_term_exists': existing_term is not None,
            'today_term': existing_term.term if existing_term else None,
            'scheduler_type': 'APScheduler' if APSCHEDULER_AVAILABLE else 'Basic',
        }
        
        if self.scheduler and APSCHEDULER_AVAILABLE:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'name': job.name,
                    'next_run': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else None
                })
            status['scheduled_jobs'] = jobs
        
        return status

# 全局调度器实例
_scheduler_instance: Optional[AdvancedDailyTermScheduler] = None

def get_scheduler() -> AdvancedDailyTermScheduler:
    """获取调度器实例（单例模式）"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = AdvancedDailyTermScheduler()
    return _scheduler_instance

def start_advanced_scheduler():
    """启动高级调度器"""
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler

def stop_advanced_scheduler():
    """停止高级调度器"""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop()
        _scheduler_instance = None

if __name__ == "__main__":
    # 直接运行此文件时启动调度器
    print("🚀 直接启动高级定时调度器...")
    scheduler = start_advanced_scheduler()
    
    try:
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n⏹️  收到中断信号...")
        stop_advanced_scheduler()
        print("✅ 调度器已停止")
