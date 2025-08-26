"""
初始化简化的知识图谱数据
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from knowledge_app.knowledge_graph_models import ConceptNode, ConceptRelation


class Command(BaseCommand):
    help = '初始化简化的知识图谱数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有数据',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('清除现有知识图谱数据...')
            ConceptRelation.objects.all().delete()
            ConceptNode.objects.all().delete()

        with transaction.atomic():
            self.create_concepts()
            self.create_relations()

        self.stdout.write(
            self.style.SUCCESS('知识图谱初始化完成！')
        )

    def create_concepts(self):
        """创建概念节点"""
        concepts_data = [
            # 数据结构基础
            {
                'name': '数组',
                'category': 'data_structure',
                'difficulty': 'beginner',
                'description': '最基础的线性数据结构，元素在内存中连续存储',
                'importance_weight': 0.9,
                'keywords': ['array', 'index', 'linear'],
            },
            {
                'name': '链表',
                'category': 'data_structure',
                'difficulty': 'beginner',
                'description': '动态数据结构，通过指针连接节点',
                'importance_weight': 0.8,
                'keywords': ['linked list', 'pointer', 'node'],
            },
            {
                'name': '栈',
                'category': 'data_structure',
                'difficulty': 'beginner',
                'description': '后进先出(LIFO)的线性数据结构',
                'importance_weight': 0.8,
                'keywords': ['stack', 'LIFO', 'push', 'pop'],
            },
            {
                'name': '队列',
                'category': 'data_structure',
                'difficulty': 'beginner',
                'description': '先进先出(FIFO)的线性数据结构',
                'importance_weight': 0.8,
                'keywords': ['queue', 'FIFO', 'enqueue', 'dequeue'],
            },
            {
                'name': '二叉树',
                'category': 'data_structure',
                'difficulty': 'intermediate',
                'description': '每个节点最多有两个子节点的树结构',
                'importance_weight': 0.9,
                'keywords': ['binary tree', 'node', 'left', 'right'],
            },
            {
                'name': '二叉搜索树',
                'category': 'data_structure',
                'difficulty': 'intermediate',
                'description': '具有搜索性质的二叉树',
                'importance_weight': 0.8,
                'keywords': ['BST', 'search', 'binary'],
            },
            {
                'name': '哈希表',
                'category': 'data_structure',
                'difficulty': 'intermediate',
                'description': '基于哈希函数的键值对存储结构',
                'importance_weight': 0.9,
                'keywords': ['hash table', 'key-value', 'hash function'],
            },
            
            # 算法基础
            {
                'name': '冒泡排序',
                'category': 'algorithm',
                'difficulty': 'beginner',
                'description': '简单的交换排序算法',
                'importance_weight': 0.5,
                'keywords': ['bubble sort', 'swap', 'comparison'],
            },
            {
                'name': '快速排序',
                'category': 'algorithm',
                'difficulty': 'intermediate',
                'description': '基于分治思想的高效排序算法',
                'importance_weight': 0.9,
                'keywords': ['quick sort', 'divide and conquer', 'pivot'],
            },
            {
                'name': '二分查找',
                'category': 'algorithm',
                'difficulty': 'beginner',
                'description': '在有序数组中快速查找元素的算法',
                'importance_weight': 0.8,
                'keywords': ['binary search', 'sorted', 'divide'],
            },
            {
                'name': '深度优先搜索',
                'category': 'algorithm',
                'difficulty': 'intermediate',
                'description': '图的遍历算法，优先访问深层节点',
                'importance_weight': 0.8,
                'keywords': ['DFS', 'depth first', 'recursion', 'stack'],
            },
            {
                'name': '广度优先搜索',
                'category': 'algorithm',
                'difficulty': 'intermediate',
                'description': '图的遍历算法，逐层访问节点',
                'importance_weight': 0.8,
                'keywords': ['BFS', 'breadth first', 'queue', 'level'],
            },
        ]

        created_count = 0
        for concept_data in concepts_data:
            concept, created = ConceptNode.objects.get_or_create(
                name=concept_data['name'],
                defaults=concept_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'创建概念: {concept.name}')

        self.stdout.write(f'总共创建了 {created_count} 个概念节点')

    def create_relations(self):
        """创建前置关系"""
        relations_data = [
            # 数据结构前置关系
            ('数组', '链表', 'prerequisite'),
            ('数组', '栈', 'prerequisite'),
            ('数组', '队列', 'prerequisite'),
            ('链表', '二叉树', 'prerequisite'),
            ('二叉树', '二叉搜索树', 'prerequisite'),
            ('数组', '哈希表', 'prerequisite'),

            # 算法前置关系
            ('数组', '冒泡排序', 'prerequisite'),
            ('数组', '快速排序', 'prerequisite'),
            ('数组', '二分查找', 'prerequisite'),
            ('栈', '深度优先搜索', 'prerequisite'),
            ('队列', '广度优先搜索', 'prerequisite'),

            # 相关关系
            ('栈', '深度优先搜索', 'related'),
            ('队列', '广度优先搜索', 'related'),
            ('快速排序', '冒泡排序', 'related'),
        ]

        created_count = 0
        for source_name, target_name, relation_type in relations_data:
            try:
                source = ConceptNode.objects.get(name=source_name)
                target = ConceptNode.objects.get(name=target_name)
                
                relation, created = ConceptRelation.objects.get_or_create(
                    source_concept=source,
                    target_concept=target,
                    relation_type=relation_type,
                    defaults={
                        'strength': 0.8 if relation_type == 'prerequisite' else 0.6,
                        'description': f'{source_name}是{target_name}的{relation_type}'
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'创建关系: {source_name} -> {target_name} ({relation_type})')
            except ConceptNode.DoesNotExist as e:
                self.stdout.write(
                    self.style.WARNING(f'概念不存在: {e}')
                )

        self.stdout.write(f'总共创建了 {created_count} 个关系')
