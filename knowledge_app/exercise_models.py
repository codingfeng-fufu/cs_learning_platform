from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()

class ExerciseCategory(models.Model):
    """练习题分类"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    slug = models.SlugField(unique=True, verbose_name='URL标识')
    description = models.TextField(blank=True, verbose_name='分类描述')
    icon = models.CharField(max_length=10, default='📚', verbose_name='图标')
    color = models.CharField(max_length=7, default='#4ecdc4', verbose_name='主题色')
    order = models.PositiveIntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '练习题分类'
        verbose_name_plural = '练习题分类'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class ExerciseDifficulty(models.Model):
    """练习题难度"""
    name = models.CharField(max_length=50, verbose_name='难度名称')
    level = models.PositiveIntegerField(unique=True, verbose_name='难度等级')
    color = models.CharField(max_length=7, default='#28a745', verbose_name='颜色')
    description = models.TextField(blank=True, verbose_name='难度描述')
    
    class Meta:
        verbose_name = '练习题难度'
        verbose_name_plural = '练习题难度'
        ordering = ['level']
    
    def __str__(self):
        return self.name


class Exercise(models.Model):
    """练习题"""
    QUESTION_TYPES = [
        ('single_choice', '单选题'),
        ('multiple_choice', '多选题'),
        ('true_false', '判断题'),
        ('fill_blank', '填空题'),
        ('short_answer', '简答题'),
        ('coding', '编程题'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='题目标题')
    slug = models.SlugField(unique=True, verbose_name='URL标识')
    category = models.ForeignKey(ExerciseCategory, on_delete=models.CASCADE, verbose_name='分类')
    difficulty = models.ForeignKey(ExerciseDifficulty, on_delete=models.CASCADE, verbose_name='难度')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, verbose_name='题目类型')
    
    # 题目内容
    question_text = models.TextField(verbose_name='题目描述')
    question_image = models.ImageField(upload_to='exercises/images/', blank=True, null=True, verbose_name='题目图片')
    
    # 选择题选项 (JSON格式存储)
    options = models.JSONField(default=dict, blank=True, verbose_name='选项')
    
    # 正确答案
    correct_answer = models.TextField(verbose_name='正确答案')
    
    # 解析
    explanation = models.TextField(blank=True, verbose_name='答案解析')
    explanation_image = models.ImageField(upload_to='exercises/explanations/', blank=True, null=True, verbose_name='解析图片')
    
    # 提示
    hints = models.JSONField(default=list, blank=True, verbose_name='提示')
    
    # 标签
    tags = models.CharField(max_length=200, blank=True, verbose_name='标签', help_text='用逗号分隔')
    
    # 统计信息
    view_count = models.PositiveIntegerField(default=0, verbose_name='浏览次数')
    attempt_count = models.PositiveIntegerField(default=0, verbose_name='尝试次数')
    correct_count = models.PositiveIntegerField(default=0, verbose_name='正确次数')
    
    # 时间限制（秒）
    time_limit = models.PositiveIntegerField(default=0, verbose_name='时间限制', help_text='0表示无限制')
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    is_featured = models.BooleanField(default=False, verbose_name='是否推荐')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '练习题'
        verbose_name_plural = '练习题'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'difficulty']),
            models.Index(fields=['question_type']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def success_rate(self):
        """正确率"""
        if self.attempt_count == 0:
            return 0
        return round((self.correct_count / self.attempt_count) * 100, 1)
    
    @property
    def tag_list(self):
        """标签列表"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


class ExerciseSet(models.Model):
    """练习题集"""
    name = models.CharField(max_length=200, verbose_name='题集名称')
    slug = models.SlugField(unique=True, verbose_name='URL标识')
    description = models.TextField(blank=True, verbose_name='题集描述')
    category = models.ForeignKey(ExerciseCategory, on_delete=models.CASCADE, verbose_name='分类')
    exercises = models.ManyToManyField(Exercise, through='ExerciseSetItem', verbose_name='练习题')
    
    # 设置
    time_limit = models.PositiveIntegerField(default=0, verbose_name='总时间限制', help_text='分钟，0表示无限制')
    shuffle_questions = models.BooleanField(default=False, verbose_name='随机题目顺序')
    shuffle_options = models.BooleanField(default=False, verbose_name='随机选项顺序')
    show_result_immediately = models.BooleanField(default=True, verbose_name='立即显示结果')
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '练习题集'
        verbose_name_plural = '练习题集'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def exercise_count(self):
        """题目数量"""
        return self.exercises.count()


class ExerciseSetItem(models.Model):
    """练习题集项目"""
    exercise_set = models.ForeignKey(ExerciseSet, on_delete=models.CASCADE, verbose_name='题集')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, verbose_name='练习题')
    order = models.PositiveIntegerField(default=0, verbose_name='排序')
    points = models.PositiveIntegerField(default=1, verbose_name='分值')
    
    class Meta:
        verbose_name = '练习题集项目'
        verbose_name_plural = '练习题集项目'
        unique_together = ['exercise_set', 'exercise']
        ordering = ['order']
    
    def __str__(self):
        return f"{self.exercise_set.name} - {self.exercise.title}"


class UserExerciseAttempt(models.Model):
    """用户练习记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, verbose_name='练习题')
    
    # 答题信息
    user_answer = models.TextField(verbose_name='用户答案')
    is_correct = models.BooleanField(verbose_name='是否正确')
    score = models.FloatField(default=0, verbose_name='得分')
    
    # 时间信息
    start_time = models.DateTimeField(verbose_name='开始时间')
    submit_time = models.DateTimeField(verbose_name='提交时间')
    time_spent = models.PositiveIntegerField(verbose_name='用时(秒)')
    
    # 额外信息
    hints_used = models.JSONField(default=list, blank=True, verbose_name='使用的提示')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')
    
    class Meta:
        verbose_name = '用户练习记录'
        verbose_name_plural = '用户练习记录'
        ordering = ['-submit_time']
        indexes = [
            models.Index(fields=['user', '-submit_time']),
            models.Index(fields=['exercise', '-submit_time']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise.title}"


class UserExerciseSetAttempt(models.Model):
    """用户题集练习记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    exercise_set = models.ForeignKey(ExerciseSet, on_delete=models.CASCADE, verbose_name='练习题集')
    
    # 成绩信息
    total_score = models.FloatField(default=0, verbose_name='总分')
    max_score = models.FloatField(default=0, verbose_name='满分')
    correct_count = models.PositiveIntegerField(default=0, verbose_name='正确题数')
    total_count = models.PositiveIntegerField(default=0, verbose_name='总题数')
    
    # 时间信息
    start_time = models.DateTimeField(verbose_name='开始时间')
    submit_time = models.DateTimeField(blank=True, null=True, verbose_name='提交时间')
    time_spent = models.PositiveIntegerField(default=0, verbose_name='用时(秒)')
    
    # 状态
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    
    class Meta:
        verbose_name = '用户题集练习记录'
        verbose_name_plural = '用户题集练习记录'
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise_set.name}"
    
    @property
    def success_rate(self):
        """正确率"""
        if self.total_count == 0:
            return 0
        return round((self.correct_count / self.total_count) * 100, 1)
    
    @property
    def score_percentage(self):
        """得分率"""
        if self.max_score == 0:
            return 0
        return round((self.total_score / self.max_score) * 100, 1)
