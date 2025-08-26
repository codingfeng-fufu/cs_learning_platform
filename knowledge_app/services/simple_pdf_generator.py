"""
简化的PDF生成器，专门处理中文编码问题
使用纯英文标签和ASCII字符，确保兼容性
"""

import io
from datetime import datetime
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import black, blue, red, green
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import logging

logger = logging.getLogger(__name__)


class SimplePDFGenerator:
    """简化的PDF生成器"""
    
    def __init__(self):
        self.setup_styles()
    
    def setup_styles(self):
        """设置样式"""
        self.styles = getSampleStyleSheet()
        
        # 使用Helvetica字体，确保兼容性
        self.font_name = 'Helvetica'
        
        # 标题样式
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontName=self.font_name,
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=black
        )
        
        # 副标题样式
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontName=self.font_name,
            fontSize=14,
            spaceAfter=12,
            textColor=blue
        )
        
        # 正文样式
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=10,
            spaceAfter=8,
            alignment=TA_LEFT
        )
        
        # 题目样式
        self.question_style = ParagraphStyle(
            'QuestionStyle',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=11,
            spaceAfter=6,
            leftIndent=0
        )
        
        # 选项样式
        self.option_style = ParagraphStyle(
            'OptionStyle',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=10,
            spaceAfter=3,
            leftIndent=20
        )
        
        # 答案样式
        self.answer_style = ParagraphStyle(
            'AnswerStyle',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=10,
            spaceAfter=6,
            textColor=green
        )
    
    def safe_text(self, text):
        """安全处理文本，保留中文但使用拼音标注"""
        if not text:
            return ""

        if not isinstance(text, str):
            text = str(text)

        # 只替换标签性的中文词汇，保留题目内容
        label_translations = {
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
            '题库名称': 'Library Name',
            '题库描述': 'Description',
            '用户名': 'Username',
            '错题数量': 'Wrong Answer Count',
            '错误次数': 'Wrong Count',
            '最近错误': 'Last Wrong',
            'AI分析': 'AI Analysis',
            '学习建议': 'Study Suggestion',
            '单选题': 'Single Choice',
            '多选题': 'Multiple Choice',
            '填空题': 'Fill Blank',
            '简答题': 'Short Answer',
            '简单': 'Easy',
            '中等': 'Medium',
            '困难': 'Hard'
        }

        # 只替换标签词汇
        for chinese, english in label_translations.items():
            text = text.replace(chinese, english)

        # 对于剩余的中文内容，尝试使用拼音
        try:
            import re
            chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
            chinese_matches = chinese_pattern.findall(text)

            if chinese_matches:
                # 尝试使用简单的拼音映射
                pinyin_map = self.get_simple_pinyin_map()

                for chinese_word in chinese_matches:
                    # 尝试转换为拼音
                    pinyin_result = self.chinese_to_pinyin(chinese_word, pinyin_map)
                    if pinyin_result != chinese_word:  # 如果转换成功
                        text = text.replace(chinese_word, pinyin_result)
                    else:
                        # 如果无法转换，保留原文但添加标注
                        text = text.replace(chinese_word, f"{chinese_word}(Chinese)")
        except Exception as e:
            # 如果拼音转换失败，保留原文
            pass

        # HTML转义
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')

        return text

    def get_simple_pinyin_map(self):
        """获取简单的拼音映射表"""
        return {
            # 常用计算机术语
            '数组': 'shuzu(array)',
            '访问': 'fangwen(access)',
            '元素': 'yuansu(element)',
            '时间': 'shijian(time)',
            '复杂度': 'fuzadu(complexity)',
            '栈': 'zhan(stack)',
            '队列': 'duilie(queue)',
            '链表': 'lianbiao(linkedlist)',
            '树': 'shu(tree)',
            '图': 'tu(graph)',
            '算法': 'suanfa(algorithm)',
            '排序': 'paixu(sort)',
            '查找': 'chazhao(search)',
            '插入': 'charu(insert)',
            '删除': 'shanchu(delete)',
            '更新': 'gengxin(update)',
            '数据': 'shuju(data)',
            '结构': 'jiegou(structure)',
            '网络': 'wangluo(network)',
            '协议': 'xieyi(protocol)',
            '服务器': 'fuwuqi(server)',
            '客户端': 'kehuduan(client)',
            '数据库': 'shujuku(database)',
            '表': 'biao(table)',
            '字段': 'ziduan(field)',
            '索引': 'suoyin(index)',
            '查询': 'chaxun(query)',
            '操作系统': 'caozuoxitong(OS)',
            '进程': 'jincheng(process)',
            '线程': 'xiancheng(thread)',
            '内存': 'neicun(memory)',
            '文件': 'wenjian(file)',
            '目录': 'mulu(directory)',
            '权限': 'quanxian(permission)',
        }

    def chinese_to_pinyin(self, text, pinyin_map):
        """简单的中文转拼音"""
        result = text
        for chinese, pinyin in pinyin_map.items():
            result = result.replace(chinese, pinyin)
        return result
    
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
        title = self.safe_text(f"{library.name} - Question Bank")
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 12))
        
        # 基本信息
        info_data = [
            ['Library Name:', self.safe_text(library.name)],
            ['Created Time:', library.created_at.strftime('%Y-%m-%d %H:%M')],
            ['Question Count:', str(library.total_questions)],
            ['Generated Time:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        if library.description:
            info_data.insert(1, ['Description:', self.safe_text(library.description)])
        
        info_table = Table(info_data, colWidths=[4*cm, 11*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('BACKGROUND', (0, 0), (0, -1), '#f0f0f0'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # 题目
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
            
            # 答案
            answer_text = self.safe_text(f"Answer: {question.correct_answer}")
            story.append(Paragraph(answer_text, self.answer_style))
            
            # 解析
            if question.explanation:
                explanation_text = self.safe_text(f"Explanation: {question.explanation}")
                story.append(Paragraph(explanation_text, self.body_style))
            
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
        title = self.safe_text(f"{user.username} - Wrong Answers Collection")
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 12))
        
        # 基本信息
        if not wrong_answers:
            from ..personal_quiz_models import WrongAnswer
            wrong_answers = WrongAnswer.objects.filter(user=user).order_by('-last_wrong_at')
        
        info_data = [
            ['Username:', self.safe_text(user.username)],
            ['Wrong Answer Count:', str(len(wrong_answers))],
            ['Generated Time:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 11*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            ('BACKGROUND', (0, 0), (0, -1), '#f0f0f0'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # 错题
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
            wrong_text = self.safe_text(f"Your Answer: {wrong_answer.wrong_answer}")
            story.append(Paragraph(wrong_text, ParagraphStyle(
                'WrongAnswer', parent=self.answer_style, textColor=red
            )))
            
            correct_text = self.safe_text(f"Correct Answer: {wrong_answer.correct_answer}")
            story.append(Paragraph(correct_text, self.answer_style))
            
            # 错误信息
            error_info = f"Wrong Count: {wrong_answer.wrong_count} | Last Wrong: {wrong_answer.last_wrong_at.strftime('%Y-%m-%d %H:%M')}"
            story.append(Paragraph(error_info, self.body_style))
            
            # 解析和AI分析
            if question.explanation:
                explanation_text = self.safe_text(f"Explanation: {question.explanation}")
                story.append(Paragraph(explanation_text, self.body_style))
            
            if wrong_answer.ai_analysis:
                ai_text = self.safe_text(f"AI Analysis: {wrong_answer.ai_analysis}")
                story.append(Paragraph(ai_text, ParagraphStyle(
                    'AIAnalysis', parent=self.body_style, textColor=blue
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
simple_pdf_generator = SimplePDFGenerator()
