"""
中文PDF生成器
专门处理中文内容的PDF生成，确保中文正确显示
"""

import io
import os
from datetime import datetime
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import black, blue, red, green, orange
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging

logger = logging.getLogger(__name__)


class ChinesePDFGenerator:
    """中文PDF生成器"""
    
    def __init__(self):
        self.setup_chinese_font()
        self.setup_styles()
    
    def setup_chinese_font(self):
        """设置中文字体"""
        try:
            # Windows系统中文字体路径
            font_paths = [
                "C:/Windows/Fonts/simhei.ttf",    # 黑体
                "C:/Windows/Fonts/simsun.ttc",    # 宋体
                "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
                "C:/Windows/Fonts/simkai.ttf",    # 楷体
            ]
            
            self.chinese_font = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        self.chinese_font = 'ChineseFont'
                        logger.info(f"Successfully registered Chinese font: {font_path}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to register font {font_path}: {e}")
                        continue
            
            if not self.chinese_font:
                # 如果没有找到中文字体，使用Helvetica
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
            'ChineseTitle',
            parent=self.styles['Title'],
            fontName=self.chinese_font,
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=black
        )
        
        # 副标题样式
        self.subtitle_style = ParagraphStyle(
            'ChineseSubtitle',
            parent=self.styles['Heading2'],
            fontName=self.chinese_font,
            fontSize=14,
            spaceAfter=12,
            textColor=blue
        )
        
        # 正文样式
        self.body_style = ParagraphStyle(
            'ChineseBody',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=11,
            spaceAfter=8,
            alignment=TA_LEFT,
            leading=16
        )
        
        # 题目样式
        self.question_style = ParagraphStyle(
            'ChineseQuestion',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=12,
            spaceAfter=6,
            leftIndent=0,
            textColor=black,
            leading=18
        )
        
        # 选项样式
        self.option_style = ParagraphStyle(
            'ChineseOption',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=11,
            spaceAfter=3,
            leftIndent=20,
            leading=16
        )
        
        # 答案样式
        self.answer_style = ParagraphStyle(
            'ChineseAnswer',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=11,
            spaceAfter=6,
            textColor=green,
            leading=16
        )
        
        # 错误答案样式
        self.wrong_answer_style = ParagraphStyle(
            'ChineseWrongAnswer',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=11,
            spaceAfter=6,
            textColor=red,
            leading=16
        )
        
        # 解析样式
        self.explanation_style = ParagraphStyle(
            'ChineseExplanation',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            spaceAfter=10,
            leftIndent=10,
            textColor=black,
            leading=14
        )
    
    def safe_text(self, text):
        """安全处理文本"""
        if not text:
            return ""
        
        if not isinstance(text, str):
            text = str(text)
        
        # 如果使用Helvetica字体，需要处理中文
        if self.chinese_font == 'Helvetica':
            # 将中文转换为拼音或英文
            text = self.convert_chinese_to_english(text)
        
        # HTML转义
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        return text
    
    def convert_chinese_to_english(self, text):
        """将中文转换为英文"""
        translations = {
            # 基本词汇
            '题库': 'Question Bank',
            '错题集': 'Wrong Answer Collection',
            '题目': 'Question',
            '答案': 'Answer',
            '正确答案': 'Correct Answer',
            '你的答案': 'Your Answer',
            '错误答案': 'Wrong Answer',
            '解析': 'Explanation',
            '选项': 'Options',
            '创建时间': 'Created Time',
            '生成时间': 'Generated Time',
            '题目数量': 'Question Count',
            '错题数量': 'Wrong Answer Count',
            '用户名': 'Username',
            '错误次数': 'Wrong Count',
            '最近错误': 'Last Wrong',
            '学习建议': 'Study Suggestion',
            '分析': 'Analysis',
            
            # 计算机术语
            '数组': 'Array',
            '访问': 'Access',
            '元素': 'Element',
            '时间复杂度': 'Time Complexity',
            '栈': 'Stack',
            '队列': 'Queue',
            '链表': 'Linked List',
            '二分查找': 'Binary Search',
            '排序': 'Sort',
            '算法': 'Algorithm',
            '数据结构': 'Data Structure',
            '网络': 'Network',
            '协议': 'Protocol',
            '数据库': 'Database',
            '操作系统': 'Operating System',
            '进程': 'Process',
            '线程': 'Thread',
            '内存': 'Memory',
            
            # 其他常用词
            '在': 'In',
            '中': 'in',
            '的': 'of',
            '是': 'is',
            '个': '',
            '第': 'No.',
            '道': '',
            '次': 'times',
            '年': 'Year',
            '月': 'Month',
            '日': 'Day',
            '时': 'Hour',
            '分': 'Minute',
        }
        
        # 替换已知的中文词汇
        for chinese, english in translations.items():
            text = text.replace(chinese, english)
        
        # 处理剩余的中文字符
        import re
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        matches = chinese_pattern.findall(text)
        
        for match in matches:
            # 为未翻译的中文添加标注
            text = text.replace(match, f'[{match}]')
        
        return text
    
    def generate_library_pdf(self, library, questions=None):
        """生成题库PDF"""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # 标题
        title = self.safe_text(f"{library.name} - 题库")
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 12))
        
        # 基本信息表格
        info_data = [
            [self.safe_text('题库名称:'), self.safe_text(library.name)],
            [self.safe_text('创建时间:'), library.created_at.strftime('%Y-%m-%d %H:%M')],
            [self.safe_text('题目数量:'), f"{library.total_questions} 道"],
            [self.safe_text('生成时间:'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        if library.description:
            info_data.insert(1, [self.safe_text('题库描述:'), self.safe_text(library.description)])
        
        info_table = Table(info_data, colWidths=[4*cm, 11*cm])
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
        
        # 题目列表
        if not questions:
            questions = library.questions.all().order_by('created_at')
        
        for i, question in enumerate(questions, 1):
            # 题目标题
            question_title = self.safe_text(f"{i}. {question.title}")
            story.append(Paragraph(question_title, self.question_style))
            
            # 题目内容
            story.append(Paragraph(self.safe_text(question.content), self.body_style))
            story.append(Spacer(1, 6))
            
            # 选项
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
            
            # 分隔线
            if i < len(questions):
                story.append(HRFlowable(width="100%", thickness=0.5, color=black))
                story.append(Spacer(1, 10))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_wrong_answers_pdf(self, user, wrong_answers=None):
        """生成错题集PDF"""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # 标题
        title = self.safe_text(f"{user.username} - 错题集")
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 12))
        
        # 基本信息
        if not wrong_answers:
            from ..personal_quiz_models import WrongAnswer
            wrong_answers = WrongAnswer.objects.filter(user=user).order_by('-last_wrong_at')
        
        info_data = [
            [self.safe_text('用户名:'), self.safe_text(user.username)],
            [self.safe_text('错题数量:'), f"{len(wrong_answers)} 道"],
            [self.safe_text('生成时间:'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 11*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('BACKGROUND', (0, 0), (0, -1), '#ffebee'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # 错题列表
        for i, wrong_answer in enumerate(wrong_answers, 1):
            question = wrong_answer.question
            
            # 题目标题
            question_title = self.safe_text(f"{i}. {question.title}")
            story.append(Paragraph(question_title, self.question_style))
            
            # 题目内容
            story.append(Paragraph(self.safe_text(question.content), self.body_style))
            story.append(Spacer(1, 6))
            
            # 选项
            if question.question_type in ['single_choice', 'multiple_choice']:
                for key, value in question.options.items():
                    option_text = self.safe_text(f"{key}. {value}")
                    story.append(Paragraph(option_text, self.option_style))
            
            story.append(Spacer(1, 6))
            
            # 答案对比
            wrong_text = self.safe_text(f"你的答案: {wrong_answer.wrong_answer}")
            story.append(Paragraph(wrong_text, self.wrong_answer_style))
            
            correct_text = self.safe_text(f"正确答案: {wrong_answer.correct_answer}")
            story.append(Paragraph(correct_text, self.answer_style))
            
            # 错误信息
            error_info = self.safe_text(f"错误次数: {wrong_answer.wrong_count} 次 | 最近错误: {wrong_answer.last_wrong_at.strftime('%Y-%m-%d %H:%M')}")
            story.append(Paragraph(error_info, self.body_style))
            
            # 解析
            if question.explanation:
                explanation_text = self.safe_text(f"解析: {question.explanation}")
                story.append(Paragraph(explanation_text, self.explanation_style))
            
            # AI分析
            if wrong_answer.ai_analysis:
                ai_text = self.safe_text(f"AI分析: {wrong_answer.ai_analysis}")
                story.append(Paragraph(ai_text, ParagraphStyle(
                    'AIAnalysis', parent=self.explanation_style, textColor=blue
                )))
            
            # 学习建议
            if wrong_answer.study_suggestion:
                suggestion_text = self.safe_text(f"学习建议: {wrong_answer.study_suggestion}")
                story.append(Paragraph(suggestion_text, ParagraphStyle(
                    'StudySuggestion', parent=self.explanation_style, textColor=orange
                )))
            
            # 分隔线
            if i < len(wrong_answers):
                story.append(HRFlowable(width="100%", thickness=0.5, color=black))
                story.append(Spacer(1, 10))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def create_pdf_response(self, pdf_content, filename):
        """创建PDF响应"""
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# 创建全局实例
chinese_pdf_generator = ChinesePDFGenerator()
