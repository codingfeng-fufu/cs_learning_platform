"""
初始化工具和资源数据的管理命令
用法：python manage.py init_tools_data
"""

from django.core.management.base import BaseCommand
from resource_aggregator.models import ResourceCategory, ResourceSource, LearningResource
from resource_aggregator.config import DEFAULT_CATEGORIES, DEFAULT_RESOURCES
from resource_aggregator.extended_resources import EXTENDED_RESOURCES
from resource_aggregator.additional_tools import ADDITIONAL_TOOLS


class Command(BaseCommand):
    help = '初始化工具箱的工具和资源数据'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新创建所有数据（会删除现有数据）'
        )
        
        parser.add_argument(
            '--categories-only',
            action='store_true',
            help='只创建分类，不创建资源'
        )
        
        parser.add_argument(
            '--resources-only',
            action='store_true',
            help='只创建资源，不创建分类'
        )

        parser.add_argument(
            '--extended',
            action='store_true',
            help='同时加载扩展资源（50+个额外资源）'
        )

        parser.add_argument(
            '--additional',
            action='store_true',
            help='加载额外工具（20+个新工具）'
        )

        parser.add_argument(
            '--all',
            action='store_true',
            help='加载所有资源（基础+扩展+额外）'
        )
    
    def handle(self, *args, **options):
        force = options['force']
        categories_only = options['categories_only']
        resources_only = options['resources_only']
        extended = options['extended']
        additional = options['additional']
        load_all = options['all']
        
        if force:
            self.stdout.write(
                self.style.WARNING('强制模式：将删除现有数据并重新创建')
            )
            if not resources_only:
                ResourceCategory.objects.all().delete()
            if not categories_only:
                LearningResource.objects.all().delete()
        
        # 创建分类
        if not resources_only:
            self.stdout.write('正在创建工具分类...')
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
        
        # 创建资源
        if not categories_only:
            self.stdout.write('\n正在创建工具和资源...')
            resources_created = 0
            
            # 获取或创建默认资源来源
            default_source, _ = ResourceSource.objects.get_or_create(
                platform='custom',
                defaults={
                    'name': '精选工具',
                    'base_url': 'https://example.com',
                    'is_active': True,
                    'priority': 1,
                    'rate_limit': 0
                }
            )
            
            # 合并默认资源和扩展资源
            all_resources = DEFAULT_RESOURCES.copy()
            if extended or load_all:
                all_resources.extend(EXTENDED_RESOURCES)
                self.stdout.write(f'  加载扩展资源')
            if additional or load_all:
                all_resources.extend(ADDITIONAL_TOOLS)
                self.stdout.write(f'  加载额外工具')

            self.stdout.write(f'  总共 {len(all_resources)} 个资源')

            for resource_data in all_resources:
                # 获取分类
                try:
                    category = ResourceCategory.objects.get(slug=resource_data['category_slug'])
                except ResourceCategory.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'分类不存在: {resource_data["category_slug"]}')
                    )
                    continue
                
                # 检查是否已存在
                existing = LearningResource.objects.filter(
                    title=resource_data['title']
                ).first()
                
                if not existing:
                    # 创建资源
                    resource = LearningResource.objects.create(
                        title=resource_data['title'],
                        description=resource_data['description'],
                        short_description=resource_data.get('short_description', ''),
                        url=resource_data['url'],
                        category=category,
                        resource_type=resource_data['resource_type'],
                        source=default_source,
                        is_free=resource_data.get('is_free', True),
                        price_info=resource_data.get('price_info', ''),
                        features=resource_data.get('features', []),
                        pros_cons=resource_data.get('pros_cons', {}),
                        platform_support=resource_data.get('platform_support', []),
                        usage_tips=resource_data.get('usage_tips', ''),
                        tags=resource_data.get('tags', []),
                        is_active=True
                    )
                    
                    resources_created += 1
                    self.stdout.write(f'  ✓ 创建工具: {resource.title}')
                else:
                    self.stdout.write(f'  - 工具已存在: {existing.title}')
        
        # 显示统计信息
        self.stdout.write(
            self.style.SUCCESS(f'\n初始化完成!')
        )
        
        if not resources_only:
            categories_created = categories_created if 'categories_created' in locals() else 0
            self.stdout.write(f'创建了 {categories_created} 个新分类')
        
        if not categories_only:
            resources_created = resources_created if 'resources_created' in locals() else 0
            self.stdout.write(f'创建了 {resources_created} 个新工具/资源')
        
        total_categories = ResourceCategory.objects.count()
        total_resources = LearningResource.objects.count()
        
        self.stdout.write(f'当前共有 {total_categories} 个分类')
        self.stdout.write(f'当前共有 {total_resources} 个工具/资源')
        
        # 显示下一步提示
        self.stdout.write(
            self.style.SUCCESS('\n🎉 工具箱已准备就绪!')
        )
        self.stdout.write('访问 http://localhost:8000/resources/ 查看工具箱')
        self.stdout.write('访问管理后台可以添加更多工具和资源')
