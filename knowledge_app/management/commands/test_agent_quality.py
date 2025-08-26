"""
测试Agent质量的管理命令
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, date
from knowledge_app.services.exercise_generator_service import ExerciseGeneratorService
from knowledge_app.services.glm_chatbot_service import GLMChatbotService
from knowledge_app.services.daily_term_service import DailyTermService
from knowledge_app.services.agent_quality_monitor import quality_monitor


class Command(BaseCommand):
    help = '测试Agent质量和幻觉检测'

    def add_arguments(self, parser):
        parser.add_argument(
            '--agent',
            type=str,
            choices=['exercise', 'chatbot', 'term', 'all'],
            default='all',
            help='要测试的Agent类型'
        )
        
        parser.add_argument(
            '--count',
            type=int,
            default=3,
            help='测试生成的数量'
        )

    def handle(self, *args, **options):
        agent_type = options['agent']
        count = options['count']
        
        self.stdout.write("🧪 Agent质量测试开始")
        self.stdout.write("=" * 50)
        
        if agent_type in ['exercise', 'all']:
            self.test_exercise_generator(count)
        
        if agent_type in ['chatbot', 'all']:
            self.test_chatbot(count)
        
        if agent_type in ['term', 'all']:
            self.test_term_generator(count)
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("✅ Agent质量测试完成")
    
    def test_exercise_generator(self, count):
        """测试练习生成器"""
        self.stdout.write(f"\n🎯 测试练习生成器 (生成{count}道题)")
        self.stdout.write("-" * 30)
        
        try:
            service = ExerciseGeneratorService()
            
            # 测试不同难度的题目
            test_cases = [
                ('hamming-code', 'easy'),
                ('binary-tree', 'medium'),
                ('tcp-protocol', 'hard')
            ]
            
            total_generated = 0
            total_issues = 0
            
            for knowledge_point, difficulty in test_cases:
                self.stdout.write(f"📝 测试: {knowledge_point} ({difficulty})")
                
                try:
                    # 创建一个测试用户
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    test_user, created = User.objects.get_or_create(
                        username='test_user',
                        defaults={'email': 'test@example.com'}
                    )

                    # 生成练习会话
                    session = service.generate_exercise_session(
                        user=test_user,
                        knowledge_point=knowledge_point,
                        difficulty=difficulty,
                        count=count
                    )

                    if session:
                        exercises = session.exercises
                        for i, exercise in enumerate(exercises):
                            total_generated += 1

                            # 将练习转换为字典格式进行质量检查
                            exercise_dict = {
                                'type': exercise.get('type', 'choice'),
                                'question': exercise.get('question', ''),
                                'options': exercise.get('options', []),
                                'answer': exercise.get('answer', ''),
                                'explanation': exercise.get('explanation', '')
                            }

                            is_quality_ok, issues = quality_monitor.validate_exercise_quality(exercise_dict)

                            if issues:
                                total_issues += len(issues)
                                self.stdout.write(
                                    self.style.WARNING(f"  题目{i+1}质量问题: {', '.join(issues)}")
                                )
                            else:
                                self.stdout.write(
                                    self.style.SUCCESS(f"  题目{i+1}: ✅ 质量良好")
                                )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"  生成失败: 无法创建练习会话")
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  测试出错: {e}")
                    )
            
            # 统计结果
            if total_generated > 0:
                quality_rate = (total_generated - total_issues) / total_generated * 100
                self.stdout.write(f"\n📊 练习生成器质量统计:")
                self.stdout.write(f"  总生成数: {total_generated}")
                self.stdout.write(f"  质量问题: {total_issues}")
                self.stdout.write(f"  质量率: {quality_rate:.1f}%")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"练习生成器测试失败: {e}")
            )
    
    def test_chatbot(self, count):
        """测试聊天机器人"""
        self.stdout.write(f"\n🤖 测试聊天机器人 (测试{count}个对话)")
        self.stdout.write("-" * 30)
        
        try:
            service = GLMChatbotService()
            
            if not service.is_available():
                self.stdout.write(
                    self.style.WARNING("GLM API未配置，跳过聊天机器人测试")
                )
                return
            
            # 测试用例
            test_cases = [
                ("人工智能", "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。", "人工智能有哪些应用？"),
                ("二叉树", "二叉树是一种树形数据结构，其中每个节点最多有两个子节点。", "二叉树的遍历方法有哪些？"),
                ("TCP协议", "TCP是一种面向连接的、可靠的传输层协议。", "TCP和UDP有什么区别？")
            ]
            
            total_responses = 0
            total_issues = 0
            
            for term, explanation, question in test_cases[:count]:
                self.stdout.write(f"💬 测试对话: {term}")
                
                try:
                    result = service.ask_about_term(term, explanation, question)
                    
                    if result['success']:
                        total_responses += 1
                        answer = result['answer']
                        
                        is_quality_ok, issues = quality_monitor.validate_chat_response_quality(
                            answer, explanation
                        )
                        
                        if issues:
                            total_issues += len(issues)
                            self.stdout.write(
                                self.style.WARNING(f"  回复质量问题: {', '.join(issues)}")
                            )
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(f"  回复质量: ✅ 良好")
                            )
                        
                        # 显示回复摘要
                        self.stdout.write(f"  回复摘要: {answer[:100]}...")
                        
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"  对话失败: {result.get('error', '未知错误')}")
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  测试出错: {e}")
                    )
            
            # 统计结果
            if total_responses > 0:
                quality_rate = (total_responses - total_issues) / total_responses * 100
                self.stdout.write(f"\n📊 聊天机器人质量统计:")
                self.stdout.write(f"  总回复数: {total_responses}")
                self.stdout.write(f"  质量问题: {total_issues}")
                self.stdout.write(f"  质量率: {quality_rate:.1f}%")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"聊天机器人测试失败: {e}")
            )
    
    def test_term_generator(self, count):
        """测试名词生成器"""
        self.stdout.write(f"\n📚 测试名词生成器 (生成{count}个名词)")
        self.stdout.write("-" * 30)
        
        try:
            service = DailyTermService()
            
            total_generated = 0
            total_issues = 0
            
            for i in range(count):
                self.stdout.write(f"📖 生成名词 {i+1}")
                
                try:
                    # 生成名词和解释
                    result = service.generate_daily_term()
                    
                    if result:
                        total_generated += 1
                        term = result.term
                        explanation = result.explanation
                        
                        # 质量检查
                        is_quality_ok, issues = quality_monitor.validate_explanation_quality(
                            term, explanation
                        )
                        
                        if issues:
                            total_issues += len(issues)
                            self.stdout.write(
                                self.style.WARNING(f"  名词'{term}'质量问题: {', '.join(issues)}")
                            )
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(f"  名词'{term}': ✅ 质量良好")
                            )
                        
                        # 显示解释摘要
                        self.stdout.write(f"  解释摘要: {explanation[:100]}...")
                        
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"  生成失败")
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  测试出错: {e}")
                    )
            
            # 统计结果
            if total_generated > 0:
                quality_rate = (total_generated - total_issues) / total_generated * 100
                self.stdout.write(f"\n📊 名词生成器质量统计:")
                self.stdout.write(f"  总生成数: {total_generated}")
                self.stdout.write(f"  质量问题: {total_issues}")
                self.stdout.write(f"  质量率: {quality_rate:.1f}%")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"名词生成器测试失败: {e}")
            )
