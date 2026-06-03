# LangGraph 基础笔记

## 1. 核心三要素：State → Graph → Compile

LangGraph 本质是一个**状态机**，三个步骤构建：

```python
from langgraph.graph import StateGraph
from typing_extensions import TypedDict

# ① 定义 State（图的数据结构，贯穿所有节点的共享数据）
class State(TypedDict):
    messages: list[AnyMessage]
    extra_field: int

# ② 用 State 创建图
graph_builder = StateGraph(State)

# ③ 编译成可执行对象
graph = graph_builder.compile()
```

---

## 2. 消息类型（Messages）

LangChain 中的三种消息角色：

| 类型 | OpenAI 对应 | 用途 |
|------|------------|------|
| `SystemMessage` | system | 设定 AI 的行为规则 |
| `HumanMessage` | user | 用户的输入 |
| `AIMessage` | assistant | AI 的回复 |

使用示例：

```python
from langchain.schema import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage(content="你是一个乐于助人的AI助手"),
    HumanMessage(content="你好！"),
    AIMessage(content="你好！我是AI助手"),
    HumanMessage(content='Python里如何写"Hello World"')
]
response = llm.invoke(messages)
```

---

## 3. 节点（Nodes）与边（Edges）

### 3.1 基本概念

```python
# 定义节点函数，签名: (state) -> dict，返回的 dict 会部分更新 state
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# 注册节点（直接传函数即可，无需 RunnableLambda 包装）
graph_builder.add_node("chatbot", chatbot)

# 边：固定路由
graph_builder.add_edge(START, "chatbot")   # 入口 → 节点
graph_builder.add_edge("chatbot", END)     # 节点 → 出口
```

### 3.2 图结构

```
START → chatbot → END
```

### 3.3 入口设置的两种等价写法

```python
# 写法1：用 START 边（推荐，与出口风格统一）
builder.add_edge(START, "user_input")

# 写法2：用 set_entry_point（内置方法）
builder.set_entry_point("user_input")
```

### 3.4 流式输出

```python
for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
    for value in event.values():
        print("Assistant:", value["messages"][-1].content)
```

---

## 4. Reducer（状态合并策略）

**这是 LangGraph 最关键的概念之一**：节点返回的 dict 如何合并到 state 中。

```python
from typing import Annotated
from operator import add

class State(TypedDict):
    foo: int                              # 无 reducer → 直接替换
    bar: Annotated[list[AnyMessage], add] # 有 reducer → 用 add 合并（追加）
```

### 两种更新策略对比

| 字段定义 | 更新行为 | 示例 |
|---------|---------|------|
| `foo: int` | **替换**：新值覆盖旧值 | `2` 替换 `1` |
| `bar: Annotated[list, add]` | **合并**：`operator.add` 列表拼接 | `["hi"] + ["bye"]` = `["hi", "bye"]` |

### 自定义合并函数

可以根据需要自定义 reducer，例如取最大值、最小值、去重合并等。

---

## 5. 多 Schema：输入/输出/整体/私有状态

不同节点可以使用**不同的输入输出 Schema**，实现精细的数据访问控制。

### 5.1 Schema 类型

```python
class InputState(TypedDict):    # 图的入口 schema，过滤外部输入
    user_input: str

class OutputState(TypedDict):   # 图的出口 schema，过滤输出
    graph_output: str

class OverallState(TypedDict):  # 贯穿全图的共享状态
    foo: str
    user_input: str
    graph_output: str

class PrivateState(TypedDict):  # 只在特定节点间传递的私有数据
    bar: str
```

### 5.2 节点间的"私密通道"

```python
def node_1(state: OverallState) -> Node1Output:  # 返回 private_data
    return {"private_data": "set by node_1"}

def node_2(state: Node2Input) -> OverallState:    # 能接收 private_data
    ...

def node_3(state: OverallState) -> OverallState:  # 看不到 private_data！
    ...
```

**关键理解**：node_1 产生的 `private_data`，node_2 能看到，但 node_3 看不到。只有声明了对应输入类型的节点才能访问特定字段。

### 5.3 数据流图

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   node_1    │───▶│   node_2    │───▶│   node_3    │
│ InputState  │    │ OverallState│    │ PrivateState│
│ → Overall   │    │ → Private   │    │ → Output    │
└─────────────┘    └─────────────┘    └─────────────┘
```

---

## 6. 多轮对话的消息累积

利用 `operator.add` 实现对话历史自动追加：

```python
class ChatState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]  # 自动追加
```

```python
def handle_user_input(state):
    return {"messages": [HumanMessage(content=user_input)]}   # 追加用户消息

def generate_ai_response(state):
    recent_history = state["messages"][-6:]  # 取最近 6 条作为上下文
    response = model.invoke(recent_history)
    return {"messages": [response]}           # 追加 AI 回复
```

每次 `invoke` 后 messages 不断增长：`[系统提示, 用户1, AI1, 用户2, AI2, ...]`

---

## 7. Map-Reduce 并行模式

### 7.1 add_conditional_edges 条件边 API

`add_conditional_edges(source, router_func)` — 与普通边的区别：

```python
# 普通边：固定路由，from → to 永远不变
builder.add_edge(START, "generate_joke")

# 条件边：运行时根据 state 动态决定下一步走到哪
builder.add_conditional_edges(START, continue_to_jokes)
```

### 7.2 router_func 的三种返回值 → 三种行为

```python
# ① 返回字符串 → 单一路由
def router(state):
    return "node_a"

# ② 返回字符串列表 → 串行走到多个节点
def router(state):
    return ["node_a", "node_b"]

# ③ 返回 Send 列表 → 并行分发，每个 Send 携带独立参数
def router(state):
    return [Send("generate_joke", {"subject": s}) for s in state['subjects']]
```

### 7.3 并行如何实现：分三步

#### 第一步：`Send` 不是调用函数，是"任务单"

```python
Send("generate_joke", {"subject": "cats"})
#     ↑ 目标节点名      ↑ 传给该节点实例的独立参数
```

这行代码**不会立即执行** `generate_joke`。它只是创建一个"任务描述"，告诉 LangGraph 引擎："稍后请以 `{"subject": "cats"}` 为参数，跑一次 `generate_joke` 节点"。

#### 第二步：返回多个 Send → 引擎扇出 + 并行推送

```python
def continue_to_jokes(state):
    return [
        Send("generate_joke", {"subject": "cats"}),   # 任务单1
        Send("generate_joke", {"subject": "dogs"}),   # 任务单2
    ]
```

当 router_func 返回 **Send 列表**时，LangGraph 引擎识别后做两件事：

1. **扇出（Fan-out）**：列表里有几个 Send，就创建几条执行分支
2. **并行推送**：把每条分支的任务单分别塞给目标节点，**各分支互不等待、同时跑**

```
                    Send1 ──▶ generate_joke(subject="cats") ──▶ {"jokes": ["Joke about cats"]}
                   /
START → continue_to_jokes
                   \
                    Send2 ──▶ generate_joke(subject="dogs") ──▶ {"jokes": ["Joke about dogs"]}
```

#### 第三步：Reducer 自动合并结果

所有分支跑完后，各自返回的 `{"jokes": [...]}` 通过 `Annotated[list[str], operator.add]` 自动拼在一起：

```python
["Joke about cats"] + ["Joke about dogs"] = ["Joke about cats", "Joke about dogs"]
```

### 7.4 一句话总结

**并行不是靠多线程，是靠 `Send` 列表让引擎一次性扇出多条执行分支**。每条分支是同一个节点、不同输入，引擎内部并发调度，结果通过 reducer 自动合并。

### 7.5 完整代码

```python
from langgraph.types import Send

def continue_to_jokes(state: OverallState):
    # 为每个 subject 创建一个并行任务
    return [Send("generate_joke", {"subject": s}) for s in state['subjects']]

builder.add_node("generate_joke", lambda state: {"jokes": [f"Joke about {state['subject']}"]})
builder.add_conditional_edges(START, continue_to_jokes)  # 条件分发
builder.add_edge("generate_joke", END)
```

输入 `{"subjects": ["cats", "dogs"]}` → 输出 `{"jokes": ["Joke about cats", "Joke about dogs"]}`

---

## 8. 总览：一张图概括所有概念

```
                    ┌──────────────────────────────┐
                    │   StateGraph(OverallState)    │
                    │   ┌─────────────────────┐    │
  InputState ──────▶│   │  Shared State        │    │──────▶ OutputState
  (入口过滤)         │   │  - messages (add)     │    │         (出口过滤)
                    │   │  - foo (replace)      │    │
                    │   └─────────────────────┘    │
                    │        ▲      │              │
                    │        │      ▼              │
                    │   ┌────────┐ ┌────────┐     │
                    │   │ Node A │ │ Node B │ ... │
                    │   └────────┘ └────────┘     │
                    │    PrivateState 可做私密通道  │
                    └──────────────────────────────┘
                              │
                     conditional_edges + Send
                        实现 Map-Reduce 并行
```

| 概念 | 作用 |
|------|------|
| **State** | 图的共享内存，TypedDict 定义 |
| **Node** | 处理单元，`(state) -> dict` |
| **Edge** | 固定路由，`add_edge(from, to)` |
| **Reducer** | 控制字段更新方式：替换 or 合并 |
| **Schema 分离** | Input/Output/Overall/Private 控制节点可见性 |
| **Send + conditional_edges** | 并行分发，实现 Map-Reduce |
| **START / END** | 虚拟节点，标记图的入口和出口 |
