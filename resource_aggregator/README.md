# 学习资源聚合器 (Resource Aggregator)

一个独立的Django应用，用于聚合和管理来自各个平台的学习资源。

## 🌟 特性

- **多平台支持**: YouTube、GitHub、Bilibili等主流平台
- **智能搜索**: 基于关键词和分类的智能资源发现
- **松耦合设计**: 可以轻松迁移到其他项目或独立部署
- **缓存优化**: 内置缓存机制，提升搜索性能
- **用户交互**: 支持收藏、点赞、查看历史等功能
- **管理后台**: 完整的Django Admin集成
- **API接口**: RESTful API支持

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install aiohttp requests
```

### 2. 添加到Django项目

在 `settings.py` 中添加应用：

```python
INSTALLED_APPS = [
    # ... 其他应用
    'resource_aggregator',
]
```

在 `urls.py` 中添加路由：

```python
urlpatterns = [
    # ... 其他路由
    path('resources/', include('resource_aggregator.urls')),
]
```

### 3. 运行迁移

```bash
python manage.py makemigrations resource_aggregator
python manage.py migrate
```

### 4. 初始化数据

```bash
python manage.py init_resource_data
```

### 5. 配置API密钥（可选）

在环境变量中设置：

```bash
export YOUTUBE_API_KEY="your_youtube_api_key"
export GITHUB_API_KEY="your_github_token"
```

## 📖 使用方法

### 管理命令

#### 初始化基础数据
```bash
python manage.py init_resource_data
```

#### 同步资源
```bash
# 基本用法
python manage.py sync_resources --query "python tutorial" --save-to-db

# 指定分类和平台
python manage.py sync_resources \
    --query "machine learning" \
    --category "data-science" \
    --platforms youtube github \
    --limit 50 \
    --save-to-db

# 试运行（不保存到数据库）
python manage.py sync_resources --query "react tutorial" --dry-run
```

### API接口

#### 搜索资源
```http
POST /resources/search/
Content-Type: application/json

{
    "query": "python tutorial",
    "category": "programming-languages",
    "platforms": ["youtube", "github"],
    "limit": 20
}
```

#### 获取分类列表
```http
GET /resources/api/categories/
```

#### 获取统计信息
```http
GET /resources/api/stats/
```

### 页面访问

- 资源列表: `/resources/`
- 智能搜索: `/resources/search/`
- 用户仪表板: `/resources/dashboard/` (需要登录)

## 🔧 配置

### 平台配置

在 `resource_aggregator/config.py` 中可以配置各个平台的参数：

```python
RESOURCE_AGGREGATOR_CONFIG = {
    'PLATFORMS': {
        'youtube': {
            'enabled': True,
            'api_key': os.getenv('YOUTUBE_API_KEY', ''),
            'rate_limit': 100,
        },
        'github': {
            'enabled': True,
            'api_key': os.getenv('GITHUB_API_KEY', ''),
            'rate_limit': 60,
        }
    }
}
```

### 缓存配置

```python
RESOURCE_AGGREGATOR_CONFIG = {
    'CACHE_TIMEOUT': 3600,  # 1小时
    'MAX_RESULTS_PER_SOURCE': 20,
    'ENABLE_ASYNC_FETCH': True,
}
```

## 🏗️ 架构设计

### 核心组件

1. **Models**: 数据模型定义
   - `ResourceCategory`: 资源分类
   - `ResourceSource`: 资源来源平台
   - `LearningResource`: 学习资源
   - `UserResourceInteraction`: 用户交互记录

2. **Services**: 业务逻辑层
   - `ResourceAggregatorService`: 核心聚合服务
   - `ResourceFetcher`: 资源获取器基类
   - 各平台具体实现 (`YouTubeFetcher`, `GitHubFetcher` 等)

3. **Views**: 视图层
   - 页面视图和API接口
   - 用户交互处理

4. **Admin**: 管理后台
   - 完整的资源管理界面

### 扩展新平台

1. 继承 `ResourceFetcher` 基类
2. 实现 `fetch_resources` 和 `parse_resource` 方法
3. 在 `ResourceAggregatorService` 中注册

```python
class CustomFetcher(ResourceFetcher):
    async def fetch_resources(self, query, category=None, limit=10):
        # 实现资源获取逻辑
        pass
    
    def parse_resource(self, raw_data):
        # 实现数据解析逻辑
        pass
```

## 🚀 独立部署

### 1. 复制模块

将整个 `resource_aggregator` 目录复制到新项目中。

### 2. 安装依赖

```bash
pip install django aiohttp requests
```

### 3. 创建Django项目

```bash
django-admin startproject resource_project
cd resource_project
# 复制 resource_aggregator 目录到这里
```

### 4. 配置设置

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'resource_aggregator',
]

# urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('resource_aggregator.urls')),
]
```

### 5. 运行项目

```bash
python manage.py migrate
python manage.py init_resource_data
python manage.py runserver
```

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题，请创建Issue或联系开发团队。
