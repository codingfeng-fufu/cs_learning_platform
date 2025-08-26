#!/usr/bin/env python
"""
静态资源优化脚本
压缩CSS、JS文件，优化图片，提升加载速度
"""

import os
import re
import gzip
import shutil
from pathlib import Path

def minify_css(css_content):
    """简单的CSS压缩"""
    # 移除注释
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    # 移除多余的空白
    css_content = re.sub(r'\s+', ' ', css_content)
    # 移除不必要的分号和空格
    css_content = re.sub(r';\s*}', '}', css_content)
    css_content = re.sub(r'{\s*', '{', css_content)
    css_content = re.sub(r'}\s*', '}', css_content)
    css_content = re.sub(r':\s*', ':', css_content)
    css_content = re.sub(r';\s*', ';', css_content)
    return css_content.strip()

def minify_js(js_content):
    """简单的JS压缩"""
    # 移除单行注释
    js_content = re.sub(r'//.*$', '', js_content, flags=re.MULTILINE)
    # 移除多行注释
    js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
    # 移除多余的空白（保留字符串内的空白）
    js_content = re.sub(r'\s+', ' ', js_content)
    return js_content.strip()

def create_gzip_version(file_path):
    """创建gzip压缩版本"""
    with open(file_path, 'rb') as f_in:
        with gzip.open(f'{file_path}.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    original_size = os.path.getsize(file_path)
    compressed_size = os.path.getsize(f'{file_path}.gz')
    compression_ratio = (1 - compressed_size / original_size) * 100
    
    return original_size, compressed_size, compression_ratio

def optimize_templates():
    """优化模板文件中的内联CSS和JS"""
    template_dirs = ['templates']
    
    for template_dir in template_dirs:
        if not os.path.exists(template_dir):
            continue
            
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    optimize_template_file(file_path)

def optimize_template_file(file_path):
    """优化单个模板文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        
        # 压缩内联CSS
        def compress_css_block(match):
            css_content = match.group(1)
            compressed = minify_css(css_content)
            return f'<style>{compressed}</style>'
        
        content = re.sub(r'<style[^>]*>(.*?)</style>', compress_css_block, content, flags=re.DOTALL)
        
        # 压缩内联JS
        def compress_js_block(match):
            js_content = match.group(1)
            compressed = minify_js(js_content)
            return f'<script>{compressed}</script>'
        
        content = re.sub(r'<script[^>]*>(.*?)</script>', compress_js_block, content, flags=re.DOTALL)
        
        # 移除HTML中的多余空白（保留pre标签内容）
        content = re.sub(r'>\s+<', '><', content)
        
        new_size = len(content)
        
        if new_size < original_size:
            # 备份原文件
            backup_path = f'{file_path}.backup'
            if not os.path.exists(backup_path):
                shutil.copy2(file_path, backup_path)
            
            # 写入优化后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            compression_ratio = (1 - new_size / original_size) * 100
            print(f'✅ 优化 {file_path}: {original_size} -> {new_size} bytes ({compression_ratio:.1f}% 压缩)')
        
    except Exception as e:
        print(f'❌ 优化 {file_path} 失败: {e}')

def create_performance_middleware():
    """创建性能优化中间件"""
    middleware_content = '''"""
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
'''
    
    os.makedirs('knowledge_app/middleware', exist_ok=True)
    
    # 创建__init__.py
    with open('knowledge_app/middleware/__init__.py', 'w') as f:
        f.write('')
    
    # 创建中间件文件
    with open('knowledge_app/middleware/performance.py', 'w', encoding='utf-8') as f:
        f.write(middleware_content)
    
    print('✅ 创建性能优化中间件')

def create_lazy_loading_js():
    """创建懒加载JavaScript"""
    lazy_loading_js = '''
// 图片懒加载
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
});

// 预加载关键资源
function preloadResource(href, as = 'script') {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = href;
    link.as = as;
    document.head.appendChild(link);
}

// 延迟加载非关键CSS
function loadCSS(href) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = href;
    link.media = 'print';
    link.onload = function() { this.media = 'all'; };
    document.head.appendChild(link);
}
'''
    
    os.makedirs('static/js', exist_ok=True)
    with open('static/js/performance.js', 'w', encoding='utf-8') as f:
        f.write(lazy_loading_js)
    
    print('✅ 创建懒加载JavaScript')

def main():
    """主函数"""
    print('🚀 开始静态资源优化...')
    print('=' * 50)
    
    # 1. 优化模板文件
    print('\n📝 优化模板文件...')
    optimize_templates()
    
    # 2. 创建性能中间件
    print('\n⚙️ 创建性能中间件...')
    create_performance_middleware()
    
    # 3. 创建懒加载脚本
    print('\n📱 创建懒加载脚本...')
    create_lazy_loading_js()
    
    print('\n' + '=' * 50)
    print('✅ 静态资源优化完成！')
    
    print('\n📋 后续步骤:')
    print('1. 在settings.py中添加中间件:')
    print("   'knowledge_app.middleware.performance.PerformanceMiddleware',")
    print("   'knowledge_app.middleware.performance.CacheControlMiddleware',")
    print('\n2. 在模板中添加懒加载脚本:')
    print("   <script src='{% static \"js/performance.js\" %}'></script>")
    print('\n3. 重启Django服务器以应用更改')

if __name__ == '__main__':
    main()
