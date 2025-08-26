# 🎓 计算机科学学习平台

一个专注于计算机科学基础知识的交互式在线学习平台，通过可视化和详细步骤展示帮助学习者深入理解各种算法和数据结构。

![平台预览](https://img.shields.io/badge/Django-4.2+-green) ![Python版本](https://img.shields.io/badge/Python-3.8+-blue) ![许可证](https://img.shields.io/badge/License-MIT-orange)

## ✨ 特色功能

- 🧮 **海明码编码解码** - 完整的错误检测与纠正演示
- 🔍 **CRC循环冗余检验** - 数据完整性校验原理学习
- 📚 **详细原理讲解** - 每个知识点都有完整的理论基础
- 🎯 **步骤化演示** - 算法执行的每一步都清晰可见
- 📱 **响应式设计** - 支持桌面和移动设备
- 🚀 **易于扩展** - 模块化架构，便于添加新知识点
- 🆓 **完全免费** - 开源项目，持续更新

## 🎯 在线演示

访问 [在线演示](https://your-demo-site.com) 体验完整功能。

## 📋 目录

- [快速开始](#-快速开始)
- [功能详解](#-功能详解)
- [项目结构](#-项目结构)
- [开发指南](#-开发指南)
- [部署说明](#-部署说明)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

## 🚀 快速开始

### 系统要求

- Python 3.8+
- Django 4.2+
- 现代浏览器（Chrome、Firefox、Safari、Edge）

### 一键启动

1. **下载项目**
```bash
# 如果使用Git
git clone https://github.com/yourusername/cs-learning-platform.git
cd cs-learning-platform

# 或者直接下载ZIP文件并解压
```

2. **运行启动脚本**
```bash
python start.py
```

启动脚本会自动完成：
- ✅ 检查Python版本
- ✅ 安装依赖包
- ✅ 创建数据库
- ✅ 初始化示例数据
- ✅ 启动开发服务器

3. **访问网站**
```
🌐 主页面: http://127.0.0.1:8000
🛠️ 管理后台: http://127.0.0.1:8000/admin/
```

### 手动安装

如果自动启动脚本无法运行，可以手动执行：

```bash
# 1. 创建虚拟环境（推荐）
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 5. 初始化数据
python manage.py init_knowledge

# 6. 创建超级用户（可选）
python manage.py create_superuser_auto

# 7. 启动服务器
python manage.py runserver
```

## 🎮 功能详解

### 🧮 海明码编码解码

海明码是一种线性纠错码，能够检测并纠正单个比特错误。

**功能特性：**
- 📝 **编码功能**：将原始二进制数据转换为海明码
- 🔍 **解码功能**：从海明码恢复原始数据
- 🛠️ **错误检测**：自动检测传输中的单比特错误
- 🔧 **错误纠正**：自动定位并纠正错误位
- 📋 **步骤展示**：详细显示每一步计算过程

**使用示例：**
1. 输入原始数据：`1011`
2. 系统计算校验位：需要3个校验位
3. 生成海明码：`1011010`
4. 可模拟传输错误测试纠错能力

### 🔍 CRC循环冗余检验

CRC是一种错误检测技术，通过多项式除法检测数据完整性。

**功能特性：**
- 🧮 **CRC计算**：根据数据和生成多项式计算CRC码
- ✅ **数据验证**：验证接收数据的完整性
- 📐 **多项式支持**：支持CRC-3、CRC-4、CRC-5等常用多项式
- ⚙️ **自定义多项式**：允许用户输入自定义生成多项式
- 👁️ **过程可视化**：展示多项式除法的详细过程

**支持的CRC类型：**
- **CRC-3**: 1011 (x³+x+1)
- **CRC-4**: 10011 (x⁴+x+1)
- **CRC-5**: 101001 (x⁵+x³+1)
- **自定义**: 用户自定义多项式

## 📁 项目结构

```
cs_learning_platform/
├── 📄 manage.py                          # Django管理脚本
├── 📄 start.py                           # 一键启动脚本
├── 📄 requirements.txt                   # 项目依赖
├── 📄 README.md                          # 项目说明
├── 📁 cs_learning_platform/             # 项目配置目录
│   ├── 📄 __init__.py
│   ├── 📄 settings.py                    # Django设置
│   ├── 📄 urls.py                        # 根URL配置
│   └── 📄 wsgi.py                        # WSGI配置
└── 📁 knowledge_app/                     # 主应用目录
    ├── 📄 __init__.py
    ├── 📄 admin.py                       # 管理后台配置
    ├── 📄 apps.py                        # 应用配置
    ├── 📄 models.py                      # 数据模型
    ├── 📄 views.py                       # 视图函数
    ├── 📄 urls.py                        # URL配置
    ├── 📁 algorithms/                    # 算法实现模块
    │   ├── 📄 __init__.py
    │   ├── 📄 hamming_code.py           # 海明码算法
    │   └── 📄 crc_check.py              # CRC算法
    ├── 📁 management/                    # Django管理命令
    │   └── 📁 commands/
    │       ├── 📄 __init__.py
    │       ├── 📄 init_knowledge.py      # 初始化知识点
    │       ├── 📄 list_knowledge.py      # 列出知识点
    │       └── 📄 create_superuser_auto.py
    └── 📁 templates/                     # HTML模板
        └── 📁 knowledge_app/
            ├── 📄 base.html              # 基础模板
            ├── 📄 index.html             # 主页
            ├── 📄 hamming_code.html      # 海明码页面
            ├── 📄 crc_check.html         # CRC页面
            └── 📄 coming_soon.html       # 即将推出页面
```

## 🔧 开发指南

### 添加新知识点

要添加一个新的算法学习模块，请按照以下步骤：

1. **创建算法实现**
```python
# knowledge_app/algorithms/new_algorithm.py
class NewAlgorithm:
    def __init__(self):
        self.steps = []
    
    def process(self, data):
        # 实现算法逻辑
        # 记录详细步骤
        pass
```

2. **添加数据库记录**
```bash
# 方法1: 直接在init_knowledge.py中添加
# 方法2: 使用Django管理后台添加
python manage.py init_knowledge
```

3. **创建视图函数**
```python
# views.py中添加API接口
@csrf_exempt
def new_algorithm_api(request):
    # API实现
    pass
```

4. **创建HTML模板**
```html
<!-- templates/knowledge_app/new_algorithm.html -->
{% extends 'knowledge_app/base.html' %}
<!-- 页面实现 -->
```

5. **更新URL配置**
```python
# urls.py中添加路由
path('api/new-algorithm/', views.new_algorithm_api, name='new_algorithm'),
```

### 管理命令

项目提供了便捷的管理命令：

```bash
# 📋 查看所有知识点
python manage.py list_knowledge

# 🔄 重新初始化数据
python manage.py init_knowledge --clear

# 📊 按分类查看
python manage.py list_knowledge --category=algorithm

# 👑 创建管理员
python manage.py create_superuser_auto

# 📈 查看已实现的功能
python manage.py list_knowledge --implemented-only
```

### API接口文档

**海明码编码**
```http
POST /api/hamming/encode/
Content-Type: application/json

{
    "data_bits": "1011"
}
```

**海明码解码**
```http
POST /api/hamming/decode/
Content-Type: application/json

{
    "hamming_bits": "1011010"
}
```

**CRC计算**
```http
POST /api/crc/calculate/
Content-Type: application/json

{
    "data_bits": "1101",
    "polynomial": "1011"
}
```

**CRC验证**
```http
POST /api/crc/verify/
Content-Type: application/json

{
    "data_with_crc": "1101010",
    "polynomial": "1011"
}
```

## 🚀 部署说明

### 开发环境

项目默认配置适用于开发环境，使用SQLite数据库和Django开发服务器。

### 生产环境

1. **环境变量配置**
```bash
# 创建.env文件
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

2. **使用PostgreSQL**
```bash
pip install psycopg2-binary
# 更新settings.py中的数据库配置
```

3. **使用Gunicorn部署**
```bash
pip install gunicorn
gunicorn cs_learning_platform.wsgi:application
```

4. **使用Nginx反向代理**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/your/staticfiles/;
    }
}
```

### Docker部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 贡献指南

我们欢迎任何形式的贡献！

### 如何贡献

1. **Fork项目**
2. **创建特性分支**：`git checkout -b feature/AmazingFeature`
3. **提交更改**：`git commit -m 'Add some AmazingFeature'`
4. **推送分支**：`git push origin feature/AmazingFeature`
5. **创建Pull Request**

### 贡献类型

- 🐛 **Bug修复**：发现并修复问题
- ✨ **新功能**：添加新的算法或知识点
- 📚 **文档改进**：完善说明文档
- 🎨 **界面优化**：改进用户体验
- 🔧 **代码重构**：提高代码质量
- 🧪 **测试用例**：增加测试覆盖率

### 开发规范

- 遵循PEP 8 Python代码规范
- 为新功能编写测试用例
- 更新相关文档
- 提交信息要清晰明确

## 📈 路线图

### 已完成 ✅
- 🧮 海明码编码解码
- 🔍 CRC循环冗余检验
- 📱 响应式用户界面
- 🛠️ 管理后台
- 📋 详细文档

### 开发中 🚧
- 🔐 RSA加密算法
- 📊 排序算法可视化
- 🗜️ 哈夫曼编码

### 计划中 📋
- 🌳 B+树索引原理
- 🗺️ 最短路径算法
- ⚙️ 进程调度算法
- 🔄 一致性哈希
- 🤖 决策树算法
- 👥 用户系统
- 📈 学习进度跟踪
- 🏆 成就系统
- 📱 移动端App

## 📞 联系方式

- 📧 **邮箱**: your.email@example.com
- 🌐 **项目主页**: https://github.com/yourusername/cs-learning-platform
- 🐛 **问题反馈**: https://github.com/yourusername/cs-learning-platform/issues
- 💬 **讨论交流**: https://github.com/yourusername/cs-learning-platform/discussions

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

```
MIT License

Copyright (c) 2025 CS Learning Platform

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 致谢

- 感谢所有贡献者的支持和参与
- 算法实现参考了经典计算机科学教材
- UI设计灵感来源于现代教育平台
- 特别感谢开源社区的无私分享

---

⭐ **如果这个项目对你有帮助，请给我们一个星标！**

💡 **有想法或建议？欢迎提交Issue或Pull Request！**

🎓 **让我们一起让计算机科学学习变得更有趣！**