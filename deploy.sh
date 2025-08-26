#!/bin/bash

# Django项目部署脚本
# 使用方法: chmod +x deploy.sh && ./deploy.sh

echo "🚀 开始部署 CS学习平台..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="cs_learning_platform"
PROJECT_DIR="/var/www/$PROJECT_NAME"
VENV_DIR="$PROJECT_DIR/venv"
NGINX_CONFIG="/etc/nginx/sites-available/$PROJECT_NAME"
SYSTEMD_SERVICE="/etc/systemd/system/$PROJECT_NAME.service"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用sudo运行此脚本${NC}"
    exit 1
fi

echo -e "${BLUE}1. 更新系统包...${NC}"
apt update && apt upgrade -y

echo -e "${BLUE}2. 安装必要的软件包...${NC}"
apt install -y python3 python3-pip python3-venv nginx mysql-server redis-server git supervisor

echo -e "${BLUE}3. 创建项目目录...${NC}"
mkdir -p $PROJECT_DIR
mkdir -p $PROJECT_DIR/logs
mkdir -p $PROJECT_DIR/staticfiles
mkdir -p $PROJECT_DIR/media

echo -e "${BLUE}4. 设置MySQL数据库...${NC}"
echo -e "${YELLOW}请手动执行以下MySQL命令:${NC}"
echo "sudo mysql -u root -p"
echo "CREATE DATABASE cs_learning_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo "CREATE USER 'cs_user'@'localhost' IDENTIFIED BY 'your_password_here';"
echo "GRANT ALL PRIVILEGES ON cs_learning_platform.* TO 'cs_user'@'localhost';"
echo "FLUSH PRIVILEGES;"
echo "EXIT;"
echo -e "${YELLOW}按任意键继续...${NC}"
read -n 1

echo -e "${BLUE}5. 复制项目文件...${NC}"
# 假设当前目录就是项目目录
cp -r . $PROJECT_DIR/
cd $PROJECT_DIR

echo -e "${BLUE}6. 创建虚拟环境...${NC}"
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

echo -e "${BLUE}7. 安装Python依赖...${NC}"
pip install --upgrade pip
pip install django mysqlclient gunicorn redis python-dotenv

# 如果有requirements.txt文件
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

echo -e "${BLUE}8. 创建环境变量文件...${NC}"
cat > $PROJECT_DIR/.env << EOF
DEBUG=False
SECRET_KEY=your-secret-key-here
DB_NAME=cs_learning_platform
DB_USER=cs_user
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST_USER=your_email@qq.com
EMAIL_HOST_PASSWORD=your_email_password
EOF

echo -e "${YELLOW}请编辑 $PROJECT_DIR/.env 文件，填入正确的配置信息${NC}"

echo -e "${BLUE}9. 数据库迁移...${NC}"
python manage.py makemigrations
python manage.py migrate --settings=cs_learning_platform.settings_production

echo -e "${BLUE}10. 收集静态文件...${NC}"
python manage.py collectstatic --noinput --settings=cs_learning_platform.settings_production

echo -e "${BLUE}11. 创建超级用户...${NC}"
echo -e "${YELLOW}请创建管理员账户:${NC}"
python manage.py createsuperuser --settings=cs_learning_platform.settings_production

echo -e "${BLUE}12. 配置Gunicorn服务...${NC}"
cat > $SYSTEMD_SERVICE << EOF
[Unit]
Description=CS Learning Platform Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind unix:$PROJECT_DIR/cs_learning_platform.sock cs_learning_platform.wsgi:application --settings=cs_learning_platform.settings_production
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo -e "${BLUE}13. 配置Nginx...${NC}"
cat > $NGINX_CONFIG << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # 替换为您的域名

    location = /favicon.ico { access_log off; log_not_found off; }
    
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

echo -e "${BLUE}14. 启用Nginx配置...${NC}"
ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/
nginx -t

echo -e "${BLUE}15. 设置文件权限...${NC}"
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR

echo -e "${BLUE}16. 启动服务...${NC}"
systemctl daemon-reload
systemctl enable $PROJECT_NAME
systemctl start $PROJECT_NAME
systemctl enable nginx
systemctl restart nginx

echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "${YELLOW}请检查以下内容:${NC}"
echo "1. 编辑 $PROJECT_DIR/.env 文件"
echo "2. 编辑 $NGINX_CONFIG 文件中的域名"
echo "3. 检查服务状态: systemctl status $PROJECT_NAME"
echo "4. 检查Nginx状态: systemctl status nginx"
echo "5. 查看日志: journalctl -u $PROJECT_NAME -f"

echo -e "${BLUE}如果使用域名，请配置DNS解析到服务器IP${NC}"
echo -e "${BLUE}如果需要HTTPS，请安装SSL证书${NC}"
