#!/bin/bash
set -e

echo "🚀 神奇海螺 · 烂尾博物馆 - 快速部署脚本"
echo "================================================"

# 检查是否在项目根目录
if [ ! -f "README.md" ] || [ ! -d "server" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检测 Python 环境
if command -v conda &> /dev/null; then
    echo "✅ 检测到 Conda 环境"
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    echo "✅ 检测到 Python3"
    PYTHON_CMD="python3"
else
    echo "❌ 错误：未找到 Python 环境"
    exit 1
fi

# 1. 安装 Python 依赖
echo ""
echo "📦 步骤 1/5: 安装 Python 依赖..."
$PYTHON_CMD -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r server/requirements.txt

# 2. 配置环境变量
echo ""
echo "⚙️  步骤 2/5: 配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env.example .env

    # 生成随机 SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env

    # 生成随机 ADMIN_TOKEN
    ADMIN_TOKEN=$(openssl rand -hex 16 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    sed -i "s/ADMIN_TOKEN=.*/ADMIN_TOKEN=${ADMIN_TOKEN}/" .env

    # 使用 SQLite（简单快速）
    sed -i 's|DB_URL=.*|DB_URL=sqlite:///./storage/app.db|' .env

    echo "✅ 已生成 .env 文件"
    echo "📝 管理员 Token: ${ADMIN_TOKEN}"
    echo "   请保存此 Token，用于访问 /admin 后台"
else
    echo "⚠️  .env 文件已存在，跳过"
fi

# 3. 创建必要的目录
echo ""
echo "📁 步骤 3/5: 创建存储目录..."
mkdir -p storage data/entries
touch storage/.gitkeep
echo "✅ 目录创建完成"

# 4. 初始化数据库
echo ""
echo "🗄️  步骤 4/5: 初始化数据库..."
$PYTHON_CMD scripts/init_db.py

# 5. 导入示例数据（如果存在）
echo ""
echo "📊 步骤 5/5: 导入示例数据..."
if [ -d "data/entries" ] && [ "$(ls -A data/entries/*.yml 2>/dev/null)" ]; then
    $PYTHON_CMD scripts/import_entries.py
else
    echo "⚠️  未找到 YAML 数据文件，跳过导入"
fi

# 完成提示
echo ""
echo "================================================"
echo "✅ 部署完成！"
echo ""
echo "🎯 启动命令："
echo "   开发模式（自动重载）："
echo "   uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "   生产模式："
echo "   uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 2"
echo ""
echo "   后台运行（使用 nohup）："
echo "   nohup uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 2 > app.log 2>&1 &"
echo ""
echo "🌐 访问地址: http://YOUR_SERVER_IP:8000"
echo "🔐 管理后台: http://YOUR_SERVER_IP:8000/admin"
echo ""
echo "📝 管理员 Token 保存在 .env 文件中"
echo "   查看: cat .env | grep ADMIN_TOKEN"
echo ""
