#!/bin/bash

# 🚀 CS学习平台一键部署脚本（新手版）
# 作者：冯宗林
# 使用方法：wget -O - https://your-repo/quick_deploy.sh | bash

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 显示欢迎信息
clear
echo -e "${PURPLE}"
echo "  ____  ____    ____                      _               ____  _       _    __                     "
echo " / ___||  _ \  / ___|  ___  __ _ _ __ _ __ (_)_ __   __ _  |  _ \| | __ _| |_ / _| ___  _ __ _ __ ___  "
echo "| |    | |_) | \___ \ / _ \/ _\` | '__| '_ \| | '_ \ / _\` | | |_) | |/ _\` | __| |_ / _ \| '__| '_ \` _ \ "
echo "| |___ |  _ <   ___) |  __/ (_| | |  | | | | | | | | (_| | |  __/| | (_| | |_|  _| (_) | |  | | | | | |"
echo " \____|_| \_\ |____/ \___|\__,_|_|  |_| |_|_|_| |_|\__, | |_|   |_|\__,_|\__|_|  \___/|_|  |_| |_| |_|"
echo "                                                   |___/                                             "
echo -e "${NC}"
echo -e "${GREEN}🎓 计算机科学学习平台 - 一键部署脚本${NC}"
echo -e "${BLUE}作者：冯宗林 (计科23级)${NC}"
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ 请使用 sudo 运行此脚本${NC}"
    echo "正确用法: sudo bash quick_deploy.sh"
    exit 1
fi

# 获取用户输入
echo -e "${YELLOW}📝 请提供以下信息：${NC}"
echo ""

read -p "🌐 您的域名 (可选，直接回车跳过): " DOMAIN
read -p "🔑 数据库密码 (建议使用强密码): " DB_PASSWORD
read -p "📧 您的QQ邮箱 (用于发送通知): " EMAIL_USER

# 生成随机SECRET_KEY
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

echo ""
echo -e "${GREEN}✅ 配置信息确认：${NC}"
echo "域名: ${DOMAIN:-'暂不配置'}"
echo "数据库密码: ${DB_PASSWORD}"
echo "邮箱: ${EMAIL_USER}"
echo ""

read -p "确认开始部署吗？(y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "部署已取消"
    exit 0
fi

echo ""
echo -e "${BLUE}🚀 开始自动部署...${NC}"

# 步骤1：更新系统
echo -e "${BLUE}📦 步骤1/10: 更新系统包...${NC}"
apt update -qq && apt upgrade -y -qq

# 步骤2：安装基础软件
echo -e "${BLUE}🛠️  步骤2/10: 安装必要软件...${NC}"
apt install -y -qq python3 python3-pip python3-venv nginx mysql-server redis-server git curl wget unzip

# 步骤3：配置MySQL
echo -e "${BLUE}🗄️  步骤3/10: 配置数据库...${NC}"
mysql -e "CREATE DATABASE IF NOT EXISTS cs_learning_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER IF NOT EXISTS 'cs_user'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';"
mysql -e "GRANT ALL PRIVILEGES ON cs_learning_platform.* TO 'cs_user'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

# 步骤4：创建项目目录
echo -e "${BLUE}📁 步骤4/10: 创建项目目录...${NC}"
PROJECT_DIR="/var/www/cs_learning_platform"
mkdir -p $PROJECT_DIR/{logs,staticfiles,media}

# 步骤5：下载项目代码（这里需要替换为实际的代码获取方式）
echo -e "${BLUE}📥 步骤5/10: 获取项目代码...${NC}"
# 如果是从当前目录部署
if [ -f "manage.py" ]; then
    cp -r . $PROJECT_DIR/
else
    echo -e "${RED}❌ 未找到Django项目文件，请确保在项目根目录运行此脚本${NC}"
    exit 1
fi

cd $PROJECT_DIR

# 步骤6：创建虚拟环境
echo -e "${BLUE}🐍 步骤6/10: 设置Python环境...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q

# 安装依赖
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
else
    pip install django mysqlclient gunicorn redis python-dotenv -q
fi

# 步骤7：创建配置文件
echo -e "${BLUE}⚙️  步骤7/10: 生成配置文件...${NC}"
cat > .env << EOF
DEBUG=False
SECRET_KEY=${SECRET_KEY}
DB_NAME=cs_learning_platform
DB_USER=cs_user
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST_USER=${EMAIL_USER}
EMAIL_HOST_PASSWORD=请手动设置QQ邮箱授权码
EOF

# 步骤8：数据库迁移
echo -e "${BLUE}🔄 步骤8/10: 初始化数据库...${NC}"
python manage.py makemigrations --settings=cs_learning_platform.settings_production
python manage.py migrate --settings=cs_learning_platform.settings_production
python manage.py collectstatic --noinput --settings=cs_learning_platform.settings_production

# 步骤9：配置系统服务
echo -e "${BLUE}🔧 步骤9/10: 配置系统服务...${NC}"

# 创建Gunicorn服务
cat > /etc/systemd/system/cs_learning_platform.service << EOF
[Unit]
Description=CS Learning Platform Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind unix:$PROJECT_DIR/cs_learning_platform.sock cs_learning_platform.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 配置Nginx
NGINX_CONFIG="/etc/nginx/sites-available/cs_learning_platform"
if [ -n "$DOMAIN" ]; then
    SERVER_NAME="$DOMAIN www.$DOMAIN"
else
    SERVER_NAME="_"
fi

cat > $NGINX_CONFIG << EOF
server {
    listen 80;
    server_name $SERVER_NAME;

    client_max_body_size 100M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        root $PROJECT_DIR;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root $PROJECT_DIR;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_DIR/cs_learning_platform.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 启用Nginx配置
ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 步骤10：启动服务
echo -e "${BLUE}🚀 步骤10/10: 启动所有服务...${NC}"

# 设置文件权限
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR

# 启动服务
systemctl daemon-reload
systemctl enable cs_learning_platform
systemctl start cs_learning_platform
systemctl enable nginx
systemctl restart nginx

# 检查服务状态
sleep 3
if systemctl is-active --quiet cs_learning_platform && systemctl is-active --quiet nginx; then
    echo ""
    echo -e "${GREEN}🎉 部署成功！${NC}"
    echo ""
    echo -e "${YELLOW}📋 部署信息：${NC}"
    echo "项目目录: $PROJECT_DIR"
    echo "配置文件: $PROJECT_DIR/.env"
    echo "日志目录: $PROJECT_DIR/logs"
    echo ""
    
    if [ -n "$DOMAIN" ]; then
        echo -e "${GREEN}🌐 访问地址: http://$DOMAIN${NC}"
        echo -e "${BLUE}💡 建议安装SSL证书: sudo ./setup_ssl.sh $DOMAIN${NC}"
    else
        SERVER_IP=$(curl -s ifconfig.me)
        echo -e "${GREEN}🌐 访问地址: http://$SERVER_IP${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}⚠️  重要提醒：${NC}"
    echo "1. 请编辑 $PROJECT_DIR/.env 文件，设置QQ邮箱授权码"
    echo "2. 创建管理员账户: cd $PROJECT_DIR && source venv/bin/activate && python manage.py createsuperuser --settings=cs_learning_platform.settings_production"
    echo "3. 如果使用域名，请配置DNS解析"
    echo ""
    echo -e "${BLUE}📞 技术支持: 2795828496@qq.com${NC}"
    
else
    echo -e "${RED}❌ 部署失败，请检查错误日志：${NC}"
    echo "Django服务状态: $(systemctl is-active cs_learning_platform)"
    echo "Nginx服务状态: $(systemctl is-active nginx)"
    echo ""
    echo "查看详细日志："
    echo "sudo journalctl -u cs_learning_platform -f"
    echo "sudo tail -f /var/log/nginx/error.log"
fi
