from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
import json

User = get_user_model()


class QuizLibrary(models.Model):
    """个人题库"""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='创建者')
    name = models.CharField(max_length=200, verbose_name='题库名称')
    description = models.TextField(blank=True, verbose_name='题库描述')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 统计字段
    total_questions = models.PositiveIntegerField(default=0, verbose_name='题目总数')
    
    class Meta:
        verbose_name = '个人题库'
        verbose_name_plural = '个人题库'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.owner.username} - {self.name}"
    
    def update_question_count(self):
        """更新题目数量"""
        self.total_questions = self.questions.filter(is_active=True).count()
        self.save(update_fields=['total_questions'])


class LibraryShare(models.Model):
    """题库分享记录"""
    SHARE_TYPE_CHOICES = [
        ('public', '公开分享'),
        ('private', '私密分享'),
        ('link', '链接分享'),
    ]

    PERMISSION_CHOICES = [
        ('view', '仅查看'),
        ('copy', '可复制'),
        ('edit', '可编辑'),
    ]

    library = models.ForeignKey(QuizLibrary, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_libraries')
    shared_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_libraries', null=True, blank=True)
    share_type = models.CharField(max_length=10, choices=SHARE_TYPE_CHOICES, default='private')
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='view')
    share_code = models.CharField(max_length=32, unique=True, null=True, blank=True)  # 用于链接分享
    message = models.TextField(blank=True, help_text="分享时的留言")
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="分享过期时间")
    created_at = models.DateTimeField(auto_now_add=True)
    accessed_at = models.DateTimeField(null=True, blank=True, help_text="最后访问时间")
    access_count = models.PositiveIntegerField(default=0, help_text="访问次数")

    class Meta:
        unique_together = ['library', 'shared_by', 'shared_to']
        indexes = [
            models.Index(fields=['share_code']),
            models.Index(fields=['shared_to', 'is_active']),
            models.Index(fields=['shared_by', 'created_at']),
        ]

    def __str__(self):
        if self.shared_to:
            return f"{self.shared_by.username} 分享 '{self.library.name}' 给 {self.shared_to.username}"
        else:
            return f"{self.shared_by.username} {self.get_share_type_display()} '{self.library.name}'"

    def save(self, *args, **kwargs):
        if self.share_type == 'link' and not self.share_code:
            import uuid
            self.share_code = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def is_expired(self):
        """检查分享是否已过期"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def can_access(self, user):
        """检查用户是否可以访问此分享"""
        if not self.is_active or self.is_expired():
            return False

        if self.share_type == 'public':
            return True
        elif self.share_type == 'private':
            return user == self.shared_to
        elif self.share_type == 'link':
            return True  # 任何有链接的人都可以访问

        return False

    def record_access(self, user=None):
        """记录访问"""
        from django.utils import timezone
        self.accessed_at = timezone.now()
        self.access_count += 1
        self.save(update_fields=['accessed_at', 'access_count'])


class LibraryCopy(models.Model):
    """题库复制记录"""
    original_library = models.ForeignKey(QuizLibrary, on_delete=models.CASCADE, related_name='copies')
    copied_library = models.ForeignKey(QuizLibrary, on_delete=models.CASCADE, related_name='original')
    copied_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='copied_libraries')
    share = models.ForeignKey(LibraryShare, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.copied_by.username} 复制了 '{self.original_library.name}'"


class QuizTag(models.Model):
    """题目标签"""
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名称')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='标签颜色')
    description = models.TextField(blank=True, verbose_name='标签描述')
    
    class Meta:
        verbose_name = '题目标签'
        verbose_name_plural = '题目标签'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class QuizQuestion(models.Model):
    """题目"""
    QUESTION_TYPES = [
        ('single_choice', '单选题'),
        ('multiple_choice', '多选题'),
        ('fill_blank', '填空题'),
        ('short_answer', '简答题'),
    ]
    
    DIFFICULTY_LEVELS = [
        (1, '简单'),
        (2, '中等'),
        (3, '困难'),
    ]
    
    library = models.ForeignKey(QuizLibrary, on_delete=models.CASCADE, related_name='questions', verbose_name='所属题库')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, verbose_name='题目类型')
    title = models.CharField(max_length=200, verbose_name='题目标题')
    content = models.TextField(verbose_name='题目内容')

    # 图片支持
    question_image = models.ImageField(upload_to='quiz_questions/', blank=True, null=True, verbose_name='题目图片')
    option_images = models.JSONField(default=dict, blank=True, verbose_name='选项图片')
    
    # 选择题选项 (JSON格式存储)
    options = models.JSONField(default=dict, blank=True, verbose_name='选项')
    
    # 答案
    correct_answer = models.TextField(verbose_name='正确答案')
    explanation = models.TextField(blank=True, verbose_name='答案解析')
    
    # 属性
    difficulty = models.IntegerField(choices=DIFFICULTY_LEVELS, default=2, verbose_name='难度')
    tags = models.ManyToManyField(QuizTag, blank=True, verbose_name='标签')
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 统计字段
    total_attempts = models.PositiveIntegerField(default=0, verbose_name='总答题次数')
    correct_attempts = models.PositiveIntegerField(default=0, verbose_name='正确次数')
    
    class Meta:
        verbose_name = '题目'
        verbose_name_plural = '题目'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.library.name} - {self.title}"
    
    @property
    def accuracy_rate(self):
        """正确率"""
        if self.total_attempts == 0:
            return 0
        return round((self.correct_attempts / self.total_attempts) * 100, 1)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 更新题库的题目数量
        self.library.update_question_count()


class QuizSession(models.Model):
    """练习会话"""
    SESSION_STATUS = [
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('paused', '已暂停'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    library = models.ForeignKey(QuizLibrary, on_delete=models.CASCADE, verbose_name='题库')
    
    # 会话信息
    session_name = models.CharField(max_length=200, verbose_name='会话名称')
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='in_progress', verbose_name='状态')
    
    # 时间记录
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    # 统计信息
    total_questions = models.PositiveIntegerField(default=0, verbose_name='总题数')
    answered_questions = models.PositiveIntegerField(default=0, verbose_name='已答题数')
    correct_answers = models.PositiveIntegerField(default=0, verbose_name='正确答案数')
    
    class Meta:
        verbose_name = '练习会话'
        verbose_name_plural = '练习会话'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.session_name}"
    
    @property
    def accuracy_rate(self):
        """正确率"""
        if self.answered_questions == 0:
            return 0
        return round((self.correct_answers / self.answered_questions) * 100, 1)
    
    @property
    def progress_rate(self):
        """进度百分比"""
        if self.total_questions == 0:
            return 0
        return round((self.answered_questions / self.total_questions) * 100, 1)
    
    @property
    def duration(self):
        """练习时长（分钟）"""
        if self.completed_at:
            delta = self.completed_at - self.started_at
            return round(delta.total_seconds() / 60, 1)
        else:
            delta = timezone.now() - self.started_at
            return round(delta.total_seconds() / 60, 1)


class QuizAnswer(models.Model):
    """答题记录"""
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='answers', verbose_name='练习会话')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, verbose_name='题目')
    user_answer = models.TextField(verbose_name='用户答案')
    is_correct = models.BooleanField(verbose_name='是否正确')
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name='答题时间')
    time_spent = models.PositiveIntegerField(default=0, verbose_name='答题用时(秒)')
    
    class Meta:
        verbose_name = '答题记录'
        verbose_name_plural = '答题记录'
        unique_together = ['session', 'question']
        ordering = ['-answered_at']
    
    def __str__(self):
        return f"{self.session.user.username} - {self.question.title}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # 更新题目统计
        self.question.total_attempts += 1
        if self.is_correct:
            self.question.correct_attempts += 1
        self.question.save(update_fields=['total_attempts', 'correct_attempts'])
        
        # 更新会话统计
        session = self.session
        session.answered_questions = session.answers.count()
        session.correct_answers = session.answers.filter(is_correct=True).count()
        session.save(update_fields=['answered_questions', 'correct_answers'])


class WrongAnswer(models.Model):
    """错题记录"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, verbose_name='题目')
    wrong_answer = models.TextField(verbose_name='错误答案')
    correct_answer = models.TextField(verbose_name='正确答案')
    
    # 错题信息
    first_wrong_at = models.DateTimeField(auto_now_add=True, verbose_name='首次答错时间')
    last_wrong_at = models.DateTimeField(auto_now=True, verbose_name='最近答错时间')
    wrong_count = models.PositiveIntegerField(default=1, verbose_name='答错次数')
    
    # 是否已掌握
    is_mastered = models.BooleanField(default=False, verbose_name='是否已掌握')
    mastered_at = models.DateTimeField(null=True, blank=True, verbose_name='掌握时间')
    
    # AI分析结果
    ai_analysis = models.TextField(blank=True, verbose_name='AI分析')
    study_suggestion = models.TextField(blank=True, verbose_name='学习建议')
    
    class Meta:
        verbose_name = '错题记录'
        verbose_name_plural = '错题记录'
        unique_together = ['user', 'question']
        ordering = ['-last_wrong_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.question.title}"
    
    def mark_as_mastered(self):
        """标记为已掌握"""
        self.is_mastered = True
        self.mastered_at = timezone.now()
        self.save(update_fields=['is_mastered', 'mastered_at'])


class StudyStats(models.Model):
    """学习统计"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    
    # 基础统计
    total_sessions = models.PositiveIntegerField(default=0, verbose_name='总练习次数')
    total_questions_answered = models.PositiveIntegerField(default=0, verbose_name='总答题数')
    total_correct_answers = models.PositiveIntegerField(default=0, verbose_name='总正确数')
    total_study_time = models.PositiveIntegerField(default=0, verbose_name='总学习时间(分钟)')
    
    # 错题统计
    total_wrong_answers = models.PositiveIntegerField(default=0, verbose_name='总错题数')
    mastered_wrong_answers = models.PositiveIntegerField(default=0, verbose_name='已掌握错题数')
    
    # 时间记录
    last_study_date = models.DateField(null=True, blank=True, verbose_name='最后学习日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '学习统计'
        verbose_name_plural = '学习统计'
    
    def __str__(self):
        return f"{self.user.username} - 学习统计"
    
    @property
    def overall_accuracy(self):
        """总体正确率"""
        if self.total_questions_answered == 0:
            return 0
        return round((self.total_correct_answers / self.total_questions_answered) * 100, 1)
    
    @property
    def wrong_answer_mastery_rate(self):
        """错题掌握率"""
        if self.total_wrong_answers == 0:
            return 0
        return round((self.mastered_wrong_answers / self.total_wrong_answers) * 100, 1)
    
    def update_stats(self):
        """更新统计数据"""
        # 更新基础统计
        sessions = QuizSession.objects.filter(user=self.user, status='completed')
        self.total_sessions = sessions.count()
        
        answers = QuizAnswer.objects.filter(session__user=self.user)
        self.total_questions_answered = answers.count()
        self.total_correct_answers = answers.filter(is_correct=True).count()
        
        # 计算总学习时间
        total_minutes = sum(session.duration for session in sessions)
        self.total_study_time = int(total_minutes)
        
        # 更新错题统计
        wrong_answers = WrongAnswer.objects.filter(user=self.user)
        self.total_wrong_answers = wrong_answers.count()
        self.mastered_wrong_answers = wrong_answers.filter(is_mastered=True).count()
        
        # 更新最后学习日期
        if sessions.exists():
            self.last_study_date = sessions.first().completed_at.date()
        
        self.save()
