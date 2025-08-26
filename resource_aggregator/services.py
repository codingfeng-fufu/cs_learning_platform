"""
学习资源聚合器 - 核心服务
独立的业务逻辑，支持多种数据源
"""

import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
import logging
import hashlib
import json

from .models import LearningResource, ResourceSource, ResourceCategory, ResourceCache

logger = logging.getLogger(__name__)


class ResourceFetcher(ABC):
    """资源获取器基类"""
    
    def __init__(self, source: ResourceSource):
        self.source = source
        self.session = None
    
    @abstractmethod
    async def fetch_resources(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """获取资源"""
        pass
    
    @abstractmethod
    def parse_resource(self, raw_data: Dict) -> Dict:
        """解析资源数据"""
        pass
    
    def generate_cache_key(self, query: str, category: str = None) -> str:
        """生成缓存键"""
        key_data = f"{self.source.platform}:{query}:{category or 'all'}"
        return hashlib.md5(key_data.encode()).hexdigest()


class YouTubeFetcher(ResourceFetcher):
    """YouTube资源获取器"""
    
    async def fetch_resources(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """从YouTube获取资源"""
        if not self.source.api_key:
            logger.warning("YouTube API key not configured")
            return []
        
        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': f"{query} programming tutorial",
                'type': 'video',
                'maxResults': limit,
                'key': self.source.api_key,
                'order': 'relevance'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [self.parse_resource(item) for item in data.get('items', [])]
                    else:
                        logger.error(f"YouTube API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching YouTube resources: {e}")
            return []
    
    def parse_resource(self, raw_data: Dict) -> Dict:
        """解析YouTube资源数据"""
        snippet = raw_data.get('snippet', {})
        video_id = raw_data.get('id', {}).get('videoId', '')
        
        return {
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'url': f"https://www.youtube.com/watch?v={video_id}",
            'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
            'author': snippet.get('channelTitle', ''),
            'external_id': video_id,
            'resource_type': 'video',
            'language': 'en',
            'tags': snippet.get('tags', [])
        }


class GitHubFetcher(ResourceFetcher):
    """GitHub资源获取器"""
    
    async def fetch_resources(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """从GitHub获取资源"""
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                'q': f"{query} language:python OR language:javascript OR language:java",
                'sort': 'stars',
                'order': 'desc',
                'per_page': limit
            }
            
            headers = {}
            if self.source.api_key:
                headers['Authorization'] = f"token {self.source.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [self.parse_resource(item) for item in data.get('items', [])]
                    else:
                        logger.error(f"GitHub API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching GitHub resources: {e}")
            return []
    
    def parse_resource(self, raw_data: Dict) -> Dict:
        """解析GitHub资源数据"""
        return {
            'title': raw_data.get('name', ''),
            'description': raw_data.get('description', ''),
            'url': raw_data.get('html_url', ''),
            'thumbnail': raw_data.get('owner', {}).get('avatar_url', ''),
            'author': raw_data.get('owner', {}).get('login', ''),
            'external_id': str(raw_data.get('id', '')),
            'resource_type': 'github',
            'language': raw_data.get('language', '').lower(),
            'rating': min(raw_data.get('stargazers_count', 0) / 1000, 5.0),  # 转换为5分制
            'view_count': raw_data.get('watchers_count', 0),
            'like_count': raw_data.get('stargazers_count', 0),
            'tags': raw_data.get('topics', [])
        }


class BilibiliFetcher(ResourceFetcher):
    """Bilibili资源获取器"""
    
    async def fetch_resources(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """从Bilibili获取资源"""
        try:
            # 注意：这里使用的是公开API，实际使用时可能需要申请官方API
            url = "https://api.bilibili.com/x/web-interface/search/all/v2"
            params = {
                'keyword': f"{query} 编程 教程",
                'page': 1,
                'pagesize': limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        videos = data.get('data', {}).get('result', {}).get('video', [])
                        return [self.parse_resource(item) for item in videos]
                    else:
                        logger.error(f"Bilibili API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching Bilibili resources: {e}")
            return []
    
    def parse_resource(self, raw_data: Dict) -> Dict:
        """解析Bilibili资源数据"""
        return {
            'title': raw_data.get('title', '').replace('<em class="keyword">', '').replace('</em>', ''),
            'description': raw_data.get('description', ''),
            'url': raw_data.get('arcurl', ''),
            'thumbnail': f"https:{raw_data.get('pic', '')}",
            'author': raw_data.get('author', ''),
            'external_id': str(raw_data.get('aid', '')),
            'resource_type': 'video',
            'language': 'zh-CN',
            'duration': raw_data.get('duration', ''),
            'view_count': raw_data.get('play', 0),
            'tags': raw_data.get('tag', '').split(',') if raw_data.get('tag') else []
        }


class ResourceAggregatorService:
    """资源聚合服务"""

    def __init__(self):
        self.fetchers = {}
        self._initialized = False

    def _initialize_fetchers(self) -> Dict[str, ResourceFetcher]:
        """初始化资源获取器"""
        if self._initialized:
            return self.fetchers

        try:
            from .models import ResourceSource
            fetchers = {}

            for source in ResourceSource.objects.filter(is_active=True):
                if source.platform == 'youtube':
                    fetchers[source.platform] = YouTubeFetcher(source)
                elif source.platform == 'github':
                    fetchers[source.platform] = GitHubFetcher(source)
                elif source.platform == 'bilibili':
                    fetchers[source.platform] = BilibiliFetcher(source)

            self.fetchers = fetchers
            self._initialized = True
            return fetchers
        except Exception:
            # 在迁移过程中可能会出错，返回空字典
            return {}
    
    async def search_resources(self, query: str, category: str = None,
                             platforms: List[str] = None, limit: int = 30) -> List[Dict]:
        """搜索学习资源"""
        # 确保fetchers已初始化
        if not self._initialized:
            self._initialize_fetchers()

        if platforms is None:
            platforms = list(self.fetchers.keys())

        # 检查缓存
        cache_key = self._generate_search_cache_key(query, category, platforms)
        try:
            from .models import ResourceCache
            cached_data = ResourceCache.get_cached_data(cache_key)
            if cached_data:
                return cached_data
        except Exception:
            # 如果缓存不可用，继续执行
            pass

        # 并发获取资源
        tasks = []
        for platform in platforms:
            if platform in self.fetchers:
                fetcher = self.fetchers[platform]
                task = fetcher.fetch_resources(query, category, limit // len(platforms))
                tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            all_resources = []
            
            for result in results:
                if isinstance(result, list):
                    all_resources.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Fetcher error: {result}")
            
            # 排序和去重
            unique_resources = self._deduplicate_resources(all_resources)
            sorted_resources = self._sort_resources(unique_resources)
            
            # 缓存结果
            try:
                from .models import ResourceCache
                ResourceCache.set_cached_data(cache_key, sorted_resources[:limit])
            except Exception:
                # 如果缓存不可用，忽略
                pass
            
            return sorted_resources[:limit]
            
        except Exception as e:
            logger.error(f"Error in search_resources: {e}")
            return []
    
    def _generate_search_cache_key(self, query: str, category: str, platforms: List[str]) -> str:
        """生成搜索缓存键"""
        key_data = f"search:{query}:{category or 'all'}:{':'.join(sorted(platforms))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _deduplicate_resources(self, resources: List[Dict]) -> List[Dict]:
        """去重资源"""
        seen_urls = set()
        unique_resources = []
        
        for resource in resources:
            url = resource.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_resources.append(resource)
        
        return unique_resources
    
    def _sort_resources(self, resources: List[Dict]) -> List[Dict]:
        """排序资源"""
        def sort_key(resource):
            # 综合评分：评分 + 观看数权重 + 点赞数权重
            rating = resource.get('rating', 0)
            view_count = resource.get('view_count', 0)
            like_count = resource.get('like_count', 0)
            
            # 标准化分数
            view_score = min(view_count / 10000, 5.0)  # 观看数转换为5分制
            like_score = min(like_count / 1000, 5.0)   # 点赞数转换为5分制
            
            return rating * 0.5 + view_score * 0.3 + like_score * 0.2
        
        return sorted(resources, key=sort_key, reverse=True)
    
    def save_resources_to_db(self, resources: List[Dict], category_slug: str = None):
        """保存资源到数据库"""
        try:
            category = None
            if category_slug:
                category = ResourceCategory.objects.get(slug=category_slug)
            
            for resource_data in resources:
                # 检查是否已存在
                existing = LearningResource.objects.filter(
                    url=resource_data['url']
                ).first()
                
                if not existing:
                    # 获取或创建资源来源
                    source, _ = ResourceSource.objects.get_or_create(
                        platform=resource_data.get('resource_type', 'custom'),
                        defaults={'name': resource_data.get('resource_type', 'Custom').title()}
                    )
                    
                    # 创建资源
                    LearningResource.objects.create(
                        title=resource_data.get('title', ''),
                        description=resource_data.get('description', ''),
                        url=resource_data.get('url', ''),
                        thumbnail=resource_data.get('thumbnail', ''),
                        category=category,
                        resource_type=resource_data.get('resource_type', 'article'),
                        source=source,
                        author=resource_data.get('author', ''),
                        duration=resource_data.get('duration', ''),
                        language=resource_data.get('language', 'zh-CN'),
                        rating=resource_data.get('rating', 0.0),
                        view_count=resource_data.get('view_count', 0),
                        like_count=resource_data.get('like_count', 0),
                        tags=resource_data.get('tags', []),
                        external_id=resource_data.get('external_id', '')
                    )
        except Exception as e:
            logger.error(f"Error saving resources to DB: {e}")


# 同步包装器，用于在Django视图中调用异步方法
def sync_search_resources(query: str, category: str = None,
                         platforms: List[str] = None, limit: int = 30) -> List[Dict]:
    """同步搜索资源的包装器"""
    service = ResourceAggregatorService()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            service.search_resources(query, category, platforms, limit)
        )
    finally:
        loop.close()


# 全局服务实例
aggregator_service = ResourceAggregatorService()
