"""
学习资源聚合器 - URL配置
独立的URL路由，方便迁移
"""

from django.urls import path
from . import views

app_name = 'resource_aggregator'

urlpatterns = [
    # 主要页面
    path('', views.resource_list, name='list'),
    path('search/', views.ResourceSearchView.as_view(), name='search'),
    path('resource/<int:resource_id>/', views.resource_detail, name='detail'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    
    # API接口
    path('api/categories/', views.api_categories, name='api_categories'),
    path('api/sources/', views.api_sources, name='api_sources'),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/interaction/', views.resource_interaction, name='api_interaction'),
    
    # 管理功能
    path('admin/sync/', views.admin_sync_resources, name='admin_sync'),
]
