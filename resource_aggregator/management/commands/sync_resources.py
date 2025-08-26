"""
同步学习资源的管理命令
用法：python manage.py sync_resources --query "python" --category "programming" --limit 50
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from resource_aggregator.services import sync_search_resources, aggregator_service
from resource_aggregator.models import ResourceCategory
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '从各个平台同步学习资源'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--query',
            type=str,
            default='programming tutorial',
            help='搜索关键词 (默认: programming tutorial)'
        )
        
        parser.add_argument(
            '--category',
            type=str,
            help='资源分类slug'
        )
        
        parser.add_argument(
            '--platforms',
            nargs='+',
            default=['youtube', 'github', 'bilibili'],
            help='要搜索的平台列表'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='每个平台的资源数量限制 (默认: 20)'
        )
        
        parser.add_argument(
            '--save-to-db',
            action='store_true',
            help='是否保存到数据库'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示结果，不保存到数据库'
        )
    
    def handle(self, *args, **options):
        query = options['query']
        category_slug = options['category']
        platforms = options['platforms']
        limit = options['limit']
        save_to_db = options['save_to_db']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(f'开始同步资源...')
        )
        self.stdout.write(f'搜索关键词: {query}')
        self.stdout.write(f'目标平台: {", ".join(platforms)}')
        self.stdout.write(f'资源限制: {limit}')
        
        if category_slug:
            try:
                category = ResourceCategory.objects.get(slug=category_slug)
                self.stdout.write(f'目标分类: {category.name}')
            except ResourceCategory.DoesNotExist:
                raise CommandError(f'分类不存在: {category_slug}')
        
        try:
            # 搜索资源
            self.stdout.write('正在搜索资源...')
            results = sync_search_resources(query, category_slug, platforms, limit)
            
            if not results:
                self.stdout.write(
                    self.style.WARNING('没有找到任何资源')
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS(f'找到 {len(results)} 个资源')
            )
            
            # 显示结果摘要
            self.display_results_summary(results)
            
            # 保存到数据库
            if save_to_db and not dry_run:
                self.stdout.write('正在保存到数据库...')
                aggregator_service.save_resources_to_db(results, category_slug)
                self.stdout.write(
                    self.style.SUCCESS('资源已保存到数据库')
                )
            elif dry_run:
                self.stdout.write(
                    self.style.WARNING('这是试运行，资源未保存到数据库')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('使用 --save-to-db 参数来保存资源到数据库')
                )
                
        except Exception as e:
            logger.error(f'同步资源失败: {e}')
            raise CommandError(f'同步失败: {e}')
    
    def display_results_summary(self, results):
        """显示结果摘要"""
        self.stdout.write('\n=== 资源摘要 ===')
        
        # 按类型统计
        type_counts = {}
        platform_counts = {}
        
        for resource in results:
            resource_type = resource.get('resource_type', 'unknown')
            type_counts[resource_type] = type_counts.get(resource_type, 0) + 1
            
            # 从URL推断平台
            url = resource.get('url', '')
            if 'youtube.com' in url:
                platform = 'YouTube'
            elif 'github.com' in url:
                platform = 'GitHub'
            elif 'bilibili.com' in url:
                platform = 'Bilibili'
            else:
                platform = 'Other'
            
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        self.stdout.write('按类型统计:')
        for resource_type, count in type_counts.items():
            self.stdout.write(f'  {resource_type}: {count}')
        
        self.stdout.write('\n按平台统计:')
        for platform, count in platform_counts.items():
            self.stdout.write(f'  {platform}: {count}')
        
        # 显示前5个资源
        self.stdout.write('\n=== 前5个资源 ===')
        for i, resource in enumerate(results[:5], 1):
            title = resource.get('title', 'No title')[:50]
            author = resource.get('author', 'Unknown')
            resource_type = resource.get('resource_type', 'unknown')
            self.stdout.write(f'{i}. [{resource_type}] {title} - {author}')
        
        if len(results) > 5:
            self.stdout.write(f'... 还有 {len(results) - 5} 个资源')
        
        self.stdout.write('')
