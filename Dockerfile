FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制所有代码
COPY . .

# 创建存储目录
RUN mkdir -p /app/storage

EXPOSE 8000

# 命令在 docker-compose.yml 中定义
