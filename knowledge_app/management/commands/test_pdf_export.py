from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from knowledge_app.personal_quiz_models import QuizLibrary
from knowledge_app.services.pdf_generator import pdf_generator
import os

User = get_user_model()


class Command(BaseCommand):
    help = '测试PDF导出功能'

    def handle(self, *args, **options):
        self.stdout.write('📄 开始测试PDF导出功能...')
        
        # 获取用户
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write(
                self.style.ERROR('❌ 没有找到超级用户，请先创建用户')
            )
            return
        
        # 获取题库
        library = QuizLibrary.objects.filter(owner=user).first()
        if not library:
            self.stdout.write(
                self.style.ERROR('❌ 没有找到题库，请先创建题库')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ 找到题库: {library.name}')
        )
        
        # 测试题库PDF导出
        try:
            self.stdout.write('📝 测试题库PDF导出...')

            from knowledge_app.services.chinese_pdf_generator import chinese_pdf_generator
            questions = library.questions.all()[:5]  # 只测试前5道题
            pdf_content = chinese_pdf_generator.generate_library_pdf(library, questions)
            
            # 保存测试文件
            test_file = f'test_library_{library.id}.pdf'
            with open(test_file, 'wb') as f:
                f.write(pdf_content)
            
            file_size = len(pdf_content)
            self.stdout.write(
                self.style.SUCCESS(f'✅ 题库PDF导出成功')
            )
            self.stdout.write(f'   文件大小: {file_size} 字节')
            self.stdout.write(f'   测试文件: {test_file}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 题库PDF导出失败: {e}')
            )
        
        # 测试错题集PDF导出
        try:
            self.stdout.write('\n❌ 测试错题集PDF导出...')
            
            from knowledge_app.personal_quiz_models import WrongAnswer
            wrong_answers = WrongAnswer.objects.filter(user=user)[:3]  # 只测试前3道错题
            
            if wrong_answers.exists():
                pdf_content = chinese_pdf_generator.generate_wrong_answers_pdf(user, wrong_answers)
                
                # 保存测试文件
                test_file = f'test_wrong_answers_{user.id}.pdf'
                with open(test_file, 'wb') as f:
                    f.write(pdf_content)
                
                file_size = len(pdf_content)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ 错题集PDF导出成功')
                )
                self.stdout.write(f'   文件大小: {file_size} 字节')
                self.stdout.write(f'   测试文件: {test_file}')
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ 没有错题，跳过错题集PDF测试')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 错题集PDF导出失败: {e}')
            )
        
        self.stdout.write('\n🎉 PDF导出功能测试完成！')
        self.stdout.write('💡 提示: 可以在浏览器中访问以下链接测试PDF导出:')
        self.stdout.write(f'   题库PDF: http://127.0.0.1:8000/quiz/libraries/{library.id}/export-pdf/')
        self.stdout.write(f'   错题PDF: http://127.0.0.1:8000/quiz/wrong-answers/export-pdf/')
