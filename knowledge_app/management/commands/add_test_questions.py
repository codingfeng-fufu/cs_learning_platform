from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from knowledge_app.personal_quiz_models import QuizLibrary, QuizQuestion, QuizTag

User = get_user_model()


class Command(BaseCommand):
    help = '添加测试题目到个人题库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='用户名（如果不指定，将使用第一个超级用户）',
        )

    def handle(self, *args, **options):
        # 获取用户
        username = options.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'用户 {username} 不存在')
                )
                return
        else:
            # 使用第一个超级用户
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stdout.write(
                    self.style.ERROR('没有找到超级用户，请先创建用户或指定用户名')
                )
                return

        # 创建或获取测试题库
        library, created = QuizLibrary.objects.get_or_create(
            owner=user,
            name='计算机基础知识测试',
            defaults={
                'description': '包含计算机科学基础概念的测试题库，适合初学者和复习使用。'
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'创建了新题库: {library.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'题库已存在: {library.name}')
            )

        # 创建标签
        tags_data = [
            ('数据结构', '#3b82f6'),
            ('算法', '#10b981'),
            ('操作系统', '#f59e0b'),
            ('网络', '#ef4444'),
            ('数据库', '#8b5cf6'),
            ('编程语言', '#06b6d4'),
        ]

        tags = {}
        for tag_name, color in tags_data:
            tag, created = QuizTag.objects.get_or_create(
                name=tag_name,
                defaults={'color': color}
            )
            tags[tag_name] = tag

        # 测试题目数据
        questions_data = [
            {
                'title': '数组的时间复杂度',
                'content': '在数组中访问第i个元素的时间复杂度是多少？',
                'options': {
                    'A': 'O(1)',
                    'B': 'O(log n)',
                    'C': 'O(n)',
                    'D': 'O(n²)'
                },
                'correct_answer': 'A',
                'explanation': '数组是连续存储的数据结构，可以通过索引直接访问任意位置的元素，时间复杂度为O(1)。',
                'difficulty': 1,
                'tags': ['数据结构', '算法']
            },
            {
                'title': '栈的特点',
                'content': '栈（Stack）数据结构遵循什么原则？',
                'options': {
                    'A': 'FIFO（先进先出）',
                    'B': 'LIFO（后进先出）',
                    'C': '随机访问',
                    'D': '优先级访问'
                },
                'correct_answer': 'B',
                'explanation': '栈是一种后进先出（LIFO）的数据结构，最后压入栈的元素最先被弹出。',
                'difficulty': 1,
                'tags': ['数据结构']
            },
            {
                'title': '二分查找的前提条件',
                'content': '二分查找算法要求数据必须满足什么条件？',
                'options': {
                    'A': '数据量要大',
                    'B': '数据已排序',
                    'C': '数据类型相同',
                    'D': '数据连续存储'
                },
                'correct_answer': 'B',
                'explanation': '二分查找算法要求数据必须是已排序的，这样才能通过比较中间元素来确定搜索方向。',
                'difficulty': 2,
                'tags': ['算法']
            },
            {
                'title': '进程和线程的区别',
                'content': '进程和线程的主要区别是什么？',
                'options': {
                    'A': '进程比线程快',
                    'B': '线程比进程占用内存少',
                    'C': '进程拥有独立的内存空间，线程共享进程的内存空间',
                    'D': '进程和线程没有区别'
                },
                'correct_answer': 'C',
                'explanation': '进程是系统资源分配的基本单位，拥有独立的内存空间；线程是CPU调度的基本单位，同一进程内的线程共享内存空间。',
                'difficulty': 2,
                'tags': ['操作系统']
            },
            {
                'title': 'TCP和UDP的区别',
                'content': 'TCP协议相比UDP协议的主要特点是什么？',
                'options': {
                    'A': '传输速度更快',
                    'B': '占用带宽更少',
                    'C': '提供可靠的数据传输',
                    'D': '支持广播传输'
                },
                'correct_answer': 'C',
                'explanation': 'TCP是面向连接的可靠传输协议，提供数据完整性检查、重传机制等，确保数据可靠传输。',
                'difficulty': 2,
                'tags': ['网络']
            },
            {
                'title': '数据库的ACID特性',
                'content': '数据库事务的ACID特性中，"I"代表什么？',
                'options': {
                    'A': 'Atomicity（原子性）',
                    'B': 'Consistency（一致性）',
                    'C': 'Isolation（隔离性）',
                    'D': 'Durability（持久性）'
                },
                'correct_answer': 'C',
                'explanation': 'ACID中的I代表Isolation（隔离性），指并发执行的事务之间不会相互影响。',
                'difficulty': 3,
                'tags': ['数据库']
            },
            {
                'title': '面向对象编程的特征',
                'content': '以下哪个不是面向对象编程的基本特征？',
                'options': {
                    'A': '封装（Encapsulation）',
                    'B': '继承（Inheritance）',
                    'C': '多态（Polymorphism）',
                    'D': '递归（Recursion）'
                },
                'correct_answer': 'D',
                'explanation': '面向对象编程的三大基本特征是封装、继承和多态。递归是一种编程技术，不是面向对象的特征。',
                'difficulty': 2,
                'tags': ['编程语言']
            },
            {
                'title': '哈希表的平均时间复杂度',
                'content': '在理想情况下，哈希表的查找、插入、删除操作的平均时间复杂度是多少？',
                'options': {
                    'A': 'O(1)',
                    'B': 'O(log n)',
                    'C': 'O(n)',
                    'D': 'O(n log n)'
                },
                'correct_answer': 'A',
                'explanation': '在理想情况下（没有哈希冲突），哈希表的查找、插入、删除操作都可以在常数时间O(1)内完成。',
                'difficulty': 2,
                'tags': ['数据结构', '算法']
            },
            {
                'title': '死锁的必要条件',
                'content': '以下哪个不是死锁产生的必要条件？',
                'options': {
                    'A': '互斥条件',
                    'B': '请求和保持条件',
                    'C': '不剥夺条件',
                    'D': '优先级条件'
                },
                'correct_answer': 'D',
                'explanation': '死锁产生的四个必要条件是：互斥条件、请求和保持条件、不剥夺条件、环路等待条件。优先级条件不是死锁的必要条件。',
                'difficulty': 3,
                'tags': ['操作系统']
            },
            {
                'title': 'HTTP状态码',
                'content': 'HTTP状态码404表示什么？',
                'options': {
                    'A': '服务器内部错误',
                    'B': '请求成功',
                    'C': '资源未找到',
                    'D': '权限不足'
                },
                'correct_answer': 'C',
                'explanation': 'HTTP状态码404表示"Not Found"，即请求的资源在服务器上未找到。',
                'difficulty': 1,
                'tags': ['网络']
            }
        ]

        # 添加题目
        added_count = 0
        for question_data in questions_data:
            # 检查题目是否已存在
            if QuizQuestion.objects.filter(
                library=library,
                title=question_data['title']
            ).exists():
                self.stdout.write(
                    self.style.WARNING(f'题目已存在: {question_data["title"]}')
                )
                continue

            # 创建题目
            question = QuizQuestion.objects.create(
                library=library,
                question_type='single_choice',
                title=question_data['title'],
                content=question_data['content'],
                options=question_data['options'],
                correct_answer=question_data['correct_answer'],
                explanation=question_data['explanation'],
                difficulty=question_data['difficulty']
            )

            # 添加标签
            for tag_name in question_data['tags']:
                if tag_name in tags:
                    question.tags.add(tags[tag_name])

            added_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'添加题目: {question.title}')
            )

        # 更新题库统计
        library.update_question_count()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n完成！共添加 {added_count} 道题目到题库 "{library.name}"'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'题库现在共有 {library.total_questions} 道题目'
            )
        )
