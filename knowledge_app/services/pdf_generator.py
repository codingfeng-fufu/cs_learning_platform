"""
个人题库PDF生成服务
支持题库和错题集的PDF导出
"""

import os
import io
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import black, blue, red, green
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging

logger = logging.getLogger(__name__)


class QuizPDFGenerator:
    """题库PDF生成器"""
    
    def __init__(self):
        self.setup_fonts()
        self.setup_styles()
    
    def setup_fonts(self):
        """设置中文字体"""
        try:
            # 尝试使用系统中文字体
            import platform
            system = platform.system()

            if system == "Windows":
                # Windows系统字体路径
                font_paths = [
                    "C:/Windows/Fonts/simhei.ttf",  # 黑体
                    "C:/Windows/Fonts/simsun.ttc",  # 宋体
                    "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
                ]
            elif system == "Darwin":  # macOS
                font_paths = [
                    "/System/Library/Fonts/PingFang.ttc",
                    "/System/Library/Fonts/STHeiti Light.ttc",
                ]
            else:  # Linux
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                ]

            # 尝试注册中文字体
            font_registered = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        self.chinese_font = 'ChineseFont'
                        font_registered = True
                        logger.info(f"Successfully registered font: {font_path}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to register font {font_path}: {e}")
                        continue

            if not font_registered:
                # 如果没有找到中文字体，使用Helvetica并记录警告
                self.chinese_font = 'Helvetica'
                logger.warning("No Chinese font found, using Helvetica")

        except Exception as e:
            logger.error(f"Font setup failed: {e}")
            self.chinese_font = 'Helvetica'
    
    def setup_styles(self):
        """设置样式"""
        self.styles = getSampleStyleSheet()
        
        # 标题样式
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontName=self.chinese_font,
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=black
        )
        
        # 副标题样式
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontName=self.chinese_font,
            fontSize=14,
            spaceAfter=12,
            textColor=blue
        )
        
        # 正文样式
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            spaceAfter=8,
            alignment=TA_JUSTIFY
        )
        
        # 题目样式
        self.question_style = ParagraphStyle(
            'QuestionStyle',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=11,
            spaceAfter=6,
            leftIndent=0,
            fontWeight='bold'
        )
        
        # 选项样式
        self.option_style = ParagraphStyle(
            'OptionStyle',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            spaceAfter=3,
            leftIndent=20
        )
        
        # 答案样式
        self.answer_style = ParagraphStyle(
            'AnswerStyle',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            spaceAfter=6,
            textColor=green
        )
        
        # 解析样式
        self.explanation_style = ParagraphStyle(
            'ExplanationStyle',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=9,
            spaceAfter=10,
            leftIndent=10,
            textColor=black
        )

    def safe_text(self, text):
        """安全处理文本，确保中文显示正常"""
        if not text:
            return ""

        # 确保文本是字符串类型
        if not isinstance(text, str):
            text = str(text)

        # 如果使用的是Helvetica字体（不支持中文），则进行特殊处理
        if self.chinese_font == 'Helvetica':
            # 将中文字符替换为拼音或英文描述
            import re
            # 简单的中文字符检测和替换
            chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
            if chinese_pattern.search(text):
                # 如果包含中文，提供英文替代
                replacements = {
                    '题库': 'Question Bank',
                    '题目': 'Question',
                    '答案': 'Answer',
                    '解析': 'Explanation',
                    '选项': 'Option',
                    '正确答案': 'Correct Answer',
                    '错误答案': 'Wrong Answer',
                    '你的答案': 'Your Answer',
                    '创建时间': 'Created Time',
                    '题目数量': 'Question Count',
                    '生成时间': 'Generated Time',
                    '用户名': 'Username',
                    '错题数量': 'Wrong Answer Count',
                    '错误次数': 'Wrong Count',
                    '最近错误': 'Last Wrong',
                    'AI分析': 'AI Analysis',
                    '学习建议': 'Study Suggestion'
                }

                for chinese, english in replacements.items():
                    text = text.replace(chinese, english)

        # HTML转义特殊字符
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')

        return text
    
    def generate_library_pdf(self, library, questions=None):
        """生成题库PDF"""
        buffer = io.BytesIO()
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 构建内容
        story = []
        
        # 添加标题
        title = self.safe_text(f"{library.name} - 题库")
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 12))
        
        # 添加基本信息
        info_data = [
            [self.safe_text('题库名称:'), self.safe_text(library.name)],
            [self.safe_text('创建时间:'), library.created_at.strftime('%Y-%m-%d %H:%M')],
            [self.safe_text('题目数量:'), str(library.total_questions)],
            [self.safe_text('生成时间:'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]

        if library.description:
            info_data.insert(1, [self.safe_text('题库描述:'), self.safe_text(library.description)])
        
        info_table = Table(info_data, colWidths=[3*cm, 12*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('BACKGROUND', (0, 0), (0, -1), '#f0f0f0'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # 添加题目
        if not questions:
            questions = library.questions.all().order_by('created_at')
        
        for i, question in enumerate(questions, 1):
            # 题目标题
            question_title = self.safe_text(f"{i}. {question.title}")
            story.append(Paragraph(question_title, self.question_style))

            # 题目内容
            story.append(Paragraph(self.safe_text(question.content), self.body_style))
            story.append(Spacer(1, 6))

            # 选项（选择题）
            if question.question_type in ['single_choice', 'multiple_choice']:
                for key, value in question.options.items():
                    option_text = self.safe_text(f"{key}. {value}")
                    story.append(Paragraph(option_text, self.option_style))

            story.append(Spacer(1, 6))

            # 正确答案
            answer_text = self.safe_text(f"答案: {question.correct_answer}")
            story.append(Paragraph(answer_text, self.answer_style))

            # 解析
            if question.explanation:
                explanation_text = self.safe_text(f"解析: {question.explanation}")
                story.append(Paragraph(explanation_text, self.explanation_style))
            
            # 题目间分隔线
            if i < len(questions):
                story.append(HRFlowable(width="100%", thickness=0.5, color=black))
                story.append(Spacer(1, 10))
        
        # 生成PDF
        doc.build(story)
        
        # 返回PDF内容
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_wrong_answers_pdf(self, user, wrong_answers=None):
        """生成错题集PDF"""
        buffer = io.BytesIO()
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 构建内容
        story = []
        
        # 添加标题
        title = self.safe_text(f"{user.username} - 错题集")
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 12))
        
        # 添加基本信息
        if not wrong_answers:
            from ..personal_quiz_models import WrongAnswer
            wrong_answers = WrongAnswer.objects.filter(user=user).order_by('-last_wrong_at')
        
        info_data = [
            [self.safe_text('用户名:'), self.safe_text(user.username)],
            [self.safe_text('错题数量:'), str(len(wrong_answers))],
            [self.safe_text('生成时间:'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        info_table = Table(info_data, colWidths=[3*cm, 12*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('BACKGROUND', (0, 0), (0, -1), '#f0f0f0'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # 添加错题
        for i, wrong_answer in enumerate(wrong_answers, 1):
            question = wrong_answer.question
            
            # 题目标题
            question_title = f"{i}. {question.title}"
            story.append(Paragraph(question_title, self.question_style))
            
            # 题目内容
            story.append(Paragraph(question.content, self.body_style))
            story.append(Spacer(1, 6))
            
            # 选项（选择题）
            if question.question_type in ['single_choice', 'multiple_choice']:
                for key, value in question.options.items():
                    option_text = f"{key}. {value}"
                    story.append(Paragraph(option_text, self.option_style))
            
            story.append(Spacer(1, 6))
            
            # 答案对比
            wrong_text = f"你的答案: {wrong_answer.wrong_answer}"
            story.append(Paragraph(wrong_text, ParagraphStyle(
                'WrongAnswer',
                parent=self.answer_style,
                textColor=red
            )))
            
            correct_text = f"正确答案: {wrong_answer.correct_answer}"
            story.append(Paragraph(correct_text, self.answer_style))
            
            # 错误次数和时间
            error_info = f"错误次数: {wrong_answer.wrong_count} | 最近错误: {wrong_answer.last_wrong_at.strftime('%Y-%m-%d %H:%M')}"
            story.append(Paragraph(error_info, ParagraphStyle(
                'ErrorInfo',
                parent=self.body_style,
                fontSize=8,
                textColor=black
            )))
            
            # 解析
            if question.explanation:
                explanation_text = f"解析: {question.explanation}"
                story.append(Paragraph(explanation_text, self.explanation_style))
            
            # AI分析
            if wrong_answer.ai_analysis:
                ai_text = f"AI分析: {wrong_answer.ai_analysis}"
                story.append(Paragraph(ai_text, ParagraphStyle(
                    'AIAnalysis',
                    parent=self.explanation_style,
                    textColor=blue
                )))
            
            # 学习建议
            if wrong_answer.study_suggestion:
                suggestion_text = f"学习建议: {wrong_answer.study_suggestion}"
                story.append(Paragraph(suggestion_text, ParagraphStyle(
                    'StudySuggestion',
                    parent=self.explanation_style,
                    textColor=blue
                )))
            
            # 题目间分隔线
            if i < len(wrong_answers):
                story.append(HRFlowable(width="100%", thickness=0.5, color=black))
                story.append(Spacer(1, 10))
        
        # 生成PDF
        doc.build(story)
        
        # 返回PDF内容
        buffer.seek(0)
        return buffer.getvalue()
    
    def create_pdf_response(self, pdf_content, filename):
        """创建PDF响应"""
        import urllib.parse

        # 处理中文文件名编码
        try:
            # 对文件名进行URL编码
            encoded_filename = urllib.parse.quote(filename.encode('utf-8'))

            response = HttpResponse(pdf_content, content_type='application/pdf')
            # 使用RFC 5987标准的文件名编码
            response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"

            # 同时提供fallback文件名（去掉中文字符）
            safe_filename = ''.join(c for c in filename if c.isascii() or c in '.-_')
            if not safe_filename or safe_filename.isspace():
                safe_filename = 'quiz_export.pdf'
            response['Content-Disposition'] += f'; filename="{safe_filename}"'

            return response

        except Exception as e:
            logger.error(f"Failed to encode filename: {e}")
            # 如果编码失败，使用安全的文件名
            safe_filename = 'quiz_export.pdf'
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
            return response


# 创建全局实例
pdf_generator = QuizPDFGenerator()
