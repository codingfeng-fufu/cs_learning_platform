/**
 * 导航管理器
 * 处理浏览器导航、历史记录和页面状态管理
 */

class NavigationManager {
    constructor() {
        this.navigationState = {
            isNavigating: false,
            currentUrl: window.location.href,
            previousUrl: null,
            navigationStartTime: null
        };
        
        this.init();
    }

    init() {
        console.log('🧭 导航管理器初始化中...');

        // 完全禁用所有可能干扰浏览器导航的功能
        // 只保留基本的页面状态保存功能，不干扰导航

        // 仅在页面卸载时保存状态，不干扰导航过程
        window.addEventListener('beforeunload', () => {
            this.savePageState();
        });

        console.log('✅ 导航管理器初始化完成（非干扰模式）');
    }

    // 历史记录管理
    setupHistoryManagement() {
        // 保存初始状态
        this.savePageState();
        
        // 监听浏览器回退/前进
        window.addEventListener('popstate', (e) => {
            console.log('🔙 浏览器历史记录导航:', e.state);
            
            this.navigationState.previousUrl = this.navigationState.currentUrl;
            this.navigationState.currentUrl = window.location.href;
            
            // 恢复页面状态
            if (e.state) {
                this.restorePageState(e.state);
            }
            
            // 触发导航事件
            this.dispatchNavigationEvent('historychange', {
                direction: this.getNavigationDirection(),
                state: e.state,
                url: window.location.href
            });
        });

        // 监听页面加载
        window.addEventListener('load', () => {
            this.navigationState.isNavigating = false;
            this.savePageState();
        });
    }

    // 页面状态管理
    setupPageStateManagement() {
        // 保存滚动位置
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                this.saveScrollPosition();
            }, 100);
        });

        // 保存表单数据
        document.addEventListener('input', (e) => {
            if (e.target.matches('input, textarea, select')) {
                this.saveFormData();
            }
        });

        // 页面卸载前保存状态
        window.addEventListener('beforeunload', () => {
            this.savePageState();
        });
    }

    // 导航拦截
    setupNavigationInterception() {
        // 拦截链接点击
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href]');
            
            if (link && this.shouldInterceptNavigation(link)) {
                // 不阻止默认行为，让浏览器正常处理
                // 只是标记导航状态和保存当前状态
                this.navigationState.isNavigating = true;
                this.navigationState.navigationStartTime = Date.now();
                
                // 保存当前页面状态
                this.savePageState();
                
                // 触发导航开始事件
                this.dispatchNavigationEvent('navigationstart', {
                    url: link.href,
                    target: link
                });
            }
        });

        // 拦截表单提交
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.method.toLowerCase() === 'get') {
                this.navigationState.isNavigating = true;
                this.savePageState();
            }
        });
    }

    // 判断是否应该拦截导航
    shouldInterceptNavigation(link) {
        // 跳过外部链接
        if (!link.href.startsWith(window.location.origin)) {
            return false;
        }
        
        // 跳过新窗口链接
        if (link.target === '_blank') {
            return false;
        }
        
        // 跳过下载链接
        if (link.hasAttribute('download')) {
            return false;
        }
        
        // 跳过锚点链接（同页面内）
        const url = new URL(link.href);
        if (url.pathname === window.location.pathname && url.hash) {
            return false;
        }
        
        return true;
    }

    // 保存页面状态
    savePageState() {
        const state = {
            url: window.location.href,
            title: document.title,
            scrollPosition: {
                x: window.pageXOffset,
                y: window.pageYOffset
            },
            timestamp: Date.now(),
            formData: this.getFormData(),
            pageData: this.getPageSpecificData()
        };

        try {
            // 使用 replaceState 更新当前历史记录项
            history.replaceState(state, document.title, window.location.href);
            
            // 同时保存到 sessionStorage 作为备份
            sessionStorage.setItem(`pageState_${window.location.pathname}`, JSON.stringify(state));
        } catch (error) {
            console.warn('保存页面状态失败:', error);
        }
    }

    // 恢复页面状态
    restorePageState(state) {
        if (!state) {
            // 尝试从 sessionStorage 恢复
            try {
                const savedState = sessionStorage.getItem(`pageState_${window.location.pathname}`);
                if (savedState) {
                    state = JSON.parse(savedState);
                }
            } catch (error) {
                console.warn('从 sessionStorage 恢复状态失败:', error);
                return;
            }
        }

        if (state) {
            // 恢复滚动位置
            if (state.scrollPosition) {
                // 延迟恢复，确保页面已渲染
                setTimeout(() => {
                    window.scrollTo(state.scrollPosition.x, state.scrollPosition.y);
                }, 100);
            }

            // 恢复表单数据
            if (state.formData) {
                this.restoreFormData(state.formData);
            }

            // 恢复页面特定数据
            if (state.pageData) {
                this.restorePageSpecificData(state.pageData);
            }
        }
    }

    // 保存滚动位置
    saveScrollPosition() {
        const state = history.state || {};
        state.scrollPosition = {
            x: window.pageXOffset,
            y: window.pageYOffset
        };
        
        try {
            history.replaceState(state, document.title, window.location.href);
        } catch (error) {
            console.warn('保存滚动位置失败:', error);
        }
    }

    // 获取表单数据
    getFormData() {
        const formData = {};
        const forms = document.querySelectorAll('form');
        
        forms.forEach((form, formIndex) => {
            const formElements = form.querySelectorAll('input, textarea, select');
            formElements.forEach((element, elementIndex) => {
                if (element.name || element.id) {
                    const key = element.name || element.id || `form_${formIndex}_element_${elementIndex}`;
                    
                    if (element.type === 'checkbox' || element.type === 'radio') {
                        formData[key] = element.checked;
                    } else {
                        formData[key] = element.value;
                    }
                }
            });
        });
        
        return formData;
    }

    // 恢复表单数据
    restoreFormData(formData) {
        Object.entries(formData).forEach(([key, value]) => {
            const element = document.querySelector(`[name="${key}"], #${key}`);
            if (element) {
                if (element.type === 'checkbox' || element.type === 'radio') {
                    element.checked = value;
                } else {
                    element.value = value;
                }
            }
        });
    }

    // 获取页面特定数据
    getPageSpecificData() {
        const pageData = {};
        
        // 保存展开/折叠状态
        const collapsibles = document.querySelectorAll('[data-bs-toggle="collapse"]');
        collapsibles.forEach((element, index) => {
            const target = document.querySelector(element.getAttribute('data-bs-target'));
            if (target) {
                pageData[`collapse_${index}`] = target.classList.contains('show');
            }
        });
        
        // 保存选项卡状态
        const tabs = document.querySelectorAll('[data-bs-toggle="tab"]');
        tabs.forEach((tab, index) => {
            if (tab.classList.contains('active')) {
                pageData.activeTab = index;
            }
        });
        
        // 保存模态框状态
        const modals = document.querySelectorAll('.modal.show');
        pageData.openModals = Array.from(modals).map(modal => modal.id);
        
        return pageData;
    }

    // 恢复页面特定数据
    restorePageSpecificData(pageData) {
        // 恢复展开/折叠状态
        Object.entries(pageData).forEach(([key, value]) => {
            if (key.startsWith('collapse_')) {
                const index = parseInt(key.split('_')[1]);
                const collapsible = document.querySelectorAll('[data-bs-toggle="collapse"]')[index];
                if (collapsible) {
                    const target = document.querySelector(collapsible.getAttribute('data-bs-target'));
                    if (target && value) {
                        target.classList.add('show');
                    }
                }
            }
        });
        
        // 恢复选项卡状态
        if (pageData.activeTab !== undefined) {
            const tabs = document.querySelectorAll('[data-bs-toggle="tab"]');
            if (tabs[pageData.activeTab]) {
                tabs[pageData.activeTab].click();
            }
        }
    }

    // 获取导航方向
    getNavigationDirection() {
        // 简单的方向检测逻辑
        if (this.navigationState.previousUrl && this.navigationState.currentUrl) {
            // 这里可以实现更复杂的逻辑来检测前进/后退
            return 'unknown';
        }
        return 'initial';
    }

    // 触发导航事件
    dispatchNavigationEvent(type, detail) {
        const event = new CustomEvent(`navigation:${type}`, {
            detail,
            bubbles: true,
            cancelable: true
        });
        
        document.dispatchEvent(event);
    }

    // 程序化导航
    navigateTo(url, options = {}) {
        const {
            replace = false,
            state = null,
            preserveScroll = false
        } = options;

        // 保存当前状态
        if (!replace) {
            this.savePageState();
        }

        // 执行导航
        if (replace) {
            history.replaceState(state, '', url);
        } else {
            history.pushState(state, '', url);
        }

        // 触发 popstate 事件来处理导航
        window.dispatchEvent(new PopStateEvent('popstate', { state }));
    }

    // 获取导航历史
    getNavigationHistory() {
        const history = [];
        let currentState = window.history.state;
        
        // 这里可以实现更复杂的历史记录跟踪
        // 目前只返回当前状态
        if (currentState) {
            history.push(currentState);
        }
        
        return history;
    }

    // 清理资源
    destroy() {
        // 移除事件监听器
        // 这里可以添加清理逻辑
        console.log('🧭 导航管理器已销毁');
    }
}

// 创建全局实例
window.navigationManager = new NavigationManager();

// 便捷方法
window.navigateTo = (url, options) => window.navigationManager.navigateTo(url, options);

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NavigationManager;
}
