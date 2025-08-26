"""
性能优化中间件
"""

import gzip
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

class PerformanceMiddleware(MiddlewareMixin):
    """性能优化中间件"""
    
    def process_request(self, request):
        """请求开始时记录时间"""
        request._start_time = time.time()
    
    def process_response(self, request, response):
        """响应时进行优化"""
        # 添加性能头
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            response['X-Response-Time'] = f'{duration:.3f}s'
        
        # Gzip压缩
        if (response.get('Content-Type', '').startswith(('text/', 'application/json', 'application/javascript')) and
            'gzip' in request.META.get('HTTP_ACCEPT_ENCODING', '') and
            len(response.content) > 1024):  # 只压缩大于1KB的内容
            
            compressed_content = gzip.compress(response.content)
            if len(compressed_content) < len(response.content):
                response.content = compressed_content
                response['Content-Encoding'] = 'gzip'
                response['Content-Length'] = str(len(compressed_content))
        
        # 添加缓存头
        if request.path.startswith('/static/'):
            response['Cache-Control'] = 'public, max-age=31536000'  # 1年
        elif request.path in ['/', '/daily-term/', '/about/']:
            response['Cache-Control'] = 'public, max-age=300'  # 5分钟
        
        return response

class CacheControlMiddleware(MiddlewareMixin):
    """缓存控制中间件"""
    
    def process_response(self, request, response):
        """设置缓存控制头"""
        if request.path.startswith('/static/'):
            # 静态文件长期缓存
            response['Cache-Control'] = 'public, max-age=31536000, immutable'
            response['Expires'] = 'Thu, 31 Dec 2025 23:59:59 GMT'
        elif request.path.startswith('/media/'):
            # 媒体文件中期缓存
            response['Cache-Control'] = 'public, max-age=86400'  # 1天
        elif request.method == 'GET' and response.status_code == 200:
            # 页面短期缓存
            if 'no-cache' not in response.get('Cache-Control', ''):
                response['Cache-Control'] = 'public, max-age=300'  # 5分钟
        
        return response
