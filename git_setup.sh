#!/bin/bash

# CS学习平台 Git 初始化脚本
# 使用方法: chmod +x git_setup.sh && ./git_setup.sh

echo "🚀 初始化 CS学习平台 Git 仓库..."

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}1. 初始化 Git 仓库...${NC}"
git init

echo -e "${BLUE}2. 添加所有文件到暂存区...${NC}"
git add .

echo -e "${BLUE}3. 创建初始提交...${NC}"
git commit -m "🎉 Initial commit: CS学习平台完整项目

✨ 功能特性:
- 每日CS名词生成系统 (AI驱动)
- 知识点管理系统 (6大领域)
- 智能练习生成器
- 用户认证和个人资料管理
- 资源聚合功能
- 性能监控和缓存优化

🔧 技术栈:
- Django 5.2.4
- MySQL数据库
- Redis缓存
- Kimi AI API集成
- Nginx + Gunicorn部署

🛡️ 安全特性:
- 环境变量配置
- 生产环境安全设置
- 自动备份系统
- 防火墙配置

📦 部署就绪:
- 一键部署脚本
- 完整的部署文档
- 生产环境配置"

echo -e "${BLUE}4. 设置默认分支为 main...${NC}"
git branch -M main

echo -e "${GREEN}✅ Git 仓库初始化完成！${NC}"
echo ""
echo -e "${YELLOW}下一步操作:${NC}"
echo "1. 在 GitHub/GitLab 创建远程仓库"
echo "2. 添加远程仓库:"
echo "   git remote add origin https://github.com/your-username/cs-learning-platform.git"
echo "3. 推送到远程仓库:"
echo "   git push -u origin main"
echo ""
echo -e "${YELLOW}常用 Git 命令:${NC}"
echo "查看状态: git status"
echo "添加文件: git add ."
echo "提交更改: git commit -m '提交信息'"
echo "推送更改: git push"
echo "拉取更新: git pull"
