# 轻量治理 Governance

## 角色 Roles
- **Maintainer（维护人）**：引导方向、合并关键 PR、主持季度回顾。 Maintainers steer direction, merge key PRs, and host quarterly reviews.
- **Reviewer（评审人）**：主持 Idea/Proposal 评估，协助质量把关。 Reviewers lead evaluations and guard quality.
- **Contributor（贡献者）**：提交创意、补充文档、实现任务。 Contributors submit ideas, docs, and code.

## 责任与权限 Responsibilities
- Maintainer：维护路线图、指定 reviewer、处理冲突升级。 Maintainers own the roadmap, assign reviewers, and resolve escalations.
- Reviewer：在 5 个工作日内反馈 Issue/PR，提供可行动建议。 Reviewers respond within five business days with actionable feedback.
- Contributor：遵守行为准则与模板，主动同步进度。 Contributors follow the Code of Conduct, templates, and communicate progress.

## 决策机制 Decision Process
- 默认采用开放讨论与 Lazy Consensus（72 小时无人反对即通过）。  
  Default to open discussion with 72h lazy consensus.
- 若存在强烈分歧，由 Maintainer 发起投票（简单多数制，至少 3 人参与）。  
  Maintainers call a simple-majority vote with ≥3 participants when conflict persists.
- 战略级决策（路线图、治理调整）需 2/3 Maintainer 赞成。  
  Strategic changes need two-thirds maintainer approval.

## 冲突处理 Conflict Resolution
1. 当事人在 Issue/PR 公开讨论并记录要点。  
   Parties first discuss in Issues/PRs and document key points.
2. 无法达成共识时，@ 指定 Reviewer 协调。  
   Ping a reviewer to mediate if consensus fails.
3. 再次僵持则由 Maintainer 小组最终裁决并更新 ADR。  
   Maintainers adjudicate and log the outcome in an ADR.

## 投票与共识 Voting & Consensus
- 投票需提供清晰选项、背景与截止时间。  
  Votes must state options, context, and deadlines.
- 结果在 24 小时内公示并链接至对应 Issue/ADR。  
  Publish results within 24h and link to the Issue/ADR.
- 未通过提案需附带改进建议或复盘计划。  
  Failed proposals must include improvement suggestions or retros.

## 透明度 Transparency
- 治理讨论优先在 Discussions 或 `docs/DECISION_RECORDS/` 记录。  
  Capture governance conversations in Discussions or ADRs.
- 私下沟通（含安全事件）在风险解除后递交总结。  
  Summaries of private discussions (incl. security) follow once resolved.

## 任期与继任 Succession
- Maintainer 每年自评是否继续担任，可自愿交接。  
  Maintainers annually self-assess and may hand off.
- 新 Maintainer 须由现有成员提名并经 2/3 投票通过。  
  New maintainers require nomination plus two-thirds approval.
- Reviewer 采用 6 个月轮值，可提前退出。  
  Reviewers rotate every six months and may opt out early.

## 社区扩展 Community Growth
- 鼓励成立兴趣小组（SIG）按主题推进，需 Maintainer 备案。  
  Theme-based SIGs are welcome with maintainer awareness.
- 外部合作（赞助/联合活动）需至少两位 Maintainer 共同批准。  
  External partnerships require approval from two maintainers.
