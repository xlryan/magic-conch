# Graveyard Entry Schema

> 伦理守则：仅提交你拥有版权或已获明确授权的项目，必须彻底脱敏，内容用于学习而非羞辱，可随时改为“复活中”。  
> Ethics first: submit only authorized, sanitized stories; we learn, not roast.

## 字段说明 Field Guide
- `id`：短小写 slug（建议 `kebab-case`），与文件名一致。
- `title`：项目名称，可含副标题。
- `owner`：主要维护者或团队名称，可匿名。
- `license`：适用的分享许可（如 CC-BY-SA-4.0）。
- `repo_url`：原仓库或档案链接，可指向快照。
- `period.start` / `period.end`：项目活跃区间（ISO 日期如 `2020-06`）。若仍在复活，可将 `period.end` 设为 `null` 并在 `comeback_potential` 中说明。
- `last_commit`：最后一次实质提交日期或快照日期。
- `why_failed[]`：造成烂尾的主要原因列表，建议聚焦于上方评分维度。
- `score.{self, reviewer, total}`：整数（0–100），`total = sum(正向项) – comeback_potential`，上下限 0–100。保留投稿者与 reviewer 的评分。
- `comeback_potential`：0–10 的数字，代表还能挽回多少；将被用于扣减总分。
- `lessons[]`：至少一条可复用心得。
- `funny_bits[]`：可选，幽默梗、命名或段子，避免嘲讽真实个体。
- `screenshots[]`：可选列表，元素包含 `title`、`path`（相对仓库路径），可附 `caption`。
- `tags[]`：关键词（如 `scope-creep`、`data-platform`、`mobile`）。
- `consent.confirmed`：布尔值，确认投稿者已阅读并同意伦理条款。
- `consent.contact`：可选，提供 reviewer 私信渠道（如 email alias）。
- `status`：可选，`abandoned` / `reviving` / `archived` 等。
- `sample`：仅示例用，真实投稿请勿保留。

### 评分分解 Scoring Breakdown
| 维度 | 分值 | 说明 |
| --- | --- | --- |
| Scope Creep 过度 | 25 | 范围失控、需求不断加码 |
| 目标漂移 / 需求反复 | 20 | 决策摇摆、不停改目标 |
| 技术债化石（依赖地狱） | 15 | 框架老旧或无法升级 |
| 文档破产（只在脑中） | 10 | 没有可交接的记录 |
| 单点风险（Bus Factor=1） | 10 | 关键知识仅一人掌握 |
| 资金 / 精力蒸发 | 10 | 预算或人力耗尽 |
| 喜剧效果 | 10 | 梗、命名、迷惑行为录 |
| 回春潜力 | −10 | 越有潜力越抵扣，鼓励复活 |

总分上下限 0–100；若计算结果超界，请在 reviewer 校准阶段修正。

## JSON Schema
下面的 JSON Schema 用于 GitHub Action 校验投稿条目：

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Magic Conch Graveyard Entry",
  "type": "object",
  "required": [
    "id",
    "title",
    "owner",
    "license",
    "repo_url",
    "period",
    "last_commit",
    "why_failed",
    "score",
    "comeback_potential",
    "lessons",
    "tags",
    "consent"
  ],
  "additionalProperties": false,
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"
    },
    "title": {
      "type": "string",
      "minLength": 3
    },
    "owner": {
      "type": "string",
      "minLength": 1
    },
    "license": {
      "type": "string",
      "minLength": 1
    },
    "repo_url": {
      "type": "string",
      "format": "uri"
    },
    "period": {
      "type": "object",
      "required": ["start", "end"],
      "additionalProperties": false,
      "properties": {
        "start": {
          "type": "string",
          "pattern": "^\\d{4}(-\\d{2})?$"
        },
        "end": {
          "anyOf": [
            {"type": "string", "pattern": "^\\d{4}(-\\d{2})?$"},
            {"type": "string", "enum": ["ongoing", "reviving"]},
            {"type": "null"}
          ]
        }
      }
    },
    "last_commit": {
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
    },
    "why_failed": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "string",
        "minLength": 6
      }
    },
    "score": {
      "type": "object",
      "required": ["self", "reviewer", "total"],
      "additionalProperties": false,
      "properties": {
        "self": {"type": "integer", "minimum": 0, "maximum": 100},
        "reviewer": {"type": "integer", "minimum": 0, "maximum": 100},
        "total": {"type": "integer", "minimum": 0, "maximum": 100}
      }
    },
    "comeback_potential": {
      "type": "integer",
      "minimum": 0,
      "maximum": 10
    },
    "lessons": {
      "type": "array",
      "minItems": 1,
      "items": {"type": "string", "minLength": 6}
    },
    "funny_bits": {
      "type": "array",
      "items": {"type": "string", "minLength": 3}
    },
    "screenshots": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["title", "path"],
        "additionalProperties": false,
        "properties": {
          "title": {"type": "string", "minLength": 1},
          "path": {"type": "string", "minLength": 1},
          "caption": {"type": "string"}
        }
      }
    },
    "tags": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "string",
        "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"
      }
    },
    "consent": {
      "type": "object",
      "required": ["confirmed"],
      "additionalProperties": false,
      "properties": {
        "confirmed": {"type": "boolean"},
        "contact": {
          "type": "string",
          "minLength": 3
        }
      }
    },
    "status": {
      "type": "string",
      "enum": ["abandoned", "reviving", "archived"]
    },
    "sample": {
      "type": "boolean"
    }
  }
}
```

> 提交 PR 前，请运行 `scripts/generate_leaderboard.py`，确保 README 和徽章同步更新。
