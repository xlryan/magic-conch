# 贡献指南 CONTRIBUTING

感谢你加入神奇海螺！我们相信「小步快跑、先丢草稿」，欢迎以低门槛的方式尝试或提问。  
Thank you for joining Magic Conch! We live by “ship drafts fast”; every question is welcome.

## 快速索引 Quick Index
- [文化与期待 Culture & Expectations](#文化与期待-culture--expectations)
- [准备工作 Before You Start](#准备工作-before-you-start)
- [流程总览 Idea → Proposal → Project](#流程总览-idea--proposal--project)
- [提交 Idea Submit an Idea](#提交-idea-submit-an-idea)
- [评审节奏 Review Cadence](#评审节奏-review-cadence)
- [任务拆解 Task Breakdown](#任务拆解-task-breakdown)
- [分支命名 Branch Naming](#分支命名-branch-naming)
- [提交信息 Commit Messages](#提交信息-commit-messages)
- [代码与文档风格 Style](#代码与文档风格-style)
- [Issue 流程 Issue Workflow](#issue-流程-issue-workflow)
- [PR 流程 Pull Request Workflow](#pr-流程-pull-request-workflow)
- [评审标准 Review Checklist](#评审标准-review-checklist)
- [沟通频道 Communication](#沟通频道-communication)
- [常见问题 FAQ](#常见问题-faq)

## 文化与期待 Culture & Expectations
- 尊重彼此的时间与节奏，明确可交付物与反馈窗口。  
  Respect each other’s time; clarify deliverables and response windows.
- 鼓励 “草稿优先”，不会嘲笑未完成的想法。  
  Draft-first culture—no shaming unfinished thoughts.
- 所有讨论默认公开，可在 ADR/记录中沉淀。  
  Default to open discussions and documented decisions.

## 准备工作 Before You Start
1. 克隆仓库并运行 `scripts/setup.sh` 安装工具。  
   Clone the repo and run `scripts/setup.sh` to install tooling.
2. 阅读 `README.md`、`VISION.md` 与 `docs/STYLEGUIDE.md`。  
   Read `README.md`, `VISION.md`, and `docs/STYLEGUIDE.md`.
3. 若发现行为准则风险，请写信 `conduct@magic-conch.dev`。  
   Email `conduct@magic-conch.dev` for conduct concerns.

## 流程总览 Idea → Proposal → Project
- **Idea**：提交创意卡片，聚焦问题与洞察。  
  Submit idea cards focused on problems and insights.
- **Proposal**：经评审后形成立项提案，明确范围与资源。  
  Approved ideas become proposals with scope and resources.
- **Project**：确认执行团队、版本计划与复盘机制。  
  Projects track execution, releases, and retros.

## 提交 Idea Submit an Idea
1. 复制 `ideas/_template.md`，填写字段（中文优先，英文简述）。  
   Copy `ideas/_template.md` and fill it bilingually.
2. 选择以下任一途径：  
   Use one of the following paths:
   - 打开 Issue，选择 “🌱 Idea Proposal | 创意提交” 模板。  
     Open an Issue with the “🌱 Idea Proposal” template.
   - 或直接提交 PR，将文件放在 `ideas/`（建议子目录或 `samples/`）。  
     Or open a PR adding the file under `ideas/`.
3. 使用标签 `type:idea`，Maintainer 会补充 `status:triage`。  
   Apply `type:idea`; maintainers add `status:triage`.
4. 欢迎附上参考链接、原型草图或数据片段。  
   Attach references, sketches, or data when possible.

## 评审节奏 Review Cadence
- Maintainer/Reviewer 每周一次同步，公开记录决议。  
  Maintainers/reviewers host weekly syncs with public notes.
- 被采纳的 idea 会迁移/复制到 `proposals/`，并指派负责人。  
  Accepted ideas move to `proposals/` with owners assigned.
- 未通过的 idea 将给出改进建议或放入 “回收池”。  
  Declined ideas receive feedback or move to a parking lot.

## 任务拆解 Task Breakdown
- 将大型目标拆分为可在 1-2 周内完成的任务。  
  Break work into 1–2 week tasks.
- 在 `projects/_template.md` 的任务看板部分记录链接。  
  Track task boards via the project template.
- 使用标签 `help-wanted` 寻找协作者。  
  Use `help-wanted` to invite collaborators.

## 分支命名 Branch Naming
| 类型 Type | 示例 Example | 说明 Description |
| --- | --- | --- |
| Idea | `idea/voice-storybook` | Idea 草稿或模板更新 / Idea drafts or template updates |
| Feature | `feat/frontend/123-magic-metronome` | 新功能 / new feature implementation |
| Fix | `fix/docs/typo-metro` | 修复或改写 / bugfix or doc tweak |

## 提交信息 Commit Messages
- 采用 Conventional Commits，例：`feat: add idea intake checklist`。  
  Use Conventional Commits, e.g., `feat: add idea intake checklist`.
- 中文可以写在正文，首行建议英文动词。  
  Use English verbs on the subject line; add Chinese context in body.
- 合并前请确保 `scripts/check.sh` 通过。  
  Run `scripts/check.sh` before merging.

## 代码与文档风格 Style
- Markdown：参照 `docs/STYLEGUIDE.md` 的标题结构与中英对照规范。  
  Follow `docs/STYLEGUIDE.md` for Markdown structure and bilingual style.
- 代码片段：优先使用简洁示例并加注释。  
  Keep code examples minimal with clarifying comments.
- 文案语气：友好、包容，鼓励草稿、避免门槛。  
  Friendly, inclusive tone that encourages drafts.

## Issue 流程 Issue Workflow
- 选择合适模板：Idea / Feature / Bug。  
  Pick the right template: Idea, Feature, or Bug.
- 填写完成度 >70% 方能进入评审列表。  
  Aim for 70% completeness before review.
- 为完成的 Issue 添加 `status:done` 并关闭。  
  Close completed issues with `status:done`.

## PR 流程 Pull Request Workflow
1. 从 `main` 创建分支，保持小粒度提交。  
   Branch from `main` and keep commits small.
2. 在 PR 中填写动机、变更类型与测试情况（模板已提供）。  
   Complete the PR template: motivation, change type, tests.
3. 请求至少 1 名 Reviewer 审阅；核心变更需 2 名。  
   Request ≥1 reviewer; core changes need two.
4. CI 通过且 checklist 完成后方可合并。  
   Merge only when CI passes and checklist is complete.
5. 合并后更新相关 Issue/Project 状态。  
   Update relevant issues/project boards post-merge.

## 评审标准 Review Checklist
- 是否遵守模板、流程与命名规范？  
  Templates, process, and naming rules followed?
- 是否通过 `scripts/check.sh` 与 CI？  
  Did it pass `scripts/check.sh` and CI?
- 是否清晰说明动机、影响范围与回滚方案？  
  Motivation, impact, rollback covered?
- 是否更新文档/ADR/Changelog（如适用）？  
  Docs/ADR/changelog updated when applicable.

## 沟通频道 Communication
- GitHub Discussions（Ideas/Q&A/Show and Tell）。  
  Use Discussions for ideas, Q&A, and show-and-tell.
- Discord/Matrix（筹建中）欢迎自我介绍。  
  Join future chat spaces to introduce yourself.
- 邮件列表：若需订阅核心决议，请关注 `maintainers@magic-conch.dev`。  
  Subscribe to `maintainers@magic-conch.dev` for governance updates.

## 常见问题 FAQ
- **我没有代码经验怎么办？** 文档、调研、测试、主持工作坊都很需要你。  
  *Not a coder?* Docs, research, testing, and facilitation are welcome.
- **Idea 会被拒绝吗？** 可能，但我们会说明原因并给出改进建议。  
  *Can ideas be declined?* Yes, with constructive feedback.
- **如何成为 Reviewer？** 持续贡献并协助评审，Maintainer 每季度评估候选人。  
  *Become a reviewer?* Consistently contribute and co-review; maintainers assess quarterly.
