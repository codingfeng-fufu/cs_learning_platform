from django.core.management.base import BaseCommand
from django.db import transaction
from knowledge_app.exercise_models import ExerciseCategory, ExerciseDifficulty, Exercise


class Command(BaseCommand):
    help = '初始化练习题系统的基础数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有数据后重新初始化',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('清除现有数据...')
            Exercise.objects.all().delete()
            ExerciseCategory.objects.all().delete()
            ExerciseDifficulty.objects.all().delete()

        with transaction.atomic():
            # 创建难度等级
            difficulties = [
                {'name': '初级', 'level': 1, 'color': '#28a745', 'description': '适合初学者'},
                {'name': '中级', 'level': 2, 'color': '#ffc107', 'description': '需要一定基础'},
                {'name': '高级', 'level': 3, 'color': '#dc3545', 'description': '需要深入理解'},
            ]

            for diff_data in difficulties:
                difficulty, created = ExerciseDifficulty.objects.get_or_create(
                    name=diff_data['name'],
                    defaults=diff_data
                )
                if created:
                    self.stdout.write(f'创建难度等级: {difficulty.name}')

            # 创建分类
            categories = [
                {
                    'name': '数据结构',
                    'slug': 'data-structures',
                    'description': '数组、链表、栈、队列、树、图等数据结构相关题目',
                    'icon': '🧠',
                    'color': '#007bff',
                    'order': 1
                },
                {
                    'name': '算法设计',
                    'slug': 'algorithm-design',
                    'description': '排序、搜索、动态规划、贪心算法等',
                    'icon': '⚡',
                    'color': '#28a745',
                    'order': 2
                },
                {
                    'name': '计算机网络',
                    'slug': 'computer-networks',
                    'description': 'TCP/IP、HTTP、网络协议等相关题目',
                    'icon': '🌐',
                    'color': '#17a2b8',
                    'order': 3
                },
                {
                    'name': '操作系统',
                    'slug': 'operating-systems',
                    'description': '进程管理、内存管理、文件系统等',
                    'icon': '💻',
                    'color': '#6f42c1',
                    'order': 4
                },
                {
                    'name': '数据库系统',
                    'slug': 'database-systems',
                    'description': 'SQL、事务、索引、数据库设计等',
                    'icon': '🗄️',
                    'color': '#fd7e14',
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
            sample_exercises = [
                {
                    'title': '数组的基本概念',
                    'slug': 'array-basic-concept',
                    'category_slug': 'data-structures',
                    'difficulty_name': '初级',
                    'question_type': 'single_choice',
                    'question_text': '数组是一种什么样的数据结构？',
                    'options': {
                        'A': '线性数据结构，元素在内存中连续存储',
                        'B': '非线性数据结构，元素随机分布',
                        'C': '树形数据结构，有层次关系',
                        'D': '图形数据结构，元素之间有复杂关系'
                    },
                    'correct_answer': 'A',
                    'explanation': '数组是一种线性数据结构，其元素在内存中连续存储，可以通过索引快速访问任意元素，时间复杂度为O(1)。',
                    'hints': [
                        '考虑数组元素在内存中的存储方式',
                        '想想数组访问元素的特点',
                        '数组支持随机访问，时间复杂度为O(1)'
                    ],
                    'tags': '数组,基础概念,线性结构'
                },
                {
                    'title': '栈的特性',
                    'slug': 'stack-characteristics',
                    'category_slug': 'data-structures',
                    'difficulty_name': '初级',
                    'question_type': 'multiple_choice',
                    'question_text': '栈数据结构具有以下哪些特性？（多选）',
                    'options': {
                        'A': '后进先出（LIFO）',
                        'B': '先进先出（FIFO）',
                        'C': '只能在栈顶进行插入和删除操作',
                        'D': '可以在任意位置插入和删除元素'
                    },
                    'correct_answer': 'A,C',
                    'explanation': '栈是一种后进先出（LIFO）的数据结构，只能在栈顶进行push（入栈）和pop（出栈）操作。',
                    'hints': [
                        '想想栈的英文名称Stack的含义',
                        '考虑栈的操作限制',
                        '栈顶是唯一的操作位置'
                    ],
                    'tags': '栈,LIFO,数据结构'
                },
                {
                    'title': '二分查找的时间复杂度',
                    'slug': 'binary-search-complexity',
                    'category_slug': 'algorithm-design',
                    'difficulty_name': '中级',
                    'question_type': 'fill_blank',
                    'question_text': '在有序数组中进行二分查找的时间复杂度是____。',
                    'correct_answer': 'O(log n)',
                    'explanation': '二分查找每次都将搜索范围缩小一半，所以时间复杂度是O(log n)，其中n是数组的长度。',
                    'hints': [
                        '考虑每次查找后搜索范围的变化',
                        '想想需要多少次才能找到目标元素',
                        '对数函数的特点'
                    ],
                    'tags': '二分查找,时间复杂度,算法分析'
                },
                {
                    'title': 'TCP协议的可靠性',
                    'slug': 'tcp-reliability',
                    'category_slug': 'computer-networks',
                    'difficulty_name': '中级',
                    'question_type': 'true_false',
                    'question_text': 'TCP协议通过序列号、确认应答、重发控制、连接管理等机制来保证数据传输的可靠性。',
                    'correct_answer': 'true',
                    'explanation': 'TCP协议确实通过多种机制来保证可靠性：序列号用于数据排序，确认应答用于确认接收，重发控制用于处理丢包，连接管理用于建立和维护连接。',
                    'hints': [
                        '回忆TCP协议的特点',
                        '考虑TCP与UDP的区别',
                        'TCP被称为可靠传输协议'
                    ],
                    'tags': 'TCP,网络协议,可靠性'
                },
                {
                    'title': '进程与线程的区别',
                    'slug': 'process-vs-thread',
                    'category_slug': 'operating-systems',
                    'difficulty_name': '中级',
                    'question_type': 'short_answer',
                    'question_text': '请简述进程和线程的主要区别。',
                    'correct_answer': '进程是系统资源分配的基本单位，拥有独立的内存空间；线程是CPU调度的基本单位，同一进程内的线程共享内存空间。进程间通信需要特殊机制，线程间通信相对简单。进程创建开销大，线程创建开销小。',
                    'explanation': '进程和线程是操作系统中的重要概念。进程拥有独立的地址空间，安全性好但开销大；线程共享进程的地址空间，效率高但需要同步控制。',
                    'hints': [
                        '从资源分配角度考虑',
                        '从调度角度考虑',
                        '从通信和同步角度考虑'
                    ],
                    'tags': '进程,线程,操作系统'
                }
            ]

            for exercise_data in sample_exercises:
                category = ExerciseCategory.objects.get(slug=exercise_data['category_slug'])
                difficulty = ExerciseDifficulty.objects.get(name=exercise_data['difficulty_name'])
                
                exercise, created = Exercise.objects.get_or_create(
                    slug=exercise_data['slug'],
                    defaults={
                        'title': exercise_data['title'],
                        'category': category,
                        'difficulty': difficulty,
                        'question_type': exercise_data['question_type'],
                        'question_text': exercise_data['question_text'],
                        'options': exercise_data.get('options', {}),
                        'correct_answer': exercise_data['correct_answer'],
                        'explanation': exercise_data['explanation'],
                        'hints': exercise_data['hints'],
                        'tags': exercise_data['tags'],
                        'is_active': True,
                        'is_featured': True
                    }
                )
                
                if created:
                    self.stdout.write(f'创建练习题: {exercise.title}')

        self.stdout.write(
            self.style.SUCCESS('练习题系统初始化完成！')
        )
        
        # 显示统计信息
        category_count = ExerciseCategory.objects.count()
        difficulty_count = ExerciseDifficulty.objects.count()
        exercise_count = Exercise.objects.count()
        
        self.stdout.write(f'分类数量: {category_count}')
        self.stdout.write(f'难度等级: {difficulty_count}')
        self.stdout.write(f'练习题数量: {exercise_count}')
        
        self.stdout.write(
            self.style.SUCCESS('现在可以访问 /admin/ 来管理练习题了！')
        )
