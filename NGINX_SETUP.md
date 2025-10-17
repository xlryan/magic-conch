# 🌐 Nginx 反向代理配置指南

本指南介绍如何为 Magic Conch 项目配置 Nginx 反向代理和 HTTPS。

---

## 📋 前置条件

- Ubuntu/Debian 服务器
- 已安装 Nginx
- 域名已解析到服务器 IP
- 已部署 Magic Conch 应用（运行在 8000 端口）

---

## 🚀 快速配置

### 1️⃣ 安装 Nginx

```bash
# 更新包列表
sudo apt update

# 安装 Nginx
sudo apt install nginx -y

# 启动并设置开机自启
sudo systemctl start nginx
sudo systemctl enable nginx

# 检查状态
sudo systemctl status nginx
```

### 2️⃣ 配置 Nginx

```bash
# 复制配置文件到 Nginx 配置目录
sudo cp ~/magic-conch/nginx.conf /etc/nginx/sites-available/magic-conch

# 创建软链接启用配置
sudo ln -s /etc/nginx/sites-available/magic-conch /etc/nginx/sites-enabled/

# 删除默认配置（可选）
sudo rm /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t
```

### 3️⃣ 配置 SSL 证书（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取 SSL 证书
sudo certbot --nginx -d conch.lesstk.com

# 按提示操作：
# 1. 输入邮箱
# 2. 同意服务条款
# 3. 选择是否重定向 HTTP 到 HTTPS（推荐选择 2）

# 测试自动续期
sudo certbot renew --dry-run
```

### 4️⃣ 重启 Nginx

```bash
# 重新加载配置
sudo systemctl reload nginx

# 或完全重启
sudo systemctl restart nginx

# 检查状态
sudo systemctl status nginx
```

### 5️⃣ 验证部署

```bash
# 测试 HTTPS 访问
curl https://conch.lesstk.com/health

# 测试 Webhook 端点
curl https://conch.lesstk.com/api/webhook/deploy

# 浏览器访问
# https://conch.lesstk.com
```

---

## 🔧 配置说明

### HTTP 到 HTTPS 重定向

```nginx
server {
    listen 80;
    server_name conch.lesstk.com;
    return 301 https://$server_name$request_uri;
}
```

### HTTPS 主配置

```nginx
server {
    listen 443 ssl http2;
    server_name conch.lesstk.com;

    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/conch.lesstk.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/conch.lesstk.com/privkey.pem;

    # 反向代理到 FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Webhook 特殊配置

```nginx
location /api/webhook/deploy {
    # GitHub IP 白名单（可选）
    # allow 192.30.252.0/22;
    # deny all;

    proxy_pass http://127.0.0.1:8000;

    # 保留 GitHub 签名头
    proxy_set_header X-Hub-Signature-256 $http_x_hub_signature_256;

    # 增加超时（部署可能需要 5 分钟）
    proxy_read_timeout 300s;
}
```

---

## 🔒 安全增强

### 1. 启用防火墙

```bash
# 安装 UFW
sudo apt install ufw -y

# 允许 SSH（重要！避免锁死）
sudo ufw allow ssh
sudo ufw allow 22/tcp

# 允许 HTTP 和 HTTPS
sudo ufw allow 'Nginx Full'

# 或手动配置
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable

# 检查状态
sudo ufw status
```

### 2. 启用 GitHub IP 白名单

编辑 Nginx 配置，取消注释 webhook 白名单：

```bash
sudo nano /etc/nginx/sites-available/magic-conch
```

找到 `/api/webhook/deploy` 部分，取消注释：

```nginx
location /api/webhook/deploy {
    # 启用 GitHub IP 白名单
    allow 192.30.252.0/22;
    allow 185.199.108.0/22;
    allow 140.82.112.0/20;
    allow 143.55.64.0/20;
    deny all;

    # ... 其他配置
}
```

重新加载 Nginx：

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 3. 限制请求速率

添加到 `http` 块（`/etc/nginx/nginx.conf`）：

```nginx
http {
    # 限制 Webhook 请求速率
    limit_req_zone $binary_remote_addr zone=webhook:10m rate=10r/m;

    # ... 其他配置
}
```

在 `server` 块中应用：

```nginx
location /api/webhook/deploy {
    limit_req zone=webhook burst=5;
    # ... 其他配置
}
```

---

## 📊 监控和日志

### 查看 Nginx 日志

```bash
# 访问日志
sudo tail -f /var/log/nginx/magic-conch-access.log

# 错误日志
sudo tail -f /var/log/nginx/magic-conch-error.log

# 实时监控 Webhook 请求
sudo tail -f /var/log/nginx/magic-conch-access.log | grep webhook
```

### 日志轮转

Nginx 默认已配置日志轮转，检查配置：

```bash
cat /etc/logrotate.d/nginx
```

### 监控 SSL 证书过期

```bash
# 查看证书有效期
sudo certbot certificates

# 手动续期（自动续期已配置在 cron）
sudo certbot renew

# 强制续期
sudo certbot renew --force-renewal
```

---

## 🐛 故障排查

### Nginx 无法启动

```bash
# 检查配置语法
sudo nginx -t

# 查看详细错误
sudo systemctl status nginx -l

# 查看错误日志
sudo tail -50 /var/log/nginx/error.log
```

### 502 Bad Gateway

**原因**：Nginx 无法连接到后端应用

```bash
# 检查 FastAPI 是否运行
sudo systemctl status magic-conch

# 检查端口监听
sudo netstat -tlnp | grep 8000

# 检查防火墙
sudo ufw status

# 测试本地连接
curl http://127.0.0.1:8000/health
```

### 504 Gateway Timeout

**原因**：后端处理时间过长

增加超时配置：

```nginx
location / {
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
}
```

### SSL 证书问题

```bash
# 检查证书
sudo certbot certificates

# 测试 SSL 配置
sudo nginx -t

# 查看 Certbot 日志
sudo tail -50 /var/log/letsencrypt/letsencrypt.log

# 强制重新获取证书
sudo certbot delete --cert-name conch.lesstk.com
sudo certbot --nginx -d conch.lesstk.com
```

### Webhook 403 错误

**原因**：可能是 IP 白名单限制

```bash
# 查看访问日志
sudo tail -100 /var/log/nginx/magic-conch-access.log | grep webhook

# 临时禁用白名单测试
# 编辑配置，注释掉 allow/deny 行
sudo nano /etc/nginx/sites-available/magic-conch
sudo systemctl reload nginx
```

---

## 📈 性能优化

### 启用 Gzip 压缩

添加到 `server` 块：

```nginx
# Gzip 压缩
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript
           application/json application/javascript application/xml+rss;
```

### 启用浏览器缓存

已在配置中包含：

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 7d;
    add_header Cache-Control "public, immutable";
}
```

### 连接优化

添加到 `http` 块：

```nginx
http {
    # 保持连接
    keepalive_timeout 65;
    keepalive_requests 100;

    # 缓存
    open_file_cache max=1000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
}
```

---

## 🔄 配置更新流程

```bash
# 1. 修改配置
sudo nano /etc/nginx/sites-available/magic-conch

# 2. 测试配置
sudo nginx -t

# 3. 重新加载（不中断服务）
sudo systemctl reload nginx

# 4. 查看状态
sudo systemctl status nginx
```

---

## 📝 完整部署检查清单

- [ ] Nginx 已安装并运行
- [ ] 配置文件已复制到 `/etc/nginx/sites-available/`
- [ ] 软链接已创建到 `/etc/nginx/sites-enabled/`
- [ ] SSL 证书已通过 Certbot 获取
- [ ] HTTP 自动重定向到 HTTPS
- [ ] 防火墙已配置（UFW 允许 80/443）
- [ ] FastAPI 应用运行在 8000 端口
- [ ] Webhook 端点可访问
- [ ] 日志正常记录
- [ ] SSL 自动续期已配置

---

## 🆘 常用命令速查

```bash
# 启动/停止/重启
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx

# 检查状态
sudo systemctl status nginx

# 测试配置
sudo nginx -t

# 查看日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# SSL 证书
sudo certbot certificates
sudo certbot renew
sudo certbot renew --dry-run

# 防火墙
sudo ufw status
sudo ufw allow 'Nginx Full'
```

---

## 📞 获取帮助

- Nginx 官方文档: <https://nginx.org/en/docs/>
- Let's Encrypt 文档: <https://letsencrypt.org/docs/>
- 项目 Issues: <https://github.com/xlryan/magic-conch/issues>

---

**🎉 配置完成后，你的应用将通过 HTTPS 安全访问！**
