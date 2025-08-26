"""
学习资源聚合器 - 数据模型
独立设计，支持多种数据库后端
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
import json
from typing import Dict, List, Optional


class ResourceCategory(models.Model):
    """工具和资源分类"""
    name = models.CharField(max_length=100, unique=True, verbose_name="分类名称")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="分类标识")
    description = models.TextField(blank=True, verbose_name="分类描述")
    icon = models.CharField(max_length=50, default="🛠️", verbose_name="图标")
    color = models.CharField(max_length=7, default="#667eea", verbose_name="主题色")
    order = models.IntegerField(default=0, verbose_name="排序")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "工具分类"
        verbose_name_plural = "工具分类"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class ResourceSource(models.Model):
    """资源来源平台"""
    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('bilibili', 'Bilibili'),
        ('github', 'GitHub'),
        ('stackoverflow', 'Stack Overflow'),
        ('medium', 'Medium'),
        ('arxiv', 'arXiv'),
        ('coursera', 'Coursera'),
        ('edux', 'edX'),
        ('custom', '自定义'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="平台名称")
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, verbose_name="平台类型")
    base_url = models.URLField(verbose_name="基础URL")
    api_endpoint = models.URLField(blank=True, verbose_name="API端点")
    api_key = models.CharField(max_length=200, blank=True, verbose_name="API密钥")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    rate_limit = models.IntegerField(default=60, verbose_name="每分钟请求限制")
    priority = models.IntegerField(default=1, verbose_name="优先级")
    
    class Meta:
        verbose_name = "资源来源"
        verbose_name_plural = "资源来源"
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_platform_display()})"


class LearningResource(models.Model):
    """实用工具和学习资源"""
    RESOURCE_TYPE_CHOICES = [
        ('tool', '开发工具'),
        ('design', '设计工具'),
        ('ai', 'AI工具'),
        ('course', '在线课程'),
        ('video', '视频教程'),
        ('article', '技术文章'),
        ('book', '电子书籍'),
        ('documentation', '官方文档'),
        ('github', '开源项目'),
        ('website', '实用网站'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', '初级'),
        ('intermediate', '中级'),
        ('advanced', '高级'),
    ]
    
    # 基本信息
    title = models.CharField(max_length=300, verbose_name="工具/资源名称")
    description = models.TextField(verbose_name="详细描述")
    short_description = models.CharField(max_length=200, blank=True, verbose_name="简短描述")
    url = models.URLField(verbose_name="官方链接")
    thumbnail = models.URLField(blank=True, verbose_name="图标/截图")

    # 工具特性
    is_free = models.BooleanField(default=True, verbose_name="是否免费")
    price_info = models.CharField(max_length=100, blank=True, verbose_name="价格信息")
    features = models.JSONField(default=list, verbose_name="主要功能特性")
    pros_cons = models.JSONField(default=dict, verbose_name="优缺点", help_text="格式: {'pros': ['优点1', '优点2'], 'cons': ['缺点1']}")

    # 使用信息
    platform_support = models.JSONField(default=list, verbose_name="支持平台", help_text="如: ['Web', 'Windows', 'macOS', 'Linux']")
    usage_tips = models.TextField(blank=True, verbose_name="使用技巧")
    
    # 分类信息
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE, verbose_name="分类")
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES, verbose_name="资源类型")
    source = models.ForeignKey(ResourceSource, on_delete=models.CASCADE, verbose_name="来源")
    
    # 质量指标
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='intermediate', verbose_name="难度")
    rating = models.FloatField(default=0.0, verbose_name="评分")
    view_count = models.IntegerField(default=0, verbose_name="观看数")
    like_count = models.IntegerField(default=0, verbose_name="点赞数")
    
    # 元数据
    author = models.CharField(max_length=200, blank=True, verbose_name="作者")
    duration = models.CharField(max_length=50, blank=True, verbose_name="时长")
    language = models.CharField(max_length=10, default='zh-CN', verbose_name="语言")
    tags = models.JSONField(default=list, verbose_name="标签")
    
    # 系统字段
    external_id = models.CharField(max_length=200, blank=True, verbose_name="外部ID")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="最后更新")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    
    class Meta:
        verbose_name = "学习资源"
        verbose_name_plural = "学习资源"
        ordering = ['-rating', '-view_count', '-created_at']
        indexes = [
            models.Index(fields=['category', 'resource_type']),
            models.Index(fields=['source', 'external_id']),
            models.Index(fields=['-rating', '-view_count']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def tags_list(self) -> List[str]:
        """获取标签列表"""
        return self.tags if isinstance(self.tags, list) else []
    
    def add_tag(self, tag: str):
        """添加标签"""
        if tag not in self.tags_list:
            self.tags = self.tags_list + [tag]
            self.save()
    
    def remove_tag(self, tag: str):
        """移除标签"""
        tags = self.tags_list
        if tag in tags:
            tags.remove(tag)
            self.tags = tags
            self.save()


class UserResourceInteraction(models.Model):
    """用户资源交互记录"""
    ACTION_CHOICES = [
        ('view', '查看'),
        ('like', '点赞'),
        ('bookmark', '收藏'),
        ('share', '分享'),
        ('complete', '完成'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE, verbose_name="资源")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="操作类型")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    metadata = models.JSONField(default=dict, verbose_name="额外数据")
    
    class Meta:
        verbose_name = "用户资源交互"
        verbose_name_plural = "用户资源交互"
        unique_together = ['user', 'resource', 'action']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['resource', 'action']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.get_action_display()} {self.resource.title}"


class ResourceCache(models.Model):
    """资源缓存"""
    cache_key = models.CharField(max_length=200, unique=True, verbose_name="缓存键")
    data = models.JSONField(verbose_name="缓存数据")
    expires_at = models.DateTimeField(verbose_name="过期时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "资源缓存"
        verbose_name_plural = "资源缓存"
        indexes = [
            models.Index(fields=['expires_at']),
        ]
    
    @classmethod
    def get_cached_data(cls, key: str) -> Optional[Dict]:
        """获取缓存数据"""
        try:
            cache = cls.objects.get(cache_key=key, expires_at__gt=timezone.now())
            return cache.data
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def set_cached_data(cls, key: str, data: Dict, timeout: int = 3600):
        """设置缓存数据"""
        expires_at = timezone.now() + timezone.timedelta(seconds=timeout)
        cls.objects.update_or_create(
            cache_key=key,
            defaults={'data': data, 'expires_at': expires_at}
        )
    
    @classmethod
    def clear_expired(cls):
        """清理过期缓存"""
        cls.objects.filter(expires_at__lt=timezone.now()).delete()
