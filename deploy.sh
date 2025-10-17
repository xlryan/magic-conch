#!/bin/bash
set -e

# 检查是否使用 bash 执行
if [ -z "$BASH_VERSION" ]; then
    echo "❌ 错误：请使用 bash 执行此脚本"
    echo "   正确命令: bash deploy.sh"
    exit 1
fi

echo "🚀 神奇海螺 · 烂尾博物馆 - 生产环境一键部署"
echo "================================================"

# 检查是否在项目根目录
if [ ! -f "README.md" ] || [ ! -d "server" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 自动检测环境信息
CURRENT_USER=$(whoami)
CURRENT_DIR=$(pwd)
echo "📋 检测到的环境信息："
echo "   用户: $CURRENT_USER"
echo "   目录: $CURRENT_DIR"

# 检测 Python 环境和路径
if command -v conda &> /dev/null; then
    echo "✅ 检测到 Conda 环境"
    PYTHON_CMD="python"
    CONDA_PATH=$(dirname $(dirname $(which conda)))
    PYTHON_PATH="$CONDA_PATH/bin/python"
    UVICORN_PATH="$CONDA_PATH/bin/uvicorn"
    echo "   Conda 路径: $CONDA_PATH"
elif command -v python3 &> /dev/null; then
    echo "✅ 检测到 Python3"
    PYTHON_CMD="python3"
    PYTHON_PATH=$(which python3)
    UVICORN_PATH=$(dirname $PYTHON_PATH)/uvicorn
else
    echo "❌ 错误：未找到 Python 环境"
    exit 1
fi

# 询问是否配置生产环境服务
echo ""
read -p "是否配置为生产环境服务（systemd）？[y/N] " -n 1 -r
echo
SETUP_SYSTEMD=$REPLY

# 1. 安装 Python 依赖
echo ""
echo "📦 步骤 1/6: 安装 Python 依赖..."
$PYTHON_CMD -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r server/requirements.txt

# 2. 配置环境变量
echo ""
echo "⚙️  步骤 2/6: 配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env.example .env

    # 生成随机 SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env

    # 生成随机 ADMIN_TOKEN
    ADMIN_TOKEN=$(openssl rand -hex 16 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    sed -i.bak "s/ADMIN_TOKEN=.*/ADMIN_TOKEN=${ADMIN_TOKEN}/" .env

    # 使用 SQLite（简单快速）
    sed -i.bak 's|DB_URL=.*|DB_URL=sqlite:///./storage/app.db|' .env

    # 删除备份文件
    rm -f .env.bak

    echo "✅ 已生成 .env 文件"
    echo "📝 管理员 Token: ${ADMIN_TOKEN}"
    echo "   请保存此 Token，用于访问 /admin 后台"

    # 保存 Token 到单独文件
    echo "$ADMIN_TOKEN" > .admin_token
    chmod 600 .admin_token
    echo "   Token 已保存到 .admin_token 文件"
else
    echo "⚠️  .env 文件已存在，跳过"
    if [ -f ".admin_token" ]; then
        ADMIN_TOKEN=$(cat .admin_token)
    else
        ADMIN_TOKEN=$(grep ADMIN_TOKEN .env | cut -d '=' -f2)
    fi
fi

# 3. 创建必要的目录
echo ""
echo "📁 步骤 3/6: 创建存储目录..."
mkdir -p storage data/entries
touch storage/.gitkeep
echo "✅ 目录创建完成"

# 4. 初始化数据库
echo ""
echo "🗄️  步骤 4/6: 初始化数据库..."
$PYTHON_CMD scripts/init_db.py

# 5. 导入示例数据（如果存在）
echo ""
echo "📊 步骤 5/6: 导入示例数据..."
if [ -d "data/entries" ] && [ "$(ls -A data/entries/*.yml 2>/dev/null)" ]; then
    $PYTHON_CMD scripts/import_entries.py
else
    echo "⚠️  未找到 YAML 数据文件，跳过导入"
fi

# 6. 配置 Systemd 服务（如果用户选择）
if [[ $SETUP_SYSTEMD =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔧 步骤 6/6: 配置 Systemd 服务..."

    # 创建日志目录
    sudo mkdir -p /var/log/magic-conch
    sudo chown $CURRENT_USER:$CURRENT_USER /var/log/magic-conch
    echo "✅ 日志目录创建完成: /var/log/magic-conch"

    # 自动生成 systemd 服务文件
    cat > magic-conch.service.tmp << EOF
[Unit]
Description=Magic Conch Graveyard Museum
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CONDA_PATH/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$UVICORN_PATH server.app:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

# 日志
StandardOutput=append:/var/log/magic-conch/access.log
StandardError=append:/var/log/magic-conch/error.log

# 安全设置
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    # 安装服务
    sudo cp magic-conch.service.tmp /etc/systemd/system/magic-conch.service
    sudo systemctl daemon-reload
    sudo systemctl enable magic-conch
    sudo systemctl start magic-conch

    # 清理临时文件
    rm magic-conch.service.tmp

    echo "✅ Systemd 服务配置完成"
    echo ""
    echo "📋 服务管理命令："
    echo "   查看状态: sudo systemctl status magic-conch"
    echo "   查看日志: sudo journalctl -u magic-conch -f"
    echo "   重启服务: sudo systemctl restart magic-conch"
    echo "   停止服务: sudo systemctl stop magic-conch"

    # 等待服务启动
    sleep 3

    # 检查服务状态
    if sudo systemctl is-active --quiet magic-conch; then
        echo ""
        echo "✅ 服务已成功启动！"
        SERVER_IP=$(hostname -I | awk '{print $1}')
        echo "🌐 访问地址: http://$SERVER_IP:8000"
    else
        echo ""
        echo "⚠️  服务启动失败，请检查日志："
        echo "   sudo journalctl -u magic-conch -n 50"
    fi
else
    echo ""
    echo "⏭️  步骤 6/6: 跳过 Systemd 配置"
fi

# 完成提示
echo ""
echo "================================================"
echo "✅ 部署完成！"
echo ""

if [[ ! $SETUP_SYSTEMD =~ ^[Yy]$ ]]; then
    echo "🎯 手动启动命令："
    echo ""
    echo "   开发模式（自动重载）："
    echo "   uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload"
    echo ""
    echo "   生产模式（2个工作进程）："
    echo "   uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 2"
    echo ""
    echo "   后台运行（使用 nohup）："
    echo "   nohup uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 2 > app.log 2>&1 &"
    echo ""
    SERVER_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "YOUR_SERVER_IP")
    echo "🌐 访问地址: http://$SERVER_IP:8000"
fi

echo "🔐 管理后台: http://YOUR_SERVER_IP:8000/admin"
echo ""
echo "📝 管理员 Token: $ADMIN_TOKEN"
echo "   Token 已保存到 .admin_token 文件"
echo "   查看: cat .admin_token"
echo ""
echo "📚 更多帮助: 查看 DEPLOY.md"
echo ""
