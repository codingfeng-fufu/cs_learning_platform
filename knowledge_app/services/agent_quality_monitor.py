"""
Agent质量监控和验证系统
用于监控和验证AI生成内容的质量，减少幻觉问题
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)


class AgentQualityMonitor:
    """Agent质量监控器"""
    
    def __init__(self):
        # 常见的幻觉指标词汇
        self.hallucination_indicators = [
            # 具体数字和日期
            r'\d{4}年', r'\d+月\d+日', r'\d+\.\d+版本', r'\d+%的',
            # 具体人名和公司
            r'由.*发明', r'.*公司开发', r'.*教授提出',
            # 绝对化表述
            r'一定是', r'必须是', r'绝对', r'永远', r'从来不',
            # 未经证实的声明
            r'据统计', r'研究表明', r'实验证明', r'调查显示',
            # 具体的技术参数
            r'\d+位', r'\d+字节', r'\d+MHz', r'\d+GB',
        ]
        
        # 质量指标
        self.quality_indicators = [
            # 限定词（好的表现）
            r'通常', r'一般来说', r'大多数情况下', r'可能', r'往往',
            # 承认局限性
            r'需要进一步', r'具体实现可能', r'根据不同情况',
        ]
    
    def validate_exercise_quality(self, exercise: Dict) -> Tuple[bool, List[str]]:
        """验证练习题质量"""
        issues = []
        
        # 检查题目质量
        question = exercise.get('question', '')
        if self._has_hallucination_indicators(question):
            issues.append("题目包含可能不准确的具体信息")
        
        # 检查选项质量
        options = exercise.get('options', [])
        for i, option in enumerate(options):
            if self._has_hallucination_indicators(option):
                issues.append(f"选项{chr(65+i)}包含可能不准确的具体信息")
        
        # 检查解析质量
        explanation = exercise.get('explanation', '')
        if self._has_hallucination_indicators(explanation):
            issues.append("解析包含可能不准确的具体信息")
        
        # 检查答案合理性
        answer = exercise.get('answer', '')
        if answer not in ['A', 'B', 'C', 'D']:
            issues.append("答案格式不正确")
        
        # 检查选项重复
        option_texts = [opt.split('.', 1)[1].strip() if '.' in opt else opt for opt in options]
        if len(set(option_texts)) != len(option_texts):
            issues.append("选项存在重复内容")
        
        return len(issues) == 0, issues
    
    def validate_explanation_quality(self, term: str, explanation: str) -> Tuple[bool, List[str]]:
        """验证名词解释质量"""
        issues = []
        
        # 检查长度
        if len(explanation) < 50:
            issues.append("解释过短，可能不够详细")
        elif len(explanation) > 800:
            issues.append("解释过长，可能包含不必要的细节")
        
        # 检查幻觉指标
        if self._has_hallucination_indicators(explanation):
            issues.append("解释包含可能不准确的具体信息")
        
        # 检查是否包含名词本身
        if term not in explanation:
            issues.append("解释中未包含要解释的名词")
        
        # 检查结构完整性
        structure_keywords = ['定义', '特点', '用途', '应用', '作用', '原理', '方法']
        has_structure = any(keyword in explanation for keyword in structure_keywords)
        if not has_structure:
            issues.append("解释缺乏结构化内容")
        
        # 检查质量指标
        quality_score = self._calculate_quality_score(explanation)
        if quality_score < 0.3:
            issues.append("解释质量评分较低，可能存在问题")
        
        return len(issues) == 0, issues
    
    def validate_chat_response_quality(self, response: str, context: str) -> Tuple[bool, List[str]]:
        """验证聊天回复质量"""
        issues = []
        
        # 检查长度
        if len(response) < 20:
            issues.append("回复过短")
        elif len(response) > 600:
            issues.append("回复过长")
        
        # 检查幻觉指标
        if self._has_hallucination_indicators(response):
            issues.append("回复包含可能不准确的具体信息")
        
        # 检查是否与上下文相关
        if context and not self._is_contextually_relevant(response, context):
            issues.append("回复与上下文相关性较低")
        
        # 检查是否承认局限性
        has_limitations = any(indicator in response for indicator in [
            '根据给定', '需要进一步', '可能需要', '建议查阅', '具体情况'
        ])
        
        quality_score = self._calculate_quality_score(response)
        if quality_score < 0.4:
            issues.append("回复质量评分较低")
        
        return len(issues) == 0, issues
    
    def _has_hallucination_indicators(self, text: str) -> bool:
        """检查文本是否包含幻觉指标"""
        for pattern in self.hallucination_indicators:
            if re.search(pattern, text):
                return True
        return False
    
    def _calculate_quality_score(self, text: str) -> float:
        """计算文本质量评分"""
        score = 0.5  # 基础分
        
        # 正面指标
        for pattern in self.quality_indicators:
            if re.search(pattern, text):
                score += 0.1
        
        # 负面指标
        for pattern in self.hallucination_indicators:
            if re.search(pattern, text):
                score -= 0.2
        
        # 长度适中加分
        if 100 <= len(text) <= 400:
            score += 0.1
        
        # 结构化内容加分
        if '。' in text and text.count('。') >= 2:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _is_contextually_relevant(self, response: str, context: str) -> bool:
        """检查回复与上下文的相关性"""
        # 简单的关键词匹配检查
        context_words = set(re.findall(r'\w+', context.lower()))
        response_words = set(re.findall(r'\w+', response.lower()))
        
        # 计算交集比例
        if len(context_words) == 0:
            return True
        
        intersection = context_words.intersection(response_words)
        relevance_ratio = len(intersection) / len(context_words)
        
        return relevance_ratio > 0.1  # 至少10%的词汇重叠
    
    def log_quality_issue(self, agent_type: str, content_type: str, issues: List[str], content: str = ""):
        """记录质量问题"""
        timestamp = timezone.now()
        
        logger.warning(f"Quality issues detected - Agent: {agent_type}, Type: {content_type}")
        for issue in issues:
            logger.warning(f"  - {issue}")
        
        if content:
            logger.debug(f"Content: {content[:200]}...")
    
    def get_quality_report(self, agent_type: str, period_days: int = 7) -> Dict:
        """生成质量报告"""
        # 这里可以扩展为从数据库中统计质量数据
        return {
            'agent_type': agent_type,
            'period_days': period_days,
            'total_generated': 0,
            'quality_issues': 0,
            'quality_rate': 0.0,
            'common_issues': [],
            'recommendations': self._get_quality_recommendations(agent_type)
        }
    
    def _get_quality_recommendations(self, agent_type: str) -> List[str]:
        """获取质量改进建议"""
        recommendations = {
            'exercise_generator': [
                "使用更保守的temperature设置",
                "增加题目验证步骤",
                "避免生成具体的技术参数",
                "加强选项差异性检查"
            ],
            'term_explainer': [
                "使用领域上下文限制生成范围",
                "增加解释结构化要求",
                "避免具体的历史细节",
                "加强概念准确性验证"
            ],
            'chatbot': [
                "基于给定上下文进行回复",
                "承认知识局限性",
                "使用限定词避免绝对化表述",
                "鼓励用户进一步学习"
            ]
        }
        
        return recommendations.get(agent_type, [])


# 全局质量监控器实例
quality_monitor = AgentQualityMonitor()
