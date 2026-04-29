# Agent开发

## 1.ReAct思想

![image-20260424140442050](/Users/apple/Library/Application Support/typora-user-images/image-20260424140442050.png)

## 2.开发理解

一般来说我们不会用像ChatGPT这种模型直接作为我们的后端服务引擎，OpenAI也不允许，而是基于大语言模型封装对应的api暴露出模型的能力，期间会去处理Memory等等

## 3.agent的主要分类，可能有交叉

| 类型                             | 核心特点                                                     |
| -------------------------------- | ------------------------------------------------------------ |
| **Action**              行动代理 | 模型直接调用方法拓展能力（比如调用 API、操作文件、控制机器人） |
| **Simulation **    模拟代理      | 角色扮演，通过promt不断训练模型，训练成为一个专家角色        |
| **Autonomous**  自主智能体       | 完全自主，还需迭代，整合更多工具调用。 Auto-gpt              |

## 4. 技术理解（function Call、promt工程）

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

## 5. auto-GPT 完全智能体探索

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

## 6.市面上常见agent

>ChatRobot (聊天)、 Evaluation（评估能力）、RAG（向量检索）、Reflection（反思）、Planning（规划）

## 7. RAG && Topk

之前直接用的pgVector操作的，接下来需要了解如何切片，如何去检索的（余弦相似度/欧式距离）？如果知识库里面没有检索到对应知识应该如何处理？（webSearch）

>1. 文档切片 → 转**向量 Embedding**，存入向量库
>2. 用户问题 → 同样转向量
>3. 计算**向量相似度**（余弦相似度 / 欧氏距离）
>4. 按相似度从高到低排序
>5. 截取**前 K 条**最相似文档 → 塞进大模型 Prompt （TopK）
>6. 大模型结合检索到的内容回答

- CRAG(corrective RAG). -  纠正/反思检索内容，以及没有检索到的知识处理
- self - RAG. -   拿到检索结果，给大模型润色/整合/反思/过滤，不断改正生成结果

### 

## 8. multi - agent

| 维度         | LLMChain                   | RouterChain                    |
| ------------ | -------------------------- | ------------------------------ |
| **核心作用** | 执行单一 LLM 任务          | 动态选择并执行子链             |
| **执行路径** | 固定一条                   | 多条分支，运行时选             |
| **组成**     | 1 个 Prompt+1 个 LLM       | 1 个路由层 + 多个子链          |
| **输入处理** | 直接传给 Prompt            | 先分类，再转发子链             |
| **典型场景** | 翻译、摘要、写作（单任务） | 智能客服、意图识别、多任务助手 |
| **依赖关系** | 独立使用，或作为子链       | 必须依赖多个 LLMChain / 子链   |

>agent的能力取决于你写的提示词，很难有完美的提示词，所以当下multi-agent模式效率会更高



## 9. langchain / langgraph

| 特性     | LangChain（LLMChain / RouterChain） | LangGraph                                  |
| -------- | ----------------------------------- | ------------------------------------------ |
| 结构     | 线性链条、静态分支                  | 有向图、节点 + 条件边                      |
| 执行方式 | 顺序执行、一次性跑完                | 支持**循环、回退、迭代**                   |
| 状态管理 | 无统一全局 State                    | 全局 State 贯穿全流程                      |
| 分支能力 | Router 静态选链，跑完结束           | 任意条件分支、多轮判断                     |
| 自修正   | 无法自我纠错、不能回头              | 可反思、重试、多轮优化                     |
| 适用     | 简单 RAG、单任务、固定流程          | 复杂 Agent、深度 RAG、工具调用、多轮智能体 |

## 10. agent基本要素

- **规划 (Planning)**：拆解复杂任务，支持自我反思、迭代修正，制定执行步骤；
- **记忆 (Memory)**：分为短期上下文记忆与长期向量持久化记忆，支撑历史信息检索与跨轮对话；
- **工具 (Tools)**：封装外部拓展能力，弥补大模型原生能力不足；
- **行动 (Action)**：模型结合上下文与规划决策，调用对应工具完成实际执行，形成闭环。

**闭环**： 

> 思考 (Plan) → 决策选工具 (Action) → 调用工具 (Tools) → 结果写入记忆 (Memory) → 循环迭代

## 11.RAG

### 1. 初识RAG

#### 11.1 为什么需要RAG？（联网搜索除外）

- 局限性

>1️⃣ 时效性：大模型无法查询最新的时事
>
>2️⃣ 知识覆盖度：虽然大模型的训练数据集庞大，可能无法覆盖特定领域特定深度的信息
>
>3️⃣ 幻觉问题： AI幻觉，大模型胡说八道
>
>**AI幻觉解决方案： RAG 和 微调**
>
>- 微调：针对特定领域用专门的数据集进行调整和优化，可能会导致其他领域的能力退化
>- RAG：足够便宜，效果足够好

#### 11.2  什么是RAG

（**1）外挂知识库的方式，成本和复杂度比微调更低**

**（2）方案比对**

| 方法       | 知识更新能力          | 实现复杂度 | 成本 | 适用场景             |
| ---------- | --------------------- | ---------- | ---- | -------------------- |
| 提示词工程 | 低 (依赖模型原有知识) | 低         | 低   | 静态知识场景         |
| 微调       | 中 (需要重新训练)     | 高         | 高   | 领域知识需要定期更新 |
| RAG        | 高 (实时检索最新数据) | 中         | 中   | 需要最新信息的场景   |

- RAG在知识库更新方面表现最佳，可以实时访问最新数据源
- 微调需要定期重新训练模型才能纳入新知识
- 提示词工程及户无法解决知识更新问题，完全依赖训练模型的数据集

**（3）检索 + 增强 + 生成 通过代码进行检索，以前是关键字检索，现在是语义/向量检索**

>RAG的本质： RAG = 大模型LLM + 外部数据
>
>- **以前**直接问LLM
>
>- **现在**新增知识库（向量：数字存储）, 1️⃣先查询知识库，基于向量，语义检索；2️⃣ 把提示词增强（提问+提问相关的内容）；3️⃣ LLM生成答案（提炼归纳总结）

![image-20260425143442227](/Users/apple/Library/Application Support/typora-user-images/image-20260425143442227.png)

#### **(4) 初体验：基于FastGPT搭建RAG**

重点不在FastGPT，在于体验搭建RAG知识库

**（5）Naive RAG 流程**

1. 索引化：文档 → 分块 → 向量化（向量模型） → 存储         

   > **索引的目的：**提升查询的速度，其中一个算法举例：构建索引树，防止全文检索
   >
   > ！自行补充知识： 向量检索算法

2. 检索：用户提问 → 向量化 → 检索数据库 → 得到 top-K 个相关文档块

   >top-K是取关联度前k条数据，top-P = 2 是取和<=2的前n条数据（0.8+0.7+0.5(取以前的) +0.2）

3. 增强生成：增强提示词 (原始问题 + 相关文档块) → LLM → 生成答案

### **（6）文档分块**

现阶段先只考虑NLP（自然语言）知识库,

- **流程如下：**

>1️⃣ 一般将各种知识文档（txt、doc、html）转换成 txt
>
>2️⃣ 然后根据我们的规则进行文档分chunk （chunk块满足一定语义和向量模型的要求）
>
>3️⃣ 通过**向量模型**（把自然语言 -> 对应的向量）存到**向量数据库**（vector DB）里面
>
>4️⃣ 根据用户问题 进行检索增强

- **分块策略 （详情参考RAG分块策略文档）**

>1️⃣ 固定字数   - 语义不行
>
>![image-20260425155900739](/Users/apple/Library/Application Support/typora-user-images/image-20260425155900739.png)
>
>2️⃣ 固定字数结合滑动窗口 - 现象 ： 第二块的开头有第一块的最后一部分 - 实现了一定优化（重复块一般在一块的10% - 15%）
>
>![image-20260425155935893](/Users/apple/Library/Application Support/typora-user-images/image-20260425155935893.png)
>
>3️⃣ 根据句子切割 - 正则表达式(re模块) -  优点：能够保留最小语义 ， 缺点：句子太小，RAG的检索会检索更多句子
>
>4️⃣ 利用递归拆分 - `langchain的RecursiveCharacterTextSplitter`

```
splitter = RecursiveCharacterTextSplitter(
    chunk_size=20,  # 分割长度
    chunk_overlap=5,  # 重叠长度 /重叠窗口大小
   # separators=["\n\n", "\n", " ", ""],
    separators = ["\n\n", "\n", "。", "，"] // 检索到这些符号执行切割
)
```

**（...）一些细节点补充**

- 一般在企业级项目我们会在用户输入之后做一个判断 - 是否需要使用知识库去检索
- Naive RAG只是跑基本流程，每一步的优化后续学习 `Advanced RAG`
- 分块大小上限：根据向量模型的每批次支持的max-token（每一块的最大token：maxtoken/批次大小）

### 2. 向量检索

> Transformer（512维），给予更多的维度可以进行更多的特征向量的表达
>
> 在RAG当中，**一个文本块对应一个向量**

#### （1）向量模型（Embeddings） 

> 常用的 qwen-EmBadding-model 就是基于我们的Transformer来实现的，只是保留了一个Transformer层，参数机制层做了权重分配，不同的向量嵌入模型得出的向量也可能是不一样的
>
> - 向量维度：多少个数字去表达一个文本的坐标（64min - max）
> - 批次大小（batch）：一次性能够处理的文本块数量

1、**向量模型的选择？**（本地部署 or  线上向量模型） - 考虑数据的安全合规性

2、向量化存储和检索的维度一定要保持一致

```
//接入向量嵌入模型(client_qwen.embeddings.create)
def get_embeddings(texts, model, dimensions=1024):
    data = client_qwen.embeddings.create(input=texts, model=model, dimensions=1024).data
    return [x.embedding for x in data]
```



#### （2）向量数据库  

>不仅存储向量，还会存储我们的原始语料

1、选型

- 传统数据库（pg、redis都已经支持了向量检索）MySql可以存向量数据，但是不支持向量检索

- 向量数据库：chroma、margo、vespa、Milvus（根据文本检索搜索向量）

  ![image-20260425200610380](/Users/apple/Library/Application Support/typora-user-images/image-20260425200610380.png)

2、chroma存储检索流程

>1️⃣ 加载文档，读取数据
>
>2️⃣ 初始化向量数据库对象
>
>3️⃣ 读取的content使用langchain的递归切片，然后存储向量数据库（**向量+文档**都需要存储）
>
>向量库的存储格式（示例） ['我爱你'，'中国'， ‘我们爱你’]  🆚  [[1,2,4,2...], [31,3425,13], [34,13,5,14]]一一对应
>
> 4️⃣ 根据问题检索数据库，返回对应文档片段（支持top-k）
>
>5️⃣ 写好提示词（role、object、measure、向量数据库中检索文档）

### (3)chroma使用指南

###### 一、创建 Client（客户端实例）

Chromadb 提供两种核心客户端模式，决定数据是否持久化：

| 模式       | 代码                                              | 说明                                                     |
| ---------- | ------------------------------------------------- | -------------------------------------------------------- |
| 内存模式   | `client = chromadb.Client()`                      | 数据仅存于内存，程序关闭后丢失，适合临时测试             |
| 持久化模式 | `client = chromadb.PersistentClient(path="路径")` | 数据会保存到本地指定路径，重启程序后可恢复，适合正式场景 |

------

###### 二、Collection（集合）的基础操作

Collection 是 Chromadb 中存储向量、文档和元数据的核心单元，对应传统数据库的 “表” 概念。

| 操作                      | 代码                                                         | 说明                                       |
| ------------------------- | ------------------------------------------------------------ | ------------------------------------------ |
| 列出所有集合              | `client.list_collections()`                                  | 查看当前数据库中所有已创建的集合           |
| 创建集合                  | `client.create_collection(name="集合名", embedding_function=向量化函数)` | 新建集合，可指定自定义向量化函数           |
| 获取集合                  | `collection = client.get_collection(name="my_collection", embedding_function=emb_fn)` | 获取已存在的集合，需传入创建时的向量化函数 |
| 不存在则创建 / 存在则获取 | `client.get_or_create_collection(name="集合名")`             | 更安全的方式，避免重复创建报错             |
| 删除集合                  | `client.delete_collection(name="my_collection")`             | 删除指定集合，会清空集合内所有数据         |

------

###### 三、Collection 核心功能

##### 1. 添加文档与向量

```
collection.add(
    documents=[...],       # 可选：原始文本内容，方便后续查看
    embeddings=[[...], [...]],  # 必须：文档对应的向量表示
    ids=[...]              # 必须：每个文档的唯一 ID，不可重复
)
```

- 补充说明：`documents` 可选，但推荐传入，方便后续溯源；`embeddings` 和 `ids` 必须一一对应，长度一致。

##### 2. 相似度检索 ！！！

```
results = collection.query(
    query_embeddings=[0.1, 0.2, ...],  # 查询向量，需和插入时维度一致
    n_results=5,                        # 返回前 5 个最相似的结果
)
```

- 返回结果中，`distances` 字段表示向量间的距离，**数值越小，相似度越高**。

------

###### 四、关键注意事项（避坑指南）

| 项目         | 核心要求                                        | 影响                               |
| ------------ | ----------------------------------------------- | :--------------------------------- |
| 向量维度一致 | 查询和插入时，必须使用**同一个 Embedding 模型** | 维度不一致会直接报错，无法完成检索 |
| ID 唯一性    | 插入时每个文档必须有唯一的 ID                   | 重复 ID 会导致插入失败或覆盖数据   |
| 距离与相似度 | `distances` 数值越小，向量相似度越高            | 不要误判 “距离大 = 相似度高”       |
| 支持批量操作 | `add` 和 `query` 都支持传入多个文档 / 向量      | 可以一次性处理多条数据，提升效率   |

>补充疑惑：
>
>##### ✅ **Chroma 里的 Collection = 数据库里的 “表”**
>
>你完全可以把：
>
>- **一个 Collection = 一张表**
>- **一个文档 = 表里的一行数据**
>
>##### ✅ **不需要一个文档建一个 Collection！绝对不要！**
>
>###### ✅ **推荐：一个领域 = 一个 Collection**

#### 4、向量相似度的判断

> 在python中采用 numpy进行计算

- 余弦相似度。 cos 余弦相似度越大，两个向量的距离越小

```
dot(A,B)  //求的是 A模*B模 *cos角度
越小越近
```

- 欧式距离l2   两向量终点端点的距离

```
norm(A)
```

#### 5、键值对数据源

>数据库的其他方法都是一样的，只是存储的时候需要存储 【问题的向量， 问题对应答案的原文】
>
>检索的时候只需要将query向量化去检索出对应的问题的向量，直接返回对应的回答的原文就行

#### 6、常见的检索方式

1、基本理解

- 关键字检索。（传统MySql数据库的关键字查询）

```
select * from user where name = '张%'
```

- 大模型的向量相似度检索（RAG）
- 全文检索  - 将query切割之后去检索查询

> 关键字检索：查「字」（严格字符串匹配，不懂语义）

> 全文检索：查「词」（分词后匹配，不懂语义，比关键字灵活）

> 向量相似度检索（RAG 核心）：查「意思」（语义匹配，最智能）

2、详细对比

###### 一、全文检索    - 可以使用bm25和jieba库实现全文检索

- **匹配层级**：词级 / 短语级匹配，依赖显式关键词的精确或模糊匹配（如通配符、模糊查询）
- **语义能力**：无法理解语义深层关联，例如 “计算机” 和 “电脑” 会被视为不同查询词，除非配置同义词库
- **核心算法**：基于词频、逆文档频率、位置权重等统计特征，通过**BM25、TF-IDF**等算法计算匹配度，得分过程透明可解释
- **特点**：侧重精确性与可解释性

------

###### 二、基于词向量的相似度检索

- **匹配层级**：语义级理解，能捕捉文本深层语义关联（如同义词、上下文歧义、逻辑推理）
- **语义能力**：无需显式配置规则，可识别不同表述下的相似语义，例如 “如何修复笔记本故障” 与 “电脑主板维修指南” 会被判定为高相关
- **核心逻辑**：将文本转化为向量，通过向量空间距离衡量相似度
- **特点**：侧重语义理解与泛化能力，但向量是 “黑盒表征”，相似度结果难以直观解释

#### 7、混合检索（bm25全量检索 + 向量相似度检索）

##### 一、 BM25 全文检索模块 (`bm25_search`)

###### 目标

基于词频匹配，快速计算查询与文档的字面相似度。

###### 步骤

1. **文档分词**：使用 `jieba.lcut` 对所有 `instructions` 进行分词，构建分词后的语料库 `tokenized_corpus`。
2. **初始化 BM25 模型**：将分词后的语料库传入 `BM25Okapi`，预计算文档词频统计信息。
3. **查询分词**：对用户输入的 `query` 同样使用 `jieba.lcut` 分词。
4. **计算 BM25 分数**：调用 `get_scores` 得到查询与每个文档的原始相似度分数。
5. **分数归一化**：
   - 公式：`(分数 - 最小值) / (最大值 - 最小值)`
   - 目的：将 BM25 分数缩放到 `[0, 1]` 区间，便于后续与向量分数融合。
   - [1,2,3,4,5] -> [0,0.25,0.5,0.75,1]

##### 二、 向量检索模块

1. **获取向量**：

- 调用 `get_embeddings_batch` 分别获取 `query` 和所有 `instructions` 的向量。

2. **计算欧氏距离**：

- 使用 `np.linalg.norm` 计算查询向量与每个文档向量的 L2 距离。
- 距离越小，语义越相似。

3. **距离转相似度并归一化**：

- 公式：`1 - (距离 - 最小距离) / (最大距离 - 最小距离)`
- 目的：将距离转换为 `[0, 1]` 区间的相似度分数（距离越小，分数越高）

##### 三 、 混合检索融合逻辑 (`hybrid_search`)

###### 目标

结合 BM25 的字面匹配能力和向量检索的语义理解能力。

###### 步骤

1. **获取单路分数**：

   - 调用 `bm25_search` 得到归一化后的 BM25 分数。
   - 调用 `vector_search` 得到归一化后的向量相似度分数。

   

2. **加权融合**：

   - 公式：`combined_score = bm25_weight * bm25_score + (1 - bm25_weight) * vector_score`
   - 默认 `bm25_weight=0.5`，即两路权重各占 50%。

   

3. **排序取 Top-K**：

   - 对融合后的分数进行降序排序，获取索引。
   - 根据索引提取对应的 `outputs` 作为最终结果。

## 12. langhcain

### 12.1 存在的意义

>- 原生构建RAG，langchain也可以更高效地构建RAG
>- 不仅可以构建RAG，也可以构建智能体
>- 当下时代AI工程师岗位的核心素养



### 12.2 什么是 LangChain？

#### 从 LangChain 0.3 到 LangChain 1.0

##### 版本与发布时间

- **LangChain V1.0 上线时间**：2025 年 10 月 23 日正式发布
- 官宣时间：2025 年 10 月 22 日，官方宣布 LangChain 1.0 与 LangGraph 1.0 即将发布

------

##### (1) 核心定位

LangChain V1.0 相较于 V0.3，是一次**面向生产级工程化的重大升级**，在 API 设计、架构、可维护性、稳定性与扩展能力上实现了质的飞跃。

------

##### (2) 关键升级亮点

1. **统一 Agent 创建接口**
   - 新增 `create_agent()`，标准化 Agent 构建方式
2. **中间件系统（Middleware）**
   - 提供细粒度流程控制，方便自定义处理逻辑
3. **标准化输出**
   - `.content_blocks`：无论使用哪家模型，输出统一为结构化内容块
4. **结构化输出原生支持**
   - 将结构化输出能力直接集成到主循环中，无需额外适配
5. **基于 LangGraph 的底层架构**
   - Agent 本质是 LangGraph 编排的状态图（StateGraph），原生支持复杂状态管理与流程控制
6. **包结构精简与平滑迁移路径**
   - 移除冗余模块，核心包更轻量
   - 旧版功能（如 `LLMChain`、`ConversationBufferMemory`）迁移到 `langchain-classic` 兼容包

------

##### (3) 一句话总结

> LangChain 1.0 是面向生产环境的稳定重构版本，**以 LangGraph 为核心，接口更统一、架构更清晰、兼容性更好**，是当前 AI Agent / RAG 开发的主流选择。

### 12.3   提示词模版

1️⃣ 字符串提示词模版 PromptTemplate

```
# 字符串提示词模板 {text}  占位符，通过text变量动态设置提示词内容
prompt = PromptTemplate(template="你是一个翻译助手，请讲以下内容翻译成{language}:{text}")

# 输入参数内容，构建真正的提示词
fact_prompt = prompt.format(language="中文", text="I am a handsome man")

result = model.invoke(fact_prompt)
```

2️⃣ 对话提示词模版   ChatPromptTemplate.from_messages

```
# 设置对话提示词模板，设置角色
prompt = ChatPromptTemplate.from_messages([
    # ("system", "你是一个翻译助手，请将以下内容翻译成{language}"),
    SystemMessagePromptTemplate.from_template("你是一个翻译助手，请将以下内容翻译成{language}"),
    # ("human", "{text}"),
    HumanMessagePromptTemplate.from_template("{text}")
    # AIMessagePromptTemplate  ai的角色消息，用来记录维持对话
])


# 输入参数内容，构建真正的提示词
fact_prompt = prompt.format(language="中文", text="I am a programmer")

result = model.invoke(fact_prompt)
```

3️⃣  FrewShot Promt

```
# 创建少样本示例的对象
prompt = FewShotPromptTemplate(
    examples=examples, # 示例样本
    example_prompt=prompt_sample, # 示例的提示模板
    prefix="你是一个数学专家, 能够准确说出算式的类型，", #前缀
    suffix="现在给你算式: {input} ， 值: {output} ，告诉我类型：", #后缀
    input_variables=["input", "output"]
)
```

4️⃣ 可选参数提示词

```
prompt_txt = "讲一个关于{date}的小故事：{text}"

prompt = PromptTemplate(template=prompt_txt, input_variables=["date", "text"])

# 输入参数内容，构建真正的提示词
half_prompt = prompt.partial(date="2008-08-08")

result = model.invoke(half_prompt.format(text="一个幸福的爱情故事"))
#3.获取打印结果
print(result.content)

result = model.invoke(half_prompt.format(text="一个悲伤的爱情故事"))
```

### 12.4    chain的基础认知（后续深入）

我们定义提示词，发送给大模型，并且接受大模型的返回并解析输出三步，可以使用超级简洁的chain去调用，传入字典就可以完成整个流程

```
# 1.创建模型客户端
model = ChatTongyi()
#2.构建提示词，访问模型
prompt = PromptTemplate(template="你是一个翻译助手，请讲以下内容翻译成{language}:{text}")
#3.解析大模型的返回
parser = StrOutputParser()

# 链的调用   在langchain中  "|" 是一个链的调用符
chain = prompt | model | parser
result = chain.invoke({"language": "中文", "text": "I am a programmer"})
```

>使整个过程处理更高效，并且能够构建更复杂的应用

### 12.5   输出解析器（parser）

- ###### 核心定义

  **输出解析器（Output Parser）**：负责获取大语言模型（LLM）的输出，并将其转换为程序可直接使用的、结构化的格式，解决 “模型输出是文本，程序需要特定数据格式” 的问题。

  ------

  ###### 常见解析器类型

  | 解析器名称                                       | 用途                                       | 适用场景                               |
  | ------------------------------------------------ | ------------------------------------------ | -------------------------------------- |
  | **StrOutputParser**                              | 最基础的解析器，直接将模型输出转换为字符串 | 通用场景，仅需获取纯文本结果           |
  | **CommaSeparatedListOutputParser（CSV 解析器）** | 将模型以逗号分隔的输出，解析为 Python 列表 | 提取关键词、标签、选项等多值输出       |
  | **DatetimeOutputParser（日期时间解析器）**       | 将模型输出解析为标准日期时间格式           | 日程安排、时间计算、格式标准化         |
  | **JsonOutputParser（JSON 解析器）**              | 强制模型输出符合指定结构的 JSON 对象       | 结构化数据提取、API 参数生成、工具调用 |

  ------

  ###### 核心总结

  输出解析器是 LLM 输出与程序数据格式之间的**翻译器**，让模型生成的自然语言，变成代码能直接处理的列表、日期、JSON 等结构化数据。

### 12.6  langchain程序的部署（Fastapi + langserve）

>部署之后，可以通过 `localhost:8000/lanchainServer/invoke`传参数调用api

```
#部署为服务  部署成web应用的框架
app = FastAPI(title="基于LangChain的服务",version="V1.5",description="翻译服务")
# 函数和访问路径一一对应
add_routes(app, chain,path="/lanchainServer")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
```



## 13. FastApi - study

>详见FastApi入门.md资料





## 14. Langchain Expression Lauguage （LCEL）

#### （一）链的介绍和调用

- 流式输出    stream
- 接受输入输出 invoke
- 批量处理输入输出   batch

#### （二）链的sequence构建

>chain = prompt | model | outParser       ===      chain = RunnableSequence(prompt,model,outParser)

#### （三）RunnableLambda封装函数 & 装饰器在chain中调用

###### 一、核心作用

LCEL 链式语法仅支持串联 Runnable 对象，原生普通函数无法直接接入链式管道。

二者核心作用：**把普通 Python 函数转为标准 Runnable 对象**，使其可以通过 `|` 加入链路、支持统一调用方式。

###### 二、RunnableLambda

1. 手动将普通函数包装为可运行组件。
2. 适用场景：临时简单逻辑、匿名函数、一次性代码片段。
3. 特点：灵活轻量，按需包装，适合短逻辑。

###### 三、@chain 装饰器

1. 装饰器修饰函数，自动将函数转为 Runnable，无需手动包装。
2. 适用场景：复用性高的自定义函数、复杂业务处理逻辑。
3. 特点：代码简洁，可读性强，适合长期复用的自定义链路逻辑。

###### 四、共性

1. 底层能力完全等价，都兼容 LCEL 完整语法。
2. 统一支持同步调用、批量调用、流式调用三种执行方式。
3. 可搭配字段取值工具、提示词、大模型、输出解析器自由拼接组合。

###### 五、使用选择

1. 临时简单处理逻辑，优先使用 RunnableLambda。
2. 独立封装、需要多次复用的自定义函数，优先使用 @chain 装饰器。

#### (四) langchian高级特性和组件

1️⃣` RunnableParallel/ RunnableMap`

支持并行执行，返回字典

```
# 测试parallel并行执行
# 同时执行三个函数，输出结果以字段的形式返回{a=2,b=2,c=3}
# chain = RunnableParallel(
#     a=add_one,
#     b=mul_two,
#     c=mul_three,
# )

chain = RunnableMap(
    a=add_one,
    b=mul_two,
    c=mul_three,
)
# 调用链
print(chain.invoke(1)) #{a=2,b=2,c=3}
```

2️⃣ langchain.core 包里面`set_debug`查看链路日志bug

3️⃣ RunnableSequence 构建按顺序实行的 chain

4️⃣ RunnablePassThrough. -  对一个节点的输出做数据增强处理然后传递给下一个节点

>增强传递，需要传递键值对并且返回的是一个全新字典

```
# 数据增强，增强后进行继续传递  实现了给hello world输出数据增强
chain = RunnableParallel(
    passed = RunnablePassthrough().assign(modified= lambda x: x["k1"]+"!!!"),
)

# 增强调用，需要使用字典格式
print(chain.invoke({"k1": "hello world"}))

# 输出，可以将增强后的modefied传递给下一个节点进行使用
{'passed':{'k1':'hello world','modefied':'hello world!!!'}}
```

5️⃣ 预定义链：

- LangChain 官方提供了多种预制的 LCEL 链，可在官方 API 文档中查询：

  ```
  https://reference.langchain.com/python/langchain_classic/chains/
  ```

- ⚠️ 注意：位于 `Deprecated classes 和 Deprecated functions` 中的类与函数属于**已声明废弃**，不建议在新项目中使用。

  ------

  ######  示例：`create_stuff_documents_chain`

- **功能**：将多个文档内容合并成一个长文本，然后一次性交给 LLM 处理。

### （五）记忆Memory

##### 一、ChatMessageHistory

几个核心api

>```
>#  创建消息历史记录，存储组件
>chat_history = ChatMessageHistory()
>
># add_user_message() 添加用户的输入信息
># add_ai_message() 添加存储大模型的回复信息
># .messages 属性获取所有历史消息
>```

补充：**ChatMessageHistory** 本身不限制条数，但你传给 LLM 的历史消息越多，检索 / 理解效果会下降，成本会升高，速度会变慢，最终会超出模型最大长度报错 。**只存在运行内存里，临时存储、不落地、不持久化**。

⚠️ **必须限制历史轮数**（推荐保留最近 5～10 轮），手动保存上下文的时候提示词模版需要携带上上下文`MessagesPlaceholder(variable_name="messages")`,  #QA

##### 二、持久化记忆

1️⃣ 将历史会话存储在数据库中 （redis、Mysql）

- 安装docker 、启动redis 、下次启动指令(Mac)

```
//首次下载启动
brew install --cask docker
open /Applications/Docker.app
docker run -d --name myredis -p 6379:6379 redis
docker ps  //验证


//之后启动指令
# 1. 打开Docker
open -a Docker

# 2. 启动redis容器
docker start myredis

# 3. 查看是否运行
docker ps

# 4. 停止redis（关机前可选）
docker stop myredis
```

2️⃣ 自动管理存储对话 **RunnableWithMessageHistory**

```
//传递链、存储记忆函数、用户的输入
chatbot_with_his = RunnableWithMessageHistory(
    # 执行流程
    chain,
    # 记忆存储的位置的函数
    get_session_history,
    input_messages_key="input",
)
```

> 多用户对话存储需要session_id用户标识去区分上下文

## 15、阶段练习：基于Langchain的电商客户反馈系统

#### （一） 需求描述

>###### 情感分析：判断用户反馈的情感倾向
>
>###### 问题分类：识别反馈中的问题类型
>
>###### 紧急程度评估：根据内容判断处理优先级
>
>###### 生成回复草稿：根据分析结果生成初步回复

#### （二） 详细流程

>前置条件：基于Fastapi获取到用户的输入信息，然后在接口处调用langchain服务获取结果返回，下面是关于langchain流程介绍

- 第一步：从用户的输入中提取中订单号信息以及原始文本`RunnableParellel`（首选正则 -> 大模型兜底解析）

  > 通过langchain的链式调用将第一步获取到的订单信息和用户的提问传给第二步

- 第二步：通过`RunnablePassthrough`获取到用户的输入信息并且对信息进行增强

- 第三步：并行执行调用大模型方法得出关键信息    -  注意数据结构！！！

  > 补充点：强制使用prompt让大模型输出Json很可能不稳定,首先使用JSONParser解析器，如果报错才使用大模型的输出（try excpet）

  ![22480ffa44cbcbc67f47567124a796af](/Users/apple/Library/Containers/com.tencent.qq/Data/Library/Application Support/QQ/nt_qq_2660a18f42d347253957f815ee444e2a/nt_data/Pic/2026-04/Ori/22480ffa44cbcbc67f47567124a796af.png)

- 第四步：调用大模型提示词方法传输数据

```
# 节省大模型处理的时间，使用并行处理
analysis_chain = RunnableParallel(
# 情感分析
    sentiment=RunnableLambda(analyze_sentiment),
# 问题分类
    categories=RunnableLambda(classify_issue),
# 紧急程度
    urgency=RunnableLambda(assess_urgency)
)
```

##### (...)其他细节补充点

```
# lambda 表达式，简化形式，匿名函数的定义
# def fun(x):
#     return x
```

## 16、大模型认知

| 阶段   | 核心目标               | 输入数据                | 核心作用                      |
| ------ | ---------------------- | ----------------------- | ----------------------------- |
| 预训练 | 学习语言规律与通用知识 | 无标注原始文本          | 构建模型的 “知识底座”         |
| SFT    | 响应人类指令           | 人工标注的指令 - 回答对 | 实现 “指令 - 输出” 的基础对齐 |
| RLHF   | 符合人类偏好与价值观   | 人类对回答的偏好评分    | 优化输出质量，实现人性化对齐  |

三者的底层逻辑是：

1. Transformer 提供 “计算能力”，让模型能处理大规模文本；
2. 预训练填充 “知识”，让模型懂语言、懂世界；
3. SFT 建立 “指令映射”，让模型懂人类需求；
4. RLHF 优化 “输出偏好”，让模型的回答符合人类预期。

>**Transformer** 是 LLM 的核心架构，自注意力机制解决了大规模文本建模的效率与依赖问题，是所有后续训练的基础；
>
>预训练、SFT、RLHF 是 LLM 能力塑造的三层核心：预训练打底知识，SFT 对齐指令，RLHF 对齐人类偏好；
>
>LLM 的 “智能” 本质是参数对数据分布的拟合，而非真正的 “理解”，这也是其优势（大规模数据驱动）与局限（幻觉、无真正推理）的根源
