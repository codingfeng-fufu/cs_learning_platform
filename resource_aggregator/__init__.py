# 学习资源聚合器模块
# 独立设计，可以轻松迁移到其他项目或独立部署

__version__ = '1.0.0'
__author__ = 'CS Learning Platform'
__description__ = '学习资源聚合器 - 整合各平台优质学习资源'

# 模块配置
DEFAULT_CONFIG = {
    'CACHE_TIMEOUT': 3600,  # 缓存1小时
    'MAX_RESULTS_PER_SOURCE': 10,
    'ENABLE_ASYNC_FETCH': True,
    'DEFAULT_LANGUAGE': 'zh-CN',
    'RATE_LIMIT': {
        'requests_per_minute': 60,
        'requests_per_hour': 1000
    }
}

# 支持的资源类型
RESOURCE_TYPES = {
    'VIDEO': 'video',
    'ARTICLE': 'article', 
    'COURSE': 'course',
    'BOOK': 'book',
    'DOCUMENTATION': 'documentation',
    'GITHUB': 'github',
    'PAPER': 'paper'
}

# 支持的平台
SUPPORTED_PLATFORMS = {
    'YOUTUBE': 'youtube',
    'BILIBILI': 'bilibili',
    'GITHUB': 'github',
    'STACKOVERFLOW': 'stackoverflow',
    'MEDIUM': 'medium',
    'ARXIV': 'arxiv',
    'COURSERA': 'coursera',
    'EDUX': 'edux'
}
