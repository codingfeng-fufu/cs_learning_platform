/**
 * 缓存管理器
 * 智能缓存数据和资源，提升页面加载速度
 */

class CacheManager {
    constructor() {
        this.memoryCache = new Map();
        this.storageCache = window.localStorage;
        this.sessionCache = window.sessionStorage;
        this.cacheConfig = {
            maxMemorySize: 50 * 1024 * 1024, // 50MB
            maxStorageSize: 100 * 1024 * 1024, // 100MB
            defaultTTL: 30 * 60 * 1000, // 30分钟
            cleanupInterval: 5 * 60 * 1000 // 5分钟清理一次
        };
        
        this.init();
    }

    init() {
        console.log('💾 缓存管理器初始化中...');
        
        // 启动定期清理
        this.startCleanupTimer();
        
        // 监听存储空间变化
        this.monitorStorageUsage();
        
        // 页面卸载时清理
        window.addEventListener('beforeunload', () => this.cleanup());
        
        console.log('✅ 缓存管理器初始化完成');
    }

    // 设置缓存
    set(key, data, options = {}) {
        const {
            ttl = this.cacheConfig.defaultTTL,
            storage = 'memory',
            compress = false,
            priority = 'normal'
        } = options;

        const cacheItem = {
            data,
            timestamp: Date.now(),
            ttl,
            priority,
            size: this.calculateSize(data),
            compressed: compress
        };

        // 压缩数据（如果需要）
        if (compress && typeof data === 'object') {
            cacheItem.data = this.compressData(data);
            cacheItem.compressed = true;
        }

        try {
            switch (storage) {
                case 'memory':
                    this.setMemoryCache(key, cacheItem);
                    break;
                case 'local':
                    this.setStorageCache(key, cacheItem, this.storageCache);
                    break;
                case 'session':
                    this.setStorageCache(key, cacheItem, this.sessionCache);
                    break;
                default:
                    this.setMemoryCache(key, cacheItem);
            }
            
            console.log(`💾 缓存已设置 [${key}] (${storage}): ${this.formatSize(cacheItem.size)}`);
            return true;
        } catch (error) {
            console.error('缓存设置失败:', error);
            return false;
        }
    }

    // 获取缓存
    get(key, storage = 'memory') {
        try {
            let cacheItem;
            
            switch (storage) {
                case 'memory':
                    cacheItem = this.memoryCache.get(key);
                    break;
                case 'local':
                    cacheItem = this.getStorageCache(key, this.storageCache);
                    break;
                case 'session':
                    cacheItem = this.getStorageCache(key, this.sessionCache);
                    break;
                case 'auto':
                    // 自动查找最佳缓存
                    cacheItem = this.memoryCache.get(key) ||
                               this.getStorageCache(key, this.sessionCache) ||
                               this.getStorageCache(key, this.storageCache);
                    break;
                default:
                    cacheItem = this.memoryCache.get(key);
            }

            if (!cacheItem) {
                return null;
            }

            // 检查是否过期
            if (this.isExpired(cacheItem)) {
                this.delete(key, storage);
                return null;
            }

            // 解压数据（如果需要）
            let data = cacheItem.data;
            if (cacheItem.compressed) {
                data = this.decompressData(data);
            }

            console.log(`💾 缓存命中 [${key}] (${storage})`);
            return data;
        } catch (error) {
            console.error('缓存获取失败:', error);
            return null;
        }
    }

    // 删除缓存
    delete(key, storage = 'all') {
        try {
            let deleted = false;
            
            if (storage === 'all' || storage === 'memory') {
                deleted = this.memoryCache.delete(key) || deleted;
            }
            
            if (storage === 'all' || storage === 'local') {
                this.storageCache.removeItem(key);
                deleted = true;
            }
            
            if (storage === 'all' || storage === 'session') {
                this.sessionCache.removeItem(key);
                deleted = true;
            }
            
            if (deleted) {
                console.log(`💾 缓存已删除 [${key}]`);
            }
            
            return deleted;
        } catch (error) {
            console.error('缓存删除失败:', error);
            return false;
        }
    }

    // 清空所有缓存
    clear(storage = 'all') {
        try {
            if (storage === 'all' || storage === 'memory') {
                this.memoryCache.clear();
            }
            
            if (storage === 'all' || storage === 'local') {
                this.clearStorageCache(this.storageCache);
            }
            
            if (storage === 'all' || storage === 'session') {
                this.clearStorageCache(this.sessionCache);
            }
            
            console.log(`💾 缓存已清空 (${storage})`);
            return true;
        } catch (error) {
            console.error('缓存清空失败:', error);
            return false;
        }
    }

    // 设置内存缓存
    setMemoryCache(key, cacheItem) {
        // 检查内存使用量
        if (this.getMemoryUsage() + cacheItem.size > this.cacheConfig.maxMemorySize) {
            this.evictMemoryCache();
        }
        
        this.memoryCache.set(key, cacheItem);
    }

    // 设置存储缓存
    setStorageCache(key, cacheItem, storage) {
        const serialized = JSON.stringify(cacheItem);
        
        // 检查存储空间
        if (this.getStorageUsage(storage) + serialized.length > this.cacheConfig.maxStorageSize) {
            this.evictStorageCache(storage);
        }
        
        storage.setItem(key, serialized);
    }

    // 获取存储缓存
    getStorageCache(key, storage) {
        const serialized = storage.getItem(key);
        if (!serialized) return null;
        
        try {
            return JSON.parse(serialized);
        } catch (error) {
            console.error('缓存反序列化失败:', error);
            storage.removeItem(key);
            return null;
        }
    }

    // 清空存储缓存
    clearStorageCache(storage) {
        const keys = [];
        for (let i = 0; i < storage.length; i++) {
            const key = storage.key(i);
            if (key && key.startsWith('cache_')) {
                keys.push(key);
            }
        }
        keys.forEach(key => storage.removeItem(key));
    }

    // 检查是否过期
    isExpired(cacheItem) {
        return Date.now() - cacheItem.timestamp > cacheItem.ttl;
    }

    // 内存缓存淘汰
    evictMemoryCache() {
        const entries = Array.from(this.memoryCache.entries());
        
        // 按优先级和时间排序
        entries.sort((a, b) => {
            const [, itemA] = a;
            const [, itemB] = b;
            
            // 优先级排序
            const priorityOrder = { low: 0, normal: 1, high: 2 };
            const priorityDiff = priorityOrder[itemA.priority] - priorityOrder[itemB.priority];
            if (priorityDiff !== 0) return priorityDiff;
            
            // 时间排序（旧的先淘汰）
            return itemA.timestamp - itemB.timestamp;
        });
        
        // 删除25%的缓存
        const deleteCount = Math.ceil(entries.length * 0.25);
        for (let i = 0; i < deleteCount; i++) {
            const [key] = entries[i];
            this.memoryCache.delete(key);
        }
        
        console.log(`💾 内存缓存淘汰: 删除了 ${deleteCount} 个项目`);
    }

    // 存储缓存淘汰
    evictStorageCache(storage) {
        const keys = [];
        const items = [];
        
        for (let i = 0; i < storage.length; i++) {
            const key = storage.key(i);
            if (key && key.startsWith('cache_')) {
                try {
                    const item = JSON.parse(storage.getItem(key));
                    keys.push(key);
                    items.push({ key, ...item });
                } catch (error) {
                    // 删除损坏的缓存项
                    storage.removeItem(key);
                }
            }
        }
        
        // 按时间排序，删除最旧的25%
        items.sort((a, b) => a.timestamp - b.timestamp);
        const deleteCount = Math.ceil(items.length * 0.25);
        
        for (let i = 0; i < deleteCount; i++) {
            storage.removeItem(items[i].key);
        }
        
        console.log(`💾 存储缓存淘汰: 删除了 ${deleteCount} 个项目`);
    }

    // 获取内存使用量
    getMemoryUsage() {
        let totalSize = 0;
        for (const [, item] of this.memoryCache) {
            totalSize += item.size;
        }
        return totalSize;
    }

    // 获取存储使用量
    getStorageUsage(storage) {
        let totalSize = 0;
        for (let i = 0; i < storage.length; i++) {
            const key = storage.key(i);
            if (key && key.startsWith('cache_')) {
                totalSize += storage.getItem(key).length;
            }
        }
        return totalSize;
    }

    // 计算数据大小
    calculateSize(data) {
        if (typeof data === 'string') {
            return data.length * 2; // UTF-16
        } else if (typeof data === 'object') {
            return JSON.stringify(data).length * 2;
        } else {
            return 8; // 基本类型大约8字节
        }
    }

    // 格式化大小显示
    formatSize(bytes) {
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(1)}${units[unitIndex]}`;
    }

    // 压缩数据
    compressData(data) {
        // 简单的JSON压缩（移除空格）
        return JSON.stringify(data);
    }

    // 解压数据
    decompressData(compressedData) {
        try {
            return JSON.parse(compressedData);
        } catch (error) {
            console.error('数据解压失败:', error);
            return compressedData;
        }
    }

    // 启动清理定时器
    startCleanupTimer() {
        setInterval(() => {
            this.cleanup();
        }, this.cacheConfig.cleanupInterval);
    }

    // 清理过期缓存
    cleanup() {
        let cleanedCount = 0;
        
        // 清理内存缓存
        for (const [key, item] of this.memoryCache) {
            if (this.isExpired(item)) {
                this.memoryCache.delete(key);
                cleanedCount++;
            }
        }
        
        // 清理存储缓存
        [this.storageCache, this.sessionCache].forEach(storage => {
            for (let i = storage.length - 1; i >= 0; i--) {
                const key = storage.key(i);
                if (key && key.startsWith('cache_')) {
                    try {
                        const item = JSON.parse(storage.getItem(key));
                        if (this.isExpired(item)) {
                            storage.removeItem(key);
                            cleanedCount++;
                        }
                    } catch (error) {
                        // 删除损坏的缓存项
                        storage.removeItem(key);
                        cleanedCount++;
                    }
                }
            }
        });
        
        if (cleanedCount > 0) {
            console.log(`💾 缓存清理完成: 清理了 ${cleanedCount} 个过期项目`);
        }
    }

    // 监控存储使用情况
    monitorStorageUsage() {
        setInterval(() => {
            const memoryUsage = this.getMemoryUsage();
            const localUsage = this.getStorageUsage(this.storageCache);
            const sessionUsage = this.getStorageUsage(this.sessionCache);
            
            console.log(`💾 缓存使用情况:`, {
                内存: this.formatSize(memoryUsage),
                本地存储: this.formatSize(localUsage),
                会话存储: this.formatSize(sessionUsage)
            });
            
            // 如果使用量过高，触发清理
            if (memoryUsage > this.cacheConfig.maxMemorySize * 0.8) {
                this.evictMemoryCache();
            }
        }, 60000); // 每分钟检查一次
    }

    // 获取缓存统计信息
    getStats() {
        return {
            memory: {
                count: this.memoryCache.size,
                size: this.formatSize(this.getMemoryUsage())
            },
            localStorage: {
                size: this.formatSize(this.getStorageUsage(this.storageCache))
            },
            sessionStorage: {
                size: this.formatSize(this.getStorageUsage(this.sessionCache))
            }
        };
    }

    // 缓存API响应
    cacheApiResponse(url, response, options = {}) {
        const key = `api_${url}`;
        return this.set(key, response, {
            storage: 'local',
            ttl: options.ttl || 10 * 60 * 1000, // 10分钟
            ...options
        });
    }

    // 获取缓存的API响应
    getCachedApiResponse(url) {
        const key = `api_${url}`;
        return this.get(key, 'local');
    }
}

// 创建全局实例
window.cacheManager = new CacheManager();

// 便捷方法
window.cache = {
    set: (key, data, options) => window.cacheManager.set(key, data, options),
    get: (key, storage) => window.cacheManager.get(key, storage),
    delete: (key, storage) => window.cacheManager.delete(key, storage),
    clear: (storage) => window.cacheManager.clear(storage)
};

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CacheManager;
}
