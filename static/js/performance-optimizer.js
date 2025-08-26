/**
 * 全局性能优化器
 * 提升页面加载速度和用户体验
 */

class PerformanceOptimizer {
    constructor() {
        this.isInitialized = false;
        this.loadingElements = new Set();
        this.deferredTasks = [];
        this.performanceMetrics = {};
        
        this.init();
    }

    init() {
        if (this.isInitialized) return;
        
        console.log('🚀 性能优化器初始化中...');
        
        // 记录页面加载开始时间
        this.performanceMetrics.startTime = performance.now();
        
        // 初始化各种优化功能
        this.initLazyLoading();
        this.initResourcePreloading();
        this.initCriticalResourceOptimization();
        this.initAnimationOptimization();
        this.initMemoryOptimization();
        
        // 页面加载完成后的优化
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.onDOMContentLoaded());
        } else {
            this.onDOMContentLoaded();
        }
        
        window.addEventListener('load', () => this.onWindowLoad());
        
        this.isInitialized = true;
        console.log('✅ 性能优化器初始化完成');
    }

    // 懒加载优化
    initLazyLoading() {
        if (!('IntersectionObserver' in window)) {
            console.warn('⚠️ 浏览器不支持IntersectionObserver，跳过懒加载优化');
            return;
        }

        // 图片懒加载
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        this.loadImage(img);
                        imageObserver.unobserve(img);
                    }
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.01
        });

        // 观察所有懒加载图片
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });

        // 内容懒加载
        const contentObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    if (element.dataset.lazyContent) {
                        this.loadLazyContent(element);
                        contentObserver.unobserve(element);
                    }
                }
            });
        }, {
            rootMargin: '100px 0px',
            threshold: 0.01
        });

        document.querySelectorAll('[data-lazy-content]').forEach(el => {
            contentObserver.observe(el);
        });
    }

    // 资源预加载
    initResourcePreloading() {
        // 预加载关键CSS
        this.preloadResource('/static/css/critical.css', 'style');
        
        // 预加载重要字体
        this.preloadResource('/static/fonts/main.woff2', 'font', 'font/woff2');
        
        // 预连接到外部域名
        this.preconnectDomain('https://fonts.googleapis.com');
        this.preconnectDomain('https://cdn.jsdelivr.net');
    }

    // 关键资源优化
    initCriticalResourceOptimization() {
        // 延迟加载非关键CSS
        this.deferNonCriticalCSS();
        
        // 延迟加载非关键JavaScript
        this.deferNonCriticalJS();
        
        // 优化字体加载
        this.optimizeFontLoading();
    }

    // 动画性能优化
    initAnimationOptimization() {
        // 检测设备性能
        const isLowEndDevice = this.detectLowEndDevice();
        
        if (isLowEndDevice) {
            // 在低端设备上减少动画
            document.documentElement.classList.add('reduce-motion');
            console.log('📱 检测到低端设备，已启用动画优化');
        }

        // 使用requestAnimationFrame优化动画
        this.optimizeAnimations();
    }

    // 内存优化
    initMemoryOptimization() {
        // 清理未使用的事件监听器
        this.cleanupEventListeners();
        
        // 优化DOM操作
        this.optimizeDOMOperations();
        
        // 内存泄漏检测
        this.detectMemoryLeaks();
    }

    // 加载图片
    loadImage(img) {
        return new Promise((resolve, reject) => {
            const newImg = new Image();
            newImg.onload = () => {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                img.classList.add('loaded');
                resolve();
            };
            newImg.onerror = reject;
            newImg.src = img.dataset.src;
        });
    }

    // 加载懒加载内容
    loadLazyContent(element) {
        const contentUrl = element.dataset.lazyContent;
        
        fetch(contentUrl)
            .then(response => response.text())
            .then(html => {
                element.innerHTML = html;
                element.removeAttribute('data-lazy-content');
                element.classList.add('content-loaded');
            })
            .catch(error => {
                console.error('懒加载内容失败:', error);
                element.innerHTML = '<p>内容加载失败，请刷新页面重试</p>';
            });
    }

    // 预加载资源
    preloadResource(href, as, type = null) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = href;
        link.as = as;
        if (type) link.type = type;
        link.crossOrigin = 'anonymous';
        document.head.appendChild(link);
    }

    // 预连接域名
    preconnectDomain(href) {
        const link = document.createElement('link');
        link.rel = 'preconnect';
        link.href = href;
        link.crossOrigin = 'anonymous';
        document.head.appendChild(link);
    }

    // 延迟加载非关键CSS
    deferNonCriticalCSS() {
        const nonCriticalCSS = [
            '/static/css/animations.css',
            '/static/css/print.css'
        ];

        nonCriticalCSS.forEach(href => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.media = 'print';
            link.onload = function() {
                this.media = 'all';
            };
            document.head.appendChild(link);
        });
    }

    // 延迟加载非关键JavaScript
    deferNonCriticalJS() {
        const nonCriticalJS = [
            '/static/js/analytics.js',
            '/static/js/social-share.js'
        ];

        // 页面加载完成后再加载这些脚本
        window.addEventListener('load', () => {
            nonCriticalJS.forEach(src => {
                const script = document.createElement('script');
                script.src = src;
                script.async = true;
                document.head.appendChild(script);
            });
        });
    }

    // 优化字体加载
    optimizeFontLoading() {
        // 使用font-display: swap优化字体加载
        const style = document.createElement('style');
        style.textContent = `
            @font-face {
                font-family: 'MainFont';
                src: url('/static/fonts/main.woff2') format('woff2');
                font-display: swap;
            }
        `;
        document.head.appendChild(style);
    }

    // 检测低端设备
    detectLowEndDevice() {
        // 基于多个指标判断设备性能
        const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        const memory = navigator.deviceMemory;
        const cores = navigator.hardwareConcurrency;

        let score = 0;

        // 网络连接评分
        if (connection) {
            if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
                score += 3;
            } else if (connection.effectiveType === '3g') {
                score += 2;
            }
        }

        // 内存评分
        if (memory && memory <= 2) {
            score += 2;
        }

        // CPU核心数评分
        if (cores && cores <= 2) {
            score += 1;
        }

        // 屏幕尺寸评分
        if (window.innerWidth <= 768) {
            score += 1;
        }

        return score >= 3;
    }

    // 优化动画
    optimizeAnimations() {
        let animationFrame;
        const animationQueue = [];

        const processAnimations = () => {
            if (animationQueue.length > 0) {
                const animation = animationQueue.shift();
                animation();
            }
            
            if (animationQueue.length > 0) {
                animationFrame = requestAnimationFrame(processAnimations);
            }
        };

        // 全局动画队列
        window.queueAnimation = (callback) => {
            animationQueue.push(callback);
            if (!animationFrame) {
                animationFrame = requestAnimationFrame(processAnimations);
            }
        };
    }

    // 清理事件监听器
    cleanupEventListeners() {
        // 页面卸载时清理
        window.addEventListener('beforeunload', () => {
            // 清理所有自定义事件监听器
            this.loadingElements.clear();
            this.deferredTasks = [];
        });
    }

    // 优化DOM操作
    optimizeDOMOperations() {
        // 批量DOM操作
        window.batchDOMUpdates = (updates) => {
            const fragment = document.createDocumentFragment();
            updates.forEach(update => update(fragment));
            document.body.appendChild(fragment);
        };
    }

    // 内存泄漏检测
    detectMemoryLeaks() {
        if (typeof performance !== 'undefined' && performance.memory) {
            setInterval(() => {
                const memory = performance.memory;
                if (memory.usedJSHeapSize > memory.totalJSHeapSize * 0.9) {
                    console.warn('⚠️ 检测到可能的内存泄漏');
                }
            }, 30000); // 每30秒检查一次
        }
    }

    // DOM内容加载完成
    onDOMContentLoaded() {
        this.performanceMetrics.domContentLoaded = performance.now();
        
        // 执行延迟任务
        this.deferredTasks.forEach(task => {
            try {
                task();
            } catch (error) {
                console.error('延迟任务执行失败:', error);
            }
        });
        
        console.log(`📊 DOM加载耗时: ${(this.performanceMetrics.domContentLoaded - this.performanceMetrics.startTime).toFixed(2)}ms`);
    }

    // 窗口加载完成
    onWindowLoad() {
        this.performanceMetrics.windowLoaded = performance.now();
        
        // 记录性能指标
        this.recordPerformanceMetrics();
        
        // 启动后台优化任务
        this.startBackgroundOptimizations();
        
        console.log(`📊 页面完全加载耗时: ${(this.performanceMetrics.windowLoaded - this.performanceMetrics.startTime).toFixed(2)}ms`);
    }

    // 记录性能指标
    recordPerformanceMetrics() {
        if (typeof performance !== 'undefined' && performance.getEntriesByType) {
            const navigation = performance.getEntriesByType('navigation')[0];
            if (navigation) {
                console.log('📊 性能指标:', {
                    DNS查询: `${navigation.domainLookupEnd - navigation.domainLookupStart}ms`,
                    TCP连接: `${navigation.connectEnd - navigation.connectStart}ms`,
                    请求响应: `${navigation.responseEnd - navigation.requestStart}ms`,
                    DOM解析: `${navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart}ms`,
                    资源加载: `${navigation.loadEventEnd - navigation.loadEventStart}ms`
                });
            }
        }
    }

    // 启动后台优化任务
    startBackgroundOptimizations() {
        // 预加载可能访问的页面
        this.preloadLikelyPages();
        
        // 清理过期缓存
        this.cleanupExpiredCache();
        
        // 优化图片质量
        this.optimizeImageQuality();
    }

    // 预加载可能访问的页面
    preloadLikelyPages() {
        const likelyPages = [
            '/exercises/',
            '/achievements/',
            '/category/data-structures/'
        ];

        // 在空闲时间预加载
        if ('requestIdleCallback' in window) {
            requestIdleCallback(() => {
                likelyPages.forEach(url => {
                    const link = document.createElement('link');
                    link.rel = 'prefetch';
                    link.href = url;
                    document.head.appendChild(link);
                });
            });
        }
    }

    // 清理过期缓存
    cleanupExpiredCache() {
        if ('caches' in window) {
            caches.keys().then(cacheNames => {
                cacheNames.forEach(cacheName => {
                    if (cacheName.includes('old') || cacheName.includes('expired')) {
                        caches.delete(cacheName);
                    }
                });
            });
        }
    }

    // 优化图片质量
    optimizeImageQuality() {
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            if (img.complete && img.naturalWidth > 0) {
                // 检查图片是否过大
                if (img.naturalWidth > img.offsetWidth * 2) {
                    console.log('📷 发现过大图片，建议优化:', img.src);
                }
            }
        });
    }

    // 添加延迟任务
    addDeferredTask(task) {
        this.deferredTasks.push(task);
    }

    // 显示加载状态
    showLoading(element, message = '加载中...') {
        if (this.loadingElements.has(element)) return;
        
        this.loadingElements.add(element);
        element.classList.add('loading');
        
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-message">${message}</div>
        `;
        
        element.style.position = 'relative';
        element.appendChild(loadingOverlay);
    }

    // 隐藏加载状态
    hideLoading(element) {
        if (!this.loadingElements.has(element)) return;
        
        this.loadingElements.delete(element);
        element.classList.remove('loading');
        
        const overlay = element.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
}

// 创建全局实例
window.performanceOptimizer = new PerformanceOptimizer();

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceOptimizer;
}
