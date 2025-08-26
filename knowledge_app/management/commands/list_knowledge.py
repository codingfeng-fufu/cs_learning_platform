"""
列出知识点的Django管理命令

运行方式:
python manage.py list_knowledge
python manage.py list_knowledge --category=algorithm
python manage.py list_knowledge --active-only
"""

from django.core.management.base import BaseCommand
from knowledge_app.models import KnowledgePoint


class Command(BaseCommand):
    help = '列出所有知识点及其详细信息'

    def add_arguments(self, parser):
        parser.add_argument(
            '--category',
            type=str,
            choices=[choice[0] for choice in KnowledgePoint.CATEGORY_CHOICES],
            help='按分类筛选知识点',
        )
        parser.add_argument(
            '--difficulty',
            type=str,
            choices=[choice[0] for choice in KnowledgePoint.DIFFICULTY_CHOICES],
            help='按难度筛选知识点',
        )
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='只显示启用的知识点',
        )
        parser.add_argument(
            '--implemented-only',
            action='store_true',
            help='只显示已实现的知识点',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['table', 'list', 'json'],
            default='table',
            help='输出格式 (默认: table)',
        )
        parser.add_argument(
            '--order-by',
            type=str,
            choices=['order', 'title', 'category', 'difficulty', 'created_at'],
            default='order',
            help='排序字段 (默认: order)',
        )

    def handle(self, *args, **options):
        """执行命令的主要逻辑"""

        # 构建查询
        queryset = KnowledgePoint.objects.all()

        # 应用筛选条件
        if options['category']:
            queryset = queryset.filter(category=options['category'])

        if options['difficulty']:
            queryset = queryset.filter(difficulty=options['difficulty'])

        if options['active_only']:
            queryset = queryset.filter(is_active=True)

        if options['implemented_only']:
            # 获取已实现的知识点
            implemented_slugs = ['hamming-code', 'crc-check']
            queryset = queryset.filter(slug__in=implemented_slugs)

        # 应用排序
        order_field = options['order_by']
        if order_field == 'order':
            queryset = queryset.order_by('order', 'created_at')
        else:
            queryset = queryset.order_by(order_field)

        # 检查是否有数据
        if not queryset.exists():
            self.stdout.write(
                self.style.WARNING('没有找到匹配的知识点')
            )
            self.stdout.write(
                self.style.HTTP_INFO('提示: 运行 python manage.py init_knowledge 初始化数据')
            )
            return

        # 根据格式输出
        output_format = options['format']

        if output_format == 'json':
            self._output_json(queryset)
        elif output_format == 'list':
            self._output_list(queryset)
        else:  # table
            self._output_table(queryset, options)

    def _output_table(self, queryset, options):
        """以表格格式输出知识点列表"""

        # 输出筛选条件
        conditions = []
        if options['category']:
            category_name = dict(KnowledgePoint.CATEGORY_CHOICES)[options['category']]
            conditions.append(f"分类: {category_name}")
        if options['difficulty']:
            difficulty_name = dict(KnowledgePoint.DIFFICULTY_CHOICES)[options['difficulty']]
            conditions.append(f"难度: {difficulty_name}")
        if options['active_only']:
            conditions.append("只显示启用的")
        if options['implemented_only']:
            conditions.append("只显示已实现的")

        if conditions:
            self.stdout.write(f'筛选条件: {", ".join(conditions)}')
            self.stdout.write('')

        self.stdout.write(f'找到 {queryset.count()} 个知识点:')
        self.stdout.write('')

        # 表头
        header = f"{'序号':<4} {'状态':<4} {'图标':<4} {'标题':<20} {'分类':<12} {'难度':<6} {'实现':<6} {'排序':<4}"
        self.stdout.write(header)
        self.stdout.write('-' * len(header))

        # 数据行
        for index, point in enumerate(queryset, 1):
            status = '✓' if point.is_active else '✗'
            category_name = point.get_category_display()
            difficulty_name = point.get_difficulty_display()
            implemented = '✓' if point.is_implemented else '✗'

            # 截断过长的标题
            title = point.title
            if len(title) > 18:
                title = title[:15] + '...'

            row = f"{index:<4} {status:<4} {point.icon:<4} {title:<20} {category_name:<12} {difficulty_name:<6} {implemented:<6} {point.order:<4}"

            # 根据状态设置颜色
            if point.is_active:
                if point.is_implemented:
                    self.stdout.write(self.style.SUCCESS(row))
                else:
                    self.stdout.write(self.style.WARNING(row))
            else:
                self.stdout.write(self.style.HTTP_INFO(row))

        self.stdout.write('-' * len(header))

        # 统计信息
        total = queryset.count()
        active = queryset.filter(is_active=True).count()
        implemented = len([p for p in queryset if p.is_implemented])

        self.stdout.write('')
        self.stdout.write('📊 统计信息:')
        self.stdout.write(f'   总计: {total} 个知识点')
        self.stdout.write(f'   已启用: {active} 个')
        self.stdout.write(f'   已实现: {implemented} 个')
        self.stdout.write(f'   完成度: {implemented / total * 100:.1f}%' if total > 0 else '   完成度: 0%')

    def _output_list(self, queryset):
        """以列表格式输出知识点"""

        for point in queryset:
            status_icon = '✅' if point.is_active else '❌'
            impl_icon = '🚀' if point.is_implemented else '⏳'

            self.stdout.write(f'{status_icon} {impl_icon} {point.icon} {point.title}')
            self.stdout.write(f'   分类: {point.get_category_display()} | 难度: {point.get_difficulty_display()}')
            self.stdout.write(f'   描述: {point.description}')
            self.stdout.write(f'   URL: /learn/{point.slug}/')
            self.stdout.write('')

    def _output_json(self, queryset):
        """以JSON格式输出知识点"""
        import json

        data = []
        for point in queryset:
            data.append({
                'id': point.id,
                'title': point.title,
                'slug': point.slug,
                'description': point.description,
                'category': point.category,
                'category_display': point.get_category_display(),
                'difficulty': point.difficulty,
                'difficulty_display': point.get_difficulty_display(),
                'icon': point.icon,
                'is_active': point.is_active,
                'is_implemented': point.is_implemented,
                'order': point.order,
                'created_at': point.created_at.isoformat(),
                'updated_at': point.updated_at.isoformat(),
                'url': f'/learn/{point.slug}/'
            })

        self.stdout.write(json.dumps(data, ensure_ascii=False, indent=2))