# 🚀 AI Matchmaker - 快速启动指南

## 📋 前置要求

确保以下服务正在运行：
- ✅ PostgreSQL (端口 5432)
- ✅ Redis (端口 6379)
- ✅ Python 3.11+ 已安装
- ✅ Node.js 18+ 已安装（用于前端）

---

## 🔧 后端启动步骤

### 1. 激活虚拟环境

```bash
# Windows
cd backend
..\venv\Scripts\activate

# Linux/Mac
cd backend
source ../venv/bin/activate
```

### 2. 检查环境配置

确保 `.env` 文件包含正确的配置：

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ai_matchmaker

# Redis 配置
REDIS_URL=redis://localhost:6379

# 安全配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. 启动后端服务器

```bash
# 开发模式（带自动重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

服务器将在 `http://localhost:8000` 启动

---

## 🌐 前端启动步骤

### 1. 安装依赖（首次运行）

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:5173` 启动

---

## 📚 API 文档

启动后端后，访问以下 URL 查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🧪 测试 API

### 使用 curl 测试

#### 1. 注册用户

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User",
    "date_of_birth": "1990-01-01",
    "gender": "other"
  }'
```

#### 2. 登录

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

#### 3. 获取当前用户信息

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 4. 获取通知

```bash
curl -X GET http://localhost:8000/api/v1/notifications/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🛠️ 常用命令

### 数据库管理

```bash
# 创建新的迁移
cd backend
alembic revision --autogenerate -m "描述"

# 运行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看当前版本
alembic current

# 查看迁移历史
alembic history
```

### 数据库重置（开发环境）

```bash
# 删除所有表并重新创建
cd backend
python -c "from app.core.database import Base, engine; import asyncio; asyncio.run(Base.metadata.drop_all(engine)); asyncio.run(Base.metadata.create_all(engine))"

# 运行种子数据
python -m app.core.seed_data
```

### Redis 管理

```bash
# 连接到 Redis CLI
redis-cli

# 查看所有键
KEYS *

# 清空所有数据
FLUSHALL

# 查看特定键
GET session:xxx

# 删除特定键
DEL session:xxx
```

---

## 🐛 故障排查

### 问题 1: 数据库连接失败

**错误**: `could not connect to server`

**解决方案**:
1. 检查 PostgreSQL 是否正在运行
2. 验证 `.env` 中的数据库 URL
3. 确保数据库已创建：`createdb ai_matchmaker`

### 问题 2: Redis 连接失败

**错误**: `Error connecting to Redis`

**解决方案**:
1. 检查 Redis 是否正在运行：`redis-cli ping`
2. 验证 `.env` 中的 Redis URL
3. 启动 Redis：`redis-server`

### 问题 3: 导入错误

**错误**: `ModuleNotFoundError`

**解决方案**:
1. 确保虚拟环境已激活
2. 重新安装依赖：`pip install -r requirements.txt`
3. 检查 Python 版本：`python --version`

### 问题 4: 端口已被占用

**错误**: `Address already in use`

**解决方案**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

---

## 📊 监控和日志

### 查看实时日志

```bash
# 后端日志
cd backend
tail -f logs/app.log

# 使用 uvicorn 的日志级别
uvicorn main:app --reload --log-level debug
```

### 数据库查询日志

在 `.env` 中设置：
```env
DATABASE_ECHO=true
```

### Redis 监控

```bash
# 实时监控 Redis 命令
redis-cli monitor

# 查看 Redis 信息
redis-cli info
```

---

## 🔐 安全注意事项

### 生产环境配置

1. **更改默认密钥**:
   ```env
   SECRET_KEY=$(openssl rand -hex 32)
   ```

2. **使用环境变量**:
   - 不要在代码中硬编码敏感信息
   - 使用 `.env` 文件（不要提交到 Git）

3. **HTTPS**:
   - 在生产环境中使用 HTTPS
   - 配置 SSL 证书

4. **CORS 设置**:
   - 限制允许的源
   - 不要使用 `*` 作为允许的源

5. **速率限制**:
   - 实施 API 速率限制
   - 防止暴力攻击

---

## 📦 部署

### Docker 部署（推荐）

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 手动部署

1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**:
   ```bash
   export DATABASE_URL="postgresql+asyncpg://..."
   export REDIS_URL="redis://..."
   export SECRET_KEY="..."
   ```

3. **运行迁移**:
   ```bash
   alembic upgrade head
   ```

4. **启动服务**:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

---

## 🎯 下一步

1. ✅ 完成个性化测评系统
2. ✅ 实现 AI 头像功能
3. ✅ 添加匹配算法
4. ✅ 实现实时聊天
5. ✅ 添加支付集成
6. ✅ 实施推荐系统

---

## 📞 获取帮助

- **文档**: 查看 `/docs` 目录
- **API 文档**: http://localhost:8000/docs
- **问题追踪**: GitHub Issues
- **社区**: Discord/Slack

---

*最后更新: 2026-02-03*
