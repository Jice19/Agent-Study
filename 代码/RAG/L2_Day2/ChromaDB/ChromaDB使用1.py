# chromaDB使用.py
import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ===================== 【阿里云配置 直接写死】=====================
ALI_TONGYI_API_KEY = os.getenv("ALI_TONGYI_API_KEY")
ALI_TONGYI_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
ALI_TONGYI_EMBEDDING_V3 = "text-embedding-v3"
ALI_TONGYI_TURBO_MODEL = "qwen-turbo"
# ================================================================

# 1.加载文档，读取数据
with open('../Data/deepseek百度百科.txt', 'r', encoding='utf-8') as f:
    content = f.read()
print(len(content))  # 20899


# 负责和向量数据库打交道，接收文档转为向量，并保存到向量数据库中，然后根据需要从向量库中检索出最相似的记录
class MyVectorDBConnector:
    # 初始化，传入集合名称，和向量化函数名
    def __init__(self, collection_name):
        # 当前配置中，数据保存在内存中，如果需要持久化到磁盘，需使用 PersistentClient创建客户端
        chroma_client = chromadb.Client(Settings(allow_reset=True))
        # 持久化到磁盘
        # chroma_client = chromadb.PersistentClient(path="./chroma_data")
        # 为了演示，实际不需要每次 reset()
        # chroma_client.reset()

        # 创建一个 collection
        self.collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={'hnsw:space': 'l2'}
        )

        # 【直接在这里创建阿里云客户端，不依赖外部 models】
        self.client = OpenAI(
            api_key=ALI_TONGYI_API_KEY,
            base_url=ALI_TONGYI_URL
        )

    # 向量化
    def get_embeddings(self, texts, model=ALI_TONGYI_EMBEDDING_V3):
        '''封装 OpenAI 的 Embedding 模型接口'''
        data = self.client.embeddings.create(input=texts, model=model, dimensions=64).data
        return [x.embedding for x in data]

    # 批量向量化
    def get_embeddings_batch(self, texts, model=ALI_TONGYI_EMBEDDING_V3, batch_size=10):
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_text = texts[i: i + batch_size]
            data = self.client.embeddings.create(input=batch_text, model=model, dimensions=64).data
            all_embeddings.extend([x.embedding for x in data])
        return all_embeddings

    # 添加文档与向量
    def add_documents(self, documents):
        '''向 collection 中添加文档与向量'''
        embeddings = self.get_embeddings_batch(documents)

        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            ids=[f"id{i}" for i in range(len(documents))],
        )
        print("self.collection.count():", self.collection.count())

    # 检索向量数据库
    def search(self, query, top_k):
        results = self.collection.query(
            query_embeddings=self.get_embeddings_batch([query]),
            n_results=top_k
        )
        return results

    # 查询数据
    def get(self, count):
        results = self.collection.get(include=["documents", "embeddings", "metadatas"], limit=count)
        return results


# 创建向量数据库对象
vector_db = MyVectorDBConnector("demo")

# 2.切分文档
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "?", "，", ""],
)
texts = splitter.split_text(content)

# 3.将文档存入向量数据库
vector_db.add_documents(texts)

# 4.查看数据
alldata = vector_db.get(count=1)
print("数据库内的数据为：\n" + str(alldata))
print('-' * 100)

# 5. 开始检索
user_query = "deepseek相继发布了哪些模型"
results = vector_db.search(user_query, 5)
print(results)
print('-' * 100)

for i in results['documents'][0]:
    print(i + "\n----\n")

# 拼接相关文档
contents = '\n'.join(results['documents'][0])

# 6. LLM 提示词
prompt = f"""
你是一个问答机器人。
你的任务是根据下述给定的已知信息回答用户问题。
确保你的回复完全依据下述已知信息。不要编造答案。
如果下述已知信息不足以回答用户的问题，请直接回复"我无法回答您的问题"。

已知信息:
{contents}

----
用户问：
{user_query}

请用中文回答用户问题。
"""
print(prompt)
print('-' * 100)

# 直接在这里写 LLM 调用，不依赖 models
def get_completion(prompt, model=ALI_TONGYI_TURBO_MODEL):
    messages = [{"role": "user", "content": prompt}]
    client = OpenAI(api_key=ALI_TONGYI_API_KEY, base_url=ALI_TONGYI_URL)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content

response = get_completion(prompt)
print(response)