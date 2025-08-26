from django.contrib import admin
from .models import KnowledgePoint, DailyTerm, TermHistory, AIExerciseSession
from .search_models import (
    SearchHistory, PopularSearch, SearchSuggestion,
    KnowledgePointIndex, SearchFilter
)


@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'get_category_display_with_icon',
        'difficulty',
        'is_active',
        'is_implemented',
        'order',
        'created_at'
    ]
    list_filter = ['category', 'difficulty', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'slug']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order', 'created_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'description', 'icon')
        }),
        ('分类设置', {
            'fields': ('category', 'difficulty')
        }),
        ('显示设置', {
            'fields': ('is_active', 'order')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def get_category_display_with_icon(self, obj):
        """在管理界面显示带图标的分类"""
        return obj.get_category_display_with_icon()

    get_category_display_with_icon.short_description = '分类'

    def is_implemented(self, obj):
        """显示是否已实现"""
        if obj.is_implemented:
            return "✅ 已实现"
        else:
            return "⏳ 开发中"

    is_implemented.short_description = '实现状态'

    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        """批量启用知识点"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功启用 {updated} 个知识点。')

    make_active.short_description = "启用选中的知识点"

    def make_inactive(self, request, queryset):
        """批量禁用知识点"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功禁用 {updated} 个知识点。')

    make_inactive.short_description = "禁用选中的知识点"


# 搜索相关模型管理
@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'results_count', 'search_time', 'ip_address')
    list_filter = ('search_time', 'results_count')
    search_fields = ('query', 'user__email')
    readonly_fields = ('search_time',)
    date_hierarchy = 'search_time'

@admin.register(PopularSearch)
class PopularSearchAdmin(admin.ModelAdmin):
    list_display = ('query', 'search_count', 'category', 'is_trending', 'last_searched')
    list_filter = ('category', 'is_trending', 'last_searched')
    search_fields = ('query',)
    ordering = ('-search_count', '-last_searched')

@admin.register(SearchSuggestion)
class SearchSuggestionAdmin(admin.ModelAdmin):
    list_display = ('query', 'suggestion', 'suggestion_type', 'confidence', 'is_active')
    list_filter = ('suggestion_type', 'is_active')
    search_fields = ('query', 'suggestion')

@admin.register(KnowledgePointIndex)
class KnowledgePointIndexAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'view_count', 'search_count', 'is_active')
    list_filter = ('category', 'difficulty', 'is_active')
    search_fields = ('title', 'keywords', 'description')
    ordering = ('-view_count', '-search_count')

@admin.register(SearchFilter)
class SearchFilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'filter_type', 'display_name', 'is_active', 'sort_order')
    list_filter = ('filter_type', 'is_active')
    search_fields = ('name', 'display_name')
    ordering = ('filter_type', 'sort_order')

# 每日名词管理
@admin.register(DailyTerm)
class DailyTermAdmin(admin.ModelAdmin):
    list_display = [
        'display_date',
        'term',
        'category',
        'difficulty_level',
        'status',
        'view_count',
        'like_count',
        'api_source',
        'created_at'
    ]
    list_filter = [
        'status',
        'difficulty_level',
        'category',
        'api_source',
        'display_date',
        'created_at'
    ]
    search_fields = ['term', 'explanation', 'category']
    list_editable = ['status']
    date_hierarchy = 'display_date'
    ordering = ['-display_date']

    fieldsets = (
        ('基本信息', {
            'fields': ('term', 'explanation', 'display_date')
        }),
        ('分类设置', {
            'fields': ('category', 'difficulty_level')
        }),
        ('状态管理', {
            'fields': ('status',)
        }),
        ('统计信息', {
            'fields': ('view_count', 'like_count'),
            'classes': ('collapse',)
        }),
        ('扩展信息', {
            'fields': ('extended_info',),
            'classes': ('collapse',)
        }),
        ('API信息', {
            'fields': ('api_source', 'api_request_time'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'api_request_time']

    actions = ['make_active', 'make_archived', 'regenerate_term']

    def make_active(self, request, queryset):
        """批量设为活跃状态"""
        updated = queryset.update(status='active')
        self.message_user(request, f'成功激活 {updated} 个名词。')

    make_active.short_description = "设为活跃状态"

    def make_archived(self, request, queryset):
        """批量归档"""
        updated = queryset.update(status='archived')
        self.message_user(request, f'成功归档 {updated} 个名词。')

    make_archived.short_description = "归档选中的名词"

    def regenerate_term(self, request, queryset):
        """重新生成名词解释"""
        from .services.daily_term_service import DailyTermService
        service = DailyTermService()

        success_count = 0
        for term in queryset:
            try:
                explanation_data = service.api_client.get_term_explanation(term.term)
                if explanation_data:
                    term.explanation = explanation_data['explanation']
                    term.category = explanation_data['category']
                    term.difficulty_level = explanation_data['difficulty']
                    term.extended_info = explanation_data['extended_info']
                    term.api_request_time = timezone.now()
                    term.save()
                    success_count += 1
            except Exception as e:
                continue

        self.message_user(request, f'成功重新生成 {success_count} 个名词解释。')

    regenerate_term.short_description = "重新生成名词解释"


@admin.register(TermHistory)
class TermHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'original_term',
        'term_lower',
        'first_used_date',
        'usage_count',
        'created_at'
    ]
    list_filter = ['first_used_date', 'usage_count', 'created_at']
    search_fields = ['original_term', 'term_lower']
    readonly_fields = ['created_at']
    date_hierarchy = 'first_used_date'
    ordering = ['-usage_count', '-first_used_date']

    def has_add_permission(self, request):
        """禁止手动添加历史记录"""
        return False


@admin.register(AIExerciseSession)
class AIExerciseSessionAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'knowledge_point',
        'score',
        'accuracy_rate_display',
        'total_questions',
        'difficulty_level',
        'is_completed',
        'started_at'
    ]
    list_filter = [
        'is_completed',
        'difficulty_level',
        'knowledge_point',
        'started_at',
        'api_source'
    ]
    search_fields = ['user__username', 'knowledge_point']
    readonly_fields = [
        'started_at',
        'completed_at',
        'exercises',
        'user_answers',
        'score',
        'correct_count',
        'total_questions'
    ]
    date_hierarchy = 'started_at'
    ordering = ['-started_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'knowledge_point', 'difficulty_level')
        }),
        ('练习内容', {
            'fields': ('exercises', 'user_answers'),
            'classes': ('collapse',)
        }),
        ('成绩统计', {
            'fields': ('score', 'correct_count', 'total_questions', 'is_completed')
        }),
        ('时间信息', {
            'fields': ('started_at', 'completed_at', 'time_spent')
        }),
        ('技术信息', {
            'fields': ('api_source',),
            'classes': ('collapse',)
        }),
    )

    def accuracy_rate_display(self, obj):
        """显示正确率"""
        return f"{obj.get_accuracy_rate():.1f}%"

    accuracy_rate_display.short_description = "正确率"

    def has_add_permission(self, request):
        """禁止手动添加练习会话"""
        return False


# 导入练习题管理配置
from .exercise_admin import *

# 自定义管理站点配置
admin.site.site_header = '计算机科学学习平台管理'
admin.site.site_title = 'CS学习平台'
admin.site.index_title = '欢迎使用管理后台'