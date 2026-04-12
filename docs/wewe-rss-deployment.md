# WeWe RSS 部署指南

> 微信公众号转 RSS 订阅服务，私有部署踩坑经验总结

## 项目信息

- **GitHub**: https://github.com/cooderl/wewe-rss
- **原理**: 基于微信读书接口获取公众号文章
- **费用**: 完全免费开源（MIT 协议）

---

## 快速部署

### 1. Docker Compose 配置

```yaml
services:
  wewe-rss:
    image: cooderl/wewe-rss-sqlite:latest
    container_name: wewe-rss
    ports:
      - "4000:4000"
    volumes:
      - wewe-rss-data:/app/data
    environment:
      - MAX_REQUEST_PER_MINUTE=60        # 每分钟最大请求数
      - MAX_WAIT_SECOND=30               # 最大等待时间
      - AUTH_CODE=hwj                    # 访问密码（可选，禁用则留空）
      - SERVER_ORIGIN_URL=http://你的服务器IP  # ⚠️ 必须配置！
    restart: unless-stopped

volumes:
  wewe-rss-data:
```

### 2. 启动服务

```bash
docker compose up -d
```

---

## ⚠️ 重要踩坑点

### 坑 1：SERVER_ORIGIN_URL 必须配置

**问题**：前端页面空白，API 请求失败

**原因**：WeWe RSS 前端需要知道服务器地址才能发送 API 请求

**解决**：
```yaml
environment:
  - SERVER_ORIGIN_URL=http://你的服务器IP
```

验证配置生效：
```bash
curl http://localhost:4000/dash/ | grep "__WEWE_RSS_SERVER_ORIGIN_URL__"
# 应输出：window.__WEWE_RSS_SERVER_ORIGIN_URL__ = 'http://你的服务器IP';
```

---

### 坑 2：Docker Hub 网络超时

**问题**：拉取镜像失败 `Client.Timeout exceeded while waiting for connection`

**解决**：配置 Docker 镜像加速器

```bash
cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.tech"
  ]
}
EOF
systemctl restart docker
```

---

### 坑 3：Nginx 反向代理静态资源 404

**问题**：页面能加载，但 JS/CSS 文件 404

**原因**：Nginx 的正则 location 捕获了 `.js|.css` 文件，优先级高于 `/dash/` location

**解决**：使用 `^~` 修饰符强制优先匹配

```nginx
# wewe-rss 代理 - 必须放在 server 块最前面
location ^~ /dash/ {
    proxy_pass http://wewe-rss:4000/dash/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

location ^~ /trpc/ {
    proxy_pass http://wewe-rss:4000/trpc/;
    proxy_set_header Host $host;
    proxy_set_header Authorization $http_authorization;
}

location ^~ /feeds/ {
    proxy_pass http://wewe-rss:4000/feeds/;
    proxy_set_header Host $host;
}

# 静态文件正则（放在后面，不会匹配 /dash/ 下的文件）
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    root /usr/share/nginx/html;
    expires 1y;
}
```

**关键点**：`^~` 修饰符会阻止正则表达式匹配，确保 `/dash/assets/*.js` 被正确代理

---

### 坑 4：容器网络不通

**问题**：Nginx 内部无法访问 `http://wewe-rss:4000`

**解决**：连接到同一 Docker 网络

```bash
docker network create common-net
docker network connect common-net wewe-rss
docker network connect common-net nginx
```

验证：
```bash
docker exec nginx ping -c1 wewe-rss
docker exec nginx curl http://wewe-rss:4000/dash/
```

---

### 坑 5：Auth Code 配置

**问题**：禁用 auth code 仍要求输入

**原因**：环境变量 `AUTH_CODE` 留空字符串或未设置时，默认启用

**禁用方式**：
```yaml
environment:
  - AUTH_CODE=  # 留空（但不推荐，会有安全隐患）
```

**设置密码**：
```yaml
environment:
  - AUTH_CODE=hwj  # 设置你的密码
```

---

## 完整 Nginx 配置示例

```nginx
server {
    listen 80;
    server_name localhost;

    # WeWe RSS 代理 - 放在最前面
    location ^~ /dash/ {
        proxy_pass http://wewe-rss:4000/dash/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location ^~ /trpc/ {
        proxy_pass http://wewe-rss:4000/trpc/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Authorization $http_authorization;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    location ^~ /feeds/ {
        proxy_pass http://wewe-rss:4000/feeds/;
        proxy_set_header Host $host;
    }

    # 其他应用
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 使用步骤

1. **访问管理界面**: `http://你的IP/dash/`
2. **输入 Auth Code**: `hwj`
3. **添加微信读书账号**: 点击「账号管理」→「添加账号」→ 微信读书扫码
4. **添加公众号源**: 点击「公众号源」→「添加」→ 输入任意一篇文章链接
5. **获取 RSS 链接**: `http://你的IP/feeds/公众号ID.rss`

---

## 风控限制

- 每个账号约能订阅 **10 个公众号**
- 刷新频率约 **每天 2 次**
- 超限会触发验证码，建议：
  - 准备多个微信读书账号轮换
  - 使用专用小号，避免主账号被封

---

## 访问地址

- **管理界面**: http://115.190.82.67/dash/
- **Auth Code**: hwj

---

*部署时间：2026-04-12*
*服务器：115.190.82.67*