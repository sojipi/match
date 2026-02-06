# AI 模型配置管理

## 概述

所有 Gemini 模型名称现在统一在 `backend/app/core/ai_config.py` 中管理，避免了硬编码和重复配置。

## 配置结构

### 模型配置 (AI_MODEL_CONFIGS)

```python
AI_MODEL_CONFIGS = {
    "gemini_flash": {
        "model_name": "gemini-2.5-flash",
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 0.9,
        "top_k": 40
    },
    "gemini_pro": {
        "model_name": "gemini-2.5-pro", 
        "temperature": 0.7,
        "max_tokens": 2000,
        "top_p": 0.9,
        "top_k": 40
    },
    "mock_model": {
        "responses": [...]
    }
}
```

### 默认模型

```python
DEFAULT_GEMINI_MODEL = "gemini_flash"
```

## 使用方法

### 1. 获取默认模型名称

```python
from app.core.ai_config import get_gemini_model_name

model_name = get_gemini_model_name()  # 返回: "gemini-2.5-flash"
```

### 2. 获取特定模型名称

```python
flash_model = get_gemini_model_name("gemini_flash")  # "gemini-2.5-flash"
pro_model = get_gemini_model_name("gemini_pro")      # "gemini-2.5-pro"
```

### 3. 在 AI 代理中使用

```python
response = client.models.generate_content(
    model=get_gemini_model_name(),  # 使用统一配置
    contents=prompt
)
```

## 修改模型配置

### 更换默认模型

在 `ai_config.py` 中修改：

```python
DEFAULT_GEMINI_MODEL = "gemini_pro"  # 切换到 Pro 模型
```

### 添加新模型

```python
AI_MODEL_CONFIGS["gemini_new"] = {
    "model_name": "gemini-3.0-flash",
    "temperature": 0.8,
    "max_tokens": 1500,
    "top_p": 0.95,
    "top_k": 50
}
```

### 更新现有模型

```python
AI_MODEL_CONFIGS["gemini_flash"]["model_name"] = "gemini-2.5-flash-latest"
```

## 受影响的文件

以下文件现在使用统一的模型配置：

1. `backend/app/core/ai_config.py` - 配置管理中心
2. `backend/app/services/ai_agent_service.py` - AI 代理服务
   - UserAvatarAgent._initialize_agentscope_agent()
   - UserAvatarAgent._generate_gemini_response()
   - MatchMakerAgent._initialize_agentscope_agent()
   - MatchMakerAgent._generate_gemini_facilitation()
   - ScenarioGenerator._generate_gemini_scenario()

## 优势

1. **集中管理**: 所有模型配置在一个地方
2. **易于维护**: 修改模型只需要改一个地方
3. **类型安全**: 通过函数获取模型名称，减少拼写错误
4. **灵活配置**: 支持不同场景使用不同模型
5. **版本控制**: 模型升级时只需要修改配置文件

## 最佳实践

1. 始终使用 `get_gemini_model_name()` 获取模型名称
2. 不要在代码中硬编码模型名称
3. 新增模型时同时更新配置和文档
4. 测试时可以临时切换到不同模型进行对比