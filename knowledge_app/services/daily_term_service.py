"""
每日计算机名词解释服务
负责与kimi API交互，获取和处理每日名词
"""

import requests
import json
import logging
import time
import random
import pytz
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, Tuple
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

from ..models import DailyTerm, TermHistory
from .domain_scheduler import domain_scheduler, build_domain_specific_prompt
from .agent_quality_monitor import quality_monitor

logger = logging.getLogger(__name__)


class KimiAPIClient:
    """Kimi API客户端"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'KIMI_API_KEY', 'sk-x2Ao6ONLlSycGnrkQwUtRT4Hysay2DSHPmFT9HHrt1Wi7ADb')
        self.base_url = getattr(settings, 'KIMI_API_URL', 'https://api.moonshot.cn/v1/chat/completions')
        self.model = getattr(settings, 'KIMI_MODEL', 'moonshot-v1-8k')
        self.timeout = 30
        self.max_retries = 3
    
    def _make_request(self, messages: list, max_tokens: int = 1000, temperature: float = 0.7) -> Optional[str]:
        """发送API请求"""
        if not self.api_key:
            logger.error("Kimi API key not configured")
            return None
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        data = {
            'model': self.model,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    logger.warning(f"API request failed with status {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"API request error (attempt {attempt + 1}): {e}")
                
            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
        
        return None
    
    def get_computer_term(self, target_date: date = None) -> Optional[str]:
        """获取一个计算机相关的名词（基于当前领域）"""

        # 获取当前日期的领域信息
        if target_date is None:
            target_date = timezone.now().date()

        domain_info = domain_scheduler.get_domain_info(target_date)
        domain = domain_info['domain']

        # 获取最近使用过的名词，避免重复
        recent_terms = DailyTerm.objects.filter(
            status='active',
            display_date__gte=target_date - timedelta(days=30)
        ).values_list('term', flat=True)

        recent_terms_str = ', '.join(recent_terms) if recent_terms else '无'

        # 构建高质量的领域特定提示词
        prompt = f"""你是一位资深的计算机科学教育专家，请从{domain['name']}领域中精心选择一个最适合今日学习的专业名词。

🎯 **目标领域**：{domain['name']}
📝 **领域描述**：{domain['description']}
🔑 **核心关键词**：{', '.join(domain['keywords'][:8])}
💡 **典型示例**：{', '.join(domain['examples'][:5])}

⚠️ **避免重复**（最近30天已使用）：{recent_terms_str}

🎓 **选择标准**：
1. **教育价值高**：对计算机专业学生具有重要学习意义
2. **实用性强**：在实际工作中经常遇到或使用
3. **概念清晰**：有明确定义，不会产生歧义
4. **难度适中**：既不过于基础（如"文件"、"程序"），也不过于高深
5. **领域代表性**：能很好地代表{domain['name']}领域的特色
6. **知识连接性**：能与其他计算机概念形成良好的知识链接

🎯 **优先选择类型**：
- 核心算法和数据结构
- 重要设计模式和架构
- 关键技术和协议
- 标准化概念和方法
- 性能优化技术
- 安全相关概念

📋 **输出要求**：
- 只返回一个精确的中文名词
- 如果是英文缩写，提供中文全称（如：HTTP → 超文本传输协议）
- 不要包含任何解释、标点或额外文字
- 确保名词在{domain['name']}领域中具有代表性

请基于以上要求，选择一个最佳的专业名词："""

        messages = [
            {
                "role": "system",
                "content": f"你是一个{domain['name']}领域的教育专家，专门为计算机专业学生选择合适的学习名词。请基于给定的领域信息和示例，选择一个具体、准确、有教育价值的专业名词。"
            },
            {"role": "user", "content": prompt}
        ]

        response = self._make_request(messages, max_tokens=30, temperature=0.8)  # 增加随机性避免重复

        if response:
            # 清理响应，只保留名词
            term = response.strip().strip('。').strip('"').strip("'").strip('：').strip(':').strip('、')

            # 更严格的验证
            if self._validate_term(term, domain):
                logger.info(f"Generated term for {domain['name']}: {term}")
                return term
            else:
                logger.warning(f"Invalid term generated: {term}")

        return None

    def _validate_term(self, term: str, domain: Dict) -> bool:
        """验证生成的名词是否合理"""
        # 基本格式检查
        if not term or len(term) < 1 or len(term) > 25:
            return False

        # 排除明显无效的内容
        invalid_patterns = ['？', '?', '请', '是一个', '名词', '概念是', '技术是', '方法是']
        if any(pattern in term for pattern in invalid_patterns):
            return False

        # 排除过于通用的词汇（但允许专业术语）
        generic_terms = ['计算机', '软件', '硬件', '信息', '程序']
        if term in generic_terms:
            return False

        # 检查是否包含领域相关的关键词
        domain_keywords = [kw.lower() for kw in domain['keywords']]
        term_lower = term.lower()

        # 如果名词中包含领域关键词，增加可信度
        has_domain_keyword = any(keyword in term_lower for keyword in domain_keywords)

        # 检查是否在示例中
        is_in_examples = term in domain['examples']

        # 如果在示例中或包含领域关键词，认为是有效的
        if is_in_examples or has_domain_keyword:
            return True

        # 允许常见的计算机专业术语（即使很短）
        valid_short_terms = ['堆', '栈', '树', '图', 'CPU', 'GPU', 'RAM', 'API', 'SQL', 'TCP', 'UDP', 'DNS', 'HTTP', 'FTP']
        if term in valid_short_terms:
            return True

        # 其他情况下，进行长度检查（允许2个字符以上）
        return 2 <= len(term) <= 15
    
    def get_term_explanation(self, term: str, target_date: date = None) -> Optional[Dict[str, Any]]:
        """获取名词的详细解释"""

        # 获取当前领域信息以提供更准确的上下文
        if target_date is None:
            target_date = timezone.now().date()

        domain_info = domain_scheduler.get_domain_info(target_date)
        domain = domain_info['domain']

        prompt = f"""你是一位优秀的计算机科学教育专家，请为"{term}"这个专业名词提供一份高质量的学习解释。

🎯 **目标名词**：{term}
📚 **所属领域**：{domain['name']} - {domain['description']}
🔗 **相关概念**：{', '.join(domain['keywords'][:6])}

请按照以下结构提供专业而易懂的解释：

## 📖 核心概念
用清晰准确的语言解释这个概念的本质含义，确保：
- 定义准确且完整
- 语言通俗易懂，避免循环定义
- 突出概念的核心特征和价值
- 字数：100-150字

## 🔤 术语信息
提供完整的术语信息：
- 英文名称（全称和常用缩写）
- 中文别名（如果有）
- 相关术语对比（如果适用）

## 🛠️ 工作原理
简要说明这个概念的工作机制或实现原理：
- 基本工作流程
- 关键技术要点
- 与其他概念的关系
- 字数：80-120字

## 💡 实际应用
列举3-4个具体的应用场景，要求：
- 应用场景要具体且贴近实际
- 每个场景说明其作用和价值
- 涵盖不同层面的应用
- 每个场景40-60字

## 🎓 学习要点
为学习者提供关键的学习建议：
- 理解这个概念需要掌握的前置知识
- 学习过程中的重点和难点
- 与其他知识点的联系
- 字数：60-80字

📋 **写作要求**：
1. 语言专业但不晦涩，适合计算机专业学生
2. 内容准确，避免过时或错误信息
3. 结构清晰，逻辑性强
4. 总字数控制在450-600字
5. 每个部分都要有实质性内容，不要空洞的描述
6. 重点突出实用性和学习价值

请提供高质量的专业解释:"""

        messages = [
            {
                "role": "system",
                "content": f"你是一位资深的{domain['name']}领域教育专家，拥有丰富的教学经验。你擅长将复杂的技术概念转化为清晰、准确、易懂的学习材料。你的解释既保持专业性，又注重实用性，能够帮助学生建立完整的知识体系。你总是提供结构化、高质量的内容，包含核心概念、术语信息、工作原理、实际应用和学习要点。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        explanation = self._make_request(messages, max_tokens=800, temperature=0.1)  # 增加token并降低随机性
        
        if explanation:
            # 质量检查
            is_quality_ok, quality_issues = quality_monitor.validate_explanation_quality(term, explanation)

            if not is_quality_ok:
                logger.warning(f"Explanation quality issues for '{term}': {', '.join(quality_issues)}")
                quality_monitor.log_quality_issue('term_explainer', 'explanation', quality_issues, explanation)

                # 如果质量问题严重，返回None重新生成
                if len(quality_issues) > 2:
                    logger.warning(f"Explanation quality too poor for '{term}', skipping")
                    return None

            # 尝试解析难度等级
            difficulty = self._analyze_difficulty(explanation)
            category = self._analyze_category(term, explanation)

            return {
                'explanation': explanation,
                'difficulty': difficulty,
                'category': category,
                'extended_info': {
                    'api_response_time': datetime.now().isoformat(),
                    'term_length': len(term),
                    'explanation_length': len(explanation),
                    'quality_issues': quality_issues if quality_issues else []
                }
            }

        return None
    
    def _analyze_difficulty(self, explanation: str) -> str:
        """分析名词难度等级"""
        # 简单的关键词分析
        beginner_keywords = ['基础', '简单', '入门', '基本', '初级']
        advanced_keywords = ['复杂', '高级', '深入', '专业', '算法', '架构']
        
        explanation_lower = explanation.lower()
        
        advanced_score = sum(1 for keyword in advanced_keywords if keyword in explanation_lower)
        beginner_score = sum(1 for keyword in beginner_keywords if keyword in explanation_lower)
        
        if advanced_score > beginner_score and advanced_score >= 2:
            return 'advanced'
        elif beginner_score > 0:
            return 'beginner'
        else:
            return 'intermediate'
    
    def _analyze_category(self, term: str, explanation: str) -> str:
        """分析名词所属分类"""
        categories = {
            '算法': ['算法', '排序', '搜索', '递归', '动态规划', '贪心'],
            '数据结构': ['数组', '链表', '栈', '队列', '树', '图', '哈希'],
            '网络': ['网络', '协议', 'TCP', 'UDP', 'HTTP', 'IP', '路由'],
            '数据库': ['数据库', 'SQL', '索引', '事务', '关系', '查询'],
            '操作系统': ['进程', '线程', '内存', '文件系统', '调度', '同步'],
            '编程语言': ['编程', '语言', '编译', '解释', '语法', '变量'],
            '软件工程': ['设计模式', '架构', '测试', '版本控制', '敏捷'],
            '人工智能': ['机器学习', '神经网络', '深度学习', 'AI', '智能'],
            '安全': ['加密', '安全', '认证', '防火墙', '漏洞', '攻击']
        }
        
        text = (term + ' ' + explanation).lower()
        
        for category, keywords in categories.items():
            if any(keyword.lower() in text for keyword in keywords):
                return category
        
        return '计算机基础'


class DailyTermService:
    """每日名词服务"""
    
    def __init__(self):
        self.api_client = KimiAPIClient()
        self.max_retry_attempts = 5
    
    def generate_daily_term(self, target_date: date = None) -> Optional[DailyTerm]:
        """生成每日名词"""
        if target_date is None:
            target_date = timezone.now().date()
        
        # 检查是否已存在当日名词
        existing_term = DailyTerm.objects.filter(
            display_date=target_date,
            status='active'
        ).first()
        
        if existing_term:
            logger.info(f"Daily term already exists for {target_date}: {existing_term.term}")
            return existing_term
        
        # 尝试获取新名词
        for attempt in range(self.max_retry_attempts):
            logger.info(f"Attempting to generate daily term (attempt {attempt + 1})")
            
            # 获取名词（基于指定日期的领域）
            term = self.api_client.get_computer_term(target_date)
            if not term:
                logger.warning(f"Failed to get term from API for {target_date} (attempt {attempt + 1})")
                continue
            
            # 清理名词
            term = self._clean_term(term)
            if not term:
                logger.warning(f"Term cleaning failed (attempt {attempt + 1})")
                continue
            
            # 检查是否已使用过
            if TermHistory.is_term_used(term):
                logger.info(f"Term '{term}' already used, trying again (attempt {attempt + 1})")
                continue
            
            # 获取解释（传递日期参数）
            explanation_data = self.api_client.get_term_explanation(term, target_date)
            if not explanation_data:
                logger.warning(f"Failed to get explanation for '{term}' (attempt {attempt + 1})")
                continue
            
            # 创建每日名词记录
            try:
                daily_term = DailyTerm.objects.create(
                    term=term,
                    explanation=explanation_data['explanation'],
                    category=explanation_data['category'],
                    difficulty_level=explanation_data['difficulty'],
                    extended_info=explanation_data['extended_info'],
                    display_date=target_date,
                    status='active',
                    api_source='kimi',
                    api_request_time=timezone.now()
                )
                
                # 添加到历史记录
                TermHistory.add_term(term, target_date)
                
                logger.info(f"Successfully generated daily term: {term}")
                return daily_term
                
            except Exception as e:
                logger.error(f"Failed to create daily term record: {e}")
                continue
        
        logger.error(f"Failed to generate daily term after {self.max_retry_attempts} attempts")
        return None
    
    def _clean_term(self, term: str) -> Optional[str]:
        """清理和验证名词"""
        if not term:
            return None
        
        # 移除多余的空白和标点
        term = term.strip().strip('.,!?;:"\'()[]{}')
        
        # 检查长度
        if len(term) < 2 or len(term) > 100:
            return None
        
        # 移除可能的前缀
        prefixes_to_remove = ['名词：', '术语：', '概念：', '答案：', '回答：']
        for prefix in prefixes_to_remove:
            if term.startswith(prefix):
                term = term[len(prefix):].strip()
        
        return term if term else None
    
    def get_today_term(self) -> Optional[DailyTerm]:
        """获取今日名词"""
        return DailyTerm.get_today_term()
    
    def get_term_history(self, days: int = 7) -> list:
        """获取历史名词"""
        return DailyTerm.get_latest_terms(days)
