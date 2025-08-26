from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, UserProfile, KnowledgePoint, StudySession,
    UserKnowledgeProgress, Achievement, UserAchievement,
    EmailVerificationToken, PasswordResetToken
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_email_verified', 'level', 'points', 'date_joined')
    list_filter = ('is_email_verified', 'level', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('学习信息', {
            'fields': ('is_email_verified', 'total_study_time', 'points', 'level')
        }),
        ('偏好设置', {
            'fields': ('preferred_language', 'email_notifications')
        }),
        ('个人信息', {
            'fields': ('bio', 'birth_date', 'location', 'website', 'github_username')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'study_goal', 'daily_study_goal', 'current_streak', 'longest_streak', 'total_knowledge_points')
    list_filter = ('study_goal', 'current_streak')
    search_fields = ('user__email', 'user__username')

@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category', 'subcategory', 'difficulty', 'estimated_time', 'is_active')
    list_filter = ('category', 'subcategory', 'difficulty', 'is_active')
    search_fields = ('title', 'slug', 'category')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'knowledge_point', 'start_time', 'duration', 'is_completed', 'progress_percentage')
    list_filter = ('is_completed', 'start_time', 'knowledge_point__category')
    search_fields = ('user__email', 'knowledge_point__title')
    date_hierarchy = 'start_time'

@admin.register(UserKnowledgeProgress)
class UserKnowledgeProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'knowledge_point', 'status', 'progress_percentage', 'total_study_time', 'last_accessed')
    list_filter = ('status', 'knowledge_point__category', 'last_accessed')
    search_fields = ('user__email', 'knowledge_point__title')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'condition_type', 'condition_value', 'points_reward', 'is_active')
    list_filter = ('category', 'condition_type', 'is_active')
    search_fields = ('name', 'description')

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    list_filter = ('achievement__category', 'earned_at')
    search_fields = ('user__email', 'achievement__name')
    date_hierarchy = 'earned_at'

@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('token',)

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('token',)
