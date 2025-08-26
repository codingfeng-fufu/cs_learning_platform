"""
额外工具资源 - 更多实用工具和资源
包含更多开发工具、学习资源、效率工具等
"""

ADDITIONAL_TOOLS = [
    # 更多开发工具
    {
        'title': 'WebStorm',
        'short_description': 'JetBrains的JavaScript IDE',
        'description': 'WebStorm是JetBrains开发的专业JavaScript IDE，为现代Web开发提供智能编码辅助。支持JavaScript、TypeScript、React、Vue、Angular等前端技术栈，内置调试器、版本控制、测试工具等功能，是前端开发者的专业选择。',
        'url': 'https://www.jetbrains.com/webstorm/',
        'category_slug': 'dev-tools',
        'resource_type': 'tool',
        'is_free': False,
        'price_info': '免费试用，$59/年',
        'features': ['智能代码补全', 'JavaScript调试', '版本控制集成', '测试运行器', '重构工具', 'Live Edit'],
        'pros_cons': {
            'pros': ['专业的前端开发环境', '强大的调试功能', '优秀的代码分析', '丰富的插件生态'],
            'cons': ['需要付费', '资源占用较高', '启动速度较慢']
        },
        'platform_support': ['Windows', 'macOS', 'Linux'],
        'usage_tips': '充分利用Live Edit功能进行实时预览，使用内置的调试器调试复杂的JavaScript应用。',
        'tags': ['JavaScript', 'IDE', 'JetBrains', '前端开发']
    },
    {
        'title': 'Insomnia',
        'short_description': 'API测试客户端',
        'description': 'Insomnia是一款现代化的API测试客户端，提供直观的界面来测试REST、GraphQL和gRPC API。支持环境变量、代码生成、团队协作等功能，是Postman的优秀替代品。',
        'url': 'https://insomnia.rest/',
        'category_slug': 'dev-tools',
        'resource_type': 'tool',
        'is_free': True,
        'price_info': '免费版，Plus版$5/月',
        'features': ['REST API测试', 'GraphQL支持', '环境管理', '代码生成', '团队协作', '插件系统'],
        'pros_cons': {
            'pros': ['界面简洁美观', '支持多种API类型', '免费版功能丰富', '性能优秀'],
            'cons': ['功能相对简单', '插件生态较小', '高级功能需付费']
        },
        'platform_support': ['Windows', 'macOS', 'Linux'],
        'usage_tips': '使用环境变量管理不同的API端点，利用代码生成功能快速生成客户端代码。',
        'tags': ['API测试', 'REST', 'GraphQL', '开发工具']
    },
    {
        'title': 'TablePlus',
        'short_description': '现代数据库管理工具',
        'description': 'TablePlus是一款现代化的数据库管理工具，支持多种数据库类型包括MySQL、PostgreSQL、SQLite、Redis等。提供直观的界面、强大的查询编辑器和数据可视化功能。',
        'url': 'https://tableplus.com/',
        'category_slug': 'dev-tools',
        'resource_type': 'tool',
        'is_free': False,
        'price_info': '免费试用，$59买断',
        'features': ['多数据库支持', '智能查询编辑器', '数据可视化', '安全连接', '导入导出', '团队协作'],
        'pros_cons': {
            'pros': ['界面美观现代', '支持多种数据库', '性能优秀', '安全性高'],
            'cons': ['需要付费', '免费版功能限制', '学习成本一般']
        },
        'platform_support': ['Windows', 'macOS', 'Linux', 'iOS'],
        'usage_tips': '使用SSH隧道连接远程数据库，利用查询历史功能管理常用SQL语句。',
        'tags': ['数据库', 'MySQL', 'PostgreSQL', '管理工具']
    },
    {
        'title': 'Sourcetree',
        'short_description': 'Git图形化客户端',
        'description': 'Sourcetree是Atlassian开发的免费Git图形化客户端，提供直观的界面来管理Git仓库。支持Git Flow、子模块、大文件等高级功能，适合不熟悉命令行的开发者使用。',
        'url': 'https://www.sourcetreeapp.com/',
        'category_slug': 'dev-tools',
        'resource_type': 'tool',
        'is_free': True,
        'features': ['Git图形界面', 'Git Flow支持', '分支管理', '冲突解决', '子模块支持', '远程仓库管理'],
        'pros_cons': {
            'pros': ['完全免费', '界面直观', '功能全面', 'Atlassian生态集成'],
            'cons': ['性能一般', '占用资源较多', '复杂操作仍需命令行']
        },
        'platform_support': ['Windows', 'macOS'],
        'usage_tips': '使用Git Flow功能管理分支策略，利用可视化界面理解复杂的合并历史。',
        'tags': ['Git', '版本控制', '图形界面', 'Atlassian']
    },

    # 更多AI工具
    {
        'title': 'Stable Diffusion',
        'short_description': '开源AI图像生成',
        'description': 'Stable Diffusion是一个开源的AI图像生成模型，能够根据文本描述生成高质量图像。与商业产品不同，它可以本地运行，提供更多的控制和自定义选项，是AI艺术创作的强大工具。',
        'url': 'https://stability.ai/stable-diffusion',
        'category_slug': 'ai-tools',
        'resource_type': 'ai',
        'is_free': True,
        'features': ['文本到图像生成', '图像到图像转换', '本地运行', '开源模型', '自定义训练', '多种界面'],
        'pros_cons': {
            'pros': ['完全开源免费', '可本地运行', '高度可定制', '社区活跃'],
            'cons': ['需要技术知识', '硬件要求高', '设置复杂']
        },
        'platform_support': ['Windows', 'macOS', 'Linux', 'Web'],
        'usage_tips': '使用详细的提示词获得更好的生成效果，调整采样步数和CFG值优化图像质量。',
        'tags': ['AI绘画', '图像生成', '开源', '机器学习']
    },
    {
        'title': 'Grammarly',
        'short_description': 'AI写作助手',
        'description': 'Grammarly是一款AI驱动的写作助手，能够检查语法、拼写、标点符号错误，并提供写作风格建议。支持多种平台和应用，是英文写作的必备工具。',
        'url': 'https://www.grammarly.com/',
        'category_slug': 'ai-tools',
        'resource_type': 'ai',
        'is_free': True,
        'price_info': '免费版，Premium版$12/月',
        'features': ['语法检查', '拼写纠正', '写作建议', '抄袭检测', '语调分析', '多平台支持'],
        'pros_cons': {
            'pros': ['准确率高', '多平台集成', '实时检查', '写作建议有用'],
            'cons': ['主要支持英文', '高级功能需付费', '有时建议过于保守']
        },
        'platform_support': ['Web', 'Windows', 'macOS', 'Browser Extension', 'Mobile'],
        'usage_tips': '安装浏览器插件在各种网站使用，设置写作目标获得更精准的建议。',
        'tags': ['写作助手', '语法检查', '英文写作', 'AI']
    },

    # 更多设计工具
    {
        'title': 'Framer',
        'short_description': '交互设计和原型工具',
        'description': 'Framer是一款强大的交互设计和原型制作工具，支持高保真原型、动画设计和代码组件。特别适合设计复杂的交互效果和动画，是现代产品设计师的专业选择。',
        'url': 'https://www.framer.com/',
        'category_slug': 'design-tools',
        'resource_type': 'design',
        'is_free': True,
        'price_info': '免费版，Pro版$15/月',
        'features': ['高保真原型', '交互动画', '代码组件', '实时协作', '响应式设计', '发布部署'],
        'pros_cons': {
            'pros': ['交互效果强大', '动画制作专业', '代码集成好', '学习资源丰富'],
            'cons': ['学习曲线陡峭', '性能要求高', '复杂项目需付费']
        },
        'platform_support': ['Web', 'macOS'],
        'usage_tips': '从简单的原型开始学习，利用组件库提高设计效率，使用Smart Animate创建流畅动画。',
        'tags': ['原型设计', '交互设计', '动画', 'UI设计']
    },
    {
        'title': 'Principle',
        'short_description': 'Mac动画设计工具',
        'description': 'Principle是Mac平台上的专业动画设计工具，专注于创建流畅的界面动画和交互效果。提供时间轴编辑器和直观的动画控制，是移动应用和Web界面动画设计的利器。',
        'url': 'https://principleformac.com/',
        'category_slug': 'design-tools',
        'resource_type': 'design',
        'is_free': False,
        'price_info': '$129买断',
        'features': ['时间轴动画', '交互原型', '实时预览', '导出视频', '组件系统', '响应式设计'],
        'pros_cons': {
            'pros': ['动画制作专业', '操作直观', '预览效果好', '导出格式多'],
            'cons': ['仅支持Mac', '需要付费', '功能相对单一']
        },
        'platform_support': ['macOS'],
        'usage_tips': '使用时间轴精确控制动画时机，利用驱动器创建复杂的交互逻辑。',
        'tags': ['动画设计', 'Mac', '交互原型', 'UI动画']
    },
    {
        'title': 'Iconify',
        'short_description': '开源图标库',
        'description': 'Iconify是一个庞大的开源图标库，包含超过100,000个图标，来自各种流行的图标集。提供统一的API和多种使用方式，支持SVG、Web字体等格式，是设计师和开发者的图标资源宝库。',
        'url': 'https://iconify.design/',
        'category_slug': 'design-tools',
        'resource_type': 'website',
        'is_free': True,
        'features': ['海量图标', '统一API', '多种格式', '搜索功能', '自定义颜色', '框架集成'],
        'pros_cons': {
            'pros': ['图标数量庞大', '完全免费', '使用方便', '质量统一'],
            'cons': ['需要网络连接', '部分图标质量一般', '搜索有时不准确']
        },
        'platform_support': ['Web', 'API'],
        'usage_tips': '使用关键词搜索图标，利用API在项目中动态加载图标，自定义颜色和大小。',
        'tags': ['图标', '开源', 'SVG', '设计资源']
    },

    # 更多学术工具
    {
        'title': 'Typora',
        'short_description': '所见即所得Markdown编辑器',
        'description': 'Typora是一款优雅的Markdown编辑器，提供所见即所得的编辑体验。支持数学公式、图表、代码高亮等功能，是学术写作和技术文档编写的理想选择。',
        'url': 'https://typora.io/',
        'category_slug': 'academic-tools',
        'resource_type': 'tool',
        'is_free': False,
        'price_info': '$14.99买断',
        'features': ['所见即所得', '数学公式', '图表支持', '代码高亮', '主题定制', '导出多格式'],
        'pros_cons': {
            'pros': ['编辑体验优秀', '功能全面', '界面简洁', '性能好'],
            'cons': ['需要付费', '功能更新较慢', '插件生态较小']
        },
        'platform_support': ['Windows', 'macOS', 'Linux'],
        'usage_tips': '使用数学模式编写公式，自定义CSS样式美化文档，利用大纲视图管理长文档。',
        'tags': ['Markdown', '编辑器', '学术写作', '文档']
    },
    {
        'title': 'Zotero',
        'short_description': '开源文献管理工具',
        'description': 'Zotero是一款免费开源的文献管理工具，帮助研究者收集、整理、引用和分享研究资源。支持自动抓取文献信息、PDF注释、协作共享等功能，是学术研究的必备工具。',
        'url': 'https://www.zotero.org/',
        'category_slug': 'academic-tools',
        'resource_type': 'tool',
        'is_free': True,
        'features': ['文献收集', '自动引用', 'PDF注释', '团队协作', '浏览器插件', '多格式导出'],
        'pros_cons': {
            'pros': ['完全免费', '开源软件', '功能强大', '社区支持好'],
            'cons': ['界面较老', '同步空间有限', '学习成本一般']
        },
        'platform_support': ['Windows', 'macOS', 'Linux', 'Web'],
        'usage_tips': '安装浏览器插件一键保存文献，使用标签和文件夹组织文献，设置引用格式自动生成参考文献。',
        'tags': ['文献管理', '学术研究', '开源', '引用']
    },

    # 更多在线课程和学习资源
    {
        'title': 'freeCodeCamp',
        'short_description': '免费编程学习平台',
        'description': 'freeCodeCamp是一个完全免费的编程学习平台，提供全栈Web开发、数据科学、机器学习等课程。通过项目实践的方式学习，完成课程可获得认证，是自学编程的最佳选择之一。',
        'url': 'https://www.freecodecamp.org/',
        'category_slug': 'online-courses',
        'resource_type': 'course',
        'is_free': True,
        'features': ['完全免费', '项目实践', '认证证书', '社区支持', '多语言支持', '移动友好'],
        'pros_cons': {
            'pros': ['完全免费', '内容质量高', '实践性强', '社区活跃'],
            'cons': ['进度较慢', '缺乏个性化', '部分内容较基础']
        },
        'platform_support': ['Web', 'Mobile App'],
        'usage_tips': '按照课程顺序学习，完成所有项目获得认证，积极参与社区讨论。',
        'tags': ['编程学习', '免费', 'Web开发', '认证']
    },
    {
        'title': 'Codecademy',
        'short_description': '交互式编程学习',
        'description': 'Codecademy是一个交互式编程学习平台，提供Python、JavaScript、SQL等多种编程语言的课程。通过在线编码练习和项目实战，让学习者在实践中掌握编程技能。',
        'url': 'https://www.codecademy.com/',
        'category_slug': 'online-courses',
        'resource_type': 'course',
        'is_free': True,
        'price_info': '免费版，Pro版$15.99/月',
        'features': ['交互式学习', '即时反馈', '项目实战', '学习路径', '技能评估', '证书认证'],
        'pros_cons': {
            'pros': ['学习体验好', '即时反馈', '内容结构化', '适合初学者'],
            'cons': ['高级内容需付费', '缺乏深度', '项目相对简单']
        },
        'platform_support': ['Web', 'Mobile App'],
        'usage_tips': '选择适合的学习路径，完成所有练习和项目，利用社区功能寻求帮助。',
        'tags': ['编程学习', '交互式', '在线教育', '初学者']
    },

    # 更多实用网站
    {
        'title': 'Excalidraw',
        'short_description': '手绘风格图表工具',
        'description': 'Excalidraw是一个开源的手绘风格图表制作工具，支持实时协作。界面简洁直观，适合制作流程图、架构图、思维导图等，特别适合快速原型设计和头脑风暴。',
        'url': 'https://excalidraw.com/',
        'category_slug': 'useful-websites',
        'resource_type': 'website',
        'is_free': True,
        'features': ['手绘风格', '实时协作', '无需注册', '导出多格式', '开源免费', '响应式设计'],
        'pros_cons': {
            'pros': ['完全免费', '使用简单', '协作方便', '风格独特'],
            'cons': ['功能相对简单', '样式选择有限', '不适合复杂图表']
        },
        'platform_support': ['Web'],
        'usage_tips': '使用快捷键提高绘制效率，利用协作功能进行团队讨论，导出PNG或SVG格式保存。',
        'tags': ['图表制作', '手绘风格', '协作', '开源']
    },
    {
        'title': 'Shields.io',
        'short_description': '项目徽章生成器',
        'description': 'Shields.io是一个项目徽章生成服务，为开源项目提供各种状态徽章，如构建状态、代码覆盖率、版本信息等。支持多种服务集成，是GitHub项目README美化的必备工具。',
        'url': 'https://shields.io/',
        'category_slug': 'useful-websites',
        'resource_type': 'website',
        'is_free': True,
        'features': ['徽章生成', '多服务集成', '自定义样式', '实时更新', 'API支持', '开源免费'],
        'pros_cons': {
            'pros': ['完全免费', '集成服务多', '自定义程度高', '更新及时'],
            'cons': ['主要面向开发者', '设计选择有限', '依赖第三方服务']
        },
        'platform_support': ['Web', 'API'],
        'usage_tips': '选择合适的徽章类型，自定义颜色和文字，将生成的Markdown代码添加到README中。',
        'tags': ['徽章', 'GitHub', '开源项目', '状态显示']
    },
    {
        'title': 'Carbon',
        'short_description': '代码截图美化工具',
        'description': 'Carbon是一个在线代码截图美化工具，能够将代码转换为美观的图片。支持多种编程语言语法高亮、主题选择、窗口样式定制等功能，适合制作技术分享和教程。',
        'url': 'https://carbon.now.sh/',
        'category_slug': 'useful-websites',
        'resource_type': 'website',
        'is_free': True,
        'features': ['代码美化', '语法高亮', '主题选择', '窗口样式', '导出图片', '分享链接'],
        'pros_cons': {
            'pros': ['完全免费', '效果美观', '使用简单', '主题丰富'],
            'cons': ['功能单一', '不支持动画', '导出格式有限']
        },
        'platform_support': ['Web'],
        'usage_tips': '选择合适的主题和字体，调整窗口样式，使用快捷键快速操作。',
        'tags': ['代码截图', '美化', '分享', '教程制作']
    }
]
