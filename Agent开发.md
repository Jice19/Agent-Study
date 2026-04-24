# Agent开发

### 1.ReAct思想

![image-20260424140442050](/Users/apple/Library/Application Support/typora-user-images/image-20260424140442050.png)

### 2.开发理解

一般来说我们不会用像ChatGPT这种模型直接作为我们的后端服务引擎，OpenAI也不允许，而是基于大语言模型封装对应的api暴露出模型的能力，期间会去处理Memory等等

### 3.agent的主要分类，可能有交叉

| 类型                             | 核心特点                                                     |
| -------------------------------- | ------------------------------------------------------------ |
| **Action**              行动代理 | 模型直接调用方法拓展能力（比如调用 API、操作文件、控制机器人） |
| **Simulation **    模拟代理      | 角色扮演，通过promt不断训练模型，训练成为一个专家角色        |
| **Autonomous**  自主智能体       | 完全自主，还需迭代，整合更多工具调用。 Auto-gpt              |

### 4. 技术理解（function Call、promt工程）

- function Call ： 模型调用方法去拓展自身能力 （查数据库之类的能力）

- promt工程 -优化效果：

>**Zero-shot**：啥例子不给，直接答
>
>**One-shot**：给 1 个例子
>
>**Few-shot**：给少量例子，规范输出
>
>**CoT**：分步思考，提升复杂问题正确率

- python agent核心api - import 使用

>`requests` 发请求
>
>`json` 解析模型返回
>
>`openai` 调用大模型
>
>`re` 提取 Thought/Action
>
>`os` 读环境变量
>
>`datetime` 传时间
>
>`lru_cache` 缓存
>
>`subprocess` 执行命令
>
>`redis` 分布式缓存
>
>`pydantic` 工具参数校验

### 5. auto-GPT 完全智能体探索

- 组成

>AutoGPT = **LLM（大脑）+ ReAct（循环）+ 工具（手脚）+ 向量记忆（长期上下文）**

- ##### 和 Zero/Few-Shot、CoT、ReAct 的关系

  ###### 1）Zero/Few-Shot

  - AutoGPT 的每个步骤，本质都是**Few-Shot + CoT**：
    - 给 LLM 的 Prompt 里，自带 “任务格式示例”（Few-Shot）
    - 强制分步思考（CoT），避免直接给答案

  ###### 2）CoT（思维链）

  - AutoGPT 强制开启 CoT：每一步都要写 “思考过程”，再输出行动，提升复杂任务正确率

  ###### 3）ReAct

  - AutoGPT = **ReAct + 工具调用 + 长期记忆**
  - ReAct 是它的核心工作流，让 “思考→行动→观察” 循环起来

### 6.市面上常见agent

>ChatRobot (聊天)、 Evaluation（评估能力）、RAG（向量检索）、Reflection（反思）、Planning（规划）