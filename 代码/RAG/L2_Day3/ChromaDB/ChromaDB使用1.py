# chromaDB使用.py
import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.sql.functions import count

from models import *


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
        self.collection = chroma_client.get_or_create_collection(name=collection_name,
                                                                 # 向量相似度计算方法： l2(默认), cosine, ip
                                                                 metadata={'hnsw:space': 'l2'})

        # 连接大模型的客户端
        self.client = get_normal_client()

    # 向量化
    def get_embeddings(self, texts, model=ALI_TONGYI_EMBEDDING_V3):
        '''封装 OpenAI 的 Embedding 模型接口'''
        data = self.client.embeddings.create(input=texts, model=model, dimensions=64).data
        return [x.embedding for x in data]

    # 批量向量化：get_embeddings函数的变体版，因为各个模型对一次能处理的文本条数有限制且每个平台不一致，新增一个batch_size参数用以控制。
    def get_embeddings_batch(self, texts, model=ALI_TONGYI_EMBEDDING_V3, batch_size=10):
        # 57 文档块
        all_embeddings = []
        for i in range(0, len(texts), 10):
            # texts[0:10],texts[10:20],texts[20:30],texts[30:40],texts[40:50],texts[50:60]
            batch_text = texts[i : i+10]
            data = self.client.embeddings.create(input=batch_text, model=model, dimensions=64).data
            all_embeddings.extend([x.embedding for x in data])
        return all_embeddings

    # 添加文档与向量
    def add_documents(self, documents):
        '''向 collection 中添加文档与向量'''
        embeddings = self.get_embeddings_batch(documents)

        self.collection.add(
            embeddings=embeddings,  # 每个文档的向量
            documents=documents,  # 文档的原文
            ids=[f"id{i}" for i in range(len(documents))],  # 每个文档的 id
        )
        print("self.collection.count():", self.collection.count())

    # 检索向量数据库
    def search(self, query, top_k):
        ''' 检索向量数据库
           query是用户的查询，
           top_k指查出top_k个相似高的记录
        '''
        results = self.collection.query(
            query_embeddings=self.get_embeddings_batch([query]),
            n_results=top_k
        )
        return results

    #查询存储在向量数据库的数据。仅限于测试，实际使用中，请勿使用。该方法会返回向量数据库中的所有数据，包括文档内容、向量、元数据和ID。
    def get(self,count):
        results = self.collection.get(include=["documents", "embeddings", "metadatas"], limit=count)
        return results


# 创建一个向量数据库对象
vector_db = MyVectorDBConnector("demo")


# 2.切分文档
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # 分割长度
    chunk_overlap=50,  # 重叠长度 /重叠窗口大小
    separators=["\n\n", "\n", "。", "?", "，", ""],
)
texts = splitter.split_text(content)
# for i, chunk in enumerate(texts):
#     print(f"块 {i + 1} - 长度{len(chunk)}，内容: {chunk}")

# 3.将文档存入向量数据库
# 向 向量数据库 中添加文档
vector_db.add_documents(texts)

# 4.查看向量数据库中的数据（仅为了满足测试需要。）
alldata = vector_db.get(count=1)
print("数据库内的数据为：\n" + str(alldata))
print('-' * 100)

# 5. 开始检索
# user_query = "DeepSeek的全称是什么?"
user_query = "deepseek相继发布了哪些模型"
# user_query = '360集团创始人周鸿祎说了什么?'
results = vector_db.search(user_query, 5)
print(results)
print('-' * 100)

# results['documents'] :
for i in results['documents'][0]:
    print(i + "\n----\n")

# 相关文档
contents = '\n'.join(results['documents'][0])

# 6. llm
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

def get_completion(prompt, model=ALI_TONGYI_TURBO_MODEL):
    '''封装 openai 接口'''
    messages = [{"role": "user", "content": prompt}]
    client = get_normal_client()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content

response = get_completion(prompt)
print(response)

