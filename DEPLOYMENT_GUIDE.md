# 🚀 CS学习平台部署指南

## 📋 准备清单

### 1. 购买服务器
**推荐配置：**
- **CPU**: 1核心（最低）/ 2核心（推荐）
- **内存**: 2GB（最低）/ 4GB（推荐）
- **存储**: 40GB SSD
- **带宽**: 1Mbps（最低）/ 5Mbps（推荐）

**推荐服务商：**
- 阿里云：学生机约100元/年
- 腾讯云：新用户优惠
- 华为云：企业级稳定

### 2. 购买域名（可选但推荐）
- 在阿里云、腾讯云等购买域名
- 价格：.com域名约60元/年
- 配置DNS解析到服务器IP

### 3. 操作系统选择
- **推荐**: Ubuntu 20.04 LTS 或 Ubuntu 22.04 LTS
- **原因**: 稳定、文档丰富、社区支持好

## 🛠️ 部署步骤

### 第一步：连接服务器

```bash
# 使用SSH连接服务器（替换为您的服务器IP）
ssh root@your-server-ip

# 或者使用用户名连接
ssh username@your-server-ip
```

### 第二步：上传项目文件

**方法1：使用Git（推荐）**
```bash
# 在服务器上克隆项目
git clone https://github.com/your-username/cs-learning-platform.git
cd cs-learning-platform
```

**方法2：使用SCP上传**
```bash
# 在本地执行，上传整个项目文件夹
scp -r /path/to/your/project root@your-server-ip:/tmp/
```

### 第三步：运行部署脚本

```bash
# 给脚本执行权限
chmod +x deploy.sh

# 运行部署脚本
sudo ./deploy.sh
```

### 第四步：配置数据库

```bash
# 登录MySQL
sudo mysql -u root -p

# 执行以下SQL命令
CREATE DATABASE cs_learning_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'cs_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON cs_learning_platform.* TO 'cs_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 第五步：配置环境变量

```bash
# 编辑环境变量文件
sudo nano /var/www/cs_learning_platform/.env
```

填入以下内容：
```env
DEBUG=False
SECRET_KEY=your-very-long-secret-key-here
DB_NAME=cs_learning_platform
DB_USER=cs_user
DB_PASSWORD=your_strong_password
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST_USER=your_email@qq.com
EMAIL_HOST_PASSWORD=your_email_app_password
```

### 第六步：配置域名（如果有）

```bash
# 编辑Nginx配置
sudo nano /etc/nginx/sites-available/cs_learning_platform
```

将 `your-domain.com` 替换为您的实际域名。

### 第七步：启动服务

```bash
# 重启所有服务
sudo systemctl restart cs_learning_platform
sudo systemctl restart nginx

# 检查服务状态
sudo systemctl status cs_learning_platform
sudo systemctl status nginx
```

### 第八步：配置SSL证书（推荐）

```bash
# 给SSL脚本执行权限
chmod +x setup_ssl.sh

# 安装SSL证书（替换为您的域名）
sudo ./setup_ssl.sh your-domain.com
```

## 🔧 常见问题解决

### 1. 服务启动失败
```bash
# 查看详细错误日志
sudo journalctl -u cs_learning_platform -f

# 检查配置文件语法
sudo nginx -t
```

### 2. 数据库连接失败
```bash
# 检查MySQL服务状态
sudo systemctl status mysql

# 测试数据库连接
mysql -u cs_user -p cs_learning_platform
```

### 3. 静态文件不显示
```bash
# 重新收集静态文件
cd /var/www/cs_learning_platform
source venv/bin/activate
python manage.py collectstatic --noinput --settings=cs_learning_platform.settings_production
```

### 4. 权限问题
```bash
# 重新设置文件权限
sudo chown -R www-data:www-data /var/www/cs_learning_platform
sudo chmod -R 755 /var/www/cs_learning_platform
```

## 📊 性能优化建议

### 1. 启用Gzip压缩
在Nginx配置中添加：
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
```

### 2. 配置缓存
```bash
# 安装Redis
sudo apt install redis-server

# 在Django设置中启用缓存
# 已在settings_production.py中配置
```

### 3. 数据库优化
```sql
-- 为常用查询添加索引
-- 在MySQL中执行
USE cs_learning_platform;
CREATE INDEX idx_daily_term_date ON knowledge_app_dailyterm(display_date);
CREATE INDEX idx_exercise_active ON knowledge_app_exercise(is_active);
```

## 🔒 安全建议

### 1. 防火墙配置
```bash
# 启用UFW防火墙
sudo ufw enable

# 允许SSH、HTTP、HTTPS
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
```

### 2. 定期备份
```bash
# 创建备份脚本
sudo nano /usr/local/bin/backup_cs_platform.sh
```

### 3. 监控设置
```bash
# 安装监控工具
sudo apt install htop iotop

# 设置日志轮转
sudo nano /etc/logrotate.d/cs_learning_platform
```

## 📈 监控和维护

### 1. 查看日志
```bash
# Django应用日志
sudo tail -f /var/www/cs_learning_platform/logs/django.log

# Nginx访问日志
sudo tail -f /var/log/nginx/access.log

# 系统服务日志
sudo journalctl -u cs_learning_platform -f
```

### 2. 性能监控
```bash
# 查看系统资源使用
htop

# 查看磁盘使用
df -h

# 查看内存使用
free -h
```

### 3. 更新部署
```bash
# 拉取最新代码
cd /var/www/cs_learning_platform
git pull origin main

# 重启服务
sudo systemctl restart cs_learning_platform
```

## 🆘 紧急情况处理

### 网站无法访问
1. 检查服务状态：`sudo systemctl status nginx cs_learning_platform`
2. 查看错误日志：`sudo tail -f /var/log/nginx/error.log`
3. 重启服务：`sudo systemctl restart nginx cs_learning_platform`

### 数据库问题
1. 检查MySQL状态：`sudo systemctl status mysql`
2. 查看MySQL日志：`sudo tail -f /var/log/mysql/error.log`
3. 重启MySQL：`sudo systemctl restart mysql`

### 磁盘空间不足
1. 清理日志文件：`sudo find /var/log -name "*.log" -type f -size +100M -delete`
2. 清理临时文件：`sudo apt autoremove && sudo apt autoclean`

## 📞 技术支持

如果遇到问题，可以：
1. 发送邮件到：2795828496@qq.com
2. 提供错误日志和系统信息
3. 描述具体的操作步骤和错误现象

---

**祝您部署成功！🎉**
