"""
初始化知识图谱数据的管理命令
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from knowledge_app.knowledge_graph_models import ConceptNode, ConceptRelation


class Command(BaseCommand):
    help = '初始化知识图谱数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有数据后重新初始化',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('清除现有知识图谱数据...')
            ConceptRelation.objects.all().delete()
            ConceptNode.objects.all().delete()

        self.stdout.write('开始初始化知识图谱数据...')
        
        with transaction.atomic():
            # 创建概念节点
            concepts = self.create_concepts()
            
            # 创建概念关系
            self.create_relations(concepts)

        self.stdout.write(
            self.style.SUCCESS(f'成功初始化知识图谱数据：{len(concepts)} 个概念节点')
        )

    def create_concepts(self):
        """创建概念节点"""
        concepts_data = [
            # 数据结构
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
                'learning_time': 50,
                'keywords': ['BST', 'search', 'binary'],
            },
            {
                'name': '哈希表',
                'category': 'data_structure',
                'difficulty': 'intermediate',
                'description': '基于哈希函数的键值对存储结构',
                'importance_weight': 0.9,
                'learning_time': 55,
                'keywords': ['hash table', 'key-value', 'hash function'],
            },
            {
                'name': '堆',
                'category': 'data_structure',
                'difficulty': 'intermediate',
                'description': '完全二叉树实现的优先队列',
                'importance_weight': 0.7,
                'learning_time': 50,
                'keywords': ['heap', 'priority queue', 'complete binary tree'],
            },
            {
                'name': '图',
                'category': 'data_structure',
                'difficulty': 'advanced',
                'description': '由顶点和边组成的非线性数据结构',
                'importance_weight': 0.9,
                'learning_time': 70,
                'keywords': ['graph', 'vertex', 'edge', 'adjacency'],
            },

            # 算法
            {
                'name': '冒泡排序',
                'category': 'algorithm',
                'difficulty': 'beginner',
                'description': '简单的交换排序算法',
                'importance_weight': 0.5,
                'learning_time': 25,
                'keywords': ['bubble sort', 'swap', 'comparison'],
            },
            {
                'name': '快速排序',
                'category': 'algorithm',
                'difficulty': 'intermediate',
                'description': '基于分治思想的高效排序算法',
                'importance_weight': 0.9,
                'learning_time': 50,
                'keywords': ['quick sort', 'divide and conquer', 'pivot'],
            },
            {
                'name': '归并排序',
                'category': 'algorithm',
                'difficulty': 'intermediate',
                'description': '稳定的分治排序算法',
                'importance_weight': 0.8,
                'learning_time': 45,
                'keywords': ['merge sort', 'divide and conquer', 'stable'],
            },
            {
                'name': '二分查找',
                'category': 'algorithm',
                'difficulty': 'beginner',
                'description': '在有序数组中快速查找元素的算法',
                'importance_weight': 0.8,
                'learning_time': 30,
                'keywords': ['binary search', 'sorted', 'divide'],
            },
            {
                'name': '深度优先搜索',
                'category': 'algorithm',
                'difficulty': 'intermediate',
                'description': '图的遍历算法，优先访问深层节点',
                'importance_weight': 0.8,
                'learning_time': 40,
                'keywords': ['DFS', 'depth first', 'recursion', 'stack'],
            },
            {
                'name': '广度优先搜索',
                'category': 'algorithm',
                'difficulty': 'intermediate',
                'description': '图的遍历算法，逐层访问节点',
                'importance_weight': 0.8,
                'learning_time': 40,
                'keywords': ['BFS', 'breadth first', 'queue', 'level'],
            },
            {
                'name': '动态规划',
                'category': 'algorithm',
                'difficulty': 'advanced',
                'description': '通过子问题最优解构建原问题最优解',
                'importance_weight': 0.9,
                'learning_time': 80,
                'keywords': ['dynamic programming', 'optimal substructure', 'memoization'],
            },
            {
                'name': '贪心算法',
                'category': 'algorithm',
                'difficulty': 'intermediate',
                'description': '每步选择局部最优解的算法策略',
                'importance_weight': 0.7,
                'learning_time': 45,
                'keywords': ['greedy', 'local optimal', 'strategy'],
            },

            # 计算机网络
            {
                'name': 'TCP协议',
                'category': 'network',
                'difficulty': 'intermediate',
                'description': '可靠的传输层协议',
                'importance_weight': 0.9,
                'learning_time': 60,
                'keywords': ['TCP', 'reliable', 'connection', 'transport'],
            },
            {
                'name': 'HTTP协议',
                'category': 'network',
                'difficulty': 'beginner',
                'description': '超文本传输协议',
                'importance_weight': 0.8,
                'learning_time': 40,
                'keywords': ['HTTP', 'web', 'request', 'response'],
            },
            {
                'name': 'IP协议',
                'category': 'network',
                'difficulty': 'intermediate',
                'description': '网络层的核心协议',
                'importance_weight': 0.9,
                'learning_time': 50,
                'keywords': ['IP', 'network layer', 'routing', 'address'],
            },

            # 操作系统
            {
                'name': '进程',
                'category': 'os',
                'difficulty': 'intermediate',
                'description': '程序的执行实例',
                'importance_weight': 0.9,
                'learning_time': 50,
                'keywords': ['process', 'execution', 'program', 'instance'],
            },
            {
                'name': '线程',
                'category': 'os',
                'difficulty': 'intermediate',
                'description': '进程内的执行单元',
                'importance_weight': 0.8,
                'learning_time': 45,
                'keywords': ['thread', 'execution unit', 'concurrent'],
            },
            {
                'name': '内存管理',
                'category': 'os',
                'difficulty': 'advanced',
                'description': '操作系统的内存分配和回收机制',
                'importance_weight': 0.8,
                'learning_time': 60,
                'keywords': ['memory management', 'allocation', 'virtual memory'],
            },

            # 数据库
            {
                'name': 'SQL',
                'category': 'database',
                'difficulty': 'beginner',
                'description': '结构化查询语言',
                'importance_weight': 0.9,
                'learning_time': 50,
                'keywords': ['SQL', 'query', 'database', 'structured'],
            },
            {
                'name': '关系数据库',
                'category': 'database',
                'difficulty': 'intermediate',
                'description': '基于关系模型的数据库系统',
                'importance_weight': 0.8,
                'learning_time': 55,
                'keywords': ['relational database', 'table', 'relation', 'RDBMS'],
            },
            {
                'name': '事务',
                'category': 'database',
                'difficulty': 'intermediate',
                'description': '数据库操作的逻辑单元',
                'importance_weight': 0.7,

                'keywords': ['transaction', 'ACID', 'consistency', 'isolation'],
            },
        ]

        concepts = {}
        for concept_data in concepts_data:
            concept, created = ConceptNode.objects.get_or_create(
                name=concept_data['name'],
                defaults=concept_data
            )
            concepts[concept_data['name']] = concept
            if created:
                self.stdout.write(f'创建概念: {concept.name}')

        return concepts

    def create_relations(self, concepts):
        """创建概念关系"""
        relations_data = [
            # 数据结构关系
            ('数组', '链表', 'related', 0.7, '都是线性数据结构'),
            ('栈', '队列', 'related', 0.8, '都是线性数据结构的特殊形式'),
            ('数组', '栈', 'implements', 0.6, '数组可以实现栈'),
            ('数组', '队列', 'implements', 0.6, '数组可以实现队列'),
            ('链表', '栈', 'implements', 0.6, '链表可以实现栈'),
            ('链表', '队列', 'implements', 0.6, '链表可以实现队列'),
            ('二叉树', '二叉搜索树', 'contains', 0.9, '二叉搜索树是特殊的二叉树'),
            ('二叉树', '堆', 'implements', 0.7, '堆通常用完全二叉树实现'),
            ('哈希表', '数组', 'uses', 0.6, '哈希表底层使用数组'),

            # 算法关系
            ('数组', '冒泡排序', 'prerequisite', 0.8, '需要理解数组才能学习冒泡排序'),
            ('数组', '快速排序', 'prerequisite', 0.8, '需要理解数组才能学习快速排序'),
            ('数组', '归并排序', 'prerequisite', 0.8, '需要理解数组才能学习归并排序'),
            ('数组', '二分查找', 'prerequisite', 0.9, '二分查找需要有序数组'),
            ('快速排序', '归并排序', 'related', 0.8, '都是分治排序算法'),
            ('图', '深度优先搜索', 'prerequisite', 0.9, '需要理解图结构才能学习DFS'),
            ('图', '广度优先搜索', 'prerequisite', 0.9, '需要理解图结构才能学习BFS'),
            ('栈', '深度优先搜索', 'implements', 0.7, 'DFS可以用栈实现'),
            ('队列', '广度优先搜索', 'implements', 0.8, 'BFS需要用队列实现'),

            # 网络协议关系
            ('IP协议', 'TCP协议', 'prerequisite', 0.8, 'TCP基于IP协议'),
            ('TCP协议', 'HTTP协议', 'prerequisite', 0.7, 'HTTP通常基于TCP'),

            # 操作系统关系
            ('进程', '线程', 'contains', 0.8, '进程包含一个或多个线程'),
            ('进程', '内存管理', 'related', 0.7, '进程需要内存管理'),

            # 数据库关系
            ('关系数据库', 'SQL', 'uses', 0.9, '关系数据库使用SQL查询'),
            ('关系数据库', '事务', 'contains', 0.8, '关系数据库支持事务'),
        ]

        for source_name, target_name, relation_type, strength, description in relations_data:
            if source_name in concepts and target_name in concepts:
                relation, created = ConceptRelation.objects.get_or_create(
                    source_concept=concepts[source_name],
                    target_concept=concepts[target_name],
                    relation_type=relation_type,
                    defaults={
                        'strength': strength,
                        'description': description,
                    }
                )
                if created:
                    self.stdout.write(f'创建关系: {source_name} -> {target_name} ({relation_type})')
