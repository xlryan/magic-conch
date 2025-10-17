# 🔧 GitHub Actions 自动部署配置指南

本项目支持通过 GitHub Actions 自动部署到生产服务器。当代码 push 到 `main` 分支时，会自动触发部署流程。

---

## 📋 前置条件

1. 服务器已完成初始部署（运行过 `bash deploy.sh`）
2. 服务器已配置 systemd 服务
3. GitHub 仓库有管理员权限

---

## 🔑 配置 GitHub Secrets

在 GitHub 仓库中配置以下 Secrets：

### 必需的 Secrets

进入：`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

#### 1. `SERVER_HOST`
- **描述**：服务器 IP 地址或域名
- **示例**：`192.168.1.100` 或 `example.com`

#### 2. `SERVER_USER`
- **描述**：SSH 登录用户名
- **示例**：`ubuntu` 或 `root`

#### 3. `SERVER_SSH_KEY`
- **描述**：SSH 私钥（用于免密登录）
- **获取方法**：

```bash
# 在本地生成 SSH 密钥对（如果没有）
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key

# 查看私钥（复制全部内容到 SECRET）
cat ~/.ssh/github_deploy_key

# 复制公钥到服务器
ssh-copy-id -i ~/.ssh/github_deploy_key.pub user@server_ip

# 或手动添加到服务器
cat ~/.ssh/github_deploy_key.pub
# 在服务器上：
echo "公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 可选的 Secrets

#### 4. `SERVER_PORT`（可选）
- **描述**：SSH 端口
- **默认值**：`22`
- **示例**：`2222`

#### 5. `PROJECT_PATH`（可选）
- **描述**：项目在服务器上的路径
- **默认值**：`~/magic-conch`
- **示例**：`/home/ubuntu/magic-conch`

---

## 🚀 部署流程

### 自动触发

每次 push 到 `main` 分支时自动部署：

```bash
git add .
git commit -m "feat: update feature"
git push origin main
# GitHub Actions 自动开始部署
```

### 手动触发

在 GitHub Actions 页面手动运行：

1. 进入 `Actions` 标签
2. 选择 `Deploy to Production`
3. 点击 `Run workflow`
4. 选择 `main` 分支
5. 点击 `Run workflow` 确认

---

## 📊 部署步骤

GitHub Actions 会自动执行以下步骤：

1. **📦 拉取最新代码**
   ```bash
   git fetch origin
   git reset --hard origin/main
   ```

2. **🔧 激活 Conda 环境**
   - 自动检测并激活 Conda

3. **📦 更新依赖**
   ```bash
   pip install -r server/requirements.txt
   ```

4. **🗄️ 数据库迁移**
   ```bash
   python scripts/init_db.py
   ```

5. **🔄 重启服务**
   ```bash
   sudo systemctl restart magic-conch
   ```

6. **✅ 验证部署**
   - 检查服务状态
   - 显示服务日志

---

## 🔍 监控部署状态

### 查看 Actions 日志

1. 进入 GitHub 仓库
2. 点击 `Actions` 标签
3. 选择对应的 workflow run
4. 查看详细日志

### 查看服务器日志

```bash
# 查看实时日志
sudo journalctl -u magic-conch -f

# 查看最近 50 条日志
sudo journalctl -u magic-conch -n 50

# 查看错误日志
sudo journalctl -u magic-conch -p err
```

### 检查服务状态

```bash
# 查看服务状态
sudo systemctl status magic-conch

# 检查进程
ps aux | grep uvicorn

# 检查端口
sudo netstat -tlnp | grep 8000
```

---

## 🐛 故障排查

### 部署失败

**SSH 连接失败**
```bash
# 检查服务器 SSH 配置
sudo systemctl status sshd

# 测试 SSH 密钥
ssh -i path/to/private_key user@server_ip

# 检查防火墙
sudo ufw status
```

**权限问题**
```bash
# 确保用户可以执行 sudo systemctl
sudo visudo
# 添加：
username ALL=(ALL) NOPASSWD: /bin/systemctl restart magic-conch
username ALL=(ALL) NOPASSWD: /bin/systemctl status magic-conch
username ALL=(ALL) NOPASSWD: /bin/journalctl
```

**服务重启失败**
```bash
# 查看服务详细状态
sudo systemctl status magic-conch -l

# 查看服务日志
sudo journalctl -u magic-conch -n 100

# 手动测试启动
cd /path/to/project
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

### 回滚部署

```bash
# SSH 登录服务器
ssh user@server_ip

# 进入项目目录
cd ~/magic-conch

# 查看 Git 历史
git log --oneline -10

# 回滚到指定版本
git reset --hard <commit-hash>

# 重启服务
sudo systemctl restart magic-conch
```

---

## 🔒 安全建议

1. **SSH 密钥管理**
   - 为 GitHub Actions 单独生成密钥对
   - 定期轮换密钥
   - 不要在多个地方共用同一密钥

2. **Sudo 权限**
   - 使用 NOPASSWD 仅限必要的命令
   - 不要给予完全的 sudo 权限

3. **Git 权限**
   - 保护 main 分支（Branch Protection Rules）
   - 要求 PR review
   - 要求 CI 通过

4. **服务器安全**
   - 修改 SSH 默认端口
   - 禁用密码登录
   - 配置防火墙
   - 定期更新系统

---

## 📝 配置示例

### 完整的 Secrets 配置

```
SERVER_HOST=192.168.1.100
SERVER_USER=ubuntu
SERVER_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAA...
-----END OPENSSH PRIVATE KEY-----
SERVER_PORT=22
PROJECT_PATH=/home/ubuntu/magic-conch
```

### Sudo 配置示例

在服务器上运行：
```bash
sudo visudo
```

添加以下内容（替换 `ubuntu` 为你的用户名）：
```
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart magic-conch
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl status magic-conch
ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl is-active magic-conch
ubuntu ALL=(ALL) NOPASSWD: /bin/journalctl
```

### SSH 配置示例

`~/.ssh/config`：
```
Host magic-conch-server
    HostName 192.168.1.100
    User ubuntu
    Port 22
    IdentityFile ~/.ssh/github_deploy_key
    StrictHostKeyChecking no
```

---

## 🎯 最佳实践

1. **测试分支**
   - 在 dev 分支测试功能
   - 通过 PR 合并到 main
   - main 分支自动部署

2. **部署通知**
   - 配置 Slack/钉钉通知
   - 发送邮件提醒

3. **健康检查**
   - 部署后自动运行测试
   - 检查关键 API 端点

4. **数据库备份**
   - 部署前自动备份数据库
   - 保留最近 N 个备份

5. **灰度发布**
   - 使用多台服务器
   - 逐步切换流量

---

## 📞 获取帮助

- GitHub Actions 文档: https://docs.github.com/en/actions
- SSH Action: https://github.com/appleboy/ssh-action
- 项目 Issues: https://github.com/xlryan/magic-conch/issues

---

**🎉 配置完成后，每次 push 到 main 都会自动部署！**
