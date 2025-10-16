# ADR-0001: Idea Intake Process | 创意提交流程

- **状态 Status**：Accepted / 已通过  
- **日期 Date**：2024-10-24  
- **作者 Author**：Maintainer 团队 / Maintainer Team

## 背景 Background
神奇海螺需要一个可复制、低门槛的创意提交流程，以确保「先丢草稿」但又能快速收敛到可执行的项目。  
Magic Conch requires a repeatable, low-friction idea intake process that embraces drafts while converging toward actionable projects.

## 决策 Decision
1. 采用 `ideas/_template.md` 作为标准创意卡片模板。  
   Use `ideas/_template.md` as the standard idea card template.
2. Idea 可通过 Issue（🌱 模板）或 PR 提交，皆进入同一评审队列。  
   Ideas arrive via Issues (🌱 template) or PRs and share one review queue.
3. Maintainer/Reviewer 每周评审，结果分为：进入 Proposal、待补充、归档。  
   Weekly reviews classify outcomes: promote to Proposal, needs work, or archive.
4. 通过后复制到 `proposals/` 并指派负责人。  
   Accepted ideas get cloned into `proposals/` with owners.
5. 标签规则：`type:idea` + `status:*` 统一管理进度。  
   Enforce `type:idea` plus `status:*` labels to track progress.

## 备选方案 Alternatives
- 直接使用 Discussions：但难以版本化与追踪变更。  
  Pure Discussions—harder to version and track.
- 使用外部表单/工具：增加维护成本，难以 PR 协作。  
  External forms/tools—higher maintenance, less PR collaboration.

## 影响 Impact
- 有清晰入口与模板，提高可读性与复用度。  
  Clear entry and templates improve readability and reuse.
- 评审节奏固定，便于协作者安排时间。  
  Fixed cadence aids scheduling.
- 模板化可能抬高初次贡献门槛，需在 README 强调“草稿可提交”。  
  Templates may feel heavy; README stresses drafts welcome.

## 后续行动 Follow-ups
- 定期收集使用反馈，必要时调整模板。  
  Gather feedback and iterate templates.
- 为首次贡献者录制填写示例视频（待定）。  
  Record a template walkthrough for newcomers (planned).
- 在 `ROADMAP.md` 中跟踪流程优化任务。  
  Track process improvements in `ROADMAP.md`.
