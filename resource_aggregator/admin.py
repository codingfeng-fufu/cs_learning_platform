"""
学习资源聚合器 - 管理后台
独立的管理界面配置
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import ResourceCategory, ResourceSource, LearningResource, UserResourceInteraction, ResourceCache


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'color_preview', 'resource_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 50%; display: inline-block;"></div>',
            obj.color
        )
    color_preview.short_description = '颜色预览'
    
    def resource_count(self, obj):
        count = obj.learningresource_set.count()
        if count > 0:
            url = reverse('admin:resource_aggregator_learningresource_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} 个资源</a>', url, count)
        return '0 个资源'
    resource_count.short_description = '资源数量'


@admin.register(ResourceSource)
class ResourceSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform', 'is_active', 'priority', 'rate_limit', 'resource_count']
    list_filter = ['platform', 'is_active']
    search_fields = ['name', 'base_url']
    list_editable = ['is_active', 'priority', 'rate_limit']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'platform', 'base_url', 'is_active', 'priority')
        }),
        ('API配置', {
            'fields': ('api_endpoint', 'api_key', 'rate_limit'),
            'classes': ('collapse',)
        }),
    )
    
    def resource_count(self, obj):
        count = obj.learningresource_set.count()
        if count > 0:
            url = reverse('admin:resource_aggregator_learningresource_changelist') + f'?source__id__exact={obj.id}'
            return format_html('<a href="{}">{} 个资源</a>', url, count)
        return '0 个资源'
    resource_count.short_description = '资源数量'


@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'category', 'source', 'difficulty', 'rating', 'view_count', 'is_active', 'created_at']
    list_filter = ['resource_type', 'category', 'source', 'difficulty', 'is_active', 'language', 'created_at']
    search_fields = ['title', 'description', 'author', 'tags']
    list_editable = ['is_active', 'difficulty', 'rating']
    readonly_fields = ['external_id', 'created_at', 'last_updated', 'thumbnail_preview']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'url', 'thumbnail', 'thumbnail_preview')
        }),
        ('分类信息', {
            'fields': ('category', 'resource_type', 'source', 'difficulty')
        }),
        ('质量指标', {
            'fields': ('rating', 'view_count', 'like_count', 'author', 'duration', 'language')
        }),
        ('元数据', {
            'fields': ('tags', 'external_id', 'is_active'),
            'classes': ('collapse',)
        }),
        ('系统信息', {
            'fields': ('created_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 150px;" />', obj.thumbnail)
        return '无缩略图'
    thumbnail_preview.short_description = '缩略图预览'
    
    actions = ['mark_active', 'mark_inactive', 'update_ratings']
    
    def mark_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'已激活 {updated} 个资源')
    mark_active.short_description = '标记为激活'
    
    def mark_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'已停用 {updated} 个资源')
    mark_inactive.short_description = '标记为停用'
    
    def update_ratings(self, request, queryset):
        # 这里可以添加更新评分的逻辑
        self.message_user(request, '评分更新功能待实现')
    update_ratings.short_description = '更新评分'


@admin.register(UserResourceInteraction)
class UserResourceInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource_title', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'resource__title']
    readonly_fields = ['created_at']
    
    def resource_title(self, obj):
        return obj.resource.title[:50] + ('...' if len(obj.resource.title) > 50 else '')
    resource_title.short_description = '资源标题'
    
    def has_add_permission(self, request):
        return False  # 不允许手动添加交互记录


@admin.register(ResourceCache)
class ResourceCacheAdmin(admin.ModelAdmin):
    list_display = ['cache_key', 'expires_at', 'created_at', 'is_expired']
    list_filter = ['expires_at', 'created_at']
    search_fields = ['cache_key']
    readonly_fields = ['created_at']
    
    def is_expired(self, obj):
        from django.utils import timezone
        expired = obj.expires_at < timezone.now()
        if expired:
            return format_html('<span style="color: red;">已过期</span>')
        return format_html('<span style="color: green;">有效</span>')
    is_expired.short_description = '状态'
    
    actions = ['clear_expired_cache']
    
    def clear_expired_cache(self, request, queryset):
        from django.utils import timezone
        expired_count = ResourceCache.objects.filter(expires_at__lt=timezone.now()).count()
        ResourceCache.clear_expired()
        self.message_user(request, f'已清理 {expired_count} 个过期缓存')
    clear_expired_cache.short_description = '清理过期缓存'


# 自定义管理站点标题
admin.site.site_header = '学习资源聚合器管理'
admin.site.site_title = '资源管理'
admin.site.index_title = '欢迎使用学习资源聚合器管理系统'
