"""
学习资源聚合器 - Django应用配置
"""

from django.apps import AppConfig


class ResourceAggregatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'resource_aggregator'
    verbose_name = '学习资源聚合器'
    
    def ready(self):
        """应用启动时的初始化"""
        # 导入信号处理器
        try:
            from . import signals
        except ImportError:
            pass
