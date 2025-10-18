# 🔐 SSL 证书自动配置指南

## 快速开始

### 1. 上传脚本到服务器

```bash
# 在本地推送代码
git add scripts/setup_ssl.sh
git commit -m "feat: add SSL auto-configuration script"
git push

# 在服务器上拉取
cd ~/magic-conch
git pull
```

### 2. 运行配置脚本

```bash
# 赋予执行权限
chmod +x scripts/setup_ssl.sh

# 运行脚本
bash scripts/setup_ssl.sh
```

## 脚本功能

✅ **自动检测和安装**
- 检查 Nginx 和 Certbot 是否已安装
- 自动安装缺失的组件

✅ **DNS 验证**
- 验证所有域名的 DNS 解析状态
- 确保域名已正确指向服务器

✅ **证书申请**
- 为以下域名申请 SSL 证书：
  - jam.lesstk.com
  - lesstk.com
  - dev.lesstk.com
  - conch.lesstk.com

✅ **自动续期配置**
- 启用 systemd 定时任务（每天检查两次）
- 配置续期后自动重载 Nginx
- 测试续期流程

✅ **生成配置示例**
- 创建 Nginx SSL 配置示例文件
- 包含安全的 SSL 参数配置

## 域名配置

当前配置的域名列表：
- `jam.lesstk.com`
- `lesstk.com`
- `dev.lesstk.com`
- `conch.lesstk.com`

如需修改域名列表，编辑 `scripts/setup_ssl.sh` 文件中的 `DOMAINS` 数组：

```bash
DOMAINS=(
    "jam.lesstk.com"
    "lesstk.com"
    "dev.lesstk.com"
    "conch.lesstk.com"
    # 添加更多域名...
)
```

## 运行后步骤

脚本执行完成后会生成 `nginx-ssl-config-example.conf` 文件，按以下步骤应用配置：

### 1. 查看生成的配置

```bash
cat nginx-ssl-config-example.conf
```

### 2. 应用到 Nginx

**选项 A：更新现有配置**

编辑你的 Nginx 站点配置：
```bash
sudo nano /etc/nginx/sites-available/magic-conch
```

将示例配置中的 SSL 部分复制到你的配置文件中。

**选项 B：使用新配置文件**

```bash
# 复制配置到 Nginx
sudo cp nginx-ssl-config-example.conf /etc/nginx/sites-available/magic-conch

# 创建软链接
sudo ln -sf /etc/nginx/sites-available/magic-conch /etc/nginx/sites-enabled/
```

### 3. 测试并重载 Nginx

```bash
# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

## 验证配置

### 检查证书状态

```bash
# 查看所有证书
sudo certbot certificates

# 查看证书过期时间
sudo certbot certificates | grep "Expiry Date"
```

### 检查自动续期

```bash
# 查看定时任务状态
sudo systemctl status certbot.timer

# 查看下次运行时间
sudo systemctl list-timers | grep certbot

# 测试自动续期（模拟运行）
sudo certbot renew --dry-run
```

### 测试 HTTPS 访问

```bash
# 测试 SSL 握手
openssl s_client -connect jam.lesstk.com:443 -servername jam.lesstk.com < /dev/null

# 测试 HTTP 重定向
curl -I http://jam.lesstk.com

# 测试 HTTPS 访问
curl -I https://jam.lesstk.com
```

## 证书续期

### 自动续期

证书会通过 systemd 定时任务自动续期：
- **运行时间**：每天随机时间执行两次
- **续期条件**：证书剩余有效期少于 30 天
- **自动重载**：续期成功后自动重载 Nginx

### 手动续期

如需手动续期：

```bash
# 续期所有证书
sudo certbot renew

# 强制续期（不检查到期时间）
sudo certbot renew --force-renewal

# 续期后查看状态
sudo certbot certificates
```

## 日志查看

### Certbot 日志

```bash
# 查看 Certbot 日志
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# 查看定时任务日志
sudo journalctl -u certbot.timer -f

# 查看最近的续期记录
sudo journalctl -u certbot.service --since "1 week ago"
```

### Nginx 日志

```bash
# 查看访问日志
sudo tail -f /var/log/nginx/access.log

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

## 常见问题

### 1. DNS 解析失败

**问题**：脚本提示域名 DNS 解析失败

**解决**：
```bash
# 检查域名解析
host jam.lesstk.com
nslookup jam.lesstk.com

# 确保 A 记录指向服务器 IP
dig +short jam.lesstk.com
```

### 2. 证书申请失败

**问题**：Certbot 证书申请失败

**可能原因**：
- DNS 未正确解析
- 80/443 端口未开放
- Nginx 配置错误

**解决**：
```bash
# 检查端口是否开放
sudo netstat -tlnp | grep -E ':(80|443)'

# 检查防火墙
sudo ufw status

# 查看详细错误日志
sudo tail -50 /var/log/letsencrypt/letsencrypt.log
```

### 3. 自动续期未启用

**问题**：certbot.timer 未运行

**解决**：
```bash
# 启用并启动定时任务
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# 验证状态
sudo systemctl status certbot.timer
```

### 4. Nginx 重载失败

**问题**：证书续期后 Nginx 未自动重载

**解决**：
```bash
# 检查 Hook 脚本
sudo cat /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh

# 确保脚本有执行权限
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh

# 手动测试重载
sudo systemctl reload nginx
```

## 安全建议

1. **定期检查证书状态**
   ```bash
   sudo certbot certificates
   ```

2. **监控续期日志**
   ```bash
   sudo journalctl -u certbot.service --since "1 month ago"
   ```

3. **备份证书配置**
   ```bash
   sudo tar czf letsencrypt-backup-$(date +%Y%m%d).tar.gz /etc/letsencrypt
   ```

4. **启用 HSTS**（已包含在配置示例中）
   ```nginx
   add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
   ```

5. **使用强加密套件**（已包含在配置示例中）
   ```nginx
   ssl_protocols TLSv1.2 TLSv1.3;
   ssl_ciphers HIGH:!aNULL:!MD5;
   ```

## 多域名管理

### 为不同域名配置不同的应用

如果不同域名需要代理到不同的后端服务：

```nginx
# jam.lesstk.com -> 8001
server {
    listen 443 ssl http2;
    server_name jam.lesstk.com;

    ssl_certificate /etc/letsencrypt/live/jam.lesstk.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jam.lesstk.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8001;
    }
}

# conch.lesstk.com -> 8002
server {
    listen 443 ssl http2;
    server_name conch.lesstk.com;

    ssl_certificate /etc/letsencrypt/live/jam.lesstk.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jam.lesstk.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8002;
    }
}
```

### 添加新域名

1. 修改 `scripts/setup_ssl.sh`，添加新域名到 `DOMAINS` 数组
2. 重新运行脚本：`bash scripts/setup_ssl.sh`
3. 脚本会自动为新域名申请证书并更新配置

## 证书吊销

如需吊销证书：

```bash
# 吊销证书
sudo certbot revoke --cert-path /etc/letsencrypt/live/jam.lesstk.com/cert.pem

# 删除证书
sudo certbot delete --cert-name jam.lesstk.com
```

## 参考资源

- [Let's Encrypt 官方文档](https://letsencrypt.org/docs/)
- [Certbot 用户指南](https://certbot.eff.org/docs/)
- [Nginx SSL 配置指南](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [SSL Labs 测试工具](https://www.ssllabs.com/ssltest/)

## 支持

如遇到问题：
1. 查看 `/var/log/letsencrypt/letsencrypt.log`
2. 运行 `sudo certbot renew --dry-run` 测试
3. 检查 Nginx 配置：`sudo nginx -t`

---

**最后更新**：2025-10-18
