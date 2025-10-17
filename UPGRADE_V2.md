# 🚀 升级到 V2.0 - 完整功能说明

## ✨ 新增功能总览

### 1. 数据库升级
- ✅ **MySQL 支持**：同时支持 SQLite 和 MySQL
- ✅ **新增表结构**：
  - `likes` - 点赞记录表
  - `entries` 新增审核相关字段（status, submitted_at, reviewed_at, review_note）

### 2. 用户提交功能
- ✅ **在线提交**：用户无需 clone 代码，直接在网页提交项目
- ✅ **表单验证**：完整的前端和后端验证
- ✅ **标签系统**：支持添加多个标签（按 Enter 键添加）
- ✅ **待审核状态**：所有用户提交默认为 `pending` 状态

### 3. 审核工作流
- ✅ **三种状态**：
  - `pending` - 待审核
  - `approved` - 已批准（展示在主页）
  - `rejected` - 已拒绝
- ✅ **管理员审核页面**：`/admin`
- ✅ **审核备注**：管理员可添加审核说明
- ✅ **Token 认证**：使用环境变量 `ADMIN_TOKEN` 保护管理接口

### 4. 点赞功能
- ✅ **点赞/取消点赞**：每个 IP 每条目可点赞一次（可切换）
- ✅ **永久 IP 哈希**：与"踩一脚"不同，点赞使用永久哈希
- ✅ **实时更新**：点赞数实时显示

### 5. 全新设计系统
- ✅ **"夕阳博物馆"主题**：
  - 温暖琥珀色 (#f4a261) - 时光沉淀
  - 柔和薰衣草紫 (#b388eb) - 回忆和梦想
  - 深紫灰背景 (#1a1825) - 优雅不压抑
- ✅ **完整设计令牌**：
  - 颜色系统、间距系统、字体系统
  - 阴影、圆角、过渡动画
- ✅ **组件库**：
  - 按钮（primary/secondary/ghost）
  - 卡片、表单、标签、Toast
  - 排行榜徽章（金/银/铜特效）
- ✅ **响应式设计**：完美支持移动端

### 6. 增强的交互
- ✅ **键盘快捷键**：Ctrl/Cmd + K 聚焦到提交表单
- ✅ **Toast 通知**：成功/错误/信息提示
- ✅ **平滑动画**：卡片悬停、按钮点击、页面滚动
- ✅ **Loading 状态**：所有异步操作都有加载提示

---

## 📊 新增 API 端点

### 用户端点
```
POST /api/submit       - 提交新项目（待审核）
POST /api/like         - 点赞/取消点赞
```

### 管理员端点（需要 X-Admin-Token）
```
GET  /api/admin/pending          - 获取待审核列表
POST /api/admin/review/{id}      - 审核项目（approve/reject）
```

### 更新的端点
```
GET /api/entries       - 现在返回 likes 字段和 status
POST /api/vote         - 现在会检查审核状态
```

---

## 🗄️ 数据库迁移

### 新增表

#### likes 表
```sql
CREATE TABLE likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id VARCHAR(100) NOT NULL,
    ip_hash VARCHAR(64) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_unique_like (entry_id, ip_hash)
);
```

#### entries 表新增字段
```sql
ALTER TABLE entries ADD COLUMN status ENUM('pending','approved','rejected') DEFAULT 'pending';
ALTER TABLE entries ADD COLUMN submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE entries ADD COLUMN reviewed_at DATETIME NULL;
ALTER TABLE entries ADD COLUMN review_note TEXT NULL;
```

---

## 🚀 部署指南

### 方式一：Docker Compose（推荐）

1. **更新环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，设置以下变量：
# - SECRET_KEY（必须）
# - ADMIN_TOKEN（必须）
# - DB_URL（MySQL 或 SQLite）
```

2. **启动服务**
```bash
docker compose up -d
```

MySQL 会自动启动，数据持久化到 `mysql_data` 卷。

### 方式二：本地开发

1. **安装依赖**
```bash
pip install -r server/requirements.txt
```

2. **配置环境**
```bash
cp .env.example .env
# 本地测试使用 SQLite：
# DB_URL=sqlite:///./storage/app.db
```

3. **导入数据**
```bash
python scripts/import_entries.py
```

4. **启动服务**
```bash
uvicorn server.app:app --reload
```

---

## 🔑 环境变量说明

```env
# 必需
SECRET_KEY=your-random-secret-key-here
ADMIN_TOKEN=your-admin-token-here

# 数据库配置
# 选择一种：
DB_URL=sqlite:///./storage/app.db  # SQLite
DB_URL=mysql+pymysql://user:pass@mysql:3306/graveyard  # MySQL

# MySQL 配置（仅 Docker Compose）
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=graveyard
MYSQL_USER=graveyard_user
MYSQL_PASSWORD=graveyard_pass

# 可选
ALLOWED_ORIGINS=*
HCAPTCHA_SECRET=
HCAPTCHA_SITEKEY=
```

---

## 📝 使用流程

### 用户提交项目
1. 访问主页，滚动到"提交你的烂尾项目"
2. 填写表单（所有信息应已脱敏）
3. 添加标签（可选，按 Enter 键添加）
4. 提交后进入待审核状态

### 管理员审核
1. 访问 `/admin`
2. 输入 `ADMIN_TOKEN`
3. 查看待审核列表
4. 点击"批准"或"拒绝"
5. 可选添加审核备注

### 用户互动
- **踩一脚**：每天每条目限 1 次（影响烂尾指数）
- **点赞**：每条目限 1 次，可切换（不影响分数，仅表示支持）
- **查看项目**：点击链接跳转到仓库

---

## 🎨 设计亮点

### 配色方案
- **琥珀色**：温暖、怀旧、时光流逝
- **薰衣草紫**：柔和、梦幻、未完成的美感
- **深紫灰**：优雅、专业、不压抑

### 设计理念
- **温柔而非嘲笑**：柔和的色彩、圆润的边角
- **博物馆感**：玻璃态效果、光晕、沉淀感
- **鼓励而非羞辱**：点赞系统、正向反馈

### 交互细节
- 卡片悬停时顶部渐变条
- 按钮点击波纹效果
- 排行榜前三名特殊徽章（金银铜）
- 平滑的页面滚动和元素定位

---

## 🔒 安全特性

1. **IP 哈希**：不存储明文 IP
   - 踩一脚：`sha256(ip + SECRET_KEY + date)` - 每日更新
   - 点赞：`sha256(ip + SECRET_KEY)` - 永久

2. **防刷机制**：
   - 踩一脚：每天每条目 1 票
   - 点赞：每条目 1 次（可切换）
   - 提交：无限制（靠审核控制）

3. **XSS 防护**：所有用户输入通过 `escapeHtml()` 处理

4. **SQL 注入防护**：使用 SQLAlchemy ORM 参数化查询

5. **CORS 配置**：可通过环境变量限制

---

## 📊 数据模型

### Entry（条目）
```python
{
    "id": "my-project-20250117123456",  # 自动生成
    "title": "我的项目",
    "owner": "开发者名",
    "repo_url": "https://github.com/...",
    "last_commit": "2024-10-01",
    "summary": "项目描述...",
    "tags": "web,app,ai",  # 逗号分隔
    "status": "pending",   # pending/approved/rejected
    "submitted_at": "2025-01-17T12:34:56",
    "reviewed_at": null,
    "review_note": null,
    "votes": 5,            # 计算字段
    "likes": 10,           # 计算字段
    "score": 62            # 计算字段
}
```

---

## 🐛 已知问题与限制

1. **排行榜实时性**：需要手动刷新页面
2. **点赞状态记忆**：刷新页面后不显示是否已点赞（需要额外 API）
3. **统计数据**：管理后台的统计数据尚未实现
4. **批量操作**：管理员需逐个审核

---

## 🎯 未来计划

- [ ] 实时 WebSocket 更新
- [ ] 点赞状态记忆
- [ ] 批量审核操作
- [ ] 导出数据功能
- [ ] 用户头像上传
- [ ] 评论系统
- [ ] 邮件通知（审核结果）

---

## 📦 文件变更清单

### 新增文件
- `public/admin.html` - 管理员审核页面
- `UPGRADE_V2.md` - 本文档

### 重要修改
- `server/app.py` - 完全重写（新增 submit, like, admin 接口）
- `server/models.py` - 新增 Like 表，Entry 表增加审核字段
- `server/schema.py` - 新增多个 Pydantic 模型
- `public/index.html` - 添加提交表单
- `public/main.js` - 完全重写，新增提交、点赞功能
- `public/styles.css` - 完全重写，新设计系统
- `docker-compose.yml` - 添加 MySQL 服务
- `.env.example` - 新增 MySQL 配置
- `server/requirements.txt` - 新增依赖

---

**🎉 升级完成！享受全新的烂尾博物馆体验！**
