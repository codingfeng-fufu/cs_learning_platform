from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
import json
import pytz


class KnowledgePoint(models.Model):
    """知识点模型"""

    CATEGORY_CHOICES = [
        ('network', '计算机网络'),
        ('algorithm', '算法与数据结构'),
        ('security', '信息安全'),
        ('system', '操作系统'),
        ('database', '数据库'),
        ('ai', '人工智能'),
    ]

    DIFFICULTY_CHOICES = [
        ('beginner', '初级'),
        ('intermediate', '中级'),
        ('advanced', '高级'),
    ]

    title = models.CharField(max_length=100, verbose_name='标题')
    slug = models.SlugField(unique=True, verbose_name='URL标识')
    description = models.TextField(verbose_name='描述')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name='分类'
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        verbose_name='难度'
    )
    icon = models.CharField(max_length=50, default='🧮', verbose_name='图标')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = '知识点'
        verbose_name_plural = '知识点'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """获取知识点的绝对URL"""
        return reverse('knowledge_app:detail', kwargs={'slug': self.slug})

    def get_category_display_with_icon(self):
        """获取带图标的分类显示"""
        category_icons = {
            'network': '🌐',
            'algorithm': '🧠',
            'security': '🔐',
            'system': '💻',
            'database': '🗄️',
            'ai': '🤖',
        }
        icon = category_icons.get(self.category, '📚')
        return f"{icon} {self.get_category_display()}"

    def get_difficulty_badge_class(self):
        """获取难度徽章的CSS类"""
        return f"difficulty-{self.difficulty}"

    @property
    def is_implemented(self):
        """判断是否已实现"""
        implemented_slugs = ['hamming-code', 'crc-check', 'single-linklist','graph_dfs']
        return self.slug in implemented_slugs

class DailyTerm(models.Model):
    """每日计算机名词解释模型"""

    STATUS_CHOICES = [
        ('active', '当前展示'),
        ('archived', '已归档'),
        ('draft', '草稿'),
    ]

    term = models.CharField(max_length=200, verbose_name='专业名词')
    explanation = models.TextField(verbose_name='详细解释')
    category = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='所属分类'
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', '初级'),
            ('intermediate', '中级'),
            ('advanced', '高级'),
        ],
        default='beginner',
        verbose_name='难度等级'
    )

    # 扩展信息（JSON格式存储）
    extended_info = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='扩展信息',
        help_text='存储示例、相关链接等额外信息'
    )

    # 状态管理
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='状态'
    )

    # 展示日期
    display_date = models.DateField(
        unique=True,
        verbose_name='展示日期',
        help_text='该名词展示的日期'
    )

    # 统计信息
    view_count = models.PositiveIntegerField(default=0, verbose_name='浏览次数')
    like_count = models.PositiveIntegerField(default=0, verbose_name='点赞次数')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    # API相关信息
    api_source = models.CharField(
        max_length=50,
        default='kimi',
        verbose_name='API来源'
    )
    api_request_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='API请求时间'
    )

    class Meta:
        ordering = ['-display_date']
        verbose_name = '每日名词'
        verbose_name_plural = '每日名词'
        indexes = [
            models.Index(fields=['display_date']),
            models.Index(fields=['status']),
            models.Index(fields=['term']),
        ]

    def __str__(self):
        return f"{self.display_date} - {self.term}"

    def save(self, *args, **kwargs):
        # 如果没有设置展示日期，使用今天
        if not self.display_date:
            self.display_date = timezone.now().date()
        super().save(*args, **kwargs)

    @classmethod
    def get_today_term(cls):
        """获取今日名词（带缓存优化）"""
        from django.core.cache import cache

        beijing_tz = pytz.timezone('Asia/Shanghai')
        today = timezone.now().astimezone(beijing_tz).date()

        # 先从缓存获取
        cache_key = f'today_term_{today}'
        cached_term = cache.get(cache_key)
        if cached_term:
            return cached_term

        try:
            term = cls.objects.select_related().get(display_date=today, status='active')
            # 缓存今日名词（1小时）
            cache.set(cache_key, term, 3600)
            return term
        except cls.DoesNotExist:
            # 如果今日没有名词，尝试触发生成
            print(f"⚠️  今日({today})没有找到名词，尝试生成...")

            try:
                from .services.daily_term_service import DailyTermService
                service = DailyTermService()
                daily_term = service.generate_daily_term(today)

                if daily_term:
                    print(f"✅ 成功生成今日名词: {daily_term.term}")
                    # 缓存新生成的名词
                    cache.set(cache_key, daily_term, 3600)
                    return daily_term
                else:
                    print("❌ 生成今日名词失败")
            except Exception as e:
                print(f"❌ 生成今日名词时出错: {e}")

            # 如果生成失败，返回最新的名词作为备用
            latest_term = cls.objects.filter(status='active').order_by('-display_date').first()
            if latest_term:
                print(f"📋 使用最新名词作为备用: {latest_term.term} (日期: {latest_term.display_date})")
                # 短期缓存备用名词（10分钟）
                cache.set(cache_key, latest_term, 600)
                return latest_term

            return None

    @classmethod
    def get_latest_terms(cls, count=7):
        """获取最近的名词列表"""
        return cls.objects.filter(status='active').order_by('-display_date')[:count]

    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def increment_like_count(self):
        """增加点赞次数"""
        self.like_count += 1
        self.save(update_fields=['like_count'])


class TermHistory(models.Model):
    """名词历史记录模型 - 用于去重"""

    term_lower = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='名词（小写）',
        help_text='用于去重检查的小写名词'
    )
    original_term = models.CharField(max_length=200, verbose_name='原始名词')
    first_used_date = models.DateField(verbose_name='首次使用日期')
    usage_count = models.PositiveIntegerField(default=1, verbose_name='使用次数')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '名词历史'
        verbose_name_plural = '名词历史'
        indexes = [
            models.Index(fields=['term_lower']),
        ]

    def __str__(self):
        return f"{self.original_term} (使用{self.usage_count}次)"

    @classmethod
    def is_term_used(cls, term):
        """检查名词是否已被使用"""
        return cls.objects.filter(term_lower=term.lower().strip()).exists()

    @classmethod
    def add_term(cls, term, date=None):
        """添加新名词到历史记录"""
        if date is None:
            date = timezone.now().date()

        term_lower = term.lower().strip()
        obj, created = cls.objects.get_or_create(
            term_lower=term_lower,
            defaults={
                'original_term': term,
                'first_used_date': date,
                'usage_count': 1
            }
        )

        if not created:
            obj.usage_count += 1
            obj.save(update_fields=['usage_count'])

        return obj


class AIExerciseSession(models.Model):
    """AI练习会话模型"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='用户'
    )
    knowledge_point = models.CharField(max_length=100, verbose_name='知识点')
    exercises = models.JSONField(verbose_name='练习题目', help_text='生成的题目数据')
    user_answers = models.JSONField(
        default=list,
        verbose_name='用户答案'
    )
    score = models.IntegerField(default=0, verbose_name='得分')
    total_questions = models.IntegerField(default=0, verbose_name='题目总数')
    correct_count = models.IntegerField(default=0, verbose_name='正确数量')

    # 时间统计
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    time_spent = models.IntegerField(default=0, verbose_name='用时（秒）')

    # 状态
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')

    # AI生成相关
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('easy', '简单'),
            ('medium', '中等'),
            ('hard', '困难'),
        ],
        default='medium',
        verbose_name='难度等级'
    )
    api_source = models.CharField(
        max_length=50,
        default='kimi',
        verbose_name='API来源'
    )

    class Meta:
        verbose_name = 'AI练习会话'
        verbose_name_plural = 'AI练习会话'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'knowledge_point']),
            models.Index(fields=['started_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.knowledge_point} ({self.score}分)"

    def calculate_score(self):
        """计算得分"""
        if not self.user_answers or not self.exercises:
            return 0

        correct = 0
        total = len(self.exercises)

        for i, exercise in enumerate(self.exercises):
            if i < len(self.user_answers):
                user_answer = self.user_answers[i]
                correct_answer = exercise.get('answer', '')

                if str(user_answer).strip().lower() == str(correct_answer).strip().lower():
                    correct += 1

        self.correct_count = correct
        self.total_questions = total
        self.score = int((correct / total) * 100) if total > 0 else 0

        return self.score

    def get_accuracy_rate(self):
        """获取正确率"""
        if self.total_questions == 0:
            return 0
        return (self.correct_count / self.total_questions) * 100


# 导入搜索相关模型
from .search_models import *

# 导入练习题相关模型
from .exercise_models import *

# 导入知识图谱相关模型
from .knowledge_graph_models import *