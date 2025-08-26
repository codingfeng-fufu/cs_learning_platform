"""
每日名词系统诊断命令
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import pytz
import os

class Command(BaseCommand):
    help = '诊断每日名词系统状态'
    
    def handle(self, *args, **options):
        self.stdout.write('🔍 每日名词系统诊断报告')
        self.stdout.write('=' * 50)
        
        # 1. 检查当前状态
        self.check_current_status()
        
        # 2. 检查最近的名词
        self.check_recent_terms()
        
        # 3. 检查环境配置
        self.check_environment()
        
        # 4. 检查API配置
        self.check_api_config()
        
        # 5. 测试调度器逻辑
        self.test_scheduler_logic()
        
        # 6. 提供修复建议
        self.provide_suggestions()
    
    def check_current_status(self):
        """检查当前每日名词状态"""
        self.stdout.write('\n📊 当前状态检查:')
        
        from knowledge_app.models import DailyTerm
        
        # 获取北京时间
        beijing_tz = pytz.timezone('Asia/Shanghai')
        beijing_now = timezone.now().astimezone(beijing_tz)
        today = beijing_now.date()
        
        self.stdout.write(f'  📅 当前北京时间: {beijing_now}')
        self.stdout.write(f'  📅 今天日期: {today}')
        
        # 检查今日名词
        today_term = DailyTerm.objects.filter(display_date=today, status='active').first()
        if today_term:
            self.stdout.write(self.style.SUCCESS(f'  ✅ 今日名词已存在: {today_term.term}'))
            self.stdout.write(f'     创建时间: {today_term.created_at}')
            if today_term.api_request_time:
                self.stdout.write(f'     API请求时间: {today_term.api_request_time}')
        else:
            self.stdout.write(self.style.ERROR('  ❌ 今日名词不存在'))
    
    def check_recent_terms(self):
        """检查最近的名词"""
        self.stdout.write('\n📋 最近的名词记录:')
        
        from knowledge_app.models import DailyTerm
        
        recent_terms = DailyTerm.objects.filter(status='active').order_by('-display_date')[:7]
        
        if not recent_terms:
            self.stdout.write(self.style.ERROR('  ❌ 没有找到任何名词记录'))
            return
        
        for term in recent_terms:
            self.stdout.write(f'  {term.display_date}: {term.term} (创建: {term.created_at.strftime("%m-%d %H:%M")})')
    
    def check_environment(self):
        """检查环境配置"""
        self.stdout.write('\n🌍 环境配置检查:')
        
        run_main = os.environ.get('RUN_MAIN')
        start_scheduler = os.environ.get('START_SCHEDULER')
        
        self.stdout.write(f'  RUN_MAIN: {run_main}')
        self.stdout.write(f'  START_SCHEDULER: {start_scheduler}')
        self.stdout.write(f'  DEBUG: {settings.DEBUG}')
        
        if run_main == 'true' or start_scheduler == 'true':
            self.stdout.write(self.style.SUCCESS('  ✅ 环境变量配置正确'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  环境变量可能不正确'))
    
    def check_api_config(self):
        """检查API配置"""
        self.stdout.write('\n🔑 API配置检查:')
        
        try:
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if api_key:
                masked_key = api_key[:8] + '...' + api_key[-4:] if len(api_key) > 12 else '***'
                self.stdout.write(f'  OpenAI API Key: {masked_key}')
                self.stdout.write(self.style.SUCCESS('  ✅ API密钥已配置'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ OpenAI API密钥未配置'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ 检查API配置时出错: {e}'))
    
    def test_scheduler_logic(self):
        """测试调度器逻辑"""
        self.stdout.write('\n🧪 调度器逻辑测试:')
        
        try:
            from knowledge_app.management.commands.start_daily_term_scheduler import DailyTermScheduler
            
            scheduler = DailyTermScheduler()
            beijing_tz = pytz.timezone('Asia/Shanghai')
            today = timezone.now().astimezone(beijing_tz).date()
            
            should_generate = scheduler._should_generate_term(today)
            self.stdout.write(f'  📊 调度器判断今日是否需要生成名词: {should_generate}')
            
            if should_generate:
                self.stdout.write(self.style.SUCCESS('  ✅ 调度器逻辑正常'))
            else:
                self.stdout.write(self.style.WARNING('  ⚠️  调度器认为不需要生成名词'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ 测试调度器逻辑时出错: {e}'))
    
    def provide_suggestions(self):
        """提供修复建议"""
        self.stdout.write('\n💡 修复建议:')
        
        from knowledge_app.models import DailyTerm
        beijing_tz = pytz.timezone('Asia/Shanghai')
        today = timezone.now().astimezone(beijing_tz).date()
        
        today_term = DailyTerm.objects.filter(display_date=today, status='active').first()
        
        if not today_term:
            self.stdout.write('  🔧 立即修复建议:')
            self.stdout.write('     1. 运行: python manage.py start_scheduler --check-only')
            self.stdout.write('     2. 或强制生成: python manage.py start_scheduler --force-generate')
            self.stdout.write('     3. 或手动生成: python manage.py generate_daily_term')
        
        self.stdout.write('\n  🛠️  长期解决方案:')
        self.stdout.write('     1. 确保开发服务器启动时设置 RUN_MAIN=true')
        self.stdout.write('     2. 或设置 START_SCHEDULER=true 环境变量')
        self.stdout.write('     3. 检查API密钥配置是否正确')
        self.stdout.write('     4. 考虑使用系统cron任务作为备用')
        
        self.stdout.write('\n  📝 cron任务示例:')
        self.stdout.write('     # 每天早上8点检查')
        self.stdout.write('     0 8 * * * cd /path/to/project && python manage.py start_scheduler --check-only')
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('🔍 诊断完成')
