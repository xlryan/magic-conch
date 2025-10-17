# 神奇海螺 · 烂尾博物馆 (Graveyard Museum)

一个极简的「烂尾项目」展览馆，让未完成的项目以有趣的方式被记录和纪念。

## 🎯 核心功能

- **条目展示**：展示各种"烂尾"项目，包括标题、描述、最后活跃时间和当前分数
- **踩一脚**：访客可以为项目投票，每个 IP 每天对每个项目限投 1 票
- **实时排行榜**：根据投票数和停更时间自动计算"烂尾指数"(0-100分)
- **YAML 投稿**：通过提交 YAML 文件添加新项目

## 📊 评分模型

烂尾指数由两部分组成，分数越高越"烂"：

- **群众投票 (V)**：`min(60, round(20 * log2(1 + votes)))`，最高 60 分
- **停更时间 (S)**：`min(40, floor(停更天数 / 7))`，每周 +1 分，最高 40 分
- **总分**：`score = min(100, V + S)`

## 🚀 快速部署

### Docker Compose（推荐）

```bash
cp .env.example .env
# 编辑 .env 文件，设置你的 SECRET_KEY 和 ADMIN_TOKEN
docker compose up -d
```

### 服务器一键部署

适用于 Ubuntu 服务器（2核8G + Conda 环境）：

```bash
git clone https://github.com/xlryan/magic-conch.git
cd magic-conch
bash deploy.sh
```

详细部署文档：[DEPLOY.md](./DEPLOY.md)

### 生产环境更新

当需要更新生产环境时，在服务器上执行：

```bash
cd ~/magic-conch
git pull origin main
pip install -r server/requirements.txt
python scripts/init_db.py
sudo systemctl restart magic-conch
```

> **⚠️ 开源项目安全提示**：不建议在公开仓库中配置 GitHub Actions 自动部署，这会暴露服务器信息。推荐使用私有仓库或手动部署。

### 访问应用

- 主页：`http://localhost:8000`
- 管理后台：`http://localhost:8000/admin`

## 📝 添加新条目

在 `data/entries/` 目录下创建 YAML 文件，例如 `my-project.yml`：

```yaml
id: my-awesome-project
title: 我的超棒项目
owner: Your Name
repo_url: https://github.com/yourname/project
last_commit: 2024-06-15
summary: 这个项目原本计划改变世界，但现在已经停更 XXX 天了...
tags: [web, app, ai]
```

提交后重启容器或调用管理接口：

```bash
curl -X POST http://localhost:8000/api/reload \
  -H "X-Admin-Token: your-admin-token"
```

## 🛠️ 技术栈

- **后端**：Python 3.11 + FastAPI + PostgreSQL/SQLite + SQLAlchemy
- **前端**：原生 HTML + CSS + JavaScript (无框架)
- **容器化**：Docker + Docker Compose
- **极简原则**：最少依赖，最大可维护性

## 🔒 防刷机制

- IP 哈希存储（不保存明文 IP）：`sha256(ip + SECRET_KEY + date)`
- 每个 IP 每天对同一条目仅可投票 1 次
- 可选 hCaptcha 支持（通过环境变量配置）

## ⚖️ 伦理声明

本项目旨在以轻松、有趣的方式记录开发者的创作历程，**绝非羞辱或攻击**：

- 仅收录投稿者本人拥有或已获授权的项目
- 所有信息已脱敏处理
- "烂尾"是开发者的常态，也是成长的一部分
- 我们鼓励重启和完成，而不是嘲笑

## 📂 项目结构

```
.
├── README.md
├── docker-compose.yml
├── .env.example
├── server/                 # 后端代码
│   ├── app.py             # FastAPI 主应用
│   ├── models.py          # 数据库模型
│   ├── schema.py          # Pydantic 模型
│   ├── scoring.py         # 评分算法
│   ├── settings.py        # 配置管理
│   └── requirements.txt
├── public/                # 前端静态文件
│   ├── index.html
│   ├── styles.css
│   └── main.js
├── data/
│   └── entries/          # YAML 条目文件
│       ├── sample-quaver.yml
│       └── sample-datalens.yml
├── scripts/
│   └── import_entries.py # 数据导入脚本
└── storage/              # SQLite 数据库（运行时生成）
    └── .gitkeep
```

## 🔧 本地开发

### 不使用 Docker

```bash
# 1. 安装依赖（使用清华镜像加速）
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r server/requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 使用 SQLite: DB_URL=sqlite:///./storage/app.db

# 3. 初始化数据库
python scripts/init_db.py

# 4. 导入数据
python scripts/import_entries.py

# 5. 启动服务
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

> **提示**：国内用户推荐配置 pip 镜像源以加速下载：
> ```bash
> pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
> ```

## 📡 API 接口

- `GET /api/entries` - 获取所有条目（含实时评分）
- `POST /api/vote` - 为条目投票 `{entry_id: "xxx"}`
- `POST /api/reload` - 重新加载条目（需要 Admin Token）

## 📜 开源协议

MIT License

---

**神奇海螺说**：*烂尾不可怕，可怕的是不敢开始。*
