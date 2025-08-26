from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 认证相关
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # 邮箱验证
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    
    # 密码重置
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/<uuid:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # 用户资料
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('preferences/', views.preferences, name='preferences'),
    path('change-password/', views.change_password, name='change_password'),
    path('learning-dashboard/', views.learning_dashboard, name='learning_dashboard'),
    path('learning-plan/', views.learning_plan, name='learning_plan'),

    # 学习进度API
    path('api/start-learning/', views.start_learning, name='start_learning'),
    path('api/end-learning/', views.end_learning, name='end_learning'),
    path('api/learning-stats/', views.learning_stats, name='learning_stats'),
    path('api/learning-calendar/', views.learning_calendar_api, name='learning_calendar_api'),
    path('api/weekly-chart/', views.weekly_chart_api, name='weekly_chart_api'),
]
