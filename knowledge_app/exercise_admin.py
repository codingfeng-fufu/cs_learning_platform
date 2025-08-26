from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django import forms
from django.forms import widgets
from .exercise_models import (
    ExerciseCategory, ExerciseDifficulty, Exercise, ExerciseSet,
    ExerciseSetItem, UserExerciseAttempt, UserExerciseSetAttempt
)
import json


class OptionsWidget(widgets.Textarea):
    """自定义选项编辑器组件"""

    def __init__(self, attrs=None):
        default_attrs = {'class': 'options-widget', 'rows': 6}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_value(self, value):
        if value is None:
            return ''
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False, indent=2)
        return value

    class Media:
        css = {
            'all': ('admin/css/exercise_admin.css',)
        }
        js = ('admin/js/exercise_admin.js',)


class HintsWidget(widgets.Textarea):
    """自定义提示编辑器组件"""

    def __init__(self, attrs=None):
        default_attrs = {'class': 'hints-widget', 'rows': 4}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_value(self, value):
        if value is None:
            return ''
        if isinstance(value, list):
            return json.dumps(value, ensure_ascii=False, indent=2)
        return value

    class Media:
        css = {
            'all': ('admin/css/exercise_admin.css',)
        }
        js = ('admin/js/exercise_admin.js',)


class ExerciseAdminForm(forms.ModelForm):
    """练习题管理表单"""

    class Meta:
        model = Exercise
        fields = '__all__'
        widgets = {
            'options': OptionsWidget(),
            'hints': HintsWidget(),
            'question_text': forms.Textarea(attrs={'rows': 4}),
            'explanation': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 添加帮助文本
        self.fields['options'].help_text = '选择题选项，JSON格式。例如：{"A": "选项A", "B": "选项B"}'
        self.fields['hints'].help_text = '提示信息，JSON数组格式。例如：["提示1", "提示2"]'
        self.fields['correct_answer'].help_text = '正确答案。单选题：A；多选题：A,C,D；判断题：true/false'

        # 根据题目类型调整字段
        if self.instance and self.instance.pk:
            question_type = self.instance.question_type
            if question_type not in ['single_choice', 'multiple_choice']:
                self.fields['options'].widget = forms.HiddenInput()
                self.fields['options'].required = False

@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_display', 'color_display', 'exercise_count', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    
    def icon_display(self, obj):
        return format_html('<span style="font-size: 1.5em;">{}</span>', obj.icon)
    icon_display.short_description = '图标'
    
    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = '颜色'
    
    def exercise_count(self, obj):
        count = obj.exercise_set.count()
        return format_html('<strong>{}</strong>', count)
    exercise_count.short_description = '题目数量'


@admin.register(ExerciseDifficulty)
class ExerciseDifficultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'color_display', 'description')
    ordering = ('level',)
    
    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></div>',
            obj.color
        )
    color_display.short_description = '颜色'


class ExerciseSetItemInline(admin.TabularInline):
    model = ExerciseSetItem
    extra = 0
    fields = ('exercise', 'order', 'points')
    ordering = ('order',)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    form = ExerciseAdminForm
    list_display = (
        'title', 'category', 'difficulty', 'question_type', 'success_rate_display',
        'view_count', 'is_featured', 'is_active', 'created_at'
    )
    list_filter = ('category', 'difficulty', 'question_type', 'is_featured', 'is_active', 'created_at')
    search_fields = ('title', 'question_text', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('view_count', 'attempt_count', 'correct_count', 'success_rate_display', 'preview_link')

    # 自定义表单模板
    change_form_template = 'admin/exercise_change_form.html'
    add_form_template = 'admin/exercise_add_form.html'

    fieldsets = (
        ('📋 基本信息', {
            'fields': ('title', 'slug', 'category', 'difficulty', 'question_type', 'tags'),
            'description': '填写题目的基本信息。标题要简洁明确，系统会自动生成URL标识。'
        }),
        ('📝 题目内容', {
            'fields': ('question_text', 'question_image', 'options', 'correct_answer'),
            'description': '编写题目内容。对于选择题，请在选项字段中填写JSON格式的选项。'
        }),
        ('💡 解析和提示', {
            'fields': ('explanation', 'explanation_image', 'hints'),
            'description': '提供详细的答案解析和分步提示，帮助学生理解题目。'
        }),
        ('⚙️ 设置', {
            'fields': ('time_limit', 'is_active', 'is_featured'),
            'description': '设置题目的时间限制和状态。时间限制为0表示无限制。'
        }),
        ('📊 统计信息', {
            'fields': ('view_count', 'attempt_count', 'correct_count', 'success_rate_display', 'preview_link'),
            'classes': ('collapse',),
            'description': '题目的使用统计数据，系统自动更新。'
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/exercise_admin.css',)
        }
        js = ('admin/js/exercise_admin.js',)
    
    def success_rate_display(self, obj):
        rate = obj.success_rate
        color = '#28a745' if rate >= 70 else '#ffc107' if rate >= 40 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, rate
        )
    success_rate_display.short_description = '正确率'

    def preview_link(self, obj):
        """题目预览链接"""
        if obj.pk:
            url = reverse('knowledge_app:exercise_preview', args=[obj.pk])
            return format_html(
                '<a href="{}" target="_blank" class="button">🔍 预览题目</a>',
                url
            )
        return '-'
    preview_link.short_description = '预览'



    def options_display(self, obj):
        """显示选项的友好格式"""
        if not obj.options:
            return '-'

        if obj.question_type in ['single_choice', 'multiple_choice']:
            options_html = '<ul>'
            for key, value in obj.options.items():
                options_html += f'<li><strong>{key}:</strong> {value}</li>'
            options_html += '</ul>'
            return mark_safe(options_html)
        
        return str(obj.options)
    options_display.short_description = '选项'
    
    def hints_display(self, obj):
        """显示提示的友好格式"""
        if not obj.hints:
            return '-'
        
        hints_html = '<ol>'
        for hint in obj.hints:
            hints_html += f'<li>{hint}</li>'
        hints_html += '</ol>'
        return mark_safe(hints_html)
    hints_display.short_description = '提示'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # 为选项字段添加帮助文本
        if 'options' in form.base_fields:
            form.base_fields['options'].help_text = '''
            选择题选项格式示例：{"A": "选项A内容", "B": "选项B内容", "C": "选项C内容", "D": "选项D内容"}
            '''
        
        # 为提示字段添加帮助文本
        if 'hints' in form.base_fields:
            form.base_fields['hints'].help_text = '''
            提示格式示例：["第一个提示", "第二个提示", "第三个提示"]
            '''
        
        return form


@admin.register(ExerciseSet)
class ExerciseSetAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'exercise_count_display', 'time_limit', 
        'is_public', 'is_active', 'created_at'
    )
    list_filter = ('category', 'is_public', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ExerciseSetItemInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('设置', {
            'fields': (
                'time_limit', 'shuffle_questions', 'shuffle_options', 
                'show_result_immediately', 'is_public', 'is_active'
            )
        }),
    )
    
    def exercise_count_display(self, obj):
        count = obj.exercises.count()
        return format_html('<strong>{}</strong>', count)
    exercise_count_display.short_description = '题目数量'


@admin.register(UserExerciseAttempt)
class UserExerciseAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'exercise', 'is_correct_display', 'score', 
        'time_spent_display', 'submit_time'
    )
    list_filter = ('is_correct', 'exercise__category', 'exercise__difficulty', 'submit_time')
    search_fields = ('user__username', 'user__email', 'exercise__title')
    readonly_fields = ('time_spent_display',)
    date_hierarchy = 'submit_time'
    
    def is_correct_display(self, obj):
        if obj.is_correct:
            return format_html('<span style="color: #28a745;">✓ 正确</span>')
        else:
            return format_html('<span style="color: #dc3545;">✗ 错误</span>')
    is_correct_display.short_description = '结果'
    
    def time_spent_display(self, obj):
        minutes = obj.time_spent // 60
        seconds = obj.time_spent % 60
        return f"{minutes}分{seconds}秒"
    time_spent_display.short_description = '用时'


@admin.register(UserExerciseSetAttempt)
class UserExerciseSetAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'exercise_set', 'score_display', 'success_rate_display', 
        'time_spent_display', 'is_completed', 'start_time'
    )
    list_filter = ('is_completed', 'exercise_set__category', 'start_time')
    search_fields = ('user__username', 'user__email', 'exercise_set__name')
    readonly_fields = ('score_percentage_display', 'time_spent_display')
    date_hierarchy = 'start_time'
    
    def score_display(self, obj):
        return f"{obj.total_score}/{obj.max_score}"
    score_display.short_description = '得分'
    
    def success_rate_display(self, obj):
        rate = obj.success_rate
        color = '#28a745' if rate >= 70 else '#ffc107' if rate >= 40 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, rate
        )
    success_rate_display.short_description = '正确率'
    
    def time_spent_display(self, obj):
        hours = obj.time_spent // 3600
        minutes = (obj.time_spent % 3600) // 60
        seconds = obj.time_spent % 60
        
        if hours > 0:
            return f"{hours}时{minutes}分{seconds}秒"
        else:
            return f"{minutes}分{seconds}秒"
    time_spent_display.short_description = '用时'
    
    def score_percentage_display(self, obj):
        percentage = obj.score_percentage
        color = '#28a745' if percentage >= 70 else '#ffc107' if percentage >= 40 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, percentage
        )
    score_percentage_display.short_description = '得分率'


# 自定义管理页面标题
admin.site.site_header = '计算机科学学习平台 - 练习题库管理'
admin.site.site_title = 'CS练习题库'
admin.site.index_title = '练习题库管理后台'
