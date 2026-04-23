# Docker Django Example

## 项目简介
生产级 Django 示例项目，使用 PostgreSQL、Redis、Celery、Gunicorn，前端资源通过 esbuild + Tailwind CSS 构建。采用多阶段 Docker 构建，支持开发和生产环境配置。

## 快速启动

### Docker 启动（推荐）

```bash
# 克隆项目
git clone <GitHub 地址>
cd solo-zj-00052-20260414

# 复制环境变量
cp .env.example .env

# 启动所有服务
docker compose --profile postgres --profile redis --profile web up -d

# 查看运行状态
docker compose ps
```

### 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| Web 应用 | http://localhost:8000 | Django 主服务 |
| PostgreSQL | localhost:5432 | 数据库 |
| Redis | localhost:6379 | 缓存 |

### 停止服务

```bash
docker compose down
```

## 项目结构
- `src/` - Django 项目源码
- `assets/` - 前端资源（JS/CSS）
- `bin/` - Docker 入口脚本
- `config/` - Gunicorn 配置

## 来源
- 原始来源: https://github.com/nickjj/docker-django-example
- GitHub（上传）: https://github.com/11DingKing/solo-zj-00052-20260414
