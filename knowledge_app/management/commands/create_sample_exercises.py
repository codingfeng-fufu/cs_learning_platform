from django.core.management.base import BaseCommand
from knowledge_app.exercise_models import ExerciseCategory, ExerciseDifficulty, Exercise, ExerciseSet, ExerciseSetItem

class Command(BaseCommand):
    help = '创建示例练习题数据'

    def handle(self, *args, **options):
        self.stdout.write('开始创建示例练习题数据...')
        
        # 创建难度等级
        difficulties = [
            {'name': '初级', 'level': 1, 'color': '#28a745', 'description': '适合初学者，基础概念题目'},
            {'name': '中级', 'level': 2, 'color': '#ffc107', 'description': '需要一定基础，综合应用题目'},
            {'name': '高级', 'level': 3, 'color': '#dc3545', 'description': '需要深入理解，复杂分析题目'},
        ]
        
        for diff_data in difficulties:
            difficulty, created = ExerciseDifficulty.objects.get_or_create(
                level=diff_data['level'],
                defaults=diff_data
            )
            if created:
                self.stdout.write(f'创建难度: {difficulty.name}')
        
        # 创建分类
        categories = [
            {
                'name': '数据结构',
                'slug': 'data-structures',
                'description': '数组、链表、栈、队列、树、图等数据结构相关题目',
                'icon': '🌳',
                'color': '#4ecdc4',
                'order': 1
            },
            {
                'name': '算法设计',
                'slug': 'algorithms',
                'description': '排序、查找、动态规划、贪心算法等算法设计题目',
                'icon': '⚡',
                'color': '#ff6b6b',
                'order': 2
            },
            {
                'name': '计算机网络',
                'slug': 'computer-networks',
                'description': 'TCP/IP、HTTP、网络协议等计算机网络相关题目',
                'icon': '🌐',
                'color': '#4dabf7',
                'order': 3
            },
            {
                'name': '操作系统',
                'slug': 'operating-systems',
                'description': '进程、线程、内存管理、文件系统等操作系统题目',
                'icon': '💻',
                'color': '#69db7c',
                'order': 4
            },
            {
                'name': '数据库系统',
                'slug': 'database-systems',
                'description': 'SQL、关系型数据库、事务处理等数据库相关题目',
                'icon': '🗄️',
                'color': '#ffd43b',
                'order': 5
            }
        ]
        
        for cat_data in categories:
            category, created = ExerciseCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'创建分类: {category.name}')
        
        # 创建示例练习题
        self.create_data_structure_exercises()
        self.create_algorithm_exercises()
        self.create_network_exercises()
        self.create_os_exercises()
        self.create_database_exercises()
        
        # 创建示例题集
        self.create_sample_exercise_sets()
        
        self.stdout.write(self.style.SUCCESS('示例练习题数据创建完成！'))
    
    def create_data_structure_exercises(self):
        """创建数据结构练习题"""
        category = ExerciseCategory.objects.get(slug='data-structures')
        easy = ExerciseDifficulty.objects.get(level=1)
        medium = ExerciseDifficulty.objects.get(level=2)
        hard = ExerciseDifficulty.objects.get(level=3)
        
        exercises = [
            {
                'title': '数组的基本概念',
                'slug': 'array-basic-concept',
                'category': category,
                'difficulty': easy,
                'question_type': 'single_choice',
                'question_text': '数组是一种什么样的数据结构？',
                'options': {
                    'A': '线性数据结构，元素在内存中连续存储',
                    'B': '非线性数据结构，元素随机存储',
                    'C': '树形数据结构，有层次关系',
                    'D': '图形数据结构，元素之间有复杂关系'
                },
                'correct_answer': 'A',
                'explanation': '数组是一种线性数据结构，其特点是：\n1. 元素类型相同\n2. 元素在内存中连续存储\n3. 可以通过下标直接访问元素\n4. 支持随机访问，时间复杂度为O(1)',
                'hints': ['考虑数组元素在内存中的存储方式', '想想数组访问元素的特点'],
                'tags': '数组,基础概念,线性结构',
                'time_limit': 60,
                'is_featured': True
            },
            {
                'title': '链表插入操作',
                'slug': 'linked-list-insertion',
                'category': category,
                'difficulty': medium,
                'question_type': 'single_choice',
                'question_text': '在单链表的头部插入一个新节点的时间复杂度是多少？',
                'options': {
                    'A': 'O(1)',
                    'B': 'O(n)',
                    'C': 'O(log n)',
                    'D': 'O(n²)'
                },
                'correct_answer': 'A',
                'explanation': '在单链表头部插入节点的步骤：\n1. 创建新节点\n2. 将新节点的next指向原头节点\n3. 更新头指针指向新节点\n\n这些操作都是常数时间操作，所以时间复杂度是O(1)。',
                'hints': ['考虑需要遍历链表吗？', '头部插入只需要修改几个指针？'],
                'tags': '链表,插入操作,时间复杂度',
                'time_limit': 90
            },
            {
                'title': '栈的应用场景',
                'slug': 'stack-applications',
                'category': category,
                'difficulty': easy,
                'question_type': 'multiple_choice',
                'question_text': '以下哪些是栈的典型应用场景？（多选）',
                'options': {
                    'A': '函数调用管理',
                    'B': '表达式求值',
                    'C': '括号匹配检查',
                    'D': '广度优先搜索'
                },
                'correct_answer': 'A,B,C',
                'explanation': '栈的典型应用包括：\nA. 函数调用管理 - 函数调用栈\nB. 表达式求值 - 中缀转后缀，后缀表达式计算\nC. 括号匹配检查 - 利用栈的后进先出特性\n\nD. 广度优先搜索通常使用队列，不是栈的应用。',
                'hints': ['想想栈的"后进先出"特性适合什么场景', '函数调用时发生了什么？'],
                'tags': '栈,应用场景,LIFO',
                'time_limit': 120
            },
            {
                'title': '二叉树遍历',
                'slug': 'binary-tree-traversal',
                'category': category,
                'difficulty': medium,
                'question_type': 'fill_blank',
                'question_text': '对于二叉树的中序遍历，访问顺序是：先访问____子树，再访问____节点，最后访问____子树。',
                'options': {},
                'correct_answer': '左,根,右',
                'explanation': '二叉树的三种遍历方式：\n1. 前序遍历：根 → 左 → 右\n2. 中序遍历：左 → 根 → 右\n3. 后序遍历：左 → 右 → 根\n\n中序遍历对于二叉搜索树可以得到有序序列。',
                'hints': ['回忆三种遍历方式的定义', '中序遍历的"中"指的是根节点的位置'],
                'tags': '二叉树,遍历,中序',
                'time_limit': 90
            }
        ]
        
        for ex_data in exercises:
            exercise, created = Exercise.objects.get_or_create(
                slug=ex_data['slug'],
                defaults=ex_data
            )
            if created:
                self.stdout.write(f'创建练习题: {exercise.title}')
    
    def create_algorithm_exercises(self):
        """创建算法设计练习题"""
        category = ExerciseCategory.objects.get(slug='algorithms')
        easy = ExerciseDifficulty.objects.get(level=1)
        medium = ExerciseDifficulty.objects.get(level=2)
        
        exercises = [
            {
                'title': '冒泡排序时间复杂度',
                'slug': 'bubble-sort-complexity',
                'category': category,
                'difficulty': easy,
                'question_type': 'single_choice',
                'question_text': '冒泡排序在最坏情况下的时间复杂度是多少？',
                'options': {
                    'A': 'O(n)',
                    'B': 'O(n log n)',
                    'C': 'O(n²)',
                    'D': 'O(2ⁿ)'
                },
                'correct_answer': 'C',
                'explanation': '冒泡排序的时间复杂度分析：\n- 最好情况（已排序）：O(n)\n- 平均情况：O(n²)\n- 最坏情况（逆序）：O(n²)\n\n最坏情况下需要进行n-1轮比较，每轮最多n-1次交换，总共约n²/2次操作。',
                'hints': ['考虑数组完全逆序的情况', '需要多少轮比较？每轮多少次操作？'],
                'tags': '冒泡排序,时间复杂度,排序算法',
                'time_limit': 60,
                'is_featured': True
            },
            {
                'title': '二分查找条件',
                'slug': 'binary-search-condition',
                'category': category,
                'difficulty': easy,
                'question_type': 'true_false',
                'question_text': '二分查找算法要求数组必须是有序的。',
                'options': {},
                'correct_answer': 'true',
                'explanation': '二分查找的前提条件：\n1. 数组必须是有序的（升序或降序）\n2. 支持随机访问（如数组）\n\n有序性是二分查找能够工作的基础，因为算法依赖于比较中间元素来决定搜索方向。',
                'hints': ['想想二分查找的工作原理', '为什么能够排除一半的元素？'],
                'tags': '二分查找,有序数组,查找算法',
                'time_limit': 45
            }
        ]
        
        for ex_data in exercises:
            exercise, created = Exercise.objects.get_or_create(
                slug=ex_data['slug'],
                defaults=ex_data
            )
            if created:
                self.stdout.write(f'创建练习题: {exercise.title}')
    
    def create_network_exercises(self):
        """创建计算机网络练习题"""
        category = ExerciseCategory.objects.get(slug='computer-networks')
        easy = ExerciseDifficulty.objects.get(level=1)
        
        exercises = [
            {
                'title': 'TCP和UDP的区别',
                'slug': 'tcp-udp-difference',
                'category': category,
                'difficulty': easy,
                'question_type': 'single_choice',
                'question_text': 'TCP和UDP最主要的区别是什么？',
                'options': {
                    'A': 'TCP是面向连接的，UDP是无连接的',
                    'B': 'TCP速度快，UDP速度慢',
                    'C': 'TCP用于局域网，UDP用于广域网',
                    'D': 'TCP是硬件协议，UDP是软件协议'
                },
                'correct_answer': 'A',
                'explanation': 'TCP和UDP的主要区别：\n\nTCP（传输控制协议）：\n- 面向连接\n- 可靠传输\n- 有序传输\n- 流量控制\n- 拥塞控制\n\nUDP（用户数据报协议）：\n- 无连接\n- 不可靠传输\n- 简单快速\n- 无流量控制',
                'hints': ['想想建立连接的过程', 'TCP需要三次握手，UDP呢？'],
                'tags': 'TCP,UDP,传输层协议',
                'time_limit': 90,
                'is_featured': True
            }
        ]
        
        for ex_data in exercises:
            exercise, created = Exercise.objects.get_or_create(
                slug=ex_data['slug'],
                defaults=ex_data
            )
            if created:
                self.stdout.write(f'创建练习题: {exercise.title}')
    
    def create_os_exercises(self):
        """创建操作系统练习题"""
        category = ExerciseCategory.objects.get(slug='operating-systems')
        medium = ExerciseDifficulty.objects.get(level=2)
        
        exercises = [
            {
                'title': '进程和线程的区别',
                'slug': 'process-thread-difference',
                'category': category,
                'difficulty': medium,
                'question_type': 'short_answer',
                'question_text': '请简述进程和线程的主要区别。',
                'options': {},
                'correct_answer': '进程是资源分配的基本单位，线程是CPU调度的基本单位。进程拥有独立的内存空间，线程共享进程的内存空间。',
                'explanation': '进程和线程的区别：\n\n进程：\n- 资源分配的基本单位\n- 拥有独立的内存空间\n- 进程间通信需要特殊机制\n- 创建和切换开销大\n\n线程：\n- CPU调度的基本单位\n- 共享进程的内存空间\n- 线程间通信简单\n- 创建和切换开销小',
                'hints': ['考虑资源分配和调度的角度', '想想内存空间的共享情况'],
                'tags': '进程,线程,操作系统',
                'time_limit': 180
            }
        ]
        
        for ex_data in exercises:
            exercise, created = Exercise.objects.get_or_create(
                slug=ex_data['slug'],
                defaults=ex_data
            )
            if created:
                self.stdout.write(f'创建练习题: {exercise.title}')
    
    def create_database_exercises(self):
        """创建数据库练习题"""
        category = ExerciseCategory.objects.get(slug='database-systems')
        easy = ExerciseDifficulty.objects.get(level=1)
        
        exercises = [
            {
                'title': 'SQL基本查询',
                'slug': 'sql-basic-query',
                'category': category,
                'difficulty': easy,
                'question_type': 'coding',
                'question_text': '编写SQL语句，从students表中查询所有年龄大于20岁的学生姓名。',
                'options': {},
                'correct_answer': 'SELECT name FROM students WHERE age > 20;',
                'explanation': 'SQL基本查询语法：\nSELECT 列名 FROM 表名 WHERE 条件;\n\n这个查询的组成部分：\n- SELECT name: 选择name列\n- FROM students: 从students表\n- WHERE age > 20: 条件是年龄大于20',
                'hints': ['使用SELECT语句', '记住WHERE子句的语法', '注意SQL语句以分号结尾'],
                'tags': 'SQL,查询,数据库',
                'time_limit': 120
            }
        ]
        
        for ex_data in exercises:
            exercise, created = Exercise.objects.get_or_create(
                slug=ex_data['slug'],
                defaults=ex_data
            )
            if created:
                self.stdout.write(f'创建练习题: {exercise.title}')
    
    def create_sample_exercise_sets(self):
        """创建示例题集"""
        # 数据结构基础题集
        ds_category = ExerciseCategory.objects.get(slug='data-structures')
        ds_set, created = ExerciseSet.objects.get_or_create(
            slug='data-structures-basics',
            defaults={
                'name': '数据结构基础',
                'description': '包含数组、链表、栈、队列、树等基础数据结构的练习题',
                'category': ds_category,
                'time_limit': 30,
                'shuffle_questions': True,
                'show_result_immediately': True,
                'is_public': True
            }
        )
        
        if created:
            # 添加题目到题集
            ds_exercises = Exercise.objects.filter(category=ds_category)
            for i, exercise in enumerate(ds_exercises):
                ExerciseSetItem.objects.create(
                    exercise_set=ds_set,
                    exercise=exercise,
                    order=i + 1,
                    points=10
                )
            self.stdout.write(f'创建题集: {ds_set.name}')
        
        # 算法基础题集
        algo_category = ExerciseCategory.objects.get(slug='algorithms')
        algo_set, created = ExerciseSet.objects.get_or_create(
            slug='algorithms-basics',
            defaults={
                'name': '算法基础',
                'description': '包含排序、查找等基础算法的练习题',
                'category': algo_category,
                'time_limit': 20,
                'shuffle_questions': False,
                'show_result_immediately': True,
                'is_public': True
            }
        )
        
        if created:
            algo_exercises = Exercise.objects.filter(category=algo_category)
            for i, exercise in enumerate(algo_exercises):
                ExerciseSetItem.objects.create(
                    exercise_set=algo_set,
                    exercise=exercise,
                    order=i + 1,
                    points=15
                )
            self.stdout.write(f'创建题集: {algo_set.name}')
