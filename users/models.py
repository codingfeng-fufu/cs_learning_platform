from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

class User(AbstractUser):
    """扩展的用户模型"""
    email = models.EmailField(unique=True, verbose_name='邮箱')
    is_email_verified = models.BooleanField(default=False, verbose_name='邮箱已验证')
    # avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')  # 需要安装Pillow
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    birth_date = models.DateField(blank=True, null=True, verbose_name='出生日期')
    location = models.CharField(max_length=100, blank=True, verbose_name='所在地')
    website = models.URLField(blank=True, verbose_name='个人网站')
    github_username = models.CharField(max_length=100, blank=True, verbose_name='GitHub用户名')

    # 学习相关字段
    total_study_time = models.PositiveIntegerField(default=0, verbose_name='总学习时间(分钟)')
    points = models.PositiveIntegerField(default=0, verbose_name='学习积分')
    level = models.PositiveIntegerField(default=1, verbose_name='用户等级')

    # 偏好设置
    preferred_language = models.CharField(
        max_length=10,
        choices=[
            ('zh', '中文'),
            ('en', 'English'),
        ],
        default='zh',
        verbose_name='首选语言'
    )
    email_notifications = models.BooleanField(default=True, verbose_name='接收邮件通知')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.email

    def get_full_name(self):
        """获取用户全名"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def get_display_name(self):
        """获取显示名称"""
        if self.first_name:
            return self.first_name
        return self.username


class EmailVerificationToken(models.Model):
    """邮箱验证令牌"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    token = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='验证令牌')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    is_used = models.BooleanField(default=False, verbose_name='已使用')

    class Meta:
        verbose_name = '邮箱验证令牌'
        verbose_name_plural = '邮箱验证令牌'

    def __str__(self):
        return f"{self.user.email} - {self.token}"

    def is_expired(self):
        """检查令牌是否过期"""
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # 设置24小时后过期
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)


class PasswordResetToken(models.Model):
    """密码重置令牌"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    token = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='重置令牌')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    is_used = models.BooleanField(default=False, verbose_name='已使用')

    class Meta:
        verbose_name = '密码重置令牌'
        verbose_name_plural = '密码重置令牌'

    def __str__(self):
        return f"{self.user.email} - {self.token}"

    def is_expired(self):
        """检查令牌是否过期"""
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # 设置1小时后过期
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """用户学习档案"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')

    # 学习统计
    total_knowledge_points = models.PositiveIntegerField(default=0, verbose_name='已学知识点数')
    completed_exercises = models.PositiveIntegerField(default=0, verbose_name='完成练习数')
    correct_rate = models.FloatField(default=0.0, verbose_name='正确率')

    # 学习偏好
    study_goal = models.CharField(
        max_length=50,
        choices=[
            ('beginner', '入门学习'),
            ('interview', '面试准备'),
            ('advanced', '深入研究'),
            ('review', '复习巩固'),
        ],
        default='beginner',
        verbose_name='学习目标'
    )

    daily_study_goal = models.PositiveIntegerField(default=30, verbose_name='每日学习目标(分钟)')

    # 最后活动
    last_study_date = models.DateField(blank=True, null=True, verbose_name='最后学习日期')
    current_streak = models.PositiveIntegerField(default=0, verbose_name='连续学习天数')
    longest_streak = models.PositiveIntegerField(default=0, verbose_name='最长连续学习天数')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户档案'
        verbose_name_plural = '用户档案'

    def __str__(self):
        return f"{self.user.email} - 档案"


class KnowledgePoint(models.Model):
    """知识点模型"""
    slug = models.CharField(max_length=100, unique=True, verbose_name='标识符')
    title = models.CharField(max_length=200, verbose_name='标题')
    category = models.CharField(max_length=100, verbose_name='分类')
    subcategory = models.CharField(max_length=100, verbose_name='子分类')
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('beginner', '初级'),
            ('intermediate', '中级'),
            ('advanced', '高级'),
        ],
        default='beginner',
        verbose_name='难度'
    )
    estimated_time = models.PositiveIntegerField(default=30, verbose_name='预计学习时间(分钟)')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '知识点'
        verbose_name_plural = '知识点'

    def __str__(self):
        return self.title


class StudySession(models.Model):
    """学习会话记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    knowledge_point = models.ForeignKey(KnowledgePoint, on_delete=models.CASCADE, verbose_name='知识点')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(blank=True, null=True, verbose_name='结束时间')
    duration = models.PositiveIntegerField(default=0, verbose_name='学习时长(秒)')
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    progress_percentage = models.FloatField(default=0.0, verbose_name='进度百分比')

    class Meta:
        verbose_name = '学习会话'
        verbose_name_plural = '学习会话'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.user.username} - {self.knowledge_point.title}"

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            self.duration = int((self.end_time - self.start_time).total_seconds())
        super().save(*args, **kwargs)


class UserKnowledgeProgress(models.Model):
    """用户知识点进度"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    knowledge_point = models.ForeignKey(KnowledgePoint, on_delete=models.CASCADE, verbose_name='知识点')
    status = models.CharField(
        max_length=20,
        choices=[
            ('not_started', '未开始'),
            ('in_progress', '学习中'),
            ('completed', '已完成'),
            ('mastered', '已掌握'),
        ],
        default='not_started',
        verbose_name='学习状态'
    )
    progress_percentage = models.FloatField(default=0.0, verbose_name='进度百分比')
    total_study_time = models.PositiveIntegerField(default=0, verbose_name='总学习时间(秒)')
    first_accessed = models.DateTimeField(auto_now_add=True, verbose_name='首次访问')
    last_accessed = models.DateTimeField(auto_now=True, verbose_name='最后访问')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='完成时间')

    class Meta:
        verbose_name = '用户知识点进度'
        verbose_name_plural = '用户知识点进度'
        unique_together = ['user', 'knowledge_point']

    def __str__(self):
        return f"{self.user.username} - {self.knowledge_point.title} ({self.get_status_display()})"


class Achievement(models.Model):
    """成就模型"""
    name = models.CharField(max_length=100, verbose_name='成就名称')
    description = models.TextField(verbose_name='成就描述')
    icon = models.CharField(max_length=10, default='🏆', verbose_name='图标')
    category = models.CharField(
        max_length=50,
        choices=[
            ('learning', '学习成就'),
            ('time', '时间成就'),
            ('streak', '连续成就'),
            ('completion', '完成成就'),
            ('special', '特殊成就'),
        ],
        default='learning',
        verbose_name='成就类别'
    )
    condition_type = models.CharField(
        max_length=50,
        choices=[
            ('knowledge_points', '完成知识点数量'),
            ('study_time', '累计学习时间'),
            ('streak_days', '连续学习天数'),
            ('category_complete', '完成分类'),
            ('first_login', '首次登录'),
        ],
        verbose_name='达成条件类型'
    )
    condition_value = models.PositiveIntegerField(verbose_name='条件数值')
    points_reward = models.PositiveIntegerField(default=0, verbose_name='奖励积分')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '成就'
        verbose_name_plural = '成就'

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """用户成就记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, verbose_name='成就')
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name='获得时间')

    class Meta:
        verbose_name = '用户成就'
        verbose_name_plural = '用户成就'
        unique_together = ['user', 'achievement']
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"
