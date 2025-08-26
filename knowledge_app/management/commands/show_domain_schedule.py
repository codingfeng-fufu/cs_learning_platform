"""
显示计算机领域调度情况
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, date, timedelta
from knowledge_app.services.domain_scheduler import domain_scheduler


class Command(BaseCommand):
    help = '显示计算机领域调度情况'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='显示多少天的调度情况（默认30天）'
        )
        
        parser.add_argument(
            '--start-date',
            type=str,
            help='开始日期 (格式: YYYY-MM-DD)，默认为今天'
        )

    def handle(self, *args, **options):
        days = options['days']
        start_date_str = options.get('start_date')
        
        # 解析开始日期
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('日期格式错误，请使用 YYYY-MM-DD 格式')
                )
                return
        else:
            start_date = timezone.now().date()
        
        self.stdout.write("🗓️  计算机领域调度表")
        self.stdout.write("=" * 60)
        
        # 显示当前领域信息
        current_info = domain_scheduler.get_domain_info(start_date)
        current_domain = current_info['domain']
        
        self.stdout.write(f"📅 查询日期: {start_date}")
        self.stdout.write(f"🎯 当前领域: {current_domain['name']} ({current_domain['english']})")
        self.stdout.write(f"📖 领域描述: {current_domain['description']}")
        self.stdout.write(f"🔄 周期编号: 第 {current_info['cycle_number']} 周期")
        self.stdout.write(f"📊 周期进度: {current_info['days_in_cycle']}/{domain_scheduler.CYCLE_DAYS} 天")
        self.stdout.write(f"⏰ 周期时间: {current_info['cycle_start']} 至 {current_info['cycle_end']}")
        self.stdout.write(f"⏳ 剩余天数: {current_info['days_remaining']} 天")
        
        # 显示下一次变更
        next_change_date, next_domain = domain_scheduler.get_next_domain_change(start_date)
        self.stdout.write(f"🔜 下次变更: {next_change_date} → {next_domain['name']}")
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"📋 未来 {days} 天的领域调度:")
        self.stdout.write("=" * 60)
        
        # 获取调度表
        schedule = domain_scheduler.get_domain_schedule(start_date, days)
        
        current_domain_name = None
        for schedule_date, domain in schedule:
            # 检查是否是新的领域周期
            if domain['name'] != current_domain_name:
                if current_domain_name is not None:
                    self.stdout.write("")  # 空行分隔
                
                self.stdout.write(
                    self.style.SUCCESS(f"🎯 {domain['name']} ({domain['english']})")
                )
                self.stdout.write(f"   📖 {domain['description']}")
                self.stdout.write(f"   🔑 关键词: {', '.join(domain['keywords'][:5])}")
                self.stdout.write("")
                current_domain_name = domain['name']
            
            # 显示日期（高亮今天）
            if schedule_date == timezone.now().date():
                date_str = self.style.WARNING(f"   📅 {schedule_date} (今天)")
            else:
                date_str = f"   📅 {schedule_date}"
            
            self.stdout.write(date_str)
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📊 领域统计信息:")
        self.stdout.write("=" * 60)
        
        # 统计每个领域出现的次数
        domain_counts = {}
        for _, domain in schedule:
            domain_name = domain['name']
            domain_counts[domain_name] = domain_counts.get(domain_name, 0) + 1
        
        for domain_name, count in domain_counts.items():
            percentage = (count / days) * 100
            self.stdout.write(f"   {domain_name}: {count} 天 ({percentage:.1f}%)")
        
        self.stdout.write(f"\n📈 总计: {len(domain_scheduler.domains)} 个领域，每 {domain_scheduler.CYCLE_DAYS} 天轮换一次")
        self.stdout.write(f"🔄 完整轮换周期: {len(domain_scheduler.domains) * domain_scheduler.CYCLE_DAYS} 天")
        
        # 显示所有可用领域
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("🎯 所有可用领域:")
        self.stdout.write("=" * 60)
        
        for i, domain in enumerate(domain_scheduler.domains, 1):
            self.stdout.write(f"{i:2d}. {domain['name']} ({domain['english']})")
            self.stdout.write(f"     📖 {domain['description']}")
            self.stdout.write(f"     💡 示例: {', '.join(domain['examples'][:3])}")
            self.stdout.write("")
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ 领域调度信息显示完成！")
        )
