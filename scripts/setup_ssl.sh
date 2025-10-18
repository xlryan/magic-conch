#!/bin/bash
# SSL 证书自动配置和更新脚本
# 支持多个域名的证书申请和自动续期

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为 root 或有 sudo 权限
if [ "$EUID" -ne 0 ] && ! sudo -n true 2>/dev/null; then
    echo -e "${RED}错误：此脚本需要 root 权限或 sudo 权限${NC}"
    exit 1
fi

echo -e "${GREEN}🔐 SSL 证书自动配置脚本${NC}"
echo "================================"
echo ""

# 域名列表
DOMAINS=(
    "jam.lesstk.com"
    "lesstk.com"
    "dev.lesstk.com"
    "conch.lesstk.com"
)

# 检查 Nginx 是否已安装
check_nginx() {
    echo -e "${YELLOW}📋 检查 Nginx 安装状态...${NC}"
    if ! command -v nginx &> /dev/null; then
        echo -e "${RED}错误：未检测到 Nginx，请先安装 Nginx${NC}"
        echo "安装命令: sudo apt update && sudo apt install nginx -y"
        exit 1
    fi
    echo -e "${GREEN}✅ Nginx 已安装${NC}"
    echo ""
}

# 检查 Certbot 是否已安装
check_certbot() {
    echo -e "${YELLOW}📋 检查 Certbot 安装状态...${NC}"
    if ! command -v certbot &> /dev/null; then
        echo -e "${YELLOW}⚠️  未检测到 Certbot，正在安装...${NC}"
        sudo apt update
        sudo apt install certbot python3-certbot-nginx -y
        echo -e "${GREEN}✅ Certbot 安装完成${NC}"
    else
        echo -e "${GREEN}✅ Certbot 已安装${NC}"
    fi
    echo ""
}

# 检查域名 DNS 解析
check_dns() {
    echo -e "${YELLOW}📋 检查域名 DNS 解析...${NC}"
    local all_resolved=true

    for domain in "${DOMAINS[@]}"; do
        if host "$domain" > /dev/null 2>&1; then
            local ip=$(host "$domain" | grep "has address" | awk '{print $4}' | head -1)
            echo -e "${GREEN}✅ $domain -> $ip${NC}"
        else
            echo -e "${RED}❌ $domain DNS 解析失败${NC}"
            all_resolved=false
        fi
    done

    echo ""

    if [ "$all_resolved" = false ]; then
        echo -e "${YELLOW}⚠️  部分域名 DNS 解析失败，请确保域名已正确配置 A 记录${NC}"
        read -p "是否继续？(y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 申请 SSL 证书
request_certificates() {
    echo -e "${YELLOW}🔒 开始申请 SSL 证书...${NC}"
    echo ""

    # 构建域名参数
    local domain_args=""
    for domain in "${DOMAINS[@]}"; do
        domain_args="$domain_args -d $domain"
    done

    # 检查是否已存在证书
    if sudo certbot certificates 2>/dev/null | grep -q "${DOMAINS[0]}"; then
        echo -e "${YELLOW}⚠️  检测到已存在的证书${NC}"
        read -p "是否强制重新申请？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}正在强制重新申请证书...${NC}"
            sudo certbot certonly --nginx $domain_args --force-renewal --non-interactive --agree-tos --email admin@lesstk.com
        else
            echo -e "${GREEN}跳过证书申请${NC}"
        fi
    else
        echo -e "${YELLOW}正在申请新证书...${NC}"
        sudo certbot certonly --nginx $domain_args --non-interactive --agree-tos --email admin@lesstk.com
    fi

    echo -e "${GREEN}✅ 证书申请完成${NC}"
    echo ""
}

# 配置自动续期
setup_auto_renewal() {
    echo -e "${YELLOW}⚙️  配置自动续期...${NC}"

    # 检查 certbot timer 是否启用
    if sudo systemctl is-enabled certbot.timer &> /dev/null; then
        echo -e "${GREEN}✅ Certbot 自动续期已启用${NC}"
    else
        echo -e "${YELLOW}正在启用 Certbot 自动续期...${NC}"
        sudo systemctl enable certbot.timer
        sudo systemctl start certbot.timer
        echo -e "${GREEN}✅ Certbot 自动续期已启用${NC}"
    fi

    # 显示下次运行时间
    echo ""
    echo -e "${YELLOW}📅 下次自动续期时间：${NC}"
    sudo systemctl list-timers certbot.timer | grep certbot
    echo ""
}

# 配置续期后 Hook（重载 Nginx）
setup_renewal_hook() {
    echo -e "${YELLOW}⚙️  配置续期后 Hook...${NC}"

    # 创建续期后 Hook 脚本
    local hook_script="/etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh"

    sudo mkdir -p /etc/letsencrypt/renewal-hooks/deploy

    sudo tee "$hook_script" > /dev/null <<'EOF'
#!/bin/bash
# 证书续期成功后自动重载 Nginx

if systemctl is-active --quiet nginx; then
    systemctl reload nginx
    echo "✅ Nginx 已重载 ($(date))"
else
    echo "⚠️  Nginx 未运行，跳过重载 ($(date))"
fi
EOF

    sudo chmod +x "$hook_script"

    echo -e "${GREEN}✅ 续期后 Hook 已配置${NC}"
    echo "   证书续期成功后将自动重载 Nginx"
    echo ""
}

# 测试证书续期
test_renewal() {
    echo -e "${YELLOW}🧪 测试证书续期（模拟运行）...${NC}"
    echo ""

    if sudo certbot renew --dry-run; then
        echo ""
        echo -e "${GREEN}✅ 证书续期测试成功！${NC}"
    else
        echo ""
        echo -e "${RED}❌ 证书续期测试失败${NC}"
        echo -e "${YELLOW}请检查错误信息并手动修复${NC}"
        return 1
    fi
    echo ""
}

# 显示证书信息
show_certificate_info() {
    echo -e "${YELLOW}📜 当前证书信息：${NC}"
    echo ""
    sudo certbot certificates
    echo ""
}

# 创建 Nginx SSL 配置示例
create_nginx_config_example() {
    echo -e "${YELLOW}📝 创建 Nginx 配置示例...${NC}"

    local example_file="./nginx-ssl-config-example.conf"

    cat > "$example_file" <<'EOF'
# Nginx SSL 配置示例
# 将此配置应用到你的 Nginx 站点配置中

server {
    listen 80;
    server_name jam.lesstk.com lesstk.com dev.lesstk.com conch.lesstk.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name jam.lesstk.com lesstk.com dev.lesstk.com conch.lesstk.com;

    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/jam.lesstk.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jam.lesstk.com/privkey.pem;

    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS (可选，增强安全性)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

    echo -e "${GREEN}✅ 配置示例已创建: $example_file${NC}"
    echo ""
}

# 主函数
main() {
    echo -e "${YELLOW}准备为以下域名配置 SSL 证书：${NC}"
    for domain in "${DOMAINS[@]}"; do
        echo "  - $domain"
    done
    echo ""

    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 0
    fi

    echo ""

    # 执行配置流程
    check_nginx
    check_certbot
    check_dns
    request_certificates
    setup_auto_renewal
    setup_renewal_hook
    test_renewal
    show_certificate_info
    create_nginx_config_example

    echo "================================"
    echo -e "${GREEN}🎉 SSL 证书配置完成！${NC}"
    echo ""
    echo -e "${YELLOW}接下来的步骤：${NC}"
    echo "1. 查看生成的 Nginx 配置示例: nginx-ssl-config-example.conf"
    echo "2. 将配置应用到你的 Nginx 站点配置文件"
    echo "3. 测试 Nginx 配置: sudo nginx -t"
    echo "4. 重载 Nginx: sudo systemctl reload nginx"
    echo ""
    echo -e "${YELLOW}证书自动续期已配置，系统会每天检查两次并自动续期${NC}"
    echo ""
}

# 运行主函数
main
