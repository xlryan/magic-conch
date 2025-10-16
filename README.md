# Magic Conch – Museum of Unfinished 神奇海螺·烂尾博物馆

![Graveyard Leaderboard](https://img.shields.io/badge/Graveyard-Top%2010%20Pending-8f14e45f?logo=github&labelColor=232323&color=ff5d73)
![Opt-In Ethics](https://img.shields.io/badge/Consented-Yes-44cc11)

> 🐚 "神奇海螺，有个项目烂尾了怎么办？" —— "把它好好写进博物馆。"  
> We celebrate unfinished business with kindness, humor, and useful retros.

## 项目定位 Project Focus
- 收集个人或授权团队的**烂尾 / 搁置项目复盘**，像逛展一样读懂失败背后的条件反射。  
  A curated hall of famously unfinished experiments, with respectful post-mortems.
- 用幽默但不尖刻的角度记录“失败档案”，帮助后来人少踩雷。  
  Laugh with—not at—the mess, so the next crew avoids repeating it.
- 由投稿者提供自述，社区 reviewer 协助校准评分与伦理审查。  
  Authors self-report; reviewers calibrate scores and check ethics.

## 如何投稿 Submission Walkthrough
1. Fork 本仓库，创建分支。Fork the repo and branch out.
2. 新建 `graveyard/entries/<slug>.yml`（按 schema 填写），资源请放进 `graveyard/assets/<slug>/`。  
   Add your YAML entry per schema and stash sanitized assets alongside it.
3. 在 PR 中附带预览（可运行 `python scripts/generate_leaderboard.py`），并勾选投稿 Issue 模板。  
   Run the leaderboard script locally before opening the PR.
4. Reviewer 会执行 `validate-entry` 工作流：校验 JSON Schema、检查敏感词、对齐评分。  
   The workflow enforces schema, linting, and basic redaction checks.
5. 通过后，你的项目将出现在排行榜与徽章页；若复活进展，请更新评分或改标记为 “复活中”。

更多细节与行为准则：请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

## 评分摘要 Scoring TL;DR (0–100，越高越烂)
| 项目坑点 | 分值 | 英文提示 |
| --- | --- | --- |
| Scope Creep 过度 | 25 | Scope creep overload |
| 目标漂移 / 需求反复 | 20 | Pivot mania |
| 技术债化石（依赖地狱） | 15 | Fossilized tech debt |
| 文档破产（知识只在脑中） | 10 | Docs bankruptcy |
| 单点风险（Bus Factor = 1） | 10 | Single point of failure |
| 资金 / 精力蒸发 | 10 | Burnout or funding void |
| 喜剧效果（梗图 / 梗命名） | 10 | Comedy factor |
| 回春潜力抵扣 | −10 | Comeback potential offset |

> **总分 = Σ(正向项) – 回春潜力**，上限 100，下限 0。投稿者自评，Reviewer 校准；两者并列展示。

## 伦理与授权 Ethics & Consent
- 仅收录投稿者本人拥有版权或已获明确授权的项目。  
  Submit only what you have rights to share.
- 必须脱敏：密钥、隐私数据、公司机密请删除或匿名化。  
  Redact secrets, personal info, and corporate IP.
- 尊重所有贡献者署名与许可证，不以羞辱为目的。  
  Credit collaborators and avoid punch-down humor.
- 可随时将“烂尾”条目更新为“复活中”，保留历史评分便于对照。  
  You may flip status to "resurrecting" while keeping historical scores.

## 排行榜 Top 10 Graveyards
排行榜由脚本自动生成，含回春抵扣提醒。若手动修改，本地脚本会覆盖。

<!-- LEADERBOARD:START -->
| 排名 | 项目 | 自评 / Reviewer | 总分 (越烂越高) | 回春潜力 | 标签 |
| --- | --- | --- | --- | --- | --- |
| 1 | **DataLens 元数据放大镜：设计开到宇宙但忘了起步 (Sample)**<br/><small>洞察未遂研究所 / Insight Almost Works</small><br/><code>abandoned</code> | 88 / 91 | 94 | 2/10 | data-platform, metadata, access-control |
| 2 | **Quaver 多端重构：声波未到，需求先炸 (Sample)**<br/><small>浮夸节拍工作室 / Exaggerated Beat Studio</small><br/><code>abandoned</code> | 78 / 82 | 84 | 4/10 | scope-creep, audio, electron |
<!-- LEADERBOARD:END -->

## 从烂尾到复活 Comeback Corner
- `comeback_potential` 字段越高，回春抵扣越大，排行榜会展示原始坑点与潜在转机。  
  Higher comeback scores mean stronger revival chances and lower total.
- 可在 `graveyard/entries/<slug>.yml` 中补充复活计划、资源、看板链接。  
  Add revival plans, resources, or project boards as you reboot.
- 欢迎把条目迁移到独立的“复活追踪”文档，并在 README 中分享救赎故事。  
  Graduated stories are welcome—tell us how you brought it back.

## 自动化工具链 Automation
- `scripts/generate_leaderboard.py`：解析所有条目，更新 README Top 10 与 `badges/README-badges.md`。  
  Keeps leaderboards and badges fresh.
- `.github/workflows/validate-entry.yml`：每次 PR 校验条目结构、分值范围与敏感词。  
  Validates schema, field completeness, and redaction hints.
- `.github/workflows/leaderboard.yml`：合并后自动重跑脚本并提交排行榜更新。  
  Auto-regenerates leaderboard post-merge using `GITHUB_TOKEN`.

## 看板与社区 Boards & Community
- 建议将 GitHub Projects 设为「复活追踪」看板，挂接 `type:grave` 与 `comeback?` 标签。  
  Spin up a GitHub Project view filtered by the graveyard labels.
- 标签速览： `type:grave`、`status:triage`、`needs:schema-fix`、`ethics:check`、`comeback?`。  
  Check `.github/labels.yml` for full label docs.
- 讨论区保留原有节奏：欢迎用幽默又负责任的方式分享经验。  
  Humor is welcome; malice is not.

## 延伸阅读 More Docs
- [CONTRIBUTING.md](CONTRIBUTING.md) – 投稿与评审流程
- [GOVERNANCE.md](GOVERNANCE.md) – 治理 / Governance model
- [SECURITY.md](SECURITY.md) – 安全报告渠道
- [VISION.md](VISION.md) & [ROADMAP.md](ROADMAP.md) – 原始愿景与演进纪要

欢迎来到神奇海螺的烂尾博物馆，愿你的翻车故事照亮别人的夜航灯。  
May every stalled dream become someone else's lighthouse.
