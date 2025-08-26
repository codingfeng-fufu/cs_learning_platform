"""
智能练习生成器服务
负责调用AI API生成练习题
"""

import requests
import json
import logging
import random
from typing import List, Dict, Any, Optional
from django.conf import settings
from django.utils import timezone

from ..models import AIExerciseSession
from .agent_quality_monitor import quality_monitor

logger = logging.getLogger(__name__)


class ExerciseGeneratorClient:
    """练习生成AI客户端"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'KIMI_API_KEY', '')
        self.base_url = getattr(settings, 'KIMI_API_URL', 'https://api.moonshot.cn/v1/chat/completions')
        self.model = getattr(settings, 'KIMI_MODEL', 'moonshot-v1-8k')
        self.timeout = 30
        self.max_retries = 3
    
    def _make_request(self, messages: list, max_tokens: int = 2000) -> Optional[str]:
        """发送API请求"""
        if not self.api_key:
            logger.error("AI API key not configured")
            return None
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        data = {
            'model': self.model,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': 0.7
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
                import time
                time.sleep(2 ** attempt)  # 指数退避
        
        return None
    
    def generate_exercises(self, knowledge_point: str, difficulty: str = 'medium', count: int = 5) -> Optional[List[Dict]]:
        """生成练习题"""
        prompt = self._build_exercise_prompt(knowledge_point, difficulty, count)
        
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的计算机科学练习题生成器，能够生成高质量的练习题。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self._make_request(messages, max_tokens=2000)
        
        if response:
            try:
                # 尝试解析JSON响应
                if response.startswith('```json'):
                    response = response.replace('```json', '').replace('```', '').strip()
                
                data = json.loads(response)
                exercises = data.get('exercises', [])
                
                # 验证和清理数据
                cleaned_exercises = []
                for exercise in exercises:
                    if self._validate_exercise(exercise):
                        cleaned_exercises.append(exercise)
                
                return cleaned_exercises
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse exercise JSON: {e}")
                logger.error(f"Response content: {response}")
                return None
        
        return None
    
    def _build_exercise_prompt(self, knowledge_point: str, difficulty: str, count: int) -> str:
        """构建练习题生成提示词"""
        
        # 知识点相关的提示
        knowledge_prompts = {
            'hamming-code': '海明码编码解码，包括校验位计算、错误检测与纠正',
            'crc-check': 'CRC循环冗余检验，包括多项式除法、校验码计算',
            'single-linklist': '单链表操作，包括插入、删除、查找、遍历',
            'graph-dfs': '图的深度优先搜索，包括遍历过程、递归实现、应用场景',
            'binary-search-tree': '二叉搜索树，包括插入、删除、查找操作',
            'quick-sort': '快速排序算法，包括分治思想、划分过程',
            'hash-table': '哈希表，包括哈希函数、冲突解决',
            'dynamic-programming': '动态规划，包括状态转移、最优子结构'
        }
        
        knowledge_desc = knowledge_prompts.get(knowledge_point, knowledge_point)
        
        # 难度相关的提示
        difficulty_prompts = {
            'easy': '基础概念理解，适合初学者',
            'medium': '概念应用和简单分析，适合有一定基础的学习者',
            'hard': '综合应用和深入分析，适合进阶学习者'
        }
        
        difficulty_desc = difficulty_prompts.get(difficulty, '中等难度')
        
        # 获取当前领域信息以提供更精确的上下文
        from .domain_scheduler import domain_scheduler
        try:
            domain_info = domain_scheduler.get_domain_info()
            current_domain = domain_info['domain']
            domain_context = f"当前学习领域：{current_domain['name']} - {current_domain['description']}"
            related_concepts = f"相关概念：{', '.join(current_domain['keywords'][:8])}"
        except:
            domain_context = ""
            related_concepts = ""

        prompt = f"""
你是一个专业的计算机科学教育专家，专门出选择题。请为"{knowledge_desc}"生成{count}道高质量的选择题。

{domain_context}
{related_concepts}

题目要求：
1. 题目类型：仅生成选择题（单选题）
2. 难度等级：{difficulty_desc}
3. 知识点相关性：必须与"{knowledge_point}"直接相关
4. 质量控制要求：
   - 避免过于简单的定义题
   - 避免容易产生歧义的表述
   - 确保选项之间有明确区别
   - 不要使用"以上都对"或"以上都错"选项
   - 正确答案要准确无误
   - 干扰项要有合理性，但明确错误

选择题具体要求：
- 每题4个选项，标记为A、B、C、D
- 只有一个正确答案
- 3个干扰项应该是学习者可能的错误理解
- 题目表述要清晰、无歧义
- 涵盖不同层面：概念理解、应用分析、问题解决

请严格按照以下JSON格式输出：
```json
{{
  "exercises": [
    {{
      "type": "choice",
      "question": "清晰准确的题目描述",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "A",
      "explanation": "详细解析：说明正确答案的原因，以及其他选项为什么错误",
      "difficulty": "{difficulty}",
      "tags": ["{knowledge_point}", "相关标签"]
    }}
  ]
}}
```

重要提醒：
- 确保每道题的正确答案都是准确的
- 解析要详细说明为什么其他选项错误
- 避免任何可能产生歧义或错误的内容
- JSON格式必须正确，可以被解析
"""
        
        return prompt
    
    def _validate_exercise(self, exercise: Dict) -> bool:
        """验证练习题数据格式（仅接受选择题）"""
        required_fields = ['type', 'question', 'answer', 'explanation', 'options']

        for field in required_fields:
            if field not in exercise or not exercise[field]:
                logger.warning(f"Exercise missing required field: {field}")
                return False

        # 只接受选择题
        if exercise['type'] != 'choice':
            logger.warning(f"Only choice exercises are accepted, got: {exercise['type']}")
            return False

        # 验证选择题格式
        if not isinstance(exercise['options'], list):
            logger.warning("Choice exercise options must be a list")
            return False

        if len(exercise['options']) != 4:
            logger.warning(f"Choice exercise must have exactly 4 options, got {len(exercise['options'])}")
            return False

        # 验证答案格式
        if exercise['answer'] not in ['A', 'B', 'C', 'D']:
            logger.warning(f"Invalid choice answer format: {exercise['answer']}")
            return False

        # 验证选项格式
        for i, option in enumerate(exercise['options']):
            expected_prefix = ['A.', 'B.', 'C.', 'D.'][i]
            if not option.startswith(expected_prefix):
                logger.warning(f"Option {i} should start with '{expected_prefix}', got: {option}")
                return False

        # 验证题目质量
        question = exercise['question'].strip()
        if len(question) < 10:
            logger.warning("Question too short, might be low quality")
            return False

        # 验证解析质量
        explanation = exercise['explanation'].strip()
        if len(explanation) < 20:
            logger.warning("Explanation too short, might be low quality")
            return False

        # 使用质量监控器进行额外验证
        is_quality_ok, quality_issues = quality_monitor.validate_exercise_quality(exercise)
        if not is_quality_ok:
            logger.warning(f"Exercise quality issues: {', '.join(quality_issues)}")
            quality_monitor.log_quality_issue('exercise_generator', 'exercise', quality_issues,
                                            exercise.get('question', ''))
            return False

        return True


class ExerciseGeneratorService:
    """练习生成器服务"""
    
    def __init__(self):
        self.client = ExerciseGeneratorClient()
    
    def generate_exercise_session(self, user, knowledge_point: str, difficulty: str = 'medium', count: int = 5) -> Optional[AIExerciseSession]:
        """生成练习会话"""
        
        # 生成练习题
        exercises = self.client.generate_exercises(knowledge_point, difficulty, count)
        
        if not exercises:
            logger.error(f"Failed to generate exercises for {knowledge_point}")
            return None
        
        # 创建练习会话
        session = AIExerciseSession.objects.create(
            user=user,
            knowledge_point=knowledge_point,
            exercises=exercises,
            total_questions=len(exercises),
            difficulty_level=difficulty
        )
        
        # 记录日志
        logger.info(f"Generated exercise session {session.id} for {knowledge_point}")
        
        return session

    def submit_answers(self, session_id: int, answers: List[str]) -> Optional[AIExerciseSession]:
        """提交答案并计算得分"""
        try:
            session = AIExerciseSession.objects.get(id=session_id)
            
            # 保存用户答案
            session.user_answers = answers
            session.completed_at = timezone.now()
            session.is_completed = True
            
            # 计算用时
            if session.started_at and session.completed_at:
                time_diff = session.completed_at - session.started_at
                session.time_spent = int(time_diff.total_seconds())
            
            # 计算得分
            session.calculate_score()
            session.save()
            
            logger.info(f"Session {session_id} completed with score {session.score}")
            return session
            
        except AIExerciseSession.DoesNotExist:
            logger.error(f"Exercise session {session_id} not found")
            return None
    
    def get_session_report(self, session_id: int) -> Optional[Dict]:
        """获取练习报告"""
        try:
            session = AIExerciseSession.objects.get(id=session_id)
            
            if not session.is_completed:
                return None
            
            # 生成详细报告
            report = {
                'session_id': session.id,
                'knowledge_point': session.knowledge_point,
                'score': session.score,
                'accuracy_rate': session.get_accuracy_rate(),
                'total_questions': session.total_questions,
                'correct_count': session.correct_count,
                'time_spent': session.time_spent,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'exercises_detail': []
            }
            
            # 添加每道题的详细信息
            for i, exercise in enumerate(session.exercises):
                user_answer = session.user_answers[i] if i < len(session.user_answers) else ''
                correct_answer = exercise.get('answer', '')
                is_correct = str(user_answer).strip().lower() == str(correct_answer).strip().lower()
                
                exercise_detail = {
                    'question': exercise.get('question', ''),
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'explanation': exercise.get('explanation', ''),
                    'type': exercise.get('type', ''),
                    'options': exercise.get('options', [])
                }
                
                report['exercises_detail'].append(exercise_detail)
            
            return report
            
        except AIExerciseSession.DoesNotExist:
            logger.error(f"Exercise session {session_id} not found")
            return None
    

