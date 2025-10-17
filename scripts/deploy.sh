#!/bin/bash
# Webhook 自动部署脚本
# 由 GitHub Webhook 触发执行

set -e

echo "🚀 开始自动部署..."
echo "================================"

# 获取项目根目录
PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$PROJECT_DIR"

echo "📂 项目目录: $PROJECT_DIR"
echo ""

# 1. 拉取最新代码
echo "📦 拉取最新代码..."
git fetch origin
git reset --hard origin/main
echo "✅ 代码已更新到最新版本"
echo ""

# 2. 激活 Conda 环境（如果存在）
if command -v conda &> /dev/null; then
    echo "🔧 激活 Conda 环境..."
    eval "$(conda shell.bash hook)"
    conda activate base || true
    echo "✅ Conda 环境已激活"
    echo ""
fi

# 3. 更新 Python 依赖
echo "📦 更新依赖..."
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r server/requirements.txt --quiet
echo "✅ 依赖已更新"
echo ""

# 4. 运行数据库迁移
echo "🗄️ 运行数据库迁移..."
python scripts/init_db.py
echo "✅ 数据库已同步"
echo ""

# 5. 重启服务
echo "🔄 重启服务..."
if command -v systemctl &> /dev/null && systemctl is-active --quiet magic-conch 2>/dev/null; then
    echo "   使用 systemd 重启服务..."
    sudo systemctl restart magic-conch
    sleep 2

    if systemctl is-active --quiet magic-conch; then
        echo "✅ 服务重启成功"
    else
        echo "❌ 服务重启失败"
        sudo journalctl -u magic-conch -n 20 --no-pager
        exit 1
    fi
else
    echo "⚠️  未检测到 systemd 服务，跳过重启"
fi

echo ""
echo "================================"
echo "🎉 部署完成！"
echo ""

# 输出服务状态
if command -v systemctl &> /dev/null && systemctl is-active --quiet magic-conch 2>/dev/null; then
    echo "📊 服务状态："
    sudo systemctl status magic-conch --no-pager --lines=5 || true
fi

echo ""
echo "⏰ 部署时间: $(date '+%Y-%m-%d %H:%M:%S')"
