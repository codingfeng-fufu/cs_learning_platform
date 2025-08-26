"""
扩展资源数据 - 50个高质量学习资源
包含学习视频、笔记工具、代码编辑器、技术博客等
"""

EXTENDED_RESOURCES = [
    # 更多开发工具
    {
        'title': 'JetBrains IntelliJ IDEA',
        'short_description': '强大的Java IDE',
        'description': 'IntelliJ IDEA是JetBrains开发的Java集成开发环境，提供智能代码补全、重构、调试等功能，是Java开发者的首选IDE。',
        'url': 'https://www.jetbrains.com/idea/',
        'category_slug': 'dev-tools',
        'resource_type': 'tool',
        'is_free': False,
        'price_info': '免费社区版，专业版$149/年',
        'features': ['智能代码补全', '强大重构', '调试工具', '版本控制', '插件生态'],
        'platform_support': ['Windows', 'macOS', 'Linux'],
        'tags': ['Java', 'IDE', 'JetBrains', '开发工具']
    },
    {
        'title': 'Sublime Text',
        'short_description': '轻量级代码编辑器',
        'description': 'Sublime Text是一款轻量级但功能强大的代码编辑器，以其快速响应和丰富的插件系统而闻名。',
        'url': 'https://www.sublimetext.com/',
        'category_slug': 'dev-tools',
        'resource_type': 'tool',
        'is_free': False,
        'price_info': '免费试用，$99买断',
        'features': ['快速响应', '多选编辑', '命令面板', '插件系统', '跨平台'],
        'platform_support': ['Windows', 'macOS', 'Linux'],
        'tags': ['代码编辑器', '轻量级', '插件']
    },
    {
        'title': 'Postman',
        'short_description': 'API开发测试工具',
        'description': 'Postman是一款强大的API开发和测试工具，支持REST、GraphQL等多种API类型，提供完整的API开发生命周期管理。',
        'url': 'https://www.postman.com/',
        'category_slug': 'dev-tools',
        'resource_type': 'tool',
        'is_free': True,
        'price_info': '免费版，团队版$12/月',
        'features': ['API测试', '自动化测试', '团队协作', '文档生成', 'Mock服务'],
        'platform_support': ['Windows', 'macOS', 'Linux', 'Web'],
        'tags': ['API', '测试', '开发工具']
    },
    {
        'title': 'Docker',
        'short_description': '容器化平台',
        'description': 'Docker是一个开源的容器化平台，可以将应用程序及其依赖项打包到轻量级、可移植的容器中。',
        'url': 'https://www.docker.com/',
        'category_slug': 'dev-tools',
        'resource_type': 'tool',
        'is_free': True,
        'price_info': '个人免费，企业版付费',
        'features': ['容器化', '微服务', '持续集成', '云部署', '资源隔离'],
        'platform_support': ['Windows', 'macOS', 'Linux'],
        'tags': ['容器', 'DevOps', '部署']
    },
    {
        'title': 'Vim',
        'short_description': '经典文本编辑器',
        'description': 'Vim是一个高度可配置的文本编辑器，以其强大的编辑功能和键盘快捷键而闻名，是许多程序员的最爱。',
        'url': 'https://www.vim.org/',
        'category_slug': 'dev-tools',
        'resource_type': 'tool',
        'is_free': True,
        'features': ['键盘操作', '高度可配置', '插件系统', '语法高亮', '多窗口'],
        'platform_support': ['Windows', 'macOS', 'Linux'],
        'tags': ['文本编辑器', '命令行', '开源']
    },

    # 更多AI工具
    {
        'title': 'GitHub Copilot',
        'short_description': 'AI代码助手',
        'description': 'GitHub Copilot是GitHub与OpenAI合作开发的革命性AI编程助手，基于数十亿行开源代码训练。它能够实时理解你的代码上下文，提供智能的代码补全建议，甚至能够根据注释生成完整的函数。Copilot不仅能加速编码过程，还能帮助学习新的编程模式和最佳实践，是现代开发者的得力助手。',
        'url': 'https://github.com/features/copilot',
        'category_slug': 'ai-tools',
        'resource_type': 'ai',
        'is_free': False,
        'price_info': '$10/月，学生和开源维护者免费',
        'features': ['智能代码补全', '函数自动生成', '注释转代码', '多语言支持', '上下文感知', 'IDE深度集成'],
        'pros_cons': {
            'pros': ['代码生成质量高', '支持多种编程语言', '与IDE无缝集成', '学生免费', '持续学习改进'],
            'cons': ['需要付费订阅', '可能生成有版权争议的代码', '有时建议不够准确']
        },
        'platform_support': ['VS Code', 'JetBrains IDEs', 'Neovim', 'Visual Studio'],
        'usage_tips': '写清晰的注释能获得更好的代码生成效果。使用Tab键接受建议，Ctrl+]查看更多选项。定期查看生成的代码确保质量。',
        'tags': ['AI', '代码生成', 'GitHub', 'OpenAI', '编程助手']
    },
    {
        'title': 'Midjourney',
        'short_description': 'AI图像生成工具',
        'description': 'Midjourney是一款强大的AI图像生成工具，能够根据文本描述生成高质量的艺术作品和图像。',
        'url': 'https://www.midjourney.com/',
        'category_slug': 'ai-tools',
        'resource_type': 'ai',
        'is_free': False,
        'price_info': '$10/月起',
        'features': ['文本到图像', '艺术风格', '高分辨率', '商业使用', '社区分享'],
        'platform_support': ['Discord', 'Web'],
        'tags': ['AI绘画', '图像生成', '艺术']
    },
    {
        'title': 'Perplexity AI',
        'short_description': 'AI搜索引擎',
        'description': 'Perplexity AI是一个AI驱动的搜索引擎，能够提供准确的答案并引用可靠的来源。',
        'url': 'https://www.perplexity.ai/',
        'category_slug': 'ai-tools',
        'resource_type': 'ai',
        'is_free': True,
        'price_info': '免费版，Pro版$20/月',
        'features': ['AI搜索', '来源引用', '实时信息', '多语言', '对话式查询'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['AI搜索', '信息检索', '研究']
    },

    # 更多设计工具
    {
        'title': 'Adobe XD',
        'short_description': 'UI/UX设计工具',
        'description': 'Adobe XD是Adobe推出的UI/UX设计和原型制作工具，提供完整的设计到开发工作流程。',
        'url': 'https://www.adobe.com/products/xd.html',
        'category_slug': 'design-tools',
        'resource_type': 'design',
        'is_free': True,
        'price_info': '免费版，付费版$9.99/月',
        'features': ['UI设计', '原型制作', '协作', '设计系统', '开发者交接'],
        'platform_support': ['Windows', 'macOS'],
        'tags': ['UI设计', 'UX设计', 'Adobe', '原型']
    },
    {
        'title': 'Sketch',
        'short_description': 'Mac专用设计工具',
        'description': 'Sketch是Mac平台上的专业UI设计工具，以其简洁的界面和强大的矢量编辑功能而受到设计师喜爱。',
        'url': 'https://www.sketch.com/',
        'category_slug': 'design-tools',
        'resource_type': 'design',
        'is_free': False,
        'price_info': '$9/月',
        'features': ['矢量设计', '符号系统', '插件生态', '协作', '开发者工具'],
        'platform_support': ['macOS'],
        'tags': ['UI设计', 'Mac', '矢量', '设计']
    },
    {
        'title': 'Canva',
        'short_description': '在线设计平台',
        'description': 'Canva是一个易于使用的在线设计平台，提供丰富的模板和设计元素，适合非专业设计师使用。',
        'url': 'https://www.canva.com/',
        'category_slug': 'design-tools',
        'resource_type': 'design',
        'is_free': True,
        'price_info': '免费版，Pro版$12.99/月',
        'features': ['模板库', '拖拽设计', '团队协作', '品牌套件', '多格式导出'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['在线设计', '模板', '易用']
    },

    # 学术工具
    {
        'title': 'Zotero',
        'short_description': '文献管理工具',
        'description': 'Zotero是一款免费的文献管理工具，帮助研究者收集、整理、引用和分享研究资源。',
        'url': 'https://www.zotero.org/',
        'category_slug': 'academic-tools',
        'resource_type': 'tool',
        'is_free': True,
        'features': ['文献收集', '自动引用', '笔记管理', '团队协作', '浏览器插件'],
        'platform_support': ['Windows', 'macOS', 'Linux', 'Web'],
        'tags': ['文献管理', '学术研究', '引用']
    },
    {
        'title': 'Mendeley',
        'short_description': '学术社交网络',
        'description': 'Mendeley是一个学术社交网络和文献管理工具，结合了文献管理和学术社交功能。',
        'url': 'https://www.mendeley.com/',
        'category_slug': 'academic-tools',
        'resource_type': 'tool',
        'is_free': True,
        'price_info': '免费版，付费版有更多存储',
        'features': ['文献管理', '学术社交', 'PDF注释', '引用生成', '研究发现'],
        'platform_support': ['Windows', 'macOS', 'Linux', 'Web', 'Mobile'],
        'tags': ['文献管理', '学术社交', 'PDF']
    },
    {
        'title': 'Obsidian',
        'short_description': '知识图谱笔记',
        'description': 'Obsidian是一款基于链接的笔记应用，帮助用户构建个人知识图谱，支持双向链接和图谱可视化。',
        'url': 'https://obsidian.md/',
        'category_slug': 'academic-tools',
        'resource_type': 'tool',
        'is_free': True,
        'price_info': '个人免费，商业版$50/年',
        'features': ['双向链接', '知识图谱', 'Markdown', '插件系统', '本地存储'],
        'platform_support': ['Windows', 'macOS', 'Linux', 'Mobile'],
        'tags': ['笔记', '知识管理', '图谱', 'Markdown']
    },

    # 在线课程平台
    {
        'title': 'Coursera',
        'short_description': '在线课程平台',
        'description': 'Coursera是全球领先的在线学习平台，与顶尖大学和公司合作提供高质量的课程和学位项目。',
        'url': 'https://www.coursera.org/',
        'category_slug': 'online-courses',
        'resource_type': 'course',
        'is_free': True,
        'price_info': '免费旁听，证书$39-79/月',
        'features': ['大学课程', '专业证书', '学位项目', '实践项目', '同行评议'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['在线教育', '大学课程', '证书']
    },
    {
        'title': 'edX',
        'short_description': '开放式在线课程',
        'description': 'edX是由哈佛大学和MIT创立的开放式在线课程平台，提供来自世界顶尖大学的免费课程。',
        'url': 'https://www.edx.org/',
        'category_slug': 'online-courses',
        'resource_type': 'course',
        'is_free': True,
        'price_info': '免费学习，证书$50-300',
        'features': ['顶尖大学', '免费课程', '微硕士', '专业教育', '自主学习'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['在线教育', 'MIT', '哈佛', '免费']
    },
    {
        'title': 'Udemy',
        'short_description': '技能学习平台',
        'description': 'Udemy是一个全球性的学习平台，提供各种技能课程，从编程到设计，从商业到个人发展。',
        'url': 'https://www.udemy.com/',
        'category_slug': 'online-courses',
        'resource_type': 'course',
        'is_free': False,
        'price_info': '课程$10-200，经常打折',
        'features': ['实用技能', '终身访问', '证书', '移动学习', '多语言'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['技能学习', '实用课程', '编程']
    },
    {
        'title': 'Khan Academy',
        'short_description': '免费教育平台',
        'description': 'Khan Academy是一个非营利性的免费在线教育平台，提供从基础数学到高级编程的各种课程。',
        'url': 'https://www.khanacademy.org/',
        'category_slug': 'online-courses',
        'resource_type': 'course',
        'is_free': True,
        'features': ['完全免费', '个性化学习', '练习题', '进度跟踪', '多语言'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['免费教育', '数学', '编程', '基础教育']
    },

    # 技术文档和学习资源
    {
        'title': 'MDN Web Docs',
        'short_description': 'Web开发文档',
        'description': 'MDN Web Docs是Mozilla维护的Web开发文档，是学习HTML、CSS、JavaScript的权威资源。',
        'url': 'https://developer.mozilla.org/',
        'category_slug': 'documentation',
        'resource_type': 'documentation',
        'is_free': True,
        'features': ['权威文档', '示例代码', '浏览器兼容性', '教程', '参考手册'],
        'platform_support': ['Web'],
        'tags': ['Web开发', 'JavaScript', 'HTML', 'CSS', 'Mozilla']
    },
    {
        'title': 'Stack Overflow',
        'short_description': '程序员问答社区',
        'description': 'Stack Overflow是全球最大的程序员问答社区，几乎所有编程问题都能在这里找到答案。',
        'url': 'https://stackoverflow.com/',
        'category_slug': 'documentation',
        'resource_type': 'website',
        'is_free': True,
        'features': ['问答社区', '代码示例', '专家解答', '标签系统', '声誉系统'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['问答', '编程', '社区', '调试']
    },
    {
        'title': 'W3Schools',
        'short_description': 'Web技术教程',
        'description': 'W3Schools提供全面的Web开发教程，包括HTML、CSS、JavaScript、Python等多种技术。',
        'url': 'https://www.w3schools.com/',
        'category_slug': 'documentation',
        'resource_type': 'documentation',
        'is_free': True,
        'features': ['在线教程', '代码示例', '在线编辑器', '练习题', '证书'],
        'platform_support': ['Web'],
        'tags': ['Web教程', 'HTML', 'CSS', 'JavaScript', '初学者']
    },

    # 开源项目和代码库
    {
        'title': 'GitLab',
        'short_description': 'DevOps平台',
        'description': 'GitLab是一个完整的DevOps平台，提供代码托管、CI/CD、项目管理等功能。',
        'url': 'https://gitlab.com/',
        'category_slug': 'open-source',
        'resource_type': 'tool',
        'is_free': True,
        'price_info': '免费版，付费版$4/月起',
        'features': ['Git托管', 'CI/CD', '项目管理', '安全扫描', '容器注册'],
        'platform_support': ['Web', 'Self-hosted'],
        'tags': ['Git', 'DevOps', 'CI/CD', '项目管理']
    },
    {
        'title': 'Awesome Lists',
        'short_description': '精选资源列表',
        'description': 'Awesome Lists是GitHub上的精选资源列表集合，涵盖各种技术领域的优质资源。',
        'url': 'https://github.com/sindresorhus/awesome',
        'category_slug': 'open-source',
        'resource_type': 'github',
        'is_free': True,
        'features': ['精选资源', '分类整理', '社区维护', '持续更新', '多领域覆盖'],
        'platform_support': ['Web'],
        'tags': ['资源列表', '开源', '精选', '学习资源']
    },

    # 学习视频和教程
    {
        'title': 'YouTube - 编程教学频道',
        'short_description': '优质编程教学视频',
        'description': 'YouTube上有众多优质的编程教学频道，如Traversy Media、The Net Ninja、freeCodeCamp等。',
        'url': 'https://www.youtube.com/',
        'category_slug': 'online-courses',
        'resource_type': 'video',
        'is_free': True,
        'features': ['免费视频', '多语言', '实时更新', '社区互动', '播放列表'],
        'platform_support': ['Web', 'Mobile App', 'TV'],
        'tags': ['视频教程', '编程', '免费', '多样化']
    },
    {
        'title': 'Bilibili - 技术区',
        'short_description': '中文技术学习视频',
        'description': 'Bilibili技术区有大量优质的中文编程和技术教学视频，适合中文用户学习。',
        'url': 'https://www.bilibili.com/',
        'category_slug': 'online-courses',
        'resource_type': 'video',
        'is_free': True,
        'features': ['中文内容', '弹幕互动', '系列教程', '实战项目', '技术分享'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['中文视频', '技术教程', 'B站', '编程']
    },
    {
        'title': 'Pluralsight',
        'short_description': '技术技能学习平台',
        'description': 'Pluralsight是专注于技术技能的在线学习平台，提供高质量的编程、云计算、数据科学等课程。',
        'url': 'https://www.pluralsight.com/',
        'category_slug': 'online-courses',
        'resource_type': 'course',
        'is_free': False,
        'price_info': '$29/月，免费试用',
        'features': ['技术专精', '技能评估', '学习路径', '实践练习', '证书'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['技术学习', '编程', '云计算', '付费']
    },

    # 实用网站和工具
    {
        'title': 'CodePen',
        'short_description': '前端代码分享平台',
        'description': 'CodePen是一个前端代码分享和演示平台，开发者可以在线编写和分享HTML、CSS、JavaScript代码。',
        'url': 'https://codepen.io/',
        'category_slug': 'useful-websites',
        'resource_type': 'website',
        'is_free': True,
        'price_info': '免费版，Pro版$8/月',
        'features': ['在线编辑', '实时预览', '代码分享', '社区', '模板库'],
        'platform_support': ['Web'],
        'tags': ['前端', '代码分享', '在线编辑', 'HTML', 'CSS', 'JavaScript']
    },
    {
        'title': 'JSFiddle',
        'short_description': '在线代码编辑器',
        'description': 'JSFiddle是一个在线的HTML、CSS、JavaScript代码编辑和测试工具。',
        'url': 'https://jsfiddle.net/',
        'category_slug': 'useful-websites',
        'resource_type': 'website',
        'is_free': True,
        'features': ['在线编辑', '实时预览', '代码分享', '库支持', '协作'],
        'platform_support': ['Web'],
        'tags': ['在线编辑', 'JavaScript', '前端', '测试']
    },
    {
        'title': 'Repl.it',
        'short_description': '在线编程环境',
        'description': 'Repl.it是一个在线编程环境，支持50+种编程语言，可以在浏览器中直接编写和运行代码。',
        'url': 'https://replit.com/',
        'category_slug': 'useful-websites',
        'resource_type': 'website',
        'is_free': True,
        'price_info': '免费版，付费版$7/月',
        'features': ['多语言支持', '在线运行', '协作编程', '版本控制', '部署'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['在线编程', '多语言', '协作', '云IDE']
    },
    {
        'title': 'LeetCode',
        'short_description': '算法练习平台',
        'description': 'LeetCode是全球知名的算法和数据结构练习平台，提供大量编程题目，是技术面试准备的首选。',
        'url': 'https://leetcode.com/',
        'category_slug': 'useful-websites',
        'resource_type': 'website',
        'is_free': True,
        'price_info': '免费版，Premium $35/月',
        'features': ['算法题库', '在线判题', '面试准备', '竞赛', '讨论区'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['算法', '数据结构', '面试', '编程题']
    },
    {
        'title': 'HackerRank',
        'short_description': '编程技能评估平台',
        'description': 'HackerRank是一个编程技能评估和练习平台，提供各种编程挑战和技能认证。',
        'url': 'https://www.hackerrank.com/',
        'category_slug': 'useful-websites',
        'resource_type': 'website',
        'is_free': True,
        'features': ['编程挑战', '技能认证', '竞赛', '招聘', '学习路径'],
        'platform_support': ['Web'],
        'tags': ['编程挑战', '技能评估', '认证', '竞赛']
    },

    # 技术博客和资讯
    {
        'title': '阮一峰的网络日志',
        'short_description': '知名技术博客',
        'description': '阮一峰老师的技术博客，内容涵盖前端技术、编程思想、技术趋势等，文章质量很高。',
        'url': 'https://www.ruanyifeng.com/blog/',
        'category_slug': 'useful-websites',
        'resource_type': 'article',
        'is_free': True,
        'features': ['技术文章', '前端技术', '编程思想', '定期更新', '中文内容'],
        'platform_support': ['Web'],
        'tags': ['技术博客', '前端', '阮一峰', '中文', '编程']
    },
    {
        'title': 'Dev.to',
        'short_description': '开发者社区',
        'description': 'Dev.to是一个开发者社区平台，开发者可以在这里分享技术文章、经验和见解。',
        'url': 'https://dev.to/',
        'category_slug': 'useful-websites',
        'resource_type': 'article',
        'is_free': True,
        'features': ['技术文章', '开发者社区', '经验分享', '标签系统', '互动讨论'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['开发者社区', '技术文章', '经验分享', '编程']
    },
    {
        'title': 'Medium - Programming',
        'short_description': '编程技术文章平台',
        'description': 'Medium上有大量高质量的编程和技术文章，涵盖各种技术领域和最新趋势。',
        'url': 'https://medium.com/topic/programming',
        'category_slug': 'useful-websites',
        'resource_type': 'article',
        'is_free': False,
        'price_info': '部分免费，会员$5/月',
        'features': ['高质量文章', '技术趋势', '专家见解', '多样化内容', '社区互动'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['技术文章', 'Medium', '编程', '趋势']
    },
    {
        'title': 'Hacker News',
        'short_description': '技术新闻聚合',
        'description': 'Hacker News是Y Combinator运营的技术新闻聚合网站，汇集最新的技术资讯和讨论。',
        'url': 'https://news.ycombinator.com/',
        'category_slug': 'useful-websites',
        'resource_type': 'website',
        'is_free': True,
        'features': ['技术新闻', '社区讨论', '创业资讯', '开源项目', '技术趋势'],
        'platform_support': ['Web'],
        'tags': ['技术新闻', '创业', 'Y Combinator', '讨论']
    },

    # 更多笔记和知识管理工具
    {
        'title': 'Roam Research',
        'short_description': '网络化思维笔记',
        'description': 'Roam Research是一款基于双向链接的笔记工具，帮助用户构建网络化的思维和知识体系。',
        'url': 'https://roamresearch.com/',
        'category_slug': 'academic-tools',
        'resource_type': 'tool',
        'is_free': False,
        'price_info': '$15/月',
        'features': ['双向链接', '块引用', '图谱视图', '每日笔记', '标签系统'],
        'platform_support': ['Web'],
        'tags': ['笔记', '知识管理', '双向链接', '思维']
    },
    {
        'title': 'Logseq',
        'short_description': '本地优先的知识管理',
        'description': 'Logseq是一个开源的本地优先知识管理工具，支持双向链接和块级引用。',
        'url': 'https://logseq.com/',
        'category_slug': 'academic-tools',
        'resource_type': 'tool',
        'is_free': True,
        'features': ['本地存储', '双向链接', '块引用', '开源', '隐私保护'],
        'platform_support': ['Windows', 'macOS', 'Linux', 'Mobile'],
        'tags': ['笔记', '开源', '本地', '知识管理']
    },
    {
        'title': 'Anki',
        'short_description': '间隔重复记忆工具',
        'description': 'Anki是一款基于间隔重复算法的记忆工具，帮助用户高效记忆和复习知识点。',
        'url': 'https://apps.ankiweb.net/',
        'category_slug': 'academic-tools',
        'resource_type': 'tool',
        'is_free': True,
        'price_info': '桌面免费，iOS $24.99',
        'features': ['间隔重复', '自定义卡片', '同步', '插件系统', '统计分析'],
        'platform_support': ['Windows', 'macOS', 'Linux', 'Mobile', 'Web'],
        'tags': ['记忆', '复习', '间隔重复', '学习']
    },

    # 更多开发和部署工具
    {
        'title': 'Vercel',
        'short_description': '前端部署平台',
        'description': 'Vercel是一个专注于前端的部署平台，支持静态网站和Serverless函数的快速部署。',
        'url': 'https://vercel.com/',
        'category_slug': 'dev-tools',
        'resource_type': 'tool',
        'is_free': True,
        'price_info': '免费版，Pro版$20/月',
        'features': ['快速部署', 'CDN加速', 'Serverless', 'Git集成', '预览部署'],
        'platform_support': ['Web'],
        'tags': ['部署', '前端', 'Serverless', 'CDN']
    },
    {
        'title': 'Netlify',
        'short_description': 'JAMstack部署平台',
        'description': 'Netlify是一个现代化的Web开发平台，专注于JAMstack应用的构建和部署。',
        'url': 'https://www.netlify.com/',
        'category_slug': 'dev-tools',
        'resource_type': 'tool',
        'is_free': True,
        'price_info': '免费版，Pro版$19/月',
        'features': ['持续部署', '表单处理', '身份验证', 'CDN', '分支预览'],
        'platform_support': ['Web'],
        'tags': ['部署', 'JAMstack', '静态网站', 'CDN']
    },
    {
        'title': 'Heroku',
        'short_description': '云应用平台',
        'description': 'Heroku是一个云平台即服务(PaaS)，支持多种编程语言的应用部署和管理。',
        'url': 'https://www.heroku.com/',
        'category_slug': 'dev-tools',
        'resource_type': 'tool',
        'is_free': False,
        'price_info': '免费额度，付费$7/月起',
        'features': ['多语言支持', '插件生态', '自动扩展', 'Git部署', '数据库'],
        'platform_support': ['Web'],
        'tags': ['云平台', 'PaaS', '部署', '多语言']
    },

    # 数据库和后端服务
    {
        'title': 'Firebase',
        'short_description': 'Google后端服务平台',
        'description': 'Firebase是Google提供的后端即服务平台，提供数据库、认证、托管等服务。',
        'url': 'https://firebase.google.com/',
        'category_slug': 'dev-tools',
        'resource_type': 'tool',
        'is_free': True,
        'price_info': '免费额度，按使用量付费',
        'features': ['实时数据库', '用户认证', '云存储', '托管', '分析'],
        'platform_support': ['Web', 'Mobile', 'Server'],
        'tags': ['后端服务', 'Google', '数据库', '认证']
    },
    {
        'title': 'Supabase',
        'short_description': '开源Firebase替代',
        'description': 'Supabase是一个开源的Firebase替代方案，提供数据库、认证、实时订阅等功能。',
        'url': 'https://supabase.com/',
        'category_slug': 'dev-tools',
        'resource_type': 'tool',
        'is_free': True,
        'price_info': '免费版，Pro版$25/月',
        'features': ['PostgreSQL', '实时API', '用户认证', '存储', '边缘函数'],
        'platform_support': ['Web', 'Mobile', 'Server'],
        'tags': ['开源', '数据库', 'PostgreSQL', '后端服务']
    },

    # 设计资源和素材
    {
        'title': 'Unsplash',
        'short_description': '免费高质量图片',
        'description': 'Unsplash提供大量免费的高质量图片，可用于商业和个人项目。',
        'url': 'https://unsplash.com/',
        'category_slug': 'design-tools',
        'resource_type': 'website',
        'is_free': True,
        'features': ['高质量图片', '免费商用', 'API支持', '分类丰富', '搜索功能'],
        'platform_support': ['Web', 'API'],
        'tags': ['图片素材', '免费', '商用', '高质量']
    },
    {
        'title': 'Dribbble',
        'short_description': '设计师作品展示平台',
        'description': 'Dribbble是全球知名的设计师作品展示和交流平台，汇集了大量优秀的设计作品。',
        'url': 'https://dribbble.com/',
        'category_slug': 'design-tools',
        'resource_type': 'website',
        'is_free': True,
        'price_info': '免费浏览，Pro版$8/月',
        'features': ['设计作品', '设计师社区', '招聘', '设计趋势', '灵感'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['设计作品', '设计师', '灵感', '社区']
    },
    {
        'title': 'Behance',
        'short_description': 'Adobe创意作品平台',
        'description': 'Behance是Adobe旗下的创意作品展示平台，设计师可以在这里展示和发现优秀作品。',
        'url': 'https://www.behance.net/',
        'category_slug': 'design-tools',
        'resource_type': 'website',
        'is_free': True,
        'features': ['作品展示', '创意社区', '项目管理', '设计趋势', 'Adobe集成'],
        'platform_support': ['Web', 'Mobile App'],
        'tags': ['创意作品', 'Adobe', '设计', '作品集']
    },

    # 更多实用工具
    {
        'title': 'Regex101',
        'short_description': '正则表达式测试工具',
        'description': 'Regex101是一个在线正则表达式测试和学习工具，支持多种编程语言的正则语法。',
        'url': 'https://regex101.com/',
        'category_slug': 'useful-websites',
        'resource_type': 'website',
        'is_free': True,
        'features': ['正则测试', '语法解释', '多语言支持', '保存分享', '学习资源'],
        'platform_support': ['Web'],
        'tags': ['正则表达式', '测试工具', '学习', '编程']
    },
    {
        'title': 'Can I Use',
        'short_description': '浏览器兼容性查询',
        'description': 'Can I Use提供Web技术在各种浏览器中的兼容性信息，是前端开发的必备工具。',
        'url': 'https://caniuse.com/',
        'category_slug': 'useful-websites',
        'resource_type': 'website',
        'is_free': True,
        'features': ['兼容性查询', '浏览器支持', '使用统计', '特性搜索', '历史数据'],
        'platform_support': ['Web'],
        'tags': ['浏览器兼容性', '前端', 'Web标准', '查询工具']
    },
    {
        'title': 'JSON Formatter',
        'short_description': 'JSON格式化工具',
        'description': '在线JSON格式化和验证工具，帮助开发者处理和调试JSON数据。',
        'url': 'https://jsonformatter.curiousconcept.com/',
        'category_slug': 'useful-websites',
        'resource_type': 'website',
        'is_free': True,
        'features': ['JSON格式化', '语法验证', '压缩', '美化', '错误提示'],
        'platform_support': ['Web'],
        'tags': ['JSON', '格式化', '验证', '开发工具']
    }
]
