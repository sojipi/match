# Gemini API Key 用户自定义功能

## 功能概述

允许用户配置自己的 Gemini API Key，避免系统配额限制，享受不间断的 AI 对话服务。

## 实现内容

### 1. 后端实现

#### 数据库更改
- **表**: `users`
- **新字段**: `gemini_api_key VARCHAR(255)`
- **迁移脚本**: `add_gemini_api_key_column.sql`

```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS gemini_api_key VARCHAR(255);
```

#### API 端点

**文件**: `backend/app/api/v1/endpoints/user_settings.py`

- `GET /api/v1/users/settings` - 获取用户设置（API Key 已脱敏）
- `PUT /api/v1/users/settings` - 更新用户设置

#### 错误检测和处理

**文件**: `backend/app/services/ai_agent_service.py`

- 检测 Gemini API 429 错误（配额超限）
- 抛出特定异常 `GEMINI_QUOTA_EXCEEDED`

**文件**: `backend/app/websocket/manager.py`

- 捕获配额错误
- 广播 `gemini_quota_exceeded` 事件到前端

### 2. 前端实现

#### 设置页面

**文件**: `frontend/src/pages/SettingsPage.tsx`

功能：
- 显示 Gemini API Key 配置界面
- 提供获取 API Key 的指引
- 安全的 API Key 输入（可显示/隐藏）
- 保存设置到后端

#### 配额超限弹窗

**文件**: `frontend/src/components/matching/LiveMatchingTheater.tsx`

功能：
- 监听 `gemini_quota_exceeded` WebSocket 事件
- 显示友好的错误提示弹窗
- 提供"前往设置"按钮，引导用户配置 API Key

#### 路由配置

**文件**: `frontend/src/App.tsx`

- 添加 `/settings` 路由
- 导入 `SettingsPage` 组件

## 使用流程

### 用户视角

1. **遇到配额限制**
   - 用户在 AI 对话中遇到配额限制
   - 系统显示弹窗提示

2. **前往设置页面**
   - 点击"前往设置"按钮
   - 跳转到 `/settings` 页面

3. **配置 API Key**
   - 访问 [Google AI Studio](https://ai.google.dev/)
   - 创建新的 API Key
   - 复制并粘贴到设置页面
   - 点击"保存设置"

4. **继续使用**
   - 返回 AI 对话页面
   - 使用自己的 API Key 继续对话

### 技术流程

```
AI 对话请求
    ↓
检查用户是否有自定义 API Key
    ↓
使用用户 API Key（如果有）或系统 API Key
    ↓
调用 Gemini API
    ↓
如果返回 429 错误
    ↓
广播 gemini_quota_exceeded 事件
    ↓
前端显示配额超限弹窗
    ↓
用户前往设置页面配置 API Key
```

## 安全考虑

1. **API Key 加密存储**
   - 数据库中存储的 API Key 应该加密（待实现）
   - 当前版本为明文存储，生产环境需要加密

2. **API Key 脱敏显示**
   - GET 接口返回的 API Key 已脱敏
   - 只显示最后 4 位字符

3. **API Key 验证**
   - 基本格式验证（必须以 'AIza' 开头）
   - 可以添加更严格的验证逻辑

## 部署步骤

### 1. 数据库迁移

```bash
# 连接到数据库
psql -U user -d ai_matchmaker

# 执行迁移脚本
\i backend/add_gemini_api_key_column.sql
```

### 2. 重启后端服务

```bash
cd backend
python main.py
```

### 3. 重新构建前端

```bash
cd frontend
npm run build
```

## 测试验证

### 1. 测试 API 端点

```bash
# 获取用户设置
curl -X GET http://localhost:8000/api/v1/users/settings \
  -H "Authorization: Bearer YOUR_TOKEN"

# 更新用户设置
curl -X PUT http://localhost:8000/api/v1/users/settings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"gemini_api_key": "AIzaSyC..."}'
```

### 2. 测试前端流程

1. 访问 http://localhost:3000/settings
2. 输入测试 API Key
3. 点击保存
4. 验证保存成功提示

### 3. 测试配额超限流程

1. 使用已达配额限制的 API Key
2. 启动 AI 对话
3. 验证弹窗显示
4. 点击"前往设置"
5. 验证跳转到设置页面

## 未来改进

1. **API Key 加密**
   - 使用 Fernet 或 AES 加密存储
   - 环境变量中配置加密密钥

2. **API Key 验证**
   - 调用 Gemini API 验证 Key 有效性
   - 显示 Key 的配额使用情况

3. **多 API Key 支持**
   - 允许用户配置多个 API Key
   - 自动轮换使用

4. **使用统计**
   - 显示用户 API Key 的使用统计
   - 配额预警提醒

5. **API Key 管理**
   - 支持删除/重置 API Key
   - API Key 使用历史记录

## 相关文件

### 后端
- `backend/app/models/user.py` - User 模型
- `backend/app/api/v1/endpoints/user_settings.py` - 设置 API
- `backend/app/api/v1/api.py` - API 路由配置
- `backend/app/services/ai_agent_service.py` - AI 代理服务
- `backend/app/websocket/manager.py` - WebSocket 管理
- `backend/add_gemini_api_key_column.sql` - 数据库迁移

### 前端
- `frontend/src/pages/SettingsPage.tsx` - 设置页面
- `frontend/src/components/matching/LiveMatchingTheater.tsx` - AI 对话界面
- `frontend/src/App.tsx` - 路由配置