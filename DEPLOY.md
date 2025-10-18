# 🚀 服务器快速部署指南

适用于全新的 Ubuntu 服务器（2核8G + Conda 环境）

---

## 📋 前置要求

- Ubuntu 18.04+ 服务器
- 已安装 Conda 环境
- Git 已安装
- 可访问的 8000 端口

---

## 🎯 方式一：一键部署（推荐）

### 1. 克隆项目

```bash
cd ~
git clone https://github.com/xlryan/magic-conch.git
cd magic-conch
```

### 2. 运行部署脚本

```bash
bash deploy.sh
```

脚本会自动完成：
- ✅ 安装 Python 依赖（使用清华镜像）
- ✅ 生成 `.env` 配置文件
- ✅ 生成随机的 SECRET_KEY 和 ADMIN_TOKEN
- ✅ 初始化 SQLite 数据库
- ✅ 导入示例数据（如果有）

### 3. 启动服务

**开发模式（自动重载）：**
```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

**生产模式（多进程）：**
```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 2
```

**后台运行（nohup）：**
```bash
nohup uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 2 > app.log 2>&1 &
```

### 4. 访问应用

```
主页：http://YOUR_SERVER_IP:8000
管理后台：http://YOUR_SERVER_IP:8000/admin
```

### 5. 查看管理员 Token

```bash
cat .env | grep ADMIN_TOKEN
```

---

## 🔧 方式二：手动部署

### 1. 安装依赖

```bash
# 激活 Conda 环境
conda activate base  # 或你的环境名

# 安装 Python 包（使用清华镜像）
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r server/requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置
nano .env
```

修改以下内容：
```env
# 生成随机密钥（重要！）
SECRET_KEY=your-random-64-char-string-here

# 设置管理员 Token（保密！）
ADMIN_TOKEN=your-admin-token-here

# 数据库（SQLite 即可）
DB_URL=sqlite:///./storage/app.db
```

生成随机密钥：
```bash
# SECRET_KEY (64字符)
openssl rand -hex 32

# ADMIN_TOKEN (32字符)
openssl rand -hex 16
```

### 3. 初始化数据库

```bash
# 创建目录
mkdir -p storage data/entries

# 初始化表结构
python scripts/init_db.py

# 导入示例数据（可选）
python scripts/import_entries.py
```

### 4. 启动服务

```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 2
```

---

## 🐳 方式三：Docker Compose（可选）

如果服务器安装了 Docker：

```bash
# 配置环境变量
cp .env.example .env
nano .env  # 修改 SECRET_KEY 和 ADMIN_TOKEN

# 启动服务（包含 PostgreSQL）
docker compose up -d

# 查看日志
docker compose logs -f app
```

---

## 🔐 使用 Systemd 管理服务（推荐生产环境）

### 1. 编辑服务文件

```bash
nano magic-conch.service
```

修改以下内容：
```ini
User=YOUR_USERNAME                                    # 你的用户名
WorkingDirectory=/home/YOUR_USERNAME/magic-conch      # 项目路径
Environment="PATH=/home/YOUR_USERNAME/miniconda3/bin:..." # Conda 路径
ExecStart=/home/YOUR_USERNAME/miniconda3/bin/uvicorn ...  # uvicorn 路径
```

查找 Conda 路径：
```bash
which conda
# 输出类似：/home/username/miniconda3/bin/conda
```

### 2. 创建日志目录

```bash
sudo mkdir -p /var/log/magic-conch
sudo chown $USER:$USER /var/log/magic-conch
```

### 3. 安装并启动服务

```bash
# 复制服务文件
sudo cp magic-conch.service /etc/systemd/system/

# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start magic-conch

# 开机自启
sudo systemctl enable magic-conch

# 查看状态
sudo systemctl status magic-conch
```

### 4. 管理服务

```bash
# 查看日志
sudo journalctl -u magic-conch -f

# 重启服务
sudo systemctl restart magic-conch

# 停止服务
sudo systemctl stop magic-conch
```

---

## 🌐 配置 Nginx 反向代理（可选）

### 1. 安装 Nginx

```bash
sudo apt update
sudo apt install nginx -y
```

### 2. 创建配置文件

```bash
sudo nano /etc/nginx/sites-available/magic-conch
```

添加以下内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名或 IP

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/magic-conch /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

### 4. 配置 HTTPS（推荐）

#### 方式 A：一键配置（推荐）

使用自动化脚本配置多域名 SSL 证书和自动续期：

```bash
# 运行 SSL 配置脚本
bash scripts/setup_ssl.sh
```

脚本会自动完成：
- ✅ 检查并安装 Certbot
- ✅ 验证域名 DNS 解析
- ✅ 为所有域名申请 SSL 证书（jam.lesstk.com, lesstk.com, dev.lesstk.com, conch.lesstk.com）
- ✅ 配置自动续期（每天检查两次）
- ✅ 配置续期后自动重载 Nginx
- ✅ 生成 Nginx SSL 配置示例

#### 方式 B：手动配置

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书（单个域名）
sudo certbot --nginx -d your-domain.com

# 获取证书（多个域名）
sudo certbot --nginx -d domain1.com -d domain2.com -d domain3.com

# 测试自动续期
sudo certbot renew --dry-run

# 查看证书信息
sudo certbot certificates

# 查看自动续期定时任务
sudo systemctl list-timers | grep certbot
```

---

## 📊 性能优化建议

### 1. Worker 进程数

```bash
# 2核8G 建议 2-4 个 worker
uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 2
```

### 2. 使用 PostgreSQL（可选）

如果数据量大，推荐切换到 PostgreSQL：

```bash
# 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# 创建数据库
sudo -u postgres psql
CREATE DATABASE graveyard;
CREATE USER graveyard_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE graveyard TO graveyard_user;
\q

# 修改 .env
DB_URL=postgresql+psycopg2://graveyard_user:your_password@localhost:5432/graveyard
```

### 3. 启用 Gzip 压缩（Nginx）

在 Nginx 配置中添加：
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_min_length 1000;
```

---

## 🐛 常见问题

### 1. 端口被占用

```bash
# 查看占用进程
sudo lsof -i :8000

# 杀死进程
sudo kill -9 PID
```

### 2. 数据库初始化失败

```bash
# 删除旧数据库
rm -f storage/app.db

# 重新初始化
python scripts/init_db.py
```

### 3. 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像重试
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r server/requirements.txt
```

### 4. 查看应用日志

```bash
# nohup 方式
tail -f app.log

# systemd 方式
sudo journalctl -u magic-conch -f
```

---

## 📝 维护命令

```bash
# 查看运行状态
ps aux | grep uvicorn

# 查看端口监听
sudo netstat -tlnp | grep 8000

# 查看数据库大小
du -h storage/app.db

# 备份数据库
cp storage/app.db storage/app.db.backup.$(date +%Y%m%d)

# 更新代码
git pull
pip install -r server/requirements.txt
sudo systemctl restart magic-conch
```

---

## 🔒 安全建议

1. **修改默认密钥**：务必修改 `.env` 中的 `SECRET_KEY` 和 `ADMIN_TOKEN`
2. **限制端口访问**：使用防火墙限制 8000 端口仅本地访问，通过 Nginx 代理
3. **定期备份**：定期备份 `storage/app.db` 数据库文件
4. **HTTPS 访问**：生产环境务必配置 HTTPS
5. **限制 CORS**：修改 `.env` 中的 `ALLOWED_ORIGINS`

---

## 📞 获取帮助

- GitHub Issues: https://github.com/xlryan/magic-conch/issues
- 文档: https://github.com/xlryan/magic-conch/blob/main/README.md

---

**🎉 部署完成！享受神奇海螺·烂尾博物馆！**
