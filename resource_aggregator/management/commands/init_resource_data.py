"""
初始化资源聚合器数据的管理命令
用法：python manage.py init_resource_data
"""

from django.core.management.base import BaseCommand
from resource_aggregator.models import ResourceCategory, ResourceSource
from resource_aggregator.config import DEFAULT_CATEGORIES, DEFAULT_SOURCES


class Command(BaseCommand):
    help = '初始化资源聚合器的基础数据（分类和来源）'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新创建所有数据（会删除现有数据）'
        )
    
    def handle(self, *args, **options):
        force = options['force']
        
        if force:
            self.stdout.write(
                self.style.WARNING('强制模式：将删除现有数据并重新创建')
            )
            ResourceCategory.objects.all().delete()
            ResourceSource.objects.all().delete()
        
        # 创建分类
        self.stdout.write('正在创建资源分类...')
        categories_created = 0
        
        for category_data in DEFAULT_CATEGORIES:
            category, created = ResourceCategory.objects.get_or_create(
                slug=category_data['slug'],
                defaults=category_data
            )
            
            if created:
                categories_created += 1
                self.stdout.write(f'  ✓ 创建分类: {category.name}')
            else:
                self.stdout.write(f'  - 分类已存在: {category.name}')
        
        # 创建资源来源
        self.stdout.write('\n正在创建资源来源...')
        sources_created = 0
        
        for source_data in DEFAULT_SOURCES:
            source, created = ResourceSource.objects.get_or_create(
                platform=source_data['platform'],
                defaults=source_data
            )
            
            if created:
                sources_created += 1
                self.stdout.write(f'  ✓ 创建来源: {source.name}')
            else:
                self.stdout.write(f'  - 来源已存在: {source.name}')
        
        # 显示统计信息
        self.stdout.write(
            self.style.SUCCESS(f'\n初始化完成!')
        )
        self.stdout.write(f'创建了 {categories_created} 个新分类')
        self.stdout.write(f'创建了 {sources_created} 个新来源')
        
        total_categories = ResourceCategory.objects.count()
        total_sources = ResourceSource.objects.count()
        
        self.stdout.write(f'当前共有 {total_categories} 个分类')
        self.stdout.write(f'当前共有 {total_sources} 个资源来源')
        
        # 显示下一步提示
        self.stdout.write(
            self.style.SUCCESS('\n下一步操作建议:')
        )
        self.stdout.write('1. 配置API密钥（YouTube、GitHub等）')
        self.stdout.write('2. 运行 python manage.py sync_resources 同步资源')
        self.stdout.write('3. 访问管理后台配置更多设置')
