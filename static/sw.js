/**
 * Service Worker - 离线缓存和性能优化
 */

const CACHE_NAME = 'cs-learning-platform-v1.0.0';
const STATIC_CACHE = 'static-v1.0.0';
const DYNAMIC_CACHE = 'dynamic-v1.0.0';

// 需要缓存的静态资源
const STATIC_ASSETS = [
    '/',
    '/static/css/critical.css',
    '/static/js/performance-optimizer.js',
    '/static/js/loading-manager.js',
    '/static/js/cache-manager.js',
    '/static/manifest.json',
    // 常用页面
    '/exercises/',
    '/achievements/',
    '/category/data-structures/',
    '/category/algorithm-design/',
    // 外部资源
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// 动态缓存策略配置
const CACHE_STRATEGIES = {
    // 静态资源：缓存优先
    static: {
        pattern: /\.(css|js|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot)$/,
        strategy: 'cacheFirst',
        maxAge: 30 * 24 * 60 * 60 * 1000 // 30天
    },
    // API请求：网络优先，缓存备用
    api: {
        pattern: /\/api\//,
        strategy: 'networkFirst',
        maxAge: 5 * 60 * 1000 // 5分钟
    },
    // 页面：网络优先，缓存备用
    pages: {
        pattern: /\/(exercises|achievements|category|about|profile)\//,
        strategy: 'networkFirst',
        maxAge: 10 * 60 * 1000 // 10分钟
    },
    // 其他：网络优先
    default: {
        strategy: 'networkFirst',
        maxAge: 60 * 1000 // 1分钟
    }
};

// Service Worker安装
self.addEventListener('install', event => {
    console.log('🔧 Service Worker安装中...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('📦 缓存静态资源...');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('✅ Service Worker安装完成');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('❌ Service Worker安装失败:', error);
            })
    );
});

// Service Worker激活
self.addEventListener('activate', event => {
    console.log('🚀 Service Worker激活中...');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        // 删除旧版本缓存
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('🗑️ 删除旧缓存:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('✅ Service Worker激活完成');
                return self.clients.claim();
            })
    );
});

// 拦截网络请求
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // 跳过非GET请求
    if (request.method !== 'GET') {
        return;
    }
    
    // 跳过chrome-extension等特殊协议
    if (!url.protocol.startsWith('http')) {
        return;
    }
    
    // 确定缓存策略
    const strategy = getCacheStrategy(request.url);
    
    event.respondWith(
        handleRequest(request, strategy)
    );
});

// 获取缓存策略
function getCacheStrategy(url) {
    for (const [name, config] of Object.entries(CACHE_STRATEGIES)) {
        if (config.pattern && config.pattern.test(url)) {
            return config;
        }
    }
    return CACHE_STRATEGIES.default;
}

// 处理请求
async function handleRequest(request, strategy) {
    switch (strategy.strategy) {
        case 'cacheFirst':
            return cacheFirst(request, strategy);
        case 'networkFirst':
            return networkFirst(request, strategy);
        case 'staleWhileRevalidate':
            return staleWhileRevalidate(request, strategy);
        default:
            return networkFirst(request, strategy);
    }
}

// 缓存优先策略
async function cacheFirst(request, strategy) {
    try {
        const cache = await caches.open(STATIC_CACHE);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            // 检查缓存是否过期
            const cacheTime = await getCacheTime(request.url);
            if (cacheTime && Date.now() - cacheTime < strategy.maxAge) {
                return cachedResponse;
            }
        }
        
        // 缓存未命中或已过期，从网络获取
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const responseClone = networkResponse.clone();
            await cache.put(request, responseClone);
            await setCacheTime(request.url, Date.now());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('缓存优先策略失败:', error);
        
        // 网络失败，尝试返回缓存
        const cache = await caches.open(STATIC_CACHE);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // 返回离线页面
        return getOfflinePage();
    }
}

// 网络优先策略
async function networkFirst(request, strategy) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            const responseClone = networkResponse.clone();
            await cache.put(request, responseClone);
            await setCacheTime(request.url, Date.now());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('网络请求失败，尝试缓存:', request.url);
        
        // 网络失败，尝试缓存
        const cache = await caches.open(DYNAMIC_CACHE);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            // 检查缓存是否过期
            const cacheTime = await getCacheTime(request.url);
            if (!cacheTime || Date.now() - cacheTime < strategy.maxAge) {
                return cachedResponse;
            }
        }
        
        // 返回离线页面
        return getOfflinePage();
    }
}

// 过期重新验证策略
async function staleWhileRevalidate(request, strategy) {
    const cache = await caches.open(DYNAMIC_CACHE);
    const cachedResponse = await cache.match(request);
    
    // 后台更新缓存
    const networkResponsePromise = fetch(request)
        .then(networkResponse => {
            if (networkResponse.ok) {
                const responseClone = networkResponse.clone();
                cache.put(request, responseClone);
                setCacheTime(request.url, Date.now());
            }
            return networkResponse;
        })
        .catch(error => {
            console.log('后台更新失败:', error);
        });
    
    // 立即返回缓存（如果有）
    if (cachedResponse) {
        return cachedResponse;
    }
    
    // 没有缓存，等待网络响应
    return networkResponsePromise || getOfflinePage();
}

// 获取缓存时间
async function getCacheTime(url) {
    try {
        const cache = await caches.open('cache-metadata');
        const response = await cache.match(url + '_timestamp');
        if (response) {
            const timestamp = await response.text();
            return parseInt(timestamp);
        }
    } catch (error) {
        console.error('获取缓存时间失败:', error);
    }
    return null;
}

// 设置缓存时间
async function setCacheTime(url, timestamp) {
    try {
        const cache = await caches.open('cache-metadata');
        await cache.put(url + '_timestamp', new Response(timestamp.toString()));
    } catch (error) {
        console.error('设置缓存时间失败:', error);
    }
}

// 获取离线页面
function getOfflinePage() {
    return new Response(`
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>离线模式 - CS学习平台</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    text-align: center;
                }
                .offline-container {
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(20px);
                    border-radius: 20px;
                    padding: 40px;
                    max-width: 400px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
                .offline-icon {
                    font-size: 4rem;
                    margin-bottom: 20px;
                }
                .offline-title {
                    font-size: 1.5rem;
                    font-weight: 600;
                    margin-bottom: 15px;
                }
                .offline-message {
                    opacity: 0.9;
                    line-height: 1.6;
                    margin-bottom: 20px;
                }
                .retry-btn {
                    background: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    color: white;
                    padding: 10px 20px;
                    border-radius: 10px;
                    cursor: pointer;
                    font-weight: 600;
                }
                .retry-btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                }
            </style>
        </head>
        <body>
            <div class="offline-container">
                <div class="offline-icon">📡</div>
                <div class="offline-title">网络连接中断</div>
                <div class="offline-message">
                    抱歉，当前无法连接到服务器。<br>
                    请检查您的网络连接后重试。
                </div>
                <button class="retry-btn" onclick="window.location.reload()">
                    重新加载
                </button>
            </div>
        </body>
        </html>
    `, {
        headers: {
            'Content-Type': 'text/html; charset=utf-8'
        }
    });
}

// 后台同步
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

// 执行后台同步
async function doBackgroundSync() {
    console.log('🔄 执行后台同步...');
    
    try {
        // 清理过期缓存
        await cleanupExpiredCache();
        
        // 预加载重要资源
        await preloadImportantResources();
        
        console.log('✅ 后台同步完成');
    } catch (error) {
        console.error('❌ 后台同步失败:', error);
    }
}

// 清理过期缓存
async function cleanupExpiredCache() {
    const cacheNames = await caches.keys();
    
    for (const cacheName of cacheNames) {
        if (cacheName.includes('old') || cacheName.includes('expired')) {
            await caches.delete(cacheName);
            console.log('🗑️ 删除过期缓存:', cacheName);
        }
    }
}

// 预加载重要资源
async function preloadImportantResources() {
    const importantUrls = [
        '/exercises/',
        '/achievements/',
        '/category/data-structures/'
    ];
    
    const cache = await caches.open(DYNAMIC_CACHE);
    
    for (const url of importantUrls) {
        try {
            const response = await fetch(url);
            if (response.ok) {
                await cache.put(url, response);
            }
        } catch (error) {
            console.log('预加载失败:', url, error);
        }
    }
}

// 推送通知
self.addEventListener('push', event => {
    if (event.data) {
        const data = event.data.json();
        
        const options = {
            body: data.body,
            icon: '/static/icon-192x192.png',
            badge: '/static/badge-72x72.png',
            vibrate: [100, 50, 100],
            data: data.data,
            actions: data.actions
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

// 通知点击
self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    if (event.action === 'open') {
        event.waitUntil(
            clients.openWindow(event.notification.data.url)
        );
    }
});

console.log('🎯 Service Worker已加载');
