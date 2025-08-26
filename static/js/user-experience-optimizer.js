/**
 * 用户体验优化器
 * 提供智能的用户体验优化功能
 */

class UserExperienceOptimizer {
    constructor() {
        this.userPreferences = this.loadUserPreferences();
        this.sessionData = this.initSessionData();
        this.interactionMetrics = {
            clicks: 0,
            scrolls: 0,
            timeOnPage: 0,
            bounceRate: 0
        };
        
        this.init();
    }

    init() {
        console.log('🎯 用户体验优化器初始化中...');
        
        // 初始化各种优化功能
        this.initAccessibilityEnhancements();
        this.initPersonalization();
        this.initSmartNavigation();
        this.initPerformanceFeedback();
        this.initErrorHandling();
        this.initAnalytics();
        
        // 监听用户交互
        this.setupInteractionTracking();
        
        console.log('✅ 用户体验优化器初始化完成');
    }

    // 无障碍功能增强
    initAccessibilityEnhancements() {
        // 键盘导航增强
        this.enhanceKeyboardNavigation();
        
        // 屏幕阅读器支持
        this.enhanceScreenReaderSupport();
        
        // 高对比度模式
        this.initHighContrastMode();
        
        // 字体大小调节
        this.initFontSizeControls();
        
        // 动画控制
        this.initAnimationControls();
    }

    // 增强键盘导航
    enhanceKeyboardNavigation() {
        // 添加跳转到主内容的链接
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = '跳转到主内容';
        skipLink.className = 'skip-link';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: #000;
            color: #fff;
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 10000;
            transition: top 0.3s;
        `;
        
        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '6px';
        });
        
        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);

        // 增强焦点可见性
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });

        // 添加焦点样式
        const style = document.createElement('style');
        style.textContent = `
            .keyboard-navigation *:focus {
                outline: 3px solid #667eea !important;
                outline-offset: 2px !important;
            }
        `;
        document.head.appendChild(style);
    }

    // 屏幕阅读器支持
    enhanceScreenReaderSupport() {
        // 为动态内容添加aria-live区域
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.style.cssText = `
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        `;
        document.body.appendChild(liveRegion);
        
        window.announceToScreenReader = (message) => {
            liveRegion.textContent = message;
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        };

        // 为图片添加alt属性检查
        document.querySelectorAll('img:not([alt])').forEach(img => {
            img.setAttribute('alt', '装饰性图片');
        });

        // 为链接添加描述性文本
        document.querySelectorAll('a').forEach(link => {
            if (!link.getAttribute('aria-label') && !link.textContent.trim()) {
                link.setAttribute('aria-label', '链接');
            }
        });
    }

    // 高对比度模式
    initHighContrastMode() {
        const toggleButton = document.createElement('button');
        toggleButton.textContent = '🎨 高对比度';
        toggleButton.className = 'accessibility-toggle high-contrast-toggle';
        toggleButton.setAttribute('aria-label', '切换高对比度模式');
        
        toggleButton.addEventListener('click', () => {
            document.body.classList.toggle('high-contrast');
            const isEnabled = document.body.classList.contains('high-contrast');
            
            toggleButton.textContent = isEnabled ? '🎨 标准模式' : '🎨 高对比度';
            this.saveUserPreference('highContrast', isEnabled);
            
            window.announceToScreenReader(
                isEnabled ? '已启用高对比度模式' : '已关闭高对比度模式'
            );
        });

        this.addAccessibilityControl(toggleButton);

        // 应用保存的偏好
        if (this.userPreferences.highContrast) {
            document.body.classList.add('high-contrast');
            toggleButton.textContent = '🎨 标准模式';
        }

        // 添加高对比度样式
        const style = document.createElement('style');
        style.textContent = `
            .high-contrast {
                filter: contrast(150%) brightness(120%);
            }
            .high-contrast .card,
            .high-contrast .btn {
                border: 2px solid #000 !important;
            }
            .high-contrast a {
                text-decoration: underline !important;
            }
        `;
        document.head.appendChild(style);
    }

    // 字体大小控制
    initFontSizeControls() {
        const container = document.createElement('div');
        container.className = 'font-size-controls';
        
        const decreaseBtn = document.createElement('button');
        decreaseBtn.textContent = 'A-';
        decreaseBtn.className = 'accessibility-toggle';
        decreaseBtn.setAttribute('aria-label', '减小字体');
        
        const resetBtn = document.createElement('button');
        resetBtn.textContent = 'A';
        resetBtn.className = 'accessibility-toggle';
        resetBtn.setAttribute('aria-label', '重置字体大小');
        
        const increaseBtn = document.createElement('button');
        increaseBtn.textContent = 'A+';
        increaseBtn.className = 'accessibility-toggle';
        increaseBtn.setAttribute('aria-label', '增大字体');

        let currentFontSize = this.userPreferences.fontSize || 100;

        const updateFontSize = (size) => {
            currentFontSize = Math.max(80, Math.min(150, size));
            document.documentElement.style.fontSize = `${currentFontSize}%`;
            this.saveUserPreference('fontSize', currentFontSize);
            
            window.announceToScreenReader(`字体大小已调整为 ${currentFontSize}%`);
        };

        decreaseBtn.addEventListener('click', () => updateFontSize(currentFontSize - 10));
        resetBtn.addEventListener('click', () => updateFontSize(100));
        increaseBtn.addEventListener('click', () => updateFontSize(currentFontSize + 10));

        container.appendChild(decreaseBtn);
        container.appendChild(resetBtn);
        container.appendChild(increaseBtn);
        
        this.addAccessibilityControl(container);

        // 应用保存的字体大小
        if (currentFontSize !== 100) {
            updateFontSize(currentFontSize);
        }
    }

    // 动画控制
    initAnimationControls() {
        const toggleButton = document.createElement('button');
        toggleButton.textContent = '⚡ 减少动画';
        toggleButton.className = 'accessibility-toggle animation-toggle';
        toggleButton.setAttribute('aria-label', '切换动画效果');
        
        toggleButton.addEventListener('click', () => {
            document.body.classList.toggle('reduce-motion');
            const isReduced = document.body.classList.contains('reduce-motion');
            
            toggleButton.textContent = isReduced ? '⚡ 启用动画' : '⚡ 减少动画';
            this.saveUserPreference('reduceMotion', isReduced);
            
            window.announceToScreenReader(
                isReduced ? '已减少动画效果' : '已启用动画效果'
            );
        });

        this.addAccessibilityControl(toggleButton);

        // 应用保存的偏好或系统偏好
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (this.userPreferences.reduceMotion || prefersReducedMotion) {
            document.body.classList.add('reduce-motion');
            toggleButton.textContent = '⚡ 启用动画';
        }
    }

    // 添加无障碍控制面板
    addAccessibilityControl(element) {
        let panel = document.querySelector('.accessibility-panel');
        
        if (!panel) {
            panel = document.createElement('div');
            panel.className = 'accessibility-panel';
            panel.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 15px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
                transform: translateX(100%);
                transition: transform 0.3s ease;
            `;

            const togglePanelBtn = document.createElement('button');
            togglePanelBtn.textContent = '♿';
            togglePanelBtn.className = 'accessibility-panel-toggle';
            togglePanelBtn.setAttribute('aria-label', '打开无障碍设置');
            togglePanelBtn.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: #667eea;
                color: white;
                border: none;
                font-size: 20px;
                cursor: pointer;
                z-index: 10000;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                transition: all 0.3s ease;
            `;

            togglePanelBtn.addEventListener('click', () => {
                const isOpen = panel.style.transform === 'translateX(0px)';
                panel.style.transform = isOpen ? 'translateX(100%)' : 'translateX(0px)';
                togglePanelBtn.style.right = isOpen ? '20px' : '280px';
                togglePanelBtn.setAttribute('aria-label', 
                    isOpen ? '打开无障碍设置' : '关闭无障碍设置'
                );
            });

            document.body.appendChild(panel);
            document.body.appendChild(togglePanelBtn);
        }

        // 为控制元素添加样式
        element.style.cssText = `
            background: rgba(102, 126, 234, 0.1);
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 8px;
            padding: 8px 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        `;

        element.addEventListener('mouseenter', () => {
            element.style.background = 'rgba(102, 126, 234, 0.2)';
        });

        element.addEventListener('mouseleave', () => {
            element.style.background = 'rgba(102, 126, 234, 0.1)';
        });

        panel.appendChild(element);
    }

    // 个性化功能
    initPersonalization() {
        // 记住用户偏好
        this.applyUserPreferences();
        
        // 智能推荐
        this.initSmartRecommendations();
        
        // 学习进度跟踪
        this.initProgressTracking();
    }

    // 应用用户偏好
    applyUserPreferences() {
        const prefs = this.userPreferences;
        
        // 应用主题偏好
        if (prefs.theme) {
            document.body.classList.add(`theme-${prefs.theme}`);
        }
        
        // 应用布局偏好
        if (prefs.layout) {
            document.body.classList.add(`layout-${prefs.layout}`);
        }
    }

    // 智能导航
    initSmartNavigation() {
        // 面包屑导航增强
        this.enhanceBreadcrumbs();
        
        // 快捷键支持
        this.initKeyboardShortcuts();
        
        // 智能搜索建议
        this.initSmartSearch();
    }

    // 增强面包屑导航
    enhanceBreadcrumbs() {
        const breadcrumbs = document.querySelectorAll('.breadcrumb');
        breadcrumbs.forEach(breadcrumb => {
            // 添加结构化数据
            breadcrumb.setAttribute('itemscope', '');
            breadcrumb.setAttribute('itemtype', 'https://schema.org/BreadcrumbList');
            
            const items = breadcrumb.querySelectorAll('.breadcrumb-item');
            items.forEach((item, index) => {
                item.setAttribute('itemprop', 'itemListElement');
                item.setAttribute('itemscope', '');
                item.setAttribute('itemtype', 'https://schema.org/ListItem');
                
                const link = item.querySelector('a');
                if (link) {
                    link.setAttribute('itemprop', 'item');
                    
                    const span = document.createElement('span');
                    span.setAttribute('itemprop', 'name');
                    span.textContent = link.textContent;
                    link.appendChild(span);
                }
                
                const position = document.createElement('meta');
                position.setAttribute('itemprop', 'position');
                position.setAttribute('content', (index + 1).toString());
                item.appendChild(position);
            });
        });
    }

    // 键盘快捷键
    initKeyboardShortcuts() {
        const shortcuts = {
            'Alt+H': () => window.location.href = '/',
            'Alt+S': () => {
                const searchInput = document.querySelector('input[type="search"], .search-input');
                if (searchInput) searchInput.focus();
            },
            'Alt+M': () => {
                const menu = document.querySelector('.navbar-toggler');
                if (menu) menu.click();
            },
            'Escape': () => {
                // 关闭模态框或下拉菜单
                const modal = document.querySelector('.modal.show');
                if (modal) {
                    const closeBtn = modal.querySelector('.btn-close, .close');
                    if (closeBtn) closeBtn.click();
                }
            }
        };

        document.addEventListener('keydown', (e) => {
            const key = `${e.altKey ? 'Alt+' : ''}${e.ctrlKey ? 'Ctrl+' : ''}${e.key}`;
            if (shortcuts[key]) {
                e.preventDefault();
                shortcuts[key]();
            }
        });

        // 显示快捷键帮助
        const helpButton = document.createElement('button');
        helpButton.textContent = '❓ 快捷键';
        helpButton.className = 'accessibility-toggle';
        helpButton.addEventListener('click', this.showKeyboardShortcuts);
        this.addAccessibilityControl(helpButton);
    }

    // 显示快捷键帮助
    showKeyboardShortcuts() {
        const modal = document.createElement('div');
        modal.className = 'shortcuts-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10001;
        `;

        const content = document.createElement('div');
        content.style.cssText = `
            background: white;
            border-radius: 15px;
            padding: 30px;
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
        `;

        content.innerHTML = `
            <h3>键盘快捷键</h3>
            <ul style="list-style: none; padding: 0;">
                <li><kbd>Alt + H</kbd> - 返回首页</li>
                <li><kbd>Alt + S</kbd> - 聚焦搜索框</li>
                <li><kbd>Alt + M</kbd> - 打开菜单</li>
                <li><kbd>Tab</kbd> - 导航到下一个元素</li>
                <li><kbd>Shift + Tab</kbd> - 导航到上一个元素</li>
                <li><kbd>Enter</kbd> - 激活链接或按钮</li>
                <li><kbd>Escape</kbd> - 关闭模态框</li>
            </ul>
            <button class="btn btn-primary" onclick="this.closest('.shortcuts-modal').remove()">
                关闭
            </button>
        `;

        modal.appendChild(content);
        document.body.appendChild(modal);

        // 点击外部关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    // 性能反馈
    initPerformanceFeedback() {
        // 监控页面性能
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.entryType === 'navigation') {
                        const loadTime = entry.loadEventEnd - entry.loadEventStart;
                        if (loadTime > 3000) {
                            this.showPerformanceWarning('页面加载较慢，正在优化中...');
                        }
                    }
                }
            });
            
            observer.observe({ entryTypes: ['navigation'] });
        }
    }

    // 显示性能警告
    showPerformanceWarning(message) {
        const warning = document.createElement('div');
        warning.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: #ff9800;
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            z-index: 10000;
            max-width: 300px;
            box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
        `;
        warning.textContent = message;
        
        document.body.appendChild(warning);
        
        setTimeout(() => {
            warning.style.opacity = '0';
            warning.style.transition = 'opacity 0.3s ease';
            setTimeout(() => warning.remove(), 300);
        }, 5000);
    }

    // 错误处理
    initErrorHandling() {
        // 全局错误处理
        window.addEventListener('error', (e) => {
            this.handleError('JavaScript错误', e.error);
        });

        // Promise错误处理
        window.addEventListener('unhandledrejection', (e) => {
            this.handleError('Promise错误', e.reason);
        });

        // 网络错误处理
        window.addEventListener('offline', () => {
            this.showNetworkStatus(false);
        });

        window.addEventListener('online', () => {
            this.showNetworkStatus(true);
        });
    }

    // 处理错误
    handleError(type, error) {
        console.error(`${type}:`, error);
        
        // 显示用户友好的错误消息
        this.showErrorMessage('抱歉，出现了一个小问题。页面功能可能受到影响。');
    }

    // 显示错误消息
    showErrorMessage(message) {
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #f44336;
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            z-index: 10000;
            box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
        `;
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.style.opacity = '0';
            errorDiv.style.transition = 'opacity 0.3s ease';
            setTimeout(() => errorDiv.remove(), 300);
        }, 5000);
    }

    // 显示网络状态
    showNetworkStatus(isOnline) {
        const status = document.createElement('div');
        status.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: ${isOnline ? '#4caf50' : '#f44336'};
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            z-index: 10000;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        `;
        status.textContent = isOnline ? '网络连接已恢复' : '网络连接中断';
        
        document.body.appendChild(status);
        
        setTimeout(() => {
            status.style.opacity = '0';
            status.style.transition = 'opacity 0.3s ease';
            setTimeout(() => status.remove(), 300);
        }, 3000);
    }

    // 交互跟踪
    setupInteractionTracking() {
        // 点击跟踪
        document.addEventListener('click', () => {
            this.interactionMetrics.clicks++;
        });

        // 滚动跟踪
        let scrollTimeout;
        document.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                this.interactionMetrics.scrolls++;
            }, 100);
        });

        // 页面停留时间
        this.sessionData.startTime = Date.now();
        
        window.addEventListener('beforeunload', () => {
            this.interactionMetrics.timeOnPage = Date.now() - this.sessionData.startTime;
            this.saveSessionData();
        });
    }

    // 分析功能
    initAnalytics() {
        // 收集用户行为数据（匿名）
        this.collectUsageData();
    }

    // 收集使用数据
    collectUsageData() {
        const data = {
            userAgent: navigator.userAgent,
            screenResolution: `${screen.width}x${screen.height}`,
            viewport: `${window.innerWidth}x${window.innerHeight}`,
            colorDepth: screen.colorDepth,
            language: navigator.language,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            timestamp: Date.now()
        };

        // 存储到本地（不发送到服务器，保护隐私）
        localStorage.setItem('usage_data', JSON.stringify(data));
    }

    // 用户偏好管理
    loadUserPreferences() {
        try {
            const prefs = localStorage.getItem('user_preferences');
            return prefs ? JSON.parse(prefs) : {};
        } catch (error) {
            console.error('加载用户偏好失败:', error);
            return {};
        }
    }

    saveUserPreference(key, value) {
        this.userPreferences[key] = value;
        try {
            localStorage.setItem('user_preferences', JSON.stringify(this.userPreferences));
        } catch (error) {
            console.error('保存用户偏好失败:', error);
        }
    }

    // 会话数据管理
    initSessionData() {
        return {
            startTime: Date.now(),
            pageViews: 1,
            interactions: 0
        };
    }

    saveSessionData() {
        try {
            sessionStorage.setItem('session_data', JSON.stringify({
                ...this.sessionData,
                interactionMetrics: this.interactionMetrics
            }));
        } catch (error) {
            console.error('保存会话数据失败:', error);
        }
    }
}

// 创建全局实例
window.uxOptimizer = new UserExperienceOptimizer();

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UserExperienceOptimizer;
}
