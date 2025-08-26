"""
安全防护中间件
提供DDoS防护、SQL注入防护、XSS防护等安全功能
"""

import time
import re
import json
import hashlib
from collections import defaultdict, deque
from django.http import HttpResponse, JsonResponse
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('django.security')


class DDoSProtectionMiddleware(MiddlewareMixin):
    """DDoS攻击防护中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 内存中的请求计数器
        self.request_counts = defaultdict(deque)
        self.blocked_ips = {}
        
        # 配置参数
        self.max_requests_per_minute = getattr(settings, 'DDOS_MAX_REQUESTS_PER_MINUTE', 60)
        self.max_requests_per_hour = getattr(settings, 'DDOS_MAX_REQUESTS_PER_HOUR', 1000)
        self.block_duration = getattr(settings, 'DDOS_BLOCK_DURATION', 3600)  # 1小时
        self.whitelist = getattr(settings, 'DDOS_WHITELIST', ['127.0.0.1'])
        
        super().__init__(get_response)
    
    def __call__(self, request):
        client_ip = self.get_client_ip(request)
        
        # 检查白名单
        if client_ip in self.whitelist:
            return self.get_response(request)
        
        # 检查是否被封禁
        if self.is_blocked(client_ip):
            logger.warning(f'Blocked IP {client_ip} attempted access')
            return self.create_blocked_response()
        
        # 检查请求频率
        if self.should_block(client_ip):
            self.block_ip(client_ip)
            logger.warning(f'IP {client_ip} blocked due to high request rate')
            return self.create_rate_limit_response()
        
        # 记录请求
        self.record_request(client_ip)
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        """获取客户端真实IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_blocked(self, ip):
        """检查IP是否被封禁"""
        if ip in self.blocked_ips:
            block_time = self.blocked_ips[ip]
            if time.time() - block_time < self.block_duration:
                return True
            else:
                # 解除封禁
                del self.blocked_ips[ip]
        return False
    
    def should_block(self, ip):
        """判断是否应该封禁IP"""
        current_time = time.time()
        
        # 清理过期记录
        while self.request_counts[ip] and current_time - self.request_counts[ip][0] > 3600:
            self.request_counts[ip].popleft()
        
        # 检查每分钟请求数
        minute_requests = sum(1 for t in self.request_counts[ip] if current_time - t < 60)
        if minute_requests >= self.max_requests_per_minute:
            return True
        
        # 检查每小时请求数
        hour_requests = len(self.request_counts[ip])
        if hour_requests >= self.max_requests_per_hour:
            return True
        
        return False
    
    def record_request(self, ip):
        """记录请求"""
        current_time = time.time()
        self.request_counts[ip].append(current_time)
        
        # 限制内存使用，只保留最近的记录
        if len(self.request_counts[ip]) > self.max_requests_per_hour:
            self.request_counts[ip].popleft()
    
    def block_ip(self, ip):
        """封禁IP"""
        self.blocked_ips[ip] = time.time()
        
        # 同时写入缓存，支持多实例共享
        cache_key = f'blocked_ip_{ip}'
        cache.set(cache_key, time.time(), self.block_duration)
    
    def create_blocked_response(self):
        """创建封禁响应"""
        return HttpResponse(
            'Access Denied - IP Blocked',
            status=403,
            content_type='text/plain'
        )
    
    def create_rate_limit_response(self):
        """创建限流响应"""
        return JsonResponse({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.',
            'retry_after': 60
        }, status=429)


class SQLInjectionProtectionMiddleware(MiddlewareMixin):
    """SQL注入防护中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # SQL注入检测模式
        self.sql_patterns = [
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
            r'(\b(or|and)\s+\d+\s*=\s*\d+)',
            r'(\b(or|and)\s+[\'"]?\w+[\'"]?\s*=\s*[\'"]?\w+[\'"]?)',
            r'(--|#|/\*|\*/)',
            r'(\bxp_cmdshell\b)',
            r'(\bsp_executesql\b)',
            r'(\binto\s+outfile\b)',
            r'(\bload_file\b)',
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.sql_patterns]
        super().__init__(get_response)
    
    def __call__(self, request):
        # 检查GET参数
        for key, value in request.GET.items():
            if self.contains_sql_injection(value):
                logger.warning(f'SQL injection attempt detected in GET parameter {key}: {value}')
                return self.create_security_response('Invalid input detected')
        
        # 检查POST数据
        if hasattr(request, 'POST'):
            for key, value in request.POST.items():
                if self.contains_sql_injection(value):
                    logger.warning(f'SQL injection attempt detected in POST parameter {key}: {value}')
                    return self.create_security_response('Invalid input detected')
        
        # 检查JSON数据
        if request.content_type == 'application/json':
            try:
                json_data = json.loads(request.body)
                if self.check_json_for_sql_injection(json_data):
                    logger.warning(f'SQL injection attempt detected in JSON data')
                    return self.create_security_response('Invalid input detected')
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        
        return self.get_response(request)
    
    def contains_sql_injection(self, value):
        """检查字符串是否包含SQL注入"""
        if not isinstance(value, str):
            return False
        
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                return True
        return False
    
    def check_json_for_sql_injection(self, data):
        """递归检查JSON数据中的SQL注入"""
        if isinstance(data, dict):
            for key, value in data.items():
                if self.contains_sql_injection(str(key)) or self.check_json_for_sql_injection(value):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self.check_json_for_sql_injection(item):
                    return True
        elif isinstance(data, str):
            return self.contains_sql_injection(data)
        
        return False
    
    def create_security_response(self, message):
        """创建安全响应"""
        return JsonResponse({
            'error': 'Security violation',
            'message': message
        }, status=400)


class XSSProtectionMiddleware(MiddlewareMixin):
    """XSS攻击防护中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # XSS检测模式
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'eval\s*\(',
            r'expression\s*\(',
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in self.xss_patterns]
        super().__init__(get_response)
    
    def __call__(self, request):
        # 检查所有输入参数
        for key, value in request.GET.items():
            if self.contains_xss(value):
                logger.warning(f'XSS attempt detected in GET parameter {key}: {value}')
                return self.create_security_response('Potentially dangerous content detected')
        
        if hasattr(request, 'POST'):
            for key, value in request.POST.items():
                if self.contains_xss(value):
                    logger.warning(f'XSS attempt detected in POST parameter {key}: {value}')
                    return self.create_security_response('Potentially dangerous content detected')
        
        return self.get_response(request)
    
    def contains_xss(self, value):
        """检查字符串是否包含XSS"""
        if not isinstance(value, str):
            return False
        
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                return True
        return False
    
    def create_security_response(self, message):
        """创建安全响应"""
        return JsonResponse({
            'error': 'Security violation',
            'message': message
        }, status=400)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """安全头部中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # 添加安全头部
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # 内容安全策略
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net cdnjs.cloudflare.com",
            "style-src 'self' 'unsafe-inline' fonts.googleapis.com cdn.jsdelivr.net cdnjs.cloudflare.com",
            "font-src 'self' fonts.gstatic.com cdnjs.cloudflare.com",
            "img-src 'self' data: blob:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        
        response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        # HTTPS相关头部（仅在HTTPS环境下）
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """请求日志中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        start_time = time.time()
        
        # 记录请求信息
        client_ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        response = self.get_response(request)
        
        # 记录响应信息
        response_time = time.time() - start_time
        
        # 记录可疑请求
        if self.is_suspicious_request(request, response):
            logger.warning(
                f'Suspicious request: {client_ip} {request.method} {request.path} '
                f'Status: {response.status_code} Time: {response_time:.3f}s '
                f'User-Agent: {user_agent}'
            )
        
        return response
    
    def get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_suspicious_request(self, request, response):
        """判断是否为可疑请求"""
        # 4xx和5xx状态码
        if response.status_code >= 400:
            return True
        
        # 包含可疑路径
        suspicious_paths = [
            '/admin/', '/wp-admin/', '/phpmyadmin/', '/.env',
            '/config/', '/backup/', '/test/', '/debug/'
        ]
        
        for path in suspicious_paths:
            if path in request.path.lower():
                return True
        
        # 可疑User-Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        suspicious_agents = ['bot', 'crawler', 'scanner', 'exploit']
        
        for agent in suspicious_agents:
            if agent in user_agent:
                return True
        
        return False
