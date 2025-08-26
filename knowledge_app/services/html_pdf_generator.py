"""
HTML转PDF生成器
使用HTML模板生成PDF，完美支持中文
"""

import os
import io
from datetime import datetime
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class HTMLPDFGenerator:
    """HTML转PDF生成器"""
    
    def __init__(self):
        pass
    
    def generate_library_pdf(self, library, questions=None):
        """生成题库PDF"""
        try:
            # 获取题目
            if not questions:
                questions = library.questions.all().order_by('created_at')
            
            # 准备模板数据
            context = {
                'library': library,
                'questions': questions,
                'generated_time': datetime.now(),
                'total_questions': len(questions)
            }
            
            # 渲染HTML模板
            html_content = render_to_string('knowledge_app/quiz/pdf_library_template.html', context)
            
            # 转换为PDF
            pdf_content = self.html_to_pdf(html_content)
            
            return pdf_content
            
        except Exception as e:
            logger.error(f"Failed to generate library PDF: {e}")
            raise
    
    def generate_wrong_answers_pdf(self, user, wrong_answers=None):
        """生成错题集PDF"""
        try:
            # 获取错题
            if not wrong_answers:
                from ..personal_quiz_models import WrongAnswer
                wrong_answers = WrongAnswer.objects.filter(user=user).order_by('-last_wrong_at')
            
            # 准备模板数据
            context = {
                'user': user,
                'wrong_answers': wrong_answers,
                'generated_time': datetime.now(),
                'total_wrong_answers': len(wrong_answers)
            }
            
            # 渲染HTML模板
            html_content = render_to_string('knowledge_app/quiz/pdf_wrong_answers_template.html', context)
            
            # 转换为PDF
            pdf_content = self.html_to_pdf(html_content)
            
            return pdf_content
            
        except Exception as e:
            logger.error(f"Failed to generate wrong answers PDF: {e}")
            raise
    
    def html_to_pdf(self, html_content):
        """将HTML转换为PDF"""
        try:
            # 尝试使用weasyprint
            try:
                import weasyprint
                pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
                return pdf_bytes
            except ImportError:
                logger.warning("weasyprint not available, falling back to simple text PDF")
                return self.create_simple_text_pdf(html_content)
                
        except Exception as e:
            logger.error(f"HTML to PDF conversion failed: {e}")
            # 回退到简单文本PDF
            return self.create_simple_text_pdf(html_content)
    
    def create_simple_text_pdf(self, html_content):
        """创建简单的文本PDF（回退方案）"""
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        import re
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        
        styles = getSampleStyleSheet()
        story = []
        
        # 简单解析HTML内容
        text_content = re.sub(r'<[^>]+>', '', html_content)  # 移除HTML标签
        text_content = text_content.replace('&nbsp;', ' ')
        text_content = text_content.replace('&amp;', '&')
        text_content = text_content.replace('&lt;', '<')
        text_content = text_content.replace('&gt;', '>')
        
        # 分段处理
        paragraphs = text_content.split('\n')
        for para in paragraphs:
            para = para.strip()
            if para:
                try:
                    story.append(Paragraph(para, styles['Normal']))
                    story.append(Spacer(1, 6))
                except Exception as e:
                    # 如果段落包含无法处理的字符，跳过
                    logger.warning(f"Skipped paragraph due to encoding issue: {e}")
                    continue
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def create_pdf_response(self, pdf_content, filename):
        """创建PDF响应"""
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# 创建全局实例
html_pdf_generator = HTMLPDFGenerator()
