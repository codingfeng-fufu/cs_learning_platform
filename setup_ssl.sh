#!/bin/bash

# SSL证书安装脚本（使用Let's Encrypt）
# 使用方法: chmod +x setup_ssl.sh && sudo ./setup_ssl.sh your-domain.com

DOMAIN=$1
PROJECT_NAME="cs_learning_platform"

if [ -z "$DOMAIN" ]; then
    echo "使用方法: ./setup_ssl.sh your-domain.com"
    exit 1
fi

echo "🔒 为域名 $DOMAIN 安装SSL证书..."

# 安装Certbot
apt update
apt install -y certbot python3-certbot-nginx

# 获取SSL证书
certbot --nginx -d $DOMAIN -d www.$DOMAIN

# 设置自动续期
crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | crontab -

echo "✅ SSL证书安装完成！"
echo "您的网站现在可以通过 https://$DOMAIN 访问"

# 更新Nginx配置以强制HTTPS
cat > /etc/nginx/sites-available/$PROJECT_NAME << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/$PROJECT_NAME;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root /var/www/$PROJECT_NAME;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/$PROJECT_NAME/cs_learning_platform.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

nginx -t && systemctl reload nginx

echo "🔒 HTTPS重定向已配置完成！"
