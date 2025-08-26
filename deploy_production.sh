#!/bin/bash

# CS学习平台生产环境部署脚本
# 使用方法: chmod +x deploy_production.sh && sudo ./deploy_production.sh

echo "🚀 开始部署 CS学习平台 (生产环境)..."

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

# 检查环境变量文件
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}错误: 未找到环境变量文件 $PROJECT_DIR/.env${NC}"
    echo -e "${YELLOW}请先复制 .env.example 为 .env 并填入正确的配置${NC}"
    exit 1
fi

echo -e "${BLUE}1. 更新系统包...${NC}"
apt update && apt upgrade -y

echo -e "${BLUE}2. 安装必要的软件包...${NC}"
apt install -y python3 python3-pip python3-venv nginx mysql-server redis-server git supervisor ufw

echo -e "${BLUE}3. 创建项目目录结构...${NC}"
mkdir -p $PROJECT_DIR/logs
mkdir -p $PROJECT_DIR/staticfiles
mkdir -p $PROJECT_DIR/media
mkdir -p $PROJECT_DIR/backups

echo -e "${BLUE}4. 设置虚拟环境...${NC}"
cd $PROJECT_DIR
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

echo -e "${BLUE}5. 安装Python依赖...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${BLUE}6. 运行数据库迁移...${NC}"
python manage.py makemigrations --settings=cs_learning_platform.settings_production
python manage.py migrate --settings=cs_learning_platform.settings_production

echo -e "${BLUE}7. 收集静态文件...${NC}"
python manage.py collectstatic --noinput --settings=cs_learning_platform.settings_production

echo -e "${BLUE}8. 创建超级用户...${NC}"
echo -e "${YELLOW}请创建管理员账户:${NC}"
python manage.py createsuperuser --settings=cs_learning_platform.settings_production

echo -e "${BLUE}9. 配置Gunicorn服务...${NC}"
cat > $SYSTEMD_SERVICE << EOF
[Unit]
Description=CS Learning Platform Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind unix:$PROJECT_DIR/cs_learning_platform.sock cs_learning_platform.wsgi:application --settings=cs_learning_platform.settings_production
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${BLUE}10. 配置Nginx...${NC}"
cat > $NGINX_CONFIG << EOF
server {
    listen 80;
    server_name _;  # 临时配置，请替换为您的域名

    client_max_body_size 20M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        root $PROJECT_DIR;
        expires 30d;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
        gzip_static on;
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
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
}
EOF

echo -e "${BLUE}11. 启用Nginx配置...${NC}"
ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

echo -e "${BLUE}12. 设置文件权限...${NC}"
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod 600 $PROJECT_DIR/.env

echo -e "${BLUE}13. 配置防火墙...${NC}"
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'

echo -e "${BLUE}14. 启动服务...${NC}"
systemctl daemon-reload
systemctl enable $PROJECT_NAME
systemctl start $PROJECT_NAME
systemctl enable nginx
systemctl restart nginx
systemctl enable redis-server
systemctl start redis-server

echo -e "${BLUE}15. 创建备份脚本...${NC}"
cat > /usr/local/bin/backup_cs_platform.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/www/cs_learning_platform/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份数据库
mysqldump -u cs_user -p cs_learning_platform > "$BACKUP_DIR/db_backup_$DATE.sql"

# 备份媒体文件
tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" -C /var/www/cs_learning_platform media/

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: $DATE"
EOF

chmod +x /usr/local/bin/backup_cs_platform.sh

echo -e "${BLUE}16. 设置定时备份...${NC}"
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup_cs_platform.sh") | crontab -

echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "${YELLOW}部署后检查清单:${NC}"
echo "1. 检查服务状态:"
echo "   systemctl status $PROJECT_NAME"
echo "   systemctl status nginx"
echo "   systemctl status redis-server"
echo ""
echo "2. 查看日志:"
echo "   journalctl -u $PROJECT_NAME -f"
echo "   tail -f /var/log/nginx/error.log"
echo ""
echo "3. 测试网站:"
echo "   curl -I http://localhost"
echo ""
echo "4. 配置域名:"
echo "   编辑 $NGINX_CONFIG 中的 server_name"
echo ""
echo "5. 设置SSL证书 (推荐):"
echo "   ./setup_ssl.sh your-domain.com"

echo -e "${BLUE}🎉 CS学习平台部署成功！${NC}"
