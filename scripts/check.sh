#!/usr/bin/env bash
# 汇总 Markdown 链接、拼写与 YAML 校验。All-in-one local checks.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export PATH="$HOME/.local/bin:$PATH"

echo "==> Markdown Lint / Markdown 格式检查"
if command -v markdownlint >/dev/null 2>&1; then
  markdownlint "**/*.md" --ignore "node_modules" || {
    echo "❌ markdownlint 失败"; exit 1;
  }
else
  npx --yes markdownlint-cli@0.37.0 "**/*.md" --ignore "node_modules" || {
    echo "❌ markdownlint 失败"; exit 1;
  }
fi

echo
echo "==> Markdown Link Check / Markdown 链接校验"
find . -name "node_modules" -prune -o -name "*.md" -print0 | \
  while IFS= read -r -d '' file; do
    echo "🔗 Checking $file"
    if ! markdown-link-check --quiet "$file"; then
      echo "❌ 链接校验失败：$file"; exit 1;
    fi
  done

echo
echo "==> Spell Check / 拼写检查（codespell）"
if command -v codespell >/dev/null 2>&1; then
  codespell --ignore-words-list=conch,metronome --skip="./.git,./node_modules" --quiet-level=2
else
  echo "⚠️ 未安装 codespell，跳过拼写检查。Install codespell to enable spell checks."
fi

echo
echo "==> YAML Lint / YAML 校验"
if command -v yamllint >/dev/null 2>&1; then
  yamllint .
else
  echo "⚠️ 未安装 yamllint，跳过 YAML 校验。Install yamllint to enable YAML linting."
fi

echo
echo "✅ 所有检查完成 / All checks finished."
