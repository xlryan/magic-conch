# 项目文件清单

## ✅ 已生成的完整文件列表

### 📋 配置文件
- ✅ `README.md` - 项目说明文档
- ✅ `.env.example` - 环境变量示例
- ✅ `.env` - 环境变量配置（已从示例复制）
- ✅ `.gitignore` - Git 忽略规则
- ✅ `Dockerfile` - Docker 镜像构建文件
- ✅ `docker-compose.yml` - Docker Compose 编排文件

### 🐍 后端代码 (`server/`)
- ✅ `server/__init__.py` - 包初始化文件
- ✅ `server/requirements.txt` - Python 依赖清单
- ✅ `server/settings.py` - 应用配置管理
- ✅ `server/models.py` - SQLAlchemy 数据库模型
- ✅ `server/schema.py` - Pydantic 数据模型
- ✅ `server/scoring.py` - 评分算法实现
- ✅ `server/app.py` - FastAPI 主应用

### 🎨 前端文件 (`public/`)
- ✅ `public/index.html` - 主页面
- ✅ `public/styles.css` - 样式表
- ✅ `public/main.js` - 前端交互逻辑

### 📊 示例数据 (`data/entries/`)
- ✅ `data/entries/sample-quaver.yml` - Quaver 音乐助手示例
- ✅ `data/entries/sample-datalens.yml` - DataLens 数据中台示例

### 🔧 脚本 (`scripts/`)
- ✅ `scripts/import_entries.py` - YAML 数据导入脚本

### 📦 存储目录 (`storage/`)
- ✅ `storage/.gitkeep` - 保留目录结构（数据库运行时生成）

---

## 🚀 快速开始

### 方式一：使用 Docker（推荐）

```bash
# 1. 启动服务
docker compose up -d

# 2. 查看日志
docker compose logs -f

# 3. 访问应用
open http://localhost:8000
```

### 方式二：本地运行

```bash
# 1. 安装依赖
pip install -r server/requirements.txt

# 2. 导入数据
python scripts/import_entries.py

# 3. 启动服务
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload

# 4. 访问应用
open http://localhost:8000
```

---

## 📡 API 端点

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | `/` | 返回前端页面 | - |
| GET | `/api/entries` | 获取所有条目（含实时评分） | - |
| POST | `/api/vote` | 为条目投票 | `{entry_id: "xxx"}` |
| POST | `/api/reload` | 重新加载条目 | Header: `X-Admin-Token` |
| GET | `/health` | 健康检查 | - |

---

## 🎯 功能验收清单

### ✅ 核心功能
- [x] 展示项目列表（标题、描述、最后活跃时间、分数）
- [x] "踩一脚"投票按钮
- [x] 实时排行榜（按分数降序）
- [x] 评分模型实现（投票分 0-60 + 停更分 0-40）

### ✅ 防刷机制
- [x] IP 哈希存储（不保存明文 IP）
- [x] 每个 IP 每天每条目限投 1 票
- [x] 投票失败返回友好错误信息

### ✅ 技术实现
- [x] Python 3.11 + FastAPI
- [x] SQLite + SQLAlchemy
- [x] 原生 HTML/CSS/JS（无框架）
- [x] Docker + Docker Compose 一键部署
- [x] YAML 文件投稿系统

### ✅ 用户体验
- [x] 响应式设计（移动端友好）
- [x] 暗色主题 + 暖橙色点缀
- [x] 加载状态提示
- [x] 投票成功/失败 Toast 提示
- [x] 按钮防抖（2秒冷却）

---

## 📐 评分公式

```python
# 投票分数 (0-60)
V = min(60, round(20 * log2(1 + votes)))

# 停更分数 (0-40)
S = min(40, floor(days_since_last_commit / 7))

# 总分 (0-100)
score = min(100, V + S)
```

---

## 🔐 安全特性

1. **IP 哈希**：`sha256(ip + SECRET_KEY + date)` - 不存储明文 IP
2. **CORS 配置**：可通过环境变量限制允许的域名
3. **管理接口保护**：`/api/reload` 需要 Admin Token
4. **XSS 防护**：前端使用 `textContent` 避免 HTML 注入
5. **SQL 注入防护**：使用 SQLAlchemy ORM 参数化查询

---

## 📝 添加新条目

在 `data/entries/` 创建 YAML 文件：

```yaml
id: my-project
title: 我的项目
owner: Your Name
repo_url: https://github.com/yourname/project
last_commit: 2024-10-01
summary: 项目描述...
tags: [web, app]
```

然后重启容器或调用：

```bash
curl -X POST http://localhost:8000/api/reload \
  -H "X-Admin-Token: your-admin-token"
```

---

## 🛠️ 技术栈详情

### 后端依赖
- `fastapi==0.109.0` - Web 框架
- `uvicorn[standard]==0.27.0` - ASGI 服务器
- `sqlalchemy==2.0.25` - ORM
- `pydantic==2.5.3` - 数据验证
- `pydantic-settings==2.1.0` - 配置管理
- `pyyaml==6.0.1` - YAML 解析
- `python-multipart==0.0.6` - 表单数据处理

### 前端技术
- 原生 HTML5
- 原生 CSS3（CSS Grid + Flexbox）
- 原生 JavaScript（ES6+）
- Fetch API

### 数据库
- SQLite 3
- 两张表：`entries`（条目）、`votes`（投票）

---

## 📊 数据库结构

### entries 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | STRING (PK) | 条目唯一标识 |
| title | STRING | 项目标题 |
| owner | STRING | 所有者 |
| repo_url | STRING | 仓库链接 |
| last_commit | DATE | 最后提交日期 |
| summary | STRING | 项目简介 |
| tags | STRING | 标签（逗号分隔） |

### votes 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER (PK) | 自增主键 |
| entry_id | STRING | 条目 ID |
| vote_date | DATE | 投票日期 |
| ip_hash | STRING | IP 哈希 |

**唯一索引**：`(entry_id, vote_date, ip_hash)`

---

## 🎨 设计规范

### 颜色变量
```css
--color-bg: #1a1a1a          /* 背景 */
--color-bg-card: #252525     /* 卡片背景 */
--color-text: #e0e0e0        /* 文字 */
--color-primary: #ff6b35     /* 主题色（暖橙） */
```

### 响应式断点
- 移动端：< 768px（单列布局）
- 桌面端：≥ 768px（2列布局）

---

## ⚖️ 伦理声明

本项目遵循以下原则：

1. **仅收录授权内容**：投稿者必须拥有项目版权或已获明确授权
2. **必须脱敏**：删除密钥、隐私数据、公司机密
3. **尊重贡献者**：保留署名，不以羞辱为目的
4. **鼓励复活**：可随时更新状态为"复活中"

---

## 📄 许可证

MIT License

---

**神奇海螺说**：*烂尾不可怕，可怕的是不敢开始。*
