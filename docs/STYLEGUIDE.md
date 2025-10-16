# 文档与风格指南 Style Guide

## 写作原则 Writing Principles
- **中文优先，英文简述**：先用中文完整表达，再附英文摘要。  
  Lead with Chinese, follow with concise English.
- **小步快跑、先丢草稿**：允许草稿形态，但需标注 TODO 或 Draft。  
  Drafts are welcome—mark TODO or Draft for clarity.
- **友好、包容、可执行**：强调行动建议，不进行人身批评。  
  Friendly, inclusive, action-oriented tone.

## Markdown 规范 Markdown Conventions
- 一级标题仅用于文档名称，内容从二级标题开始。  
  Use H1 for document title only; content starts at H2.
- 使用有序/无序列表简化双语对照，一行内中英并列。  
  Keep bilingual text on the same line where possible.
- 链接使用内联 `<https://example.com>` 或 `[标题](url)`。  
  Prefer inline links for clarity.

## 代码块与示例 Code Blocks
- 指定语言高亮：` ```bash`、` ```yaml` 等。  
  Specify language hints for code fences.
- 添加必要注释帮助理解上下文。  
  Add minimal comments to clarify context.
- 使用简单示例，必要时链接到完整实现。  
  Keep examples small; link out for full implementations.

## 命名与 slug Naming
- 使用 kebab-case，例如 `magic-metronome.md`。  
  Use kebab-case for file names.
- 分支命名遵循 `CONTRIBUTING.md` 规范。  
  Branch naming per CONTRIBUTING guidelines.

## 图片与资源 Media
- 优先使用矢量或压缩图片，放置于 `docs/assets/`（如需）。  
  Store assets under `docs/assets/` when needed.
- 必须提供版权或来源说明。  
  Credit sources for media.

## 中英术语 Terminology
- 初次出现专业术语，使用“中文（English）”形式。  
  Introduce terms as “中文（English）”.
- 后续可使用英文或缩写，视上下文而定。  
  Later occurrences may use English/abbreviations.

## 评审提示 Review Notes
- 提交前自查：运行 `scripts/check.sh`。  
  Run `scripts/check.sh` before review.
- Reviewer 对语气、结构有建议时，请给出示例修改。  
  Reviewers suggesting tone/structure should offer examples.
