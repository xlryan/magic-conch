#!/usr/bin/env bash
# 用于安装基础工具并配置本地环境。Install base tooling and local hooks.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> 安装 Node 与 Python 工具（需要 npm 与 pip）"
echo "==> Installing Node & Python tooling (requires npm and pip)"

if ! command -v npm >/dev/null 2>&1; then
  echo "⚠️ 未检测到 npm，请先安装 Node.js。No npm detected, please install Node.js."
else
  npm install --global markdownlint-cli@0.37.0 markdown-link-check@3.10.3 || {
    echo "⚠️ npm 安装失败，请检查网络或权限。Install failed, check network/permissions."
    exit 1
  }
  echo "✅ 已安装 markdownlint-cli 与 markdown-link-check"
fi

if ! command -v pip >/dev/null 2>&1 && ! command -v pip3 >/dev/null 2>&1; then
  echo "⚠️ 未检测到 pip，请先安装 Python。No pip detected, please install Python."
else
  (pip install --user yamllint==1.32.0 codespell==2.2.6 2>/dev/null || pip3 install --user yamllint==1.32.0 codespell==2.2.6) \
    && echo "✅ 已安装 yamllint 与 codespell"
fi

HOOK_PATH="$ROOT_DIR/.git/hooks/pre-commit"

if [ -d "$ROOT_DIR/.git" ]; then
  cat > "$HOOK_PATH" <<'HOOK'
#!/usr/bin/env bash
# 神奇海螺预提交钩子：在提交前运行基础校验。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ -x "$REPO_ROOT/scripts/check.sh" ]; then
  echo "🔍 运行 scripts/check.sh..."
  "$REPO_ROOT/scripts/check.sh"
else
  echo "⚠️ 未找到 scripts/check.sh，跳过预提交校验。"
fi
HOOK
  chmod +x "$HOOK_PATH"
  echo "✅ 已创建 .git/hooks/pre-commit（如不需要可自定义）。Pre-commit hook installed."
else
  echo "ℹ️ 未检测到 .git 目录，未创建钩子。No .git directory detected; hook not created."
fi

echo "🎉 初始化完成！欢迎开始贡献。Ready to co-create!"
