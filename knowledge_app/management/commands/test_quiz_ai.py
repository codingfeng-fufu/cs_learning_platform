from django.core.management.base import BaseCommand
from knowledge_app.services.quiz_ai_service import quiz_ai_analyzer


class Command(BaseCommand):
    help = '测试题库AI分析功能'

    def handle(self, *args, **options):
        self.stdout.write('🤖 开始测试题库AI分析功能...')
        
        # 检查AI服务是否可用
        if not quiz_ai_analyzer.is_available():
            self.stdout.write(
                self.style.ERROR('❌ AI服务不可用，请检查API配置')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS('✅ AI服务可用')
        )
        
        # 测试错题分析
        self.stdout.write('\n📝 测试错题分析功能...')
        
        test_wrong_answer = {
            'question': '在数组中访问第i个元素的时间复杂度是多少？',
            'user_answer': 'O(n)',
            'correct_answer': 'O(1)',
            'question_type': 'single_choice',
            'question_title': '数组的时间复杂度',
            'difficulty': '简单',
        }
        
        result = quiz_ai_analyzer.analyze_wrong_answer(test_wrong_answer)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ 错题分析成功')
            )
            self.stdout.write(f"📊 错误分析: {result['analysis']}")
            self.stdout.write(f"💡 学习建议: {result['suggestion']}")
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ 错题分析失败: {result.get("error", "未知错误")}')
            )
        
        # 测试会话分析
        self.stdout.write('\n📈 测试会话分析功能...')
        
        test_session_data = {
            'total_questions': 5,
            'correct_answers': 3,
            'accuracy': 60,
            'wrong_answers': [
                {
                    'question_title': '数组的时间复杂度',
                    'user_answer': 'O(n)',
                    'correct_answer': 'O(1)',
                    'question_type': '单选题',
                },
                {
                    'question_title': 'TCP和UDP的区别',
                    'user_answer': 'A',
                    'correct_answer': 'C',
                    'question_type': '单选题',
                }
            ],
            'type_stats': {
                '单选题': {'total': 5, 'correct': 3, 'accuracy': 60}
            }
        }
        
        result = quiz_ai_analyzer.analyze_session_performance(test_session_data)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ 会话分析成功')
            )
            self.stdout.write(f"📊 整体评价: {result['overall_analysis']}")
            self.stdout.write(f"💪 优势领域: {', '.join(result['strengths'])}")
            self.stdout.write(f"⚠️ 薄弱环节: {', '.join(result['weaknesses'])}")
            self.stdout.write(f"💡 学习建议: {', '.join(result['suggestions'])}")
            self.stdout.write(f"🎯 下一步计划: {', '.join(result['next_steps'])}")
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ 会话分析失败: {result.get("error", "未知错误")}')
            )
        
        self.stdout.write('\n🎉 AI功能测试完成！')
