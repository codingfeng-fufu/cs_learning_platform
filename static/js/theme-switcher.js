/**
 * 主题切换系统
 * 支持多种主题切换，本地存储用户偏好
 */

class ThemeSwitcher {
    constructor() {
        this.themes = {
            'default': {
                name: '科技蓝',
                icon: '🔵',
                description: '默认的科技感蓝色主题'
            },
            'dark': {
                name: '深色模式',
                icon: '🌙',
                description: '护眼的深色主题'
            },
            'green': {
                name: '护眼绿',
                icon: '🌿',
                description: '舒缓的绿色护眼主题'
            },
            'warm': {
                name: '温暖橙',
                icon: '🔥',
                description: '温暖的橙色主题'
            },
            'purple': {
                name: '优雅紫',
                icon: '💜',
                description: '优雅的紫色主题'
            },
            'pink': {
                name: '可爱粉',
                icon: '🌸',
                description: '可爱的粉色主题'
            },
            'contrast': {
                name: '高对比',
                icon: '⚫',
                description: '高对比度无障碍主题'
            }
        };
        
        // 优先使用用户保存的主题，否则默认使用科技蓝主题
        this.currentTheme = this.getStoredTheme() || 'default';
        this.init();
    }

    init() {
        this.createSwitcher();
        this.applyTheme(this.currentTheme);
        this.bindEvents();
        // 移除自动主题检测，让用户自己选择
    }

    createSwitcher() {
        // 创建主题切换器HTML
        const switcherHTML = `
            <div class="theme-switcher" id="themeSwitcher">
                <button class="theme-switcher-toggle" id="themeSwitcherToggle" title="切换主题">
                    🎨
                </button>
                <div class="theme-options" id="themeOptions">
                    ${Object.entries(this.themes).map(([key, theme]) => `
                        <button class="theme-option ${key === this.currentTheme ? 'active' : ''}"
                                data-theme="${key}"
                                title="${theme.description}">
                            <div class="theme-preview ${key}"></div>
                            <span>${theme.icon} ${theme.name}</span>
                        </button>
                    `).join('')}
                    <hr style="margin: 10px 0; border: none; border-top: 1px solid var(--border-color);">
                    <button class="theme-option" id="resetTheme" title="重置为默认主题">
                        <div class="theme-preview" style="background: linear-gradient(45deg, #ccc, #999);"></div>
                        <span>🔄 重置主题</span>
                    </button>
                </div>
            </div>
        `;

        // 添加到页面
        document.body.insertAdjacentHTML('beforeend', switcherHTML);
    }

    bindEvents() {
        const toggle = document.getElementById('themeSwitcherToggle');
        const options = document.getElementById('themeOptions');
        const switcher = document.getElementById('themeSwitcher');

        // 切换主题选项显示/隐藏
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            options.classList.toggle('show');
        });

        // 点击其他地方关闭主题选项
        document.addEventListener('click', (e) => {
            if (!switcher.contains(e.target)) {
                options.classList.remove('show');
            }
        });

        // 主题选择事件
        options.addEventListener('click', (e) => {
            const themeOption = e.target.closest('.theme-option');
            if (themeOption) {
                // 检查是否是重置按钮
                if (themeOption.id === 'resetTheme') {
                    this.resetTheme();
                } else {
                    const theme = themeOption.dataset.theme;
                    if (theme) {
                        this.switchTheme(theme);
                    }
                }
                options.classList.remove('show');
            }
        });

        // 键盘快捷键支持
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Shift + T 切换主题
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.cycleTheme();
            }
        });

        // 移除系统主题监听，让用户完全控制主题选择
    }

    switchTheme(theme) {
        if (this.themes[theme]) {
            this.currentTheme = theme;
            this.applyTheme(theme);
            this.storeTheme(theme);
            this.updateActiveOption(theme);
            this.showThemeNotification(theme);
        }
    }

    applyTheme(theme) {
        // 移除所有主题类
        document.documentElement.removeAttribute('data-theme');
        
        // 应用新主题
        if (theme !== 'default') {
            document.documentElement.setAttribute('data-theme', theme);
        }

        // 更新meta theme-color
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            const themeColors = {
                'default': '#667eea',
                'dark': '#1a1a2e',
                'green': '#10b981',
                'warm': '#f59e0b',
                'purple': '#8b5cf6',
                'pink': '#ec4899',
                'contrast': '#000000'
            };
            metaThemeColor.setAttribute('content', themeColors[theme] || themeColors.default);
        }

        // 触发主题变化事件
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme, themeName: this.themes[theme].name }
        }));
    }

    updateActiveOption(theme) {
        const options = document.querySelectorAll('.theme-option');
        options.forEach(option => {
            option.classList.toggle('active', option.dataset.theme === theme);
        });
    }

    cycleTheme() {
        const themeKeys = Object.keys(this.themes);
        const currentIndex = themeKeys.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % themeKeys.length;
        const nextTheme = themeKeys[nextIndex];
        this.switchTheme(nextTheme);
    }

    // 移除自动系统主题检测功能

    getStoredTheme() {
        try {
            return localStorage.getItem('preferred-theme');
        } catch (e) {
            console.warn('无法访问localStorage，使用默认主题');
            return null;
        }
    }

    storeTheme(theme) {
        try {
            localStorage.setItem('preferred-theme', theme);
        } catch (e) {
            console.warn('无法保存主题偏好到localStorage');
        }
    }

    showThemeNotification(theme) {
        const themeName = this.themes[theme].name;
        const notification = document.createElement('div');
        notification.className = 'theme-notification';
        notification.innerHTML = `
            <div class="theme-notification-content">
                ${this.themes[theme].icon} 已切换到 ${themeName} 主题
            </div>
        `;
        
        // 添加通知样式
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-card);
            color: var(--text-primary);
            padding: 12px 20px;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-lg);
            z-index: 10001;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            border: 1px solid var(--border-color);
            backdrop-filter: blur(10px);
        `;

        document.body.appendChild(notification);

        // 显示动画
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // 自动隐藏
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 2000);
    }

    // 获取当前主题信息
    getCurrentTheme() {
        return {
            key: this.currentTheme,
            ...this.themes[this.currentTheme]
        };
    }

    // 添加自定义主题
    addCustomTheme(key, themeConfig) {
        this.themes[key] = themeConfig;
        // 重新创建切换器以包含新主题
        const existingSwitcher = document.getElementById('themeSwitcher');
        if (existingSwitcher) {
            existingSwitcher.remove();
            this.createSwitcher();
            this.bindEvents();
        }
    }

    // 移除主题
    removeTheme(key) {
        if (key !== 'default' && this.themes[key]) {
            delete this.themes[key];
            if (this.currentTheme === key) {
                this.switchTheme('default');
            }
        }
    }

    // 重置主题到默认
    resetTheme() {
        try {
            localStorage.removeItem('preferred-theme');
        } catch (e) {
            console.warn('无法清除主题偏好');
        }
        this.switchTheme('default');
        this.showThemeNotification('default');
    }
}

// 页面加载完成后初始化主题切换器
document.addEventListener('DOMContentLoaded', () => {
    window.themeSwitcher = new ThemeSwitcher();
    
    // 为其他脚本提供主题切换API
    window.switchTheme = (theme) => window.themeSwitcher.switchTheme(theme);
    window.getCurrentTheme = () => window.themeSwitcher.getCurrentTheme();
    
    console.log('🎨 主题切换系统已初始化');
});

// 监听主题变化事件的示例
window.addEventListener('themeChanged', (e) => {
    console.log(`主题已切换到: ${e.detail.themeName}`);
    
    // 可以在这里添加主题切换后的额外处理
    // 例如：更新图表颜色、重新渲染某些组件等
});

// 导出ThemeSwitcher类供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeSwitcher;
}
