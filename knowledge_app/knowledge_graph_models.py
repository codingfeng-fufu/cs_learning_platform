"""
知识图谱相关数据模型
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class ConceptNode(models.Model):
    """概念节点模型"""
    
    DIFFICULTY_CHOICES = [
        ('beginner', '初级'),
        ('intermediate', '中级'),
        ('advanced', '高级'),
        ('expert', '专家级'),
    ]
    
    CATEGORY_CHOICES = [
        ('algorithm', '算法'),
        ('data_structure', '数据结构'),
        ('network', '计算机网络'),
        ('os', '操作系统'),
        ('database', '数据库'),
        ('software_engineering', '软件工程'),
        ('programming', '编程语言'),
        ('ai', '人工智能'),
        ('security', '信息安全'),
        ('architecture', '计算机体系结构'),
        ('theory', '计算理论'),
        ('graphics', '计算机图形学'),
        ('hci', '人机交互'),
        ('distributed', '分布式系统'),
    ]
    
    # 基本信息
    name = models.CharField(max_length=200, unique=True, verbose_name='概念名称')
    name_en = models.CharField(max_length=200, blank=True, verbose_name='英文名称')
    description = models.TextField(verbose_name='概念描述')
    
    # 分类和难度
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES,
        verbose_name='所属分类'
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='beginner',
        verbose_name='难度等级'
    )
    
    # 重要性权重（用于图谱布局和推荐）
    importance_weight = models.FloatField(default=1.0, verbose_name='重要性权重')
    
    # 学习统计
    view_count = models.PositiveIntegerField(default=0, verbose_name='查看次数')
    learn_count = models.PositiveIntegerField(default=0, verbose_name='学习次数')
    
    # 扩展信息
    keywords = models.JSONField(default=list, blank=True, verbose_name='关键词')
    examples = models.JSONField(default=list, blank=True, verbose_name='示例')
    resources = models.JSONField(default=list, blank=True, verbose_name='学习资源')
    
    # 图谱位置信息（用于可视化布局）
    graph_position = models.JSONField(
        default=dict, 
        blank=True, 
        verbose_name='图谱位置',
        help_text='存储节点在图谱中的坐标信息'
    )
    
    # 状态管理
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '概念节点'
        verbose_name_plural = '概念节点'
        ordering = ['category', 'difficulty', 'name']
        indexes = [
            models.Index(fields=['category', 'difficulty']),
            models.Index(fields=['importance_weight']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def get_related_concepts(self, relation_type=None):
        """获取相关概念"""
        relations = ConceptRelation.objects.filter(
            models.Q(source_concept=self) | models.Q(target_concept=self),
            is_active=True
        )
        
        if relation_type:
            relations = relations.filter(relation_type=relation_type)
        
        return relations
    
    def get_prerequisites(self):
        """获取前置概念"""
        return ConceptRelation.objects.filter(
            target_concept=self,
            relation_type='prerequisite',
            is_active=True
        )
    
    def get_follow_ups(self):
        """获取后续概念"""
        return ConceptRelation.objects.filter(
            source_concept=self,
            relation_type='prerequisite',
            is_active=True
        )


class ConceptRelation(models.Model):
    """概念关系模型"""
    
    RELATION_TYPES = [
        ('prerequisite', '前置关系'),  # A是B的前置概念
        ('related', '相关关系'),      # A和B相关
        ('contains', '包含关系'),     # A包含B
        ('implements', '实现关系'),   # A实现了B
        ('extends', '扩展关系'),      # A扩展了B
        ('uses', '使用关系'),         # A使用了B
        ('similar', '相似关系'),      # A和B相似
        ('opposite', '对立关系'),     # A和B对立
    ]
    
    source_concept = models.ForeignKey(
        ConceptNode,
        on_delete=models.CASCADE,
        related_name='outgoing_relations',
        verbose_name='源概念'
    )
    target_concept = models.ForeignKey(
        ConceptNode,
        on_delete=models.CASCADE,
        related_name='incoming_relations',
        verbose_name='目标概念'
    )
    
    relation_type = models.CharField(
        max_length=20,
        choices=RELATION_TYPES,
        verbose_name='关系类型'
    )
    
    # 关系强度（0-1之间，用于图谱布局和推荐权重）
    strength = models.FloatField(default=0.5, verbose_name='关系强度')
    
    # 关系描述
    description = models.TextField(blank=True, verbose_name='关系描述')
    
    # 状态管理
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='创建者'
    )
    
    class Meta:
        verbose_name = '概念关系'
        verbose_name_plural = '概念关系'
        unique_together = ['source_concept', 'target_concept', 'relation_type']
        indexes = [
            models.Index(fields=['relation_type', 'strength']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.source_concept.name} --{self.get_relation_type_display()}--> {self.target_concept.name}"


class LearningPath(models.Model):
    """学习路径模型"""
    
    DIFFICULTY_LEVELS = [
        ('beginner', '初学者路径'),
        ('intermediate', '进阶路径'),
        ('advanced', '高级路径'),
        ('expert', '专家路径'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='路径名称')
    description = models.TextField(verbose_name='路径描述')
    
    # 路径属性
    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_LEVELS,
        default='beginner',
        verbose_name='难度等级'
    )
    estimated_hours = models.PositiveIntegerField(
        default=0,
        verbose_name='预计学习时长(小时)'
    )
    
    # 路径中的概念（有序）
    concepts = models.ManyToManyField(
        ConceptNode,
        through='PathStep',
        verbose_name='包含概念'
    )
    
    # 统计信息
    follower_count = models.PositiveIntegerField(default=0, verbose_name='关注人数')
    completion_count = models.PositiveIntegerField(default=0, verbose_name='完成人数')
    
    # 状态管理
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    is_featured = models.BooleanField(default=False, verbose_name='是否推荐')
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '学习路径'
        verbose_name_plural = '学习路径'
        ordering = ['-is_featured', '-follower_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_difficulty_level_display()})"
    
    def get_ordered_concepts(self):
        """获取有序的概念列表"""
        return self.concepts.through.objects.filter(
            learning_path=self
        ).order_by('order').select_related('concept')


class PathStep(models.Model):
    """学习路径步骤模型"""
    
    learning_path = models.ForeignKey(
        LearningPath,
        on_delete=models.CASCADE,
        verbose_name='学习路径'
    )
    concept = models.ForeignKey(
        ConceptNode,
        on_delete=models.CASCADE,
        verbose_name='概念'
    )
    
    order = models.PositiveIntegerField(verbose_name='顺序')
    is_required = models.BooleanField(default=True, verbose_name='是否必需')
    estimated_time = models.PositiveIntegerField(
        default=60,
        verbose_name='预计学习时间(分钟)'
    )
    
    # 步骤说明
    notes = models.TextField(blank=True, verbose_name='学习说明')
    
    class Meta:
        verbose_name = '路径步骤'
        verbose_name_plural = '路径步骤'
        unique_together = ['learning_path', 'concept']
        ordering = ['learning_path', 'order']
    
    def __str__(self):
        return f"{self.learning_path.name} - 步骤{self.order}: {self.concept.name}"


class UserLearningProgress(models.Model):
    """用户学习进度模型"""
    
    STATUS_CHOICES = [
        ('not_started', '未开始'),
        ('in_progress', '学习中'),
        ('completed', '已完成'),
        ('mastered', '已掌握'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    concept = models.ForeignKey(ConceptNode, on_delete=models.CASCADE, verbose_name='概念')
    
    # 学习状态
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started',
        verbose_name='学习状态'
    )
    
    # 掌握程度（0-100）
    mastery_level = models.PositiveIntegerField(default=0, verbose_name='掌握程度')
    
    # 时间统计
    total_study_time = models.PositiveIntegerField(default=0, verbose_name='总学习时间(分钟)')
    last_studied_at = models.DateTimeField(null=True, blank=True, verbose_name='最后学习时间')
    
    # 学习次数
    study_sessions = models.PositiveIntegerField(default=0, verbose_name='学习次数')
    
    # 相关学习路径
    learning_paths = models.ManyToManyField(
        LearningPath,
        blank=True,
        verbose_name='相关学习路径'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户学习进度'
        verbose_name_plural = '用户学习进度'
        unique_together = ['user', 'concept']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['mastery_level']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.concept.name} ({self.get_status_display()})"
    
    def update_progress(self, study_time_minutes=0):
        """更新学习进度"""
        self.study_sessions += 1
        self.total_study_time += study_time_minutes
        self.last_studied_at = timezone.now()
        
        # 根据学习时间和次数计算掌握程度
        base_mastery = min(self.study_sessions * 10, 50)  # 基础掌握度
        time_bonus = min(self.total_study_time // 30, 30)  # 时间奖励
        self.mastery_level = min(base_mastery + time_bonus, 100)
        
        # 更新状态
        if self.mastery_level >= 90:
            self.status = 'mastered'
        elif self.mastery_level >= 70:
            self.status = 'completed'
        elif self.mastery_level > 0:
            self.status = 'in_progress'
        
        self.save()
