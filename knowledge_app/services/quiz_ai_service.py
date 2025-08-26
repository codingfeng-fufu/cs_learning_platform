"""
个人题库AI分析服务
基于GLM4.5提供智能错题分析和学习建议
"""

import json
import logging
from typing import Dict, List, Optional, Any
from django.utils import timezone
from .glm_chatbot_service import GLMChatbotClient

logger = logging.getLogger(__name__)


class QuizAIAnalyzer:
    """题库AI分析器"""
    
    def __init__(self):
        self.client = GLMChatbotClient()
    
    def analyze_wrong_answer(self, wrong_answer_data: Dict) -> Dict[str, Any]:
        """分析单个错题"""
        try:
            question = wrong_answer_data['question']
            user_answer = wrong_answer_data['user_answer']
            correct_answer = wrong_answer_data['correct_answer']
            question_type = wrong_answer_data.get('question_type', '')
            
            # 构建分析提示
            prompt = self._build_wrong_answer_prompt(
                question, user_answer, correct_answer, question_type
            )
            
            messages = [
                {
                    "role": "system", 
                    "content": "你是一位经验丰富的计算机科学教师，擅长分析学生的错误并提供针对性的学习建议。"
                },
                {"role": "user", "content": prompt}
            ]
            
            response = self.client._make_request(messages, max_tokens=800, temperature=0.3)
            
            if response:
                # 解析AI回复
                analysis_result = self._parse_analysis_response(response)
                return {
                    'success': True,
                    'analysis': analysis_result.get('analysis', ''),
                    'suggestion': analysis_result.get('suggestion', ''),
                    'raw_response': response
                }
            else:
                return {
                    'success': False,
                    'error': 'AI分析服务暂时不可用'
                }
                
        except Exception as e:
            logger.error(f"Wrong answer analysis failed: {e}")
            return {
                'success': False,
                'error': f'分析失败：{str(e)}'
            }
    
    def analyze_session_performance(self, session_data: Dict) -> Dict[str, Any]:
        """分析整个练习会话的表现"""
        try:
            # 构建会话分析提示
            prompt = self._build_session_analysis_prompt(session_data)
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一位专业的学习分析师，擅长从学生的答题表现中发现学习模式和提供改进建议。"
                },
                {"role": "user", "content": prompt}
            ]
            
            response = self.client._make_request(messages, max_tokens=1000, temperature=0.4)
            
            if response:
                analysis_result = self._parse_session_analysis_response(response)
                return {
                    'success': True,
                    'overall_analysis': analysis_result.get('overall_analysis', ''),
                    'strengths': analysis_result.get('strengths', []),
                    'weaknesses': analysis_result.get('weaknesses', []),
                    'suggestions': analysis_result.get('suggestions', []),
                    'next_steps': analysis_result.get('next_steps', []),
                    'raw_response': response
                }
            else:
                return {
                    'success': False,
                    'error': 'AI分析服务暂时不可用'
                }
                
        except Exception as e:
            logger.error(f"Session analysis failed: {e}")
            return {
                'success': False,
                'error': f'分析失败：{str(e)}'
            }
    
    def _build_wrong_answer_prompt(self, question: str, user_answer: str, 
                                 correct_answer: str, question_type: str) -> str:
        """构建错题分析提示"""
        type_map = {
            'single_choice': '单选题',
            'multiple_choice': '多选题',
            'fill_blank': '填空题',
            'short_answer': '简答题'
        }
        
        question_type_zh = type_map.get(question_type, '题目')
        
        prompt = f"""请分析以下错题情况，并提供学习建议：

题目类型：{question_type_zh}
题目内容：{question}
学生答案：{user_answer}
正确答案：{correct_answer}

请从以下几个方面进行分析：

1. 错误原因分析：
   - 分析学生可能的思维误区
   - 指出知识点理解上的偏差
   - 识别答题技巧上的问题

2. 知识点梳理：
   - 涉及的核心概念
   - 相关的基础知识
   - 容易混淆的概念

3. 学习建议：
   - 针对性的复习重点
   - 推荐的学习方法
   - 类似题目的练习建议

请用简洁明了的语言回答，分为"错误分析"和"学习建议"两个部分，每部分控制在100字以内。

格式要求：
错误分析：[你的分析内容]
学习建议：[你的建议内容]"""

        return prompt
    
    def _build_session_analysis_prompt(self, session_data: Dict) -> str:
        """构建会话分析提示"""
        total_questions = session_data.get('total_questions', 0)
        correct_answers = session_data.get('correct_answers', 0)
        accuracy = session_data.get('accuracy', 0)
        wrong_answers = session_data.get('wrong_answers', [])
        type_stats = session_data.get('type_stats', {})
        
        # 构建错题摘要
        wrong_summary = []
        for wrong in wrong_answers[:5]:  # 最多分析5道错题
            wrong_summary.append(f"- {wrong.get('question_title', '题目')}: 答案{wrong.get('user_answer', '')} → 正确答案{wrong.get('correct_answer', '')}")
        
        # 构建题型表现摘要
        type_performance = []
        for type_name, stats in type_stats.items():
            type_performance.append(f"- {type_name}: {stats.get('correct', 0)}/{stats.get('total', 0)}题正确 ({stats.get('accuracy', 0)}%)")
        
        prompt = f"""请分析以下学习会话的表现，并提供个性化建议：

练习概况：
- 总题数：{total_questions}题
- 正确数：{correct_answers}题
- 正确率：{accuracy}%

题型表现：
{chr(10).join(type_performance) if type_performance else '- 暂无详细统计'}

主要错题：
{chr(10).join(wrong_summary) if wrong_summary else '- 无错题'}

请从以下方面进行分析：

1. 整体表现评价（50字以内）
2. 优势领域（列出2-3个强项）
3. 薄弱环节（列出2-3个需要改进的方面）
4. 学习建议（3-4条具体建议）
5. 下一步学习计划（2-3个行动建议）

请用简洁的语言回答，每个方面都要具体明确。

格式要求：
整体评价：[评价内容]
优势领域：[强项1] | [强项2] | [强项3]
薄弱环节：[薄弱点1] | [薄弱点2] | [薄弱点3]
学习建议：[建议1] | [建议2] | [建议3] | [建议4]
下一步计划：[计划1] | [计划2] | [计划3]"""

        return prompt
    
    def _parse_analysis_response(self, response: str) -> Dict[str, str]:
        """解析错题分析回复"""
        result = {'analysis': '', 'suggestion': ''}
        
        try:
            lines = response.strip().split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('错误分析：'):
                    current_section = 'analysis'
                    result['analysis'] = line.replace('错误分析：', '').strip()
                elif line.startswith('学习建议：'):
                    current_section = 'suggestion'
                    result['suggestion'] = line.replace('学习建议：', '').strip()
                elif current_section and line:
                    result[current_section] += ' ' + line
            
            # 如果没有找到标准格式，尝试简单分割
            if not result['analysis'] and not result['suggestion']:
                parts = response.split('学习建议')
                if len(parts) >= 2:
                    result['analysis'] = parts[0].replace('错误分析', '').strip('：').strip()
                    result['suggestion'] = parts[1].strip('：').strip()
                else:
                    # 如果都没有，将整个回复作为分析
                    result['analysis'] = response[:200]
                    result['suggestion'] = '建议多练习相关题目，加强基础知识理解。'
                    
        except Exception as e:
            logger.warning(f"Failed to parse analysis response: {e}")
            result['analysis'] = response[:200] if response else '分析内容解析失败'
            result['suggestion'] = '建议多练习相关题目，加强基础知识理解。'
        
        return result
    
    def _parse_session_analysis_response(self, response: str) -> Dict[str, Any]:
        """解析会话分析回复"""
        result = {
            'overall_analysis': '',
            'strengths': [],
            'weaknesses': [],
            'suggestions': [],
            'next_steps': []
        }
        
        try:
            lines = response.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('整体评价：'):
                    result['overall_analysis'] = line.replace('整体评价：', '').strip()
                elif line.startswith('优势领域：'):
                    strengths_text = line.replace('优势领域：', '').strip()
                    result['strengths'] = [s.strip() for s in strengths_text.split('|') if s.strip()]
                elif line.startswith('薄弱环节：'):
                    weaknesses_text = line.replace('薄弱环节：', '').strip()
                    result['weaknesses'] = [w.strip() for w in weaknesses_text.split('|') if w.strip()]
                elif line.startswith('学习建议：'):
                    suggestions_text = line.replace('学习建议：', '').strip()
                    result['suggestions'] = [s.strip() for s in suggestions_text.split('|') if s.strip()]
                elif line.startswith('下一步计划：'):
                    next_steps_text = line.replace('下一步计划：', '').strip()
                    result['next_steps'] = [n.strip() for n in next_steps_text.split('|') if n.strip()]
            
            # 提供默认值
            if not result['overall_analysis']:
                result['overall_analysis'] = '本次练习表现良好，继续保持学习热情。'
            if not result['suggestions']:
                result['suggestions'] = ['多做练习题', '复习基础知识', '总结错题规律']
                
        except Exception as e:
            logger.warning(f"Failed to parse session analysis response: {e}")
            result['overall_analysis'] = '分析内容解析失败，建议继续练习。'
            result['suggestions'] = ['多做练习题', '复习基础知识', '总结错题规律']
        
        return result
    
    def is_available(self) -> bool:
        """检查AI服务是否可用"""
        return bool(self.client.api_key)


# 创建全局实例
quiz_ai_analyzer = QuizAIAnalyzer()
