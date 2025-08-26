from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class SearchHistory(models.Model):
    """用户搜索历史"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', null=True, blank=True)
    query = models.CharField(max_length=200, verbose_name='搜索词')
    results_count = models.PositiveIntegerField(default=0, verbose_name='结果数量')
    clicked_result = models.CharField(max_length=100, blank=True, verbose_name='点击的结果')
    search_time = models.DateTimeField(auto_now_add=True, verbose_name='搜索时间')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    
    class Meta:
        verbose_name = '搜索历史'
        verbose_name_plural = '搜索历史'
        ordering = ['-search_time']
        indexes = [
            models.Index(fields=['user', '-search_time']),
            models.Index(fields=['query']),
        ]
    
    def __str__(self):
        return f"{self.user or 'Anonymous'} - {self.query}"


class PopularSearch(models.Model):
    """热门搜索"""
    query = models.CharField(max_length=200, unique=True, verbose_name='搜索词')
    search_count = models.PositiveIntegerField(default=0, verbose_name='搜索次数')
    last_searched = models.DateTimeField(auto_now=True, verbose_name='最后搜索时间')
    is_trending = models.BooleanField(default=False, verbose_name='是否热门')
    category = models.CharField(
        max_length=50,
        choices=[
            ('data_structure', '数据结构'),
            ('algorithm', '算法'),
            ('network', '计算机网络'),
            ('os', '操作系统'),
            ('database', '数据库'),
            ('software_engineering', '软件工程'),
            ('other', '其他'),
        ],
        default='other',
        verbose_name='分类'
    )
    
    class Meta:
        verbose_name = '热门搜索'
        verbose_name_plural = '热门搜索'
        ordering = ['-search_count', '-last_searched']
    
    def __str__(self):
        return f"{self.query} ({self.search_count}次)"


class SearchSuggestion(models.Model):
    """搜索建议"""
    query = models.CharField(max_length=200, verbose_name='原始查询')
    suggestion = models.CharField(max_length=200, verbose_name='建议词')
    suggestion_type = models.CharField(
        max_length=20,
        choices=[
            ('correction', '拼写纠正'),
            ('completion', '自动补全'),
            ('related', '相关搜索'),
            ('synonym', '同义词'),
        ],
        verbose_name='建议类型'
    )
    confidence = models.FloatField(default=1.0, verbose_name='置信度')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '搜索建议'
        verbose_name_plural = '搜索建议'
        unique_together = ['query', 'suggestion']
    
    def __str__(self):
        return f"{self.query} -> {self.suggestion}"


class KnowledgePointIndex(models.Model):
    """知识点搜索索引"""
    slug = models.CharField(max_length=100, unique=True, verbose_name='标识符')
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(verbose_name='描述')
    content = models.TextField(verbose_name='内容')
    keywords = models.TextField(verbose_name='关键词')
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
    view_count = models.PositiveIntegerField(default=0, verbose_name='浏览次数')
    search_count = models.PositiveIntegerField(default=0, verbose_name='搜索次数')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='最后更新')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    class Meta:
        verbose_name = '知识点索引'
        verbose_name_plural = '知识点索引'
        indexes = [
            models.Index(fields=['category', 'subcategory']),
            models.Index(fields=['difficulty']),
            models.Index(fields=['-view_count']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_search_score(self, query):
        """计算搜索相关性得分"""
        score = 0
        query_lower = query.lower()
        
        # 标题匹配（权重最高）
        if query_lower in self.title.lower():
            score += 100
            if self.title.lower().startswith(query_lower):
                score += 50
        
        # 关键词匹配
        if query_lower in self.keywords.lower():
            score += 80
        
        # 描述匹配
        if query_lower in self.description.lower():
            score += 60
        
        # 内容匹配
        if query_lower in self.content.lower():
            score += 40
        
        # 分类匹配
        if query_lower in self.category.lower() or query_lower in self.subcategory.lower():
            score += 30
        
        # 考虑浏览次数（热门程度）
        score += min(self.view_count / 100, 20)
        
        return score


class SearchFilter(models.Model):
    """搜索过滤器"""
    name = models.CharField(max_length=50, verbose_name='过滤器名称')
    filter_type = models.CharField(
        max_length=20,
        choices=[
            ('category', '分类'),
            ('difficulty', '难度'),
            ('duration', '时长'),
            ('status', '状态'),
        ],
        verbose_name='过滤器类型'
    )
    filter_value = models.CharField(max_length=100, verbose_name='过滤值')
    display_name = models.CharField(max_length=100, verbose_name='显示名称')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='排序')
    
    class Meta:
        verbose_name = '搜索过滤器'
        verbose_name_plural = '搜索过滤器'
        ordering = ['filter_type', 'sort_order']
    
    def __str__(self):
        return f"{self.get_filter_type_display()} - {self.display_name}"
