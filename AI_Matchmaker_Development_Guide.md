# AI 代理相亲应用开发指南 - 基于 AgentScope

## 1. 项目简介

本项目旨在开发一款 **AI 代理相亲应用**，通过 AI Agent 模拟用户进行初步相亲接触，并进行婚后生活模拟。

**核心价值：**
*   **节省时间**：AI 代理完成初步筛选和了解，减少无效社交。
*   **还原真实**：通过深度训练让 Agent 学习用户真实性格，避免过度美化。
*   **深度预测**：通过“婚后模拟”功能，让双方 Agent 共同面对未来可能发生的真实生活挑战，检验契合度。

**技术栈：**
*   **框架**：[AgentScope](https://github.com/agentscope-ai/agentscope)
*   **语言**：Python 3.10+
*   **模型**：使用Gemini API

*   **记忆**：Mem0 或 ReMe (AgentScope 内置支持) 用于存储用户画像。

---

## 2. 系统架构

系统分为三个主要阶段：

1.  **训练阶段 (Training Phase)**：用户与自己的 Agent 对话，通过问答形式构建“数字替身”。
2.  **相亲阶段 (Matchmaking Phase)**：双方用户的 Agent 在虚拟空间见面，进行多轮对话了解彼此。
3.  **模拟阶段 (Simulation Phase)**：投入特定婚姻场景（如育儿、理财、家庭矛盾），观察 Agent 的应对和互动。

---

## 3. 详细功能设计与实现

### 3.1 训练阶段：构建数字替身

**目标**：让 Agent 充分了解用户。
**实现方式**：
*   使用 `ReActAgent` 配合 `LongTermMemory`。
*   Agent 扮演“采访者”角色，主动向用户提问（基于预设心理学问卷或动态追问）。
*   利用 `agent_control` 模式，Agent 自主调用 `record_to_memory` 将关键信息存入长期记忆。

**代码示例 (训练 Agent)**：

```python
from agentscope.agent import ReActAgent
from agentscope.memory import Mem0LongTermMemory
from agentscope.tool import Toolkit

# 定义长期记忆
long_term_memory = Mem0LongTermMemory(
    agent_name="MyAvatar",
    user_name="User_Real",
    # ... 配置模型和 embedding
)

# 定义采访者 Agent
trainer_agent = ReActAgent(
    name="Trainer",
    sys_prompt="""
    你是一个专业的相亲顾问。你的任务是通过提问了解用户的性格、价值观、生活习惯和择偶标准。
    请循序渐进地提问，不要一次问太多。
    当你获得关键信息时，使用 record_to_memory 工具将其记录下来。
    关注点包括：消费观、家庭观、兴趣爱好、对未来的规划、雷点等。
    """,
    long_term_memory=long_term_memory,
    long_term_memory_mode="agent_control", # 允许 Agent 自主记录
    toolkit=Toolkit(), # 注册记录工具
    # ... 其他配置
)
```

### 3.2 相亲阶段：Agent 互通

**目标**：两个 Agent 代表各自用户进行交流。
**实现方式**：
*   使用 `MsgHub` 创建一个封闭的对话空间。
*   引入 **MatchMaker (红娘)** Agent 来主持流程，破冰、引导话题、总结。
*   Agent 在回答对方问题时，会检索 LongTermMemory 中的用户真实数据。

**代码示例 (相亲会话)**：

```python
from agentscope.pipeline import MsgHub
from agentscope.message import Msg

async def run_matchmaking(agent_male, agent_female, matchmaker):
    # 创建对话环境
    async with MsgHub(
        participants=[agent_male, agent_female, matchmaker],
        announcement=Msg("system", "相亲开始，请双方Agent入场。", "system")
    ):
        # 红娘开场
        await matchmaker(Msg("MatchMaker", "欢迎两位，请先做个自我介绍吧。", "assistant"))
        
        # 双方交互 (轮流发言，或由红娘点名)
        msg = await agent_male() 
        msg = await agent_female(msg)
        
        # ... 多轮对话逻辑 ...
        
        # 红娘总结
        await matchmaker(Msg("MatchMaker", "第一轮了解结束，现在生成初步匹配报告。", "assistant"))
```

### 3.3 模拟阶段：婚后生活推演

**目标**：检验 Agent 在具体压力场景下的反应。
**实现方式**：
*   构建 **ScenarioGenerator (场景生成)** Agent，负责抛出突发事件。
*   事件库示例：
    *   “月底了，房贷还完只剩 1000 块，通过怎么分配？”
    *   “婆婆坚持要来住一个月，怎么处理？”
    *   “孩子在学校打架了，老师叫家长，谁去？”
*   双方 Agent 基于用户画像进行决策和对话。
*   最后由 **Evaluator (评估)** Agent 对两人的配合度打分。

**Prompt 设计思路**：
*   **Avatar Agent**: "现在发生了 [事件]。基于你记忆中的用户性格（急躁/冷静、节约/大手大脚），你会怎么对你的伴侣说？请保持真实，不要刻意讨好。"

---

## 4. 开发步骤

1.  **环境搭建**：
    *   安装 AgentScope: `pip install agentscope`
    *   配置 LLM API Key (如 DashScope, OpenAI)。
    *   配置 Vector DB (如果使用 Mem0/ReMe 的高级功能)。

2.  **原型开发 (MVP)**：
    *   实现 `TrainerAgent`，跑通“问答-记忆”流程。
    *   验证记忆检索准确性（问 Agent：如果不喜欢吃辣，去四川餐厅你会点什么？）。

3.  **多 Agent 联调**：
    *   创建两个不同性格的 Agent。
    *   实现简单的 `MsgHub` 对话。

4.  **场景库构建**：
    *   编写 5-10 个典型婚姻冲突场景的 Prompt 模板。

5.  **前端/交互层** (可选)：
    *   可以使用 AgentScope 的 `A2UI` 或简单的 Gradio/Streamlit 界面展示聊天过程。

## 5. 关键难点与解决方案

*   **难点 1：Agent 过度客气**
    *   *解决*：在 System Prompt 中强调“Roleplay”指令，要求“User Persona”优先于“Helpful Assistant”原则。明确指示“如果遇到原则问题，可以争吵”。
*   **难点 2：记忆检索不准确**
    *   *解决*：优化 Embedding 模型；在检索时使用 Hybrid Search (关键词+语义)；在 System Prompt 中加入 Memory Summary 步骤。
*   **难点 3：对话死循环**
    *   *解决*：由 MatchMaker 或 ScenarioAgent 强制推进流程，设置最大对话轮次。

---

## 6. 总结

利用 AgentScope 强大的 **Multi-Agent 编排** 和 **Memory 管理** 能力，我们可以快速搭建出一个具备“深度模拟”能力的相亲应用。这不仅是一个聊天室，更是一个基于真实数据的“社会实验”平台。
