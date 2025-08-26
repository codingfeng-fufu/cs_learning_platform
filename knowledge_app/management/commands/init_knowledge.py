"""
初始化知识点数据的Django管理命令

运行方式:
python manage.py init_knowledge
python manage.py init_knowledge --clear  # 清空现有数据
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from knowledge_app.models import KnowledgePoint


class Command(BaseCommand):
    help = '初始化知识点数据到数据库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清空现有数据再初始化',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示将要创建的数据，不实际写入数据库',
        )

    def handle(self, *args, **options):
        """执行命令的主要逻辑"""

        if options['clear']:
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING('[DRY RUN] 将清空所有现有知识点数据')
                )
            else:
                self.stdout.write('清空现有知识点数据...')
                deleted_count = KnowledgePoint.objects.count()
                KnowledgePoint.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f'已删除 {deleted_count} 个现有知识点')
                )

        # 默认知识点数据
        knowledge_points_data = self.get_default_knowledge_points()

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] 将创建以下 {len(knowledge_points_data)} 个知识点:')
            )
            for point_data in knowledge_points_data:
                self.stdout.write(f"  - {point_data['icon']} {point_data['title']}")
            return

        # 使用数据库事务确保数据一致性
        try:
            with transaction.atomic():
                created_count = 0
                updated_count = 0

                for point_data in knowledge_points_data:
                    obj, created = KnowledgePoint.objects.get_or_create(
                        slug=point_data['slug'],
                        defaults=point_data
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ 创建知识点: {obj.icon} {obj.title}')
                        )
                    else:
                        # 更新现有记录
                        updated_fields = []
                        for field, value in point_data.items():
                            if field != 'slug' and getattr(obj, field) != value:
                                setattr(obj, field, value)
                                updated_fields.append(field)

                        if updated_fields:
                            obj.save()
                            updated_count += 1
                            self.stdout.write(
                                self.style.WARNING(
                                    f'⚠ 更新知识点: {obj.icon} {obj.title} '
                                    f'(更新字段: {", ".join(updated_fields)})'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.HTTP_INFO(f'- 跳过知识点: {obj.icon} {obj.title} (无变化)')
                            )

                # 显示统计信息
                self.stdout.write('')
                self.stdout.write(
                    self.style.SUCCESS(
                        f'🎉 初始化完成! '
                        f'创建 {created_count} 个新知识点，'
                        f'更新 {updated_count} 个现有知识点。'
                    )
                )

                # 显示数据库统计
                total = KnowledgePoint.objects.count()
                active = KnowledgePoint.objects.filter(is_active=True).count()
                categories = KnowledgePoint.objects.values_list('category', flat=True).distinct().count()

                self.stdout.write('')
                self.stdout.write('📊 数据库统计:')
                self.stdout.write(f'   总知识点数: {total}')
                self.stdout.write(f'   已启用: {active}')
                self.stdout.write(f'   分类数: {categories}')

                # 按分类显示统计
                self.stdout.write('')
                self.stdout.write('📚 分类统计:')
                for category, name in KnowledgePoint.CATEGORY_CHOICES:
                    count = KnowledgePoint.objects.filter(category=category, is_active=True).count()
                    if count > 0:
                        self.stdout.write(f'   {name}: {count} 个')

        except Exception as e:
            raise CommandError(f'初始化失败: {str(e)}')

    def get_default_knowledge_points(self):
        """获取默认的知识点数据"""
        return [
            {
                'title': '海明码编码解码',
                'slug': 'hamming-code',
                'description': '学习海明码的编码、解码原理，掌握错误检测与纠正技术。广泛应用于计算机内存和数据传输中，是理解纠错码的经典入门案例。',
                'category': 'network',
                'difficulty': 'intermediate',
                'icon': '🧮',
                'order': 1
            },
            {
                'title': 'CRC循环冗余检验',
                'slug': 'crc-check',
                'description': '理解CRC算法原理，学习如何进行数据完整性校验。常用于网络传输和存储系统，掌握多项式除法的实际应用。',
                'category': 'network',
                'difficulty': 'intermediate',
                'icon': '🔍',
                'order': 2
            },
            {
                'title': 'RSA加密算法',
                'slug': 'rsa-crypto',
                'description': '掌握RSA非对称加密算法，理解公钥密码学的基本原理和应用场景。学习大数运算、模幂运算等数学基础。',
                'category': 'security',
                'difficulty': 'advanced',
                'icon': '🔐',
                'order': 3
            },
            {
                'title': '排序算法可视化',
                'slug': 'sorting-algorithms',
                'description': '通过可视化方式学习各种排序算法，比较时间复杂度和空间复杂度。包括冒泡、选择、插入、快排等经典算法。',
                'category': 'algorithm',
                'difficulty': 'beginner',
                'icon': '📊',
                'order': 4
            },
            {
                'title': '哈夫曼编码',
                'slug': 'huffman-coding',
                'description': '学习哈夫曼编码算法，理解数据压缩的基本原理和贪心算法的应用。掌握二叉树构建和编码表生成过程。',
                'category': 'algorithm',
                'difficulty': 'intermediate',
                'icon': '🗜️',
                'order': 5
            },
            {
                'title': 'B+树索引原理',
                'slug': 'btree-index',
                'description': '深入理解B+树数据结构，掌握数据库索引的工作原理和优化策略。学习磁盘I/O优化和范围查询实现。',
                'category': 'database',
                'difficulty': 'advanced',
                'icon': '🌳',
                'order': 6
            },
            {
                'title': '最短路径算法',
                'slug': 'shortest-path',
                'description': '学习Dijkstra和Floyd算法，理解图论中最短路径问题的解决方案。掌握动态规划和贪心策略的应用。',
                'category': 'algorithm',
                'difficulty': 'intermediate',
                'icon': '🗺️',
                'order': 7
            },
            {
                'title': '进程调度算法',
                'slug': 'process-scheduling',
                'description': '了解操作系统中的进程调度策略，包括FCFS、SJF、时间片轮转等算法。理解公平性和效率的权衡。',
                'category': 'system',
                'difficulty': 'intermediate',
                'icon': '⚙️',
                'order': 8
            },
            {
                'title': '一致性哈希',
                'slug': 'consistent-hashing',
                'description': '学习分布式系统中的一致性哈希算法，理解负载均衡和数据分片的原理。掌握虚拟节点和哈希环概念。',
                'category': 'system',
                'difficulty': 'advanced',
                'icon': '🔄',
                'order': 9
            },
            {
                'title': '决策树算法',
                'slug': 'decision-tree',
                'description': '掌握机器学习中的决策树算法，理解信息增益和剪枝的概念。学习特征选择和过拟合防止策略。',
                'category': 'ai',
                'difficulty': 'intermediate',
                'icon': '🤖',
                'order': 10
            },
            {
                'title': '线性回归分析',
                'slug': 'linear-regression',
                'description': '学习机器学习的基础算法——线性回归，理解最小二乘法和梯度下降。掌握特征工程和模型评估方法。',
                'category': 'ai',
                'difficulty': 'beginner',
                'icon': '📈',
                'order': 11
            },
            {
                'title': '内存管理策略',
                'slug': 'memory-management',
                'description': '深入理解操作系统的内存管理机制，包括分页、分段、虚拟内存等概念。学习内存分配和回收算法。',
                'category': 'system',
                'difficulty': 'advanced',
                'icon': '💾',
                'order': 12
            },
            {
                'title': '单链表',
                'slug': 'single-linklist',
                'description': '理解单链表的存储结构，可视化节点的插入与删除',
                'category': 'algorithm',
                'difficulty': 'beginner',
                'icon':'💾',
                'order': 13
            },
            {
                'title': "图的深度优先搜索",
                'slug': 'graph_dfs',
                'description': '深入理解图的dfs过程',
                'category': 'algorithm',
                'difficulty': 'beginner',
                'icon':'📈',
                'order': 14
            }

        ]