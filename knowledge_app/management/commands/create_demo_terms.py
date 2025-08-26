"""
创建演示每日名词数据
用于在没有API密钥的情况下测试系统功能
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random

from knowledge_app.models import DailyTerm, TermHistory


class Command(BaseCommand):
    help = '创建演示每日名词数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='创建多少天的演示数据'
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有数据'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write("清除现有数据...")
            DailyTerm.objects.all().delete()
            TermHistory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ 数据清除完成"))

        days = options['days']
        self.stdout.write(f"创建 {days} 天的演示数据...")

        # 演示数据
        demo_terms = [
            {
                'term': '算法复杂度',
                'explanation': '''算法复杂度是衡量算法效率的重要指标，主要包括时间复杂度和空间复杂度。

时间复杂度描述算法执行时间与输入规模的关系，常用大O记号表示，如O(1)、O(n)、O(log n)等。

空间复杂度描述算法执行过程中所需存储空间与输入规模的关系。

理解算法复杂度有助于选择最适合的算法来解决问题，是程序员必备的基础知识。''',
                'category': '算法设计',
                'difficulty': 'intermediate'
            },
            {
                'term': '哈希表',
                'explanation': '''哈希表（Hash Table）是一种基于哈希函数的数据结构，能够实现快速的数据存储和检索。

基本原理：通过哈希函数将键（key）映射到数组的特定位置，实现O(1)的平均查找时间。

主要特点：
1. 快速访问：平均时间复杂度为O(1)
2. 空间换时间：需要额外的存储空间
3. 处理冲突：通过链表法或开放寻址法解决哈希冲突

应用场景：数据库索引、缓存系统、编程语言中的字典/映射等。''',
                'category': '数据结构',
                'difficulty': 'beginner'
            },
            {
                'term': 'TCP三次握手',
                'explanation': '''TCP三次握手是建立可靠连接的重要机制，确保通信双方都准备好进行数据传输。

握手过程：
1. 第一次握手：客户端发送SYN包，请求建立连接
2. 第二次握手：服务器回复SYN+ACK包，确认连接请求
3. 第三次握手：客户端发送ACK包，确认连接建立

这个过程解决了网络通信中的同步问题，确保双方都知道对方已准备好通信。

理解三次握手有助于深入理解网络编程和故障排除。''',
                'category': '计算机网络',
                'difficulty': 'intermediate'
            },
            {
                'term': '二叉搜索树',
                'explanation': '''二叉搜索树（Binary Search Tree，BST）是一种特殊的二叉树数据结构。

基本性质：
1. 左子树的所有节点值小于根节点值
2. 右子树的所有节点值大于根节点值
3. 左右子树也都是二叉搜索树

主要操作：
- 查找：O(log n)平均时间复杂度
- 插入：O(log n)平均时间复杂度
- 删除：O(log n)平均时间复杂度

应用场景：数据库索引、表达式解析、优先队列等。

注意：在最坏情况下（树退化为链表），时间复杂度会变为O(n)。''',
                'category': '数据结构',
                'difficulty': 'intermediate'
            },
            {
                'term': '进程与线程',
                'explanation': '''进程和线程是操作系统中的重要概念，用于实现程序的并发执行。

进程（Process）：
- 是程序的一次执行实例
- 拥有独立的内存空间
- 进程间通信需要特殊机制（IPC）

线程（Thread）：
- 是进程内的执行单元
- 共享进程的内存空间
- 线程间通信更加便捷

主要区别：
1. 资源占用：进程占用更多系统资源
2. 通信方式：线程通信更高效
3. 稳定性：进程崩溃不影响其他进程

理解进程和线程对于系统编程和性能优化非常重要。''',
                'category': '操作系统',
                'difficulty': 'intermediate'
            },
            {
                'term': 'SQL注入',
                'explanation': '''SQL注入是一种常见的网络安全漏洞，攻击者通过在输入中插入恶意SQL代码来操控数据库。

攻击原理：
当应用程序直接将用户输入拼接到SQL语句中时，恶意用户可以构造特殊输入来改变SQL语句的逻辑。

防护措施：
1. 使用参数化查询（预编译语句）
2. 输入验证和过滤
3. 最小权限原则
4. 使用存储过程
5. 定期安全审计

示例：
原始查询：SELECT * FROM users WHERE id = '$user_id'
恶意输入：1' OR '1'='1
结果查询：SELECT * FROM users WHERE id = '1' OR '1'='1'

这会返回所有用户数据，造成信息泄露。''',
                'category': '信息安全',
                'difficulty': 'advanced'
            },
            {
                'term': '面向对象编程',
                'explanation': '''面向对象编程（Object-Oriented Programming，OOP）是一种编程范式，以对象为中心组织代码。

四大基本特性：
1. 封装（Encapsulation）：将数据和方法封装在类中
2. 继承（Inheritance）：子类可以继承父类的属性和方法
3. 多态（Polymorphism）：同一接口可以有不同的实现
4. 抽象（Abstraction）：隐藏复杂的实现细节

优势：
- 代码重用性高
- 易于维护和扩展
- 更好地模拟现实世界
- 提高开发效率

常见的面向对象语言：Java、C++、Python、C#等。

理解OOP思想对于现代软件开发至关重要。''',
                'category': '编程基础',
                'difficulty': 'beginner'
            },
            {
                'term': '数据库事务',
                'explanation': '''数据库事务是一组数据库操作的逻辑单元，要么全部成功，要么全部失败。

ACID特性：
1. 原子性（Atomicity）：事务中的操作要么全部完成，要么全部不完成
2. 一致性（Consistency）：事务执行前后数据库状态保持一致
3. 隔离性（Isolation）：并发事务之间相互隔离
4. 持久性（Durability）：已提交的事务永久保存

事务状态：
- 活动状态：事务正在执行
- 部分提交：事务执行完毕，等待提交
- 提交状态：事务成功完成
- 失败状态：事务执行失败
- 中止状态：事务回滚完成

事务对于保证数据一致性和可靠性至关重要。''',
                'category': '数据库系统',
                'difficulty': 'intermediate'
            },
            {
                'term': '机器学习',
                'explanation': '''机器学习是人工智能的一个分支，通过算法让计算机从数据中自动学习和改进。

主要类型：
1. 监督学习：使用标记数据训练模型（如分类、回归）
2. 无监督学习：从无标记数据中发现模式（如聚类、降维）
3. 强化学习：通过与环境交互学习最优策略

常见算法：
- 线性回归、逻辑回归
- 决策树、随机森林
- 支持向量机（SVM）
- 神经网络、深度学习

应用领域：
图像识别、自然语言处理、推荐系统、自动驾驶等。

机器学习正在改变各个行业，是当前最热门的技术领域之一。''',
                'category': '人工智能',
                'difficulty': 'advanced'
            },
            {
                'term': '版本控制系统',
                'explanation': '''版本控制系统用于跟踪文件的历史变化，管理代码的不同版本。

主要功能：
1. 记录文件变化历史
2. 支持多人协作开发
3. 分支管理和合并
4. 回滚到历史版本

常见系统：
- Git：分布式版本控制，最流行
- SVN：集中式版本控制
- Mercurial：分布式版本控制

Git基本概念：
- 仓库（Repository）：存储项目的地方
- 提交（Commit）：保存文件变化的快照
- 分支（Branch）：独立的开发线
- 合并（Merge）：将分支变化合并到主线

版本控制是现代软件开发的基础工具。''',
                'category': '软件工程',
                'difficulty': 'beginner'
            }
        ]

        success_count = 0
        today = timezone.now().date()

        for i in range(days):
            display_date = today - timedelta(days=days-1-i)
            
            # 选择一个演示名词
            term_data = demo_terms[i % len(demo_terms)]
            
            # 检查是否已存在
            if DailyTerm.objects.filter(display_date=display_date).exists():
                self.stdout.write(f"⏭️  {display_date} 已存在名词，跳过")
                continue
            
            try:
                # 创建每日名词
                daily_term = DailyTerm.objects.create(
                    term=term_data['term'],
                    explanation=term_data['explanation'],
                    category=term_data['category'],
                    difficulty_level=term_data['difficulty'],
                    display_date=display_date,
                    status='active',
                    api_source='demo',
                    api_request_time=timezone.now(),
                    extended_info={
                        'demo_data': True,
                        'created_by': 'demo_script'
                    }
                )
                
                # 添加到历史记录
                TermHistory.add_term(term_data['term'], display_date)
                
                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ {display_date}: {term_data['term']}")
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ {display_date}: 创建失败 - {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 演示数据创建完成: 成功 {success_count} 个")
        )
        
        # 显示访问链接
        self.stdout.write("\n📚 现在您可以访问:")
        self.stdout.write("   - 每日名词主页: http://localhost:8000/daily-term/")
        self.stdout.write("   - 管理后台: http://localhost:8000/admin/")
        self.stdout.write("   - 历史记录: http://localhost:8000/daily-term/history/")
