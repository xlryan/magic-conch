#!/bin/bash
# 配置 CI/CD 所需的 sudo 权限

set -e

echo "🔧 配置 GitHub Actions CI/CD 权限"
echo "=================================="

CURRENT_USER=$(whoami)

echo "📋 当前用户: $CURRENT_USER"
echo ""
echo "⚠️  此脚本将配置以下 sudo 权限（无需密码）："
echo "   - systemctl restart magic-conch"
echo "   - systemctl status magic-conch"
echo "   - systemctl is-active magic-conch"
echo "   - journalctl"
echo ""

read -p "是否继续？[y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 0
fi

# 创建 sudoers 配置文件
SUDOERS_FILE="/etc/sudoers.d/magic-conch-$CURRENT_USER"

echo ""
echo "📝 创建 sudoers 配置..."

sudo tee "$SUDOERS_FILE" > /dev/null << EOF
# Magic Conch CI/CD Permissions
# User: $CURRENT_USER
# Created: $(date)

$CURRENT_USER ALL=(ALL) NOPASSWD: /bin/systemctl restart magic-conch
$CURRENT_USER ALL=(ALL) NOPASSWD: /bin/systemctl status magic-conch
$CURRENT_USER ALL=(ALL) NOPASSWD: /bin/systemctl is-active magic-conch
$CURRENT_USER ALL=(ALL) NOPASSWD: /bin/journalctl
EOF

# 设置正确的权限
sudo chmod 0440 "$SUDOERS_FILE"

# 验证配置
echo ""
echo "🔍 验证配置..."
if sudo visudo -c -f "$SUDOERS_FILE"; then
    echo "✅ Sudoers 配置验证成功"
else
    echo "❌ 配置文件有错误，已删除"
    sudo rm -f "$SUDOERS_FILE"
    exit 1
fi

# 测试权限
echo ""
echo "🧪 测试权限..."

if sudo systemctl is-active --quiet magic-conch 2>/dev/null; then
    echo "✅ 测试通过: sudo systemctl is-active magic-conch"
else
    echo "⚠️  服务未运行，但权限配置正确"
fi

echo ""
echo "=================================="
echo "✅ 权限配置完成！"
echo ""
echo "📋 配置文件: $SUDOERS_FILE"
echo ""
echo "🧪 测试命令："
echo "   sudo systemctl restart magic-conch"
echo "   sudo systemctl status magic-conch"
echo "   sudo journalctl -u magic-conch -n 10"
echo ""
echo "🔄 下一步："
echo "   1. 配置 GitHub Secrets (见 .github/DEPLOY_SETUP.md)"
echo "   2. Push 代码到 main 分支测试自动部署"
echo ""
