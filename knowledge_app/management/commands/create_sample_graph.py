"""
创建示例知识图谱数据的管理命令
"""

from django.core.management.base import BaseCommand
from knowledge_app.knowledge_graph_models import ConceptNode, ConceptRelation, LearningPath, PathStep


class Command(BaseCommand):
    help = '创建示例知识图谱数据'

    def handle(self, *args, **options):
        self.stdout.write("🚀 开始创建示例知识图谱数据...")
        
        # 创建概念节点
        concepts = self.create_concepts()
        
        # 创建概念关系
        self.create_relations(concepts)
        
        # 创建学习路径
        self.create_learning_paths(concepts)
        
        self.stdout.write(
            self.style.SUCCESS("✅ 示例知识图谱数据创建完成！")
        )
    
    def create_concepts(self):
        """创建概念节点"""
        self.stdout.write("📚 创建概念节点...")
        
        concepts_data = [
            # 数据结构
            {
                'name': '数组',
                'name_en': 'Array',
                'description': '数组是一种线性数据结构，用于存储相同类型的元素序列。元素在内存中连续存储，可以通过索引快速访问。',
                'category': 'data_structure',
                'difficulty': 'beginner',
                'importance_weight': 0.9,
                'keywords': ['线性结构', '索引', '连续存储'],
                'examples': ['一维数组', '多维数组', '动态数组'],
            },
            {
                'name': '链表',
                'name_en': 'Linked List',
                'description': '链表是一种线性数据结构，元素通过指针连接。不需要连续的内存空间，插入和删除操作效率高。',
                'category': 'data_structure',
                'difficulty': 'beginner',
                'importance_weight': 0.8,
                'keywords': ['指针', '节点', '动态结构'],
                'examples': ['单链表', '双链表', '循环链表'],
            },
            {
                'name': '栈',
                'name_en': 'Stack',
                'description': '栈是一种后进先出(LIFO)的数据结构。只能在栈顶进行插入和删除操作，常用于函数调用、表达式求值等场景。',
                'category': 'data_structure',
                'difficulty': 'beginner',
                'importance_weight': 0.7,
                'keywords': ['LIFO', '栈顶', '压栈', '弹栈'],
                'examples': ['函数调用栈', '表达式求值', '括号匹配'],
            },
            {
                'name': '队列',
                'name_en': 'Queue',
                'description': '队列是一种先进先出(FIFO)的数据结构。在队尾插入元素，在队头删除元素，常用于任务调度、广度优先搜索等。',
                'category': 'data_structure',
                'difficulty': 'beginner',
                'importance_weight': 0.7,
                'keywords': ['FIFO', '队头', '队尾', '入队', '出队'],
                'examples': ['任务队列', '打印队列', '广度优先搜索'],
            },
            {
                'name': '二叉树',
                'name_en': 'Binary Tree',
                'description': '二叉树是一种树形数据结构，每个节点最多有两个子节点。具有递归性质，是许多高级数据结构的基础。',
                'category': 'data_structure',
                'difficulty': 'intermediate',
                'importance_weight': 0.8,
                'keywords': ['树形结构', '节点', '左子树', '右子树'],
                'examples': ['二叉搜索树', '完全二叉树', '平衡二叉树'],
            },
            {
                'name': '哈希表',
                'name_en': 'Hash Table',
                'description': '哈希表是一种基于哈希函数的数据结构，提供平均O(1)时间复杂度的查找、插入和删除操作。',
                'category': 'data_structure',
                'difficulty': 'intermediate',
                'importance_weight': 0.9,
                'keywords': ['哈希函数', '散列', '冲突处理', '负载因子'],
                'examples': ['字典', '缓存', '数据库索引'],
            },
            
            # 算法
            {
                'name': '排序算法',
                'name_en': 'Sorting Algorithm',
                'description': '排序算法用于将一组数据按照特定顺序重新排列。不同算法有不同的时间复杂度和空间复杂度特性。',
                'category': 'algorithm',
                'difficulty': 'intermediate',
                'importance_weight': 0.8,
                'keywords': ['比较排序', '非比较排序', '稳定性', '时间复杂度'],
                'examples': ['快速排序', '归并排序', '堆排序'],
            },
            {
                'name': '搜索算法',
                'name_en': 'Search Algorithm',
                'description': '搜索算法用于在数据结构中查找特定元素。根据数据的组织方式选择合适的搜索策略。',
                'category': 'algorithm',
                'difficulty': 'beginner',
                'importance_weight': 0.7,
                'keywords': ['线性搜索', '二分搜索', '查找效率'],
                'examples': ['顺序搜索', '二分搜索', '哈希搜索'],
            },
            {
                'name': '动态规划',
                'name_en': 'Dynamic Programming',
                'description': '动态规划是一种算法设计技术，通过将复杂问题分解为子问题，并存储子问题的解来避免重复计算。',
                'category': 'algorithm',
                'difficulty': 'advanced',
                'importance_weight': 0.9,
                'keywords': ['最优子结构', '重叠子问题', '状态转移'],
                'examples': ['斐波那契数列', '背包问题', '最长公共子序列'],
            },
            {
                'name': '贪心算法',
                'name_en': 'Greedy Algorithm',
                'description': '贪心算法在每一步选择中都采取当前状态下最好或最优的选择，从而希望导致结果是全局最好或最优的算法。',
                'category': 'algorithm',
                'difficulty': 'intermediate',
                'importance_weight': 0.7,
                'keywords': ['局部最优', '全局最优', '贪心选择性质'],
                'examples': ['活动选择', '霍夫曼编码', '最小生成树'],
            },
            
            # 计算机网络
            {
                'name': 'TCP协议',
                'name_en': 'TCP Protocol',
                'description': 'TCP是一种面向连接的、可靠的传输层协议。提供数据的可靠传输，包括错误检测、流量控制和拥塞控制。',
                'category': 'network',
                'difficulty': 'intermediate',
                'importance_weight': 0.9,
                'keywords': ['面向连接', '可靠传输', '流量控制', '拥塞控制'],
                'examples': ['三次握手', '四次挥手', '滑动窗口'],
            },
            {
                'name': 'HTTP协议',
                'name_en': 'HTTP Protocol',
                'description': 'HTTP是一种应用层协议，用于在Web浏览器和Web服务器之间传输超文本。是万维网数据通信的基础。',
                'category': 'network',
                'difficulty': 'beginner',
                'importance_weight': 0.8,
                'keywords': ['应用层', '无状态', '请求响应', '超文本'],
                'examples': ['GET请求', 'POST请求', 'HTTP状态码'],
            },
            
            # 操作系统
            {
                'name': '进程',
                'name_en': 'Process',
                'description': '进程是程序在执行过程中的一个实例，是系统进行资源分配和调度的基本单位。每个进程都有独立的内存空间。',
                'category': 'os',
                'difficulty': 'intermediate',
                'importance_weight': 0.8,
                'keywords': ['程序实例', '资源分配', '独立内存', '进程调度'],
                'examples': ['进程创建', '进程通信', '进程同步'],
            },
            {
                'name': '线程',
                'name_en': 'Thread',
                'description': '线程是进程中的执行单元，是CPU调度的基本单位。同一进程中的线程共享内存空间，创建和切换开销较小。',
                'category': 'os',
                'difficulty': 'intermediate',
                'importance_weight': 0.7,
                'keywords': ['执行单元', 'CPU调度', '共享内存', '轻量级'],
                'examples': ['多线程编程', '线程同步', '线程池'],
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
                self.stdout.write(f"  ✅ 创建概念: {concept.name}")
            else:
                self.stdout.write(f"  ⚠️  概念已存在: {concept.name}")
        
        return concepts
    
    def create_relations(self, concepts):
        """创建概念关系"""
        self.stdout.write("🔗 创建概念关系...")
        
        relations_data = [
            # 数据结构之间的关系
            ('数组', '链表', 'related', 0.7, '都是线性数据结构'),
            ('栈', '队列', 'related', 0.8, '都是受限的线性结构'),
            ('数组', '栈', 'implements', 0.6, '数组可以实现栈'),
            ('数组', '队列', 'implements', 0.6, '数组可以实现队列'),
            ('链表', '栈', 'implements', 0.7, '链表可以实现栈'),
            ('链表', '队列', 'implements', 0.7, '链表可以实现队列'),
            ('二叉树', '数组', 'related', 0.5, '二叉树可以用数组存储'),
            ('哈希表', '数组', 'uses', 0.8, '哈希表底层使用数组'),
            
            # 算法之间的关系
            ('排序算法', '搜索算法', 'related', 0.6, '排序后可以提高搜索效率'),
            ('动态规划', '贪心算法', 'related', 0.7, '都是算法设计策略'),
            
            # 算法与数据结构的关系
            ('排序算法', '数组', 'uses', 0.9, '排序算法通常操作数组'),
            ('搜索算法', '数组', 'uses', 0.8, '搜索算法可以在数组中查找'),
            ('搜索算法', '二叉树', 'uses', 0.8, '二叉搜索树支持高效搜索'),
            ('哈希表', '搜索算法', 'implements', 0.9, '哈希表实现了快速搜索'),
            
            # 网络协议关系
            ('HTTP协议', 'TCP协议', 'uses', 0.9, 'HTTP基于TCP协议'),
            
            # 操作系统概念关系
            ('进程', '线程', 'contains', 0.9, '进程包含一个或多个线程'),
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
                    self.stdout.write(f"  ✅ 创建关系: {source_name} --{relation_type}--> {target_name}")
                else:
                    self.stdout.write(f"  ⚠️  关系已存在: {source_name} --{relation_type}--> {target_name}")
    
    def create_learning_paths(self, concepts):
        """创建学习路径"""
        self.stdout.write("🛤️  创建学习路径...")
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # 获取或创建一个系统用户
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@example.com',
                'is_staff': True,
            }
        )
        
        paths_data = [
            {
                'name': '数据结构基础',
                'description': '从基础的线性数据结构开始，逐步学习更复杂的数据结构',
                'difficulty_level': 'beginner',
                'estimated_hours': 20,
                'concepts': ['数组', '链表', '栈', '队列', '二叉树'],
            },
            {
                'name': '算法设计入门',
                'description': '学习基本的算法设计思想和常用算法',
                'difficulty_level': 'intermediate',
                'estimated_hours': 30,
                'concepts': ['搜索算法', '排序算法', '贪心算法', '动态规划'],
            },
            {
                'name': '网络协议基础',
                'description': '了解计算机网络中的基本协议',
                'difficulty_level': 'beginner',
                'estimated_hours': 15,
                'concepts': ['HTTP协议', 'TCP协议'],
            },
            {
                'name': '操作系统核心概念',
                'description': '掌握操作系统的核心概念',
                'difficulty_level': 'intermediate',
                'estimated_hours': 25,
                'concepts': ['进程', '线程'],
            },
        ]
        
        for path_data in paths_data:
            path, created = LearningPath.objects.get_or_create(
                name=path_data['name'],
                defaults={
                    'description': path_data['description'],
                    'difficulty_level': path_data['difficulty_level'],
                    'estimated_hours': path_data['estimated_hours'],
                    'created_by': system_user,
                }
            )
            
            if created:
                self.stdout.write(f"  ✅ 创建学习路径: {path.name}")
                
                # 添加路径步骤
                for order, concept_name in enumerate(path_data['concepts'], 1):
                    if concept_name in concepts:
                        PathStep.objects.get_or_create(
                            learning_path=path,
                            concept=concepts[concept_name],
                            defaults={
                                'order': order,
                                'estimated_time': 60 * path_data['estimated_hours'] // len(path_data['concepts']),
                                'notes': f'学习{concept_name}的基本概念和应用',
                            }
                        )
            else:
                self.stdout.write(f"  ⚠️  学习路径已存在: {path.name}")
        
        self.stdout.write(f"📊 数据统计:")
        self.stdout.write(f"  - 概念节点: {ConceptNode.objects.count()} 个")
        self.stdout.write(f"  - 概念关系: {ConceptRelation.objects.count()} 个")
        self.stdout.write(f"  - 学习路径: {LearningPath.objects.count()} 个")
