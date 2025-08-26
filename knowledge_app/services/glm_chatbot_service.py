"""
GLM4.5 聊天机器人服务
专门用于每日名词解释的智能问答
"""

import requests
import json
import logging
from typing import List, Dict, Optional
from django.conf import settings
from django.utils import timezone
from .agent_quality_monitor import quality_monitor

logger = logging.getLogger(__name__)


class GLMChatbotClient:
    """GLM4.5 API客户端"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GLM_API_KEY', '51543173ea8949b081c0872986350579.UWJVMorlloyKEj09')
        self.base_url = getattr(settings, 'GLM_API_URL', 'https://open.bigmodel.cn/api/paas/v4/chat/completions')
        self.model = getattr(settings, 'GLM_MODEL', 'glm-4.5')
        self.timeout = 30
        self.max_retries = 3
    
    def _make_request(self, messages: List[Dict], max_tokens: int = 1000, temperature: float = 0.7) -> Optional[str]:
        """发送API请求"""
        if not self.api_key:
            logger.error("GLM API key not configured")
            return None
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        data = {
            'model': self.model,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'stream': False
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
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content'].strip()
                    else:
                        logger.warning(f"Unexpected response format: {result}")
                else:
                    logger.warning(f"GLM API request failed with status {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"GLM API request error (attempt {attempt + 1}): {e}")
                
            if attempt < self.max_retries - 1:
                import time
                time.sleep(2 ** attempt)  # 指数退避
        
        return None
    
    def chat_about_term(self, term: str, term_explanation: str, user_question: str, theme_info: Dict = None) -> Optional[str]:
        """针对特定名词进行问答"""

        # 获取当前领域信息以提供更准确的上下文
        from .domain_scheduler import domain_scheduler
        try:
            domain_info = domain_scheduler.get_domain_info()
            current_domain = domain_info['domain']
            domain_context = f"当前学习领域：{current_domain['name']}"
            related_concepts = f"相关概念：{', '.join(current_domain['keywords'][:6])}"
        except:
            domain_context = ""
            related_concepts = ""

        # 处理主题信息
        if theme_info:
            theme_name = theme_info.get('name', '友好助手')
            theme_personality = theme_info.get('personality', '友好、耐心、鼓励性')
            theme_style = theme_info.get('style', '使用亲切的语言')
            theme_avatar = theme_info.get('avatar', '😊')
        else:
            theme_name = '友好助手'
            theme_personality = '友好、耐心、鼓励性'
            theme_style = '使用亲切的语言'
            theme_avatar = '😊'

        system_prompt = f"""你是一个{theme_name} {theme_avatar}，专门帮助学生理解计算机专业名词。

角色特征：{theme_personality}
回答风格：{theme_style}

当前讨论的名词：{term}
名词解释：{term_explanation}
{domain_context}
{related_concepts}

重要原则：
1. 严格基于给定的名词解释进行回答
2. 如果不确定某个信息，明确说明"根据给定的解释"或"需要进一步查证"
3. 避免提供可能不准确的具体数据、年份、人名等细节
4. 专注于概念理解和应用，而非具体实现细节

你的任务：
1. 基于给定的名词和解释，准确回答学生的问题
2. 用通俗易懂的语言解释复杂概念
3. 提供概念性的例子和应用场景（避免具体的代码或数值）
4. 如果学生问题与当前名词无关，礼貌地引导回到主题
5. 如果问题超出给定解释的范围，诚实说明并建议查阅更多资料
6. 回答要简洁明了，一般控制在200字以内

回答约束：
- 不要编造具体的数据、统计信息或历史细节
- 不要提供可能过时的技术规范
- 避免绝对化的表述，使用"通常"、"一般来说"等限定词
- 如果涉及争议性话题，说明存在不同观点
- 承认知识的局限性，鼓励学生进一步学习

回答风格：
- 友好、耐心、专业
- 用简单的语言解释复杂概念
- 适当使用比喻和概念性例子
- 鼓励学生继续学习和思考"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]

        return self._make_request(messages, max_tokens=500, temperature=0.3)  # 降低temperature减少随机性
    
    def get_related_questions(self, term: str, term_explanation: str) -> List[str]:
        """生成与名词相关的推荐问题"""

        # 获取当前领域信息
        from .domain_scheduler import domain_scheduler
        try:
            domain_info = domain_scheduler.get_domain_info()
            current_domain = domain_info['domain']
            domain_context = f"当前学习领域：{current_domain['name']}"
        except:
            domain_context = ""

        prompt = f"""你是一个教学专家，请基于给定的名词解释生成5个学习问题。

名词：{term}
解释：{term_explanation}
{domain_context}

问题生成原则：
1. 严格基于给定的名词解释内容
2. 避免需要额外知识才能回答的问题
3. 不要问具体的技术参数、历史细节或实现代码
4. 专注于概念理解、应用场景和学习要点

请生成5个问题，这些问题应该：
- 帮助学生理解核心概念
- 涉及概念的应用和意义
- 适合基于给定解释进行回答
- 避免过于具体的技术细节
- 每个问题都要清晰和有价值

问题类型建议：
- 概念理解类："这个概念的核心思想是什么？"
- 应用场景类："这个技术主要用在什么地方？"
- 对比分析类："它与相关概念有什么区别？"
- 学习要点类："学习这个概念需要注意什么？"
- 实际意义类："为什么这个概念很重要？"

请按以下格式返回，每行一个问题：
1. 问题1
2. 问题2
3. 问题3
4. 问题4
5. 问题5"""

        messages = [
            {"role": "system", "content": "你是一个教学专家，擅长设计基于给定材料的学习问题，避免超出材料范围的内容。"},
            {"role": "user", "content": prompt}
        ]

        response = self._make_request(messages, max_tokens=300, temperature=0.5)  # 降低随机性

        if response:
            # 解析问题列表
            questions = []
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # 移除序号和标点
                    question = line.split('.', 1)[-1].strip()
                    question = question.lstrip('-•').strip()
                    if question and len(question) > 5:
                        questions.append(question)

            return questions[:5]  # 最多返回5个问题

        return []


class GLMChatbotService:
    """GLM聊天机器人服务"""

    # 聊天机器人主题配置
    CHATBOT_THEMES = {
        'professional': {
            'name': '专业导师',
            'avatar': '🎓',
            'personality': '严谨、专业、学术化',
            'style': '使用正式的学术语言，注重准确性和专业性',
            'greeting': '您好！我是您的专业学习导师，专门帮助您深入理解计算机科学概念。',
            'color_scheme': 'blue'
        },
        'friendly': {
            'name': '友好助手',
            'avatar': '😊',
            'personality': '友好、耐心、鼓励性',
            'style': '使用亲切的语言，多用比喻和生活化的例子',
            'greeting': '嗨！我是您的学习小伙伴，让我们一起轻松愉快地学习计算机知识吧！',
            'color_scheme': 'green'
        },
        'tech_guru': {
            'name': '技术大牛',
            'avatar': '🚀',
            'personality': '前沿、创新、实践导向',
            'style': '关注最新技术趋势，强调实际应用和项目经验',
            'greeting': '欢迎！我是技术前沿的探索者，让我们一起探讨计算机技术的奥秘！',
            'color_scheme': 'purple'
        },
        'patient_teacher': {
            'name': '耐心老师',
            'avatar': '👨‍🏫',
            'personality': '耐心、细致、循序渐进',
            'style': '从基础开始，逐步深入，确保每个概念都被理解',
            'greeting': '同学你好！我是您的耐心老师，会从最基础的概念开始，帮您建立扎实的知识基础。',
            'color_scheme': 'orange'
        },
        'research_assistant': {
            'name': '研究助手',
            'avatar': '🔬',
            'personality': '严谨、分析性、研究导向',
            'style': '注重理论基础，提供深度分析和学术视角',
            'greeting': '您好！我是您的研究助手，专注于为您提供深入的理论分析和学术见解。',
            'color_scheme': 'teal'
        }
    }

    def __init__(self):
        self.client = GLMChatbotClient()
        self.current_theme = 'friendly'  # 默认主题
    
    def set_theme(self, theme_key: str) -> bool:
        """设置聊天机器人主题"""
        if theme_key in self.CHATBOT_THEMES:
            self.current_theme = theme_key
            return True
        return False

    def get_current_theme(self) -> Dict:
        """获取当前主题信息"""
        return self.CHATBOT_THEMES.get(self.current_theme, self.CHATBOT_THEMES['friendly'])

    def get_all_themes(self) -> Dict:
        """获取所有可用主题"""
        return self.CHATBOT_THEMES

    def ask_about_term(self, term: str, term_explanation: str, user_question: str, user_id: int = None, theme: str = None) -> Dict:
        """询问关于名词的问题"""

        # 设置主题（如果提供）
        if theme and theme in self.CHATBOT_THEMES:
            self.current_theme = theme

        # 记录用户问题（可选）
        if user_id:
            logger.info(f"User {user_id} asked about '{term}': {user_question}")

        # 获取当前主题信息
        current_theme_info = self.get_current_theme()

        # 获取AI回答（传递主题信息）
        answer = self.client.chat_about_term(term, term_explanation, user_question, current_theme_info)

        if answer:
            # 质量检查
            is_quality_ok, quality_issues = quality_monitor.validate_chat_response_quality(
                answer, term_explanation
            )

            if not is_quality_ok:
                logger.warning(f"Chat response quality issues: {', '.join(quality_issues)}")
                quality_monitor.log_quality_issue('chatbot', 'response', quality_issues, answer)

                # 如果质量问题严重，返回保守回复
                if len(quality_issues) > 2:
                    return {
                        'success': True,
                        'answer': f'关于"{term}"的问题比较复杂，建议您查阅更多专业资料来获得准确的信息。根据给定的解释，{term_explanation[:100]}...',
                        'timestamp': timezone.now().isoformat(),
                        'quality_fallback': True
                    }

            return {
                'success': True,
                'answer': answer,
                'timestamp': timezone.now().isoformat()
            }
        else:
            return {
                'success': False,
                'error': 'AI服务暂时不可用，请稍后重试',
                'timestamp': timezone.now().isoformat()
            }
    
    def get_suggested_questions(self, term: str, term_explanation: str) -> Dict:
        """获取推荐问题"""
        
        questions = self.client.get_related_questions(term, term_explanation)
        
        if questions:
            return {
                'success': True,
                'questions': questions,
                'count': len(questions)
            }
        else:
            # 提供默认问题
            default_questions = [
                f"{term}的主要作用是什么？",
                f"{term}在实际项目中如何应用？",
                f"学习{term}需要什么基础知识？",
                f"{term}有哪些常见的误区？",
                f"如何更好地理解{term}这个概念？"
            ]
            
            return {
                'success': True,
                'questions': default_questions,
                'count': len(default_questions),
                'is_default': True
            }
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return bool(self.client.api_key)
    
    def get_service_status(self) -> Dict:
        """获取服务状态"""
        return {
            'available': self.is_available(),
            'model': self.client.model,
            'api_configured': bool(self.client.api_key)
        }
