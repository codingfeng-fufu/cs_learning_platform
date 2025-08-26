/**
 * 全局加载状态管理器
 * 统一管理页面加载状态，提升用户体验
 */

class LoadingManager {
    constructor() {
        this.loadingStates = new Map();
        this.globalLoadingCount = 0;
        this.loadingQueue = [];
        this.init();
    }

    init() {
        // 创建全局加载指示器
        this.createGlobalLoader();
        
        // 监听页面导航
        this.setupNavigationLoading();
        
        // 监听AJAX请求
        this.setupAjaxLoading();
        
        console.log('📊 加载管理器初始化完成');
    }

    // 创建全局加载指示器
    createGlobalLoader() {
        const loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.className = 'global-loader hidden';
        loader.innerHTML = `
            <div class="global-loader-backdrop"></div>
            <div class="global-loader-content">
                <div class="global-loader-spinner"></div>
                <div class="global-loader-text">加载中...</div>
                <div class="global-loader-progress">
                    <div class="global-loader-progress-bar"></div>
                </div>
            </div>
        `;
        
        document.body.appendChild(loader);
        
        // 添加样式
        this.addGlobalLoaderStyles();
    }

    // 添加全局加载器样式
    addGlobalLoaderStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .global-loader {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: opacity 0.3s ease;
            }
            
            .global-loader.hidden {
                opacity: 0;
                pointer-events: none;
            }
            
            .global-loader.visible {
                opacity: 1;
                pointer-events: all;
            }
            
            .global-loader-backdrop {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(10px);
            }
            
            .global-loader-content {
                position: relative;
                text-align: center;
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(0, 0, 0, 0.05);
                min-width: 200px;
            }
            
            .global-loader-spinner {
                width: 50px;
                height: 50px;
                border: 4px solid #e2e8f0;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            .global-loader-text {
                font-size: 1.1rem;
                font-weight: 600;
                color: #4a5568;
                margin-bottom: 20px;
            }
            
            .global-loader-progress {
                width: 100%;
                height: 4px;
                background: #e2e8f0;
                border-radius: 2px;
                overflow: hidden;
            }
            
            .global-loader-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                border-radius: 2px;
                width: 0%;
                transition: width 0.3s ease;
                animation: progress-pulse 2s ease-in-out infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            @keyframes progress-pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            
            /* 页面顶部进度条 */
            .page-progress-bar {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: transparent;
                z-index: 10001;
                pointer-events: none;
            }
            
            .page-progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                width: 0%;
                transition: width 0.3s ease;
                box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
            }
            
            /* 元素加载状态 */
            .element-loading {
                position: relative;
                pointer-events: none;
                opacity: 0.7;
            }
            
            .element-loading::after {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 20px;
                height: 20px;
                margin: -10px 0 0 -10px;
                border: 2px solid #e2e8f0;
                border-top: 2px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                z-index: 1;
            }
        `;
        document.head.appendChild(style);
    }

    // 设置导航加载 - 完全不干扰浏览器原生功能
    setupNavigationLoading() {
        // 完全移除所有可能干扰浏览器导航的代码
        // 不监听 beforeunload, popstate, 或任何导航相关事件
        // 让浏览器完全自主处理回退/前进/刷新等操作

        // 只在页面完全加载后隐藏任何残留的加载状态
        window.addEventListener('load', () => {
            this.hideGlobalLoading();
        });

        // 只在页面卸载时清理资源，不显示任何加载状态
        window.addEventListener('beforeunload', () => {
            // 仅清理资源，不显示加载状态
            this.clearAllLoading();
        });
    }

    // 设置AJAX加载
    setupAjaxLoading() {
        // 拦截fetch请求
        const originalFetch = window.fetch;
        window.fetch = (...args) => {
            const loadingId = this.generateLoadingId();
            this.startLoading(loadingId, 'network');
            
            return originalFetch(...args)
                .then(response => {
                    this.stopLoading(loadingId);
                    return response;
                })
                .catch(error => {
                    this.stopLoading(loadingId);
                    throw error;
                });
        };

        // 拦截XMLHttpRequest
        const originalXHROpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(...args) {
            const loadingId = this._loadingId = this._loadingId || window.loadingManager.generateLoadingId();
            window.loadingManager.startLoading(loadingId, 'network');
            
            this.addEventListener('loadend', () => {
                window.loadingManager.stopLoading(loadingId);
            });
            
            return originalXHROpen.apply(this, args);
        };
    }

    // 显示全局加载
    showGlobalLoading(text = '加载中...', progress = 0) {
        const loader = document.getElementById('global-loader');
        const textElement = loader.querySelector('.global-loader-text');
        const progressBar = loader.querySelector('.global-loader-progress-bar');
        
        textElement.textContent = text;
        progressBar.style.width = `${progress}%`;
        
        loader.classList.remove('hidden');
        loader.classList.add('visible');
        
        // 防止页面滚动
        document.body.style.overflow = 'hidden';
    }

    // 隐藏全局加载
    hideGlobalLoading() {
        const loader = document.getElementById('global-loader');
        loader.classList.remove('visible');
        loader.classList.add('hidden');
        
        // 恢复页面滚动
        document.body.style.overflow = '';
    }

    // 更新全局加载进度
    updateGlobalProgress(progress, text) {
        const loader = document.getElementById('global-loader');
        if (loader.classList.contains('visible')) {
            const textElement = loader.querySelector('.global-loader-text');
            const progressBar = loader.querySelector('.global-loader-progress-bar');
            
            if (text) textElement.textContent = text;
            progressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
        }
    }

    // 显示页面顶部进度条
    showPageProgress() {
        let progressBar = document.querySelector('.page-progress-bar');
        if (!progressBar) {
            progressBar = document.createElement('div');
            progressBar.className = 'page-progress-bar';
            progressBar.innerHTML = '<div class="page-progress-fill"></div>';
            document.body.appendChild(progressBar);
        }

        const fill = progressBar.querySelector('.page-progress-fill');
        let progress = 0;
        
        const updateProgress = () => {
            progress += Math.random() * 30;
            if (progress > 90) progress = 90;
            
            fill.style.width = `${progress}%`;
            
            if (progress < 90) {
                setTimeout(updateProgress, 200 + Math.random() * 300);
            }
        };
        
        updateProgress();
        
        // 页面加载完成后完成进度条
        window.addEventListener('load', () => {
            fill.style.width = '100%';
            setTimeout(() => {
                progressBar.style.opacity = '0';
                setTimeout(() => progressBar.remove(), 300);
            }, 200);
        });
    }

    // 开始加载
    startLoading(id, type = 'default') {
        this.loadingStates.set(id, { type, startTime: Date.now() });
        this.globalLoadingCount++;
        
        if (this.globalLoadingCount === 1) {
            this.showGlobalLoading();
        }
        
        return id;
    }

    // 停止加载
    stopLoading(id) {
        if (this.loadingStates.has(id)) {
            const loadingState = this.loadingStates.get(id);
            const duration = Date.now() - loadingState.startTime;
            
            console.log(`⏱️ 加载完成 [${id}]: ${duration}ms`);
            
            this.loadingStates.delete(id);
            this.globalLoadingCount--;
            
            if (this.globalLoadingCount <= 0) {
                this.globalLoadingCount = 0;
                setTimeout(() => this.hideGlobalLoading(), 100);
            }
        }
    }

    // 为元素显示加载状态
    showElementLoading(element, text) {
        if (!element) return;
        
        element.classList.add('element-loading');
        element.setAttribute('data-loading-text', text || '加载中...');
        
        // 禁用交互
        element.style.pointerEvents = 'none';
    }

    // 隐藏元素加载状态
    hideElementLoading(element) {
        if (!element) return;
        
        element.classList.remove('element-loading');
        element.removeAttribute('data-loading-text');
        
        // 恢复交互
        element.style.pointerEvents = '';
    }

    // 批量加载管理
    createBatchLoader(tasks, onProgress, onComplete) {
        const batchId = this.generateLoadingId();
        let completed = 0;
        const total = tasks.length;
        
        this.showGlobalLoading(`处理中... (0/${total})`);
        
        const executeNext = () => {
            if (completed >= total) {
                this.hideGlobalLoading();
                if (onComplete) onComplete();
                return;
            }
            
            const task = tasks[completed];
            const taskPromise = typeof task === 'function' ? task() : task;
            
            Promise.resolve(taskPromise)
                .then(() => {
                    completed++;
                    const progress = (completed / total) * 100;
                    
                    this.updateGlobalProgress(progress, `处理中... (${completed}/${total})`);
                    
                    if (onProgress) onProgress(completed, total, progress);
                    
                    // 短暂延迟，让用户看到进度
                    setTimeout(executeNext, 50);
                })
                .catch(error => {
                    console.error('批量任务执行失败:', error);
                    completed++;
                    setTimeout(executeNext, 50);
                });
        };
        
        executeNext();
        return batchId;
    }

    // 生成加载ID
    generateLoadingId() {
        return `loading_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // 获取加载统计
    getLoadingStats() {
        return {
            activeLoading: this.globalLoadingCount,
            loadingStates: Array.from(this.loadingStates.entries()).map(([id, state]) => ({
                id,
                type: state.type,
                duration: Date.now() - state.startTime
            }))
        };
    }

    // 清理所有加载状态
    clearAllLoading() {
        this.loadingStates.clear();
        this.globalLoadingCount = 0;
        this.hideGlobalLoading();
        
        // 清理所有元素加载状态
        document.querySelectorAll('.element-loading').forEach(el => {
            this.hideElementLoading(el);
        });
    }
}

// 创建全局实例
window.loadingManager = new LoadingManager();

// 便捷方法
window.showLoading = (text, progress) => window.loadingManager.showGlobalLoading(text, progress);
window.hideLoading = () => window.loadingManager.hideGlobalLoading();
window.updateProgress = (progress, text) => window.loadingManager.updateGlobalProgress(progress, text);

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LoadingManager;
}
