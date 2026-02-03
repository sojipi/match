# 🔌 WebSocket 连接指南

## 问题

WebSocket 连接被拒绝：
```
INFO: connection rejected (403 Forbidden)
```

## 原因

WebSocket 需要有效的 JWT 访问令牌进行身份验证，不能使用 `demo_token`。

---

## 正确的 WebSocket 连接方式

### 步骤 1: 获取有效的访问令牌

首先登录获取访问令牌：

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'
```

响应示例：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "...",
  "expires_in": 1800,
  "user": {...}
}
```

### 步骤 2: 使用访问令牌连接 WebSocket

#### 方式 1: 通过查询参数传递令牌

```javascript
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."; // 从登录响应获取
const sessionId = "c2975637-a935-44a4-9f06-84eb5428981f";
const ws = new WebSocket(`ws://localhost:8000/ws/session/${sessionId}?token=${token}`);

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket closed');
};
```

#### 方式 2: 使用 Python 客户端

```python
import asyncio
import websockets
import json

async def connect_websocket():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # 从登录获取
    session_id = "c2975637-a935-44a4-9f06-84eb5428981f"

    uri = f"ws://localhost:8000/ws/session/{session_id}?token={token}"

    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")

        # 发送消息
        await websocket.send(json.dumps({
            "type": "message",
            "content": "Hello!"
        }))

        # 接收消息
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data}")

asyncio.run(connect_websocket())
```

---

## WebSocket 端点

### 1. 匹配会话 WebSocket

**端点**: `ws://localhost:8000/ws/session/{session_id}?token={access_token}`

**用途**: 实时匹配会话通信

**消息格式**:
```json
{
  "type": "message",
  "content": "消息内容",
  "metadata": {}
}
```

---

## 测试 WebSocket 连接

### 使用 wscat 工具

```bash
# 安装 wscat
npm install -g wscat

# 连接 WebSocket
wscat -c "ws://localhost:8000/ws/session/SESSION_ID?token=YOUR_ACCESS_TOKEN"
```

### 使用浏览器控制台

```javascript
// 1. 先登录获取 token
fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'your-email@example.com',
    password: 'your-password'
  })
})
.then(res => res.json())
.then(data => {
  const token = data.access_token;
  console.log('Token:', token);

  // 2. 使用 token 连接 WebSocket
  const sessionId = 'c2975637-a935-44a4-9f06-84eb5428981f';
  const ws = new WebSocket(`ws://localhost:8000/ws/session/${sessionId}?token=${token}`);

  ws.onopen = () => console.log('Connected!');
  ws.onmessage = (e) => console.log('Message:', JSON.parse(e.data));
  ws.onerror = (e) => console.error('Error:', e);

  // 保存到全局变量以便测试
  window.ws = ws;
});

// 3. 发送测试消息
window.ws.send(JSON.stringify({
  type: 'message',
  content: 'Hello from browser!'
}));
```

---

## 常见错误和解决方案

### 错误 1: 403 Forbidden

**原因**:
- 使用了无效的 token（如 `demo_token`）
- Token 已过期
- Token 格式不正确

**解决方案**:
```bash
# 重新登录获取新的 token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

### 错误 2: 401 Unauthorized

**原因**: Token 验证失败

**解决方案**:
- 检查 token 是否完整
- 确保 token 没有被截断
- 验证 SECRET_KEY 配置正确

### 错误 3: Connection Closed

**原因**:
- 网络问题
- 服务器重启
- Token 过期

**解决方案**:
- 实现自动重连机制
- 刷新 token
- 检查服务器日志

---

## WebSocket 自动重连示例

```javascript
class WebSocketClient {
  constructor(sessionId, token) {
    this.sessionId = sessionId;
    this.token = token;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  connect() {
    const url = `ws://localhost:8000/ws/session/${this.sessionId}?token=${this.token}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
      this.reconnect();
    };
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);

      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  handleMessage(data) {
    console.log('Received message:', data);
    // 处理接收到的消息
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// 使用示例
const client = new WebSocketClient(
  'c2975637-a935-44a4-9f06-84eb5428981f',
  'your-access-token'
);
client.connect();
```

---

## 完整的前端集成示例

```typescript
// websocket.service.ts
import { BehaviorSubject } from 'rxjs';

export class WebSocketService {
  private ws: WebSocket | null = null;
  private messages$ = new BehaviorSubject<any>(null);
  private connectionStatus$ = new BehaviorSubject<string>('disconnected');

  connect(sessionId: string, token: string) {
    const url = `ws://localhost:8000/ws/session/${sessionId}?token=${token}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.connectionStatus$.next('connected');
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.messages$.next(data);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.connectionStatus$.next('error');
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
      this.connectionStatus$.next('disconnected');
    };
  }

  sendMessage(type: string, content: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, content }));
    }
  }

  getMessages() {
    return this.messages$.asObservable();
  }

  getConnectionStatus() {
    return this.connectionStatus$.asObservable();
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}
```

---

## 调试技巧

### 1. 检查 Token 是否有效

```bash
# 解码 JWT token（不验证签名）
echo "YOUR_TOKEN" | cut -d'.' -f2 | base64 -d | jq
```

### 2. 查看服务器日志

```bash
# 查看 uvicorn 日志
tail -f logs/app.log
```

### 3. 使用浏览器开发者工具

1. 打开浏览器开发者工具（F12）
2. 切换到 "Network" 标签
3. 筛选 "WS"（WebSocket）
4. 查看连接状态和消息

---

## 总结

### 关键点

1. ✅ **必须使用有效的 JWT token**，不能使用 `demo_token`
2. ✅ Token 通过查询参数 `?token=xxx` 传递
3. ✅ Token 从登录 API 获取
4. ✅ Token 有过期时间（默认 30 分钟）
5. ✅ 实现自动重连机制以处理断线

### 快速测试

```bash
# 1. 登录获取 token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# 2. 使用 wscat 连接
wscat -c "ws://localhost:8000/ws/session/SESSION_ID?token=$TOKEN"
```

---

*文档更新时间: 2026-02-03*
